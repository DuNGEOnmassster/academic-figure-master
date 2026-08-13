# Academic Figure Master

A lightweight Codex/Claude skill for publication-ready academic figures that stay **genuinely editable** in SVG, draw.io, or PowerPoint. The repository bridges one-shot image generation and heavyweight manual design: fast enough for daily research, structured enough for precise object-level revision.

![assets](https://img.shields.io/badge/editable_SVG_assets-35-3972d5) ![paper redraws](https://img.shields.io/badge/classic_paper_redraws-11-7354cf) ![curves](https://img.shields.io/badge/reproducible_curves-6-38a479) ![license](https://img.shields.io/badge/original_assets-MIT-d3a23f)

The current version includes:

- 18 reusable academic-figure primitive sheets;
- 11 source-calibrated, editable redraws of exact classic-paper figures;
- 6 reproducible curve templates with explicit fidelity labels;
- a machine-readable provenance and reproduction manifest;
- a surveyed catalog of vector models, scientific-figure systems, skills, editors, and asset libraries;
- daily GitHub metadata, stars, activity, license, and discovery refreshes; and
- dependency-free core generation, validation, synchronization, and installation scripts, plus an optional source/redraw/edge-overlay calibration harness.

## Install and invoke

After cloning the private repository:

```bash
python scripts/install_skill.py --target codex
```

The default installation is a symbolic link, so repository updates are immediately available to Codex. Use `--mode copy` for an isolated copy, `--target claude` for Claude, or `--target path --path /absolute/destination` for a custom directory.

Example request:

```text
Use $academic-figure-master to reconstruct this method figure as editable SVG.
Keep every label as text and preserve stable object IDs for later revisions.
Reuse the residual block and uncertainty-band assets where appropriate.
```

## Reusable academic primitives

Every sheet below is native SVG: text stays text, shapes stay shapes, and reusable parts have named groups. Click a preview to open the editable source.

<table>
<tr>
<td width="33%"><a href="assets/primitives/manifold-grid.svg"><img src="assets/primitives/manifold-grid.svg" alt="Editable manifold grid"></a><br><b>Manifold grid</b><br><sub>surface · coordinates · geodesic · tangent basis</sub></td>
<td width="33%"><a href="assets/primitives/sde-ode-trajectories.svg"><img src="assets/primitives/sde-ode-trajectories.svg" alt="Editable SDE and ODE trajectories"></a><br><b>SDE / ODE trajectories</b><br><sub>drift · sample paths · uncertainty</sub></td>
<td width="33%"><a href="assets/primitives/hand-drawn-arrows.svg"><img src="assets/primitives/hand-drawn-arrows.svg" alt="Editable hand-drawn arrows"></a><br><b>Hand-drawn arrows</b><br><sub>loose · emphasis · feedback · bidirectional</sub></td>
</tr>
<tr>
<td><a href="assets/primitives/diffusion-process.svg"><img src="assets/primitives/diffusion-process.svg" alt="Editable diffusion process"></a><br><b>Diffusion process</b><br><sub>forward SDE · reverse flow · score network</sub></td>
<td><a href="assets/primitives/tensor-stack.svg"><img src="assets/primitives/tensor-stack.svg" alt="Editable tensor stack"></a><br><b>Tensor stack</b><br><sub>matrix · feature maps · token sequence</sub></td>
<td><a href="assets/primitives/neural-modules.svg"><img src="assets/primitives/neural-modules.svg" alt="Editable neural modules"></a><br><b>Neural modules</b><br><sub>encoder · attention · latent · decoder · residual</sub></td>
</tr>
<tr>
<td><a href="assets/primitives/attention-heads.svg"><img src="assets/primitives/attention-heads.svg" alt="Editable multi-head attention"></a><br><b>Multi-head attention</b><br><sub>heads · softmax · value projection · concat</sub></td>
<td><a href="assets/primitives/convolution-pyramid.svg"><img src="assets/primitives/convolution-pyramid.svg" alt="Editable convolution pyramid"></a><br><b>Convolution pyramid</b><br><sub>spatial compression · channel expansion</sub></td>
<td><a href="assets/primitives/graph-message-passing.svg"><img src="assets/primitives/graph-message-passing.svg" alt="Editable graph message passing"></a><br><b>Graph message passing</b><br><sub>neighborhood · aggregate · update</sub></td>
</tr>
<tr>
<td><a href="assets/primitives/causal-dag.svg"><img src="assets/primitives/causal-dag.svg" alt="Editable causal DAG"></a><br><b>Causal DAG</b><br><sub>confounding · mediation · intervention</sub></td>
<td><a href="assets/primitives/optimization-landscape.svg"><img src="assets/primitives/optimization-landscape.svg" alt="Editable optimization landscape"></a><br><b>Optimization landscape</b><br><sub>contours · iterates · local minimum</sub></td>
<td><a href="assets/primitives/uncertainty-bands.svg"><img src="assets/primitives/uncertainty-bands.svg" alt="Editable uncertainty bands"></a><br><b>Predictive uncertainty</b><br><sub>mean · confidence band · observations</sub></td>
</tr>
<tr>
<td><a href="assets/primitives/dataset-pipeline.svg"><img src="assets/primitives/dataset-pipeline.svg" alt="Editable dataset pipeline"></a><br><b>Dataset pipeline</b><br><sub>validate · transform · split · version</sub></td>
<td><a href="assets/primitives/training-loop.svg"><img src="assets/primitives/training-loop.svg" alt="Editable training loop"></a><br><b>Training loop</b><br><sub>forward · loss · gradient · update · evaluate</sub></td>
<td><a href="assets/primitives/ensemble-voting.svg"><img src="assets/primitives/ensemble-voting.svg" alt="Editable model ensemble"></a><br><b>Model ensemble</b><br><sub>parallel models · aggregate · uncertainty</sub></td>
</tr>
<tr>
<td><a href="assets/primitives/bayesian-inference.svg"><img src="assets/primitives/bayesian-inference.svg" alt="Editable Bayesian inference"></a><br><b>Bayesian inference</b><br><sub>prior · likelihood · posterior · predictive</sub></td>
<td><a href="assets/primitives/multimodal-fusion.svg"><img src="assets/primitives/multimodal-fusion.svg" alt="Editable multimodal fusion"></a><br><b>Multimodal fusion</b><br><sub>image · text · audio · cross-attention</sub></td>
<td><a href="assets/primitives/ablation-matrix.svg"><img src="assets/primitives/ablation-matrix.svg" alt="Editable ablation matrix"></a><br><b>Ablation matrix</b><br><sub>variants · components · metric deltas</sub></td>
</tr>
</table>

## Source-calibrated classic-paper redraws

Every paper redraw now uses the exact cited Figure rather than a modern concept diagram. Each review plate shows the source crop, editable SVG render, and edge overlay side by side. Magenta is the paper source, cyan is the redraw, and black is overlap. Click a plate to open its editable SVG.

The original crop is included only as low-resolution review evidence in this private repository; the paper retains its rights. Deliverable SVGs contain no raster image. Where the source uses a photograph or face thumbnail, the SVG discloses and uses an editable vector substitute.

<a href="assets/paper-redraws/lenet-5.svg"><img src="assets/comparisons/lenet-5.png" alt="LeNet-5 Figure 2 source, editable redraw, and edge overlay"></a>

LeCun et al. (1998), Figure 2 · [paper](https://leon.bottou.org/publications/pdf/ieee-1998.pdf)

<a href="assets/paper-redraws/alexnet.svg"><img src="assets/comparisons/alexnet.png" alt="AlexNet Figure 2 source, editable redraw, and edge overlay"></a>

Krizhevsky et al. (2012), Figure 2 · [paper](https://papers.nips.cc/paper_files/paper/2012/file/c399862d3b9d6b76c8436e924a68c45b-Paper.pdf)

<a href="assets/paper-redraws/vae.svg"><img src="assets/comparisons/vae.png" alt="VAE Figure 1 source, editable redraw, and edge overlay"></a>

Kingma & Welling (2013), Figure 1 · [paper](https://arxiv.org/abs/1312.6114)

<a href="assets/paper-redraws/gan.svg"><img src="assets/comparisons/gan.png" alt="GAN Figure 1 source, editable redraw, and edge overlay"></a>

Goodfellow et al. (2014), Figure 1 · [paper](https://arxiv.org/abs/1406.2661)

<a href="assets/paper-redraws/resnet-block.svg"><img src="assets/comparisons/resnet-block.png" alt="ResNet Figure 2 source, editable redraw, and edge overlay"></a>

He et al. (2015), Figure 2 · [paper](https://arxiv.org/abs/1512.03385)

<a href="assets/paper-redraws/unet.svg"><img src="assets/comparisons/unet.png" alt="U-Net Figure 1 source, editable redraw, and edge overlay"></a>

Ronneberger et al. (2015), Figure 1 · [paper](https://arxiv.org/abs/1505.04597)

<a href="assets/paper-redraws/transformer.svg"><img src="assets/comparisons/transformer.png" alt="Transformer Figure 1 source, editable redraw, and edge overlay"></a>

Vaswani et al. (2017), Figure 1 · [paper](https://arxiv.org/abs/1706.03762)

<a href="assets/paper-redraws/neural-ode.svg"><img src="assets/comparisons/neural-ode.png" alt="Neural ODE Figure 1 source, editable redraw, and edge overlay"></a>

Chen et al. (2018), Figure 1 · [paper](https://arxiv.org/abs/1806.07366)

<a href="assets/paper-redraws/simclr.svg"><img src="assets/comparisons/simclr.png" alt="SimCLR Figure 2 source, editable redraw, and edge overlay"></a>

Chen et al. (2020), Figure 2 · [paper](https://arxiv.org/abs/2002.05709)

<a href="assets/paper-redraws/ddpm.svg"><img src="assets/comparisons/ddpm.png" alt="DDPM Figure 2 source, editable redraw, and edge overlay"></a>

Ho et al. (2020), Figure 2 · [paper](https://arxiv.org/abs/2006.11239)

<a href="assets/paper-redraws/vit.svg"><img src="assets/comparisons/vit.png" alt="Vision Transformer Figure 1 source, editable redraw, and edge overlay"></a>

Dosovitskiy et al. (2020), Figure 1 · [paper](https://arxiv.org/abs/2010.11929)

### Reproduce the paper calibration plates

The SVG gallery itself is dependency-free. Rebuilding the source comparison evidence is an optional QA step:

```bash
python scripts/generate_gallery.py
python -m pip install Pillow
npm install --no-save sharp
python scripts/calibrate_paper_figures.py
```

The harness uses [`references/paper-figure-sources.json`](references/paper-figure-sources.json) for exact PDF URLs, pages, and crop boxes. It writes ignored working files under `tmp/paper-calibration/` and regenerates the committed plates and [`assets/comparisons/qa-report.json`](assets/comparisons/qa-report.json). The six calibration passes and 35-SVG acceptance rules are documented in [`references/fidelity-protocol.md`](references/fidelity-protocol.md).

## Reproducible classic curves

The label printed in the top-right corner of every SVG states its fidelity:

- **FORMULA-DERIVED** — generated from a schedule or functional form described by the paper;
- **ILLUSTRATIVE NORMALIZED** — recreates the qualitative relationship with normalized synthetic values; it is not digitized experimental data.

<table>
<tr>
<td width="33%"><a href="assets/curves/double-descent.svg"><img src="assets/curves/double-descent.svg" alt="Double descent curve"></a><br><b>Double descent</b><br><sub>Illustrative normalized · <a href="https://arxiv.org/abs/1812.11118">Belkin et al. (2018)</a></sub></td>
<td width="33%"><a href="assets/curves/scaling-law.svg"><img src="assets/curves/scaling-law.svg" alt="Neural scaling laws"></a><br><b>Neural scaling laws</b><br><sub>Illustrative normalized log–log trends · <a href="https://arxiv.org/abs/2001.08361">Kaplan et al. (2020)</a></sub></td>
<td width="33%"><a href="assets/curves/grokking.svg"><img src="assets/curves/grokking.svg" alt="Grokking curve"></a><br><b>Grokking</b><br><sub>Illustrative normalized delayed generalization · <a href="https://arxiv.org/abs/2201.02177">Power et al. (2022)</a></sub></td>
</tr>
<tr>
<td><a href="assets/curves/cyclical-lr.svg"><img src="assets/curves/cyclical-lr.svg" alt="Cyclical learning rate"></a><br><b>Cyclical learning rate</b><br><sub>Formula-derived triangular policy · <a href="https://arxiv.org/abs/1506.01186">Smith (2015)</a></sub></td>
<td><a href="assets/curves/cosine-restarts.svg"><img src="assets/curves/cosine-restarts.svg" alt="Cosine warm restarts"></a><br><b>Cosine warm restarts</b><br><sub>Formula-derived SGDR schedule · <a href="https://arxiv.org/abs/1608.03983">Loshchilov & Hutter (2016)</a></sub></td>
<td><a href="assets/curves/diffusion-schedules.svg"><img src="assets/curves/diffusion-schedules.svg" alt="Diffusion schedules"></a><br><b>Diffusion schedules</b><br><sub>Formula-derived normalized cosine ᾱₜ · <a href="https://arxiv.org/abs/2102.09672">Nichol & Dhariwal (2021)</a></sub></td>
</tr>
</table>

### How the curves are reproduced

| Curve | Construction in `scripts/generate_gallery.py` | What it may claim |
|---|---|---|
| Double descent | Two smooth capacity-dependent peaks plus post-interpolation decay | The characteristic qualitative regimes only |
| Scaling laws | Normalized straight trends in log–log coordinates | A generic power-law relationship, not fitted exponents |
| Grokking | Two logistic transitions with delayed test generalization | The timing pattern, not a measured run |
| Cyclical LR | Periodic triangular interpolation between base and maximum learning rates | The defined triangular schedule |
| Cosine restarts | Cosine annealing over successively longer restart periods | The SGDR schedule form |
| Diffusion schedule | `cos²(((t+s)/(1+s))·π/2) / cos²((s/(1+s))·π/2)`, with `s = 0.008` | The normalized cosine cumulative signal schedule |

To reproduce everything deterministically:

```bash
python scripts/generate_gallery.py
```

To discover IDs or regenerate one figure:

```bash
python scripts/generate_gallery.py --list
python scripts/generate_gallery.py --only resnet-block
python scripts/generate_gallery.py --only diffusion-schedules
```

The generated output and its source/provenance record are in [`assets/gallery-manifest.json`](assets/gallery-manifest.json). The original six starter sheets predate the generator and are maintained directly as small editable SVG sources; the other 29 previews are deterministically regenerated by the script.

### Reproducing a new paper figure or line

1. Read the original paper and identify the exact figure, equation, architecture, or experiment being represented.
2. Choose and disclose one fidelity class: `faithful-redraw`, `semantic-redraw`, `formula-derived`, `data-recomputed`, or `illustrative-normalized`.
3. For a `faithful-redraw`, keep source, redraw, and edge overlay together and calibrate crop/aspect, topology/count, geometry, typography, appearance, then small detail. For a semantic redraw, preserve entities, topology, direction, repeated blocks, and exact technical labels while disclosing that layout differs.
4. For curves, prefer source data or an official implementation. If unavailable, use the stated formula. If only the trend is known, normalize it and label it illustrative.
5. Never present synthetic points as reported measurements. A digitized line must identify the original panel, axes, extraction method, and expected error.
6. Add the paper URL, exact figure number, fidelity, caveat, and one-command reproduction entry to the manifest.
7. Render at final publication size and repository-preview size; check the edge overlay, labels, clipping, equations, directionality, grayscale readability, and editability.

## Start here

- [`SKILL.md`](SKILL.md) — operational authoring and reconstruction workflow
- [`assets/gallery-manifest.json`](assets/gallery-manifest.json) — generated asset provenance and commands
- [`assets/manifest.json`](assets/manifest.json) — original starter sheets and editable groups
- [`references/landscape.md`](references/landscape.md) — vector-model and scientific-figure survey
- [`references/catalog-latest.md`](references/catalog-latest.md) — latest curated repositories and discovered candidates
- [`references/figure-ir.md`](references/figure-ir.md) — semantic intermediate representation
- [`references/fidelity-protocol.md`](references/fidelity-protocol.md) — original/redraw/overlay calibration loop and 35-SVG acceptance rules
- [`references/output-contracts.md`](references/output-contracts.md) — SVG, draw.io, and PPTX editability rules

## Refresh and verify

```bash
python scripts/generate_gallery.py
python scripts/sync_catalog.py
python scripts/validate_repo.py
python -m unittest discover -s tests -v
```

The scheduled workflow runs daily at 02:23 UTC. It refreshes repository metadata and star deltas, discovers candidates from bounded GitHub searches, validates the repository, and commits only the generated catalog snapshot. Discovered entries are leads, not endorsements; license and real editable-output behavior require human review before integration.

## Design and provenance rules

1. A bitmap embedded in SVG, PPTX, or draw.io is not an editable figure.
2. Text remains text; connectors remain connectors; repeated components remain reusable groups.
3. Scientific meaning, exact labels, and topology outrank decorative polish.
4. Image models may supply visual ideas, but the editable semantic scene is the source of truth.
5. External assets are opt-in and retain source and license metadata.
6. A semantic redraw is a teaching and authoring aid, not a substitute for citing or consulting the original paper.

Generator code and generic primitive sheets in this repository are MIT-licensed. Paper-inspired semantic redraws include explicit citations; source papers retain their rights, so check downstream reuse requirements for the intended venue. No third-party paper artwork or asset-library files are vendored here.
