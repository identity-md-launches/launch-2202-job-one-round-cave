"""Offline adversarial integration checks for the coupled evidence receipt."""
import copy
from fractions import Fraction
import json
from pathlib import Path
import random
import shutil
import subprocess
import sys
import tempfile
import unittest

import load_receipt as app


def rehash(receipt):
    receipt['receipt_sha256'] = app.digest({k: v for k, v in receipt.items() if k != 'receipt_sha256'})
    return receipt


class ReceiptChecks(unittest.TestCase):
    def test_exact_demo_partition_mean_and_failed_policy(self):
        result = app.demo()
        self.assertTrue(result['rehashed_histogram_forgery_rejected'])
        good = result['passing']
        self.assertEqual(good['coverage']['duration_by_depth_us'], {'0': 1000000, '1': 2000000, '2': 2000000})
        rows = {x['request']['name']: x for x in good['worksheet_result']['steps']}
        self.assertEqual(rows['partition']['base_value'], '5')
        self.assertEqual(rows['interval_time']['base_value'], '6')
        self.assertEqual(rows['mean_depth']['base_value'], '6/5')
        self.assertEqual(rows['covered_fraction']['base_value'], '4/5')
        self.assertEqual(good['calculation_exit'], 0)
        self.assertTrue(result['failed_claim']['verified'])
        self.assertEqual(result['failed_claim']['calculation_exit'], 1)

    def test_no_input_mutation_and_canonical_roundtrip(self):
        request = app.demo_request()
        before = copy.deepcopy(request)
        receipt = app.create(request)
        self.assertEqual(request, before)
        replayed = app.verify(app.decode(app.canonical(receipt)), receipt['receipt_sha256'])
        self.assertTrue(replayed['verified'])
        request['max_mean_depth'] = '3'
        self.assertEqual(receipt['request']['max_mean_depth'], '2')

    def test_rehashed_histogram_and_worksheet_forgeries(self):
        original = app.create(app.demo_request())
        mutations = [
            lambda r: r['coverage']['duration_by_depth_us'].update({'1': 1000000}),
            lambda r: r['coverage']['counts'].update(undated_lines=0),
            lambda r: r['worksheet_receipt']['result']['steps'][0].update(base_value='6'),
            lambda r: r.update(calculation_exit=True),
            lambda r: r['coverage']['counts'].update(segments_shown=True),
            lambda r: r['request'].update(max_uncovered='0 s')]
        for change in mutations:
            forged = copy.deepcopy(original)
            change(forged)
            with self.assertRaises(ValueError):
                app.verify(rehash(forged))

    def test_consistent_arithmetic_substitution_is_not_evidence(self):
        receipt = app.create(app.demo_request())
        document = copy.deepcopy(receipt['worksheet_receipt']['request'])
        document['steps'][2]['expression'] = '0 s'
        receipt['worksheet_receipt'] = app.arithmetic.create(document)
        # The arithmetic receipt alone is valid, but detached from the real histogram.
        self.assertTrue(app.arithmetic.replay(receipt['worksheet_receipt'])['verified'])
        with self.assertRaisesRegex(ValueError, 'fully replayed'):
            app.verify(rehash(receipt))

    def test_changed_pack_outside_query_rejected(self):
        request = app.demo_request()
        request['pack'] = app.load.replay.make_pack([('example.log',
            b'2026-10-18T10:00:01Z in\n2026-10-18T11:00:00Z outside\n')])
        saved = app.create(request)
        saved['request']['pack']['timeline']['events'][-1]['message'] = 'tampered'
        with self.assertRaises(ValueError):
            app.verify(rehash(saved))

    def test_source_hash_and_retained_identity(self):
        saved = app.create(app.demo_request())
        for pin in ('f' * 64, 'bad', True):
            with self.assertRaises(ValueError):
                app.verify(saved, pin)
        replaced = app.create(app.demo_request('3'))
        with self.assertRaisesRegex(ValueError, 'retained'):
            app.verify(replaced, saved['receipt_sha256'])
        saved['sources_sha256']['load_receipt.py'] = 'f' * 64
        with self.assertRaisesRegex(ValueError, 'source hashes'):
            app.verify(rehash(saved))

    def test_dimensions_and_invalid_requests(self):
        for field, value in (('max_uncovered', '1 m'), ('max_uncovered', '-1 s'),
                             ('max_mean_depth', '1 s'), ('max_mean_depth', '-1'),
                             ('max_mean_depth', True), ('max_mean_depth', '$unknown')):
            request = app.demo_request()
            request[field] = value
            with self.assertRaises(ValueError):
                app.create(request)
        for request in (None, {}, {**app.demo_request(), 'extra': 1}):
            with self.assertRaises(ValueError):
                app.create(request)
        request = app.demo_request()
        request['end'] = request['start']
        with self.assertRaises(ValueError):
            app.create(request)

    def test_no_events_in_window(self):
        request = app.demo_request()
        request['start'] = '2026-10-18T11:00:00Z'
        request['end'] = '2026-10-18T11:00:05Z'
        request['max_uncovered'] = '5 s'
        result = app.verify(app.create(request))
        self.assertEqual(result['coverage']['duration_by_depth_us'], {'0': 5000000})
        self.assertEqual(result['worksheet_result']['steps'][-1]['base_value'], '0')
        self.assertEqual(result['worksheet_result']['steps'][-2]['base_value'], '0')

    def test_seeded_independent_integral_oracle(self):
        rng = random.Random(120737)
        for _ in range(50):
            starts = [rng.randrange(-2, 8) for _ in range(rng.randrange(1, 9))]
            raw = ''.join(f'2026-10-18T10:00:{x:02d}Z sample\n'
                          for x in starts if x >= 0).encode()
            # Keep at least one event; intervals are one second wide, at integer boundaries.
            if not raw:
                raw = b'2026-10-18T10:00:07Z outside\n'
                starts = [7]
            else:
                starts = [x for x in starts if x >= 0]
            request = app.demo_request('10')
            request['pack'] = app.load.replay.make_pack([('seeded.log', raw)])
            request['max_uncovered'] = '5 s'
            result = app.verify(app.create(request))
            depths = [sum(x == t for x in starts) for t in range(5)]
            expected = {str(k): depths.count(k) * 1000000 for k in set(depths)}
            self.assertEqual(result['coverage']['duration_by_depth_us'], expected)
            self.assertEqual(Fraction(result['worksheet_result']['steps'][-2]['base_value']),
                             Fraction(sum(depths), 5))

    def test_decoder_bounds_and_ambiguous_json(self):
        for raw in (b'{"x":1,"x":2}', b'{"x":NaN}', b'{"x":1.0}', b'1' * 21,
                    b'\xff', b'[' * 30 + b']' * 30, b'x' * (app.MAX_BYTES + 1)):
            with self.assertRaises((ValueError, RecursionError)):
                app.decode(raw)
        for value in ({}, [], None):
            with self.assertRaises(ValueError):
                app.verify(value)

    def test_portable_cli_and_no_partial_stdout(self):
        scratch = Path('test/scratch')
        scratch.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=scratch) as directory:
            copied = Path(directory).resolve() / 'portable'
            shutil.copytree(app.HERE, copied)
            command = [sys.executable, '-B', str(copied / 'load_receipt.py')]
            for budget, expected in (('2', 0), ('1', 1)):
                saved = subprocess.run(command + ['create'], input=app.canonical(app.demo_request(budget)),
                                       capture_output=True, cwd=copied, timeout=20)
                self.assertEqual(saved.returncode, expected, saved.stderr)
                pin = json.loads(saved.stdout)['receipt_sha256']
                checked = subprocess.run(command + ['verify', '--expected-sha256', pin], input=saved.stdout,
                                         capture_output=True, cwd=copied, timeout=20)
                self.assertEqual(checked.returncode, expected, checked.stderr)
                self.assertTrue(json.loads(checked.stdout)['verified'])
                bad = subprocess.run(command + ['verify', '--expected-sha256', 'f' * 64],
                                     input=saved.stdout, capture_output=True, cwd=copied, timeout=20)
                self.assertEqual(bad.returncode, 2)
                self.assertEqual(bad.stdout, b'')
            bad = subprocess.run(command + ['create'], input=b'{}', capture_output=True, cwd=copied)
            self.assertEqual(bad.returncode, 2)
            self.assertEqual(bad.stdout, b'')

    def test_snapshot_provenance(self):
        records = json.loads((app.HERE / 'provenance.json').read_text())
        for row in records:
            snapshot = app.HERE / Path(row['snapshot']).relative_to('shared/load-receipt')
            self.assertEqual(app.hashlib.sha256(snapshot.read_bytes()).hexdigest(), row['sha256'])


if __name__ == '__main__':
    unittest.main()
