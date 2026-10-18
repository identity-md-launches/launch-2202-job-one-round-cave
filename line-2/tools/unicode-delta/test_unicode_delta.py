"""Behavioral checks for complete, byte-cited Unicode finding comparisons."""
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import random
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('unicode_delta', HERE / 'unicode_delta.py')
delta = importlib.util.module_from_spec(spec)
spec.loader.exec_module(delta)


def utf8(value):
    return value.encode('utf-8')


class DeltaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scratch = Path.cwd() / 'test' / 'scratch'
        cls.scratch.mkdir(parents=True, exist_ok=True)

    def assert_counts(self, report, added, removed, persisting):
        self.assertEqual(report['counts']['added'], added)
        self.assertEqual(report['counts']['removed'], removed)
        self.assertEqual(report['counts']['persisting'], persisting)
        self.assertEqual(report['counts']['before'], removed + persisting)
        self.assertEqual(report['counts']['after'], added + persisting)
        self.assertTrue(report['comparison_complete'])

    def test_empty_inputs_and_source_hashes(self):
        report = delta.review(b'', b'plain ASCII')
        self.assert_counts(report, 0, 0, 0)
        self.assertEqual(report['changes'], [])
        self.assertEqual(report['omitted_details'], 0)
        self.assertFalse(report['details_truncated'])
        for side, raw in [('before', b''), ('after', b'plain ASCII')]:
            self.assertEqual(report['sources'][side]['bytes'], len(raw))
            self.assertEqual(report['sources'][side]['sha256'], hashlib.sha256(raw).hexdigest())

    def test_added_removed_and_unchanged_are_distinct(self):
        raw = utf8('\u202e')
        for before, after, expected, status in [
                (b'', raw, (1, 0, 0), 'added'),
                (raw, b'', (0, 1, 0), 'removed'),
                (raw, raw, (0, 0, 1), 'persisting')]:
            with self.subTest(status=status):
                report = delta.review(before, after)
                self.assert_counts(report, *expected)
                change = report['changes'][0]
                self.assertEqual(change['status'], status)
                self.assertEqual(change['rule'], 'bidi-control')
                self.assertEqual(change['before'] is None, status == 'added')
                self.assertEqual(change['after'] is None, status == 'removed')

    def test_shifted_context_and_labels_do_not_change_identity(self):
        before = utf8('old \u202e!')
        after = utf8('\u00e9\r\nnew context \u202e!')
        report = delta.review(before, after, 'old label', 'different label')
        self.assert_counts(report, 0, 0, 1)
        change = report['changes'][0]
        self.assertEqual(change['before']['source']['byte_start'], before.index(utf8('\u202e')))
        self.assertEqual(change['after']['source']['byte_start'], after.index(utf8('\u202e')))
        self.assertEqual(change['after']['source']['line'], 2)
        self.assertEqual(change['after']['source']['byte_column'], 13)

    def test_duplicate_occurrences_pair_first_to_first(self):
        before = utf8('\u202e \u202e \u200b')
        after = utf8('\u202e \u200b \u200b')
        report = delta.review(before, after)
        self.assert_counts(report, 1, 1, 2)
        pairs = [(item['before']['source']['byte_start'], item['after']['source']['byte_start'])
                 for item in report['changes'] if item['status'] == 'persisting']
        self.assertEqual(pairs, [(0, 0), (8, 4)])
        removed = next(item for item in report['changes'] if item['status'] == 'removed')
        added = next(item for item in report['changes'] if item['status'] == 'added')
        self.assertEqual(removed['before']['source']['byte_start'], 4)
        self.assertEqual(added['after']['source']['byte_start'], 8)
        self.assertEqual([item['status'] for item in report['changes']],
                         ['added', 'removed', 'persisting', 'persisting'])

    def test_exact_character_and_identifier_spellings_matter(self):
        for before, after in [('\u202e', '\u202d'),
                              ('\u043ewner', 'o\u0448ner'),
                              ('\uff4fwner', '\uff4fther')]:
            with self.subTest(before=before, after=after):
                report = delta.review(utf8(before), utf8(after))
                self.assert_counts(report, 1, 1, 0)
                self.assertEqual(len({entry['signature_sha256'] for entry in report['changes']}), 2)

    def test_changed_collision_witness_is_removed_plus_added(self):
        before = utf8('owner \u043ewner')
        after = utf8('\uff4fwner \u043ewner')
        report = delta.review(before, after)
        self.assert_counts(report, 2, 1, 1)
        collisions = [item for item in report['changes'] if item['rule'] == 'lookalike-collision']
        self.assertEqual({item['status'] for item in collisions}, {'added', 'removed'})
        for item in collisions:
            side = 'after' if item['status'] == 'added' else 'before'
            raw = after if side == 'after' else before
            witness = item[side]['first_source']
            expected = utf8('\uff4fwner') if side == 'after' else b'owner'
            self.assertEqual(raw[witness['byte_start']:witness['byte_end']], expected)
            self.assertEqual(witness['sha256'], hashlib.sha256(expected).hexdigest())

    def test_collision_witness_position_can_move_without_replacement(self):
        before = utf8('owner \u043ewner')
        after = utf8('prefix\nowner ; \u043ewner')
        report = delta.review(before, after)
        self.assert_counts(report, 0, 0, 2)
        collision = next(item for item in report['changes'] if item['rule'] == 'lookalike-collision')
        self.assertEqual(collision['before']['first_source']['byte_start'], 0)
        self.assertEqual(collision['after']['first_source']['byte_start'], 7)

    def test_literal_escape_is_not_an_actual_unicode_control(self):
        report = delta.review(br'hello\u202e', utf8('hello\u202e'))
        self.assert_counts(report, 1, 0, 0)

    def test_retention_cap_keeps_complete_totals_and_prioritizes_changes(self):
        before = utf8('\u202e\u202d\u200b')
        after = utf8('\u202e\u200b\x1b\x07')
        report = delta.review(before, after, max_changes=1)
        self.assert_counts(report, 2, 1, 2)
        self.assertEqual(report['retained_details'], 1)
        self.assertEqual(len(report['changes']), 1)
        self.assertEqual(report['omitted_details'], 4)
        self.assertTrue(report['details_truncated'])
        self.assertEqual(report['changes'][0]['status'], 'added')

    def test_cap_does_not_skip_late_findings(self):
        report = delta.review(b'\x1b' * 20, b'\x1b' * 20 + b'\x07', max_changes=1)
        self.assert_counts(report, 1, 0, 20)
        self.assertEqual(report['changes'][0]['after']['source']['byte_start'], 20)

    def test_truncated_scans_are_rejected_not_compared(self):
        oversized = b'\x1b' * (delta.MAX_FINDINGS + 1)
        for before, after in [(oversized, b''), (b'', oversized), (oversized, oversized)]:
            with self.subTest(before=len(before), after=len(after)), self.assertRaises(ValueError):
                delta.review(before, after, max_changes=1)
        complete = b'\x1b' * delta.MAX_FINDINGS
        report = delta.review(complete, complete, max_changes=1)
        self.assert_counts(report, 0, 0, delta.MAX_FINDINGS)

    def test_invalid_utf8_is_checked_after_retention_would_fill(self):
        invalid = b'\x1b' * 10 + b'\xff'
        for before, after in [(invalid, b''), (b'', invalid)]:
            with self.subTest(before=len(before), after=len(after)), self.assertRaises(ValueError):
                delta.review(before, after, max_changes=1)

    def test_input_and_label_types_and_budgets(self):
        for wrong in ['', bytearray(b'a'), memoryview(b'a'), None, 1]:
            for side in ['before', 'after']:
                args = dict(before=b'', after=b'')
                args[side] = wrong
                with self.subTest(side=side, kind=type(wrong).__name__), self.assertRaises(ValueError):
                    delta.review(**args)
        for wrong in [True, 0, -1, 1001, 1.0, '1', None]:
            with self.subTest(max_changes=wrong), self.assertRaises(ValueError):
                delta.review(b'', b'', max_changes=wrong)
        for side in ['before_label', 'after_label']:
            for wrong in [b'label', None, 3, 'a' * (delta.MAX_LABEL_BYTES + 1), '\u00e9' * (delta.MAX_LABEL_BYTES // 2 + 1), '\ud800']:
                with self.subTest(side=side, kind=type(wrong).__name__), self.assertRaises(ValueError):
                    delta.review(b'', b'', **{side: wrong})
        for side in ['before', 'after']:
            args = dict(before=b'', after=b'')
            args[side] = b'a' * (delta.MAX_BYTES + 1)
            with self.subTest(side=side), self.assertRaises(ValueError):
                delta.review(**args)
        report = delta.review(b'', b'', before_label='a' * delta.MAX_LABEL_BYTES)
        self.assert_counts(report, 0, 0, 0)

    def test_citations_bind_full_spans_to_the_correct_original_bytes(self):
        before = utf8('\u00e9\r\nowner \u043ewner\u202e')
        after = utf8('\u00e9\r\nstart owner\n\u043ewner\u200b')
        report = delta.review(before, after)
        for item in report['changes']:
            self.assertEqual(len(item['signature_sha256']), 64)
            for side, raw in [('before', before), ('after', after)]:
                occurrence = item[side]
                if occurrence is None:
                    continue
                self.assertGreaterEqual(occurrence['finding_index'], 1)
                for key in ['source', 'first_source']:
                    if key not in occurrence:
                        continue
                    span = occurrence[key]
                    start, end = span['byte_start'], span['byte_end']
                    self.assertEqual(span['sha256'], hashlib.sha256(raw[start:end]).hexdigest())
                    self.assertEqual(span['line'], raw.count(b'\n', 0, start) + 1)
                    self.assertEqual(span['byte_column'], start - raw.rfind(b'\n', 0, start))

    def test_long_identifier_preview_is_bounded_but_hash_is_complete(self):
        after = utf8('a' * 20000 + '\u0430')
        report = delta.review(b'', after)
        self.assert_counts(report, 1, 0, 0)
        span = report['changes'][0]['after']['source']
        self.assertEqual(span['byte_end'], len(after))
        self.assertEqual(span['sha256'], hashlib.sha256(after).hexdigest())
        self.assertEqual(span['omitted_span_bytes'], len(after) - 64)
        self.assertLess(len(delta.render(report)), 10000)

    def test_deterministic_render_and_terminal_inert_labels(self):
        raw = utf8('owner \u043ewner\u202e\x1b]52;c;payload\x07\r\t')
        kwargs = dict(before_label='old\x1b[31m\u202e', after_label='new\n\x07\u2066')
        first = delta.review(b'', raw, **kwargs)
        second = delta.review(b'', raw, **kwargs)
        self.assertEqual(first, second)
        rendered = delta.render(first)
        self.assertEqual(rendered, delta.render(second))
        self.assertTrue(rendered.endswith('\n'))
        self.assertTrue(all(char == '\n' or 32 <= ord(char) <= 126 for char in rendered))
        decoded = json.loads(rendered)
        for side in ['before', 'after']:
            self.assertTrue(all(32 <= ord(char) <= 126 for char in decoded['sources'][side]['label']))
        self.assertNotIn('\x1b', rendered)

    def test_output_budget_errors_before_returning_partial_text(self):
        report = delta.review(b'', b'\x1b')
        with patch.object(delta, 'MAX_OUTPUT', 1), self.assertRaises(ValueError):
            delta.render(report)

    def test_generated_character_multisets_against_independent_counts(self):
        rng = random.Random(737)
        suspect = '\u202e\u202d\u200b\x1b\x07'
        alphabet = 'abc \n' + suspect
        for trial in range(60):
            before = ''.join(rng.choice(alphabet) for _ in range(rng.randrange(80)))
            after = ''.join(rng.choice(alphabet) for _ in range(rng.randrange(80)))
            left, right = Counter(before), Counter(after)
            added = sum(max(right[c] - left[c], 0) for c in suspect)
            removed = sum(max(left[c] - right[c], 0) for c in suspect)
            persisting = sum(min(left[c], right[c]) for c in suspect)
            with self.subTest(trial=trial):
                self.assert_counts(delta.review(utf8(before), utf8(after)), added, removed, persisting)

    def cli(self, *arguments, cwd=None):
        return subprocess.run([sys.executable, '-B', str(HERE / 'unicode_delta.py'), *arguments],
                              cwd=cwd, capture_output=True, text=True)

    def test_demo_cli(self):
        result = self.cli('--demo')
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertGreater(report['counts']['added'], 0)
        self.assertGreater(report['counts']['removed'], 0)
        self.assertGreater(report['counts']['persisting'], 0)

    def test_cli_statuses_and_no_partial_stdout_on_bad_input(self):
        with tempfile.TemporaryDirectory(dir=self.scratch) as directory:
            root = Path(directory)
            before, after = root / 'before.txt', root / 'after.txt'
            for left, right, status in [(b'', b'', 0), (b'', b'\x1b', 1),
                                        (b'\x1b', b'\x1b', 0), (b'\x1b', b'', 0),
                                        (b'', b'\x1b' * 10 + b'\xff', 2),
                                        (b'', b'\x1b' * (delta.MAX_FINDINGS + 1), 2)]:
                before.write_bytes(left)
                after.write_bytes(right)
                result = self.cli('--before', str(before), '--after', str(after), '--max-changes', '1')
                with self.subTest(left=len(left), right=len(right), status=status):
                    self.assertEqual(result.returncode, status, result.stderr)
                    if status == 2:
                        self.assertEqual(result.stdout, '')
                        self.assertTrue(all(c == '\n' or 32 <= ord(c) <= 126 for c in result.stderr))
                    else:
                        self.assertTrue(json.loads(result.stdout)['comparison_complete'])

    def test_three_folder_portability_and_workspace_symlink_exclusion(self):
        with tempfile.TemporaryDirectory(dir=self.scratch) as directory:
            outer = Path(directory).resolve()
            root = outer / 'workspace'
            root.mkdir()
            for name in ['unicode-delta', 'unicode-lantern', 'unicode-text-window']:
                shutil.copytree(HERE.parent / name, root / name,
                                ignore=shutil.ignore_patterns('__pycache__'))
            command = [sys.executable, '-B', 'unicode-delta/unicode_delta.py']
            result = subprocess.run(command + ['--demo'], cwd=root, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(json.loads(result.stdout)['comparison_complete'])
            (root / 'before.txt').write_bytes(b'normal')
            (outer / 'outside.txt').write_bytes(b'\x1b')
            (root / 'escape.txt').symlink_to(outer / 'outside.txt')
            result = subprocess.run(command + ['--before', 'before.txt', '--after', 'escape.txt'],
                                    cwd=root, capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(result.stdout, '')
            self.assertIn('workspace', result.stderr)


if __name__ == '__main__':
    unittest.main()
