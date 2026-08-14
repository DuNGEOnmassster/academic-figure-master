---
name: academic-figure-master
description: Create, reconstruct, and refine publication-ready academic figures as genuinely editable SVG, draw.io, or PowerPoint artifacts. Use for paper method diagrams, model architectures, SDE/ODE or manifold illustrations, graphical abstracts, reference-image component reconstruction, and local element-level edits where raster image generation is not an acceptable final deliverable.
---

# Academic Figure Master

Create a semantic figure first and compile it into native editable objects. Treat image generators as optional visual ideation tools, never as the source of truth for labels, geometry, or scientific relationships.

## Route the request

Choose one route before drawing:

- **Text or paper → figure:** extract the claim, entities, relations, stages, equations, and required labels.
- **Published PDF figure → pixel-exact dual layer:** extract the PDF's source operators first, keep that layer visible, and preserve or build a hidden semantic text-and-component layer for customization.
- **Existing raster image → editable reconstruction:** inventory every visible component, connector, label, group, alignment rule, and repeated style before rebuilding it.
- **Existing editable figure → targeted edit:** preserve unaffected object IDs, geometry, typography, and grouping; patch only the requested components.
- **Data → plot:** use a plotting library for data marks, then combine the exported vector plot with native annotations. Never redraw measured data by eye.

Read [references/output-contracts.md](references/output-contracts.md) for format-specific rules. Read [references/figure-ir.md](references/figure-ir.md) when a figure has more than one panel or will need iterative edits. For any reference-image or published-paper reconstruction, also read and follow [references/fidelity-protocol.md](references/fidelity-protocol.md). Consult [references/landscape.md](references/landscape.md) only when selecting an external model, tool, or asset source.

## Establish the figure contract

Before authoring, state or infer:

1. target format: `pptx`, `drawio`, or `svg`;
2. final physical size or aspect ratio;
3. venue/style reference and minimum readable font size;
4. exact text, mathematical notation, panel order, and directional semantics;
5. which parts must remain independently editable;
6. whether external assets are allowed and what attribution is acceptable.

Default to a restrained paper style: white background, one sans-serif family, 7–10 pt at final size, 1–1.5 pt strokes, a colorblind-safe palette, and no decorative 3D effects that imply false measurements.

## Build from a semantic scene

For nontrivial work, write a small scene manifest following [assets/examples/figure-spec.json](assets/examples/figure-spec.json). Give stable IDs to panels, nodes, connectors, labels, and reusable assets. Keep these layers distinct:

1. background and panel boundaries;
2. scientific objects and reusable primitives;
3. connectors, trajectories, braces, and uncertainty;
4. labels, equations, legends, and panel letters;
5. annotations and review notes.

Reuse original primitives from `assets/primitives/` when applicable. Search `assets/gallery-manifest.json` by tags before drawing a common architecture, paper concept, or curve from scratch. Its generated entries include provenance, fidelity, editable-output guarantees, and a one-command reproduction recipe. Their groups and IDs are deliberately editable:

- `manifold-grid.svg`: curved manifold, grid, samples, and geodesic;
- `sde-ode-trajectories.svg`: deterministic and stochastic paths;
- `hand-drawn-arrows.svg`: loose, loop, emphasis, and bidirectional arrows;
- `diffusion-process.svg`: forward noising and reverse denoising sequence;
- `tensor-stack.svg`: matrices, feature stacks, and dimension labels;
- `neural-modules.svg`: encoder, latent, decoder, attention, and merge blocks.

The directory also contains attention, convolution, graph, causal, optimization, uncertainty, data, training, ensemble, Bayesian, multimodal, and ablation sheets. Rebuild non-paper assets with `python scripts/generate_gallery.py`, or pass `--only <asset-id>` to regenerate one. Paper assets are protected from this command and use `python scripts/extract_pixel_exact_paper_figures.py --only <paper-id>`.

Copy only the needed groups into the deliverable; do not flatten the whole sheet into one image.

## Reconstruct an existing figure

1. Crop the exact target panel and keep it visible beside the editable render. If the source is a PDF, attempt direct source-operator extraction before manual drawing.
2. Separate structure from appearance. Record panels, reading order, containment, alignment, repeated components, connector topology, and exact object counts.
3. Transcribe labels exactly. Flag ambiguous text instead of inventing it.
4. For a semantic/manual reconstruction, recreate text as text, arrows as connectors, simple icons as primitives, plots from source data where available, and complex illustrations as separately replaceable assets. For pixel-exact extraction, retain source glyph outlines in the visible layer and text-as-text in `semantic-edit-layer`.
5. Maintain a third edge-overlay view: source edges in magenta, redraw edges in cyan, coincident edges in black.
6. Match in this order: crop/aspect → topology/count → geometry → typography → appearance → small detail. Fix the largest overlay separation after every pass.
7. Compare again at full view, repository-preview size, and final publication size.

Do not call an output editable when it is only a raster image embedded in SVG, PPTX, or draw.io. If a source PDF itself contains bitmap operators, preserve them only in the exact visible layer, assign stable IDs, count them in the manifest, and provide a separate semantic editing layer.

## Reproduce published figures and curves honestly

Read the original paper before reconstructing a published visual. Classify the result as `pixel-exact-dual-layer`, `faithful-redraw`, `semantic-redraw`, `formula-derived`, `data-recomputed`, `digitized`, or `illustrative-normalized`, and expose that class in the output metadata. Use `pixel-exact-dual-layer` only when the visible layer comes directly from cited PDF operators, the exact figure number and PDF hash are recorded, and source crop, pixel metrics, edge overlay, and hidden-layer isolation pass. Use `faithful-redraw` only for a manually rebuilt figure after the same review evidence has been inspected. Source crops are review evidence rather than reusable assets and retain the paper's rights.

For the pixel-exact route, loop in this order: source crop → operator extraction → tight SVG render → aspect/pixel metrics → edge overlay → crop or operator-trim correction. Do not stop while aspect error exceeds 1%, tolerant cross-renderer pixel match is below 80%, or removing the hidden semantic layer changes even one rendered pixel.

For lines, prefer author-released data or code, then a published formula. If neither is available, generate only a normalized qualitative trend and label it illustrative. Never present synthetic or digitized points as reported measurements. Use the classic examples and source records in `assets/gallery-manifest.json` as patterns.

## Refine without collateral damage

Translate each revision into an object-level patch such as `change connector:e3 route`, `replace label:t7`, or `recolor group:encoder`. Preserve stable IDs and untouched groups. Regenerate the full artifact only when the layout contract changes.

## Validate before delivery

Run:

```bash
python scripts/generate_gallery.py
python scripts/extract_pixel_exact_paper_figures.py
python scripts/calibrate_paper_figures.py
python scripts/validate_repo.py
```

For a paper redraw, additionally run the optional calibration harness described in `references/fidelity-protocol.md` and inspect every image under `assets/comparisons/` before delivery.

Then verify the actual deliverable:

- opens in its native editor without repair warnings;
- contains native semantic text and vector objects, or explicitly uses the pixel-exact dual-layer contract rather than a disguised bitmap;
- has no clipped labels, overlaps, broken connectors, or missing glyphs;
- preserves equations and scientific directionality;
- remains legible at final print size and in grayscale;
- records the source and license of every external asset;
- includes both the editable source and a rendered preview.

For a survey refresh, run `python scripts/sync_catalog.py`. For local installation after cloning, run `python scripts/install_skill.py --target codex`.
