#!/usr/bin/env python3
"""Refresh curated GitHub metadata and discover new academic-figure candidates."""

from __future__ import annotations

import argparse
import http.client
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, Protocol


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCES = ROOT / "references" / "catalog-sources.json"
DEFAULT_SNAPSHOT = ROOT / "references" / "catalog-snapshot.json"
DEFAULT_MARKDOWN = ROOT / "references" / "catalog-latest.md"


class Client(Protocol):
    def repository(self, full_name: str) -> dict[str, Any]: ...

    def search(self, query: str, limit: int) -> list[dict[str, Any]]: ...


class GitHubError(RuntimeError):
    """A bounded GitHub API failure safe to include in the sync report."""


class GitHubClient:
    def __init__(self, token: str | None = None, api_url: str = "https://api.github.com") -> None:
        self.token = token or os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
        self.api_url = api_url.rstrip("/")

    def _get(self, path: str) -> Any:
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "academic-figure-master-catalog/1.0",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        url = f"{self.api_url}{path}"
        last_error: BaseException | None = None
        attempts = 5
        for attempt in range(attempts):
            request = urllib.request.Request(url, headers=headers)
            try:
                with urllib.request.urlopen(request, timeout=30) as response:
                    return json.loads(response.read().decode("utf-8"))
            except urllib.error.HTTPError as exc:
                detail = exc.read().decode("utf-8", errors="replace")[:400]
                if exc.code not in {429, 500, 502, 503, 504}:
                    raise GitHubError(f"HTTP {exc.code}: {detail}") from exc
                last_error = GitHubError(f"HTTP {exc.code}: {detail}")
            except (urllib.error.URLError, TimeoutError, http.client.IncompleteRead, json.JSONDecodeError) as exc:
                last_error = exc
            if attempt < attempts - 1:
                time.sleep(0.25 * (2**attempt))
        raise GitHubError(f"GitHub request failed after {attempts} attempts: {last_error}") from last_error

    def repository(self, full_name: str) -> dict[str, Any]:
        safe_name = "/".join(urllib.parse.quote(part, safe="") for part in full_name.split("/"))
        return self._get(f"/repos/{safe_name}")

    def search(self, query: str, limit: int) -> list[dict[str, Any]]:
        target = max(1, min(limit, 100))
        page_size = min(target, 10)
        items: list[dict[str, Any]] = []
        page = 1
        while len(items) < target:
            requested = min(page_size, target - len(items))
            params = urllib.parse.urlencode(
                {
                    "q": query,
                    "sort": "updated",
                    "order": "desc",
                    "per_page": requested,
                    "page": page,
                }
            )
            payload = self._get(f"/search/repositories?{params}")
            batch = list(payload.get("items") or [])
            items.extend(batch)
            if len(batch) < requested:
                break
            page += 1
        return items[:target]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", type=Path, default=DEFAULT_SOURCES)
    parser.add_argument("--snapshot", type=Path, default=DEFAULT_SNAPSHOT)
    parser.add_argument("--markdown", type=Path, default=DEFAULT_MARKDOWN)
    parser.add_argument("--created-since", help="Override discovery lower bound (YYYY-MM-DD).")
    return parser.parse_args(argv)


def _load_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _license(payload: dict[str, Any]) -> str | None:
    info = payload.get("license") or {}
    value = info.get("spdx_id")
    return None if value in (None, "", "NOASSERTION") else str(value)


def repository_record(payload: dict[str, Any]) -> dict[str, Any]:
    owner = payload.get("owner") or {}
    return {
        "repo": str(payload.get("full_name") or ""),
        "url": str(payload.get("html_url") or ""),
        "description": str(payload.get("description") or "").strip(),
        "stars": int(payload.get("stargazers_count") or 0),
        "forks": int(payload.get("forks_count") or 0),
        "open_issues": int(payload.get("open_issues_count") or 0),
        "license": _license(payload),
        "archived": bool(payload.get("archived")),
        "fork": bool(payload.get("fork")),
        "owner_type": str(owner.get("type") or ""),
        "default_branch": str(payload.get("default_branch") or ""),
        "created_at": str(payload.get("created_at") or ""),
        "updated_at": str(payload.get("updated_at") or ""),
        "pushed_at": str(payload.get("pushed_at") or ""),
        "topics": sorted(str(topic) for topic in (payload.get("topics") or [])),
    }


