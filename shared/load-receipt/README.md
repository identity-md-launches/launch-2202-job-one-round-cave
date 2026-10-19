# Load Receipt

Replay a log pack's entire timeline, partition a time window by timestamp-interval
depth, and retain an exact calculation receipt for its accounting and two declared
budgets. This connects **Line 3's Timeline Load** to **Line 4's Worksheet Receipt**.
Copy this whole folder for standalone Python 3.10+ standard-library use, offline.

```sh
python3 -B shared/load-receipt/load_receipt.py demo
```

Observed locally: the synthetic five-second window has one second at depth zero,
two at depth one and two at depth two. Its interval-time integral is six seconds,
mean depth is exactly **6/5**, and covered fraction is **4/5**. The demo replays a
passing mean-depth budget of 2, faithfully replays a failed budget of 1, and rejects
a changed histogram even after its content hash is recalculated. Demo exit is 0.

## Use your own evidence

Create a pack from public or nonsensitive workspace logs with the shipped replay
tool. It accepts only named regular files inside the current workspace:

```sh
python3 -B shared/load-receipt/engines/timeline/replay.py pack path/to/worker.log --ignore-unmatched > shared/my-pack.json
```

Construct a request JSON with exactly these fields:

| Field | Value |
| --- | --- |
| `pack` | The complete Timeline Replay pack object, including embedded original bytes |
| `start`, `end` | Offset-aware ISO instants, half-open window, at most six fractional digits |
| `max_uncovered` | Nonnegative time expression such as `1 s` or `250 ms` |
| `max_mean_depth` | Nonnegative dimensionless expression such as `3/2` |

Choose the window and policies yourself. Neither budget is a claim about service
load or availability. Feed the request to `create`:

```sh
python3 -B shared/load-receipt/load_receipt.py create < shared/my-request.json > shared/my-receipt.json
```

Retain `receipt_sha256` independently. To replay the receipt later, supply that
retained value as `DIGEST`:

```sh
python3 -B shared/load-receipt/load_receipt.py verify --expected-sha256 DIGEST < shared/my-receipt.json
```

`DIGEST` is the receipt's canonical **content digest**, excluding its own digest
field, rather than a hash of the formatted JSON file. An independent copy pins
the request, pack, exact shipped source bytes, coverage result, arithmetic receipt
and claim statuses. Changing JSON whitespace or object key order is allowed.
Extracting a digest from an already untrusted replacement does not authenticate it.

**Exit 0:** all declared claims pass. **Exit 1:** a valid calculation has a failed
claim, including faithful replay of that failure. **Exit 2:** invalid input,
dimensions, pin, source drift, replay mismatch or size limit. Invalid calculations
produce no partial stdout. `verified: true` establishes faithful recomputation;
consult `calculation_exit` and the worksheet checks for whether policies passed.

## Accounting and limits

For each depth `d`, let `t[d]` be the complete histogram duration in microseconds.
The worksheet checks `sum(t[d]) == window`, computes the interval-time integral
`sum(d * t[d])`, checks zero-depth duration against its budget, and derives covered
time, covered fraction and mean depth using exact rational arithmetic. The
histogram is recomputed from all embedded evidence; a standalone valid worksheet
with substituted totals cannot pass combined verification. All eight steps and
the nested receipt are replayed. Type-sensitive canonical comparison rejects
boolean/number substitutions. Events outside the selected window are also
replayed. Undated lines remain explicit. Displayed segments are omitted (`limit=0`)
while all depths and duration totals are retained.

The CLI reads stdin and eight fixed shipped source files only. It does not reopen
log source labels, inspect configuration, read environment variables, execute log
content, use keys, sign, send, pay or contact a network. Dependencies are unchanged
ordinary source files, listed with SHA-256 pins in `provenance.json`. Imports are
fixed sibling modules; use the CLI or a fresh interpreter to avoid generic module
name collisions with other tools.

Requests, receipts and output are limited to **2 MiB**. JSON must be strict UTF-8
with no duplicate keys, floats or nonfinite constants; integers have at most 20
characters and nesting at most 24 levels. Timeline Replay's own 64-source/2-MiB
raw-log bounds and Worksheet Flint's bounded expression/rational limits also
apply. The combined receipt size is often the tighter bound. No partial receipt
is emitted on failure. There is no redaction: receipts embed the original logs.

Depth counts compatible timestamp uncertainty intervals, **not confirmed
simultaneous events or service load**. Zero depth is not downtime. Clock bounds
are assertions; widening them may remove gaps and increase depth without changing
a single source byte. Exact arithmetic cannot establish log truth, completeness,
clock accuracy, causality, input accuracy or policy suitability. Hashes are not
signatures, timestamps or authorship evidence. No currency or exchange rate is
needed.

## Checks and actual use

```sh
python3 -B -m unittest discover -s shared/load-receipt -v
```

Twelve integration tests passed: independent seeded depth/integral checks,
half-open evidence boundaries, failed-claim replay, source/digest mismatch,
rehashed coverage and arithmetic substitutions, outside-window tampering,
type confusion, invalid dimensions and JSON, immutability, provenance, and copied
standalone CLI statuses with no partial stdout.

The gathering also timestamped four actual local tool runs and reviewed the same
eight journal entries under asserted 0 ms and illustrative 750 ms clock bounds.
The 224,285-microsecond window had only eight microseconds covered in the first
model, while all eight intervals covered the entire window in the second. Both
combined receipts replayed. `gathering/observed-load-receipt.json` records the
observed journal and receipts. This is process-observation evidence, not an
external service incident; demo payloads and post hoc budgets remain illustrative.
