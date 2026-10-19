"""Behavior tests: run with python3 -B .../test_bidi_scope.py."""
import importlib.util
import json
from pathlib import Path
import random
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('bidi_scope', HERE/'bidi_scope.py')
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)
CHARS = {name: chr(cp) for cp, name in b.CODES.items()}


def run(*codes, **kwargs):
    return b.review(''.join(CHARS.get(c, c) for c in codes).encode(), **kwargs)


class ScopeTests(unittest.TestCase):
    def test_nested_embeddings(self):
        r = run('RLO', 'LRE', 'x', 'PDF', 'PDF')
        self.assertEqual([e['status'] for e in r['events']],
                         ['closed-by-pdf', 'closed-by-pdf', 'matched-pdf', 'matched-pdf'])
        self.assertEqual([e['closing_control'] for e in r['events'][:2]], [3, 2])
        self.assertEqual(r['max_lexical_depth'], 2)

    def test_isolate_barrier(self):
        r = run('RLO', 'LRI', 'PDF', 'PDI', 'PDF')
        self.assertEqual(r['events'][2]['status'], 'ignored-pdf-at-isolate')
        self.assertEqual(r['events'][0]['closing_control'], 4)
        self.assertEqual(r['events'][1]['closing_control'], 3)

    def test_pdi_ends_inner_embeddings(self):
        r = run('RLI', 'RLO', 'LRE', 'PDI')
        self.assertEqual(r['status_counts'], {'closed-by-pdi': 1,
                         'embedding-ended-by-pdi': 2, 'matched-pdi': 1})
        self.assertEqual(r['events'][3]['opening_control'], 0)
        for e in r['events'][:3]:
            self.assertEqual(e['closing_control'], 3)

    def test_pdi_nearest_isolate(self):
        r = run('LRI', 'FSI', 'RLO', 'PDI', 'PDI')
        self.assertEqual([e['closing_control'] for e in r['events'][:3]], [4, 3, 3])

    def test_unmatched_pdi_preserves_embedding(self):
        r = run('RLO', 'PDI', 'PDF', 'PDF')
        self.assertEqual([e['status'] for e in r['events']],
                         ['closed-by-pdf', 'unmatched-pdi', 'matched-pdf', 'unmatched-pdf'])

    def test_all_paragraph_boundaries(self):
        for char in ('\n', '\r', '\x1c', '\x1d', '\x1e', '\x85', '\u2029'):
            with self.subTest(char=repr(char)):
                r = run('LRI', 'RLO', char, 'PDF', 'PDI')
                self.assertEqual(r['events'][0]['status'], 'ended-at-paragraph')
                self.assertEqual(r['events'][1]['status'], 'ended-at-paragraph')
                self.assertEqual(r['events'][2]['status'], 'unmatched-pdf')
                boundary = r['events'][0]['boundary']
                self.assertEqual(boundary['bytes_hex'], char.encode().hex())
                self.assertEqual(boundary['byte_start'], 6)

    def test_line_separator_is_not_paragraph(self):
        r = run('RLO', '\u2028', 'PDF')
        self.assertEqual(r['events'][0]['status'], 'closed-by-pdf')

    def test_eof_range(self):
        r = run('LRI', 'RLO', '\u00e9')
        self.assertEqual(r['status_counts'], {'open-at-eof': 2})
        self.assertEqual(r['events'][1]['content_range'], {'byte_start': 6, 'byte_end': 8})

    def test_marks_do_not_push(self):
        r = run('LRM', 'RLM', 'ALM', 'PDF')
        self.assertEqual(r['status_counts'], {'directional-mark': 3, 'unmatched-pdf': 1})
        self.assertEqual(r['max_lexical_depth'], 0)

    def test_byte_citations(self):
        raw = '\u00e9\n\U0001f438\u202eabc\u202c'.encode()
        r = b.review(raw)
        e = r['events'][0]
        self.assertEqual(e['source']['byte_start'], 7)
        self.assertEqual(e['source']['byte_end'], 10)
        self.assertEqual((e['source']['line'], e['source']['byte_column']), (2, 5))
        self.assertEqual(e['content_range'], {'byte_start': 10, 'byte_end': 13})
        for event in r['events']:
            s = event['source']
            self.assertEqual(raw[s['byte_start']:s['byte_end']].hex(), s['bytes_hex'])

    def test_detail_limit_does_not_change_analysis(self):
        raw = (CHARS['RLO'] + CHARS['PDF'])*40
        full, short = b.review(raw.encode(), max_details=100), b.review(raw.encode(), max_details=1)
        self.assertEqual(full['status_counts'], short['status_counts'])
        self.assertEqual(short['omitted_details'], 79)
        self.assertEqual(short['events'][0]['closing_control'], 1)
        self.assertTrue(short['analysis_complete'])

    def test_invalid_utf8_after_control(self):
        with self.assertRaises(UnicodeError):
            b.review(CHARS['RLO'].encode()+b'\xff')

    def test_bounds(self):
        for value in (0, -1, 1001, True, 1.5):
            with self.assertRaises(ValueError):
                b.review(b'', max_details=value)
        for raw in ('text', bytearray(), b'x'*(b.MAX_BYTES+1)):
            with self.assertRaises(ValueError):
                b.review(raw)
        with self.assertRaises(ValueError):
            b.review((CHARS['LRM']*(b.MAX_CONTROLS+1)).encode())
        self.assertEqual(b.review((CHARS['LRM']*b.MAX_CONTROLS).encode())['controls'], b.MAX_CONTROLS)
        with self.assertRaises(ValueError):
            b.review(b'', source='x'*1025)

    def test_inert_render(self):
        r = b.review(('\x1b[31m\u202e\\\u2069').encode(), source='\x1b\u202e')
        out = b.render(r)
        self.assertTrue(all(c == '\n' or 32 <= ord(c) <= 126 for c in out))
        decoded = json.loads(out)
        self.assertTrue(all(32 <= ord(c) <= 126 for c in decoded['source']))
        for event in decoded['events']:
            self.assertTrue(all(32 <= ord(c) <= 126 for c in event['source']['before']))

    def test_literal_escapes_are_not_decoded(self):
        self.assertEqual(b.review(b'"\\u202e"')['controls'], 0)

    def test_no_controls_is_not_safety(self):
        r = b.review('p\u0430ypal\u200b'.encode())
        self.assertEqual(r['assessment'], 'no-covered-controls')
        self.assertTrue(r['limitations'])

    def test_generated_balanced_pairs(self):
        rng = random.Random(931)
        # Generate valid scope trees and retain independent expected byte ranges.
        def tree(depth):
            opening = rng.choice(['LRE', 'RLE', 'LRO', 'RLO', 'LRI', 'RLI', 'FSI'])
            closing = 'PDF' if opening in b.EMBED else 'PDI'
            children = [tree(depth-1) for _ in range(rng.randrange(3))] if depth else []
            raw = CHARS[opening].encode() + b'z'
            expected = []
            for child, spans in children:
                base = len(raw)
                expected.extend((a+base, z+base) for a, z in spans)
                raw += child
            expected.append((0, len(raw)))
            return raw+CHARS[closing].encode(), expected
        for _ in range(150):
            raw, expected = tree(4)
            report = b.review(raw, max_details=1000)
            actual = []
            for e in report['events']:
                if e['control'] in b.EMBED | b.ISOLATE:
                    closer = report['events'][e['closing_control']]
                    actual.append((e['source']['byte_start'], closer['source']['byte_start']))
            self.assertEqual(sorted(expected), sorted(actual))
            self.assertEqual(report['controls'], 2*len(expected))

    def test_portable_cli_and_exit_statuses(self):
        with tempfile.TemporaryDirectory(dir='/tmp', prefix='bidi-scope-test-') as tmp:
            root = Path(tmp)
            shutil.copyfile(HERE/'bidi_scope.py', root/'bidi_scope.py')
            def cli(*args):
                return subprocess.run([sys.executable, '-B', 'bidi_scope.py', *args],
                                      cwd=root, capture_output=True)
            self.assertEqual(cli('--demo').returncode, 0)
            (root/'data').write_bytes(CHARS['RLO'].encode())
            observed = cli('--file', 'data')
            self.assertEqual(observed.returncode, 1)
            self.assertEqual(json.loads(observed.stdout)['controls'], 1)
            (root/'data').write_bytes(b'plain')
            self.assertEqual(cli('--file', 'data').returncode, 0)
            (root/'data').write_bytes(b'\xff')
            bad = cli('--file', 'data')
            self.assertEqual(bad.returncode, 2)
            self.assertEqual(bad.stdout, b'')
            self.assertEqual(cli('--file', '../missing').returncode, 2)
            bad = cli('--bogus\x1b')
            self.assertEqual(bad.returncode, 2)
            self.assertNotIn(b'\x1b', bad.stderr)
            self.assertEqual(cli('--demo', '--file', 'data').returncode, 2)


if __name__ == '__main__':
    unittest.main()
