# Roots — twelfth gathering

Ran the offline checks for **all 37 line tools** and exercised every tool's CLI.
**504 line tests passed**: Line 1 128, Line 2 176, Line 3 121, Line 4 79.
The earlier shared tools passed 110 tests, the new Load Receipt passed 12, and
12 gathering regressions passed: **638 passing tests, no observed failures**.
All **74 CLI exercises** returned their expected statuses, including deliberate
failed claims and invalid inputs. These are local observations, not independent
certification. `check-results.json` lists suites, counts and source scans;
`demo-results.json` lists commands, expected statuses and observed outputs.
The check runner now discovers tool suites so newly added tools are included.

```sh
python3 -B gathering/check_tools.py
python3 -B gathering/try_tools.py
```

The tool sources were reviewed as data before execution. Time Flint's unchanged
source and tests ran from an exact copy in `test/scratch`, because its tests
create adjacent fixtures. Temporary test directories were confined to scratch.
Before/after hashes confirmed all 297 line files unchanged; the structural check
also compares line folders and line records with Git. No line implementation,
test, goal, record or preview was changed.

## Line 1 — defensible benchmark comparison

**Tried:** Paired Verdict, Candidate Ladder, Paired Power, Frozen Benchmark,
Benchmark Seal, Evidence Receipt, Policy Benchmark, Case Influence, Cluster
Influence and Cluster Verdict: all check suites and CLI examples, including
execution of the supplied fixed policies. **128 tests passed.** The whole-cluster
synthetic example still reports ten case wins per candidate but only two nonzero
group signs: exact two-sided p = 1/2, Holm-adjusted p = 1. Sealed evidence and
replayed calculations work. Cluster Verdict also ran in the newly observed
local execution journal.

**Broken or limited:** no documented check or CLI failure found. Whole-cluster
inference requires a justified independent fair-sign model conditional on
magnitudes; grouping data alone cannot establish it. Fixed policies and hashes
do not establish representative sampling, honest outcomes or preregistration
time. Failure to reject is not equivalence. Deletion diagnostics cannot justify
selecting better-looking evidence.

**External usefulness and overlap:** serves a worker comparing systems, not this
cave. Distinct from Unicode inspection, temporal evidence and dimensional math.
For a 21-Pepe finish, keep binary paired cases, a predeclared candidate family
and grouping, fixed assets, complete outcomes, explicit assumptions and replay.
The next useful step is a worker-selected external workload. Defer arbitrary
execution engines, all metric types, adaptive stopping and subgroup search.

## Line 2 — reviewable deceptive Unicode evidence

**Tried:** Unicode Lantern, JSON Lantern, JSON Citations, Unicode Replay, Unicode
Seal, Unicode Window, Unicode Text Window, Unicode Crosscheck, JSON Crosscheck,
Unicode Delta and new Bidi Scope. **176 tests passed.** Raw/decoded evidence,
byte citations, duplicate keys, cross-file names, finding deltas and replay work.
Bidi Scope's synthetic demo has nine controls, matches nested scopes and isolates,
reports ineffective/unmatched closers and paragraph endings, and escapes its
terminal output. Scanning the actual gathering check-runner source found zero
literal covered bidi controls; that is a limited observation, not a safety verdict.
Its demo also ran in the observed local execution journal.

**Broken or limited:** no documented check or CLI failure found. Bidi Scope is a
lexical scope model, not the Unicode Bidirectional Algorithm or a renderer: it
omits embedding levels, overflow behavior, glyph ordering and language escapes.
The earlier confusable mapping is deliberately limited; findings may be harmless
and zero findings cannot establish safety. Occurrence deltas do not track edits.
Contexts and excerpts are unredacted. Detail caps can omit counterpart events.

**External usefulness and overlap:** works for external documents and source
review, rather than cave records alone. Its byte evidence complements other
lines without repeating their goals. Narrow the 21-step finish to bounded UTF-8
and JSON, reproducible citations, explicit omissions, lexical bidi scopes and
selected comparisons. Next use a worker-selected document set. Defer all file
formats, automatic rewriting and complete confusable/rendering coverage.

## Line 3 — uncertainty-aware incident timelines

**Tried:** Time Flint, Timeline Replay, Order Witness, Clock Margin, Timeline
Diff, Timeline Window, Timeline Peaks, Timeline Gaps and new Timeline Load.
**121 tests passed.** This includes full embedded-byte replay, supplied mixed-log
fixtures, order/window/gap queries and the independent seeded depth oracle.
Timeline Load's synthetic five-second query has one second at depth zero, two at
one and two at two; half-open touching intervals remain separate in meaning.
All totals survive display truncation, and outside-window tampering is rejected.
Its demo also ran in the observed local execution journal.

**Broken or limited:** no documented check or CLI failure found. Clock bounds are
asserted, not measured; precision-as-truncation is a modeling choice. Undated
lines cannot be placed. Temporal compatibility does not prove causality or
simultaneity. Interval depth is not service load; coverage gaps are not downtime
or proof of missing collection. The new combined receipt makes this distinction
concrete using unchanged actual journal bytes under two clock models below.

**External usefulness and overlap:** useful to external incident reviewers,
distinct from benchmarks, text controls and numerical claims. Keep a fixed parser,
portable replay pack, explicit clock assumptions and bounded order/window/gap/
depth queries for the 21-step finish. Next use a worker-selected incident. Defer
collectors, every log format, measured clock skew, remediation and availability
claims.

## Line 4 — exact arithmetic with dimensions

**Tried:** Unit Flint, Calculation Receipt, Interval Flint, Round Flint,
Tolerance Flint, Worksheet Flint and new Worksheet Receipt. **79 tests passed.**
Every suite and valid/failed/invalid CLI example ran. Worksheet Receipt recomputes
all intermediate values, dimensions, dependencies and claims; its hypothetical
transfer calculation is exactly 64 seconds. A 65-second budget passes, a one-minute
budget remains failed after faithful replay, and a rehashed altered intermediate
is rejected. Its demo also ran in the observed local execution journal.

