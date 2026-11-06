#!/usr/bin/env python3
"""Inventory native PPTX objects, text and declared fonts; not a visual or PDF-font check."""
from __future__ import annotations
import argparse
import json
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

NS = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main", "p": "http://schemas.openxmlformats.org/presentationml/2006/main"}


def audit(path: Path, required_font: str | None = None) -> dict:
    if path.name.startswith("~$"):
        raise ValueError("Office lock files are not presentation packages")
    with zipfile.ZipFile(path) as archive:
        slides = sorted(n for n in archive.namelist() if re.fullmatch(r"ppt/slides/slide\d+\.xml", n))
        if not slides:
            raise ValueError("no slides found")
        all_fonts, result = set(), []
        for name in slides:
            root = ET.fromstring(archive.read(name))
            shapes = root.findall(".//p:sp", NS)
            texts = [s for s in shapes if s.findall(".//a:t", NS)]
            declared = {f.get("typeface") for f in root.findall(".//a:latin", NS) if f.get("typeface")}
            all_fonts.update(declared)
            implicit = []
            for shape in texts:
                if not shape.findall(".//a:latin", NS):
                    implicit.append("".join(shape.itertext()))
            result.append({"slide": name, "native_shapes": len(shapes), "text_objects": len(texts),
                           "pictures": len(root.findall(".//p:pic", NS)),
                           "connectors": len(root.findall(".//p:cxnSp", NS)),
                           "fonts_declared": sorted(declared), "text_objects_with_inherited_font": len(implicit)})
        issues = []
        if not any(s["text_objects"] for s in result):
            issues.append("no native text objects; check for a flattened figure")
        if required_font:
            other = all_fonts - {required_font}
            if required_font not in all_fonts:
                issues.append(f"required font not explicitly declared: {required_font}")
            if other:
                issues.append(f"other declared Latin typefaces need review: {', '.join(sorted(other))}")
            if any(s["text_objects_with_inherited_font"] for s in result):
                issues.append("some text inherits its font; resolve theme/style before asserting uniform typography")
        return {"file": str(path), "slides": result, "issues": issues,
                "scope": "OOXML structure and declarations only; inspect rendered PDF fonts and visual layout separately"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pptx", type=Path)
    parser.add_argument("--font")
    args = parser.parse_args()
    try:
        result = audit(args.pptx, args.font)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return int(bool(result["issues"]))
    except (OSError, ValueError, zipfile.BadZipFile, ET.ParseError) as exc:
        parser.exit(2, f"{exc}\n")

if __name__ == "__main__":
    raise SystemExit(main())
