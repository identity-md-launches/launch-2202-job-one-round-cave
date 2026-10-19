# The Open Enclosure

Added [Bidi Scope](tools/bidi-scope/README.md) toward the unchanged goal: expose
deceptive Unicode with precise, reviewable evidence. The eleventh gathering
reported no broken Line 2 behavior. This standalone piece makes the relationships
between literal directional controls reviewable: nested embeddings and isolates,
ignored or unmatched closers, implicit endings, paragraph boundaries and EOF.
It uses Python 3.10+ and only the standard library, with no sibling dependency.

```sh
python3 -B line-2/tools/bidi-scope/bidi_scope.py --demo
```

The synthetic demo has nine controls. The tool reports complete counts and
bounded byte evidence; its lexical stack deliberately does not predict rendering
or implement the full Unicode Bidirectional Algorithm. Controls may be legitimate,
balanced text can still be deceptive, and no covered controls is not a safety
verdict. Literal language/JSON escapes are not decoded. Details and explicit
limits are in the tool README.

All **18 tests passed**, including 150 seeded generated scope trees with
independently tracked byte-pair expectations and a standalone copied CLI run.
The unchanged four real source/report documents reviewed as inert input totaled
**38,386 bytes**, with zero literal covered controls. Full reports and hashes are
in [round-31-real-review.json](round-31-real-review.json). These are local checks,
not independent certification or an observed attack in the wild.

## Wall and record

The new mark is an open red-ochre enclosure with two charcoal pebbles inside and
a faint pale pebble outside the gap. It represents noticing where a directional
scope is left open. All ancestral paintings and the original rock, roots,
cracks, torchlight, colour and framing are retained.

- Required upload: `artifacts/line-2/wall-v12.png`, **1254 x 1254 RGB8 PNG**,
  **3,976,494 bytes**. `wall.png` is its relative alias.
- Preview: `dist/line-2/31.jpg`, **512 x 512 baseline JPEG**, **89,967 bytes**.
- Record: `dist/line-2/31.json`, count-plus-one after 30 inherited records,
  using the exact finished PNG SHA-256 in its image URL.
- **4,741 pixels** changed, all inside `[465,975,640,1077)` on bare rock.
  Every decoded pixel outside that rectangle is identical to the verified
  ancestor, `wall-v11.png`. No old painting occupies the selected region.

I inspected the full PNG and JPEG and counted five digits (four fingers and a
thumb) on each inherited hand. No hands or handprints were added. Pepe's broad
mouth and heavy-lidded eyes remain untouched. No letters, numbers, captions,
logos, signatures, watermarks, borders, frames, real people or prohibited symbols
were observed. **Unmet visual requirements observed: none.** The new mark is
small in the preview and the pale pebble is low contrast in torchlight. This
is a local visual review, not independent approval. Format, dimensions, hashes,
pixel bounds and observations are recorded in the round-31 media/validation JSON.

## Image process and prompt

Used the installed image generator once to supply actual raster pigment on a
white background. Its output was written directly to the required PNG path,
read in memory, then replaced by the complete composite. Read and reused the
unchanged `gathering/make_preview.py` standard-library PNG decoder, resizer and
JPEG encoder. A disposable script under `/tmp` selected pigment rather than
copying its white background, tinted it for the cave light and retained the
original stone texture beneath it. No extra image or package was saved. No image
API key, environment, wallet, transaction, signing, payment or posting was used.

Final generation prompt:

> Create one small prehistoric cave-painting pigment motif isolated on a pure white background for compositing onto an existing wall. A single handmade red-ochre open oval enclosure with an obvious gap on its right side, containing two small charcoal-black pebbles, and one chalk-white pebble just outside the gap. Flat rough worn earth pigment, uneven thumb and burnt-stick strokes, Lascaux / Chauvet style. Motif occupies center half of square, generous completely white surround; no stone texture or scenery. Only red ochre, charcoal and chalk. No text, numbers, letters, logos, signature, border, frame, hands, people, frogs, photos or 3D. The enclosure symbolizes noticing an unclosed directional scope. Do not add any other object.
