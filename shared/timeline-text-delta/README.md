# Timeline Text Delta

Review two revisions of timestamped logs in one offline call. It combines Line 3's
verified Timeline Diff with Line 2's original-byte Unicode Delta. The timeline
half reports source and line changes and both order relations for a cited event
pair. The text half scans one source present in both packs for added, removed and
persisting covered Unicode findings, with byte citations. Both halves use the
same embedded source bytes. Python 3.10+ and the standard library are sufficient;
copy this whole folder for standalone use.

From the repository root, run:

```sh
python3 -B shared/timeline-text-delta/timeline_text_delta.py demo
```

The explicitly synthetic demo changes a worker log timestamp from 10:00:00 to
10:00:03 and adds a right-to-left override byte sequence to its message. A
separate server event is at 10:00:02. When tried, both packs replayed; the
worker's physical line was classified as changed, the cited relation switched
from left-before-right to right-before-left, and one covered Unicode finding was
added with its original UTF-8 byte citation. Because the worker line changed,
Timeline Diff correctly labels the pair assessment
`different-or-unavailable-evidence`; the two displayed relations are model
observations, not a claim of a stable event changing order. Five integration
tests passed, including bad pins, tampered timeline content, a missing source,
bounded details, and a timeline change with zero covered Unicode findings.

For real selected workspace evidence, first make two packs using Timeline Replay
and retain the SHA-256 of each exact pack file independently. Then run:

```sh
python3 -B shared/timeline-text-delta/timeline_text_delta.py review BEFORE.json AFTER.json --expect-before-sha256 BEFORE_DIGEST --expect-after-sha256 AFTER_DIGEST --source worker.log --left worker.log 1 --right server.log 1 --max-changes 20
```

The uppercase filenames and digests above are explanatory tokens, not values to
reuse. `--source` is an embedded source name, not a file opened during review.
Input pack files must resolve to regular files inside the current workspace.
The CLI requires both retained lowercase SHA-256 pins; mismatch, failed replay,
invalid UTF-8, absent source or incomplete Unicode scan exits 2 with no partial
stdout. Successful review exits 0. The display cap omits finding details, never
complete finding totals; Timeline Diff independently caps its line details at
200 and reports the omitted count. The output is ASCII JSON.

```sh
python3 -B gathering/run_suite.py discover -s shared/timeline-text-delta -v
```

`provenance.json` names and hashes six unchanged ordinary engine source snapshots
from Lines 2 and 3. No dependency download or sibling folder is required.

Limits: physical source and line positions do not identify moved events. Clock
bounds and timestamp precision are analyst assumptions; temporal order does not
prove causality. Unicode rules are heuristic and do not prove intent or safety.
Exact pack pins and replay establish byte consistency, not authentic or complete
logs. Unicode evidence excerpts are unredacted, so select only shareable files.
The chosen source must exist in both packs and be strict UTF-8; a newly added or
fully removed source cannot be text-compared here. The tool does not sign, send,
post, pay or read a wallet, key or environment variable.
