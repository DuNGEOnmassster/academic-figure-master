#!/usr/bin/env python3
"""Install this repository as a Codex, Claude, Cursor, or DSH skill using a link or copy."""

from __future__ import annotations

import argparse
import json
import os
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAYLOAD = ("SKILL.md", "VERSION", "agents", "assets", "references", "scripts", "LICENSE")
GLOBAL_TARGETS = ("codex", "claude", "cursor", "dsh")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", choices=(*GLOBAL_TARGETS, "all", "path"), default="codex")
    parser.add_argument("--path", type=Path, help="Required when --target path is used.")
    parser.add_argument("--mode", choices=("link", "copy"), default="link")
    parser.add_argument("--force", action="store_true", help="Replace an existing installation.")
    return parser.parse_args(argv)


def target_path(target: str, explicit: Path | None = None) -> Path:
    if target == "path":
        if explicit is None:
            raise ValueError("--path is required when --target path is used")
        return explicit.expanduser().resolve()
    if target == "claude":
        return (Path.home() / ".claude" / "skills" / "academic-figure-master").resolve()
    if target == "cursor":
        cursor_root = Path(os.environ.get("CURSOR_HOME", str(Path.home() / ".cursor"))).expanduser()
        return (cursor_root / "skills" / "academic-figure-master").resolve()
    if target == "dsh":
        dsh_root = Path(os.environ.get("DSH_HOME", str(Path.home() / ".dsh"))).expanduser()
        return (dsh_root / "skills" / "academic-figure-master").resolve()
    if target == "all":
        raise ValueError("target_path() requires a concrete target, not all")
    codex_root = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))).expanduser()
    return (codex_root / "skills" / "academic-figure-master").resolve()


def _remove_existing(destination: Path) -> None:
    if destination.is_symlink() or destination.is_file():
        destination.unlink()
    else:
        shutil.rmtree(destination)


def install(destination: Path, mode: str, force: bool = False) -> dict[str, str]:
    destination = destination.expanduser().resolve()
    if destination.exists() or destination.is_symlink():
        try:
            if destination.resolve() == ROOT.resolve():
                return {"status": "already-installed", "path": str(destination), "mode": mode}
        except OSError:
            pass
        if not force:
            raise FileExistsError(f"destination exists: {destination}; pass --force to replace it")
        _remove_existing(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if mode == "link":
        destination.symlink_to(ROOT, target_is_directory=True)
    else:
        destination.mkdir()
        for name in PAYLOAD:
            source = ROOT / name
            target = destination / name
            if source.is_dir():
                shutil.copytree(source, target, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
            elif source.exists():
                shutil.copy2(source, target)
    return {"status": "installed", "path": str(destination), "mode": mode}


def install_targets(target: str, mode: str, force: bool, explicit: Path | None = None) -> list[dict[str, str]]:
    targets = GLOBAL_TARGETS if target == "all" else (target,)
    destinations = [(name, target_path(name, explicit)) for name in targets]
    for _, destination in destinations:
        if not (destination.exists() or destination.is_symlink()) or force:
            continue
        try:
            if destination.resolve() == ROOT.resolve():
                continue
        except OSError:
            pass
        raise FileExistsError(f"destination exists: {destination}; pass --force to replace it")
    return [{"target": name, **install(destination, mode, force)} for name, destination in destinations]


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        results = install_targets(args.target, args.mode, args.force, args.path)
        payload: dict[str, object] = results[0] if args.target != "all" else {"status": "installed", "targets": results}
        print(json.dumps(payload, ensure_ascii=False))
        return 0
    except (OSError, ValueError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
