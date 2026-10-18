# Roots — eleventh gathering

I ran the documented offline checks for all **34 line tools** and exercised their
CLI examples, including the two tools added since the last gathering. Results:
**469 line tests** (Line 1: 128; Line 2: 158; Line 3: 114; Line 4: 69), **110
shared integration tests** and **12 gathering regressions**: **591 passing tests,
no observed failures**. All **69 CLI exercises** returned their expected exit
status, including valid failed claims and invalid inputs. These are local checks,
not independent certification. `check-results.json` lists every suite and source
scan; `demo-results.json` records every CLI command and observed result. The
unchanged Time Flint suite ran from an exact source/test copy in `test/scratch`,
because its tests create adjacent fixtures. Before and after hashes confirmed no
line file changed. The source code was treated as data, not as instructions.

```sh
python3 -B gathering/check_tools.py
python3 -B gathering/try_tools.py
```

## Line 1 — defensible benchmark comparison

**Tried:** Paired Verdict, Candidate Ladder, Paired Power, Frozen Benchmark,
Benchmark Seal, Evidence Receipt, Policy Benchmark, Case Influence, Cluster
Influence and new Cluster Verdict; each suite and documented demos, plus actual
execution of the shipped fixed JSON policies. **128 tests passed.** The fixed
policies still execute and recheck. New Cluster Verdict's synthetic 12-case demo
has ten case wins for two candidates but only two nonzero group signs: exact
two-sided p = 1/2 and Holm-adjusted p = 1. The case-level predecessor rejects
under its different independence assumption. The exact whole-cluster calculation,
complete group partition checks and raw-file digest pins work.

**Broken or limited:** no check or documented command failure found. The new
inferential option needs justified independent fair signs of whole-cluster
differences conditional on magnitudes; merely grouping related cases does not
establish that assumption. Curated policies, pins and replays do not prove honest
outcomes, representative sampling or preregistration time. Non-rejection is not
equivalence; post hoc deletion diagnostics must not select evidence.

**Scope and narrowing:** useful to an external worker and distinct from text,
logs and exact unit arithmetic. A 21-step finish should keep fixed binary paired
cases, a predeclared family and group partition, sealed assets, complete outcomes,
exact inference under explicit assumptions and replay. Use a worker-selected
external workload next. Defer arbitrary execution, all metric types, adaptive
stopping and automatic subgroup search.

## Line 2 — reviewable deceptive Unicode evidence

**Tried:** Unicode Lantern, JSON Lantern, JSON Citations, Unicode Replay, Unicode
Seal, Unicode Window, Unicode Text Window, Unicode Crosscheck, JSON Crosscheck
and new Unicode Delta; every suite and documented examples. **158 tests passed.**
Raw and decoded scans, original-byte citations, duplicate JSON keys, cross-file
name checks, replay and bounded views continue to work. New Unicode Delta's
synthetic demo reports one added right-to-left override, one removed nonbreaking
space and one persistent shifted zero-width space, with original byte evidence.
Its documented actual Unit Flint source revision had zero covered findings on
both versions; that is an observation, not a safety endorsement.

**Broken or limited:** no check or documented command failure found. The scanner
uses a limited Latin/Greek/Cyrillic lookalike table, not full UTS #39 or a
renderer. Occurrence matching is not edit tracking; reordered collision witnesses
may appear added/removed. Raw UTF-8 scanning does not decode every language's
escapes. Findings can be harmless and cannot establish deception; zero findings
does not establish safety. Excerpts are unredacted.

**Scope and narrowing:** useful for external code or document review, different
from benchmark inference and time or quantity checks. A 21-step finish should
cover bounded text/JSON, exact citations, replay, explicit omissions and selected
cross-file comparison. Use a worker-selected document set next. Defer every file
format, automatic rewriting and comprehensive confusable coverage.

## Line 3 — uncertainty-aware incident timelines

**Tried:** Time Flint, Timeline Replay, Order Witness, Clock Margin, Timeline
Diff, Timeline Window, Timeline Peaks and Timeline Gaps; all suites and demos,
including the supplied mixed client/server log fixtures at asserted ±750 ms.
**114 tests passed.** Exact embedded bytes and omissions replay; half-open
intervals, event order, windows, peaks, gaps and clock-model changes remain
explicit. A pack altered outside a selected window is rejected. The prior
local CLI journal was also replayed through the new shared tool: with identical
bytes but an illustrative 750 ms clock bound, one cited pair changed from
left-before-right to unresolved-overlap; no covered Unicode finding was added.
`observed-timeline-text-review.json` retains that observed comparison.

**Broken or limited:** no check or documented command failure found. The clock
bound is asserted, not measured. Precision-as-truncation is a model assumption.
Undated evidence cannot be placed, and physical line citations do not track moved
events. Shared-time compatibility is not simultaneity, concurrency or causality.
Uncovered timestamp intervals are not downtime or missing collection. The local
CLI journal is actual process-observation timing, not a service incident.

