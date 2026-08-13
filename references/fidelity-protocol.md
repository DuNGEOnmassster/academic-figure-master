# Figure fidelity protocol

Use this protocol for every reconstruction and refinement. It is deliberately stricter than a semantic redraw: the reference remains visible beside the editable render throughout calibration, and pixel-exact work must pass deterministic numeric gates.

## Two-layer contract for pixel-exact paper figures

When a source PDF is available, use direct source-operator extraction before manual redrawing:

1. `source-vector-operators` is visible by default and preserves the PDF's paths, fills, strokes, glyph outlines, and source image operators.
2. `semantic-edit-layer` is hidden by default and preserves convenient text-as-text and named conceptual components.
3. Removing the hidden layer must produce an identical render, pixel for pixel.
4. Every extracted operator layer receives a SHA-256 provenance hash tied to the cited PDF and exact figure number.

This contract is honest about the tradeoff: outlined source glyphs give exact typography but are not editable as text, while the semantic layer is easy to edit but may not be pixel-identical. If the original PDF includes a bitmap, preserve it as a named data-image operator and disclose its count; do not relabel it as vector geometry.

## Three synchronized views

Maintain three views at the same review size:

1. **source crop** — the exact paper figure or user-supplied reference;
2. **editable render** — the current SVG, draw.io, or PowerPoint reconstruction; and
3. **edge overlay** — source edges in magenta, redraw edges in cyan, coincident edges in black.

Never judge only the source or only the redraw. A clean redraw can still be wrong, while a noisy overlay can reveal one shifted column, missing connector, or incorrect aspect ratio immediately.

## Calibration passes

Run the passes in order. Do not polish a later pass while an earlier one still differs.

1. **Crop and aspect ratio** — isolate the intended panel, remove captions and neighboring article text, then match the occupied bounding box and whitespace.
2. **Topology and count** — match panels, nodes, feature-map planes, repeated blocks, arrows, skip paths, legends, and ellipses. Count repeated objects explicitly.
3. **Geometry** — match centers, widths, heights, gaps, alignment lines, curve control points, and connector entry/exit points.
4. **Typography** — transcribe labels exactly; match family class, case, line breaks, mathematical subscripts, weight, anchor, and relative size.
5. **Appearance** — match fills, stroke colors, dash patterns, line weights, arrowheads, grayscale contrast, and panel boundaries.
6. **Small detail** — match ticks, dimension labels, plate labels, thumbnails, annotations, and deliberate irregularities.

After each pass, regenerate the comparison plate and fix the largest visible cyan/magenta separation before proceeding. For source-operator extraction, most corrections should be crop or operator-trim changes, not manual path edits.

## Editability contract

- Original/semantic work keeps text as `<text>` or native editor text. Exact source text may be glyph paths in the visible layer but must have a text-as-text semantic editing counterpart.
- Connectors remain paths or native connectors with independent IDs.
- Every scientific object or repeated stage has a stable named group.
- No `<foreignObject>`, script, or remote asset is allowed inside a deliverable SVG.
- `<image>` is allowed only in a cited pixel-exact paper layer, must use an embedded data URI, must receive a stable ID, and must be counted in the pixel-exact manifest.
- Source crops are review evidence only. They are not reusable assets and retain the source paper's rights.

## Local calibration command

Generic gallery generation has no runtime dependency. Rebuilding paper SVGs and comparison plates requires Poppler, Pillow, Node.js, and Sharp:

```bash
python -m pip install Pillow
npm install --no-save sharp
python scripts/extract_pixel_exact_paper_figures.py
python scripts/calibrate_paper_figures.py
```

Source URLs, exact PDF pages, normalized crop boxes, and rare operator-trim overrides live in `references/paper-figure-sources.json`. The extractor downloads PDFs into ignored temporary storage, copies their selected operators into tight dual-layer SVGs, and writes `assets/paper-redraws/pixel-exact-manifest.json`. The calibration harness renders independent PDF crops and SVGs, then writes original/redraw/edge-overlay plates plus `assets/comparisons/qa-report.json`.

## Acceptance rules for all 35 SVGs

Every SVG, not only the paper redraws, must pass the same structural core:

- a tight `viewBox` appropriate to its content;
- no slide-style title banner inside a reusable figure;
- at least one stable named group and no duplicate IDs;
- native semantic geometry, or a disclosed pixel-exact source-operator layer plus hidden semantic editing layer;
- no clipped labels or off-canvas scientific objects;
- explicit provenance and a one-command reproduction entry; and
- a final render inspected at repository-preview size and publication size.

Pixel-exact paper reproductions additionally require:

- a specific cited paper figure number and source-operator SHA-256;
- both `source-vector-operators` and `semantic-edit-layer` with unique IDs;
- hidden-layer isolation pixel match exactly `1.0`;
- tight-content aspect-ratio error no greater than `1%`;
- independent PDF↔SVG pixel match of at least `80%` at tolerance 32; and
- a three-view calibration plate with no clipped content or neighboring caption text.

The independent pixel score tolerates rasterizer-specific antialiasing; it does not replace the source-operator provenance check. Data plots additionally require formula, code, source data, or an honest `illustrative-normalized` label.
