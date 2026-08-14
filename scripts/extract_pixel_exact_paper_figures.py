#!/usr/bin/env python3
"""Extract exact paper Figure operators from source PDFs into tight editable SVGs.

The visible layer is copied from the PDF's own vector operators. Fonts are therefore
outlined as glyph paths when the PDF stores them that way. Raster operators in the
source Figure remain isolated, named, replaceable <image> components.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import shutil
import subprocess
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

try:
    from PIL import Image
except ImportError as exc:  # pragma: no cover
    raise SystemExit("Install the optional extraction dependency with `python -m pip install Pillow`.") from exc


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "references" / "paper-figure-sources.json"
DEFAULT_WORK = ROOT / "tmp" / "pixel-exact-extraction"
DEFAULT_OUTPUT = ROOT / "assets" / "paper-redraws"
SVG_NS = "http://www.w3.org/2000/svg"
XLINK_NS = "http://www.w3.org/1999/xlink"
ET.register_namespace("", SVG_NS)
ET.register_namespace("xlink", XLINK_NS)


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def element_sha256(*elements: ET.Element | None) -> str:
    digest = hashlib.sha256()
    for element in elements:
        if element is not None:
            digest.update(ET.tostring(element, encoding="utf-8"))
    return digest.hexdigest()


def download(url: str, target: Path) -> None:
    if target.exists() and target.stat().st_size > 10_000:
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(url, headers={"User-Agent": "academic-figure-master/1.0"})
    with urllib.request.urlopen(request, timeout=90) as response, target.open("wb") as stream:
        shutil.copyfileobj(response, stream)


def discover_pdftocairo(explicit: str | None) -> str:
    if explicit:
        return explicit
    environment = os.environ.get("PDFTOCAIRO")
    if environment:
        return environment
    direct = shutil.which("pdftocairo")
    if direct:
        return direct
    pdftoppm = shutil.which("pdftoppm")
    if pdftoppm:
        candidate = Path(pdftoppm).resolve().parents[2] / "native" / "poppler" / "poppler" / "bin" / "pdftocairo"
        if candidate.exists():
            return str(candidate)
    raise SystemExit("pdftocairo is required. Install Poppler or pass --pdftocairo /absolute/path.")


def run_pdf_vector_crop(pdftocairo: str, pdf: Path, item: dict[str, object], target: Path) -> None:
    box = [float(value) for value in item["crop_normalized"]]
    page_width, page_height = [float(value) for value in item.get("page_points", [612, 792])]
    left = round(box[0] * page_width)
    top = round(box[1] * page_height)
    width = max(1, round((box[2] - box[0]) * page_width))
    height = max(1, round((box[3] - box[1]) * page_height))
    target.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            pdftocairo, "-svg", "-r", "72", "-f", str(item["pdf_page"]), "-l", str(item["pdf_page"]),
            "-x", str(left), "-y", str(top), "-W", str(width), "-H", str(height), str(pdf), str(target),
        ],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def nonwhite_bbox(
    path: Path,
    viewbox: list[float],
    point_region: list[float] | None = None,
    threshold: int = 250,
) -> tuple[int, int, int, int]:
    image = Image.open(path).convert("L")
    if point_region is None:
        left, top, right, bottom = 0, 0, image.width, image.height
    else:
        scale_x = image.width / viewbox[2]
        scale_y = image.height / viewbox[3]
        left = max(0, round((point_region[0] - viewbox[0]) * scale_x))
        top = max(0, round((point_region[1] - viewbox[1]) * scale_y))
        right = min(image.width, round((point_region[2] - viewbox[0]) * scale_x))
        bottom = min(image.height, round((point_region[3] - viewbox[1]) * scale_y))
    search = image.crop((left, top, right, bottom))
    mask = search.point(lambda value: 255 if value < threshold else 0)
    local_bounds = mask.getbbox()
    bounds = None if local_bounds is None else (
        left + local_bounds[0], top + local_bounds[1], left + local_bounds[2], top + local_bounds[3]
    )
    if not bounds:
        raise RuntimeError(f"No visible operators found in {path}")
    return bounds


def add_operator_ids(group: ET.Element) -> dict[str, int]:
    counts: dict[str, int] = {}
    serial = 0
    for element in group.iter():
        kind = local_name(element.tag)
        if kind in {"g", "path", "use", "image", "rect", "circle", "line", "polyline", "polygon", "text"}:
            counts[kind] = counts.get(kind, 0) + 1
            if element is not group and not element.get("id"):
                serial += 1
                element.set("id", f"source-{kind}-{serial:04d}")
    return counts


def prefix_semantic_ids(root: ET.Element) -> None:
    mapping: dict[str, str] = {}
    for element in root.iter():
        identifier = element.get("id")
        if identifier and identifier != "semantic-edit-layer":
            mapping[identifier] = f"semantic-{identifier}"
    for element in root.iter():
        identifier = element.get("id")
        if identifier in mapping:
            element.set("id", mapping[identifier])
        for name, value in list(element.attrib.items()):
            updated = value
            for old, new in mapping.items():
                updated = updated.replace(f"url(#{old})", f"url(#{new})")
                if name.endswith("href") and updated == f"#{old}":
                    updated = f"#{new}"
            if name in {"aria-labelledby", "aria-describedby"}:
                updated = " ".join(mapping.get(token, token) for token in updated.split())
            if updated != value:
                element.set(name, updated)


def semantic_layer_from_existing(output: Path, target_box: tuple[float, float, float, float]) -> ET.Element | None:
    if not output.exists():
        return None
    existing = ET.parse(output).getroot()
    found = next((element for element in existing.iter() if element.get("id") == "semantic-edit-layer"), None)
    if found is not None:
        layer = copy.deepcopy(found)
    else:
        layer = copy.deepcopy(existing)
        layer.set("id", "semantic-edit-layer")
        layer.set("data-role", "editable-text-and-component-layer")
        prefix_semantic_ids(layer)
    x, y, width, height = target_box
    layer.set("x", f"{x:.4f}")
    layer.set("y", f"{y:.4f}")
    layer.set("width", f"{width:.4f}")
    layer.set("height", f"{height:.4f}")
    layer.set("preserveAspectRatio", "xMidYMid meet")
    layer.set("style", "display:none")
    return layer


def tighten_svg(raw_svg: Path, raw_png: Path, output: Path, item: dict[str, object], density: int) -> dict[str, object]:
    tree = ET.parse(raw_svg)
    root = tree.getroot()
    original_viewbox = [float(value) for value in root.get("viewBox", "0 0 612 792").split()]
    pixel_width, pixel_height = Image.open(raw_png).size
    scale_x = pixel_width / original_viewbox[2]
    scale_y = pixel_height / original_viewbox[3]
    trim_points = item.get("operator_trim_points")
    left, top, right, bottom = nonwhite_bbox(
        raw_png,
        original_viewbox,
        None if trim_points is None else [float(value) for value in trim_points],
    )
    pad = 1.25
    x = original_viewbox[0] + left / scale_x - pad
    y = original_viewbox[1] + top / scale_y - pad
    width = (right - left) / scale_x + 2 * pad
    height = (bottom - top) / scale_y + 2 * pad

    defs = next((child for child in root if local_name(child.tag) == "defs"), None)
    visible_children = [child for child in list(root) if child is not defs]
    for child in visible_children:
        root.remove(child)

    title = ET.Element(f"{{{SVG_NS}}}title", {"id": "svg-title"})
    title.text = f"{item['paper']} - {item['figure']}"
    description = ET.Element(f"{{{SVG_NS}}}desc", {"id": "svg-description"})
    description.text = "Pixel-exact source-vector extraction for review and editable reconstruction."
    metadata = ET.Element(f"{{{SVG_NS}}}metadata", {"id": "provenance"})
    metadata.text = json.dumps(
        {
            "reproduction": "pixel-exact-source-vector",
            "paper": item["paper"],
            "figure": item["figure"],
            "source_url": item["url"],
            "pdf_page": item["pdf_page"],
            "source_pdf_sha256": item["source_pdf_sha256"],
            "visible_text_mode": "source glyph outlines",
        },
        ensure_ascii=False,
        separators=(",", ":"),
    )
    operator_group = ET.Element(f"{{{SVG_NS}}}g", {"id": "source-vector-operators", "data-role": "pixel-exact-visible-layer"})
    for child in visible_children:
        operator_group.append(child)
    counts = add_operator_ids(operator_group)
    operator_sha = element_sha256(defs, operator_group)
    source_images = sum(
        1
        for container in (defs, operator_group)
        if container is not None
        for element in container.iter()
        if local_name(element.tag) == "image"
    )
    semantic_layer = semantic_layer_from_existing(output, (x, y, width, height))

    root.insert(1 if defs is not None else 0, title)
    root.insert(2 if defs is not None else 1, description)
    root.insert(3 if defs is not None else 2, metadata)
    root.append(operator_group)
    if semantic_layer is not None:
        root.append(semantic_layer)
    root.set("width", f"{width:.4f}pt")
    root.set("height", f"{height:.4f}pt")
    root.set("viewBox", f"{x:.4f} {y:.4f} {width:.4f} {height:.4f}")
    root.set("role", "img")
    root.set("aria-labelledby", "svg-title svg-description")
    root.set("data-fidelity", "pixel-exact-source-vector")
    output.parent.mkdir(parents=True, exist_ok=True)
    tree.write(output, encoding="utf-8", xml_declaration=True)
    return {
        "viewBox": [round(x, 4), round(y, 4), round(width, 4), round(height, 4)],
        "operator_counts": counts,
        "source_operator_sha256": operator_sha,
        "embedded_raster_components": source_images,
        "visible_text_mode": "source glyph outlines",
        "semantic_edit_layer": semantic_layer is not None,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", action="append", help="Extract one figure ID; repeat as needed.")
    parser.add_argument("--work-root", type=Path, default=DEFAULT_WORK)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--skip-download", action="store_true")
    parser.add_argument("--pdftocairo")
    parser.add_argument("--node", default="node")
    parser.add_argument("--density", type=int, default=72)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    selected = set(args.only or [])
    figures = [item for item in manifest["figures"] if not selected or item["id"] in selected]
    known = {item["id"] for item in manifest["figures"]}
    if selected - known:
        raise SystemExit(f"Unknown IDs: {', '.join(sorted(selected - known))}")
    pdftocairo = discover_pdftocairo(args.pdftocairo)
    pdf_root = args.work_root / "pdfs"
    raw_root = args.work_root / "raw-svg"
    raw_render_root = args.work_root / "raw-renders"

    for item in figures:
        pdf = pdf_root / f"{item['id']}.pdf"
        if not args.skip_download:
            download(str(item["url"]), pdf)
        if not pdf.exists():
            raise SystemExit(f"Missing source PDF: {pdf}")
        item["source_pdf_sha256"] = sha256(pdf)
        run_pdf_vector_crop(pdftocairo, pdf, item, raw_root / f"{item['id']}.svg")

    subprocess.run(
        [args.node, str(ROOT / "scripts" / "render_svgs.mjs"), str(raw_root), str(raw_render_root), str(args.density)],
        check=True,
    )
    records=[]
    for item in figures:
        record = tighten_svg(
            raw_root / f"{item['id']}.svg", raw_render_root / f"{item['id']}.png",
            args.output_root / f"{item['id']}.svg", item, args.density,
        )
        records.append({
            "id": item["id"],
            "paper": item["paper"],
            "figure": item["figure"],
            "source_url": item["url"],
            "source_pdf_sha256": item["source_pdf_sha256"],
            **record,
        })
        print(args.output_root / f"{item['id']}.svg")
    report = {"schema_version": 2, "method": "pdftocairo source-operator extraction with tight content viewBox and hidden semantic edit layer", "figures": records}
    report_path = args.output_root / "pixel-exact-manifest.json"
    if selected and report_path.exists():
        previous = json.loads(report_path.read_text(encoding="utf-8"))
        combined = {item["id"]: item for item in previous.get("figures", [])}
        combined.update({item["id"]: item for item in records})
        order = [item["id"] for item in manifest["figures"]]
        report["figures"] = [combined[identifier] for identifier in order if identifier in combined]
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
