import copy
from fractions import Fraction
import json
from pathlib import Path
import random
import subprocess
import sys
import unittest

import worksheet_receipt as receipt


def request(bound='65 s'):
    document = receipt.worksheet.demo_document()
    document['steps'][-1]['at_most'] = bound
    return document


def rehash(value):
    value['receipt_sha256'] = receipt.digest({k: v for k, v in value.items() if k != 'receipt_sha256'})
    return value


class ReceiptTests(unittest.TestCase):
    def test_roundtrip_and_immutability(self):
        document = request()
        before = copy.deepcopy(document)
        saved = receipt.create(document)
        replayed = receipt.replay(receipt.decode(receipt.formatted(saved).encode()))
        self.assertTrue(replayed['verified'])
        self.assertEqual(replayed['calculation_exit'], 0)
        self.assertEqual(document, before)
        self.assertEqual(saved, receipt.create(document))

    def test_failed_claim_is_still_failed_after_replay(self):
        result = receipt.replay(receipt.create(request('1 min')))
        self.assertTrue(result['verified'])
        self.assertEqual(result['calculation_exit'], 1)
        self.assertFalse(result['result']['passes'])
        self.assertEqual(result['result']['steps'][-1]['base_value'], '64')

    def test_independent_fraction_chains(self):
        rng = random.Random(300)
        for _ in range(100):
            distance, duration, extra = (rng.randint(1, 100) for _ in range(3))
            document = {'schema': 'worksheet-flint/1', 'steps': [
                {'name': 'd', 'expression': f'{distance} km'},
                {'name': 't', 'expression': f'{duration} h'},
                {'name': 'v', 'expression': '$d / $t', 'to': 'm/s'},
                {'name': 'end', 'expression': f'$v * {extra} s', 'to': 'm'}]}
            result = receipt.replay(receipt.create(document))['result']
            self.assertEqual(Fraction(result['steps'][2]['base_value']), Fraction(distance * 1000, duration * 3600))
            self.assertEqual(Fraction(result['steps'][3]['base_value']), Fraction(distance * 1000 * extra, duration * 3600))

    def test_rehashed_result_forgery(self):
        original = receipt.create(request())
        mutations = [
            lambda v: v['result']['steps'][2].update(base_value='60'),
            lambda v: v['result']['steps'][2].update(dimensions={'length': 1, 'mass': 0, 'time': 0, 'data': 0}),
            lambda v: v['result']['steps'][-1]['checks']['at_most'].update(passes=False),
            lambda v: v['result']['steps'][2].update(dependencies=[]),
            lambda v: v.update(calculation_exit=True),
            lambda v: v['result'].update(passes=1),
            lambda v: v['result']['steps'].reverse(),
            lambda v: v['request']['steps'][0].update(expression='751 MiB')]
        for mutation in mutations:
            forged = copy.deepcopy(original)
            mutation(forged)
            with self.assertRaises(receipt.ReceiptError):
                receipt.replay(rehash(forged))

    def test_hash_and_source_mismatches(self):
        original = receipt.create(request())
        forged = copy.deepcopy(original)
        forged['receipt_sha256'] = 'f' * 64
        with self.assertRaisesRegex(receipt.ReceiptError, 'content hash'):
            receipt.replay(forged)
        forged = copy.deepcopy(original)
        forged['sources_sha256']['worksheet_flint.py'] = 'f' * 64
        with self.assertRaisesRegex(receipt.ReceiptError, 'source hashes'):
            receipt.replay(rehash(forged))
        forged = copy.deepcopy(original)
        forged['sources_sha256']['../../outside'] = 'f' * 64
        with self.assertRaises(receipt.ReceiptError):
            receipt.replay(rehash(forged))

    def test_schema_and_extra_fields(self):
        for value in (None, [], {}, {'schema': receipt.SCHEMA}):
            with self.assertRaises(receipt.ReceiptError):
                receipt.replay(value)
        for key, value in (('schema', 'future/2'), ('extra', True)):
            forged = receipt.create(request())
            forged[key] = value
            with self.assertRaises(receipt.ReceiptError):
                receipt.replay(rehash(forged))

    def test_decoder_rejects_ambiguous_and_excessive_inputs(self):
        for value in (b'{"a":1,"a":2}', b'{"x":NaN}', b'{"x":1.0}', b'999999',
                      b'\xff', b'[' * 17 + b']' * 17, b'{} trailing', b' ' * (receipt.MAX_BYTES + 1)):
            with self.assertRaises(receipt.ReceiptError):
                receipt.decode(value)
        self.assertEqual(receipt.decode(b'{"brackets":"[[[[[[[[[[[[[[[[[[[["}'), {'brackets': '[' * 20})

    def test_worksheet_limits_are_enforced(self):
        for document in (
            {'schema': 'worksheet-flint/1', 'steps': [{'name': 'a', 'expression': '$future'}]},
            {'schema': 'worksheet-flint/1', 'steps': [{'name': 'a', 'expression': '0 m + 0 s'}]},
            {'schema': 'worksheet-flint/1', 'steps': [{'name': 'a', 'expression': '1 / 0'}]},
            {'schema': 'worksheet-flint/1', 'steps': [{'name': str(i), 'expression': '1'} for i in range(33)]},
            {'schema': 'worksheet-flint/1', 'steps': [{'name': 'a', 'expression': 3}]},
            {'schema': 'worksheet-flint/1', 'steps': [{'name': 'a', 'expression': '1' * 4097}]},
        ):
            with self.assertRaises(receipt.ReceiptError):
                receipt.create(document)

    def run_cli(self, command, value):
        return subprocess.run([sys.executable, '-B', str(Path(receipt.__file__)), command],
                              input=value, capture_output=True, timeout=15)

    def test_cli_statuses_and_no_partial_output(self):
        for bound, expected_status in (('65 s', 0), ('1 min', 1)):
            created = self.run_cli('create', json.dumps(request(bound)).encode())
            self.assertEqual(created.returncode, expected_status, created.stderr)
            verified = self.run_cli('verify', created.stdout)
            self.assertEqual(verified.returncode, expected_status, verified.stderr)
            self.assertTrue(json.loads(verified.stdout)['verified'])
        document = request()
        document['steps'].append({'name': 'bad', 'expression': '1 m + 1 s'})
        invalid = self.run_cli('create', json.dumps(document).encode())
        self.assertEqual(invalid.returncode, 2)
        self.assertEqual(invalid.stdout, b'')
        forged = receipt.create(request())
        forged['result']['steps'][0]['value'] = '999'
        invalid = self.run_cli('verify', receipt.canonical(rehash(forged)))
        self.assertEqual(invalid.returncode, 2)
        self.assertEqual(invalid.stdout, b'')

    def test_cli_demo(self):
        result = self.run_cli('demo', b'')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(json.loads(result.stdout)['rehashed_altered_intermediate_rejected'])


if __name__ == '__main__':
    unittest.main()
