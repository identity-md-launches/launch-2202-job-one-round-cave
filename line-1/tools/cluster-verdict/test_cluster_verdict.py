import csv
from fractions import Fraction
import hashlib
import io
import itertools
import json
from pathlib import Path
import random
import shutil
import subprocess
import sys
import tempfile
import unittest

import cluster_verdict as cv


def brute(deltas):
    sums = [sum(s*d for s, d in zip(signs, deltas))
            for signs in itertools.product((-1, 1), repeat=len(deltas))]
    return Fraction(sum(abs(s) >= abs(sum(deltas)) for s in sums), len(sums))


class Tests(unittest.TestCase):
    def test_exhaustive_small_integer_differences(self):
        for n in range(2, 5):
            for deltas in itertools.product(range(-2, 3), repeat=n):
                self.assertEqual(cv.exact_sign_flip(deltas)['p'], brute(deltas))

    def test_seeded_unequal_groups(self):
        rng = random.Random(3001)
        for _ in range(100):
            deltas = [rng.randint(-15, 15) for _ in range(rng.randint(2, 10))]
            self.assertEqual(cv.exact_sign_flip(deltas)['p'], brute(deltas))

    def test_exact_conditional_null_calibration(self):
        # Exhaust the independent fair-sign null, including zeros and tied sums.
        for magnitudes in ([1, 1], [1, 2, 3], [0, 2, 2, 3], [1, 1, 1, 2, 2]):
            ps = [cv.exact_sign_flip([s*d for s, d in zip(signs, magnitudes)])['p']
                  for signs in itertools.product((-1, 1), repeat=len(magnitudes))]
            for alpha in set(ps):
                self.assertLessEqual(Fraction(sum(p <= alpha for p in ps), len(ps)), alpha)

    def test_singletons_match_mcnemar(self):
        for wins in range(12):
            for losses in range(12):
                deltas = [1]*wins + [-1]*losses + [0, 0]
                self.assertEqual(cv.exact_sign_flip(deltas)['p'], cv.engine.exact_mcnemar(wins, losses))

    def test_zero_cancellation_and_integer_precision(self):
        zero = cv.exact_sign_flip([0, 0, 0])
        self.assertEqual(zero['p'], 1)
        self.assertEqual(zero['assignments'], '1')
        self.assertEqual(zero['zero_clusters'], 3)
        large = cv.exact_sign_flip([1]*128)
        self.assertEqual(large['p'], Fraction(1, 2**127))
        self.assertEqual(large['assignments'], str(2**128))
        self.assertEqual(large['tail_assignments'], '2')
        self.assertEqual(cv.exact_sign_flip([1000, -1000])['p'], 1)

    def test_family_boundary_and_holm(self):
        # Independent implementation: adjusted p is the max over earlier order stats.
        rng = random.Random(3030)
        for _ in range(100):
            ps = [Fraction(rng.randint(0, 100), 100) for _ in range(rng.randint(2, 16))]
            order = sorted(range(len(ps)), key=lambda i: (ps[i], i))
            want = [None]*len(ps)
            for rank, i in enumerate(order):
                want[i] = min(Fraction(1), max((len(ps)-j)*ps[order[j]] for j in range(rank+1)))
            self.assertEqual(cv.holm(ps), want)
        self.assertEqual(cv.holm([Fraction(1, 40)]*2), [Fraction(1, 20)]*2)

    def test_demo_and_original_case_level_contrast(self):
        raw, mapping = cv.demo_inputs()
        result = cv.analyze(raw, mapping)
        self.assertEqual(result['paired_cases'], 12)
        self.assertEqual(result['clusters'], 3)
        for c in result['candidates']:
            self.assertEqual(c['exact_two_sided_p'], cv.grouping.rational(Fraction(1, 2)))
            self.assertEqual(c['holm_adjusted_p'], cv.grouping.rational(Fraction(1)))
            self.assertFalse(c['familywise_reject_sign_exchangeability'])
            self.assertEqual(c['case_weighted_effect'], cv.grouping.rational(Fraction(5, 6)))
        names, rows = cv.engine.read_csv_bytes(raw)
        case_level = cv.engine.analyze(raw, names, rows, cv.engine.parse_alpha('0.05'))
        self.assertTrue(all(c['familywise_reject_equal_discordance'] for c in case_level['candidates']))

    def test_caps_mapping_order_and_immutability(self):
        raw, mapping = cv.demo_inputs()
        before = raw, mapping
        full = cv.analyze(raw, mapping, max_details=128)
        for cap in (0, 1, 2):
            result = cv.analyze(raw, mapping, max_details=cap)
            self.assertEqual(result['cluster_details'], full['cluster_details'][:cap])
            self.assertEqual(result['cluster_details_omitted'], 3-cap)
            self.assertEqual(result['complete_cluster_details_sha256'], full['complete_cluster_details_sha256'])
            self.assertEqual(result['candidates'], full['candidates'])
        reversed_mapping = b'\xef\xbb\xbfcase,cluster\r\n' + b'\r\n'.join(reversed(mapping.splitlines()[1:])) + b'\r\n'
        reordered = cv.analyze(raw, reversed_mapping)
        self.assertEqual(reordered['candidates'], full['candidates'])
        self.assertEqual(reordered['complete_cluster_details_sha256'], full['complete_cluster_details_sha256'])
        self.assertEqual((raw, mapping), before)

    def test_report_matches_independent_enumeration(self):
        rng = random.Random(3011)
        for _ in range(40):
            n, k, g = rng.randint(8, 30), rng.randint(2, 6), rng.randint(2, 7)
            names = [f'candidate-{i}' for i in range(k)]
            ids = [f'case-{i}' for i in range(n)]
            rows = [tuple(rng.randrange(2) for _ in range(k+1)) for _ in range(n)]
            raw = cv.grouping.encoded(names, ids, rows)
            mapping = ('case,cluster\n' + ''.join(f'{i},g{j%g}\n' for j, i in enumerate(ids))).encode()
            report = cv.analyze(raw, mapping)
            ps = []
            for i, c in enumerate(report['candidates'], 1):
                deltas = [sum(r[i]-r[0] for j, r in enumerate(rows) if j%g == group) for group in range(g)]
                p = brute(deltas)
                ps.append(p)
                self.assertEqual(c['exact_two_sided_p'], cv.grouping.rational(p))
                self.assertEqual(c['case_weighted_effect'], cv.grouping.rational(Fraction(sum(deltas), n)))
                self.assertEqual(c['candidate_passes'], sum(r[i] for r in rows))
            for p, c in zip(cv.holm(ps), report['candidates']):
                self.assertEqual(c['holm_adjusted_p'], cv.grouping.rational(p))
                self.assertEqual(c['familywise_reject_sign_exchangeability'], p <= Fraction(1, 20))

    def test_invalid_inputs(self):
        raw, mapping = cv.demo_inputs()
        for value in (b'', mapping + mapping.splitlines(keepends=True)[1],
                      b'\n'.join(mapping.splitlines()[:-1]), mapping+b'unknown,g\n',
                      mapping.replace(b'agreement', b' group'), mapping.replace(b'agreement', b'bad\x00id')):
            with self.assertRaises((ValueError, csv.Error)):
                cv.analyze(raw, value)
        for value in (b'', raw.replace(b',0,1,1', b',0,1,'), raw.replace(b',0,1,1', b',0,1,2'), b'\xff'):
            with self.assertRaises(ValueError):
                cv.analyze(value, mapping)
        for alpha in ('NaN', '0', '0.21', '1e-7'):
            with self.assertRaises(ValueError):
                cv.analyze(raw, mapping, alpha)
        for cap in (-1, 129, True, 1.5):
            with self.assertRaises(ValueError):
                cv.analyze(raw, mapping, max_details=cap)
        for deltas in ([1], [0]*129, [1001, 1000], [True, 1], [1.0, 1]):
            with self.assertRaises(ValueError):
                cv.exact_sign_flip(deltas)

    def test_unicode_quotes_bom_and_internal_cancellation(self):
        raw = b'\xef\xbb\xbfcase,baseline,a,b\r\n"comma,\xf0\x9f\x90\xb8",0,1,1\r\ny,1,0,0\r\nz,0,1,1\r\n'
        mapping = b'case,cluster\n"comma,\xf0\x9f\x90\xb8",same\ny,same\nz,other\n'
        result = cv.analyze(raw, mapping)
        self.assertEqual(result['candidates'][0]['zero_clusters'], 1)
        self.assertEqual(result['candidates'][0]['exact_two_sided_p'], cv.grouping.rational(Fraction(1)))

    def test_portable_cli_pins_and_no_partial_errors(self):
        scratch = Path('test/scratch')
        scratch.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=scratch) as temp:
            folder = Path(temp)
            for name in ('cluster_verdict.py', 'grouping_engine.py', 'ladder_engine.py'):
                shutil.copyfile(Path(__file__).with_name(name), folder/name)
            raw, mapping = cv.demo_inputs()
            (folder/'cases.csv').write_bytes(raw)
            (folder/'groups.csv').write_bytes(mapping)
            script = str(folder/'cluster_verdict.py')
            run = lambda args: subprocess.run([sys.executable, '-B', script, *args], capture_output=True)
            args = ['--input', str(folder/'cases.csv'), '--mapping', str(folder/'groups.csv'),
                    '--expected-input-sha256', cv.grouping.digest(raw),
                    '--expected-mapping-sha256', cv.grouping.digest(mapping)]
            good = run(args)
            self.assertEqual(good.returncode, 0, good.stderr)
            self.assertEqual(json.loads(good.stdout)['clusters'], 3)
            self.assertEqual(run(['--demo']).returncode, 0)
            for options in (args[:-1]+['bad'], ['--demo', '--mapping', 'x'], [],
                            ['--demo', '--alpha', 'NaN'], ['--demo', '--max-details', '129']):
                bad = run(options)
                self.assertEqual(bad.returncode, 2)
                self.assertEqual(bad.stdout, b'')
            with self.assertRaises(ValueError):
                cv.grouping.workspace_bytes(Path.cwd().parent)

    def test_snapshot_provenance(self):
        folder = Path(__file__).parent
        for item in json.loads((folder/'provenance.json').read_text())['snapshots']:
            actual = hashlib.sha256((folder/item['file']).read_bytes()).hexdigest()
            self.assertEqual(actual, item['sha256'])
            self.assertEqual((folder/item['file']).read_bytes(), Path(item['source']).read_bytes())


if __name__ == '__main__':
    unittest.main()
