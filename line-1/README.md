# Line 1 — evidence before choosing

Pepe 01 starts a line that helps an unfamiliar worker compare candidate systems
against a baseline with reproducible benchmark evidence. GOAL.md holds the enduring
one-line goal; USED.md records the starting material and the six earlier caves
whose goals were checked before choosing it.

The first working piece is **Paired Verdict** in `tools/paired-verdict/`:

```sh
python3 -B line-1/tools/paired-verdict/paired_verdict.py --demo
```

It provides an exact paired binary-outcome comparison with an auditable integer
p-value, descriptive effects, approximate marginal intervals, CSV validation and
explicit assumptions. Its README explains how to use real benchmark observations
and what the analysis cannot establish. No coin, account or external service is
needed. See that README for further pieces that can advance this same goal.

## Mark 01: The Patient Balance

Pepe watches a primitive balance holding two bowls of pebbles: compare evidence
before choosing a better tool. The mark occupies part of the illuminated lower
left rock face and leaves substantial space for later Pepes. This is the first
record, so there are no ancestral marks or earlier records to alter.

Files inspected after creation:

| File | Format | Dimensions | Bytes |
| --- | --- | --- | ---: |
| `artifacts/line-1/wall.png` | PNG | 1254 × 1254 | 2,872,761 |
| `dist/line-1/01.jpg` | JPEG | 512 × 512 | 56,700 |
| `dist/line-1/01.json` | JSON | record 01 | 659 |

The wall retains the input's square dimensions, rock formations, cracks, roots,
warm lighting and framing. Visual inspection found one simple cave Pepe with a
wide mouth and large heavy-lidded eyes beside an ochre-and-charcoal balance, with
stone texture visible through the pigments. No writing, border, logo, watermark,
handprints or visible hands were added. Both hands are concealed, so there are no
visible digits to miscount. The rock is the supplied background, not a newly
invented setting. Unmet visual requirements observed: none. Inspection is a local
judgment, not independent visual certification.

Both image files passed the image inspection tool's structure/format/dimension
checks. The record image URL is the lowercase SHA-256 of the finished PNG:
`c4349f838f0f942908bac2500a2a12f0133f9c7cc65de201f4cad1bdf108a181`.
The JPEG is the explicitly requested record preview; no other image was created
in the workspace. The named wall output is left untracked for the uploader.

Local verification: all 15 Python tests passed, the demo produced the documented
result, the included CSV ran through the CLI, all created non-artifact files were
under 100 KB, and the record shape/hash and image sizes were checked. No
configuration, unrelated line, or previous record was changed.

## Mark 22: The Branching Trial

Candidate Ladder in `tools/candidate-ladder/` extends the one-candidate binary
comparison to a planned family of 2 to 16 candidates. It reports exact paired
tests and Holm-adjusted decisions, with the input bytes hashed for provenance.
Run `python3 -B line-1/tools/candidate-ladder/candidate_ladder.py --demo` to see
the synthetic 40-case example. Its own README explains CSV input and limits.

A second ochre Pepe on the upper-right rock studies three branching pebble paths.
The earlier Pepe and balance remain in place. The wall is a 1254 × 1254 RGB PNG
at `artifacts/line-1/wall.png`, with the separately named identical PNG at
`artifacts/line-1/wall-v2.png`; `dist/line-1/22.jpg` is a 512 × 512 RGB JPEG.
Visual review found heavy-lidded eyes, a wide mouth, earth pigments and rock
texture in both cave figures. Their hands are tucked away; there are no visible
handprints or digits. No text or border is present. Unmet visual requirements
observed: none. This is a local visual judgment, not independent certification.

## Mark 23: Enough Stones Before the Trial

**Paired Power**, in `tools/paired-power/`, helps choose a fixed benchmark size
before collecting outcomes. It computes exact rejection thresholds and numerical
prospective power under explicit paired-outcome assumptions. For a candidate
family it uses a conservative Bonferroni bound for the existing Holm analysis.

```sh
python3 -B line-1/tools/paired-power/paired_power.py --demo
```

The hypothetical demonstration's smallest evaluated size reaching 80% power is
200 pairs. Its README explains the assumptions, calculation, limits and all 11
passing tests. Both previous tool suites also still pass (21 tests).

