#!/usr/bin/env python3
"""Build original/redraw/edge-overlay calibration plates for paper figures.

This is an optional review harness. The shipped editable SVGs remain dependency-free;
calibration additionally needs Pillow, Poppler's pdftoppm, Node.js, and sharp.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import urllib.request
from pathlib import Path

try:
    from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageOps
except ImportError as exc:  # pragma: no cover - exercised by users without QA extras
    raise SystemExit("Install the optional QA dependency with `python -m pip install Pillow`.") from exc


ROOT = Path(__file__).resolve().parents[1]
SOURCE_MANIFEST = ROOT / "references" / "paper-figure-sources.json"
DEFAULT_WORK = ROOT / "tmp" / "paper-calibration"
DEFAULT_OUTPUT = ROOT / "assets" / "comparisons"


def download(url: str, target: Path) -> None:
    if target.exists() and target.stat().st_size > 10_000:
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(url, headers={"User-Agent": "academic-figure-master/1.0"})
    with urllib.request.urlopen(request, timeout=90) as response, target.open("wb") as stream:
        shutil.copyfileobj(response, stream)


def render_page(pdf: Path, page: int, dpi: int, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    base = target.with_suffix("")
    subprocess.run(
        ["pdftoppm", "-png", "-r", str(dpi), "-f", str(page), "-l", str(page), "-singlefile", str(pdf), str(base)],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def crop_normalized(source: Path, box: list[float], target: Path) -> None:
    image = Image.open(source).convert("RGB")
    width, height = image.size
    pixels = (int(box[0] * width), int(box[1] * height), int(box[2] * width), int(box[3] * height))
    target.parent.mkdir(parents=True, exist_ok=True)
    image.crop(pixels).save(target)


def content_crop(image: Image.Image, threshold: int = 247) -> Image.Image:
    gray = image.convert("L")
    mask = gray.point(lambda value: 255 if value < threshold else 0)
    bounds = mask.getbbox()
    if not bounds:
        return image.copy()
    left, top, right, bottom = bounds
    pad = max(5, int(max(right - left, bottom - top) * 0.025))
    return image.crop((max(0, left - pad), max(0, top - pad), min(image.width, right + pad), min(image.height, bottom + pad)))


def fit(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    canvas = Image.new("RGB", size, "white")
    copy = content_crop(image.convert("RGB"))
    copy.thumbnail((size[0] - 36, size[1] - 36), Image.Resampling.LANCZOS)
    canvas.paste(copy, ((size[0] - copy.width) // 2, (size[1] - copy.height) // 2))
    return canvas


def edge_mask(image: Image.Image) -> Image.Image:
    gray = ImageOps.autocontrast(image.convert("L"))
    edges = gray.filter(ImageFilter.FIND_EDGES).filter(ImageFilter.MaxFilter(3))
    return edges.point(lambda value: 255 if value > 38 else 0)


def comparison_plate(original: Image.Image, redraw: Image.Image, label: str) -> tuple[Image.Image, dict[str, float]]:
    panel_size = (620, 390)
    left = fit(original, panel_size)
    middle = fit(redraw, panel_size)
    original_edges = edge_mask(left)
    redraw_edges = edge_mask(middle)
    overlay = Image.new("RGB", panel_size, "white")
    overlay.paste((215, 45, 106), mask=original_edges)
    overlay.paste((20, 150, 175), mask=redraw_edges)
    shared = ImageChops.multiply(original_edges, redraw_edges)
    overlay.paste((25, 25, 25), mask=shared)

    header = 54
    plate = Image.new("RGB", (panel_size[0] * 3, panel_size[1] + header), "white")
    draw = ImageDraw.Draw(plate)
    plate.paste(left, (0, header)); plate.paste(middle, (panel_size[0], header)); plate.paste(overlay, (panel_size[0] * 2, header))
    draw.text((16, 12), f"{label} · original source crop", fill="#111")
    draw.text((panel_size[0] + 16, 12), "editable SVG redraw", fill="#111")
    draw.text((panel_size[0] * 2 + 16, 12), "edge overlay · source magenta / redraw cyan / overlap black", fill="#111")
    draw.line((panel_size[0], 0, panel_size[0], plate.height), fill="#d0d0d0")
    draw.line((panel_size[0] * 2, 0, panel_size[0] * 2, plate.height), fill="#d0d0d0")

    source_crop = content_crop(original)
    redraw_crop = content_crop(redraw)
    source_ratio = source_crop.width / max(1, source_crop.height)
    redraw_ratio = redraw_crop.width / max(1, redraw_crop.height)
    intersection = shared.histogram()[255]
    union_mask = ImageChops.lighter(original_edges, redraw_edges)
    union = union_mask.histogram()[255]
    metrics = {
        "source_aspect_ratio": round(source_ratio, 4),
        "redraw_aspect_ratio": round(redraw_ratio, 4),
        "aspect_ratio_error": round(abs(source_ratio - redraw_ratio) / max(source_ratio, 1e-9), 4),
        "edge_iou": round(intersection / max(1, union), 4),
    }
    return plate, metrics


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", action="append", help="Calibrate one figure ID; repeat as needed.")
    parser.add_argument("--work-root", type=Path, default=DEFAULT_WORK)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--skip-download", action="store_true", help="Use PDFs already present in WORK_ROOT/pdfs.")
    parser.add_argument("--skip-svg-render", action="store_true", help="Use PNG redraws already present in WORK_ROOT/redraws.")
    parser.add_argument("--node", default="node")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))
    selected = set(args.only or [])
    figures = [item for item in manifest["figures"] if not selected or item["id"] in selected]
    if selected - {item["id"] for item in figures}:
        raise SystemExit(f"Unknown IDs: {', '.join(sorted(selected - {item['id'] for item in figures}))}")

    pdf_root = args.work_root / "pdfs"
    page_root = args.work_root / "pages"
    source_root = args.work_root / "sources"
    redraw_root = args.work_root / "redraws"
    for item in figures:
        pdf = pdf_root / f"{item['id']}.pdf"
        if not args.skip_download:
            download(item["url"], pdf)
        if not pdf.exists():
            raise SystemExit(f"Missing source PDF: {pdf}")
        page = page_root / f"{item['id']}.png"
        render_page(pdf, int(item["pdf_page"]), int(manifest["render_dpi"]), page)
        crop_normalized(page, item["crop_normalized"], source_root / f"{item['id']}.png")

    if not args.skip_svg_render:
        environment = os.environ.copy()
        subprocess.run([args.node, str(ROOT / "scripts" / "render_svgs.mjs"), str(ROOT / "assets" / "paper-redraws"), str(redraw_root)], check=True, env=environment)

    args.output_root.mkdir(parents=True, exist_ok=True)
    report = {"schema_version": 1, "method": "white-trimmed side-by-side review plus edge overlay", "figures": []}
    for item in figures:
        source = source_root / f"{item['id']}.png"
        redraw = redraw_root / f"{item['id']}.png"
        plate, metrics = comparison_plate(Image.open(source), Image.open(redraw), f"{item['paper']} · {item['figure']}")
        output = args.output_root / f"{item['id']}.png"
        plate.save(output, optimize=True)
        report["figures"].append({
            "id": item["id"], "paper": item["paper"], "figure": item["figure"], "source_url": item["url"],
            "source_sha256": sha256(source), "comparison": str(output.relative_to(ROOT)), **metrics,
        })
        print(output)
    (args.output_root / "qa-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
