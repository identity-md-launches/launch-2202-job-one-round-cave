#!/usr/bin/env python3
"""Offline structural review of literal UTF-8 bidirectional controls."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys
import unicodedata as ud

MAX_BYTES = 2 * 1024 * 1024
MAX_CONTROLS = 4096
MAX_DETAILS = 1000
MAX_OUTPUT = 4 * 1024 * 1024
EMBED = frozenset(('LRE', 'RLE', 'LRO', 'RLO'))
ISOLATE = frozenset(('LRI', 'RLI', 'FSI'))
CODES = {0x202a: 'LRE', 0x202b: 'RLE', 0x202d: 'LRO', 0x202e: 'RLO',
         0x202c: 'PDF', 0x2066: 'LRI', 0x2067: 'RLI', 0x2068: 'FSI',
         0x2069: 'PDI', 0x200e: 'LRM', 0x200f: 'RLM', 0x061c: 'ALM'}
DEMO = 'ok \u2067name \u202evalue\u202c\u2069\nignored \u2066\u202c\u2069\nopen \u202evalue\nextra \u2069\n'.encode('utf-8')


def escaped_bytes(raw):
    return ''.join(chr(b) if 32 <= b <= 126 and b != 92 else
                   '\\\\' if b == 92 else '\\x%02x' % b for b in raw)


def citation(raw, start, end, line, column):
    return dict(byte_start=start, byte_end=end, line=line, byte_column=column,
                bytes_hex=raw[start:end].hex(),
                before=escaped_bytes(raw[max(0, start-16):start]),
                after=escaped_bytes(raw[end:end+16]))


def review(raw, source='<memory>', max_details=100):
    """Match lexical scopes, without computing rendering or embedding levels.

    An isolate is a barrier for PDF. PDI ends its nearest isolate and any
    embeddings nested in it. B-class paragraph separators end all open scopes.
    No maximum rendering depth or overflow counters are simulated.
    """
    if not isinstance(raw, bytes) or len(raw) > MAX_BYTES:
        raise ValueError('input must be bytes, at most %d bytes' % MAX_BYTES)
    if not isinstance(source, str) or len(source.encode('utf-8')) > 1024:
        raise ValueError('source label must be a string of at most 1024 UTF-8 bytes')
    if type(max_details) is not int or not 1 <= max_details <= MAX_DETAILS:
        raise ValueError('max_details must be 1..%d' % MAX_DETAILS)
    text = raw.decode('utf-8', errors='strict')
    events, stack = [], []
    offset, line, line_start, max_depth = 0, 1, 0, 0

    def finish(index, status, closer=None, boundary=None):
        item = events[index]
        item['status'] = status
        item['closing_control'] = closer
        item['boundary'] = boundary
        end = (events[closer]['source']['byte_start'] if closer is not None else
               boundary['byte_start'] if boundary else len(raw))
        item['content_range'] = dict(byte_start=item['source']['byte_end'], byte_end=end)

    for char in text:
        end = offset + len(char.encode('utf-8'))
        code = CODES.get(ord(char))
        if code:
            if len(events) >= MAX_CONTROLS:
                raise ValueError('input exceeds %d controls; no partial report produced' % MAX_CONTROLS)
            index = len(events)
            item = dict(index=index, control=code, codepoint='U+%04X' % ord(char),
                        unicode_name=ud.name(char),
                        source=citation(raw, offset, end, line, offset-line_start+1),
                        status='directional-mark', opening_control=None,
                        closing_control=None, boundary=None, content_range=None)
            events.append(item)
            if code in EMBED | ISOLATE:
                item['status'] = 'open-at-eof'
                stack.append(index)
                max_depth = max(max_depth, len(stack))
            elif code == 'PDF':
                if stack and events[stack[-1]]['control'] in EMBED:
                    opener = stack.pop()
                    finish(opener, 'closed-by-pdf', index)
                    item.update(status='matched-pdf', opening_control=opener)
                elif stack:
                    item['status'] = 'ignored-pdf-at-isolate'
                else:
                    item['status'] = 'unmatched-pdf'
            elif code == 'PDI':
                # Search without popping: unmatched PDI must leave embeddings intact.
                found = next((n for n in range(len(stack)-1, -1, -1)
                              if events[stack[n]]['control'] in ISOLATE), None)
                if found is None:
                    item['status'] = 'unmatched-pdi'
                else:
                    while len(stack)-1 > found:
                        finish(stack.pop(), 'embedding-ended-by-pdi', index)
                    opener = stack.pop()
                    finish(opener, 'closed-by-pdi', index)
                    item.update(status='matched-pdi', opening_control=opener)
        elif ud.bidirectional(char) == 'B' and stack:
            boundary = citation(raw, offset, end, line, offset-line_start+1)
            boundary['codepoint'] = 'U+%04X' % ord(char)
            while stack:
                finish(stack.pop(), 'ended-at-paragraph', boundary=boundary)
        if char == '\n':
            line += 1
            line_start = end
        offset = end
    while stack:
        finish(stack.pop(), 'open-at-eof')
    counts = dict(sorted(Counter(e['status'] for e in events).items()))
    return dict(schema_version=1, tool='bidi-scope/1',
                source=source.encode('unicode_escape').decode('ascii'),
                source_sha256=hashlib.sha256(raw).hexdigest(), source_bytes=len(raw),
                unicode_version=ud.unidata_version,
                engine_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                controls=len(events), status_counts=counts, max_lexical_depth=max_depth,
                analysis_complete=True, retained_details=min(max_details, len(events)),
                omitted_details=max(0, len(events)-max_details),
                events=events[:max_details],
                assessment='review-controls' if events else 'no-covered-controls',
                coordinates='Zero-based half-open original byte ranges and event indexes; '
                            'one-based lines/byte columns; only LF increments the line.',
                model='Lexical scopes: PDF closes a top embedding but never crosses an isolate; '
                      'PDI ends the nearest isolate and its inner embeddings; '
                      'Unicode B-class characters end open scopes; EOF retains open-at-eof.',
                limitations=[
                    'Not the Unicode Bidirectional Algorithm or a display-order prediction.',
                    'No embedding levels, depth overflow, FSI direction, paired-bracket or glyph analysis.',
                    'Rendering depth limits may cause actual controls to be ignored differently.',
                    'Literal UTF-8 only: no JSON/source escapes, HTML markup or language parsing.',
                    'Controls can be legitimate; balanced scopes do not establish safety or intent.',
                    'Does not detect lookalikes, other invisible characters or all Unicode risks.',
                    'Contexts are unredacted, at most 16 bytes per side, and may split UTF-8 characters.',
                    'All totals and relationships computed before detail truncation; referenced indexes '
                    'may be omitted. Increase max_details to inspect them (up to 1000).',
                    'Hashes identify bytes, not authorship, authenticity or trustworthy provenance.'])


def render(report):
    result = json.dumps(report, ensure_ascii=True, indent=2, sort_keys=True, allow_nan=False) + '\n'
    if len(result) > MAX_OUTPUT:
        raise ValueError('output budget exceeded; reduce max_details')
    return result


class Parser(argparse.ArgumentParser):
    def error(self, message):
        self.exit(2, json.dumps({'error': message}, ensure_ascii=True) + '\n')


def main(argv=None):
    parser = Parser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--demo', action='store_true', help='built-in synthetic cases')
    group.add_argument('--file', help='explicit UTF-8 file within current workspace')
    parser.add_argument('--max-details', type=int, default=100)
    args = parser.parse_args(argv)
    try:
        if args.demo:
            raw, source = DEMO, '<synthetic-demo>'
        else:
            root = Path.cwd().resolve()
            path = Path(args.file).resolve()
            if not path.is_relative_to(root) or not path.is_file():
                raise ValueError('input must be a regular file resolving inside the current workspace')
            with path.open('rb') as handle:
                raw = handle.read(MAX_BYTES+1)
            source = str(path.relative_to(root))
        report = review(raw, source, args.max_details)
        result = render(report)
        sys.stdout.write(result)
        return 0 if args.demo or not report['controls'] else 1
    except (OSError, UnicodeError, ValueError, OverflowError) as error:
        sys.stderr.write(json.dumps({'error': str(error)}, ensure_ascii=True) + '\n')
        return 2


if __name__ == '__main__':
    sys.exit(main())
