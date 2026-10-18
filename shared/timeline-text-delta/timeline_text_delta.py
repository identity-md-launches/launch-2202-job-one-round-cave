#!/usr/bin/env python3
"""Review a changed log source through replayed time and original-byte text evidence."""

import argparse
import base64
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
TIMELINE = HERE / 'engines/timeline'
UNICODE = HERE / 'engines/unicode/unicode-delta/unicode_delta.py'
sys.path.insert(0, str(TIMELINE))
spec = importlib.util.spec_from_file_location('shared_timeline_diff', TIMELINE / 'timeline_diff.py')
timeline_diff = importlib.util.module_from_spec(spec)
spec.loader.exec_module(timeline_diff)
spec = importlib.util.spec_from_file_location('shared_unicode_delta', UNICODE)
unicode_delta = importlib.util.module_from_spec(spec)
spec.loader.exec_module(unicode_delta)

HEX = re.compile(r'[0-9a-f]{64}\Z')
MAX_OUTPUT = 5 * 1024 * 1024


def source_bytes(pack, name):
    for row in pack['inputs']:
        if row['source'] == name:
            return base64.b64decode(row['base64'], validate=True)
    raise ValueError('selected source is absent from one timeline pack')


def review(before, after, source, left, right, max_changes=20):
    """Verify both packs, compare their timeline, then scan a selected raw source.

    Both engines recompute their own evidence. The cited event pair can use any
    source in the packs; the Unicode review selects one source present in both.
    """
    if not isinstance(source, str) or not source:
        raise ValueError('source must be a nonempty name')
    time = timeline_diff.compare(before, after, left[0], left[1], right[0], right[1])
    old = source_bytes(before, source)
    new = source_bytes(after, source)
    text = unicode_delta.review(old, new, source + ' (before)',
                                source + ' (after)', max_changes)
    return {
        'format': 'timeline-text-delta/1', 'selected_source': source,
        'timeline': time, 'unicode': text,
        'joint_observation': {
            'selected_source_bytes_changed': hashlib.sha256(old).digest() != hashlib.sha256(new).digest(),
            'selected_source_timeline_line_changes': sum(
                item['source'] == source for item in time['line_changes']['shown']),
            'selected_source_line_change_count_is_capped': time['line_changes']['omitted_details'] > 0,
            'added_covered_unicode_findings': text['counts']['added'],
            'cited_pair_assessment': time['pair']['assessment'],
            'cited_pair_relation_before': time['pair']['before']['relation'],
            'cited_pair_relation_after': time['pair']['after']['relation'],
        },
        'limits': [
            'Timeline citations are physical line positions; moved lines are not tracked as the same event.',
            'Time intervals depend on supplied timestamp precision and asserted clock bounds.',
            'Unicode findings are heuristic, limited to the bundled scanner, and do not establish deception.',
            'The two reviews share exact source bytes but neither establishes provenance, completeness or causality.',
            'The selected Unicode source must be present in both packs and strict UTF-8.',
            'Evidence excerpts are unredacted; review only sources whose text may be disclosed.',
        ],
    }


def checked_pack(path, expected):
    if HEX.fullmatch(expected) is None:
        raise ValueError('expected SHA-256 must be 64 lowercase hex digits')
    raw = timeline_diff.replay.read_workspace(path, timeline_diff.replay.MAX_PACK_BYTES)
    actual = hashlib.sha256(raw).hexdigest()
    if actual != expected:
        raise ValueError('pack does not match retained SHA-256')
    return timeline_diff.replay.load_pack(raw), actual


def demo():
    before = timeline_diff.replay.make_pack([
        ('worker.log', b'2026-10-18T10:00:00Z queue ready\n'),
        ('server.log', b'2026-10-18T10:00:02Z received\n')])
    after = timeline_diff.replay.make_pack([
        ('worker.log', '2026-10-18T10:00:03Z queue \u202eready\n'.encode('utf-8')),
        ('server.log', b'2026-10-18T10:00:02Z received\n')])
    result = review(before, after, 'worker.log', ('worker.log', 1), ('server.log', 1), 2)
    result['example'] = 'synthetic, not a real incident or proof of deception'
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('demo', help='run a synthetic example with a text and order change')
    command = commands.add_parser('review', help='review two pinned workspace timeline packs')
    command.add_argument('before')
    command.add_argument('after')
    command.add_argument('--expect-before-sha256', required=True)
    command.add_argument('--expect-after-sha256', required=True)
    command.add_argument('--source', required=True, help='source name to scan in both packs')
    command.add_argument('--left', nargs=2, required=True, metavar=('SOURCE', 'LINE'))
    command.add_argument('--right', nargs=2, required=True, metavar=('SOURCE', 'LINE'))
    command.add_argument('--max-changes', type=int, default=20)
    args = parser.parse_args(argv)
    try:
        if args.command == 'demo':
            result = demo()
        else:
            before, before_hash = checked_pack(args.before, args.expect_before_sha256)
            after, after_hash = checked_pack(args.after, args.expect_after_sha256)
            left = (args.left[0], int(args.left[1]))
            right = (args.right[0], int(args.right[1]))
            result = review(before, after, args.source, left, right, args.max_changes)
            result['before_pack_sha256'] = before_hash
            result['after_pack_sha256'] = after_hash
        encoded = json.dumps(result, ensure_ascii=True, sort_keys=True, separators=(',', ':'),
                             allow_nan=False).encode('ascii') + b'\n'
        if len(encoded) > MAX_OUTPUT:
            raise ValueError('output exceeds 5 MiB; lower max-changes')
        sys.stdout.buffer.write(encoded)
        return 0
    except (OSError, ValueError, TypeError, OverflowError, RecursionError) as exc:
        print('timeline-text-delta: ' + json.dumps(str(exc), ensure_ascii=True), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