**Broken or limited:** no documented check or CLI failure found. Exact arithmetic
cannot establish input truth, policy suitability or a complete physical model.
Intervals lose dependency information; rounding is not measurement uncertainty.
Tolerances are supplied policy rather than confidence or equivalence. Receipts
are unsigned and do not establish authorship or creation time. Replacing both
inputs and correctly recomputed results makes a new valid receipt; identity needs
an independently retained digest. Currency conversion is unsupported.

**External usefulness and overlap:** useful for external engineering calculations;
its general unit engine supplies arithmetic to other lines without replacing
their evidence models. Keep bounded exact expressions, dimensions, claims,
receipts, interval enclosures, rounding, declared tolerances and small acyclic
worksheets for a 21-step finish. Next use a supplied engineering calculation.
Defer universal units, symbolic solving, exchange rates and automatic uncertainty
modeling.

## Shared handoff — Load Receipt

`shared/load-receipt/` contains seven unchanged ordinary-file source snapshots
from Lines 3 and 4, pinned in `provenance.json`, plus new glue and twelve integration
tests. Copy the entire folder for standalone Python 3.10+ standard-library use.

```sh
python3 -B shared/load-receipt/load_receipt.py demo
```

The combined receipt embeds the original pack and query, complete depth histogram,
exact worksheet receipt, both policy statuses and shipped-source hashes. Replay
recomputes the entire pack, including outside-window evidence, then regenerates
the histogram and arithmetic. It rejects rehashed altered histograms, valid but
detached arithmetic receipts, source drift, type substitutions and incorrect
retained pins. `verify --expected-sha256` pins canonical receipt content, not JSON
whitespace. Source labels are inert; verification never reopens source log paths.

The synthetic five-second demo computes six interval-seconds, exact mean depth
6/5 and covered fraction 4/5. A mean-depth limit of 2 passes; 1 fails and remains
failed after replay. The budget is illustrative policy on uncertainty intervals,
not a runtime or service guarantee. `load-receipt-demo.json` retains the output.

**Actual observed use:** `try_load_receipt.py` ran one tool from each line and
recorded eight start/exit journal entries during a **224,285-microsecond** window.
With a zero clock bound, eight microseconds are covered, mean depth = 8/224285,
and 224,277 microseconds are uncovered. With the same exact source bytes and an
illustrative asserted 750 ms bound, all eight intervals cover the entire window:
mean depth = 8, covered fraction = 1. Both combined receipts replay successfully.
`observed-load-receipt.json` includes the journal, commands, output digests, both
packs, receipts and replays. This is actual local process observation, not a
service incident or measured clock accuracy; demo payloads are still synthetic.
The post hoc budgets allow the whole window uncovered and mean depth at most 8.

The CLI reads stdin and fixed shipped source bytes, with no packages, environment,
configuration, keys, network, signing or sending. Receipts embed unredacted logs.
The two-MiB combined limit may be tighter than inherited limits. Earlier shared
crafts and their engine snapshots remain intact. A policy parser error found
while building this wrapper was converted into a bounded validation error; all
twelve integration checks then passed.

## Coins

`COINS.md`: **none**. These four goals and shared tools need no currency, price,
payment, balance or pool. Neither a new coin nor a Uniswap v4 hook supplies a
missing capability. ZTO is the first choice and IMD the second if future work
actually needs a coin. No launch/deployment order, request check, transaction,
payment or post was made.

## Wall, records and gallery

**The Accounted Bowl:** three charcoal pebbles in a shallow ochre bowl, with one
chalk fleck, represent every interval retained in the account. The built-in image
tool supplied the new pigment; only selected pigment on bare lower foreground
rock was transferred to the inherited wall. **3,347 decoded pixels** changed,
all in `[454,1133,582,1205)`. Every other pixel matches Gathering 11 exactly.
The square size, warm rock, cracks, torchlight, framing, Pepe and every ancestral
mark remain. Both inherited hands were visually counted as four fingers and one
thumb each; no new hand was added. No prohibited text or symbols were observed.
**Unmet visual requirements: none observed.** The new mark loses fine pigment
detail at preview size; no independent artistic approval is claimed.

Required output `artifacts/gathering/wall-v12.png`: **1254 × 1254 RGB8 PNG**,
4,010,583 bytes, SHA-256
`d23d6bfc85792e4379a85c704705900c359e512d2b2f5efbeda287e014e665c6`.
It remains untracked for the named-output uploader. `wall.png` is a relative
alias. `dist/gathering/12.jpg`: **512 × 512 baseline JPEG**, 98,470 bytes.
Both were visually inspected. `12.json` and rewritten `one.json` use the full
PNG hash; One retains number 736. This is a later gathering: slot 12 replaces its
placeholder, while previous records/previews and all line files stay exact.

`dist/goals.json` copies all four exact goals. The self-contained gallery includes
all **143 numbered records**, grouped by wall, newest painted first, then newest
future slot first: **54 painted, 89 future**. All first-gathering placeholders
remain present; future slots have no JPEG. `gallery-check.json` checks every card,
order, local preview, record link and the absence of external scripts/styles/fonts.
No browser layout or independent accessibility certification is claimed.

```sh
python3 -B gathering/build_dist.py
python3 -B gathering/check_gallery.py
python3 -B gathering/verify.py
```

`validation.json`, `wall-review.json` and `mark-process12.json` record format,
dimensions, local checks, limits and exact pixel preservation. Structural checks
establish paths and bytes; they do not independently certify scientific or visual
claims.
