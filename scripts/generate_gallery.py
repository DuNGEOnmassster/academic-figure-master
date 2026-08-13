#!/usr/bin/env python3
"""Generate the editable SVG asset and classic-paper gallery without dependencies."""

from __future__ import annotations

import argparse
import html
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ASSET_ROOT = ROOT / "assets"


@dataclass(frozen=True)
class Asset:
    slug: str
    title: str
    category: str
    tags: tuple[str, ...]
    renderer: Callable[[], str]
    reproduction: str = "original"
    source_title: str | None = None
    source_url: str | None = None
    source_figure: str | None = None
    note: str = "Original editable SVG authored for academic-figure-master."

    @property
    def relative_path(self) -> str:
        folder = {"primitive": "primitives", "paper": "paper-redraws", "curve": "curves"}[self.category]
        return f"{folder}/{self.slug}.svg"


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def text(x: float, y: float, value: object, css: str = "label", anchor: str = "middle", extra: str = "") -> str:
    return f'<text x="{x:g}" y="{y:g}" class="{css}" text-anchor="{anchor}" {extra}>{esc(value)}</text>'


def line(x1: float, y1: float, x2: float, y2: float, css: str = "wire", extra: str = "") -> str:
    return f'<line x1="{x1:g}" y1="{y1:g}" x2="{x2:g}" y2="{y2:g}" class="{css}" {extra}/>'


def path(d: str, css: str = "wire", extra: str = "") -> str:
    return f'<path d="{d}" class="{css}" {extra}/>'


def circle(cx: float, cy: float, r: float, css: str = "node", extra: str = "") -> str:
    return f'<circle cx="{cx:g}" cy="{cy:g}" r="{r:g}" class="{css}" {extra}/>'


def group(group_id: str, body: Iterable[str], extra: str = "") -> str:
    return f'<g id="{esc(group_id)}" {extra}>\n' + "\n".join(body) + "\n</g>"


