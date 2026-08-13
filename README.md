# Academic Figure Master

A lightweight Codex/Claude skill for publication-ready academic figures that stay **genuinely editable** in SVG, draw.io, or PowerPoint. It is designed for the gap between one-shot raster image generation and heavyweight manual tools: fast enough for everyday research, structured enough for precise component-level revision.

The repository currently provides:

- a reusable figure-authoring and reference-reconstruction workflow;
- an evidence-backed survey of vector models, scientific-figure systems, skills, editors, and asset libraries;
- a machine-readable GitHub catalog with stars, activity, license signals, and new-project discovery;
- six original native-SVG starter sheets for manifolds, SDE/ODE trajectories, hand-drawn arrows, diffusion processes, tensor stacks, and neural modules;
- a daily GitHub Actions refresh; and
- dependency-free local validation, synchronization, and installation scripts.

## Install

After cloning the private repository:

```bash
python scripts/install_skill.py --target codex
```

The default installation is a symbolic link, so local repository updates become immediately available to Codex. Use `--mode copy` for an isolated copy, `--target claude` for Claude, or `--target path --path /absolute/destination` for a custom skill directory.

Invoke it with a request such as:

```text
Use $academic-figure-master to reconstruct this method figure as editable SVG.
Keep every label as text and preserve stable object IDs for later revisions.
```

## Start here

- [`SKILL.md`](SKILL.md) — operational workflow and quality contract
- [`references/landscape.md`](references/landscape.md) — current market and research survey
- [`references/catalog-latest.md`](references/catalog-latest.md) — latest curated repositories and discovered candidates
- [`references/catalog-sources.json`](references/catalog-sources.json) — reviewed seeds and discovery queries
- [`references/figure-ir.md`](references/figure-ir.md) — semantic intermediate representation
- [`references/output-contracts.md`](references/output-contracts.md) — SVG, draw.io, and PPTX editability rules
- [`assets/manifest.json`](assets/manifest.json) — original reusable primitive sheets and licenses

## Refresh and verify

```bash
python scripts/sync_catalog.py
python scripts/validate_repo.py
python -m unittest discover -s tests -v
```

The scheduled workflow runs daily at 02:23 UTC. It refreshes existing repository metadata and star deltas, discovers candidates from bounded GitHub searches, validates the repository, and commits only the generated catalog snapshot. Discovered entries are leads, not endorsements; license and real editable-output behavior still require human review before integration.

## Design rules

1. A bitmap embedded in an SVG, PPTX, or draw.io file is not an editable figure.
2. Text remains text; connectors remain connectors; repeated components remain reusable groups.
3. Scientific meaning, exact labels, and topology outrank decorative polish.
4. Image models may supply visual ideas, but the editable semantic scene is the source of truth.
5. External assets are opt-in and must retain source and license metadata.

## Status

This first version is a directly installable skill and curated foundation, not yet a full visual editor. The intended next layer is a compiler from a stable figure IR into native SVG, draw.io, and PPTX objects, followed by reference-image decomposition and object-level patching adapters.

Licensed under MIT. Third-party projects and asset libraries listed in the survey keep their own licenses; none of their assets are vendored here.
