#!/usr/bin/env python3
"""Compare covered Unicode finding occurrences in two original UTF-8 files."""

import argparse
from collections import defaultdict, deque
import hashlib
import importlib.util
import json
from pathlib import Path
import sys


VIEWER_PATH = Path(__file__).resolve().parents[1] / 'unicode-text-window' / 'unicode_text_window.py'
_spec = importlib.util.spec_from_file_location('delta_text_window', VIEWER_PATH)
window = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(window)
lantern = window.lantern

VERSION = '1.0.0'
MAX_BYTES = lantern.MAX_BYTES
MAX_FINDINGS = lantern.MAX_FINDINGS
MAX_CHANGES = 1000
MAX_LABEL_BYTES = 1024
MAX_OUTPUT = 4 * 1024 * 1024
SEMANTIC_PREVIEW = 128
POSITION_KEYS = frozenset({'line', 'column', 'char_offset', 'byte_offset'})
NON_SEMANTIC_KEYS = POSITION_KEYS | {'rule', 'escaped', 'explanation', 'first'}

# Synthetic input: the same zero-width space moves, a non-breaking space is
# removed, and a right-to-left override is added. No external file is needed.
DEMO_BEFORE = 'owner = 1\nname\u200b = 2\nprice\u00a0= 3\n'.encode('utf-8')
DEMO_AFTER = '# inserted line\nowner = 1\nname\u200b = 2\nprice = 3\n# \u202e\n'.encode('utf-8')


def _json(value):
    return json.dumps(value, ensure_ascii=True, sort_keys=True,
                      separators=(',', ':'), allow_nan=False)


def _label(value, name):
    if not isinstance(value, str):
        raise ValueError(name + ' must be a string')
    if len(value.encode('utf-8', errors='strict')) > MAX_LABEL_BYTES:
        raise ValueError(name + ' exceeds %d UTF-8 bytes' % MAX_LABEL_BYTES)
    return lantern.escaped(value)


def _signature(finding):
    """Exact matching key; locations, explanations and excerpts are excluded."""
    semantic = {key: value for key, value in finding.items()
                if key not in NON_SEMANTIC_KEYS}
    # JSON retains types and lists and gives semantic mappings a stable order.
    # The spelling is the scanner's reversible unicode_escape representation.
    return (finding['rule'], finding['escaped'], _json(semantic),
            finding['first']['escaped'] if 'first' in finding else None)


def _summary(value):
    """Bound a scanner-produced escaped string without changing match identity."""
    return dict(escaped_preview=value[:SEMANTIC_PREVIEW],
                escaped_characters=len(value),
                escaped_sha256=hashlib.sha256(value.encode('ascii')).hexdigest(),
                omitted_escaped_characters=max(0, len(value) - SEMANTIC_PREVIEW))


def _semantic_view(finding):
    semantic = {}
    for key, value in finding.items():
        if key in NON_SEMANTIC_KEYS:
            continue
        # Normalized identifiers and skeletons can be as long as an input file.
        # Their complete escaped values still participate in exact matching.
        semantic[key] = _summary(value) if key in {'normalized', 'skeleton'} else value
    return semantic


def _occurrence(raw, finding, index):
    item = dict(finding_index=index + 1, source=window.evidence(raw, finding))
    if 'first' in finding:
        item['first_source'] = window.evidence(raw, finding['first'])
    return item


def _engine(path, name, version):
    return dict(tool=name, version=version,
                source_sha256=hashlib.sha256(path.read_bytes()).hexdigest())


