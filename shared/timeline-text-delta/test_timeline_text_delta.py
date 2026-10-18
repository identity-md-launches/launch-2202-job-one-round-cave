"""Checks for the shared original-byte and timeline review boundary."""

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import timeline_text_delta as tool


class TimelineTextDeltaTests(unittest.TestCase):
    def packs(self, before, after):
        fixed = [('server.log', b'2026-10-18T10:00:02Z received\n')]
        return (tool.timeline_diff.replay.make_pack([('worker.log', before), *fixed]),
                tool.timeline_diff.replay.make_pack([('worker.log', after), *fixed]))

    def test_demo_joins_changed_line_to_original_byte_finding(self):
        result = tool.demo()
        self.assertEqual(result['unicode']['counts']['added'], 1)
        self.assertEqual(result['timeline']['line_changes']['counts']['changed-line'], 1)
        self.assertEqual(result['joint_observation']['cited_pair_relation_before'],
                         'left-before-right')
        self.assertEqual(result['joint_observation']['cited_pair_relation_after'],
                         'right-before-left')
        source = result['unicode']['changes'][0]['after']['source']
        self.assertEqual(source['preview']['bytes'], '\\xe2\\x80\\xae')

    def test_no_unicode_finding_does_not_hide_timeline_change(self):
        before, after = self.packs(b'2026-10-18T10:00:00Z ready\n',
                                   b'2026-10-18T10:00:04Z ready\n')
        result = tool.review(before, after, 'worker.log',
                             ('worker.log', 1), ('server.log', 1))
        self.assertEqual(result['unicode']['counts']['added'], 0)
        self.assertEqual(result['timeline']['line_changes']['counts']['changed-line'], 1)
        self.assertNotEqual(result['joint_observation']['cited_pair_relation_before'],
                            result['joint_observation']['cited_pair_relation_after'])

    def test_unicode_detail_cap_keeps_complete_counts(self):
        before, after = self.packs(b'2026-10-18T10:00:00Z ready\n',
            '2026-10-18T10:00:00Z \u202eready \u200b\n'.encode())
        short = tool.review(before, after, 'worker.log',
                            ('worker.log', 1), ('server.log', 1), 1)
        long = tool.review(before, after, 'worker.log',
                           ('worker.log', 1), ('server.log', 1), 20)
        self.assertEqual(short['unicode']['counts'], long['unicode']['counts'])
        self.assertGreater(short['unicode']['omitted_details'], 0)
        self.assertEqual(short['timeline']['line_changes']['counts'],
                         long['timeline']['line_changes']['counts'])

    def test_tampered_pack_and_missing_source_rejected(self):
        before, after = self.packs(b'2026-10-18T10:00:00Z ready\n',
                                   b'2026-10-18T10:00:01Z ready\n')
        with self.assertRaisesRegex(ValueError, 'absent'):
            tool.review(before, after, 'other.log', ('worker.log', 1), ('server.log', 1))
        after['timeline']['events'][0]['message'] = 'forged'
        with self.assertRaises(ValueError):
            tool.review(before, after, 'worker.log', ('worker.log', 1), ('server.log', 1))

    def test_cli_pins_and_no_partial_error_output(self):
        before, after = self.packs(b'2026-10-18T10:00:00Z ready\n',
            '2026-10-18T10:00:03Z \u202eready\n'.encode())
        with tempfile.TemporaryDirectory(dir=ROOT / 'test/scratch') as temp:
            old = Path(temp) / 'before.json'
            new = Path(temp) / 'after.json'
            old.write_bytes(tool.timeline_diff.replay.canonical(before) + b'\n')
            new.write_bytes(tool.timeline_diff.replay.canonical(after) + b'\n')
            command = [sys.executable, '-B', str(HERE / 'timeline_text_delta.py'),
                       'review', str(old), str(new), '--source', 'worker.log',
                       '--left', 'worker.log', '1', '--right', 'server.log', '1',
                       '--expect-before-sha256', hashlib.sha256(old.read_bytes()).hexdigest(),
                       '--expect-after-sha256', hashlib.sha256(new.read_bytes()).hexdigest()]
            good = subprocess.run(command, cwd=ROOT, capture_output=True, timeout=15)
            self.assertEqual(good.returncode, 0, good.stderr)
            self.assertEqual(json.loads(good.stdout)['unicode']['counts']['added'], 1)
            bad = command.copy()
            bad[-1] = '0' * 64
            failed = subprocess.run(bad, cwd=ROOT, capture_output=True, timeout=15)
            self.assertEqual(failed.returncode, 2)
            self.assertEqual(failed.stdout, b'')


if __name__ == '__main__':
    unittest.main()
