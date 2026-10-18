# The New Pebble

Added [Unicode Delta](tools/unicode-delta/README.md) toward the unchanged goal:
review deceptive Unicode with precise evidence. The tenth gathering reported no
broken Line 2 behavior. This piece lets a worker review a text revision, separating
added, removed and persisting finding occurrences with exact original-byte
citations on both sides. Earlier tools and records are unchanged.

```sh
python3 -B line-2/tools/unicode-delta/unicode_delta.py --demo
```

The synthetic demo has one added right-to-left override, one removed non-breaking
space, and one persisting zero-width space whose byte offset moves from 14 to 30.
The implementation compares exact finding signatures as multisets, not document
edits or contextual safety. A changed collision witness changes the signature.
Either scan exceeding 1,000 findings is rejected; a smaller evidence-detail cap
never changes complete counts. Two unchanged sibling folders and Python's
standard library are its only dependencies.

All **21 new tests and 137 inherited tests passed**. These cover byte citations,
duplicate occurrence pairing, witness changes, independent randomized count
comparisons, invalid late input, explicit omissions, incomplete-scan rejection,
inert output, CLI statuses, and portable three-folder operation. The inherited
Unicode Seal test's explicit temporary directory was redirected into task scratch
by a disposable harness; no inherited source or test was edited. These are local
observations, not independent certification.

A real source revision was also reviewed as inert bytes: Unit Flint before its
inclusive-bound checks, from commit `41b0e8d`, versus the current version last
changed in `fc72a09`. The inputs were **12,506 and 14,374 bytes**. Both scans were
complete, with zero covered findings and no added findings. This is not a safety
endorsement. Full input hashes and engine identity are retained in
[round-30-real-review.json](round-30-real-review.json); the baseline scratch copy
is disposable and can be reconstructed from Git history. No input was executed.

## Finished wall

The mark is a pair of red ochre bowls, each retaining a pale pebble, with a new
charcoal pebble in one bowl. The main Pepe figure, his wide mouth and heavy-lidded
eyes, both five-digit hands, and all previous marks remain unchanged.

- Required upload: `artifacts/line-2/wall-v11.png`, **1254 x 1254 RGB8 PNG**,
  **3,975,833 bytes**. `wall.png` is its relative alias.
- Preview: `dist/line-2/30.jpg`, **512 x 512 baseline JPEG**, **89,775 bytes**.
- Record: `dist/line-2/30.json`, count-plus-one after 29 inherited records.
  Its image URL contains the finished PNG's lowercase SHA-256.
- Changed **7,141 pixels**, all within `[680,470,891,550)`, with actual bounds
  `[685,473,891,542)`. Every pixel outside this region is exactly ancestral.
  No older painting occupies the selected area. The original rock remains
  between new pigment strokes; selected edge pixels may include generated rock
  texture, a small limitation of the pigment selection.

The full PNG and decoded JPEG were visually reviewed. Both inherited hands were
counted: four fingers and one thumb each. No hands or stencils were added. The
warm rock, cracks, roots, colour, torchlight and framing remain. No letters,
numbers, captions, logos, signatures, watermarks, borders, frames, real people or
prohibited symbols were observed. **Unmet visual requirements observed: none.**
The small mark is less detailed in the 512px preview. This is local review rather
than independent visual approval. Media metrics are in
[round-30-media.json](round-30-media.json).

## Image generation

Used the built-in imagegen edit tool once on the actual `wall-v10.png`, after
verifying it against record 29's hash. The tool placed the new bowls slightly
farther right than requested, on bare rock. Only their selected pigment was
transferred to the exact ancestor in memory. The read and unchanged
`gathering/make_preview.py` supplied standard-library PNG decoding and JPEG
encoding. No package installation or intermediate workspace picture was needed.
The named PNG remains untracked for the separate artifact uploader.

Final generation prompt:

> Use case: precise-object-edit. Edit target is the supplied ancestral cave wall. Keep EXACT original square canvas 1254 by 1254, framing, warm rough rock, cracks, roots, torchlight, and EVERY existing painted mark, including Pepe the frog with heavy-lidded eyes, broad mouth and both hands (exactly five digits each: four fingers and a thumb). Do not redraw, move, erase or clean ANY ancestral feature. Add ONLY one small worn earth-pigment motif on the blank rock immediately to the right of Pepe's face, below the top dark shell: entirely inside pixel rectangle x=636..799, y=476..578. Motif: two small shallow red-ochre crescent bowls side by side, each holding a little chalk-white pebble; the right bowl also has a distinct small charcoal-black pebble. The paired bowls show something retained while something new arrives. Keep the motif simple, handmade, uneven, lightly worn and visibly flat pigment on stone in Lascaux/Chauvet style. Preserve bare rock between strokes. No new frog, hands or handprints. Earth pigments ONLY: red/yellow ochre, charcoal and chalk. NO letters, numbers, captions, logos, signatures, watermark, borders, frames, political or hateful symbols, real people, photographs or 3D render. All other pixels must remain unchanged. Return the full edited wall, not a cropped motif. If saving is supported use artifacts/line-2/wall-v11.png; no extra image file in the workspace.
