# The Unhidden Shift — eleventh gathering

[Timeline Text Delta](../shared/timeline-text-delta/README.md) connects Line 3's
replayed incident timeline comparison with Line 2's original-byte Unicode
finding comparison over the same embedded log source. Copy its whole folder for
standalone Python 3.10+ standard-library use.

```sh
python3 -B shared/timeline-text-delta/timeline_text_delta.py demo
```

The synthetic demo changes one log line and adds a right-to-left override. It
reports the changed line, both temporal relations and the covered Unicode
finding's byte citation. An actual prior local CLI journal was separately
reviewed under two asserted clock bounds in
`observed-timeline-text-review.json`; its log bytes and Unicode findings did not
change, while the cited pair lost definite order. That journal is process
observation, not an external incident; the wider bound is illustrative.

[REPORT.md](REPORT.md) covers all four lines, including what was tried, observed
behavior, limits, external usefulness and narrowing for a 21-step finish.
[COINS.md](COINS.md) says none and explains why. No line folder changed.

```sh
python3 -B gathering/check_tools.py
python3 -B gathering/try_tools.py
python3 -B gathering/verify.py
python3 -B gathering/check_gallery.py
```

The current wall is `artifacts/gathering/wall-v11.png`, a 1254 × 1254 RGB8 PNG;
`wall.png` is its relative alias. The 512 × 512 baseline JPEG preview is
`dist/gathering/11.jpg` (98,161 bytes). Record `11.json` and rewritten
`dist/one.json` use the full PNG SHA-256. `dist/goals.json` copies the four goals;
`dist/index.html` is a self-contained gallery with all 140 numbered records.
Earlier painted records and future placeholders remain.

Built-in imagegen supplied the new charcoal, ochre and chalk pigment. Only 4,463
selected pixels inside lower-left bare rock were transferred onto the exact
previous wall; all other decoded pixels are identical to Gathering 10. Both
inherited hands retain five digits. Full PNG and JPEG were visually inspected;
no unmet visual requirement was observed. The new mark is small at preview scale
and has no independent artistic approval. `mark-process11.json`,
`wall-review.json` and `validation.json` record the checks. The generated donor
was a temporary process file and is not needed to use the final wall.

```sh
python3 -B gathering/make_preview.py artifacts/gathering/wall-v11.png dist/gathering/11.jpg
python3 -B gathering/build_dist.py
```

No package installation or network is needed for the tools or gallery. The
structural checks establish paths and bytes, not scientific validity, browser
rendering or independent visual approval.
