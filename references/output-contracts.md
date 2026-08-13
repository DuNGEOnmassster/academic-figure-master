# Output contracts

## SVG

- Use a `viewBox`; avoid fixed pixel-only sizing.
- Use named groups and stable IDs for semantic components.
- Keep labels as `<text>` unless font portability requires outlined duplicates.
- Prefer simple paths, shapes, gradients, and markers; avoid filters that render inconsistently.
- Do not embed a full-canvas raster image. Isolated raster crops must be explicit and documented.
- Validate XML and inspect the SVG in at least one browser or vector editor.

## draw.io

- Use native `mxCell` vertices and edges for text, boxes, arrows, and grouping.
- Keep connector source/target references intact so moving a node moves its edges.
- Store scientific labels as editable cell values, not baked into images.
- Use embedded SVG only for complex standalone illustrations; keep attribution in metadata or an adjacent note.
- Export an SVG or PDF preview and inspect it for clipping and font substitutions.

## PowerPoint

- Use native shapes, connectors, text boxes, groups, and editable charts wherever possible.
- Keep equations as editable math when the available toolchain supports it; otherwise provide the source equation beside a vector rendering.
- Do not use a slide-sized screenshot as the figure.
- Set the slide or figure canvas to the requested final aspect ratio before layout.
- Verify by reopening the `.pptx` and rendering every slide to an image or PDF.

## Cross-format quality gates

1. Semantic fidelity: all entities, relations, directions, and quantities match the source.
2. Structural editability: a reviewer can select and change a single label, node, or connector without reconstruction.
3. Visual hierarchy: the primary claim is visible before secondary detail.
4. Typography: consistent family, hierarchy, math notation, and final-size legibility.
5. Provenance: every non-original asset has a source, license, and attribution requirement.