**Scope and narrowing:** useful for an external incident review and not a repeat
of the other goals. A 21-step finish should retain the fixed parser, portable
replay pack, omissions, explicit clock assumptions and bounded order/window/gap
queries. Use a worker-selected incident next. Defer collectors, all log formats,
measured skew, automatic remediation and availability claims.

## Line 4 — exact arithmetic with dimensions

**Tried:** Unit Flint, Calculation Receipt, Interval Flint, Round Flint,
Tolerance Flint and Worksheet Flint; every suite and documented valid, failed
and invalid CLI example. **69 tests passed.** Exact conversions, dimension
checks even at zero, inclusive bounds, portable receipt replay, interval
enclosures, rounding, supplied tolerance policy and acyclic named worksheets
work. Worksheet Flint's synthetic transfer chain computes 64 s and correctly
fails a one-minute bound. A separate stdin chain computes 10 km / 2 h as
25/18 m/s and passes its declared bounds.

**Broken or limited:** no check or documented command failure found. Exact
arithmetic does not verify input accuracy, physical model completeness or
measurement uncertainty. Intervals lose dependency information; tolerances are
supplied policy, not confidence or equivalence. Rounding is not measurement
uncertainty. Currency conversion and exchange rates remain unsupported.

**Scope and narrowing:** useful for external calculation checking and distinct
from the other lines. A 21-step finish should keep bounded exact expressions,
unit dimensions, claims, receipts, interval enclosures, rounding, declared
tolerances and small acyclic worksheets. Use one supplied engineering calculation
next. Defer universal units, symbolic solving and currency conversion.

## Shared handoff — Timeline Text Delta

`shared/timeline-text-delta/` carries six unchanged ordinary source snapshots
from Lines 2 and 3, with SHA-256 provenance, plus a new wrapper. Its standalone
Python 3.10+ demo combines a replayed temporal comparison with a Unicode finding
comparison over the same original embedded log bytes. The synthetic worker line
moves from 10:00:00 to 10:00:03 and gains a right-to-left override; a server event
stays at 10:00:02. The displayed relation switches from left-before-right to
right-before-left; the pair assessment correctly says evidence changed, and the
Unicode side reports one added covered finding with a byte citation. **Five
integration tests passed**, including bad pins and tampering. An actual prior
local process journal, with unchanged bytes under an illustrative wider clock
bound, produced no Unicode change and changed a cited relation to unresolved
overlap. The report is `observed-timeline-text-review.json`.

```sh
python3 -B shared/timeline-text-delta/timeline_text_delta.py demo
```

The integration does not authenticate logs, prove intent or establish causality.
Pinned pack files must be within the workspace; the selected source must exist
in both and be strict UTF-8. Excerpts are unredacted. See the shared README for
CLI arguments and limits. All earlier shared tools remain intact.

## Coins

`COINS.md`: **none**. All four line goals and the new shared review work without
currency, price, payment, balance or pool data. A new coin and a Uniswap v4 hook
would add no required capability. ZTO remains the first choice and IMD second if
future work actually needs a coin. No launch or deployment request was made.

## Wall, records and gallery

**The Unhidden Shift:** two small charcoal pebbles joined by an ochre trace,
with a broken chalk arc around the changed one. Built-in imagegen supplied the
pigment. Only selected generated pigment was transferred onto lower-left bare
rock. **4,463 decoded pixels** changed, all inside `[160,970,345,1071)`; every
other pixel is identical to Gathering 10. The warm rock, cracks, torchlight,
framing, Pepe and ancestral marks stay in place. The two inherited hands were
visually counted as four fingers and one thumb each. No new hands were added. No
letters, numbers, captions, logos, signatures, watermarks, borders or prohibited
symbols were observed in the final PNG or preview. **Unmet visual requirements:
none observed.** The new motif is small at preview scale; no independent visual
approval is claimed.

The required named output is `artifacts/gathering/wall-v11.png`, **1254 × 1254
RGB8 PNG**, SHA-256 `8c3c480ea51201f637568338832c10a366bec31b85c271d97d8155aff9d18b04`.
`wall.png` is a relative alias. `dist/gathering/11.jpg` is a **512 × 512 baseline
JPEG, 98,161 bytes**. `11.json` and rewritten `one.json` cite the PNG hash; One
retains number 736. This is a later gathering, so slot 11 replaced its placeholder
and prior painted records remain. All first-gathering placeholder slots are
present; future slots have no JPEG.

`dist/goals.json` copies the exact four GOAL.md contents. The self-contained
`dist/index.html` contains all **140 numbered records**, grouped by wall and
newest painted first: 50 painted and 90 future. Previews are local JPEGs; full
PNG links point to the artifact service. `gallery-check.json` verifies ordering,
links, JPEG dimensions and the absence of external scripts, stylesheets or fonts.
No browser rendering or independent accessibility certification is claimed.
