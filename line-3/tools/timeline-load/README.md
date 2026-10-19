# Timeline Load

Timeline Load fully replays a timestamped evidence pack, then partitions a chosen
time window into maximal spans with a constant number of covering event-uncertainty
intervals. It reports exact time spent at every depth, including zero. This gives
an incident worker a compact view of where retained timestamp evidence clusters.

One command from the repository root shows it working offline:

```sh
python3 -B line-3/tools/timeline-load/timeline_load.py demo
```

Tried locally: the synthetic five-second example returned five spans; depth zero
lasted one second, depth one two seconds, and depth two two seconds. Its one
undated diagnostic is counted separately. The example is not a real incident or
a measured clock bound.

For an existing Timeline Replay pack inside the current workspace:

```sh
python3 -B line-3/tools/timeline-load/timeline_load.py analyze path/to/pack.json --start 2026-10-18T10:00:00Z --end 2026-10-18T10:05:00Z --expect-sha256 TRUSTED_DIGEST
```

Supply an independently retained lowercase SHA-256 of the exact pack bytes for
`TRUSTED_DIGEST`, or omit that option for internal consistency checking alone.
The included `replay.py` can create packs from existing workspace log files;
see its `pack --help`. The tool reads only the named pack during analysis. It
never reopens paths inside that pack, executes services or contacts a network.
This whole folder is independently portable and uses Python 3.10+ standard
library only. The dependency snapshots are ordinary files with hashes recorded
in `PROVENANCE.json`.

Intervals and the query are half-open. Query endpoints are exact offset-aware
ISO instants; log timestamp precision and the pack's asserted symmetric clock
bound produce each event interval. Intervals are clipped to the query. Endings
at a time are removed before beginnings at that time are counted, so touching
intervals need not overlap. Adjacent spans with equal depth are merged. `--limit`
shows at most 0–200 spans, with exact hidden-span counts; the depth histogram
and totals always cover the entire window. The tool replays all embedded
evidence before querying, including events outside the window. Bad packs and
bad pins fail without a partial JSON report.

Depth measures how many timestamp uncertainty intervals *could* cover an
instant. It does not establish simultaneous events or service load. Zero depth
is an evidence-model coverage gap, not proof of inactivity. Undated lines
cannot be placed. Clock bounds are analyst assertions, and full replay proves
internal consistency rather than authenticity or completeness. The report
does not echo messages or source bytes; the input pack itself contains exact
unredacted logs. No coin, wallet, key, signing or payment is needed.

Run focused checks with:

```sh
python3 -B -m unittest discover -s line-3/tools/timeline-load -v
```

Observed locally: seven tests passed, including 500 seeded interval sets
checked against an independent discrete-time oracle, full-pack tamper rejection,
half-open adjacency, bounded display, exact offsets, source snapshot provenance
and a copied-folder CLI with good and bad digest pins.