def _previous_index(snapshot: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    if not snapshot:
        return {}
    records = list(snapshot.get("curated") or []) + list(snapshot.get("discovered") or [])
    return {str(record.get("repo", "")).lower(): record for record in records if record.get("repo")}


def _decorate(record: dict[str, Any], previous: dict[str, dict[str, Any]]) -> dict[str, Any]:
    old = previous.get(record["repo"].lower())
    record["previous_stars"] = None if old is None else int(old.get("stars") or 0)
    record["stars_delta"] = 0 if old is None else record["stars"] - int(old.get("stars") or 0)
    record["is_new"] = old is None
    return record


RELEVANCE_TERMS = {
    "vector-model": ("svg", "vector", "raster", "graphics", "vlm"),
    "scientific-figure-system": ("scientific", "academic", "paper", "figure", "illustration"),
    "agent-skill": ("skill", "agent", "drawio", "pptx", "figure"),
    "asset-library": ("icon", "asset", "svg", "science", "illustration"),
}


def passes_discovery_filter(record: dict[str, Any], category: str) -> bool:
    text = " ".join(
        [record.get("repo", ""), record.get("description", ""), " ".join(record.get("topics") or [])]
    ).lower()
    if record.get("archived") or record.get("fork"):
        return False
    if category == "vector-model":
        return any(term in text for term in ("svg", "vector")) and any(
            term in text for term in ("generat", "vectoriz", "raster", "image-to-svg", "image to svg", "model")
        )
    if category == "scientific-figure-system":
        return any(term in text for term in ("scientific", "academic", "paper", "research")) and any(
            term in text for term in ("figure", "illustration", "diagram", "plot", "visual")
        )
    if category == "agent-skill":
        return "skill" in text and any(
            term in text for term in ("figure", "diagram", "drawio", "svg", "pptx", "scientific", "academic")
        )
    if category == "asset-library":
        return any(term in text for term in ("scientific", "science", "biology", "medical", "chemistry")) and any(
            term in text for term in ("svg", "icon", "asset", "illustration", "template")
        )
    return False


def relevance_score(record: dict[str, Any], category: str) -> int:
    text = " ".join(
        [record.get("repo", ""), record.get("description", ""), " ".join(record.get("topics") or [])]
    ).lower()
    score = sum(8 for term in RELEVANCE_TERMS.get(category, ()) if term in text)
    if record.get("license"):
        score += 8
    if record.get("archived") or record.get("fork"):
        score -= 25
    score += min(20, len(str(record.get("stars", 0))) * 3)
    return score


def sync_catalog(
    sources: dict[str, Any],
    previous_snapshot: dict[str, Any] | None,
    client: Client,
    now: datetime,
    created_since: str | None = None,
) -> dict[str, Any]:
    previous = _previous_index(previous_snapshot)
    curated: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    curated_names = {str(item["repo"]).lower() for item in sources.get("repositories") or []}

    for seed in sources.get("repositories") or []:
        try:
            record = repository_record(client.repository(str(seed["repo"])))
            for field in ("category", "readiness", "integration", "why"):
                record[field] = seed.get(field)
            record["curated"] = True
            curated.append(_decorate(record, previous))
        except (GitHubError, KeyError, TypeError, ValueError) as exc:
            errors.append({"scope": str(seed.get("repo")), "error": str(exc)})

    if created_since is None:
        lookback = int(sources.get("lookback_days") or 180)
        created_since = (now - timedelta(days=lookback)).date().isoformat()

    discovered_by_name: dict[str, dict[str, Any]] = {}
    for query in sources.get("discovery_queries") or []:
        query_text = str(query["query"]).replace("{created_since}", created_since)
        try:
            payloads = client.search(query_text, int(query.get("limit") or 10))
        except (GitHubError, KeyError, TypeError, ValueError) as exc:
            errors.append({"scope": str(query.get("id")), "error": str(exc)})
            continue
        for payload in payloads:
            record = repository_record(payload)
            key = record["repo"].lower()
            if not key or key in curated_names:
                continue
            query_id = str(query["id"])
            category = str(query["category"])
            if not passes_discovery_filter(record, category):
                continue
            if key in discovered_by_name:
                existing = discovered_by_name[key]
                existing["matched_queries"] = sorted(set(existing["matched_queries"] + [query_id]))
                existing["relevance"] = max(existing["relevance"], relevance_score(record, category))
                continue
            record["category"] = category
            record["curated"] = False
            record["matched_queries"] = [query_id]
            record["relevance"] = relevance_score(record, category)
            discovered_by_name[key] = _decorate(record, previous)

    curated.sort(key=lambda item: (str(item.get("category")), -int(item.get("stars") or 0), item["repo"]))
    discovered = sorted(
        discovered_by_name.values(),
        key=lambda item: (-int(item.get("relevance") or 0), -int(item.get("stars") or 0), item["repo"]),
    )
    snapshot = {
        "schema_version": 1,
        "generated_at": now.astimezone(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "created_since": created_since,
        "summary": {
            "curated": len(curated),
            "discovered": len(discovered),
            "new_discovered": sum(1 for item in discovered if item["is_new"]),
            "errors": len(errors),
        },
        "curated": curated,
        "discovered": discovered,
        "errors": errors,
    }
    if not curated and errors:
        raise GitHubError("all curated repository lookups failed")
    return snapshot


def _escape(value: Any) -> str:
    return str(value if value not in (None, "") else "—").replace("|", "\\|").replace("\n", " ")


def render_markdown(snapshot: dict[str, Any]) -> str:
    summary = snapshot["summary"]
    lines = [
        "# Academic figure catalog — latest snapshot",
        "",
        f"Generated: `{snapshot['generated_at']}`. Curated: **{summary['curated']}**. "
        f"Discovered candidates: **{summary['discovered']}** "
        f"({summary['new_discovered']} new relative to the previous snapshot).",
        "",
        "Stars are a discovery signal, not a quality score. A candidate is not executable or endorsed until its license, outputs, and edit behavior are reviewed.",
        "",
        "## Curated repositories",
        "",
        "| Repository | Category | Stars | Δ | License | Last push | Readiness |",
        "|---|---|---:|---:|---|---|---|",
    ]
    for item in snapshot["curated"]:
        lines.append(
            f"| [{_escape(item['repo'])}]({item['url']}) | {_escape(item.get('category'))} | "
            f"{item['stars']:,} | {item['stars_delta']:+d} | {_escape(item.get('license'))} | "
            f"{_escape(str(item.get('pushed_at', ''))[:10])} | {_escape(item.get('readiness'))} |"
        )
    lines.extend(
        [
            "",
            "## Discovered candidates",
            "",
            "Top 50 candidates by a lightweight relevance heuristic. Review before promotion to `catalog-sources.json`.",
            "",
            "| Repository | Proposed category | Stars | License | Last push | Queries | New |",
            "|---|---|---:|---|---|---|---|",
        ]
    )
    for item in snapshot["discovered"][:50]:
        lines.append(
            f"| [{_escape(item['repo'])}]({item['url']}) | {_escape(item.get('category'))} | "
            f"{item['stars']:,} | {_escape(item.get('license'))} | {_escape(str(item.get('pushed_at', ''))[:10])} | "
            f"{_escape(', '.join(item.get('matched_queries') or []))} | {'yes' if item['is_new'] else 'no'} |"
        )
    if snapshot.get("errors"):
        lines.extend(["", "## Sync warnings", ""])
        for error in snapshot["errors"]:
            lines.append(f"- `{_escape(error['scope'])}`: {_escape(error['error'])}")
    lines.extend(
        [
            "",
            "## Promotion gate",
            "",
            "1. Confirm repository identity and current license.",
            "2. Inspect a real SVG/PPTX/draw.io output for native text, grouping, connectors, and raster embedding.",
            "3. Reproduce one generation task and one local-edit task.",
            "4. Record the narrow capability worth integrating; do not copy upstream instructions wholesale.",
            "",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        sources = _load_json(args.sources)
        previous = _load_json(args.snapshot, default=None)
        snapshot = sync_catalog(sources, previous, GitHubClient(), datetime.now(UTC), args.created_since)
        args.snapshot.parent.mkdir(parents=True, exist_ok=True)
        args.markdown.parent.mkdir(parents=True, exist_ok=True)
        args.snapshot.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        args.markdown.write_text(render_markdown(snapshot), encoding="utf-8")
        print(json.dumps(snapshot["summary"], ensure_ascii=False))
        return 0
    except (GitHubError, OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
