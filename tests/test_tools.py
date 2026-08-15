from __future__ import annotations

import json
import os
import tempfile
import unittest
import xml.etree.ElementTree as ET
from datetime import UTC, datetime
from pathlib import Path

from scripts.generate_gallery import ASSETS, generate
from scripts.install_skill import install, target_path
from scripts.sync_dsh import build_snapshot
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
            self.assertTrue((destination / "assets" / "gallery-manifest.json").exists())
            json.loads((destination / "references" / "catalog-sources.json").read_text(encoding="utf-8"))

    def test_dsh_target_uses_dsh_home(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            previous = os.environ.get("DSH_HOME")
            os.environ["DSH_HOME"] = temporary
            try:
                expected = Path(temporary) / "skills" / "academic-figure-master"
                self.assertEqual(target_path("dsh"), expected.resolve())
            finally:
                if previous is None:
                    os.environ.pop("DSH_HOME", None)
                else:
                    os.environ["DSH_HOME"] = previous

    def test_dsh_sync_preserves_verified_pin(self) -> None:
        repository = {
            "default_branch": "master",
            "html_url": "https://github.com/deepseek-ai/deepseek-harness",
            "pushed_at": "2026-08-15T00:00:00Z",
        }
        commit = {
            "sha": "a" * 40,
            "html_url": f"https://github.com/deepseek-ai/deepseek-harness/commit/{'a' * 40}",
            "commit": {"committer": {"date": "2026-08-15T00:00:00Z"}},
        }
        npm = {"dist-tags": {"latest": "0.1.0-rc.6"}, "time": {"0.1.0-rc.6": "2026-08-15T00:00:00Z"}}
        previous = {
            "verified": {
                "commit": "b" * 40,
                "source_cli_version": "0.1.0-rc.5",
                "npm_cli_version": "0.1.0-rc.5",
            }
        }
        snapshot = build_snapshot(repository, commit, None, npm, previous)
        self.assertEqual(snapshot["upstream"]["latest_commit"], "a" * 40)
        self.assertEqual(snapshot["upstream"]["npm"]["version"], "0.1.0-rc.6")
        self.assertEqual(snapshot["verified"], previous["verified"])
        self.assertFalse(snapshot["delivery"]["plugin_bundle_required"])

    def test_gallery_is_deterministic_and_complete(self) -> None:
        self.assertEqual(len(ASSETS), 29)
        with tempfile.TemporaryDirectory() as temporary:
            output_root = Path(temporary) / "assets"
            written = generate(output_root)
            self.assertEqual(len(written), 19)
            manifest = json.loads((output_root / "gallery-manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(len(manifest["assets"]), 29)
            for asset in ASSETS:
                committed = ROOT / "assets" / asset.relative_path
                if asset.category == "paper":
                    root = ET.parse(committed).getroot()
                    ids = {element.get("id") for element in root.iter() if element.get("id")}
                    self.assertEqual(root.get("data-fidelity"), "pixel-exact-source-vector")
                    self.assertIn("source-vector-operators", ids)
                    self.assertIn("semantic-edit-layer", ids)
                else:
                    generated = output_root / asset.relative_path
                    self.assertEqual(generated.read_bytes(), committed.read_bytes(), asset.slug)

    def test_paper_gallery_requires_extraction_pipeline(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(ValueError, "direct PDF operator extraction"):
                generate(Path(temporary), {"resnet-block"})


if __name__ == "__main__":
    unittest.main()
