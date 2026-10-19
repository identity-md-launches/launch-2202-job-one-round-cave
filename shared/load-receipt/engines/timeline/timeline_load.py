#!/usr/bin/env python3
"""Profile timestamp-interval coverage across a verified incident window."""

import argparse
from datetime import datetime
import re
import sys

import replay

FORMAT = 'timeline-load/1'
HEX = re.compile(r'[0-9a-f]{64}\Z')


def instant(value):
    """Parse a query endpoint as an exact UTC instant, never a log precision range."""
    if not isinstance(value, str):
        raise replay.ReplayError('endpoint must be offset-aware ISO text')
    match = replay.engine.ISO.fullmatch(value)
    if match is None:
        raise replay.ReplayError('endpoint needs offset-aware ISO text with at most 6 fractional digits')
    body, offset = match.groups()
    if offset != 'Z' and (int(offset[1:3]) > 23 or int(offset[4:]) > 59):
        raise replay.ReplayError('endpoint offset is outside ±23:59')
    return replay.engine.micros(datetime.fromisoformat(body + ('+00:00' if offset == 'Z' else offset)))


def profile(intervals, start, end):
    """Return maximal constant-depth half-open spans, including depth zero."""
    if start >= end:
        raise replay.ReplayError('window start must precede end')
    changes = {start: 0, end: 0}
    for a, b in intervals:
        if a >= b:
            raise replay.ReplayError('event interval must have positive duration')
        a, b = max(start, a), min(end, b)
        if a < b:
            changes[a] = changes.get(a, 0) + 1
            changes[b] = changes.get(b, 0) - 1
    points = sorted(changes)
    spans = []
    depth = 0
    for a, b in zip(points, points[1:]):
        depth += changes[a]
        if a < b:
            if spans and spans[-1][2] == depth:
                spans[-1] = (spans[-1][0], b, depth)
            else:
                spans.append((a, b, depth))
    if depth + changes[end] != 0 or not spans or spans[0][0] != start or spans[-1][1] != end:
        raise replay.ReplayError('coverage sweep did not partition the window')
    return spans


def analyze(pack, start_text, end_text, limit=50):
    if type(limit) is not int or not 0 <= limit <= 200:
        raise replay.ReplayError('limit must be an integer in 0..200')
    start, end = instant(start_text), instant(end_text)
    if start >= end:
        raise replay.ReplayError('window start must precede end')
    checked = replay.verify_pack(pack)  # Full replay, including outside the query.
    events = pack['timeline']['events']
    intervals = [(instant(event['start_utc']), instant(event['end_utc_exclusive']))
                 for event in events]
    spans = profile(intervals, start, end)
    histogram = {}
    for a, b, depth in spans:
        histogram[depth] = histogram.get(depth, 0) + b - a
    maximum = max(histogram)
    def describe(a, b, depth):
        return {'start_utc_inclusive': replay.engine.utc_text(a),
                'end_utc_exclusive': replay.engine.utc_text(b),
                'duration_us': b - a, 'interval_depth': depth}
    return {
        'format': FORMAT, 'replay': checked,
        'window': {'start_utc_inclusive': replay.engine.utc_text(start),
                   'end_utc_exclusive': replay.engine.utc_text(end),
                   'duration_us': end - start},
        'counts': {'timestamped_events': len(events),
                   'intersecting_events': sum(a < end and b > start for a, b in intervals),
                   'undated_lines': len(pack['timeline']['omitted']),
                   'segments_total': len(spans), 'segments_shown': min(limit, len(spans)),
                   'segments_not_shown': max(0, len(spans) - limit),
                   'maximum_interval_depth': maximum},
        'duration_by_depth_us': {str(depth): histogram[depth] for depth in sorted(histogram)},
        'segments': [describe(*span) for span in spans[:limit]],
        'engine_sha256': pack['engine_sha256'], 'options': dict(pack['options']),
        'interpretation': (
            'Depth counts timestamp uncertainty intervals compatible with each instant; '
            'it does not count confirmed simultaneous events or measure service load. '
            'Zero depth means no dated interval covers that span in this evidence model, '
            'not proof of inactivity. Undated lines cannot be placed. Clock bounds are '
            'analyst assertions. Replay checks consistency, not authenticity or completeness. '
            'Source bytes and messages are omitted from this report.')}


def demo():
    pack = replay.make_pack([('worker.log',
        b'2026-10-18T10:00:01Z opened\n'
        b'2026-10-18T10:00:02Z retried\n'
        b'untimestamped diagnostic\n'
        b'2026-10-18T10:00:03Z recovered\n')],
        clock_uncertainty_ms=500, ignore_unmatched=True)
    result = analyze(pack, '2026-10-18T10:00:00Z', '2026-10-18T10:00:05Z')
    result['example'] = 'synthetic, not a real incident'
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('demo', help='show a synthetic coverage profile')
    inspect = commands.add_parser('analyze', help='profile a verified evidence pack')
    inspect.add_argument('pack')
    inspect.add_argument('--start', required=True, help='inclusive offset-aware ISO instant')
    inspect.add_argument('--end', required=True, help='exclusive offset-aware ISO instant')
    inspect.add_argument('--limit', type=int, default=50, help='show 0..200 segments')
    inspect.add_argument('--expect-sha256', help='independently trusted exact pack digest')
    args = parser.parse_args(argv)
    try:
        if args.command == 'demo':
            result = demo()
        else:
            raw = replay.read_workspace(args.pack, replay.MAX_PACK_BYTES)
            digest = replay.digest(raw)
            if args.expect_sha256 is not None:
                if HEX.fullmatch(args.expect_sha256) is None:
                    raise replay.ReplayError('expected digest must be 64 lowercase hex digits')
                if digest != args.expect_sha256:
                    raise replay.ReplayError('pack does not match expected SHA-256')
            result = analyze(replay.load_pack(raw), args.start, args.end, args.limit)
            result['pack_sha256'] = digest
        sys.stdout.buffer.write(replay.canonical(result) + b'\n')
        return 0
    except (OSError, ValueError, OverflowError, RecursionError) as exc:
        print('timeline-load: ' + replay.engine.visible(str(exc)), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
