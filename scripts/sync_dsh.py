#!/usr/bin/env python3
"""Track the official DeepSeek Harness commit, release, and npm CLI version."""

from __future__ import annotations

import argparse
import http.client
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "references" / "dsh-compatibility.json"
REPOSITORY = "deepseek-ai/deepseek-harness"
NPM_PACKAGE = "@deepseek-ai/dsh"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args(argv)


def _request_json(url: str, *, token: str | None = None, missing_ok: bool = False) -> Any:
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "academic-figure-master-dsh-sync/1.0"}
    if "api.github.com" in url:
        headers["X-GitHub-Api-Version"] = "2022-11-28"
        if token:
            headers["Authorization"] = f"Bearer {token}"
    last_error: BaseException | None = None
    for attempt in range(5):
        request = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            if exc.code == 404 and missing_ok:
                return None
            last_error = exc
            if exc.code not in {429, 500, 502, 503, 504}:
                raise
        except (urllib.error.URLError, TimeoutError, http.client.IncompleteRead, json.JSONDecodeError) as exc:
            last_error = exc
        if attempt < 4:
            time.sleep(0.25 * (2**attempt))
    raise RuntimeError(f"request failed after 5 attempts: {url}: {last_error}") from last_error


def build_snapshot(
    repository: dict[str, Any],
    commit: dict[str, Any],
    release: dict[str, Any] | None,
    npm: dict[str, Any],
    previous: dict[str, Any] | None = None,
) -> dict[str, Any]:
    default_branch = str(repository.get("default_branch") or "master")
    commit_detail = commit.get("commit") or {}
    committer = commit_detail.get("committer") or {}
    tags = npm.get("dist-tags") or {}
    latest_npm = str(tags.get("latest") or "")
    npm_times = npm.get("time") or {}
    snapshot: dict[str, Any] = {
        "schema_version": 1,
        "upstream": {
            "repository": REPOSITORY,
            "repository_url": str(repository.get("html_url") or f"https://github.com/{REPOSITORY}"),
            "default_branch": default_branch,
            "latest_commit": str(commit.get("sha") or ""),
            "latest_commit_url": str(commit.get("html_url") or ""),
            "latest_commit_at": str(committer.get("date") or ""),
            "repository_pushed_at": str(repository.get("pushed_at") or ""),
            "github_release": None,
            "npm": {
                "package": NPM_PACKAGE,
                "version": latest_npm,
                "published_at": str(npm_times.get(latest_npm) or ""),
                "url": f"https://www.npmjs.com/package/{urllib.parse.quote(NPM_PACKAGE, safe='@')}",
            },
        },
        "delivery": {
            "mode": "native-filesystem-skill",
            "plugin_bundle_required": False,
            "user_install_root": "$DSH_HOME/skills/academic-figure-master",
            "project_install_root": ".dsh/skills/academic-figure-master",
            "install_command": "python scripts/install_skill.py --target dsh",
        },
    }
    if release:
        snapshot["upstream"]["github_release"] = {
            "tag": str(release.get("tag_name") or ""),
            "name": str(release.get("name") or ""),
            "published_at": str(release.get("published_at") or ""),
            "url": str(release.get("html_url") or ""),
        }
    if previous and previous.get("verified"):
        snapshot["verified"] = previous["verified"]
    return snapshot


def fetch_snapshot(previous: dict[str, Any] | None = None) -> dict[str, Any]:
    token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
    api = f"https://api.github.com/repos/{REPOSITORY}"
    repository = _request_json(api, token=token)
    default_branch = str(repository.get("default_branch") or "master")
    commit = _request_json(f"{api}/commits/{urllib.parse.quote(default_branch, safe='')}", token=token)
    release = _request_json(f"{api}/releases/latest", token=token, missing_ok=True)
    npm_name = urllib.parse.quote(NPM_PACKAGE, safe="")
    npm = _request_json(f"https://registry.npmjs.org/{npm_name}")
    return build_snapshot(repository, commit, release, npm, previous)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    previous = json.loads(args.output.read_text(encoding="utf-8")) if args.output.exists() else None
    snapshot = fetch_snapshot(previous)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(snapshot, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
