# Bidi Scope

Show how **literal UTF-8 bidirectional controls** open and end lexical scopes,
with exact original-byte evidence. Useful when a reviewer sees an override or
isolate warning and needs to find its counterpart, an ineffective closer, or the
paragraph/EOF where an open scope ends. This complements Unicode Lantern; it
neither changes that scanner nor expands its confusables mapping.

Python **3.10+**, standard library only; this folder is standalone. No packages,
network, configuration, environment access or sibling imports. Inputs are inert
bytes; nothing is executed, rewritten, signed or transmitted.

Run from a workspace root:

```sh
python3 -B line-2/tools/bidi-scope/bidi_scope.py --demo
```

The explicitly synthetic demo has **9 controls**: a nested override inside an
isolate, a PDF stopped by an isolate, an override ended by LF and an unmatched
PDI. It exits 0 and prints ASCII JSON. The report includes all status counts,
maximum lexical stack depth, a source digest, the runtime Unicode database
version, the engine source digest and bounded original-byte contexts.

Review an actual file (replace the path with your document):

```sh
python3 -B line-2/tools/bidi-scope/bidi_scope.py --file gathering/REPORT.md --max-details 100
```

A real file exits **1 whenever any covered control is present**, including
balanced/legitimate controls. No controls exits 0; invalid input or usage exits
2. Output is fully computed before writing to stdout. Errors are ASCII JSON on
stderr. A clean result is **not a safety verdict**. Reuse `review(raw_bytes,
source_label, max_details)` and `render(report)` from Python if needed.

## What the model means

- LRE/RLE/LRO/RLO push an embedding or override; LRI/RLI/FSI push an isolate.
- PDF closes the top embedding; it cannot cross an isolate. At an isolate it
  is reported as `ignored-pdf-at-isolate`; with no scope it is `unmatched-pdf`.
- PDI closes the nearest isolate and ends any embeddings nested inside it.
  With no isolate it is `unmatched-pdi` and leaves embeddings untouched.
- A character whose Python Unicode bidirectional class is `B` ends every open
  scope with `ended-at-paragraph` and its own byte citation. EOF leaves scopes
  `open-at-eof`. These are structural observations, not proof of an attack.
- LRM/RLM/ALM are reported as `directional-mark` and do not push scopes.

This is a deliberately **lexical model**, not an implementation of the Unicode
Bidirectional Algorithm. It does not compute embedding levels, rendering-depth
limits/overflow, FSI direction, bracket resolution, glyphs or displayed order.
A renderer can therefore ignore controls differently. Language syntax and all
JSON/HTML/source escapes remain uninterpreted. Scope ranges exclude their opening
and closing control bytes; EOF/paragraph content ranges end before the boundary.
No evidence range is a claim about all text visually affected by a control.

Event indexes are zero-based source control order. Each opening has an exact
content byte range and a `closing_control` index or paragraph citation. Matched
closers name their `opening_control`. Embeddings implicitly ended by PDI point
to that PDI; its opening index names the isolate. Ranges are zero-based and
half-open; line and byte-column are one-based, with **only LF** incrementing the
line. CR, NEL and other paragraph separators can reset scopes without changing
this LF-based coordinate convention. Contexts use printable ASCII, doubled
backslashes and `\xHH` for other bytes. Each is at most 16 original bytes and can
split a UTF-8 character. Exact control bytes also appear as hexadecimal.

## Bounds and omissions

Inputs must be strict UTF-8 bytes, at most 2 MiB, with at most **4,096 controls**.
Exceeding either bound fails without producing a partial report; malformed UTF-8
at the end fails too. CLI paths must resolve to regular files inside the current
workspace; symlinks resolving outside are rejected. Source labels are limited to
1,024 UTF-8 bytes. No recursive file discovery or secret redaction is performed.
Only inspect documents you are authorized to read.

`--max-details` is 1..1000 (default 100). Counts and relationships cover the
**entire** accepted input before retaining that many events in source order.
`omitted_details` is explicit; a closing/opening index can refer to an omitted
event. Increase the detail cap to inspect it. Inputs with over 1,000 controls
cannot show every event in one CLI report; use the Python API to select details
from smaller, independently labeled documents if appropriate, recognizing that
splitting input changes scope analysis. The serialized output limit is 4 MiB.

The detector covers only the twelve listed bidi controls, not lookalikes or all
invisible characters. Findings can be legitimate. Hashes identify bytes and do
not prove authorship, authenticity or honesty. Byte contexts are **unredacted**.

## Checks and observed use

```sh
python3 -B line-2/tools/bidi-scope/test_bidi_scope.py
```

18 tests passed locally: nested embeddings and isolates, ineffective closers,
implicit endings, paragraph separators versus line separators, EOF, UTF-8 byte
citations, all directional marks, detail omission, limits, hostile terminal
text, malformed UTF-8, literal escape non-decoding, 150 seeded generated scope
trees with independently tracked byte pairs, and standalone copied CLI behavior.

Also reviewed the actual gathering report and three inherited Unicode tool
sources as inert UTF-8. All had zero literal covered controls; their escaped
Python examples were correctly left uninterpreted. Source sizes and SHA-256
pins are in `line-2/round-31-real-review.json`. This observation says nothing
about source safety and does not establish behavior on an attack in the wild.
