---
name: academic-figure-master
description: Create, reconstruct, and refine publication-ready academic figures as genuinely editable SVG, draw.io, or PowerPoint artifacts. Use for paper method diagrams, model architectures, SDE/ODE or manifold illustrations, graphical abstracts, reference-image component reconstruction, and local element-level edits where raster image generation is not an acceptable final deliverable.
---

# Academic Figure Master

Create a semantic figure first and compile it into native editable objects. Treat image generators as optional visual ideation tools, never as the source of truth for labels, geometry, or scientific relationships.

## Route the request

Choose one route before drawing:

- **Text or paper → figure:** extract the claim, entities, relations, stages, equations, and required labels.
- **Existing image → editable reconstruction:** inventory every visible component, connector, label, group, alignment rule, and repeated style before rebuilding it.
- **Existing editable figure → targeted edit:** preserve unaffected object IDs, geometry, typography, and grouping; patch only the requested components.
- **Data → plot:** use a plotting library for data marks, then combine the exported vector plot with native annotations. Never redraw measured data by eye.

Read [references/output-contracts.md](references/output-contracts.md) for format-specific rules. Read [references/figure-ir.md](references/figure-ir.md) when a figure has more than one panel or will need iterative edits. Consult [references/landscape.md](references/landscape.md) only when selecting an external model, tool, or asset source.

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

Reuse original primitives from `assets/primitives/` when applicable. Their groups and IDs are deliberately editable:

- `manifold-grid.svg`: curved manifold, grid, samples, and geodesic;
- `sde-ode-trajectories.svg`: deterministic and stochastic paths;
- `hand-drawn-arrows.svg`: loose, loop, emphasis, and bidirectional arrows;
- `diffusion-process.svg`: forward noising and reverse denoising sequence;
- `tensor-stack.svg`: matrices, feature stacks, and dimension labels;
- `neural-modules.svg`: encoder, latent, decoder, attention, and merge blocks.

Copy only the needed groups into the deliverable; do not flatten the whole sheet into one image.

## Reconstruct an existing figure

1. Separate structure from appearance. Record panels, reading order, containment, alignment, repeated components, and connector topology.
2. Transcribe labels exactly. Flag ambiguous text instead of inventing it.
3. Recreate text as text, arrows as connectors, simple icons as primitives, plots from source data where available, and complex illustrations as separately replaceable assets.
4. Match the reference in passes: layout → typography → shape geometry → connector routing → color → small detail.
5. Compare a rendered preview with the reference at full view and at final publication size. Correct the largest structural mismatch first.

Do not call an output editable when it is a single raster image embedded in SVG, PPTX, or draw.io. If an unavoidable crop remains raster, isolate and label it in the scene manifest.

## Refine without collateral damage

Translate each revision into an object-level patch such as `change connector:e3 route`, `replace label:t7`, or `recolor group:encoder`. Preserve stable IDs and untouched groups. Regenerate the full artifact only when the layout contract changes.

## Validate before delivery

Run:

```bash
python scripts/validate_repo.py
```

Then verify the actual deliverable:

- opens in its native editor without repair warnings;
- contains editable text and vector objects rather than a disguised bitmap;
- has no clipped labels, overlaps, broken connectors, or missing glyphs;
- preserves equations and scientific directionality;
- remains legible at final print size and in grayscale;
- records the source and license of every external asset;
- includes both the editable source and a rendered preview.

For a survey refresh, run `python scripts/sync_catalog.py`. For local installation after cloning, run `python scripts/install_skill.py --target codex`.
