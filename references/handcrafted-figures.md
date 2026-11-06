# Shared handcrafted figure production

Used by `/teaser` and `/pipeline`. The profile captures a dense, human-composed scientific figure: genuine results, dark ink, warm paper, concrete labels and restrained color. Explicit user or venue requirements override this profile.

## Style configuration

Start from [assets/styles/handcrafted-paper.json](../assets/styles/handcrafted-paper.json). Comic Sans MS is the default for this profile (the intended font when a user writes “Coic Sans MS”). Confirm the actual font is installed before rendering. Keep equations legible with editable notation or source-backed vector math; document any math-font exception. For Chinese labels use a declared compatible font rather than silently substituting glyphs.

Use ink `#252D32`, paper `#FFFDF8`, cream `#F1E9D9`. Accent roles: blue for conditions/frozen parameters, rust for adaptation/trainable parameters, teal for accepted evidence/feedback; gray for neutral support. Use at most a few roles per figure and include labels/icons so meaning survives grayscale. Color small functional objects, not every large panel. Keep photographs rich and unfiltered. Prefer ink-dense layouts over large empty pastel cards.

Handcrafted means small deliberate variations in outline and tabs. It does not mean random misalignment, excessive wobble or decorative arrows. Keep connector anchors deterministic. Native freeform paths may vary by about 1–2 canvas pixels at a 2400-pixel design width; scale that amount with the canvas. Keep fills aligned with outlines. Use mild corner masks on photographs, not heavy shadows or decorative gradients.

Use a figure canvas at the final aspect ratio, not an automatic 16:9 presentation slide. Choose font sizes at the final physical width (generally 7–10 pt for labels, larger for headers); a 30 px label on a 2400 px canvas is only 3.6 pt at four inches. Increase labels, reduce content or use full width instead of accepting unreadable scaling.

## Source preparation

Inspect real assets before selection. Prefer source files to screenshots when available. For a web gallery, inspect its actual records and final-result player; a page may contain unrelated videos, failed history or stale cached files. Do not assume an endpoint exists because its filename sounds plausible. Use authorized browser/API/file access and preserve source records. Never publish unpublished manuscript material, credentials, private media or temporary access URLs into the reusable skill repository.

`scripts/figure_media.py` consumes a local JSON manifest, validates case/attempt matching for paired examples, extracts declared timestamps with FFmpeg, and emits frame-level SHA256 provenance. It does not download files or decide which output is scientifically representative. See [assets/examples/result-media.json](../assets/examples/result-media.json) for the input contract. Paths are relative to the manifest. Use `unknown` for unknown source/status fields. A manifest marked `illustrative` is a test/layout fixture, never experimental evidence.

```bash
python scripts/figure_media.py check work/result-media.json
python scripts/figure_media.py extract work/result-media.json --out work/extracted
```

Inspect contact sheets and revise timestamps before final layout. Keep the raw media unchanged. Pair IDs mean assets represent the same world/case/attempt; reference-only assets can be listed separately with their actual scope.

## Editable authoring

Use the available native presentation tool, a suitable PPTX library or the app UI. If a presentation skill/runtime is available, follow its authoring and validation contract. The optional [scripts/handcrafted.mjs](../scripts/handcrafted.mjs) helper provides native text, irregular boxes, line/arrow paths and independent pictures for an existing `@oai/artifact-tool` runtime; it is not a bundled runtime or a prompt-to-PPTX compiler. Read its small example before importing. `composeTeaser({title, groups, mosaic})` directly arranges the compact photographic recipe; each group contains a short `label` and chronological `frames` file paths. For example:

```javascript
import { composeTeaser } from './scripts/handcrafted.mjs';
const figure = await composeTeaser({
  title: 'Project name',
  groups: [
    { label: 'Object interaction', frames: ['/data/a0.png', '/data/a1.png', '/data/a2.png'] },
    { label: 'Viewpoint control', frames: ['/data/b0.png', '/data/b1.png', '/data/b2.png'] }
  ]
});
await figure.save('/work/teaser.pptx', { previewPath: '/work/teaser.png' });
```

Provide genuine inspected frames and provenance separately. Change columns/aspect/style to suit the results; inspect crops and title fit before delivery. In another environment reproduce the same primitives with the available native API. Do not install an unrelated model service just to follow this style.

Keep editable text and geometry separate from replaceable photographs. Store stable names/IDs and source notes. Retain source code, layout parameters and object-level edits privately so revisions can move an edge endpoint or replace a label without rebuilding the scientific content. Do not submit a rasterized entire figure embedded in a PPTX as “editable”.

If the host cannot produce/render PPTX, state that limitation and deliver a useful editable SVG/layout/source plan. Do not rename another format to `.pptx` or claim an untested PDF exists. This skill's installed commands guide an authoring agent; they do not supply a model, fonts, Office or PDF renderer.

## Export and inspect

1. Save a candidate PPTX and render every figure to PNG/PDF. Inspect the actual export at full view and final paper width. Fix clipped labels, wrong crops, weak hierarchy, crossings and dangling arrowheads.
2. Reopen the candidate in its native editor when available. Never claim an editor check without actually opening and inspecting it.
3. Run `python scripts/audit_figure_pptx.py figure.pptx --font "Comic Sans MS"` to inventory native shapes/pictures/text and declared typefaces. This is a structural check, not proof of visual or scientific correctness. Slide-sized pictures require manual review; a dense photographic teaser is legitimate if each tile and label remains independent.
4. Audit the rendered PDF for actual font embedding/substitution. LibreOffice on macOS may ignore system fonts unless Fontconfig includes the installed font directories. If using headless conversion, supply a task-local `FONTCONFIG_FILE` where needed and inspect `pdffonts` (or PDF font descriptors); PPTX font declarations alone do not prove the PDF used them. Never distribute font files without appropriate rights.
5. Check arrows and common origins at high zoom, then legibility at publication size and in grayscale. Automated geometry checks do not replace this pass. Recheck the exported PDF after fixes, not just the in-memory render.

## Delivery and captions

By default provide separate `figure1-teaser` and/or `figure2-pipeline` PPTX, PDF and PNG files, an English caption and LaTeX figure snippet, plus private source/frame manifest with known URLs, case/attempt/time/hash. Respect existing names and numbering. State crop and evidence scope; do not turn selected outputs into held-out evaluation or claim training admission without records. Keep caption prose outside figure artwork unless requested.

When requested, prepare an Overleaf patch with only the new figures and required caption/include changes. Preserve original labels, paths, body text and bibliography. Keep a backup or patch rather than overwriting unrelated files. Compile the existing multi-file project with its appropriate toolchain if available and inspect the actual figure pages; otherwise clearly mark compilation unverified. Include a full source bundle only when requested. Do not silently change the method to resolve a source conflict.

A concise delivery note should explain the visual hierarchy, which real samples support each claim, how the arrows map to the method, any source discrepancy and what was actually verified. Keep scripts, caches, lock files and intermediate revisions out of the Overleaf patch.
