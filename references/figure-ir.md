# Figure intermediate representation

Use a small semantic scene graph as the source of truth when a figure is multi-panel, reconstructed from a reference, or likely to receive revisions.

## Required fields

- `canvas`: width, height, unit, background, and intended final size.
- `style`: font family, type scale, stroke scale, palette, corner radius, and arrow conventions.
- `panels`: stable ID, title or panel letter, bounds, and reading order.
- `objects`: stable ID, semantic role, panel, geometry, style token, and optional asset source.
- `connectors`: stable ID, source/target ports, direction, route, label, and scientific meaning.
- `labels`: stable ID, exact text or math, anchor, alignment, and minimum size.
- `provenance`: input files, external assets, licenses, and unresolved uncertainties.

## Identity rules

- Never reuse an ID for a different scientific object.
- Keep text separate from decorative geometry.
- Give repeated objects a shared `component` plus unique instance IDs.
- Represent an arrow's scientific meaning independently from its visual route.
- Mark any raster fallback with `editable: false` and a replacement note.

## Revision format

Prefer explicit patches over broad prompts:

```json
{
  "operations": [
    {"op": "replace_text", "id": "label-score", "value": "score $s_\\theta(x,t)$"},
    {"op": "move", "id": "module-denoiser", "dx": 18, "dy": 0},
    {"op": "reroute", "id": "edge-reverse-sde", "route": "orthogonal"}
  ]
}
```

The editable file remains authoritative. A preview is an evaluation artifact, not the source.
