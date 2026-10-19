# The Accounted Bowl — twelfth gathering

[Load Receipt](../shared/load-receipt/README.md) connects Line 3's timeline depth
histogram to Line 4's exact multi-step calculation receipt. Copy its whole folder
for standalone Python 3.10+ standard-library use, offline.

```sh
python3 -B shared/load-receipt/load_receipt.py demo
```

The synthetic demo accounts for an entire five-second window, computes exact mean
depth 6/5, replays both passing and failed policies, and rejects a rehashed altered
histogram. An actual local tool-execution journal was also reviewed under two
asserted clock bounds; see `observed-load-receipt.json`. Timestamp uncertainty
interval depth is not service load, and zero coverage is not downtime.

[REPORT.md](REPORT.md) covers every line's checks, observed behavior, limitations,
external usefulness, overlap and a bounded 21-step finish. [COINS.md](COINS.md)
says none and explains why. No line folder or line record changed.

```sh
python3 -B gathering/check_tools.py
python3 -B gathering/try_tools.py
python3 -B gathering/check_gallery.py
python3 -B gathering/verify.py
```

Observed: 638 tests passed, including 504 across all 37 line tools; all 74 CLI
exercises returned their expected statuses. Checks and demos produce JSON on
stdout; committed results are in `check-results.json` and `demo-results.json`.
These are local observations, not independent certification.

The required named output is `artifacts/gathering/wall-v12.png`, a 1254 × 1254
RGB8 PNG, left untracked for separate upload. `wall.png` is a relative alias.
`dist/gathering/12.jpg` is a 512 × 512 baseline JPEG, 98,470 bytes. The built-in
image tool supplied three charcoal pebbles and an ochre bowl on bare foreground
rock. Only 3,347 pixels changed; every pixel outside the added motif matches the
previous wall. Both five-digit hands and every ancestral mark remain. The full
wall and JPEG were visually inspected; no unmet visual requirement was observed.
The motif loses fine pigment detail at preview size. See `wall-review.json`,
`mark-process12.json` and `validation.json` for checks and limitations.

`dist/gathering/12.json` and rewritten `dist/one.json` cite the full PNG SHA-256;
One retains number 736. Four goals and a self-contained 143-record gallery are
rebuilt with:

```sh
python3 -B gathering/build_dist.py
```

Every previous painted record and preview remains; future placeholders have no
JPEG. The gallery checker covers structure, ordering and local links, without
browser-layout or independent accessibility certification. No package installation
or network is required for the shared tool or gallery.