def box(
    group_id: str,
    x: float,
    y: float,
    w: float,
    h: float,
    label: str,
    sub: str = "",
    tone: str = "blue",
    rx: float = 18,
    label_css: str = "label strong",
) -> str:
    parts = [f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" rx="{rx:g}" class="card {tone}"/>']
    label_y = y + h / 2 - (7 if sub else -6)
    parts.append(text(x + w / 2, label_y, label, label_css))
    if sub:
        parts.append(text(x + w / 2, label_y + 28, sub, "small muted"))
    return group(group_id, parts)


def arrow(
    arrow_id: str,
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    label: str = "",
    css: str = "wire",
    bend: float = 0,
    marker: str = "arrow",
) -> str:
    if bend:
        cx = (x1 + x2) / 2
        cy = (y1 + y2) / 2 + bend
        element = path(f"M{x1:g},{y1:g} Q{cx:g},{cy:g} {x2:g},{y2:g}", css, f'marker-end="url(#{marker})"')
        label_y = cy - 10 if bend < 0 else cy + 24
    else:
        element = line(x1, y1, x2, y2, css, f'marker-end="url(#{marker})"')
        label_y = (y1 + y2) / 2 - 12
    parts = [element]
    if label:
        parts.append(text((x1 + x2) / 2, label_y, label, "tiny muted"))
    return group(arrow_id, parts)


def stack(group_id: str, x: float, y: float, w: float, h: float, count: int, tone: str, label: str) -> str:
    parts: list[str] = []
    for index in reversed(range(count)):
        dx = index * 9
        dy = -index * 9
        parts.append(f'<rect x="{x+dx:g}" y="{y+dy:g}" width="{w:g}" height="{h:g}" rx="12" class="card {tone}" opacity="{1-index*0.09:.2f}"/>')
    parts.append(text(x + w / 2, y + h / 2 + 6, label, "label strong"))
    return group(group_id, parts)


def svg(title: str, subtitle: str, body: Iterable[str], width: int = 1200, height: int = 600, metadata: str = "") -> str:
    styles = """
    .bg{fill:#fbfcff}.title{font:700 30px Inter,Arial,sans-serif;fill:#17233b}.subtitle{font:400 15px Inter,Arial,sans-serif;fill:#66758f}
    .label{font:500 19px Inter,Arial,sans-serif;fill:#263550}.strong{font-weight:700}.small{font:500 15px Inter,Arial,sans-serif}.tiny{font:500 13px Inter,Arial,sans-serif}.muted{fill:#66758f}
    .card{stroke-width:2.5}.blue{fill:#eaf2ff;stroke:#3972d5}.violet{fill:#f1edff;stroke:#7354cf}.red{fill:#fff0f0;stroke:#dc5963}.gold{fill:#fff7e6;stroke:#d3a23f}.green{fill:#eaf8f2;stroke:#38a479}.slate{fill:#f2f5f9;stroke:#72819a}.cyan{fill:#e9f9fb;stroke:#2b9aa5}
    .wire{fill:none;stroke:#34445f;stroke-width:3.5;stroke-linecap:round;stroke-linejoin:round}.wire2{fill:none;stroke:#3972d5;stroke-width:5;stroke-linecap:round;stroke-linejoin:round}.violet-line{fill:none;stroke:#7354cf;stroke-width:5;stroke-linecap:round;stroke-linejoin:round}.red-line{fill:none;stroke:#dc5963;stroke-width:5;stroke-linecap:round;stroke-linejoin:round}.green-line{fill:none;stroke:#38a479;stroke-width:5;stroke-linecap:round;stroke-linejoin:round}.dash{stroke-dasharray:10 9}
    .axis{fill:none;stroke:#8b98ac;stroke-width:2}.grid{stroke:#dce3ed;stroke-width:1.5}.node{fill:#fff;stroke:#34445f;stroke-width:3}.dot-blue{fill:#3972d5}.dot-violet{fill:#7354cf}.dot-red{fill:#dc5963}.dot-green{fill:#38a479}.paper-note{font:600 12px Inter,Arial,sans-serif;fill:#7354cf;letter-spacing:.06em}
    """
    meta = f"<metadata>{esc(metadata)}</metadata>" if metadata else ""
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="svg-title svg-desc">
  <title id="svg-title">{esc(title)}</title><desc id="svg-desc">{esc(subtitle)}</desc>{meta}
  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M0 0L10 5L0 10Z" fill="#34445f"/></marker>
    <marker id="arrow-blue" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M0 0L10 5L0 10Z" fill="#3972d5"/></marker>
    <marker id="arrow-violet" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M0 0L10 5L0 10Z" fill="#7354cf"/></marker>
    <linearGradient id="soft-gradient" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#eaf2ff"/><stop offset="1" stop-color="#f1edff"/></linearGradient>
    <style>{styles}</style>
  </defs>
  <rect class="bg" width="{width}" height="{height}"/>
  <g id="figure-body" transform="translate(0,-65)">{''.join(body)}</g>
</svg>
'''


def paper_svg(title: str, description: str, body: Iterable[str], width: int, height: int, metadata: str) -> str:
    """Tight, publication-style canvas used by source-faithful paper redraws."""
    styles = """
    .sans{font-family:Arial,Helvetica,sans-serif;fill:#111}.serif{font-family:'Times New Roman',Times,serif;fill:#111}
    .t9{font-size:9px}.t10{font-size:10px}.t11{font-size:11px}.t12{font-size:12px}.t13{font-size:13px}.t14{font-size:14px}.t16{font-size:16px}
    .bold{font-weight:700}.italic{font-style:italic}.thin{fill:none;stroke:#111;stroke-width:1}.mid{fill:none;stroke:#111;stroke-width:1.5}
    .thick{fill:none;stroke:#111;stroke-width:2}.gray{fill:#d7d7d7;stroke:#333;stroke-width:1}.light{fill:#f5f5f5;stroke:#111;stroke-width:1}
    .blue{fill:#dbe9f6;stroke:#386a98;stroke-width:1}.green{fill:#dcebc8;stroke:#4e7a35;stroke-width:1}.yellow{fill:#f4e7a7;stroke:#826f24;stroke-width:1}
    .orange{fill:#f4d0a3;stroke:#925c22;stroke-width:1}.pink{fill:#f2cdd0;stroke:#9b4b52;stroke-width:1}.violet{fill:#ddd4ed;stroke:#665283;stroke-width:1}
    .cyan-stroke{fill:none;stroke:#42a3b8;stroke-width:1.5}.green-stroke{fill:none;stroke:#5a9e55;stroke-width:1.5}.black-dash{fill:none;stroke:#111;stroke-width:1.5;stroke-dasharray:3 3}
    """
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="svg-title svg-desc">
  <title id="svg-title">{esc(title)}</title><desc id="svg-desc">{esc(description)}</desc><metadata>{esc(metadata)}</metadata>
  <defs>
    <marker id="paper-arrow" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0 0L10 5L0 10Z" fill="#111"/></marker>
    <marker id="paper-arrow-gray" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0 0L10 5L0 10Z" fill="#777"/></marker>
    <style>{styles}</style>
  </defs>
  <rect width="{width}" height="{height}" fill="#fff"/>
  {''.join(body)}
</svg>
'''


def primitive_attention_heads() -> str:
    parts = [stack("query-tokens", 70, 245, 125, 160, 3, "blue", "Q")]
    colors = ["blue", "violet", "red", "green"]
    parts += [arrow("query-to-head-bus", 205, 320, 275, 320), line(275, 320, 870, 320, "axis")]
    for i, tone in enumerate(colors):
        x = 300 + i * 150
        parts.append(box(f"head-{i+1}", x, 205, 112, 95, f"Head {i+1}", "QKᵀ / √d", tone))
        parts.append(arrow(f"query-to-head-{i+1}", x + 56, 320, x + 56, 300, css="wire"))
        parts.append(box(f"value-{i+1}", x, 365, 112, 75, "softmax · V", tone, label_css="small strong"))
        parts.append(arrow(f"head-to-value-{i+1}", x + 56, 300, x + 56, 365))
    parts += [box("concat", 930, 255, 150, 95, "Concat", "project Wᴼ", "gold"), arrow("heads-to-concat", 870, 330, 930, 305)]
    return svg("Multi-head attention", "Editable heads, projections, and aggregation", parts)


def primitive_convolution_pyramid() -> str:
    parts: list[str] = []
    layers = [(70, 225, 190, 235, "Input", "224 × 224 × 3", "blue"), (330, 250, 155, 185, "Conv", "112 × 112 × 64", "cyan"), (555, 275, 125, 135, "Conv", "56 × 56 × 128", "violet"), (750, 295, 100, 95, "Conv", "28 × 28 × 256", "red"), (930, 310, 145, 65, "Pool", "1 × 1 × 256", "gold")]
    for i, (x, y, w, h, label, sub, tone) in enumerate(layers):
        parts.append(stack(f"feature-stage-{i}", x, y, w, h, 3 if i < 4 else 1, tone, label))
        parts.append(text(x + w / 2, y + h + 36, sub, "small muted"))
        if i:
            px, py, pw, ph, *_ = layers[i - 1]
            parts.append(arrow(f"stage-arrow-{i}", px + pw + 28, py + ph / 2, x - 10, y + h / 2))
    return svg("Convolutional feature pyramid", "Progressive spatial compression and channel expansion", parts)


def primitive_graph_message_passing() -> str:
    positions = [(170, 320), (310, 200), (340, 430), (510, 300), (650, 180), (690, 420)]
    edges = [(0, 1), (0, 2), (1, 3), (2, 3), (3, 4), (3, 5), (4, 5)]
    parts = [group("graph-edges", [line(*positions[a], *positions[b], "axis") for a, b in edges])]
    parts.append(group("graph-nodes", [circle(x, y, 27, "node") + text(x, y + 7, f"h{i}", "small strong") for i, (x, y) in enumerate(positions)]))
    parts += [arrow("messages", 370, 270, 485, 295, "aggregate", "violet-line", marker="arrow-violet"), box("aggregator", 790, 235, 230, 130, "AGGREGATE", "Σ / mean / attention", "violet"), arrow("update-arrow", 1020, 300, 1100, 300), circle(1135, 300, 32, "node") + text(1135, 307, "h′ᵥ", "small strong")]
    return svg("Graph message passing", "Neighborhood messages, aggregation, and node update", parts)


def primitive_causal_dag() -> str:
    nodes = {"X": (170, 260, "blue"), "Z": (390, 180, "violet"), "M": (600, 330, "gold"), "Y": (850, 250, "red"), "U": (390, 440, "slate")}
    parts = [group("causal-nodes", [circle(x, y, 42, f"card {tone}") + text(x, y + 7, name, "label strong") for name, (x, y, tone) in nodes.items()])]
    edges = [("X", "Z", ""), ("Z", "Y", "confounder path"), ("X", "M", "mediated"), ("M", "Y", ""), ("U", "X", "latent"), ("U", "Y", "")]
    for idx, (a, b, label_) in enumerate(edges):
        x1, y1, _ = nodes[a]; x2, y2, _ = nodes[b]
        parts.append(arrow(f"causal-edge-{idx}", x1 + 42, y1, x2 - 42, y2, label_))
    parts += [box("intervention", 965, 410, 170, 85, "do(X = x)", "intervention", "green"), path("M170,218 L170,135 L1045,135 L1045,410", "green-line dash", 'marker-end="url(#arrow)"')]
    return svg("Causal DAG", "Confounding, mediation, latent variables, and intervention", parts)


def primitive_optimization_landscape() -> str:
    contour_paths = ["M130,460 C220,280 390,230 520,330 C640,430 760,410 900,240", "M180,480 C270,335 400,300 510,370 C620,445 760,445 960,270", "M250,500 C340,410 430,385 520,425 C630,475 770,480 1020,330"]
    parts = [group("loss-contours", [path(d, "axis") for d in contour_paths])]
    trajectory = [(160, 500), (250, 390), (360, 350), (470, 405), (580, 430), (690, 405), (790, 350), (875, 285)]
    d = "M" + " L".join(f"{x},{y}" for x, y in trajectory)
    parts += [group("optimizer-path", [path(d, "violet-line", 'marker-end="url(#arrow-violet)"')] + [circle(x, y, 6, "dot-violet") for x, y in trajectory]), circle(900, 255, 18, "dot-red"), text(930, 260, "local minimum", "small muted", "start"), text(145, 535, "θ₀", "small strong")]
    return svg("Optimization landscape", "Editable contours, iterates, and convergence annotation", parts)


def primitive_uncertainty_bands() -> str:
    parts = [line(115, 530, 1080, 530, "axis"), line(115, 530, 115, 145, "axis")]
    parts += [text(600, 585, "input / time", "small muted"), text(45, 330, "prediction", "small muted", extra='transform="rotate(-90 45 330)"')]
    upper = "M130,405 C300,210 500,175 680,250 C830,315 940,230 1060,180"
    lower = "L1060,360 C930,390 830,420 680,390 C500,340 300,470 130,500 Z"
    parts += [group("confidence-band", [path(upper + " " + lower, extra='fill="#7354cf" fill-opacity=".14" stroke="none"')]), path("M130,450 C300,280 500,240 680,315 C830,370 940,300 1060,260", "violet-line"), group("observations", [circle(x, y, 7, "dot-blue") for x, y in [(170,440),(260,340),(345,310),(455,255),(570,295),(700,330),(820,350),(930,295),(1030,250)]])]
    return svg("Predictive uncertainty", "Mean prediction, confidence band, and observations", parts)


def primitive_dataset_pipeline() -> str:
    stages = [(55, "Raw data", "files + records", "slate"), (285, "Validate", "schema + leakage", "blue"), (515, "Transform", "clean + augment", "violet"), (745, "Split", "train / val / test", "gold"), (975, "Version", "manifest + hash", "green")]
    parts = []
    for i, (x, label_, sub, tone) in enumerate(stages):
        parts.append(box(f"pipeline-stage-{i}", x, 260, 170, 115, label_, sub, tone))
        if i:
            parts.append(arrow(f"pipeline-arrow-{i}", stages[i-1][0] + 170, 318, x, 318))
    parts += [path("M600,375 L600,495 L370,495", "red-line dash", 'marker-end="url(#arrow)"'), text(485, 525, "failed checks return to transform", "small muted")]
    return svg("Dataset preparation pipeline", "Quality gates, transforms, splits, and versioning", parts)


def primitive_training_loop() -> str:
    nodes = [(190, 330, "Batch", "x, y", "blue"), (430, 190, "Forward", "ŷ = fθ(x)", "violet"), (710, 190, "Loss", "L(ŷ, y)", "red"), (930, 330, "Backward", "∇θL", "gold"), (710, 470, "Update", "θ ← θ − ηg", "green"), (430, 470, "Evaluate", "metrics", "cyan")]
    parts = [box(f"loop-node-{i}", x-80, y-50, 160, 100, a, b, tone) for i, (x, y, a, b, tone) in enumerate(nodes)]
    for i in range(len(nodes)):
        x1, y1, *_ = nodes[i]; x2, y2, *_ = nodes[(i+1)%len(nodes)]
        parts.append(arrow(f"loop-edge-{i}", x1+55 if x2>x1 else x1-55, y1, x2-55 if x2>x1 else x2+55, y2, bend=-25 if i in {0,1,2} else 25))
    parts.append(text(600, 338, "repeat until convergence", "label strong"))
    return svg("Training and evaluation loop", "Forward pass, loss, gradients, update, and validation", parts)


def primitive_ensemble_voting() -> str:
    parts = [box("input", 55, 275, 150, 100, "Input", "x", "slate")]
    tones = ["blue", "violet", "green"]
    ys = [165, 290, 415]
    for i, (tone, y) in enumerate(zip(tones, ys), 1):
        parts += [box(f"model-{i}", 325, y, 190, 90, f"Model {i}", f"p{i}(y|x)", tone), arrow(f"input-model-{i}", 205, 325, 325, y+45, bend=(y-290)/4)]
    parts += [box("aggregator", 675, 255, 190, 140, "Aggregate", "mean / vote / stack", "gold")]
    for i, y in enumerate(ys, 1):
        parts.append(arrow(f"model-aggregate-{i}", 515, y+45, 675, 325, bend=(290-y)/4))
    parts += [arrow("aggregate-output", 865, 325, 980, 325), box("prediction", 980, 275, 165, 100, "Prediction", "ŷ + uncertainty", "red")]
    return svg("Model ensemble", "Parallel predictors, aggregation, and calibrated output", parts)


def primitive_bayesian_inference() -> str:
    parts = [box("prior", 70, 255, 190, 120, "Prior", "p(θ)", "violet"), box("likelihood", 385, 255, 190, 120, "Likelihood", "p(D | θ)", "blue"), box("posterior", 700, 230, 220, 170, "Posterior", "p(θ | D)", "green"), box("predictive", 1000, 255, 160, 120, "Predict", "p(y* | x*, D)", "gold")]
    parts += [arrow("prior-likelihood", 260, 315, 385, 315, "×"), arrow("likelihood-posterior", 575, 315, 700, 315, "normalize"), arrow("posterior-predictive", 920, 315, 1000, 315, "integrate")]
    parts += [path("M800,400 C800,510 480,520 480,375", "violet-line dash", 'marker-end="url(#arrow-violet)"'), text(650, 550, "posterior predictive checking", "small muted")]
    return svg("Bayesian inference", "Prior, likelihood, posterior, and predictive distribution", parts)


def primitive_multimodal_fusion() -> str:
    inputs = [(70, 155, "Image", "patches", "blue"), (70, 290, "Text", "tokens", "violet"), (70, 425, "Audio", "frames", "green")]
    parts = []
    for i, (x, y, a, b, tone) in enumerate(inputs):
        parts += [box(f"modality-{i}", x, y, 160, 90, a, b, tone), arrow(f"modality-encoder-{i}", 230, y+45, 360, y+45), box(f"encoder-{i}", 360, y, 170, 90, "Encoder", f"z{i+1}", tone)]
    parts += [box("fusion", 675, 245, 220, 170, "Fusion", "cross-attention", "gold")]
    for i, (_, y, *_rest) in enumerate(inputs):
        parts.append(arrow(f"encoder-fusion-{i}", 530, y+45, 675, 330, bend=(290-y)/5))
    parts += [arrow("fusion-head", 895, 330, 1005, 330), box("task-head", 1005, 270, 155, 120, "Task head", "predict / generate", "red")]
    return svg("Multimodal fusion", "Separate encoders, shared fusion, and task head", parts)


def primitive_ablation_matrix() -> str:
    parts = [text(105, 150, "Component", "small strong", "start"), text(460, 150, "Variant A", "small strong"), text(650, 150, "Variant B", "small strong"), text(840, 150, "Variant C", "small strong"), text(1040, 150, "Δ metric", "small strong")]
    rows = [("Augmentation", [1,1,0], "+2.4"), ("Residual", [1,0,1], "+1.7"), ("Pretraining", [0,1,1], "+5.9"), ("Calibration", [0,0,1], "+0.8")]
    for r, (name, vals, delta) in enumerate(rows):
        y = 215 + r*88
        parts += [f'<rect x="70" y="{y-38}" width="1070" height="66" rx="14" class="card slate" opacity=".55"/>', text(105, y+4, name, "small", "start")]
        for c, value in enumerate(vals):
            x = 460 + c*190
            parts.append(circle(x, y, 16, "dot-green" if value else "node") + text(x, y+6, "✓" if value else "—", "small strong"))
        parts.append(text(1040, y+5, delta, "small strong"))
    return svg("Ablation matrix", "Editable experiment variants and metric deltas", parts)


def paper_lenet() -> str:
    def planes(gid: str, x: int, y: int, w: int, h: int, count: int) -> str:
        shapes=[]
        for i in reversed(range(count)):
            shapes.append(f'<rect x="{x+i*8}" y="{y-i*6}" width="{w}" height="{h}" fill="#b8b8b8" stroke="#555" stroke-width=".8"/>')
        return group(gid, shapes)
    parts=[
        group("input-image", ['<rect x="20" y="84" width="92" height="92" fill="#cfcfcf"/>','<path d="M42 151 L73 98 L73 174 M42 151 H100" fill="none" stroke="#111" stroke-width="5" stroke-linecap="round"/>']),
        planes("c1-feature-maps",150,70,62,92,6), planes("s2-feature-maps",285,84,56,68,6),
        planes("c3-feature-maps",420,58,50,86,7), planes("s4-feature-maps",560,79,45,58,7),
        planes("c5-layer",700,86,29,46,5), planes("f6-layer",800,87,27,44,4), planes("output-layer",900,92,22,34,3),
    ]
    labels=[(66,"INPUT","32×32"),(185,"C1: f. maps","6@28×28"),(315,"S2: f. maps","6@14×14"),(460,"C3: f. maps","16@10×10"),(595,"S4: f. maps","16@5×5"),(720,"C5: layer","120"),(818,"F6: layer","84"),(913,"OUTPUT","10")]
    parts.append(group("layer-labels",[f'<text x="{x}" y="22" class="sans t11" text-anchor="middle">{a}</text><text x="{x}" y="36" class="sans t10" text-anchor="middle">{b}</text>' for x,a,b in labels]))
    anchors=[(112,130),(160,118),(212,118),(285,118),(341,118),(420,105),(478,105),(560,108),(616,108),(700,109),(745,109),(800,109),(838,109),(900,109)]
    parts.append(group("connections",[f'<path d="M{a},{b} L{c},{d}" class="thin"/>' for (a,b),(c,d) in zip(anchors[::2],anchors[1::2])]))
    # Fan-out lines are separate editable objects, matching the original architecture sketch.
    fans=[]
    for x1,y1,x2,y2 in [(112,130,160,92),(112,130,160,150),(212,118,285,94),(212,118,285,146),(341,118,420,76),(341,118,420,140),(478,105,560,87),(478,105,560,132),(616,108,700,91),(616,108,700,128),(745,109,800,91),(745,109,800,128),(838,109,900,94),(838,109,900,124)]:
        fans.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="thin"/>')
    parts.append(group("connection-fans",fans))
    parts.append(group("operation-labels",[
        '<text x="184" y="214" class="sans t11" text-anchor="middle">Convolutions</text>',
        '<text x="318" y="214" class="sans t11" text-anchor="middle">Subsampling</text>',
        '<text x="458" y="214" class="sans t11" text-anchor="middle">Convolutions</text>',
        '<text x="594" y="214" class="sans t11" text-anchor="middle">Subsampling</text>',
        '<text x="718" y="202" class="sans t11" text-anchor="middle">Full Connection</text>',
        '<text x="820" y="214" class="sans t11" text-anchor="middle">Full Connection</text>',
        '<text x="914" y="202" class="sans t11" text-anchor="middle">Gaussian connections</text>',
    ]))
    return paper_svg("LeNet-5 architecture", "Editable reconstruction of LeCun et al. (1998), Figure 2.",[group("lenet-content",parts,'transform="scale(1,1.18)"')],960,280,"Source-faithful redraw; source paper Figure 2; no embedded raster.")


def paper_alexnet() -> str:
    def twin(gid: str,x: int,y: int,w: int,h: int,depth: int=3) -> str:
        shapes=[]
        for row in (0,1):
            cy=y+row*(h+22)
            for i in reversed(range(depth)):
                shapes.append(f'<rect x="{x+i*5}" y="{cy-i*4}" width="{w}" height="{h}" fill="#fff" stroke="#111" stroke-width=".8"/>')
        return group(gid,shapes)
    parts=[
        group("input",['<polygon points="18,51 55,28 55,248 18,225" fill="#eee" stroke="#111"/>','<path d="M25 93 L49 78 M25 116 L49 101 M25 139 L49 124" class="thin"/>']),
        twin("conv1",92,38,70,82), twin("conv2",228,50,75,67), twin("conv3",370,58,80,58), twin("conv4",500,58,80,58), twin("conv5",630,58,80,58),
        twin("fc6",765,65,26,50,1), twin("fc7",845,65,26,50,1), twin("fc8",930,76,14,38,1),
    ]
    # Connections reproduce the split-GPU topology shown in the published diagram.
    con=[]
    centers=[(55,86,92,78),(55,202,92,180),(162,78,228,82),(162,180,228,182),(303,82,370,86),(303,182,370,186),(450,86,500,86),(450,186,500,186),(580,86,630,86),(580,186,630,186),(710,86,765,87),(710,186,765,187),(791,87,845,87),(791,187,845,187),(871,87,930,93),(871,187,930,193)]
    for i,(x1,y1,x2,y2) in enumerate(centers):
        con.append(f'<line id="alexnet-link-{i}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="thin"/>')
    for i,(x1,y1,x2,y2) in enumerate([(162,78,228,182),(162,180,228,82),(303,82,370,186),(303,182,370,86),(710,86,765,187),(710,186,765,87)]):
        con.append(f'<line id="alexnet-cross-link-{i}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="thin" stroke-dasharray="2 2"/>')
    parts.append(group("network-connections",con))
    nums=[(35,266,"224"),(113,267,"55"),(251,267,"27"),(394,267,"13"),(524,267,"13"),(654,267,"13"),(777,267,"2048"),(857,267,"2048"),(937,267,"1000")]
    parts.append(group("neuron-counts",[f'<text x="{x}" y="{y}" class="sans t9" text-anchor="middle">{v}</text>' for x,y,v in nums]))
    parts.append(group("filter-labels",[
        '<text x="71" y="145" class="sans t9" text-anchor="middle">11</text><text x="75" y="158" class="sans t9">4</text>',
        '<text x="194" y="145" class="sans t9" text-anchor="middle">5</text>',
        '<text x="336" y="145" class="sans t9" text-anchor="middle">3</text>',
        '<text x="475" y="145" class="sans t9" text-anchor="middle">3</text>',
        '<text x="605" y="145" class="sans t9" text-anchor="middle">3</text>',
        '<text x="116" y="287" class="sans t9" text-anchor="middle">Stride 4</text>',
        '<text x="260" y="287" class="sans t9" text-anchor="middle">Max pooling</text>',
        '<text x="401" y="287" class="sans t9" text-anchor="middle">Max pooling</text>',
        '<text x="668" y="287" class="sans t9" text-anchor="middle">Max pooling</text>',
        '<text x="777" y="287" class="sans t9" text-anchor="middle">dense</text><text x="857" y="287" class="sans t9" text-anchor="middle">dense</text>',
    ]))
    return paper_svg("AlexNet architecture", "Editable reconstruction of Krizhevsky et al. (2012), Figure 2.",[group("alexnet-content",parts,'transform="scale(1,1.1)"')],975,330,"Source-faithful redraw; source paper Figure 2; split-GPU topology preserved.")


def paper_vae() -> str:
    parts=[
        group("plate",['<rect x="82" y="28" width="122" height="210" rx="9" class="light"/>','<text x="185" y="224" class="serif t16 italic">N</text>']),
        group("latent-z",['<circle cx="143" cy="91" r="28" fill="#fff" stroke="#111" stroke-width="1.5"/>','<text x="143" y="99" class="serif t16 italic" text-anchor="middle">z</text>']),
        group("observed-x",['<circle cx="143" cy="190" r="28" fill="#ddd" stroke="#111" stroke-width="1.5"/>','<text x="143" y="198" class="serif t16 italic" text-anchor="middle">x</text>']),
        group("generative-model",[
            '<line x1="143" y1="119" x2="143" y2="135" class="mid" marker-end="url(#paper-arrow)"/>',
            '<path d="M248 63 L174 84" class="mid" marker-end="url(#paper-arrow)"/>',
            '<path d="M248 63 L169 172" class="mid" marker-end="url(#paper-arrow)"/>',
            '<text x="260" y="61" class="serif t16 italic">θ</text>',
        ]),
        group("recognition-model",[
            '<path d="M116 177 C82 151 88 116 116 101" class="black-dash" marker-end="url(#paper-arrow)"/>',
            '<path d="M31 75 L114 87" class="black-dash" marker-end="url(#paper-arrow)"/>',
            '<text x="14" y="78" class="serif t16 italic">φ</text>',
        ]),
    ]
    return paper_svg("Variational graphical model", "Editable reconstruction of Kingma and Welling (2013), Figure 1.",[group("vae-content",parts,'transform="scale(.82,1)"')],235,255,"Source-faithful redraw; source paper Figure 1; solid generative and dashed recognition edges.")


def paper_gan() -> str:
    parts=[]
    for idx,x0 in enumerate((18,242,466,690)):
        curves=[
            (f'M{x0+10} 91 C{x0+28} 91 {x0+38} 31 {x0+69} 31 C{x0+98} 31 {x0+105} 91 {x0+125} 91',f'M{x0+77} 91 C{x0+98} 91 {x0+104} 47 {x0+127} 47 C{x0+152} 47 {x0+158} 91 {x0+181} 91'),
            (f'M{x0+13} 91 C{x0+36} 91 {x0+50} 30 {x0+82} 30 C{x0+109} 30 {x0+115} 91 {x0+132} 91',f'M{x0+76} 91 C{x0+99} 91 {x0+104} 44 {x0+129} 44 C{x0+152} 44 {x0+161} 91 {x0+181} 91'),
            (f'M{x0+12} 91 C{x0+39} 91 {x0+54} 27 {x0+88} 27 C{x0+116} 27 {x0+123} 91 {x0+144} 91',f'M{x0+54} 91 C{x0+77} 91 {x0+87} 44 {x0+111} 44 C{x0+137} 44 {x0+145} 91 {x0+174} 91'),
            (f'M{x0+14} 91 C{x0+47} 91 {x0+66} 27 {x0+97} 27 C{x0+128} 27 {x0+146} 91 {x0+177} 91',f'M{x0+14} 91 C{x0+47} 91 {x0+66} 27 {x0+97} 27 C{x0+128} 27 {x0+146} 91 {x0+177} 91'),
        ][idx]
        discriminator=[f'M{x0+8} 62 H{x0+186}',f'M{x0+8} 78 C{x0+50} 78 {x0+71} 46 {x0+102} 49 C{x0+134} 53 {x0+152} 72 {x0+186} 72',f'M{x0+8} 75 C{x0+47} 75 {x0+72} 44 {x0+106} 49 C{x0+142} 54 {x0+158} 70 {x0+186} 70',f'M{x0+8} 62 H{x0+186}'][idx]
        panel=[f'<line x1="{x0+5}" y1="92" x2="{x0+190}" y2="92" class="thin"/>',
               f'<path d="{curves[0]}" class="black-dash"/>',f'<path d="{curves[1]}" class="green-stroke"/>',
               f'<path d="{discriminator}" fill="none" stroke="#667bb0" stroke-width="1.3" stroke-dasharray="2 2"/>',
               f'<text x="{x0+7}" y="108" class="serif t11 italic">x</text>',f'<text x="{x0+98}" y="224" class="serif t13" text-anchor="middle">({chr(97+idx)})</text>']
        # Learned mapping from a uniform z line to x locations.
        panel += [f'<line x1="{x0+12}" y1="180" x2="{x0+185}" y2="180" class="thin"/>',f'<text x="{x0+5}" y="188" class="serif t11 italic">z</text>']
        for j in range(12):
            zx=x0+18+j*14
            targets=[x0+88+int(67*math.sin((j+1)*.8)),x0+97+int(56*math.sin((j+1)*.72)),x0+102+int(40*math.sin((j+1)*.62)),x0+97+int(35*math.sin((j+1)*.62))][idx]
            panel.append(f'<line x1="{zx}" y1="178" x2="{targets}" y2="118" class="thin"/>')
        panel.append(f'<line x1="{x0+5}" y1="118" x2="{x0+190}" y2="118" class="thin"/>')
        parts.append(group(f"training-stage-{chr(97+idx)}",panel))
    return paper_svg("GAN training dynamics", "Editable reconstruction of Goodfellow et al. (2014), Figure 1.",parts,900,238,"Source-faithful redraw; source paper Figure 1; distributions and mapping geometry are illustrative vectors.")


def paper_resnet() -> str:
    parts=[
        group("main-branch",[
            '<text x="150" y="18" class="sans t13">x</text><line x1="160" y1="21" x2="160" y2="42" class="mid" marker-end="url(#paper-arrow)"/>',
            '<rect x="98" y="45" width="124" height="35" class="light"/><text x="160" y="67" class="sans t12" text-anchor="middle">weight layer</text>',
            '<text x="160" y="99" class="sans t12" text-anchor="middle">relu</text><line x1="160" y1="80" x2="160" y2="112" class="mid" marker-end="url(#paper-arrow)"/>',
            '<rect x="98" y="115" width="124" height="35" class="light"/><text x="160" y="137" class="sans t12" text-anchor="middle">weight layer</text>',
            '<line x1="160" y1="150" x2="160" y2="181" class="mid" marker-end="url(#paper-arrow)"/>',
            '<circle cx="160" cy="196" r="12" fill="#fff" stroke="#111" stroke-width="1.5"/><path d="M154 196 H166 M160 190 V202" class="thin"/>',
            '<line x1="160" y1="208" x2="160" y2="225" class="mid" marker-end="url(#paper-arrow)"/><text x="160" y="242" class="sans t12" text-anchor="middle">relu</text>',
        ]),
        group("identity-shortcut",[
            '<path d="M160 28 C260 28 270 54 270 105 L270 168 C270 190 246 196 173 196" class="mid" marker-end="url(#paper-arrow)"/>',
            '<text x="287" y="92" class="sans t12">x</text><text x="287" y="108" class="sans t12">identity</text>',
        ]),
        group("function-labels",['<text x="24" y="125" class="serif t14 italic">F(x)</text>','<text x="7" y="202" class="serif t14 italic">F(x) + x</text>'])
    ]
    return paper_svg("Residual learning building block", "Editable reconstruction of He et al. (2015), Figure 2.",[group("resnet-content",parts,'transform="scale(1,.68)"')],340,180,"Source-faithful redraw; source paper Figure 2.")


def paper_unet() -> str:
    def fmap(gid: str,x: int,y: int,h: int,colors: tuple[str,...],labels: tuple[str,...]) -> str:
        shapes=[]
        for i,(color,label_) in enumerate(zip(colors,labels)):
            xx=x+i*13
            shapes.append(f'<rect x="{xx}" y="{y}" width="10" height="{h}" fill="{color}" stroke="#244d73" stroke-width=".6"/>')
            shapes.append(f'<text x="{xx+5}" y="{y-5}" class="sans t9" text-anchor="middle">{label_}</text>')
        return group(gid,shapes)
    blue="#c6def1"; gray="#eee"
    stages=[
        ("enc-1",55,38,118,(blue,blue),("64","64")),("enc-2",185,125,82,(blue,blue),("128","128")),
        ("enc-3",315,205,56,(blue,blue),("256","256")),("enc-4",445,275,38,(blue,blue),("512","512")),
        ("bottleneck",560,330,25,(blue,blue),("1024","1024")),
        ("dec-4",675,275,38,(gray,blue,blue),("512","512","512")),("dec-3",790,205,56,(gray,blue,blue),("256","256","256")),
        ("dec-2",900,125,82,(gray,blue,blue),("128","128","128")),("dec-1",1005,38,118,(gray,blue,blue),("64","64","64")),
        ("output",1070,38,118,("#e8f2fa","#e8f2fa"),("2","")),
    ]
    parts=[fmap(*s) for s in stages]
    parts.append(group("input-output-labels",[
        '<text x="18" y="82" class="sans t10">input</text><text x="18" y="94" class="sans t10">image</text><text x="18" y="106" class="sans t10">tile</text>',
        '<line x1="40" y1="96" x2="54" y2="96" stroke="#193f74" stroke-width="2" marker-end="url(#paper-arrow)"/>',
        '<text x="1100" y="82" class="sans t10">output</text><text x="1100" y="94" class="sans t10">segmentation</text><text x="1100" y="106" class="sans t10">map</text>',
    ]))
    conv=[]; pools=[]; ups=[]; copies=[]
    for x,y,h in [(81,97,118),(211,166,82),(341,233,56),(471,294,38)]:
        conv.append(f'<line x1="{x}" y1="{y}" x2="{x+70}" y2="{y}" stroke="#183d82" stroke-width="2" marker-end="url(#paper-arrow)"/>')
        pools.append(f'<line x1="{x+79}" y1="{y+12}" x2="{x+79}" y2="{y+h//2}" stroke="#b33d38" stroke-width="2" marker-end="url(#paper-arrow)"/>')
    for x1,y1,x2,y2 in [(586,342,675,294),(714,294,790,233),(829,233,900,166),(939,166,1005,97)]:
        ups.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#4a9b3e" stroke-width="3" marker-end="url(#paper-arrow)"/>')
    for x1,y,x2 in [(81,54,675),(211,140,790),(341,219,900),(471,288,1005)]:
        copies.append(f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="#777" stroke-width="1.3" marker-end="url(#paper-arrow-gray)"/>')
    parts += [group("convolution-arrows",conv),group("pooling-arrows",pools),group("upconvolution-arrows",ups),group("copy-crop-arrows",copies)]
    parts.append(group("legend",[
        '<line x1="720" y1="374" x2="747" y2="374" stroke="#183d82" stroke-width="2" marker-end="url(#paper-arrow)"/><text x="755" y="378" class="sans t10">conv 3×3, ReLU</text>',
        '<line x1="720" y1="392" x2="747" y2="392" stroke="#777" stroke-width="1.3" marker-end="url(#paper-arrow-gray)"/><text x="755" y="396" class="sans t10">copy and crop</text>',
        '<line x1="720" y1="410" x2="747" y2="410" stroke="#b33d38" stroke-width="2" marker-end="url(#paper-arrow)"/><text x="755" y="414" class="sans t10">max pool 2×2</text>',
        '<line x1="900" y1="374" x2="927" y2="374" stroke="#4a9b3e" stroke-width="3" marker-end="url(#paper-arrow)"/><text x="935" y="378" class="sans t10">up-conv 2×2</text>',
        '<line x1="900" y1="392" x2="927" y2="392" stroke="#26a2aa" stroke-width="2" marker-end="url(#paper-arrow)"/><text x="935" y="396" class="sans t10">conv 1×1</text>',
    ]))
    return paper_svg("U-Net architecture", "Editable reconstruction of Ronneberger et al. (2015), Figure 1.",[group("unet-content",parts,'transform="scale(.58,1)"')],670,430,"Source-faithful redraw; source paper Figure 1; arrows and feature maps remain independent objects.")


def paper_transformer() -> str:
    def block(gid: str,x: int,y: int,w: int,h: int,label_: str,fill: str) -> str:
        return group(gid,[f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="5" fill="{fill}" stroke="#111"/>',f'<text x="{x+w/2}" y="{y+h/2+4}" class="sans t11" text-anchor="middle">{label_}</text>'])
    parts=[
        group("encoder-shell",['<rect x="38" y="154" width="184" height="278" rx="7" fill="none" stroke="#111" stroke-width="1.4"/>','<text x="11" y="292" class="sans t12">N×</text>']),
        block("enc-self-attention",64,347,132,44,"Multi-Head Attention","#f3dda9"),block("enc-addnorm-1",64,306,132,31,"Add &amp; Norm","#dde7b9"),
        block("enc-feed-forward",64,232,132,46,"Feed Forward","#bfe0ef"),block("enc-addnorm-2",64,187,132,31,"Add &amp; Norm","#dde7b9"),
        block("input-embedding",64,480,132,40,"Input Embedding","#e4b3b2"),
        group("encoder-positional",['<circle cx="126" cy="450" r="13" fill="#fff" stroke="#111"/><path d="M120 450 H132 M126 444 V456" class="thin"/>','<path d="M8 450 L113 450" class="mid" marker-end="url(#paper-arrow)"/><text x="5" y="435" class="sans t10">Positional</text><text x="5" y="447" class="sans t10">Encoding</text>']),
        group("encoder-flow",['<path d="M126 555 V520 M126 480 V463 M126 437 V391 M126 347 V337 M126 306 V278 M126 232 V218 M126 187 V132" class="mid" marker-end="url(#paper-arrow)"/>','<text x="126" y="575" class="sans t12" text-anchor="middle">Inputs</text>']),
        group("encoder-residuals",['<path d="M126 391 C36 391 36 321 64 321" class="thin" marker-end="url(#paper-arrow)"/>','<path d="M126 278 C36 278 36 202 64 202" class="thin" marker-end="url(#paper-arrow)"/>']),
        group("decoder-shell",['<rect x="282" y="109" width="190" height="349" rx="7" fill="none" stroke="#111" stroke-width="1.4"/>','<text x="478" y="292" class="sans t12">N×</text>']),
        block("dec-masked-attention",311,373,132,44,"Masked Multi-Head","#f3dda9"),block("dec-addnorm-1",311,334,132,29,"Add &amp; Norm","#dde7b9"),
        block("dec-cross-attention",311,268,132,44,"Multi-Head Attention","#f3dda9"),block("dec-addnorm-2",311,229,132,29,"Add &amp; Norm","#dde7b9"),
        block("dec-feed-forward",311,166,132,42,"Feed Forward","#bfe0ef"),block("dec-addnorm-3",311,128,132,28,"Add &amp; Norm","#dde7b9"),
        block("output-embedding",311,495,132,39,"Output Embedding","#e4b3b2"),
        group("decoder-positional",['<circle cx="377" cy="474" r="13" fill="#fff" stroke="#111"/><path d="M371 474 H383 M377 468 V480" class="thin"/>','<path d="M487 474 L390 474" class="mid" marker-end="url(#paper-arrow)"/><text x="491" y="459" class="sans t10">Positional</text><text x="491" y="471" class="sans t10">Encoding</text>']),
        group("decoder-flow",['<path d="M377 566 V534 M377 495 V487 M377 461 V417 M377 373 V363 M377 334 V312 M377 268 V258 M377 229 V208 M377 166 V156 M377 128 V93" class="mid" marker-end="url(#paper-arrow)"/>','<text x="377" y="582" class="sans t12" text-anchor="middle">Outputs</text><text x="377" y="594" class="sans t10" text-anchor="middle">(shifted right)</text>']),
        group("decoder-residuals",['<path d="M377 417 C466 417 466 348 443 348" class="thin" marker-end="url(#paper-arrow)"/>','<path d="M377 312 C466 312 466 243 443 243" class="thin" marker-end="url(#paper-arrow)"/>','<path d="M377 208 C466 208 466 142 443 142" class="thin" marker-end="url(#paper-arrow)"/>']),
        group("cross-attention-memory",['<path d="M126 132 C126 96 274 96 274 290 L311 290" class="mid" marker-end="url(#paper-arrow)"/>']),
        block("linear",320,49,114,31,"Linear","#bfe0ef"),block("softmax",320,9,114,29,"Softmax","#dde7b9"),
        group("output-probabilities",['<path d="M377 93 V80 M377 49 V38 M377 9 V1" class="mid" marker-end="url(#paper-arrow)"/>','<text x="377" y="-4" class="sans t11" text-anchor="middle">Output Probabilities</text>']),
    ]
    return paper_svg("Transformer model architecture", "Editable reconstruction of Vaswani et al. (2017), Figure 1.",[group("transformer-content",parts,'transform="translate(0,18) scale(.62,1)"')],334,628,"Source-faithful redraw; source paper Figure 1; residual paths and cross-attention remain separate.")


def paper_neural_ode() -> str:
    parts=[]
    for panel,x0,title_ in [("residual",20,"Residual Network"),("ode",260,"ODE Network")]:
        p=[f'<rect x="{x0}" y="34" width="205" height="190" fill="#fff" stroke="#111"/>',f'<text x="{x0+102}" y="20" class="serif t13" text-anchor="middle">{title_}</text>',
           f'<text x="{x0+102}" y="246" class="serif t11" text-anchor="middle">Input/Hidden/Output</text>',f'<text x="{x0-7}" y="132" class="serif t11" transform="rotate(-90 {x0-7} 132)" text-anchor="middle">Depth</text>']
        for yy in range(56,213,28): p.append(f'<line x1="{x0+5}" y1="{yy}" x2="{x0+200}" y2="{yy}" stroke="#ddd" stroke-width=".6"/>')
        for xx in range(x0+25,x0+200,28): p.append(f'<line x1="{xx}" y1="39" x2="{xx}" y2="219" stroke="#eee" stroke-width=".5"/>')
        for row in range(5):
            for col in range(6):
                xx=x0+25+col*28; yy=58+row*34; dx=(col-2.5)*2.2; dy=-12
                p.append(f'<line x1="{xx}" y1="{yy}" x2="{xx+dx:.1f}" y2="{yy+dy}" stroke="#b66" stroke-width=".55" marker-end="url(#paper-arrow)" opacity=".55"/>')
        if panel=="residual":
            for k,base in enumerate((62,105,150)):
                points=[]
                for j in range(7): points.append((x0+base+int(12*math.sin(j*.9+k)),214-j*27))
                p.append('<path d="M'+' L'.join(f'{x},{y}' for x,y in points)+'" class="thin"/>')
                p += [f'<circle cx="{x}" cy="{y}" r="2.4" fill="#111"/>' for x,y in points]
        else:
            for k,base in enumerate((62,105,150)):
                p.append(f'<path d="M{x0+base} 214 C{x0+base-20+8*k} 165 {x0+base+22-5*k} 105 {x0+base+4*k-8} 40" class="thin"/>')
                for j in range(5):
                    yy=214-j*43; xx=x0+base+int(10*math.sin(j*.8+k))
                    p.append(f'<circle cx="{xx}" cy="{yy}" r="2.4" fill="#111"/>')
        parts.append(group(f"{panel}-panel",p))
    return paper_svg("Residual network and ODE network", "Editable reconstruction of Chen et al. (2018), Figure 1.",[group("neural-ode-content",parts,'transform="scale(1,1.35)"')],485,350,"Source-faithful redraw; source paper Figure 1; circles denote evaluation locations.")


def paper_simclr() -> str:
    def node(gid: str,cx: int,cy: int,label_: str,fill: str="#fff") -> str:
        return group(gid,[f'<circle cx="{cx}" cy="{cy}" r="23" fill="{fill}" stroke="#111" stroke-width="1.2"/>',f'<text x="{cx}" y="{cy+5}" class="serif t13 italic" text-anchor="middle">{label_}</text>'])
    parts=[
        node("input-x",320,240,"x","#eee"),node("view-xi",190,182,"x̃ᵢ","#eee"),node("view-xj",450,182,"x̃ⱼ","#eee"),
        node("repr-hi",190,111,"hᵢ"),node("repr-hj",450,111,"hⱼ"),node("proj-zi",190,42,"zᵢ"),node("proj-zj",450,42,"zⱼ"),
        group("augmentation-edges",['<path d="M303 225 C268 204 242 190 214 184" class="mid" marker-end="url(#paper-arrow)"/>','<path d="M337 225 C372 204 398 190 426 184" class="mid" marker-end="url(#paper-arrow)"/>','<text x="250" y="219" class="serif t12 italic">t ~ T</text><text x="390" y="219" class="serif t12 italic">t′ ~ T</text>']),
        group("encoder-edges",['<line x1="190" y1="159" x2="190" y2="135" class="mid" marker-end="url(#paper-arrow)"/>','<line x1="450" y1="159" x2="450" y2="135" class="mid" marker-end="url(#paper-arrow)"/>','<text x="168" y="151" class="serif t12 italic">f(·)</text><text x="428" y="151" class="serif t12 italic">f(·)</text>']),
        group("projection-edges",['<line x1="190" y1="87" x2="190" y2="66" class="mid" marker-end="url(#paper-arrow)"/>','<line x1="450" y1="87" x2="450" y2="66" class="mid" marker-end="url(#paper-arrow)"/>','<text x="164" y="81" class="serif t12 italic">g(·)</text><text x="424" y="81" class="serif t12 italic">g(·)</text>']),
        group("objectives",['<line x1="216" y1="42" x2="424" y2="42" class="thin" marker-start="url(#paper-arrow)" marker-end="url(#paper-arrow)"/>','<text x="320" y="29" class="serif t12" text-anchor="middle">Maximize agreement</text>','<line x1="216" y1="111" x2="424" y2="111" class="thin" marker-start="url(#paper-arrow)" marker-end="url(#paper-arrow)"/>','<text x="320" y="101" class="serif t12" text-anchor="middle">Representation</text>']),
    ]
    return paper_svg("SimCLR framework", "Editable reconstruction of Chen et al. (2020), Figure 2.",parts,640,270,"Source-faithful redraw; source paper Figure 2; all views and operations are native vectors.")


def paper_ddpm() -> str:
    labels=["x_T","⋯","x_t","xₜ₋₁","⋯","x_0"]
    label_x=[54,151,247,408,570,762]
    parts=[]
    for i,(lx,label_) in enumerate(zip(label_x,labels)):
        if label_=="⋯": parts.append(f'<text x="{lx}" y="46" class="serif t16" text-anchor="middle">⋯</text>')
        else: parts.append(group(f"state-{i}",[f'<circle cx="{lx}" cy="42" r="27" fill="{("#bbb" if i<4 else "#fff")}" stroke="#111" stroke-width="1.2"/>',f'<text x="{lx}" y="49" class="serif t14 italic" text-anchor="middle">{label_}</text>']))
    links=[]
    for i,(a,b) in enumerate(zip(label_x[:-1],label_x[1:])):
        start=a+29 if labels[i]!="⋯" else a+15; end=b-29 if labels[i+1]!="⋯" else b-15
        links.append(f'<line x1="{start}" y1="33" x2="{end}" y2="33" class="thin" marker-end="url(#paper-arrow)"/>')
        links.append(f'<line x1="{end}" y1="55" x2="{start}" y2="55" class="thin" marker-end="url(#paper-arrow)"/>')
    parts.append(group("markov-chain",links))
    parts.append(group("transition-labels",['<text x="398" y="15" class="serif t12 italic" text-anchor="middle">pθ(xₜ₋₁|xₜ)</text>','<text x="398" y="83" class="serif t12 italic" text-anchor="middle">q(xₜ|xₜ₋₁)</text>']))
    thumbs=[]
    for k,x in enumerate((36,229,390,744)):
        thumbs.append(f'<rect x="{x}" y="92" width="38" height="38" fill="#ddd" stroke="#aaa"/>')
        for r in range(6):
            for c in range(6):
                v=(r*17+c*29+k*31)%120+90
                color="#d9b09b" if k==3 and 1<=r<=4 and 1<=c<=4 else ("#eee" if k==3 else f'rgb({v},{v},{v})')
                thumbs.append(f'<rect x="{x+c*6.33:.1f}" y="{92+r*6.33:.1f}" width="6.4" height="6.4" fill="{color}" stroke="none"/>')
        if k==3:
            thumbs += [f'<circle cx="{x+14}" cy="108" r="1.5" fill="#333"/>',f'<circle cx="{x+25}" cy="108" r="1.5" fill="#333"/>',f'<path d="M{x+14} 119 Q{x+20} 123 {x+26} 118" class="thin"/>']
    parts.append(group("state-thumbnails",thumbs))
    return paper_svg("Diffusion graphical model", "Editable reconstruction of Ho et al. (2020), Figure 2.",[group("ddpm-content",parts,'transform="scale(1,.73)"')],820,108,"Source-faithful redraw; source paper Figure 2; thumbnails are editable vector mosaics, not embedded paper art.")


def paper_vit() -> str:
    parts=[
        group("class-and-head",['<rect x="18" y="18" width="50" height="76" rx="16" class="orange"/><text x="43" y="43" class="sans t10" text-anchor="middle">Class</text><text x="43" y="55" class="sans t10" text-anchor="middle">Bird</text><text x="43" y="67" class="sans t10" text-anchor="middle">Ball</text><text x="43" y="79" class="sans t10" text-anchor="middle">Car</text>','<rect x="92" y="25" width="54" height="48" rx="6" class="orange"/><text x="119" y="45" class="sans t10" text-anchor="middle">MLP</text><text x="119" y="58" class="sans t10" text-anchor="middle">Head</text>','<line x1="68" y1="56" x2="92" y2="50" class="mid" marker-end="url(#paper-arrow)"/>']),
        group("transformer-encoder",['<rect x="166" y="92" width="410" height="74" rx="5" fill="#eee" stroke="#111"/><text x="371" y="119" class="sans t12" text-anchor="middle">Transformer Encoder</text>','<line x1="119" y1="73" x2="166" y2="115" class="mid" marker-end="url(#paper-arrow)"/>']),
        group("linear-projection",['<rect x="176" y="221" width="390" height="32" class="pink"/><text x="371" y="241" class="sans t11" text-anchor="middle">Linear Projection of Flattened Patches</text>']),
        group("patch-image",[
            '<rect x="160" y="276" width="230" height="66" fill="#d8ecf4" stroke="#111"/>','<polygon points="160,331 224,287 270,331" fill="#769ec1"/><polygon points="214,331 285,282 352,331" fill="#3e6e97"/><rect x="160" y="327" width="230" height="15" fill="#99b86d"/>',
            '<path d="M217 276 V342 M275 276 V342 M333 276 V342 M160 298 H390 M160 320 H390" stroke="#fff" stroke-width="1" opacity=".9"/>',
        ]),
        group("patch-label",['<text x="83" y="292" class="sans t10">Patch + Position</text><text x="83" y="304" class="sans t10">Embedding</text><text x="83" y="318" class="sans t9">(Extra learnable</text><text x="83" y="328" class="sans t9">[class] embedding)</text>']),
        group("encoder-detail",[
            '<rect x="615" y="15" width="200" height="327" fill="none" stroke="#111" stroke-dasharray="5 4"/><text x="715" y="33" class="sans t12 bold" text-anchor="middle">Transformer Encoder</text><text x="626" y="63" class="sans t11">L×</text>',
            '<rect x="655" y="283" width="120" height="38" class="pink"/><text x="715" y="306" class="sans t11" text-anchor="middle">Embedded Patches</text>',
            '<rect x="655" y="239" width="120" height="28" class="yellow"/><text x="715" y="257" class="sans t11" text-anchor="middle">Norm</text>',
            '<rect x="655" y="174" width="120" height="48" class="green"/><text x="715" y="194" class="sans t10" text-anchor="middle">Multi-Head</text><text x="715" y="207" class="sans t10" text-anchor="middle">Attention</text>',
            '<rect x="655" y="130" width="120" height="28" class="yellow"/><text x="715" y="148" class="sans t11" text-anchor="middle">Norm</text>',
            '<rect x="655" y="72" width="120" height="42" class="blue"/><text x="715" y="97" class="sans t11" text-anchor="middle">MLP</text>',
            '<circle cx="715" cy="52" r="10" fill="#fff" stroke="#111"/><path d="M710 52 H720 M715 47 V57" class="thin"/>',
            '<circle cx="799" cy="162" r="9" fill="#fff" stroke="#111"/><path d="M794 162 H804 M799 157 V167" class="thin"/>',
            '<path d="M715 283 V267 M715 239 V222 M715 174 V158 M715 130 V114 M715 72 V62" class="mid" marker-end="url(#paper-arrow)"/>',
            '<path d="M715 239 C805 239 815 192 799 171" class="thin" marker-end="url(#paper-arrow)"/><path d="M799 153 C815 111 794 94 775 94" class="thin" marker-end="url(#paper-arrow)"/>',
        ]),
    ]
    tokens=[]
    for i in range(11):
        x=182+i*35
        tokens.append(f'<circle cx="{x}" cy="197" r="12" fill="{("#f4d0a3" if i==0 else "#eee")}" stroke="#111"/>')
        tokens.append(f'<text x="{x}" y="201" class="sans t9" text-anchor="middle">{("*" if i==0 else str(i))}</text>')
        tokens.append(f'<line x1="{x}" y1="221" x2="{x}" y2="210" class="thin" marker-end="url(#paper-arrow)"/>')
        tokens.append(f'<line x1="{x}" y1="185" x2="{x}" y2="166" class="thin" marker-end="url(#paper-arrow)"/>')
    parts.append(group("patch-tokens",tokens))
    return paper_svg("Vision Transformer model overview", "Editable reconstruction of Dosovitskiy et al. (2020), Figure 1.",parts,835,355,"Source-faithful redraw; source paper Figure 1; input scene is a native vector substitute for the source thumbnail.")


def axes(x0: float = 120, y0: float = 540, x1: float = 1080, y1: float = 145, xlabel: str = "x", ylabel: str = "y") -> list[str]:
    return [line(x0,y0,x1,y0,"axis"),line(x0,y0,x0,y1,"axis"),text((x0+x1)/2,y0+55,xlabel,"small muted"),text(x0-65,(y0+y1)/2,ylabel,"small muted",extra=f'transform="rotate(-90 {x0-65:g} {(y0+y1)/2:g})"')]


def point_path(points: Iterable[tuple[float, float]]) -> str:
    values=list(points)
    return "M"+" L".join(f"{x:.2f},{y:.2f}" for x,y in values)


def curve_double_descent() -> str:
    parts=axes(xlabel="model capacity",ylabel="test risk")
    pts=[]
    for i in range(101):
        x=i/100
        y=0.22+0.62*math.exp(-((x-.26)/.19)**2)+0.75*math.exp(-((x-.53)/.075)**2)+0.26*math.exp(-3.4*max(0,x-.58))
        pts.append((130+930*x,500-300*y))
    parts += [path(point_path(pts),"wire2"),line(120+930*.53,145,120+930*.53,540,"axis",'stroke-dasharray="8 8"'),text(120+930*.53,125,"interpolation threshold","tiny muted"),text(270,270,"classical regime","small strong"),text(835,330,"modern regime","small strong"),text(1125,103,"ILLUSTRATIVE NORMALIZED","paper-note")]
    return svg("Double descent", "Conceptual normalized curve after Belkin et al. (2018); not digitized data",parts,metadata="Source: Reconciling modern machine learning practice and the bias-variance trade-off; illustrative normalized curve.")


def curve_scaling_law() -> str:
    parts=axes(xlabel="log scale (parameters / data / compute)",ylabel="log loss above floor")
    colors=[("wire2",.72,0),("violet-line",.56,38),("red-line",.42,76)]
    labels=["parameters N","dataset D","compute C"]
    for idx,((css,alpha,offset),label_) in enumerate(zip(colors,labels)):
        pts=[]
        for i in range(101):
            x=i/100; y=.95-alpha*x
            pts.append((140+900*x,500-300*y+offset))
        parts += [path(point_path(pts),css),text(870,210+idx*78,label_,"small strong","start")]
    parts += [text(1125,103,"ILLUSTRATIVE NORMALIZED","paper-note"),text(600,610,"straight lines in log–log space represent power laws","tiny muted")]
    return svg("Neural scaling laws", "Normalized power-law trends after Kaplan et al. (2020); not original measurements",parts,metadata="Source: Scaling Laws for Neural Language Models; illustrative normalized curve.")


def curve_cyclical_lr() -> str:
    parts=axes(xlabel="training iteration",ylabel="learning rate")
    pts=[]
    for i in range(161):
        phase=(i%40)/40
        value=phase*2 if phase<.5 else 2*(1-phase)
        pts.append((130+930*i/160,500-285*(.12+.78*value)))
    parts += [path(point_path(pts),"wire2"),text(255,185,"max LR","tiny muted"),text(255,500,"base LR","tiny muted"),text(1125,103,"FORMULA-DERIVED","paper-note")]
    return svg("Triangular cyclical learning rate", "Schedule generated from the triangular policy in Smith (2015)",parts,metadata="Source: Cyclical Learning Rates for Training Neural Networks; formula-derived curve.")


def curve_cosine_restarts() -> str:
    parts=axes(xlabel="training iteration",ylabel="learning rate")
    pts=[]; lengths=[24,40,64]; total=sum(lengths); cursor=0
    for length in lengths:
        for j in range(length+1):
            value=.08+.82*(1+math.cos(math.pi*j/length))/2
            pts.append((130+930*(cursor+j)/total,500-300*value))
        cursor+=length
    parts += [path(point_path(pts),"violet-line"),*[line(130+930*sum(lengths[:i])/total,145,130+930*sum(lengths[:i])/total,540,"axis",'stroke-dasharray="5 8"') for i in range(1,len(lengths))],text(1125,103,"FORMULA-DERIVED","paper-note")]
    return svg("Cosine annealing with warm restarts", "SGDR schedule with growing restart periods after Loshchilov & Hutter (2016)",parts,metadata="Source: SGDR; formula-derived curve.")


def curve_diffusion_schedules() -> str:
    parts=axes(xlabel="normalized diffusion time t",ylabel="cumulative signal")
    linear=[]; cosine=[]
    for i in range(101):
        x=i/100
        linear.append((130+930*x,500-310*max(0,1-x)))
        s=.008
        value=math.cos(((x+s)/(1+s))*math.pi/2)**2 / math.cos((s/(1+s))*math.pi/2)**2
        cosine.append((130+930*x,500-310*value))
    parts += [path(point_path(linear),"red-line dash"),path(point_path(cosine),"violet-line"),line(790,180,850,180,"red-line dash"),text(865,186,"linear reference","tiny muted","start"),line(790,220,850,220,"violet-line"),text(865,226,"cosine schedule","tiny muted","start"),text(1125,103,"FORMULA-DERIVED","paper-note")]
    return svg("Diffusion signal schedules", "Linear reference and cosine cumulative signal schedule after Nichol & Dhariwal (2021)",parts,metadata="Source: Improved Denoising Diffusion Probabilistic Models; formula-derived curve.")


def curve_grokking() -> str:
    parts=axes(xlabel="log training steps",ylabel="accuracy")
    train=[]; test=[]
    for i in range(101):
        x=i/100
        train_y=.08+.9/(1+math.exp(-28*(x-.2)))
        test_y=.08+.9/(1+math.exp(-32*(x-.72)))
        train.append((130+930*x,500-310*train_y)); test.append((130+930*x,500-310*test_y))
    parts += [path(point_path(train),"wire2"),path(point_path(test),"violet-line"),line(760,180,820,180,"wire2"),text(835,186,"train","tiny muted","start"),line(760,220,820,220,"violet-line"),text(835,226,"test","tiny muted","start"),text(420,360,"memorization","small strong"),text(875,290,"delayed generalization","small strong"),text(1125,103,"ILLUSTRATIVE NORMALIZED","paper-note")]
    return svg("Grokking dynamics", "Conceptual delayed generalization after Power et al. (2022); not experiment data",parts,metadata="Source: Grokking; illustrative normalized curve.")


ASSETS: tuple[Asset, ...] = (
    Asset("attention-heads","Multi-head attention","primitive",("attention","transformer","heads"),primitive_attention_heads),
    Asset("convolution-pyramid","Convolutional feature pyramid","primitive",("cnn","feature-map","pyramid"),primitive_convolution_pyramid),
    Asset("graph-message-passing","Graph message passing","primitive",("gnn","graph","aggregation"),primitive_graph_message_passing),
    Asset("causal-dag","Causal DAG","primitive",("causal","dag","intervention"),primitive_causal_dag),
    Asset("optimization-landscape","Optimization landscape","primitive",("optimization","loss","trajectory"),primitive_optimization_landscape),
    Asset("uncertainty-bands","Predictive uncertainty","primitive",("uncertainty","confidence","prediction"),primitive_uncertainty_bands),
    Asset("dataset-pipeline","Dataset pipeline","primitive",("data","pipeline","validation"),primitive_dataset_pipeline),
    Asset("training-loop","Training loop","primitive",("training","gradient","evaluation"),primitive_training_loop),
    Asset("ensemble-voting","Model ensemble","primitive",("ensemble","voting","uncertainty"),primitive_ensemble_voting),
    Asset("bayesian-inference","Bayesian inference","primitive",("bayesian","posterior","predictive"),primitive_bayesian_inference),
    Asset("multimodal-fusion","Multimodal fusion","primitive",("multimodal","fusion","cross-attention"),primitive_multimodal_fusion),
    Asset("ablation-matrix","Ablation matrix","primitive",("ablation","experiment","matrix"),primitive_ablation_matrix),
    Asset("lenet-5","LeNet-5 architecture","paper",("cnn","architecture","classic"),paper_lenet,"pixel-exact-dual-layer","Gradient-Based Learning Applied to Document Recognition","https://leon.bottou.org/publications/pdf/ieee-1998.pdf","Figure 2","Direct source-operator layer plus a hidden semantic editing layer."),
    Asset("alexnet","AlexNet architecture","paper",("cnn","imagenet","architecture"),paper_alexnet,"pixel-exact-dual-layer","ImageNet Classification with Deep Convolutional Neural Networks","https://papers.nips.cc/paper_files/paper/2012/file/c399862d3b9d6b76c8436e924a68c45b-Paper.pdf","Figure 2","Direct source-operator layer plus a hidden semantic editing layer."),
    Asset("vae","Variational graphical model","paper",("vae","graphical-model","variational"),paper_vae,"pixel-exact-dual-layer","Auto-Encoding Variational Bayes","https://arxiv.org/abs/1312.6114","Figure 1","Direct source-operator layer plus a hidden semantic editing layer."),
    Asset("gan","GAN training dynamics","paper",("gan","training-dynamics","distribution"),paper_gan,"pixel-exact-dual-layer","Generative Adversarial Nets","https://arxiv.org/abs/1406.2661","Figure 1","Direct source-operator layer plus a hidden semantic editing layer."),
    Asset("resnet-block","Residual learning block","paper",("resnet","residual","skip"),paper_resnet,"pixel-exact-dual-layer","Deep Residual Learning for Image Recognition","https://arxiv.org/abs/1512.03385","Figure 2","Direct source-operator layer plus a hidden semantic editing layer."),
    Asset("unet","U-Net architecture","paper",("unet","segmentation","skip"),paper_unet,"pixel-exact-dual-layer","U-Net: Convolutional Networks for Biomedical Image Segmentation","https://arxiv.org/abs/1505.04597","Figure 1","Direct source-operator layer plus a hidden semantic editing layer."),
    Asset("transformer","Transformer encoder–decoder","paper",("transformer","attention","encoder-decoder"),paper_transformer,"pixel-exact-dual-layer","Attention Is All You Need","https://arxiv.org/abs/1706.03762","Figure 1","Direct source-operator layer plus a hidden semantic editing layer."),
    Asset("neural-ode","Neural ODE","paper",("ode","continuous-depth","solver"),paper_neural_ode,"pixel-exact-dual-layer","Neural Ordinary Differential Equations","https://arxiv.org/abs/1806.07366","Figure 1","Direct source-operator layer plus a hidden semantic editing layer."),
    Asset("simclr","SimCLR framework","paper",("contrastive","augmentation","representation"),paper_simclr,"pixel-exact-dual-layer","A Simple Framework for Contrastive Learning of Visual Representations","https://arxiv.org/abs/2002.05709","Figure 2","Direct source-operator layer plus a hidden semantic editing layer."),
    Asset("ddpm","Denoising diffusion graphical model","paper",("diffusion","denoising","markov"),paper_ddpm,"pixel-exact-dual-layer","Denoising Diffusion Probabilistic Models","https://arxiv.org/abs/2006.11239","Figure 2","Direct source-operator layer plus a hidden semantic editing layer; source thumbnails remain named embedded raster components."),
    Asset("vit","Vision Transformer","paper",("vit","patches","transformer"),paper_vit,"pixel-exact-dual-layer","An Image is Worth 16x16 Words","https://arxiv.org/abs/2010.11929","Figure 1","Direct source-operator layer plus a hidden semantic editing layer; source photographs remain named embedded raster components."),
    Asset("double-descent","Double descent","curve",("double-descent","capacity","generalization"),curve_double_descent,"illustrative-normalized","Reconciling modern machine learning practice and the bias-variance trade-off","https://arxiv.org/abs/1812.11118",None,"Analytic normalized trend; not digitized or claimed as original measurements."),
    Asset("scaling-law","Neural scaling laws","curve",("scaling-law","power-law","loss"),curve_scaling_law,"illustrative-normalized","Scaling Laws for Neural Language Models","https://arxiv.org/abs/2001.08361",None,"Normalized log-log trends; slopes are illustrative, not fitted paper values."),
    Asset("cyclical-lr","Cyclical learning rate","curve",("learning-rate","schedule","triangular"),curve_cyclical_lr,"formula-derived","Cyclical Learning Rates for Training Neural Networks","https://arxiv.org/abs/1506.01186",None,"Generated directly from a triangular cyclical schedule."),
    Asset("cosine-restarts","Cosine warm restarts","curve",("learning-rate","cosine","restart"),curve_cosine_restarts,"formula-derived","SGDR: Stochastic Gradient Descent with Warm Restarts","https://arxiv.org/abs/1608.03983",None,"Generated from cosine annealing with increasing restart periods."),
    Asset("diffusion-schedules","Diffusion schedules","curve",("diffusion","noise-schedule","cosine"),curve_diffusion_schedules,"formula-derived","Improved Denoising Diffusion Probabilistic Models","https://arxiv.org/abs/2102.09672",None,"Cosine cumulative signal curve generated from the published schedule form."),
    Asset("grokking","Grokking dynamics","curve",("grokking","generalization","training"),curve_grokking,"illustrative-normalized","Grokking: Generalization Beyond Overfitting on Small Algorithmic Datasets","https://arxiv.org/abs/2201.02177",None,"Normalized conceptual timing; not digitized or claimed as experiment data."),
)


def build_manifest(assets: Iterable[Asset]) -> dict[str, object]:
    exact_path = ROOT / "assets" / "paper-redraws" / "pixel-exact-manifest.json"
    exact_records = {}
    if exact_path.exists():
        exact_records = {item["id"]: item for item in json.loads(exact_path.read_text(encoding="utf-8"))["figures"]}
    records=[]
    for asset in assets:
        exact = exact_records.get(asset.slug, {})
        is_paper = asset.category == "paper"
        records.append({
            "id": asset.slug,
            "title": asset.title,
            "category": asset.category,
            "path": asset.relative_path,
            "tags": list(asset.tags),
            "reproduction": asset.reproduction,
            "source": None if asset.source_title is None else {"title":asset.source_title,"url":asset.source_url,"figure":asset.source_figure},
            "note": asset.note,
            "editable": {
                "format":"svg",
                "text_as_text": not is_paper,
                "named_groups":True,
                "embedded_raster": bool(exact.get("embedded_raster_components", 0)),
                "embedded_raster_components": int(exact.get("embedded_raster_components", 0)),
                "visible_layer": "source glyph outlines and source operators" if is_paper else "semantic vectors",
                "semantic_edit_layer": bool(exact.get("semantic_edit_layer", False)) if is_paper else True,
            },
            "source_operator_sha256": exact.get("source_operator_sha256") if is_paper else None,
            "reproduce": f"python scripts/extract_pixel_exact_paper_figures.py --only {asset.slug}" if is_paper else f"python scripts/generate_gallery.py --only {asset.slug}",
        })
    return {"schema_version":1,"license":"Generator code and generic primitives are MIT. Pixel-exact paper operator layers include citations; source papers and review crops retain their rights, and downstream reuse requirements must be checked.","assets":records}


def generate(output_root: Path = DEFAULT_ASSET_ROOT, selected: set[str] | None = None) -> list[Path]:
    chosen=[asset for asset in ASSETS if selected is None or asset.slug in selected]
    if selected:
        unknown=selected-{asset.slug for asset in ASSETS}
        if unknown:
            raise ValueError(f"Unknown asset ids: {', '.join(sorted(unknown))}")
        paper_ids = sorted(asset.slug for asset in chosen if asset.category == "paper")
        if paper_ids:
            raise ValueError(
                "Paper figures use direct PDF operator extraction; run "
                f"scripts/extract_pixel_exact_paper_figures.py for: {', '.join(paper_ids)}"
            )
    chosen = [asset for asset in chosen if asset.category != "paper"]
    written=[]
    for asset in chosen:
        target=output_root/asset.relative_path
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(asset.renderer(),encoding="utf-8")
        written.append(target)
    if selected is None:
        manifest_path=output_root/"gallery-manifest.json"
        manifest_path.write_text(json.dumps(build_manifest(ASSETS),ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        written.append(manifest_path)
    return written


def parse_args() -> argparse.Namespace:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only",action="append",help="Generate one asset id; repeat for multiple assets.")
    parser.add_argument("--output-root",type=Path,default=DEFAULT_ASSET_ROOT)
    parser.add_argument("--list",action="store_true",help="List available asset ids and exit.")
    return parser.parse_args()


def main() -> int:
    args=parse_args()
    if args.list:
        for asset in ASSETS:
            print(f"{asset.slug}\t{asset.category}\t{asset.title}")
        return 0
    written=generate(args.output_root,set(args.only) if args.only else None)
    print(json.dumps({"written":len(written),"output_root":str(args.output_root)},ensure_ascii=False))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
