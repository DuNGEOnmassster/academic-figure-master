from __future__ import annotations

import json
import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path

from scripts.install_skill import install
from scripts.sync_catalog import passes_discovery_filter, render_markdown, sync_catalog
from scripts.validate_repo import ROOT, validate


def payload(name: str, stars: int = 10) -> dict:
    return {
        "full_name": name,
        "html_url": f"https://github.com/{name}",
        "description": "Editable scientific SVG figure generator",
        "stargazers_count": stars,
        "forks_count": 2,
        "open_issues_count": 1,
        "license": {"spdx_id": "MIT"},
        "archived": False,
        "fork": False,
        "owner": {"type": "Organization"},
        "default_branch": "main",
        "created_at": "2026-01-01T00:00:00Z",
        "updated_at": "2026-08-13T00:00:00Z",
        "pushed_at": "2026-08-12T00:00:00Z",
        "topics": ["svg", "science"],
    }


class FakeClient:
    def repository(self, full_name: str) -> dict:
        return payload(full_name, 101)

    def search(self, query: str, limit: int) -> list[dict]:
        return [payload("new/figure-tool", 42)]


class ToolTests(unittest.TestCase):
    def test_repository_validates(self) -> None:
        self.assertEqual(validate(ROOT), [])

    def test_sync_tracks_star_delta_and_discovery(self) -> None:
        sources = {
            "lookback_days": 10,
            "repositories": [
                {
                    "repo": "owner/tool",
                    "category": "vector-model",
                    "readiness": "use-now",
                    "integration": "adapter",
                    "why": "test",
                }
            ],
            "discovery_queries": [
                {"id": "new", "category": "vector-model", "query": "created:>={created_since}", "limit": 5}
            ],
        }
        previous = {"curated": [{"repo": "owner/tool", "stars": 99}], "discovered": []}
        snapshot = sync_catalog(sources, previous, FakeClient(), datetime(2026, 8, 13, tzinfo=UTC))
        self.assertEqual(snapshot["curated"][0]["stars_delta"], 2)
        self.assertEqual(snapshot["discovered"][0]["repo"], "new/figure-tool")
        self.assertIn("owner/tool", render_markdown(snapshot))

    def test_discovery_filter_rejects_generic_svg_mentions(self) -> None:
        generic = payload("owner/qrcode", 500)
        generic["description"] = "Render a QR code as PNG or SVG"
        self.assertFalse(passes_discovery_filter(generic, "vector-model"))
        self.assertTrue(passes_discovery_filter(payload("owner/vectorizer"), "vector-model"))

    def test_copy_install_contains_skill_payload(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary) / "academic-figure-master"
            result = install(destination, "copy")
            self.assertEqual(result["status"], "installed")
            self.assertTrue((destination / "SKILL.md").exists())
            self.assertTrue((destination / "assets" / "examples" / "figure-spec.json").exists())
            json.loads((destination / "references" / "catalog-sources.json").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
