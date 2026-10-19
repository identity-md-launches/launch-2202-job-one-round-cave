"""Offline checks with synthetic evidence and an independent discrete-time oracle."""
import copy
import hashlib
import json
from pathlib import Path
import random
import shutil
import subprocess
import sys
import tempfile
import unittest

import replay
import timeline_load as load

HERE = Path(__file__).resolve().parent
START = '2026-10-18T10:00:00Z'
END = '2026-10-18T10:00:05Z'


class LoadTests(unittest.TestCase):
    def test_demo_and_histogram(self):
        result = load.demo()
        self.assertEqual(result['duration_by_depth_us'], {'0': 1000000, '1': 2000000, '2': 2000000})
        self.assertEqual(result['counts']['segments_total'], 5)
        self.assertEqual(result['counts']['maximum_interval_depth'], 2)
        self.assertEqual(result['counts']['undated_lines'], 1)
        self.assertEqual(sum(result['duration_by_depth_us'].values()), 5000000)

    def test_half_open_touch_and_merge(self):
        self.assertEqual(load.profile([(0, 2), (2, 4)], 0, 5), [(0, 4, 1), (4, 5, 0)])
        self.assertEqual(load.profile([(-2, 1), (0, 3), (2, 8)], 0, 5),
                         [(0, 1, 2), (1, 2, 1), (2, 3, 2), (3, 5, 1)])
        self.assertEqual(load.profile([], 0, 5), [(0, 5, 0)])
        self.assertEqual(load.profile([(5, 8), (-2, 0)], 0, 5), [(0, 5, 0)])

    def test_seeded_independent_depth_oracle(self):
        rng = random.Random(737)
        for _ in range(500):
            intervals = [(a, a + rng.randrange(1, 8))
                         for a in (rng.randrange(-5, 15) for _ in range(rng.randrange(25)))]
            spans = load.profile(intervals, 0, 10)
            self.assertEqual(sum(b - a for a, b, _ in spans), 10)
            self.assertTrue(all(spans[i][1] == spans[i+1][0] and spans[i][2] != spans[i+1][2]
                                for i in range(len(spans)-1)))
            for t in range(10):
                actual = next(depth for a, b, depth in spans if a <= t < b)
                expected = sum(a <= t < b for a, b in intervals)
                self.assertEqual(actual, expected)

    def test_exact_offset_endpoints_and_rejections(self):
        self.assertEqual(load.instant('2026-10-18T12:00+02:00'), load.instant(START))
        for text in ('2026-10-18T10:00:00', '2026-02-30T00:00Z',
                     '2026-10-18T10:00:00+24:00', '2026-10-18T10:00:00.0000001Z', True):
            with self.assertRaises((ValueError, OverflowError)):
                load.instant(text)
        with self.assertRaises(ValueError):
            load.profile([], 5, 5)

    def test_full_verification_no_mutation_or_message_echo(self):
        pack = replay.make_pack([('private.log', b'2026-10-18T10:00:01Z SECRET_MESSAGE\n')])
        original = copy.deepcopy(pack)
        result = load.analyze(pack, START, END)
        self.assertEqual(pack, original)
        self.assertNotIn(b'SECRET_MESSAGE', replay.canonical(result))
        self.assertNotIn(b'private.log', replay.canonical(result))
        self.assertEqual(replay.canonical(result), replay.canonical(load.analyze(pack, START, END)))
        pack['timeline']['events'][0]['message'] = 'forged'
        with self.assertRaises(replay.ReplayError):
            load.analyze(pack, START, END)

    def test_limit_does_not_change_exact_totals(self):
        pack = replay.make_pack([('sample.log', b'2026-10-18T10:00:01Z one\n'
                                 b'2026-10-18T10:00:03Z two\n')])
        full = load.analyze(pack, START, END)
        short = load.analyze(pack, START, END, 1)
        self.assertEqual(full['duration_by_depth_us'], short['duration_by_depth_us'])
        self.assertEqual(short['counts']['segments_not_shown'], full['counts']['segments_total'] - 1)
        for value in (True, -1, 201, 1.5):
            with self.assertRaises(ValueError):
                load.analyze(pack, START, END, value)

    def test_portable_cli_digest_and_provenance(self):
        provenance = json.loads((HERE / 'PROVENANCE.json').read_text())
        for item in provenance['dependencies']:
            self.assertEqual(hashlib.sha256((HERE / item['path']).read_bytes()).hexdigest(), item['sha256'])
        scratch = Path('test/scratch')
        scratch.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=scratch) as tmp:
            root = Path(tmp).resolve()
            copied = root / 'tool'
            shutil.copytree(HERE, copied)
            raw = replay.canonical(replay.make_pack([('sample.log', b'2026-10-18T10:00:01Z yes\n')])) + b'\n'
            evidence = root / 'pack.json'
            evidence.write_bytes(raw)
            command = [sys.executable, '-B', str(copied / 'timeline_load.py'), 'analyze', str(evidence),
                       '--start', START, '--end', END]
            good = subprocess.run(command + ['--expect-sha256', replay.digest(raw)], cwd=root,
                                  capture_output=True)
            self.assertEqual(good.returncode, 0, good.stderr)
            self.assertEqual(json.loads(good.stdout)['pack_sha256'], replay.digest(raw))
            bad = subprocess.run(command + ['--expect-sha256', '0' * 64], cwd=root,
                                 capture_output=True)
            self.assertEqual(bad.returncode, 2)
            self.assertEqual(bad.stdout, b'')


if __name__ == '__main__':
    unittest.main()