def review(before, after, before_label='<before>', after_label='<after>', max_changes=100):
    """Return complete occurrence totals and capped original-byte evidence.

    Pair exact finding signatures as multisets, earliest occurrence first.
    This compares findings, not edits or contextual safety. Either incomplete
    scanner report is an error even when the requested detail limit is small.
    """
    if type(max_changes) is not int or not 1 <= max_changes <= MAX_CHANGES:
        raise ValueError('max_changes must be between 1 and %d' % MAX_CHANGES)
    labels = dict(before=_label(before_label, 'before_label'),
                  after=_label(after_label, 'after_label'))
    for name, raw in (('before', before), ('after', after)):
        if not isinstance(raw, bytes):
            raise ValueError(name + ' input must be UTF-8 bytes')
        if len(raw) > MAX_BYTES:
            raise ValueError(name + ' input exceeds %d bytes' % MAX_BYTES)
        # Validate every byte before scanning or retaining any detail.
        raw.decode('utf-8', errors='strict')

    scans = dict(before=lantern.scan(before, before_label, MAX_FINDINGS),
                 after=lantern.scan(after, after_label, MAX_FINDINGS))
    for name, scan in scans.items():
        if scan['truncated'] or scan['finding_count'] != len(scan['findings']):
            raise ValueError('%s scan exceeds the complete-comparison limit of %d findings' %
                             (name, MAX_FINDINGS))

    old, new = scans['before']['findings'], scans['after']['findings']
    previous = defaultdict(deque)
    for index, finding in enumerate(old):
        previous[_signature(finding)].append(index)

    added, persisting, matched = [], [], set()
    for index, finding in enumerate(new):
        candidates = previous.get(_signature(finding))
        if candidates:
            old_index = candidates.popleft()
            matched.add(old_index)
            persisting.append((old_index, index))
        else:
            added.append((None, index))
    removed = [(index, None) for index in range(len(old)) if index not in matched]

    # Changed occurrences have priority when the user requests a short report.
    ordered = ([('added', *pair) for pair in added] +
               [('removed', *pair) for pair in removed] +
               [('persisting', *pair) for pair in persisting])
    details = []
    for status, old_index, new_index in ordered[:max_changes]:
        finding = new[new_index] if new_index is not None else old[old_index]
        identity = _signature(finding)
        details.append(dict(
            status=status, rule=finding['rule'], explanation=finding['explanation'],
            signature_sha256=hashlib.sha256(_json(identity).encode('ascii')).hexdigest(),
            semantic_data=_semantic_view(finding),
            before=_occurrence(before, old[old_index], old_index) if old_index is not None else None,
            after=_occurrence(after, new[new_index], new_index) if new_index is not None else None))

    sources = {name: dict(label=labels[name], sha256=scan['sha256'],
                         bytes=scan['bytes'], finding_count=scan['finding_count'])
               for name, scan in scans.items()}
    return dict(
        schema_version=1, tool='unicode-delta', tool_version=VERSION,
        sources=sources, unicode_version=scans['before']['unicode_version'],
        engines=dict(scanner=_engine(window.ENGINE, 'unicode-lantern', lantern.VERSION),
                     evidence=_engine(VIEWER_PATH, 'unicode-text-window', '1')),
        counts=dict(before=len(old), after=len(new), added=len(added),
                    removed=len(removed), persisting=len(persisting)),
        comparison_complete=True, max_changes=max_changes,
        retained_details=len(details), omitted_details=len(ordered) - len(details),
        details_truncated=len(details) < len(ordered), changes=details,
        assessment='added-covered-findings' if added else 'no-added-covered-findings',
        coordinates=dict(ranges='zero-based half-open original byte offsets',
                         line_and_byte_column='one-based; only LF starts a line',
                         finding_index='one-based scanner order, separately in each input'),
        matching='Exact rule, implicated spelling, semantic data and first witness spelling; '
                 'first-to-first multiset pairing, excluding positions and context.',
        detail_order='Added in after order, removed in before order, persisting in after order.',
        limitations=[
            'Heuristic triage, not proof of deception or absence of deception.',
            'This is occurrence comparison, not edit tracking or a contextual safety verdict.',
            'Moved or context-changed occurrences with identical signatures persist.',
            'Reordering identifiers can change the first collision witness and reported statuses.',
            'Each file is scanned independently; no cross-file collision detection.',
            'Limited Latin/Greek/Cyrillic mapping, not full Unicode confusables.',
            'Not a language parser; identifiers in comments and strings also count.',
            'Raw UTF-8 only; literal backslash escapes are not decoded as JSON or source code.',
            'Byte evidence is unredacted and may split UTF-8 characters.',
            'Excerpts contain at most 16 context bytes per side and 64 implicated bytes.',
            'Semantic previews may be cut inside an escape; do not parse them as complete escapes.',
            'Hashes identify bytes, not authorship or authenticity; matching uses exact values, not hashes.',
            'A detail limit omits evidence objects but never changes the complete counts.',
        ])


def render(report):
    """Serialize a report completely before any CLI output is written."""
    if not isinstance(report, dict):
        raise ValueError('report must be a dictionary')
    text = json.dumps(report, ensure_ascii=True, sort_keys=True, indent=2,
                      allow_nan=False) + '\n'
    if len(text) > MAX_OUTPUT:
        raise ValueError('render exceeds output budget; lower max_changes')
    if any(char != '\n' and not 32 <= ord(char) <= 126 for char in text):
        raise ValueError('render violated printable ASCII contract')
    return text


class _Parser(argparse.ArgumentParser):
    def error(self, message):
        # argparse errors may incorporate attacker-controlled option values.
        self.exit(2, _json({'error': lantern.escaped(message)}) + '\n')


def _read_input(value):
    path = lantern.workspace_file(value)
    with path.open('rb') as handle:
        raw = handle.read(MAX_BYTES + 1)
    return raw, str(path.relative_to(Path.cwd().resolve()))


def main(argv=None):
    parser = _Parser(description=__doc__)
    parser.add_argument('--before', help='explicit original UTF-8 file within the current workspace')
    parser.add_argument('--after', help='explicit revised UTF-8 file within the current workspace')
    parser.add_argument('--demo', action='store_true', help='compare built-in synthetic inputs')
    parser.add_argument('--max-changes', type=int, default=100,
                        help='retained evidence details, 1..1000; totals stay complete (default: 100)')
    args = parser.parse_args(argv)
    if args.demo and (args.before is not None or args.after is not None):
        parser.error('--demo cannot be combined with --before or --after')
    if not args.demo and (args.before is None or args.after is None):
        parser.error('choose --demo or provide both --before and --after')
    try:
        if args.demo:
            before, after = DEMO_BEFORE, DEMO_AFTER
            before_label, after_label = '<synthetic-demo-before>', '<synthetic-demo-after>'
        else:
            before, before_label = _read_input(args.before)
            after, after_label = _read_input(args.after)
        report = review(before, after, before_label, after_label, args.max_changes)
        text = render(report)
        sys.stdout.write(text)
        return 0 if args.demo or not report['counts']['added'] else 1
    except (OSError, UnicodeError, ValueError, OverflowError) as error:
        sys.stderr.write(_json({'error': lantern.escaped(str(error))}) + '\n')
        return 2


if __name__ == '__main__':
    sys.exit(main())
