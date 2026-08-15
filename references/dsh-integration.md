# DeepSeek Harness integration

## Why this is a native skill, not a bundle

DeepSeek Harness (DSH) separates two extension surfaces:

- a **skill** is an on-demand `SKILL.md` instruction bundle with optional `assets/`, `references/`, and `scripts/` resources;
- a **plugin bundle** is an installable npm package whose `dsh.bundle` manifest contributes a Cordis configuration patch to a profile.

`academic-figure-master` needs the first surface. It teaches the agent a workflow and ships files the agent can read or execute; it does not need to replace the model adapter, sandbox, session store, UI, or orchestration loop. Keeping it as a native filesystem skill avoids JavaScript runtime code, a `prepare` install hook, and profile coupling while preserving DSH hot discovery.

Use a DSH plugin bundle later only for a capability that must run continuously, such as a figure-preview panel, a remote vector-model provider, a semantic scene compiler exposed as a tool, or a release/update UI.

## Install

Install the current checkout for every DSH workspace:

```bash
python scripts/install_skill.py --target dsh
```

The default link is created at `$DSH_HOME/skills/academic-figure-master`, where `DSH_HOME` falls back to `~/.dsh`. Because the installation is a symbolic link, pulling this repository updates the skill immediately. Use `--mode copy` for an immutable snapshot.

DSH also discovers project-local skills. To scope the skill to one repository, install it under that repository's `.dsh/skills/academic-figure-master` with:

```bash
python scripts/install_skill.py --target path \
  --path /absolute/project/.dsh/skills/academic-figure-master
```

DSH's relevant discovery order is project `.dsh/skills`, project `.agents/skills`, custom roots, user `$DSH_HOME/skills`, then shared user `.agents/skills`. A project-local copy therefore overrides a user installation with the same name.

## Run from the sibling source checkout

The verified local layout is:

```text
AutoResearch/
├── deepseek-harness/
└── academic-figure-master/
```

Start the web profile:

```bash
cd ../deepseek-harness
pnpm dsh web
```

The official npm build can be run without changing the source checkout. The currently verified published CLI is:

```bash
pnpm dlx @deepseek-ai/dsh@0.1.0-rc.6 web
```

The source checkout and npm package can briefly report different release-candidate versions. Treat [`dsh-compatibility.json`](dsh-compatibility.json) as the source of truth for both pins.

Open `http://127.0.0.1:3080`, configure a model/API key in **Settings → Models**, choose a workspace, and ask DSH to load `academic-figure-master` before generating or editing a figure. Credentials belong in DSH settings or environment configuration and must never be committed to this repository.

## What “everything is a plugin” means

DSH uses Cordis as a small composition kernel. The kernel owns plugin loading, unloading, and dependency management; model providers, tools, skills, sessions, sandboxes, filesystems, loops, orchestration, and UI are replaceable plugins assembled by configuration. A **profile** is an ordered stack of plugin-bundle patches plus user overrides. The practical effect is that an agent product can be changed by swapping composition layers instead of forking one monolithic runtime.

The boundary matters:

- use a **skill** for conditional knowledge and reusable local resources;
- use a **plugin** for executable services, tools, providers, or UI that participate in the runtime lifecycle;
- use a **bundle** to distribute plugin configuration;
- use a **profile** to select a complete runnable agent composition.

DSH is currently a Developer Preview, so a thin native-skill integration is intentionally safer than compiling against unstable plugin APIs.

## Update and release policy

[`dsh-compatibility.json`](dsh-compatibility.json) keeps two states separate:

- `upstream` is refreshed from the official GitHub repository and npm registry;
- `verified` records the exact source commit and published npm CLI versions that passed local build/version/web smoke tests.

The daily workflow runs `python scripts/sync_dsh.py`. An upstream change updates `upstream` but never silently advances `verified`; compatibility must be tested first. This avoids claiming support merely because a new DSH commit exists.

Repository releases are tag-driven. Update `VERSION`, commit, and push a matching tag such as `v0.1.0`. The GitHub release workflow validates the skill, runs the tests, builds a versioned archive and checksum, and creates or updates the GitHub Release.

## Official references

- [DeepSeek Harness launch page](https://deepseek.com/harness/)
- [DeepSeek Harness official repository](https://github.com/deepseek-ai/deepseek-harness)
- [DSH skill subsystem](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/subsystems/skills.md)
- [DSH plugin publishing tutorial](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/user/develop/basic/publish.md)
