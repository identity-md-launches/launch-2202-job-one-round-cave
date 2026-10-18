# Cluster Verdict

An exact whole-cluster sign-flip test for workers comparing a baseline with a
fixed family of candidate systems on paired binary benchmark observations.
Cases within a declared cluster move together in every null assignment. This
adds an inferential option where Cluster Influence only offered group-deletion
sensitivity diagnostics. Python 3.10+, standard library only, fully offline.
Copy this entire folder; there are no runtime downloads or sibling dependencies.

From the repository root, one command shows it working:

```sh
python3 -B line-1/tools/cluster-verdict/cluster_verdict.py --demo
```

When tried, the explicitly synthetic twelve-case example contained ten wins for
each of two candidates, split between two five-case groups, plus an agreement
group. The case-weighted effect was **5/6** for each candidate. Only two nonzero
cluster signs carried information: differences `[5, 5, 0]` gave two extreme
assignments among four, hence exact two-sided **p = 1/2**, Holm-adjusted **p = 1**.
Neither candidate rejected at familywise alpha 0.05. The predecessor's case-level
test rejects on these same observations when it assumes independent cases.
The distinction reflects different assumptions, not a contradiction or a claim
that either assumed model is justified by the synthetic fixture.

## What the test assumes

For each candidate null, conditional on the absolute group differences, the
nonzero group signs must be independent fair signs. A justified randomized
whole-group swap under a sharp null can provide this; an independent,
sign-symmetric cluster-difference model can also provide it. **Independent
clusters alone, or a zero mean alone, are insufficient.** Grouping related cases
does not establish sign exchangeability. Deterministic system outputs on a
curated workload do not automatically satisfy it. This program accepts a
declared partition; it cannot certify the experimental design or assumptions.

Before examining outcomes, fix cases, binary pass criteria, partition, complete
candidate family, alpha and one analysis. Include all planned candidates. Holm
controls familywise error under valid individual tests even when candidates
share the baseline and their tests are dependent. This does not cover repeated
looks, outcome-chosen groups, selective candidate reporting or adaptive stopping.

## Using your observations

The result CSV has header `case,baseline,candidateA,candidateB`, with two through
sixteen distinct candidates and complete literal `0`/`1` outcomes on every row.
Case IDs are unique. The second UTF-8 CSV has header `case,cluster`; every case
must appear exactly once, with no unknown IDs. Groups are a disjoint partition.
There must be 2–2000 cases and 2–128 nonempty clusters; each file is at most
2 MiB. Quoted Unicode IDs, BOM and CRLF work. Empty IDs, edge whitespace, ASCII
controls, blank records, duplicate assignments and incomplete observations fail.
Group order follows first occurrence in the benchmark, regardless of mapping order.

Both input paths must resolve to regular files inside the current workspace.
Retain independent SHA-256 digests of both original files and substitute them
for the explanatory uppercase tokens below:

```sh
python3 -B line-1/tools/cluster-verdict/cluster_verdict.py --input RESULTS.csv --mapping GROUPS.csv --expected-input-sha256 RETAINED_RESULTS_DIGEST --expected-mapping-sha256 RETAINED_GROUPS_DIGEST --alpha 0.05 --max-details 20
```

Alpha accepts 0.000001–0.2; use the planned value. `--max-details` accepts 0–128.
All groups are always analyzed; the display cap cannot change results or the
complete group-detail digest. No input files are modified. Output is ASCII-escaped
JSON on stdout. Exit 0 means analysis completed regardless of rejection; exit 2
means invalid input, with no partial stdout. These statuses are not adoption
decisions. Use a new destination if redirecting output. Decoded labels need the
usual escaping when embedded in HTML.

## Exact computation and interpretation

For candidate `c` and group `g`, calculate the integer difference
`d[g] = sum(candidate_pass - baseline_pass)` over cases in that group. The
observed statistic is `sum(d)`. Under the asserted null, independently multiply
each whole-group difference by `-1` or `+1`. The two-sided p-value counts sign
assignments with `abs(null_sum) >= abs(observed_sum)`, including ties. Integer
dynamic programming preserves multiplicities; it does not approximate or sample.
Zero differences are integrated out since they double numerator and denominator
equally. Reported assignment counts therefore cover nonzero groups only.
All-zero differences return p = 1. Internal wins and losses may cancel a group
to zero even when individual cases disagree.

Apply exact Holm adjustment to the entire supplied family. Comparisons against
alpha use `Fraction`, never rounded decimals. Numerators, denominators and sign
assignment counts are strings to preserve large integers in JSON consumers.
The signed effect is the total pass difference divided by the case count; it
weights cases equally. Unequal group sizes retain unequal influence on this
statistic. This is not a test of an equal-group average or a generic weak
zero-mean null. It provides no confidence interval or equivalence claim.
Rejection is two-sided: inspect the reported direction. A significant loss is
not an improvement, and non-rejection is not proof of equivalence.

Raw-file pins bind bytes; the canonical complete-group-detail SHA-256 binds the
ordered list of all group summaries, independent of the display cap. Neither
proves honest observations, representative sampling or preregistration time.
No currency, price, pool, payment, wallet, network or account is needed.

## Checks and source reuse

```sh
python3 -B -m unittest discover -s line-1/tools/cluster-verdict -v
```

Thirteen tests passed. They exhaust every length-2–4 vector with entries -2 to 2
against direct sign enumeration; check 100 seeded unequal-magnitude vectors;
exhaust several conditional nulls for p-value calibration; compare all singleton
win/loss counts through eleven with exact McNemar; and compare forty full seeded
benchmark families with independently enumerated sign assignments. Further
checks cover Holm ties/boundaries, zeros, internal cancellation, 128-group integer
precision, caps, Unicode/quoted IDs, BOM/CRLF, mapping validation, pins, no partial
CLI output, input immutability and a standalone copied-folder CLI. These are local
checks, not independent certification or validation of a user's statistical model.

`ladder_engine.py` is the unchanged Candidate Ladder source. `grouping_engine.py`
is the unchanged Cluster Influence source; only its validation, mapping, encoding,
digest and bounded workspace-read helpers are used. The new calculation never
invokes deletion diagnostics or inherited case-level inference. `provenance.json`
pins both ordinary source snapshots. All dependencies needed offline are included.
