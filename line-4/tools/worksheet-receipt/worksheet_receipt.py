#!/usr/bin/env python3
"""Keep and replay exact multi-step dimensional worksheets; stdin only."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import sys

import worksheet_flint as worksheet

SCHEMA = 'worksheet-receipt/1'
MAX_BYTES = 524288
SOURCES = ('engine.py', 'worksheet_flint.py', 'worksheet_receipt.py')


class ReceiptError(ValueError):
    pass


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=True,
                      separators=(',', ':'), allow_nan=False).encode('ascii')


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def source_hashes():
    # Fixed siblings only: no receipt-controlled path or external configuration.
    return {name: hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
            for name in SOURCES}


def formatted(value):
    return json.dumps(value, ensure_ascii=True, indent=2, allow_nan=False) + '\n'


def create(request):
    try:
        # Apply the original worksheet's complete schema and resource limits.
        document = worksheet.decode(canonical(request))
        result = worksheet.evaluate(document)
    except worksheet.WorksheetError as exc:
        raise ReceiptError(str(exc)) from exc
    payload = {'schema': SCHEMA, 'sources_sha256': source_hashes(),
               'request': document, 'result': result,
               'calculation_exit': 0 if result['passes'] else 1}
    receipt = {**payload, 'receipt_sha256': digest(payload)}
    if len(formatted(receipt).encode('ascii')) > MAX_BYTES:
        raise ReceiptError('receipt exceeds serialized byte limit; shorten worksheet')
    return receipt


def replay(receipt):
    keys = {'schema', 'sources_sha256', 'request', 'result',
            'calculation_exit', 'receipt_sha256'}
    if type(receipt) is not dict or set(receipt) != keys:
        raise ReceiptError('receipt has missing or extra fields')
    if receipt['schema'] != SCHEMA:
        raise ReceiptError('unsupported receipt schema')
    if canonical(receipt['sources_sha256']) != canonical(source_hashes()):
        raise ReceiptError('source hashes differ; use the original tool folder')
    payload = {k: v for k, v in receipt.items() if k != 'receipt_sha256'}
    if receipt['receipt_sha256'] != digest(payload):
        raise ReceiptError('receipt content hash mismatch')
    computed = create(receipt['request'])
    # Type-sensitive bytes: Python equality alone treats True as 1.
    if canonical(computed) != canonical(receipt):
        raise ReceiptError('receipt differs from recomputed worksheet')
    return {'verified': True, 'receipt_sha256': computed['receipt_sha256'],
            'calculation_exit': computed['calculation_exit'], 'result': computed['result']}


def decode(data):
    if len(data) > MAX_BYTES:
        raise ReceiptError(f'receipt exceeds {MAX_BYTES} bytes')
    try:
        source = data.decode('utf-8')
    except UnicodeDecodeError as exc:
        raise ReceiptError('receipt must be UTF-8') from exc
    depth, quoted, escaped = 0, False, False
    for char in source:
        if quoted:
            if escaped:
                escaped = False
            elif char == '\\':
                escaped = True
            elif char == '"':
                quoted = False
        elif char == '"':
            quoted = True
        elif char in '[{':
            depth += 1
            if depth > 16:
                raise ReceiptError('receipt exceeds 16 nesting levels')
        elif char in ']}':
            depth -= 1

    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ReceiptError(f'duplicate JSON key {key!r}')
            result[key] = value
        return result

    def integer(text):
        if len(text) > 5:
            raise ReceiptError('JSON integer exceeds receipt limit')
        return int(text)

    def forbidden(text):
        raise ReceiptError('JSON floats and nonfinite constants are unsupported')

    try:
        return json.loads(source, object_pairs_hook=pairs, parse_int=integer,
                          parse_float=forbidden, parse_constant=forbidden)
    except (ValueError, RecursionError) as exc:
        raise ReceiptError(f'invalid receipt JSON: {exc}') from exc


def demo():
    request = worksheet.demo_document()
    failed = create(request)
    passing_request = copy.deepcopy(request)
    passing_request['steps'][-1]['at_most'] = '65 s'
    passing = create(passing_request)
    forged = copy.deepcopy(passing)
    forged['result']['steps'][2]['base_value'] = '60'
    forged['receipt_sha256'] = digest({k: v for k, v in forged.items() if k != 'receipt_sha256'})
    try:
        replay(forged)
    except ReceiptError:
        rejected = True
    else:
        raise ReceiptError('demo did not reject rehashed altered intermediate')
    return {'demo': 'Hypothetical transfer inputs, not measurements',
            'passing': replay(decode(canonical(passing))),
            'failed_claim': replay(decode(canonical(failed))),
            'rehashed_altered_intermediate_rejected': rejected}


def main(argv=None):
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('command', choices=('create', 'verify', 'demo'))
    args = cli.parse_args(argv)
    try:
        if args.command == 'demo':
            result = demo()
            status = 0
        elif args.command == 'create':
            request = worksheet.decode(sys.stdin.buffer.read(worksheet.MAX_BYTES + 1))
            result = create(request)
            status = result['calculation_exit']
        else:
            result = replay(decode(sys.stdin.buffer.read(MAX_BYTES + 1)))
            status = result['calculation_exit']
        print(formatted(result), end='')
        return status
    except (ReceiptError, worksheet.WorksheetError) as exc:
        print(f'worksheet-receipt: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
