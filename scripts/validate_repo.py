#!/usr/bin/env python3
"""Validate skill metadata, catalogs, and bundled vector assets without dependencies."""

from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SVG_NS = "{http://www.w3.org/2000/svg}"


def validate(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    skill_path = root / "SKILL.md"
    if not skill_path.exists():
        return ["SKILL.md is missing"]
    text = skill_path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not match:
        errors.append("SKILL.md frontmatter is invalid")
    else:
        keys = [line.split(":", 1)[0].strip() for line in match.group(1).splitlines() if ":" in line]
        if keys != ["name", "description"]:
            errors.append("SKILL.md frontmatter must contain only name and description")
        if "name: academic-figure-master" not in match.group(1):
            errors.append("skill name is incorrect")
    agent_path = root / "agents" / "openai.yaml"
    if not agent_path.exists() or "$academic-figure-master" not in agent_path.read_text(encoding="utf-8"):
        errors.append("agents/openai.yaml is missing or has a stale default prompt")

    source_path = root / "references" / "catalog-sources.json"
    try:
        sources = json.loads(source_path.read_text(encoding="utf-8"))
        repos = [item["repo"].lower() for item in sources["repositories"]]
        queries = [item["id"] for item in sources["discovery_queries"]]
        if len(repos) != len(set(repos)):
            errors.append("catalog contains duplicate repositories")
        if len(queries) != len(set(queries)):
            errors.append("catalog contains duplicate discovery query ids")
    except (OSError, json.JSONDecodeError, KeyError, TypeError) as exc:
        errors.append(f"catalog-sources.json is invalid: {exc}")

    asset_root = root / "assets"
    svgs = sorted(asset_root.rglob("*.svg"))
    if len(svgs) < 35:
        errors.append("at least 35 editable SVG assets are required")
    for path in svgs:
        display_path = path.relative_to(root)
        try:
            tree = ET.parse(path)
            svg = tree.getroot()
            if svg.tag != f"{SVG_NS}svg":
                errors.append(f"{display_path}: root is not SVG")
            if not svg.get("viewBox"):
                errors.append(f"{display_path}: viewBox is missing")
            pixel_exact = svg.get("data-fidelity") == "pixel-exact-source-vector"
            ids: list[str] = []
            for element in svg.iter():
                local = element.tag.rsplit("}", 1)[-1]
                if local in {"script", "foreignObject"}:
                    errors.append(f"{display_path}: forbidden <{local}> element")
                if local == "image":
                    href = next((value for key, value in element.attrib.items() if key.endswith("href")), "")
                    if not pixel_exact or not href.startswith("data:image/"):
                        errors.append(f"{display_path}: only source-faithful embedded data images are allowed")
                if element.get("id"):
                    ids.append(str(element.get("id")))
                for value in element.attrib.values():
                    if isinstance(value, str) and ("http://" in value or "https://" in value):
                        errors.append(f"{display_path}: external reference is not allowed")
            if len(ids) != len(set(ids)):
                errors.append(f"{display_path}: duplicate element ids")
            if not any(element.tag == f"{SVG_NS}g" and element.get("id") for element in svg.iter()):
                errors.append(f"{display_path}: no named editable groups")
            if any(element.get("id") == "figure-title" for element in svg.iter()):
                errors.append(f"{display_path}: reusable assets must not contain a slide-style title banner")
        except (ET.ParseError, OSError) as exc:
            errors.append(f"{display_path}: invalid SVG: {exc}")

    readme_path = root / "README.md"
    readme = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""
    try:
        starter_manifest = json.loads((asset_root / "manifest.json").read_text(encoding="utf-8"))
        gallery_manifest = json.loads((asset_root / "gallery-manifest.json").read_text(encoding="utf-8"))
        gallery_assets = gallery_manifest["assets"]
        if len(gallery_assets) != 29:
            errors.append("gallery-manifest.json must contain 29 generated assets")
        gallery_ids = [item["id"] for item in gallery_assets]
        if len(gallery_ids) != len(set(gallery_ids)):
            errors.append("gallery-manifest.json contains duplicate asset ids")
        allowed_reproduction = {"original", "faithful-redraw", "semantic-redraw", "pixel-exact-dual-layer", "formula-derived", "illustrative-normalized"}
        for item in gallery_assets:
            relative = str(item["path"])
            if not (asset_root / relative).exists():
                errors.append(f"gallery asset is missing: assets/{relative}")
            if item.get("reproduction") not in allowed_reproduction:
                errors.append(f"{item.get('id')}: unsupported reproduction class")
            if f"assets/{relative}" not in readme:
                errors.append(f"README does not display assets/{relative}")
            if item.get("category") == "paper":
                if item.get("reproduction") != "pixel-exact-dual-layer":
                    errors.append(f"{item.get('id')}: paper asset must use pixel-exact-dual-layer")
                if not (item.get("source") or {}).get("figure"):
                    errors.append(f"{item.get('id')}: pixel-exact redraw is missing an exact source figure number")
                comparison = asset_root / "comparisons" / f"{item.get('id')}.png"
                if not comparison.exists():
                    errors.append(f"{item.get('id')}: source/redraw/overlay comparison is missing")
                paper_svg = ET.parse(asset_root / relative).getroot()
                paper_ids_in_svg = {element.get("id") for element in paper_svg.iter() if element.get("id")}
                if paper_svg.get("data-fidelity") != "pixel-exact-source-vector":
                    errors.append(f"{item.get('id')}: visible layer is not marked pixel-exact-source-vector")
                if "source-vector-operators" not in paper_ids_in_svg:
                    errors.append(f"{item.get('id')}: source-vector-operators layer is missing")
                if "semantic-edit-layer" not in paper_ids_in_svg:
                    errors.append(f"{item.get('id')}: semantic-edit-layer is missing")
        for item in starter_manifest["assets"]:
            relative = str(item["path"])
            if f"assets/{relative}" not in readme:
                errors.append(f"README does not display assets/{relative}")
        qa_report = json.loads((asset_root / "comparisons" / "qa-report.json").read_text(encoding="utf-8"))
        exact_report = json.loads((asset_root / "paper-redraws" / "pixel-exact-manifest.json").read_text(encoding="utf-8"))
        qa_ids = [item["id"] for item in qa_report["figures"]]
        paper_ids = [item["id"] for item in gallery_assets if item.get("category") == "paper"]
        if sorted(qa_ids) != sorted(paper_ids):
            errors.append("paper comparison QA report must cover every pixel-exact redraw exactly once")
        exact_ids = [item["id"] for item in exact_report["figures"]]
        if sorted(exact_ids) != sorted(paper_ids):
            errors.append("pixel-exact manifest must cover every paper redraw exactly once")
        gallery_by_id = {item["id"]: item for item in gallery_assets}
        for item in exact_report["figures"]:
            for field in ("source_pdf_sha256", "source_operator_sha256"):
                if not re.fullmatch(r"[0-9a-f]{64}", str(item.get(field, ""))):
                    errors.append(f"{item.get('id')}: {field} is missing or invalid")
            if gallery_by_id.get(item["id"], {}).get("source_operator_sha256") != item.get("source_operator_sha256"):
                errors.append(f"{item.get('id')}: gallery and pixel-exact operator hashes differ")
        for item in qa_report["figures"]:
            if float(item.get("aspect_ratio_error", 1.0)) > 0.01:
                errors.append(f"{item.get('id')}: tight content aspect-ratio error exceeds 1%")
            if float(item.get("cross_renderer_pixel_match_t32", 0.0)) < 0.80:
                errors.append(f"{item.get('id')}: cross-renderer pixel match falls below 80%")
            if float(item.get("semantic_layer_isolation_pixel_match", 0.0)) != 1.0:
                errors.append(f"{item.get('id')}: hidden semantic layer changes visible pixels")
    except (OSError, json.JSONDecodeError, KeyError, TypeError) as exc:
        errors.append(f"asset manifests are invalid: {exc}")
    return errors


def main() -> int:
    errors = validate()
    print(json.dumps({"valid": not errors, "errors": errors}, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