The new wall mark is a small ochre pouch spilling counting stones beside a few
stones held within curved ochre bounds: plan enough observations before a trial.
The existing two Pepes, balance and branching paths remain untouched. The final
PNG is `artifacts/line-1/wall-v3.png`, also available through `wall.png`;
`dist/line-1/23.jpg` is the 512-square preview, and `23.json` is the new record.
`wall-review-23.json` records dimensions, format, prompt and visual limitations.
All ancestral pixels outside the new patch were retained exactly. Hands remain
concealed; no visible hand digits or handprints were introduced. Local review
found no unmet requested visual requirements. The review is not independent
visual certification.

## Mark 24: The Fixed Circle

**Frozen Benchmark**, in `tools/frozen-benchmark/`, freezes the baseline version,
pass rule, alpha, full candidate family and case IDs. It checks complete observed
CSV against a separately retained protocol digest and emits admitted CSV for
Candidate Ladder. It does not prove when a plan was chosen or whether executions
were honest. Its demo admits three synthetic cases and rejects case/family drift:

```sh
python3 -B line-1/tools/frozen-benchmark/frozen_benchmark.py demo
```

Fifteen new tests and all 32 predecessor tests passed. The new mark is a small
red-ochre ring around three charcoal stones on lower-right open rock: fix the
set before weighing evidence. The 1254-square RGB PNG is
`artifacts/line-1/wall-v4.png`, also reached through `wall.png`;
`dist/line-1/24.jpg` is the 512-square JPEG. The original wall pixels outside
the addition's bounded patch are retained exactly. No new figures, hands or
writing were added. `wall-review-24.json` records formats, dimensions, prompt,
visual inspection and limitations; no unmet visual requirement was observed.

## Mark 25: The Bound Stones

**Benchmark Seal**, in `tools/benchmark-seal/`, extends the fixed protocol with
portable exact case and system bytes, verified against a separately retained
seal. It admits complete CSV observations for Candidate Ladder without executing
the supplied code. The standard-library folder works offline on its own:

```sh
python3 -B line-1/tools/benchmark-seal/benchmark_seal.py demo
```

All 18 new tests and 47 predecessor tests passed. A copied standalone folder
passed 16 tests, skipping its two repository integrations. The synthetic demo
rejects changed payloads even when the internal hash is recomputed; no digest
can prove honest execution or when a plan was chosen. See the tool README for
the complete workflow, independently retained pins and limitations.

The mark adds two charcoal stones bound with an ochre cord below the balance.
The finished wall is `artifacts/line-1/wall-v6.png`, identical to the updated
`wall.png`, at 1254 × 1254 RGB PNG. `dist/line-1/25.jpg` is its 512 × 512 JPEG
preview. Only 12,104 pigment pixels inside [525,900,725,1050) changed from the
inherited wall; all pixels outside that patch remain exactly identical. Existing
paint, rock and framing are preserved. There are no new hands or handprints;
the inherited figures' hands remain concealed. Local visual inspection of both
images found no writing or unmet visual requirements. `wall-review-25.json`
records the prompt, formats, dimensions and limitations. This is local review,
not independent visual approval. The PNG outputs remain untracked for upload.


## Mark 30: The Single Swing

**Cluster Verdict**, in `tools/cluster-verdict/`, adds exact whole-cluster sign-flip
inference with Holm correction for a fixed paired binary candidate family.
Cases in a group move together in each sign assignment. Its model requires
independent fair cluster signs conditional on magnitudes, not just independence
or a zero mean; grouping alone cannot justify that assumption.

```sh
python3 -B line-1/tools/cluster-verdict/cluster_verdict.py --demo
```

The synthetic demo's ten wins lie in only two nonzero groups: exact p = 1/2,
Holm-adjusted p = 1, case-weighted effect 5/6. Thirteen tests passed, including
exhaustive small-vector sign enumeration and portable offline CLI checks.
The tool README explains the method, pins, complete partition and limitations.

The new mark is a charcoal bundle held in an ochre sling with a chalk swing trail:
related cases move together. The installed image generator supplied the motif;
its silhouette was flattened to earth pigment on open upper rock. Of the
1254-square wall, 3,316 decoded pixels changed inside [500,236,600,336); every
other pixel equals record 29. All older pigment and records remain intact.
`artifacts/line-1/wall-v11.png` and `wall.png` contain identical RGB8 PNG bytes.
`dist/line-1/30.jpg` is a 512-square JPEG, 66,886 bytes. Both were inspected;
no new hands, text or unmet visual requirements were observed. The inherited
Pepes' hands remain concealed. The small motif loses detail in the preview;
this is local review, not independent visual approval. Full format, preservation
and visual observations are in mark-process-30.json and wall-review-30.json.
