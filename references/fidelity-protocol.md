# Figure fidelity protocol

Use this protocol for every reconstruction and refinement. It is deliberately stricter than a semantic redraw: the reference remains visible beside the editable render throughout calibration.

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

After each pass, regenerate the comparison plate and fix the largest visible cyan/magenta separation before proceeding.

## Editability contract

- Text remains `<text>` or native editor text.
- Connectors remain paths or native connectors with independent IDs.
- Every scientific object or repeated stage has a stable named group.
- No `<image>`, `<foreignObject>`, script, or remote asset is allowed inside a deliverable SVG.
- When the paper uses a photograph or bitmap thumbnail, substitute a separately editable vector approximation and disclose it; never hide a raster inside an SVG and call it editable.
- Source crops are review evidence only. They are not reusable assets and retain the source paper's rights.

## Local calibration command

The editable gallery has no runtime dependency. Rebuilding source comparison plates is an optional QA operation:

```bash
python scripts/generate_gallery.py
python -m pip install Pillow
npm install --no-save sharp
python scripts/calibrate_paper_figures.py
```

Source URLs, exact PDF pages, and normalized crop boxes live in `references/paper-figure-sources.json`. The harness downloads PDFs into ignored temporary storage, renders the target pages, crops the figures, rasterizes the SVGs, and writes original/redraw/edge-overlay plates plus `assets/comparisons/qa-report.json`.

## Acceptance rules for all 35 SVGs

Every SVG, not only the paper redraws, must pass the same structural core:

- a tight `viewBox` appropriate to its content;
- no slide-style title banner inside a reusable figure;
- at least one stable named group and no duplicate IDs;
- editable text and vector geometry only;
- no clipped labels or off-canvas scientific objects;
- explicit provenance and a one-command reproduction entry; and
- a final render inspected at repository-preview size and publication size.

Paper redraws additionally require the three-view calibration plate and a specific paper figure number. Data plots additionally require formula, code, source data, or an honest `illustrative-normalized` label.
