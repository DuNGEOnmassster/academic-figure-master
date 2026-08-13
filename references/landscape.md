# Academic Figure Master landscape

Snapshot: 2026-08-13. Dynamic GitHub metadata and stars live in `catalog-snapshot.json`; refresh them with `python scripts/sync_catalog.py`.

## Executive conclusion

The opportunity is real, but the moat is not another text-to-image prompt wrapper. The strongest current image models produce attractive drafts, while researchers need a **semantic, editable, round-trippable figure** whose text, arrows, panels, equations, and scientific relationships survive repeated local edits.

The market currently splits into four imperfect lanes:

1. raster image generation with strong aesthetics but weak structure;
2. SVG foundation models that emit paths/code but do not understand paper-level figure semantics well enough;
3. scientific illustration systems that understand paper content but often use raster generation or segmentation as an intermediate;
4. professional vector editors with excellent control and a steep interaction cost.

`academic-figure-master` should sit between lanes 3 and 4: an agent-native, lightweight compiler from research intent or a reference image into a stable semantic scene, then native SVG/draw.io/PPTX. That is the “Jianying/CapCut versus Premiere” differentiation: fewer controls, better defaults, and deterministic local edits rather than a weaker copy of Illustrator.

## What counts as editable

An `.svg`, `.pptx`, or `.drawio` extension is not sufficient. Score a system on:

- **semantic objects:** text, equations, nodes, arrows, plots, and panels are distinct;
- **stable identity:** a component can be patched without regenerating neighbors;
- **native text:** labels are editable and searchable, not pixels or path soup;
- **connector topology:** edges stay attached when nodes move;
- **group/layer quality:** components are logically grouped rather than flattened;
- **node economy:** curves use a reasonable number of anchors;
- **round trip:** the artifact reopens in PowerPoint, draw.io, or a vector editor without repair;
- **visual fidelity:** a reconstruction matches layout, typography, color, and small geometry;
- **scientific fidelity:** direction, notation, quantities, and causal claims remain correct;
- **provenance:** every external asset has a license and attribution trail.

This rubric exposes why many “image to PPT/SVG” demos disappoint: they recover appearance but not the object model needed for revision.

## 1. Image and vector generation models

