#!/usr/bin/env python3
"""Install Academic Figure Master and its teaser/pipeline entrypoints using links or copies."""
from __future__ import annotations

import argparse
import json
import os
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAYLOAD = ("SKILL.md", "VERSION", "agents", "assets", "references", "scripts", "entrypoints", "LICENSE")
GLOBAL_TARGETS = ("codex", "claude", "cursor", "dsh")
MODES = ("teaser", "pipeline")


def lexical_path(path: Path) -> Path:
    # Preserve the final symlink: --force must remove the link, never its target.
    absolute = Path(os.path.abspath(path.expanduser()))
    return absolute.parent.resolve() / absolute.name


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", choices=(*GLOBAL_TARGETS, "all", "path"), default="codex")
    parser.add_argument("--path", type=Path, help="Main skill destination; mode skills are installed beside it.")
    parser.add_argument("--mode", choices=("link", "copy"), default="link")
    parser.add_argument("--force", action="store_true", help="Replace an existing installation at the named destinations.")
    parser.add_argument("--main-only", action="store_true", help="Do not install the teaser/pipeline aliases.")
    return parser.parse_args(argv)


def target_path(target: str, explicit: Path | None = None) -> Path:
    if target == "path":
        if explicit is None:
            raise ValueError("--path is required when --target path is used")
        return lexical_path(explicit)
    if target == "claude":
        base = Path.home() / ".claude"
    elif target in ("codex", "cursor", "dsh"):
        env_name = {"codex": "CODEX_HOME", "cursor": "CURSOR_HOME", "dsh": "DSH_HOME"}[target]
        base = Path(os.environ.get(env_name, str(Path.home() / f".{target}")))
    else:
        raise ValueError("target_path() requires a concrete target")
    return lexical_path(base / "skills" / "academic-figure-master")


def payload_sources(skill: str) -> dict[str, Path]:
    if skill == "academic-figure-master":
        return {name: ROOT / name for name in PAYLOAD if (ROOT / name).exists()}
    if skill not in MODES:
        raise ValueError(f"unknown skill: {skill}")
    return {"SKILL.md": ROOT / "entrypoints" / skill / "SKILL.md",
            "agents": ROOT / "entrypoints" / skill / "agents",
            **{name: ROOT / name for name in ("assets", "references", "scripts", "LICENSE", "VERSION")}}


def is_linked(destination: Path, skill: str) -> bool:
    if skill == "academic-figure-master":
        return destination.is_symlink() and destination.resolve() == ROOT.resolve()
    sources = payload_sources(skill)
    return destination.is_dir() and not destination.is_symlink() and all(
        (destination / name).is_symlink() and (destination / name).resolve() == source.resolve()
        for name, source in sources.items())


def preflight(destination: Path, skill: str, mode: str, force: bool) -> bool:
    if mode not in ("link", "copy"):
        raise ValueError(f"unknown mode: {mode}")
    for source in payload_sources(skill).values():
        if not source.exists():
            raise FileNotFoundError(f"installation source is missing: {source}")
    if is_linked(destination, skill) and mode == "link":
        return True
    resolved = destination.resolve()
    repo = ROOT.resolve()
    if resolved == repo or resolved in repo.parents or repo in resolved.parents:
        # A stale external symlink may point into the repo; replacing the link is safe.
        if not destination.is_symlink():
            raise ValueError(f"refusing to replace repository or overlapping directory: {destination}")
    if (destination.exists() or destination.is_symlink()) and not force:
        raise FileExistsError(f"destination exists: {destination}; pass --force to replace it")
    return False


def _remove_existing(destination: Path) -> None:
    if destination.is_symlink() or destination.is_file():
        destination.unlink()
    else:
        shutil.rmtree(destination)


def install(destination: Path, mode: str, force: bool = False,
            skill: str = "academic-figure-master") -> dict[str, str]:
    destination = lexical_path(destination)
    if preflight(destination, skill, mode, force):
        return {"status": "already-installed", "path": str(destination), "mode": mode, "skill": skill}
    if destination.exists() or destination.is_symlink():
        _remove_existing(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if mode == "link" and skill == "academic-figure-master":
        destination.symlink_to(ROOT, target_is_directory=True)
    else:
        destination.mkdir()
        for name, source in payload_sources(skill).items():
            target = destination / name
            if mode == "link":
                target.symlink_to(source, target_is_directory=source.is_dir())
            elif source.is_dir():
                shutil.copytree(source, target, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
            else:
                shutil.copy2(source, target)
    return {"status": "installed", "path": str(destination), "mode": mode, "skill": skill}


def install_targets(target: str, mode: str, force: bool, explicit: Path | None = None,
                    with_modes: bool = True) -> list[dict]:
    targets = GLOBAL_TARGETS if target == "all" else (target,)
    plans = []
    for name in targets:
        destination = target_path(name, explicit)
        siblings = [(skill, destination.parent / skill) for skill in MODES] if with_modes else []
        plans.append((name, destination, siblings))
    # Check the whole plan before writing, including conflicts at a short alias.
    paths = [lexical_path(p) for _, dest, siblings in plans for p in [dest, *(p for _, p in siblings)]]
    if len(paths) != len(set(paths)):
        raise ValueError("installation destinations overlap; choose a main path distinct from teaser/pipeline")
    for _, dest, siblings in plans:
        for skill, path in [("academic-figure-master", dest), *siblings]:
            preflight(path, skill, mode, force)
    results = []
    for name, dest, siblings in plans:
        result = {"target": name, **install(dest, mode, force)}
        result["modes"] = [install(path, mode, force, skill) for skill, path in siblings]
        results.append(result)
    return results


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        results = install_targets(args.target, args.mode, args.force, args.path, not args.main_only)
        payload = results[0] if args.target != "all" else {"status": "installed", "targets": results}
        print(json.dumps(payload, ensure_ascii=False))
        return 0
    except (OSError, ValueError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
