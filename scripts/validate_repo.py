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

    primitive_dir = root / "assets" / "primitives"
    svgs = sorted(primitive_dir.glob("*.svg"))
    if len(svgs) < 6:
        errors.append("at least six starter SVG primitive sheets are required")
    for path in svgs:
        try:
            tree = ET.parse(path)
            svg = tree.getroot()
            if svg.tag != f"{SVG_NS}svg":
                errors.append(f"{path.name}: root is not SVG")
            if not svg.get("viewBox"):
                errors.append(f"{path.name}: viewBox is missing")
            ids: list[str] = []
            for element in svg.iter():
                local = element.tag.rsplit("}", 1)[-1]
                if local in {"image", "script", "foreignObject"}:
                    errors.append(f"{path.name}: forbidden <{local}> element")
                if element.get("id"):
                    ids.append(str(element.get("id")))
                for value in element.attrib.values():
                    if isinstance(value, str) and ("http://" in value or "https://" in value):
                        errors.append(f"{path.name}: external reference is not allowed")
            if len(ids) != len(set(ids)):
                errors.append(f"{path.name}: duplicate element ids")
            if not any(element.tag == f"{SVG_NS}g" and element.get("id") for element in svg.iter()):
                errors.append(f"{path.name}: no named editable groups")
        except (ET.ParseError, OSError) as exc:
            errors.append(f"{path.name}: invalid SVG: {exc}")
    return errors


def main() -> int:
    errors = validate()
    print(json.dumps({"valid": not errors, "errors": errors}, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