| System | Native output and editability | Availability | Relevance to this skill |
|---|---|---|---|
| [GPT Image 2](https://developers.openai.com/api/docs/guides/image-generation) | High-quality raster generation and multi-turn edits. Official output formats are PNG, JPEG, and WebP, not SVG; OpenAI also documents remaining limits in exact text placement and layout-sensitive composition. | Hosted API | Use for art direction, reference drafts, complex icon ideation, and localized raster edits. Never treat it as the final structured figure. |
| [Adobe Illustrator Text to Vector / Concept to Vector](https://helpx.adobe.com/illustrator/desktop/use/generative-ai/generate-scenes-subjects-and-icons.html) | Native editable vectors; scene/subject/icon modes, style references, generated-object layers, editable Latin text, and raster-to-vector generation. | Proprietary desktop product | Quality/control baseline and the “professional lane” we should not imitate feature-for-feature. |
| [Recraft V4 Vector](https://www.recraft.ai/ai-models/recraft) | Direct editable SVG from prompts; vector model variants and a hosted [raster vectorization endpoint](https://www.recraft.ai/docs/api-reference/endpoints). | Commercial studio/API/MCP | Strong optional model adapter for generated illustrations and isolated vector assets. Audit grouping, text, and node economy on scientific diagrams. |
| [StarVector](https://github.com/joanrod/star-vector) | Autoregressive SVG code from images or text using a VLM; public 1B/8B models, SVG datasets, and benchmarks are linked from the [official project](https://starvector.github.io/). | Open code and weights | Best practical open baseline for image-to-SVG experiments. Good at semantic primitives; still needs scene cleanup, grouping, typography recovery, and domain reasoning. |
| [OmniSVG](https://github.com/OmniSVG/OmniSVG) | End-to-end multimodal SVG generation with released inference models, datasets, benchmark, and separate training code. | Open code/weights | Strong adapter candidate for more complex SVGs. Evaluate on paper diagrams rather than icons/anime examples. |
| [InternSVG](https://hmwang2002.github.io/release/internsvg/) | Unified multimodal model for SVG understanding, editing, generation, chemical structures, and animation; adds SAgoge/SArena data and evaluation. | Open official repository/weights | Especially relevant because editing and scientific structure are first-class tasks, not only generation. |
| [LLM4SVG](https://github.com/ximinng/LLM4SVG) | LLM training and representations for SVG understanding and generation. | Open research implementation | Useful representation/training reference; not a complete figure authoring product. |
| [Chat2SVG](https://github.com/kingnobro/Chat2SVG) | Text-to-SVG pipeline combining LLM reasoning and image diffusion priors. | Open research code | Useful for staged generation and refinement ideas, but less direct for reference-image reconstruction. |
| [NeuralSVG](https://arxiv.org/abs/2501.03992) | Text-to-vector generation with an implicit representation and attention to layered SVGs. | Research code | Layering is valuable; text-only scope limits direct reconstruction use. |
| [SVGDreamer++](https://github.com/ximinng/SVGDreamerV2) | Diffusion-guided editable vector generation optimized for diversity and shape control. | Open research code | Potential refinement backend for illustrations; optimization cost and semantic grouping need evaluation. |
| [VectorArk](https://vectorark.github.io/) | CVPR 2026 VLM vectorizer using rounded polygon representations, explicitly trained for real-world and AI-generated raster inputs. | Paper/project page; code marked coming soon at snapshot | High-priority watch item because its objective targets the “node soup” and synthetic-benchmark gap directly. |
| [DuetSVG](https://openaccess.thecvf.com/content/CVPR2026/papers/Zhang_DuetSVG_Unified_Multimodal_SVG_Generation_with_Internal_Visual_Guidance_CVPR_2026_paper.pdf) | Unified text-to-image, text-to-SVG, and image-to-SVG model with internal visual guidance. | Paper/project artifacts | Watch as a direct-generation alternative; verify code and weights before planning an adapter. |
| [Chart2SVG](https://www.yunhaiwang.net/vis2026/Chart2SVG/index.html) | Raster chart to semantically structured SVG with chart-specific tokens and a Chart Structure Graph. | VIS 2026 project/paper | Important specialized path for recovering charts without hallucinating data semantics. |
| [VTracer](https://github.com/visioncortex/vtracer) | Fast local raster tracing into SVG paths. | Open lightweight CLI/library | Excellent fallback for a single isolated icon or silhouette; it cannot recover labels, groups, or scientific relationships. |
| [diffvg](https://github.com/BachiLi/diffvg) | Differentiable rasterization and optimization of vector primitives. | Open library | A low-level refinement engine, not a semantic generator. Useful for fitting paths after decomposition. |

### Model takeaway

No single model should own the final artifact. A robust workflow needs a router:

- image model for composition/style exploration;
- VLM/SVG model for component proposals or isolated vectorization;
- OCR/math/parser for exact labels and equations;
- deterministic scene compiler for native editable output;
- rendered-difference and structural checks for QA.

## 2. Automatic scientific figure systems

| System | Core approach | Editable surface | Product lesson |
|---|---|---|---|
| [PaperBanana](https://arxiv.org/abs/2601.23265) | Multi-agent retrieval, planning, styling, rendering, and critique; introduces 292-case PaperBananaBench for method diagrams and extends to plots. | The paper's main contribution is generation and evaluation, not a native authoring IR. | Strong evidence that planning/style/critic roles matter. Do not inherit a raster-first final format. The popular [community implementation](https://github.com/llmsresearch/paperbanana) is unofficial. |
| [AutoFigure-Edit](https://arxiv.org/abs/2603.06674) | Long-form scientific understanding, reference-guided styling, initial image generation, component detection/segmentation, SVG templating, assembly, and browser editing. | Editable SVG and embedded editor. | Closest open research system to this idea. Audit whether each imported illustration is a path-native vector or an isolated raster crop inside SVG; component editability and true vectorization are different. |
| [Crafter / CraftEditor](https://arxiv.org/abs/2605.30611) | Multi-agent harness for diverse inputs and figure types; CraftEditor converts outputs to editable SVG; evaluated on PaperBananaBench and CraftBench. | Editable SVG with a dedicated reconstruction harness. | Strong architectural evidence for treating reconstruction as its own agent loop rather than a post-processing button. |
| [GenGA](https://arxiv.org/abs/2608.05478) | Direct, hierarchical vector generation for graphical abstracts; proposes Structural Independence Coefficient to measure local-edit propagation. | Hierarchical vectors intended for existing drawing tools. | The most directly aligned new research concept: editability should be measured structurally, not inferred from the file extension. Very new; implementation maturity is unknown. |
| [AutoFigure](https://github.com/ResearAI/AutoFigure) | Paper/PDF to methodology extraction, figure generation, enhancement, and FigureBench. | SVG-oriented outputs and web workflow. | Useful long-context and benchmark source; the newer AutoFigure-Edit is the more relevant authoring baseline. |
| [Paper2Any](https://github.com/OpenDCAI/Paper2Any) | Paper/text/image to figures, slides, posters, and diagrams. | Advertises editable PPTX/SVG and image-to-draw.io paths. | Closest open product competitor on format breadth. Test actual decomposition quality, not feature labels. |
| [Edit-Banana](https://github.com/BIT-DataLab/Edit-Banana) | SAM-based segmentation, OCR, formula recognition, and spatial assembly from a static image. | Native draw.io XML with independently selectable components. | Directly validates the reconstruction route. It is GPU/heavy rather than lightweight, and its README license badge conflicts with GitHub's current AGPL-3.0 detection; resolve before code reuse. |
| [BioRender AI](https://www.biorender.com/ai-tools) | Scientific icon/template library plus prompt and reference-driven generation. | Flowchart/protocol/timeline generators use editable BioRender components; the official FAQ says some custom icon/figure generators still produce flat PNGs. | High domain accuracy and UX baseline; proprietary assets, publication licensing, and mixed editability leave room for an open, file-native lane. |
| [Mind the Graph](https://platform.mindthegraph.com/) | Large scientific illustration and template library for abstracts, posters, slides, and infographics. | In-product element editing and export. | Confirms demand for a science-specific asset library; not an agent-native semantic compiler. |
| [Napkin AI](https://www.napkin.ai/) | Text-to-business visuals with fast style/layout iteration. | Exports PPT, SVG, PDF, and PNG. | Excellent simplicity benchmark, but scientific semantics, equations, and paper-figure reconstruction are not its center. |

Many 2026 “PaperBanana” commercial sites make overlapping claims about SVG/PPT/XML without transparent implementation or evaluation. Treat them as demand signals only; prefer the original paper, official repositories, and inspectable outputs as evidence.

## 3. Existing skills and editable-diagram repos

The daily catalog tracks this fast-moving group. The most relevant current patterns are:

- [Agents365 drawio-skill](https://github.com/Agents365-ai/drawio-skill): broad draw.io generation, image-to-editable-diagram, exports, and visual checks;
- [academic-figure-skills](https://github.com/Azhi-ss/academic-figure-skills): figure planning, palette selection, JSON specs, benchmarks, and one-command skill distribution;
- [codex-visio-paper-figure-skill](https://github.com/pengjunchi0/codex-visio-paper-figure-skill): research figure reconstruction into Visio/editable formats;
- [codex-paper-figure-skill](https://github.com/pengqianhan/codex-paper-figure-skill): explicitly uses image generation as a visual reference, then rebuilds native draw.io;
- [drawio-diagram-builder-skill](https://github.com/Will-hxw/drawio-diagram-builder-skill): research-style draw.io and screenshot-driven iteration;
- [drawio-reconstruction-skill](https://github.com/sxy1499894281/drawio-reconstruction-skill): narrow image reconstruction workflow;
- [nature-skills](https://github.com/Yuan1z0825/nature-skills) and [scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills): broad distribution and scientific workflow precedents;
- [next-ai-draw-io](https://github.com/DayuanJiang/next-ai-draw-io): natural-language editing inside a draw.io-based product/MCP surface.

These repos prove that the format plumbing is available. The remaining differentiation is a science-specific IR, good default aesthetics, license-aware components, stable local edits, and a quality harness that evaluates both the rendered image and the underlying object graph.

## 4. Scientific asset libraries

| Source | Scope and format | License handling | Recommended use |
|---|---|---|---|
| [NIH BioArt Source](https://bioart.niaid.nih.gov/) | 2,000+ professionally illustrated science/medical vectors, icons, brushes, templates; NIAID lists EPS, AI, PNG, and SVG downloads. | Entries may be public domain or attribution licenses; the [FAQ](https://bioart.niaid.nih.gov/faqs) describes per-entry citation. | Highest-priority biomedical source. Store entry URL, creator/collection, license, and citation with every import. |
| [Bioicons](https://bioicons.com/) | Searchable biology, chemistry, lab, ML, and scientific-graph SVGs. | Per-icon mix including CC0, CC BY, CC BY-SA, MIT, and BSD. The repository code's license does not override each icon's license. | Strong machine-searchable source if the adapter preserves individual metadata. |
| [SciDraw](https://scidraw.io/howtoupload/) | Community scientific drawings intended for reuse and modification. | Uploads are CC BY 4.0; attribution is required. | Good source for domain illustrations when a citation line is acceptable. |
| [Servier Medical Art](https://smart.servier.com/) | Medical/life-science illustration kits; current site offers PPTX/PNG rather than SVG. | [CC BY 4.0](https://smart.servier.com/terms-of-use/) with credit and modification notice. | Useful PowerPoint-native biomedical component source; do not scrape automatically because the terms prohibit bots/scrapers. |
| [ML Visuals](https://github.com/dair-ai/ml-visuals) | 100+ editable ML figures and basic components maintained in Google Slides. | Repository is MIT; author credit is requested in slide notes. | Best seed source for familiar ML architecture components and layout patterns. |
| [PhyloPic](https://www.phylopic.org/) | Organism silhouettes with API/community wrappers. | License varies by image; attribution may be required. | Useful for ecology/evolution panels only with per-asset provenance. |
| [Tabler Icons](https://github.com/tabler/tabler-icons) / [Lucide](https://github.com/lucide-icons/lucide) | Consistent general SVG icon systems. | Permissive project licenses; verify trademark-sensitive symbols. | Use only when a scientific icon is not necessary. Their consistent strokes are better than mixing arbitrary web icons. |
| [OpenMoji](https://github.com/hfg-gmuend/openmoji) | Broad pictogram set. | CC BY-SA; derivative/distribution implications require care. | Reference or presentation fallback, not the default for journal figures. |
| [Rough.js](https://github.com/rough-stuff/rough) / [Excalidraw](https://github.com/excalidraw/excalidraw) | Hand-drawn vector rendering and interaction patterns. | Open-source code; generated original geometry is safest. | Generate an original hand-drawn arrow grammar rather than copying a third-party illustration style. |

### Asset policy

Do not vendor a large mixed-license library into this repository. Keep original generic primitives locally, fetch scientific assets on demand, and write a sidecar provenance record containing:

`source_url`, `asset_id`, `creator`, `license`, `retrieved_at`, `modified`, `attribution_text`.

## 5. Recommended product architecture

```text
paper text / data / reference image
                │
        semantic decomposition
                │
      figure IR with stable object IDs
       ┌────────┼─────────┐
  asset router  │    layout/style planner
       └────────┼─────────┘
                │
      native format compiler
       SVG / draw.io / PPTX
                │
   structural QA + rendered visual QA
                │
       object-level revision patch
```

### Core principles

1. **IR before pixels.** Preserve scientific objects and relations before rendering.
2. **Image models are optional collaborators.** They can propose composition or complex art, but exact labels and final structure are rebuilt deterministically.
3. **One canonical scene, multiple compilers.** SVG, draw.io, and PPTX should share object IDs and style tokens.
4. **Local editing is an invariant.** A requested label or connector change should not perturb unrelated groups.
5. **Assets are data with licenses.** Search and attribution are part of generation, not cleanup.
6. **Quality is dual.** Inspect both pixels and structure; a beautiful flattened image and an ugly editable file both fail.

## 6. Starter component taxonomy

The local `assets/primitives/` begins with the highest-frequency computational research elements:

- manifold surfaces, coordinate grids, geodesics, and sample points;
- deterministic ODE and stochastic SDE trajectories, drift, diffusion, and uncertainty bands;
- forward/reverse diffusion sequences and score arrows;
- hand-drawn emphasis arrows, loops, braces, and bidirectional relations;
- tensor stacks, feature maps, embeddings, and dimension annotations;
- encoder/decoder/attention/merge modules and typed ports.

Next useful families should be added only with a real example and an editability test: distributions/energy landscapes, graphs and message passing, optimization paths, causal diagrams, PDE fields, database/retrieval pipelines, robotics/world models, microscopy/lab protocols, and biological mechanisms.

## 7. Build sequence

### Phase 0 — this repository

- installable skill contract;
- evidence-backed landscape and daily catalog sync;
- original editable starter primitives;
- reconstruction and output-format rules;
- repository and asset validation.

### Phase 1 — reliable native authoring

- formal JSON schema for figure IR;
- SVG compiler plus draw.io and PPTX compilers;
- object-ID-preserving patch engine;
- preview renderer and overlap/clipping checks;
- component search with license sidecars.

### Phase 2 — reference reconstruction

- OCR/math transcription with uncertainty;
- panel, object, connector, and group detection;
- chart-specific recovery through data/structure extraction;
- VLM/vector-model adapters for isolated complex regions;
- visual-difference loop and structural independence score.

### Phase 3 — product surface

- simple canvas with prompt-to-object patches;
- “lock everything except selection” edits;
- synchronized PPTX/draw.io/SVG export;
- per-venue styles and accessibility checks;
- benchmark suite drawn from real revision requests, not only one-shot generation.

## Sources and update policy

Primary papers, official project pages, official product documentation, and repositories are used whenever available. GitHub stars, activity, license detection, and newly discovered repositories are volatile and therefore excluded from static prose; the scheduled workflow refreshes `catalog-snapshot.json` and `catalog-latest.md` every day. Discovery is not endorsement: new candidates must pass output inspection, license review, and a realistic edit task before promotion into the curated list.
