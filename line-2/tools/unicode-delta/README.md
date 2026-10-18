# Unicode Delta

Compare two explicit original UTF-8 text files and see which covered Unicode
finding occurrences were added, removed, or persisted. This helps a reviewer
check a patch while keeping the exact original-byte evidence needed to inspect
each finding. Python 3.10+ and the standard library are sufficient; no network,
package installation, key, wallet, environment variable, or transaction is used.

Run this command from the repository root:

```sh
python3 line-2/tools/unicode-delta/unicode_delta.py --demo
```

The demo uses clearly labeled synthetic input. It adds a right-to-left override,
removes a non-breaking space, and retains a zero-width space at a shifted byte
offset. Its report includes all three statuses and exits successfully.

To compare your own explicitly selected, non-secret workspace files:

```sh
python3 line-2/tools/unicode-delta/unicode_delta.py --before path/to/before.txt --after path/to/after.txt --max-changes 100
```

Exit status is **1** when any covered finding occurrence was added, **0** when
none was added, and **2** for invalid input or an incomplete scan. The synthetic
demo always exits 0 after a successful comparison. A successful report is emitted
only after both files, the comparison, and the complete rendering pass validation;
errors go to stderr with no report on stdout. Passing no new findings does not
establish that text is safe.

## What counts as the same finding

Both files are scanned independently by the existing `unicode-lantern` engine.
The exact matching signature includes the rule, implicated spelling, all rule
semantic data (including normalized spelling or skeleton when present), and the
exact spelling of a collision's first witness. It excludes positions, excerpts,
and explanation text. Identical signatures form multisets: the first before
occurrence pairs with the first after occurrence, then the second with the second.
Pairing compares full exact values, not hashes.

This is occurrence comparison, not edit tracking. A moved finding or one in a
different context persists if its signature is unchanged. Reordering identifiers
can change which spelling is the first collision witness, producing added and
removed occurrences. Two independent files do not provide cross-file collision
detection. Existing scanner heuristics also inspect comments and strings and use
a limited Latin/Greek/Cyrillic lookalike mapping, not full Unicode confusables.

## Evidence and bounds

`counts` gives complete before, after, added, removed, and persisting totals.
`changes` retains at most `--max-changes` evidence details, prioritizing added
occurrences in after order, then removed occurrences in before order, then
persisting occurrences in after order. The detail limit also applies to
persisting occurrences; `omitted_details` and `details_truncated` disclose any
omission. Reducing details never changes totals or scan completeness.

Each retained side uses unchanged `unicode-text-window.evidence` to verify its
original byte span, include its SHA-256, show up to 64 implicated bytes, and show
16 context bytes on either side. Collision details include the first witness's
own byte citation. Byte ranges are zero-based and half-open; line and byte column
are one-based, with only LF starting a line. `finding_index` is one-based scanner
order within that input. Byte excerpts may split UTF-8 characters and are
unredacted. Review only files whose excerpts may be disclosed.

Each file is limited to 2 MiB, strict UTF-8, and at most 1,000 findings. Both scans
retain the scanner's full 1,000-finding limit. If either has more findings, the
tool rejects the comparison, even with a small requested detail limit. Labels
are limited to 1,024 UTF-8 bytes; details to 1–1,000; output to 4 MiB. Oversized
rendering is an error rather than silent clipping. Normalized/skeleton previews
are limited to 128 escaped characters and include full escaped-value digests and
omission counts. A preview may stop inside an escape and must not be decoded as
a complete escape sequence.

Reports use printable ASCII JSON and newlines. Labels use escaped text; excerpts
double literal backslashes and represent nonprintable or non-ASCII bytes with
`\xHH`. Source SHA-256 values, both engine source hashes, scanner version, and
the runtime Unicode database version identify the inputs and interpretation.
Hashes do not attest authenticity or authorship.

The CLI accepts regular files resolving inside the current workspace and reads
only the two selected inputs plus its two bundled Python dependencies. It does
not search directories, follow outside-workspace input symlinks, decode JSON
string escapes, or modify either input. Keep the sibling `unicode-lantern/` and
`unicode-text-window/` tool folders alongside this folder when copying it.

## Python API

```python
report = review(before_bytes, after_bytes,
                before_label='<before>', after_label='<after>', max_changes=100)
text = render(report)
```

The API takes original bytes, not caller-generated scanner reports. Invalid or
incomplete inputs raise `ValueError` (including Unicode decoding errors); file
errors from engine source reads raise `OSError`. `render` returns one complete
JSON string ending with a newline. CLI policy, including exit codes, is in
`main`.

## Local results

The demo ran successfully with Python's Unicode database 16.0.0: two findings
before, two after, one added, one removed, and one persisting. The persistent
zero-width space moved from byte offset 14 to 30, and each side retained its own
verified byte citation. No chain or network interaction was needed.

All 21 regression tests passed, including independent multiset count checks,
first-to-first duplicate pairing, collision witness changes, complete-scan
rejection at 1,001 findings, acceptance at 1,000 findings, bounded long-token
evidence, byte ranges and digests, CLI exit statuses, terminal-inert rendering,
and a copied three-folder deployment with workspace symlink rejection:

```sh
python3 -B -m unittest discover -s line-2/tools/unicode-delta -p test_unicode_delta.py -v
```

An actual Unit Flint source change was also reviewed: its 12,506-byte version
at commit `41b0e8d` versus the current 14,374-byte version containing inclusive
bound checks. Both complete scans had zero covered findings. The inputs were
read as data, never executed. Source and engine hashes are in
`line-2/round-30-real-review.json`; zero findings is not a safety endorsement.
All 137 inherited Line 2 tests also passed without modifying earlier tools.
