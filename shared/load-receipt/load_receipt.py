#!/usr/bin/env python3
"""Replay interval-depth evidence and its exact dimensional accounting together."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / 'engines/timeline'))
sys.path.insert(0, str(HERE / 'engines/worksheet'))
import timeline_load as load
import worksheet_receipt as arithmetic

SCHEMA = 'load-receipt/1'
MAX_BYTES = 2 * 1024 * 1024
SOURCE_NAMES = ('load_receipt.py', 'engines/timeline/timeline_load.py',
                'engines/timeline/replay.py', 'engines/timeline/vendor/time_flint.py',
                'engines/timeline/vendor/__init__.py',
                'engines/worksheet/worksheet_receipt.py',
                'engines/worksheet/worksheet_flint.py', 'engines/worksheet/engine.py')
REQUEST_KEYS = {'pack', 'start', 'end', 'max_uncovered', 'max_mean_depth'}


def canonical(value):
    return load.replay.canonical(value)


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def sources():
    return {name: hashlib.sha256((HERE / name).read_bytes()).hexdigest()
            for name in SOURCE_NAMES}


def seconds(value):
    if type(value) is not int or value < 0:
        raise ValueError('duration must be nonnegative integer microseconds')
    return f'({value} / 1000000) * s'


def policy(expression, dims):
    if type(expression) is not str or not 1 <= len(expression) <= 4096:
        raise ValueError('policy must be a bounded quantity expression string')
    try:
        quantity = arithmetic.worksheet.engine.Parser(expression).parse()
    except arithmetic.worksheet.engine.UnitError as exc:
        raise ValueError('invalid policy expression: ' + str(exc)) from exc
    if quantity.dims != dims or quantity.value < 0:
        raise ValueError('policy must be nonnegative and have the required dimensions')
    return expression


def create(request):
    if type(request) is not dict or set(request) != REQUEST_KEYS:
        raise ValueError('request needs exactly pack, start, end, max_uncovered, max_mean_depth')
    if len(canonical(request)) > MAX_BYTES:
        raise ValueError('request exceeds 2 MiB')
    zero_budget = policy(request['max_uncovered'], (0, 0, 1, 0))
    depth_budget = policy(request['max_mean_depth'], (0, 0, 0, 0))
    # Never trust a supplied histogram: replay the entire embedded pack first.
    coverage = load.analyze(request['pack'], request['start'], request['end'], limit=0)
    histogram = {int(k): v for k, v in coverage['duration_by_depth_us'].items()}
    duration = coverage['window']['duration_us']
    partition = sum(histogram.values())
    weighted = sum(depth * elapsed for depth, elapsed in histogram.items())
    uncovered = histogram.get(0, 0)
    document = {'schema': 'worksheet-flint/1', 'steps': [
        {'name': 'window', 'expression': seconds(duration), 'to': 's'},
        {'name': 'partition', 'expression': seconds(partition), 'expect': '$window', 'to': 's'},
        {'name': 'interval_time', 'expression': seconds(weighted), 'to': 's'},
        {'name': 'uncovered', 'expression': seconds(uncovered), 'to': 's', 'at_most': zero_budget},
        {'name': 'covered', 'expression': '$window - $uncovered', 'to': 's'},
        {'name': 'accounted', 'expression': '$covered + $uncovered', 'expect': '$window', 'to': 's'},
        {'name': 'mean_depth', 'expression': '$interval_time / $window', 'at_most': depth_budget},
        {'name': 'covered_fraction', 'expression': '$covered / $window', 'at_least': '0', 'at_most': '1'}]}
    calculation = arithmetic.create(document)
    payload = {'schema': SCHEMA, 'sources_sha256': sources(),
               'request': copy.deepcopy(request), 'coverage': coverage,
               'worksheet_receipt': calculation, 'calculation_exit': calculation['calculation_exit']}
    result = {**payload, 'receipt_sha256': digest(payload)}
    if len(canonical(result)) + 1 > MAX_BYTES:
        raise ValueError('combined receipt exceeds 2 MiB; use a smaller evidence pack')
    return result


def verify(receipt, expected_sha256=None):
    keys = {'schema', 'sources_sha256', 'request', 'coverage', 'worksheet_receipt',
            'calculation_exit', 'receipt_sha256'}
    if type(receipt) is not dict or set(receipt) != keys or receipt['schema'] != SCHEMA:
        raise ValueError('invalid load receipt schema or fields')
    if len(canonical(receipt)) + 1 > MAX_BYTES:
        raise ValueError('combined receipt exceeds 2 MiB')
    if expected_sha256 is not None:
        if type(expected_sha256) is not str or re.fullmatch('[0-9a-f]{64}', expected_sha256) is None:
            raise ValueError('expected receipt SHA-256 must be 64 lowercase hex digits')
        if receipt['receipt_sha256'] != expected_sha256:
            raise ValueError('receipt differs from retained SHA-256')
    payload = {k: v for k, v in receipt.items() if k != 'receipt_sha256'}
    if receipt['receipt_sha256'] != digest(payload):
        raise ValueError('receipt content hash mismatch')
    if canonical(receipt['sources_sha256']) != canonical(sources()):
        raise ValueError('shipped source hashes changed')
    arithmetic.replay(receipt['worksheet_receipt'])
    recomputed = create(receipt['request'])
    if canonical(recomputed) != canonical(receipt):
        raise ValueError('receipt differs from fully replayed evidence and arithmetic')
    return {'verified': True, 'receipt_sha256': receipt['receipt_sha256'],
            'calculation_exit': receipt['calculation_exit'],
            'coverage': recomputed['coverage'],
            'worksheet_result': recomputed['worksheet_receipt']['result'],
            'interpretation': [
                'Depth is timestamp-uncertainty interval coverage, not confirmed concurrency or service load.',
                'Zero depth is not downtime; widening asserted clock bounds can change every total.',
                'Budgets are supplied policy, not statistical or availability guarantees.',
                'Replay checks internal consistency, not log truth, completeness or clock accuracy.',
                'Receipt embeds unredacted source logs; hashes do not establish authorship or creation time.',
                'Retain the content digest independently to identify a receipt; whitespace is not pinned.']}


def decode(raw):
    if not isinstance(raw, bytes) or len(raw) > MAX_BYTES:
        raise ValueError('input must be at most 2 MiB of UTF-8 JSON')
    def pairs(items):
        obj = {}
        for key, value in items:
            if key in obj:
                raise ValueError('duplicate JSON key')
            obj[key] = value
        return obj
    def integer(text):
        if len(text) > 20:
            raise ValueError('JSON integer exceeds 20 characters')
        return int(text)
    def forbidden(text):
        raise ValueError('JSON floats and nonfinite constants are unsupported')
    value = json.loads(raw.decode('utf-8'), object_pairs_hook=pairs,
                       parse_int=integer, parse_float=forbidden, parse_constant=forbidden)
    def depth(obj, level=0):
        if level > 24:
            raise ValueError('JSON nesting exceeds 24 levels')
        if isinstance(obj, dict):
            for item in obj.values():
                depth(item, level + 1)
        elif isinstance(obj, list):
            for item in obj:
                depth(item, level + 1)
    depth(value)
    return value


def demo_request(max_mean_depth='2'):
    return {'pack': load.replay.make_pack([('synthetic-worker.log',
        b'2026-10-18T10:00:01Z opened\n2026-10-18T10:00:02Z retried\n'
        b'undated diagnostic\n2026-10-18T10:00:03Z recovered\n')],
        ignore_unmatched=True, clock_uncertainty_ms=500),
        'start': '2026-10-18T10:00:00Z', 'end': '2026-10-18T10:00:05Z',
        'max_uncovered': '1 s', 'max_mean_depth': max_mean_depth}


def demo():
    good = create(demo_request())
    failed = create(demo_request('1'))
    forged = copy.deepcopy(good)
    forged['coverage']['duration_by_depth_us']['2'] += 1
    forged['receipt_sha256'] = digest({k: v for k, v in forged.items() if k != 'receipt_sha256'})
    try:
        verify(forged)
    except ValueError:
        rejected = True
    else:
        raise ValueError('demo failed to reject forged histogram')
    return {'example': 'synthetic evidence, asserted 500 ms clock bound; budgets are illustrative',
            'passing': verify(good, good['receipt_sha256']),
            'failed_claim': verify(failed, failed['receipt_sha256']),
            'rehashed_histogram_forgery_rejected': rejected}


def main(argv=None):
    cli = argparse.ArgumentParser(description=__doc__)
    commands = cli.add_subparsers(dest='command', required=True)
    commands.add_parser('demo')
    commands.add_parser('create', help='read request JSON on stdin; emit combined receipt')
    check = commands.add_parser('verify', help='read combined receipt JSON on stdin; recompute both engines')
    check.add_argument('--expected-sha256', required=True, help='independently retained receipt content digest')
    args = cli.parse_args(argv)
    try:
        if args.command == 'demo':
            result, status = demo(), 0
        elif args.command == 'create':
            result = create(decode(sys.stdin.buffer.read(MAX_BYTES + 1)))
            status = result['calculation_exit']
        else:
            result = verify(decode(sys.stdin.buffer.read(MAX_BYTES + 1)), args.expected_sha256)
            status = result['calculation_exit']
        output = canonical(result) + b'\n'
        if len(output) > MAX_BYTES:
            raise ValueError('serialized report exceeds 2 MiB')
    except (OSError, ValueError, OverflowError, RecursionError, TypeError, KeyError) as exc:
        print('load-receipt: ' + ascii(str(exc)), file=sys.stderr)
        return 2
    sys.stdout.buffer.write(output)
    return status


if __name__ == '__main__':
    raise SystemExit(main())
