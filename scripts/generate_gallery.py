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


def svg(title: str, subtitle: str, body: Iterable[str], width: int = 1200, height: int = 675, metadata: str = "") -> str:
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
  <g id="figure-title">{text(52, 58, title, 'title', 'start')}{text(52, 86, subtitle, 'subtitle', 'start')}</g>
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
    stages = [(55, 240, 105, 190, "Input", "32×32", "slate"), (205, 255, 105, 160, "C1", "6@28×28", "blue"), (350, 275, 95, 120, "S2", "6@14×14", "cyan"), (490, 285, 90, 100, "C3", "16@10×10", "violet"), (625, 300, 80, 70, "S4", "16@5×5", "gold"), (755, 310, 105, 50, "C5", "120", "red"), (910, 310, 105, 50, "F6", "84", "green"), (1060, 310, 90, 50, "Output", "10", "slate")]
    parts = [text(1125, 103, "SEMANTIC REDRAW", "paper-note")]
    for i, (x,y,w,h,a,b,tone) in enumerate(stages):
        parts.append(stack(f"lenet-stage-{i}",x,y,w,h,2 if i<5 else 1,tone,a))
        parts.append(text(x+w/2,y+h+30,b,"tiny muted"))
        if i:
            px,py,pw,ph,*_=stages[i-1]
            parts.append(arrow(f"lenet-edge-{i}",px+pw+10,py+ph/2,x-8,y+h/2))
    return svg("LeNet-5 architecture", "Concept redraw after LeCun et al. (1998), Figure 2", parts, metadata="Source: Gradient-Based Learning Applied to Document Recognition; semantic redraw.")


def paper_alexnet() -> str:
    widths = [135,120,110,100,90,80,70,70,70]
    labels = [("Input","224²×3"),("Conv1","96@11²"),("Conv2","256@5²"),("Conv3","384@3²"),("Conv4","384@3²"),("Conv5","256@3²"),("FC6","4096"),("FC7","4096"),("FC8","1000 + softmax")]
    tones=["slate","blue","cyan","violet","violet","red","gold","gold","green"]
    parts=[text(1125,103,"SEMANTIC REDRAW","paper-note")]
    x=30
    for i,(w,(a,b),tone) in enumerate(zip(widths,labels,tones)):
        h=230-i*22 if i<6 else 82
        y=250+(230-h)/2
        parts += [stack(f"alexnet-stage-{i}",x,y,w,h,2 if i<6 else 1,tone,a),text(x+w/2,y+h+29,b,"tiny muted")]
        if i: parts.append(arrow(f"alexnet-edge-{i}",x-34,y+h/2,x-7,y+h/2))
        x += w+36
    parts.append(text(600,560,"5 convolutional layers → 3 fully connected layers","small muted"))
    return svg("AlexNet architecture", "Compact concept redraw after Krizhevsky, Sutskever & Hinton (2012)", parts, metadata="Source: ImageNet Classification with Deep Convolutional Neural Networks; semantic redraw.")


def paper_vae() -> str:
    parts=[text(1125,103,"SEMANTIC REDRAW","paper-note"),box("vae-input",65,270,145,100,"Data","x","slate"),box("vae-encoder",300,235,190,170,"Encoder qφ","μ(x), log σ²(x)","blue"),box("vae-noise",555,150,115,90,"Noise","ε ~ N(0,I)","violet"),box("vae-latent",555,330,115,90,"Latent","z = μ + σε","gold"),box("vae-decoder",760,235,190,170,"Decoder pθ","pθ(x | z)","green"),box("vae-output",1040,270,110,100,"Rebuild","x̂","red")]
    parts += [arrow("vae-e1",210,320,300,320),arrow("vae-e2",490,320,555,365),arrow("vae-noise-edge",612,240,612,330,"sample"),arrow("vae-e3",670,375,760,320),arrow("vae-e4",950,320,1040,320),path("M395,405 C430,525 835,525 855,405","violet-line dash",'marker-end="url(#arrow-violet)"'),text(625,550,"ELBO = reconstruction − KL(qφ(z|x) || p(z))","small strong")]
    return svg("Variational autoencoder", "Reparameterized inference and generative reconstruction after Kingma & Welling (2013)",parts,metadata="Source: Auto-Encoding Variational Bayes; semantic redraw.")


def paper_gan() -> str:
    parts=[text(1125,103,"SEMANTIC REDRAW","paper-note"),box("noise",70,205,150,100,"Noise","z ~ p(z)","violet"),box("generator",330,205,190,100,"Generator G","x̃ = G(z)","blue"),box("real",70,410,150,100,"Real data","x ~ pdata","green"),box("discriminator",700,285,210,140,"Discriminator D","real probability","red"),box("decision",1015,305,145,100,"Decision","real / fake","gold")]
    parts += [arrow("gan-zg",220,255,330,255),arrow("gan-gd",520,255,700,330,"generated"),arrow("gan-real-d",220,460,700,380,"real",bend=40),arrow("gan-out",910,355,1015,355),path("M805,425 C805,555 425,555 425,305","violet-line dash",'marker-end="url(#arrow-violet)"'),text(620,585,"min G  max D   E log D(x) + E log(1 − D(G(z)))","small strong")]
    return svg("Generative adversarial network", "Two-player minimax training after Goodfellow et al. (2014)",parts,metadata="Source: Generative Adversarial Networks; semantic redraw.")


def paper_resnet() -> str:
    parts=[text(1125,103,"SEMANTIC REDRAW","paper-note"),circle(120,330,16,"dot-blue"),text(120,380,"x","label strong"),box("res-layer-1",300,225,210,90,"Weight layer","F₁(x)","blue"),box("res-layer-2",300,390,210,90,"Weight layer","F₂(·)","violet"),circle(725,390,29,"node"),text(725,398,"+","title"),box("res-activation",865,345,180,90,"ReLU","F(x) + x","green")]
    parts += [arrow("res-main-1",136,330,300,270),arrow("res-main-2",405,315,405,390),arrow("res-main-3",510,435,696,400),arrow("res-main-4",754,390,865,390),path("M135,320 C300,120 690,120 725,360","wire2",'marker-end="url(#arrow-blue)"'),text(430,145,"identity shortcut","small strong"),text(590,470,"F(x)","small muted")]
    return svg("Residual learning block", "Modern editable redraw of Figure 2 in He et al. (2015)",parts,metadata="Source: Deep Residual Learning for Image Recognition, Figure 2; semantic redraw.")


def paper_unet() -> str:
    parts=[text(1125,103,"SEMANTIC REDRAW","paper-note")]
    left=[(80,180,145,300,"64"),(250,215,135,230,"128"),(420,250,125,160,"256"),(580,285,115,90,"512")]
    right=[(765,250,125,160,"256"),(930,215,135,230,"128"),(1090,180,80,300,"64")]
    for i,(x,y,w,h,label_) in enumerate(left):
        parts.append(stack(f"unet-down-{i}",x,y,w,h,3,"blue" if i<2 else "violet",label_))
        if i: parts.append(arrow(f"unet-down-edge-{i}",left[i-1][0]+left[i-1][2]+12,left[i-1][1]+left[i-1][3]/2,x-8,y+h/2,"pool"))
    for i,(x,y,w,h,label_) in enumerate(right):
        parts.append(stack(f"unet-up-{i}",x,y,w,h,3,"green" if i<2 else "gold",label_))
        px,py,pw,ph,_=left[-1] if i==0 else right[i-1]
        parts.append(arrow(f"unet-up-edge-{i}",px+pw+12,py+ph/2,x-8,y+h/2,"up"))
    for i in range(3):
        lx,ly,lw,lh,_=left[i]; rx,ry,rw,rh,_=right[2-i]
        parts.append(path(f"M{lx+lw},{ly+20} C{lx+lw+90},{125+i*18} {rx-90},{125+i*18} {rx},{ry+20}","violet-line dash",'marker-end="url(#arrow-violet)"'))
    parts += [text(390,130,"copy & concatenate","small strong"),text(600,555,"contracting path","small muted"),text(940,555,"expanding path","small muted")]
    return svg("U-Net architecture", "Contracting path, expanding path, and skip concatenations after Ronneberger et al. (2015)",parts,metadata="Source: U-Net, Figure 1; semantic redraw.")


def paper_transformer() -> str:
    parts=[text(1125,103,"SEMANTIC REDRAW","paper-note"),text(300,135,"ENCODER × N","small strong"),text(860,135,"DECODER × N","small strong")]
    enc=[("Input embed","+ position","blue"),("Self-attention","multi-head","violet"),("Add & norm","residual","slate"),("Feed forward","position-wise","green"),("Add & norm","residual","slate")]
    dec=[("Output embed","shifted right","blue"),("Masked attention","causal","violet"),("Add & norm","residual","slate"),("Cross-attention","encoder memory","gold"),("Add & norm","residual","slate"),("Feed forward","position-wise","green")]
    for i,(a,b,tone) in enumerate(enc):
        y=515-i*78; parts.append(box(f"transformer-enc-{i}",170,y,260,58,a,b,tone,12,"small strong"))
        if i: parts.append(arrow(f"transformer-enc-edge-{i}",300,y+58,300,y+78))
    for i,(a,b,tone) in enumerate(dec):
        y=540-i*70; parts.append(box(f"transformer-dec-{i}",730,y,260,54,a,b,tone,12,"small strong"))
        if i: parts.append(arrow(f"transformer-dec-edge-{i}",860,y+54,860,y+70))
    parts += [path("M430,220 C560,170 650,170 730,300","wire2",'marker-end="url(#arrow-blue)"'),text(590,170,"K,V memory","tiny muted"),arrow("transformer-output",860,190,860,135),box("transformer-linear",1030,150,130,100,"Linear","softmax","red")]
    return svg("Transformer encoder–decoder", "Compact semantic redraw after Vaswani et al. (2017), Figure 1",parts,metadata="Source: Attention Is All You Need, Figure 1; semantic redraw.")


def paper_neural_ode() -> str:
    parts=[text(1125,103,"SEMANTIC REDRAW","paper-note"),text(230,145,"DISCRETE DEPTH","small strong"),text(825,145,"CONTINUOUS DEPTH","small strong")]
    for i in range(6):
        x=105+i*75; y=440-42*i+8*math.sin(i); parts += [circle(x,y,17,"node"),text(x,y+6,f"h{i}","tiny strong")]
        if i: parts.append(arrow(f"ode-discrete-{i}",105+(i-1)*75,440-42*(i-1)+8*math.sin(i-1),x-18,y+10))
    parts += [text(295,505,"hₜ₊₁ = hₜ + f(hₜ, θₜ)","small muted"),path("M650,455 C730,410 740,250 840,290 C940,330 980,210 1080,190","violet-line",'marker-end="url(#arrow-violet)"'),circle(650,455,17,"dot-blue"),circle(1080,190,17,"dot-red"),text(650,500,"h(t₀)","small strong"),text(1080,160,"h(t₁)","small strong"),text(850,505,"dh/dt = f(h(t), t, θ)","small muted"),group("ode-evaluation-points",[circle(x,y,5,"dot-violet") for x,y in [(715,402),(765,308),(835,287),(905,307),(970,268),(1025,218)]])]
    return svg("Neural ODE: discrete to continuous depth", "Adaptive continuous-depth computation after Chen et al. (2018)",parts,metadata="Source: Neural Ordinary Differential Equations; semantic redraw.")


def paper_simclr() -> str:
    parts=[text(1125,103,"SEMANTIC REDRAW","paper-note"),box("simclr-image",50,280,130,100,"Image","x","slate"),box("simclr-aug-a",270,165,160,90,"Augment t","xᵢ","blue"),box("simclr-aug-b",270,410,160,90,"Augment t′","xⱼ","violet"),box("simclr-encoder-a",525,165,170,90,"Encoder f","hᵢ","green"),box("simclr-encoder-b",525,410,170,90,"Encoder f","hⱼ","green"),box("simclr-project-a",790,165,170,90,"Project g","zᵢ","gold"),box("simclr-project-b",790,410,170,90,"Project g","zⱼ","gold"),box("simclr-loss",1030,285,130,100,"NT-Xent","maximize sim","red")]
    parts += [arrow("simclr-input-a",180,330,270,210,bend=-45),arrow("simclr-input-b",180,330,270,455,bend=45),arrow("simclr-ae",430,210,525,210),arrow("simclr-be",430,455,525,455),arrow("simclr-ap",695,210,790,210),arrow("simclr-bp",695,455,790,455),arrow("simclr-al",960,210,1030,330,bend=25),arrow("simclr-bl",960,455,1030,350,bend=-25)]
    return svg("SimCLR framework", "Two augmented views, shared encoder, projection head, and contrastive objective",parts,metadata="Source: A Simple Framework for Contrastive Learning, Figure 2; semantic redraw.")


def paper_ddpm() -> str:
    parts=[text(1125,103,"SEMANTIC REDRAW","paper-note")]
    xs=[85,300,515,730,945]; tones=["blue","cyan","violet","red","slate"]
    for i,(x,tone) in enumerate(zip(xs,tones)):
        parts.append(box(f"ddpm-state-{i}",x,250,150,140,f"x{i if i<4 else 'T'}",f"noise {i*25}%",tone))
        dots=[]
        for j in range(12):
            px=x+25+(j%4)*33; py=290+(j//4)*32; opacity=max(.18,1-i*.18)
            dots.append(f'<circle cx="{px}" cy="{py}" r="5" fill="#3972d5" opacity="{opacity:.2f}"/>')
        parts.append(group(f"ddpm-particles-{i}",dots))
        if i:
            parts.append(arrow(f"ddpm-forward-{i}",xs[i-1]+150,285,x,285,"q",css="red-line"))
            parts.append(arrow(f"ddpm-reverse-{i}",x,365,xs[i-1]+150,365,"pθ",css="violet-line",marker="arrow-violet"))
    parts += [text(600,180,"forward diffusion: add Gaussian noise","small strong"),text(600,470,"learned reverse process: denoise step by step","small strong")]
    return svg("Denoising diffusion process", "Forward noising and learned reverse transitions after Ho et al. (2020)",parts,metadata="Source: Denoising Diffusion Probabilistic Models; semantic redraw.")


def paper_vit() -> str:
    parts=[text(1125,103,"SEMANTIC REDRAW","paper-note")]
    grid=[]
    for r in range(4):
        for c in range(4):
            tone=["#d9e8ff","#e9e1ff","#dff4ed","#ffebe9"][(r+c)%4]
            grid.append(f'<rect x="{65+c*48}" y="{220+r*48}" width="44" height="44" rx="5" fill="{tone}" stroke="#71819a"/>')
    parts += [group("vit-image-patches",grid),text(160,445,"image patches","small muted"),arrow("vit-patch-arrow",270,315,380,315),stack("vit-token-stack",390,225,145,180,5,"violet","patch tokens"),text(462,445,"+ [class] + position","tiny muted"),arrow("vit-transformer-arrow",570,315,680,315),box("vit-transformer",680,220,220,190,"Transformer","encoder × L","blue"),arrow("vit-head-arrow",900,315,995,315),box("vit-head",995,265,165,100,"MLP head","class logits","gold")]
    return svg("Vision Transformer", "Patchify, embed, encode, and classify after Dosovitskiy et al. (2020)",parts,metadata="Source: An Image is Worth 16x16 Words, Figure 1; semantic redraw.")


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
    Asset("lenet-5","LeNet-5 architecture","paper",("cnn","architecture","classic"),paper_lenet,"semantic-redraw","Gradient-Based Learning Applied to Document Recognition","https://yann.lecun.com/exdb/publis/pdf/lecun-98.pdf","Figure 2","Modern semantic redraw; no original artwork or measured data copied."),
    Asset("alexnet","AlexNet architecture","paper",("cnn","imagenet","architecture"),paper_alexnet,"semantic-redraw","ImageNet Classification with Deep Convolutional Neural Networks","https://papers.nips.cc/paper_files/paper/2012/hash/c399862d3b9d6b76c8436e924a68c45b-Abstract.html",None,"Compact semantic redraw of the reported five-convolution/three-fully-connected architecture."),
    Asset("vae","Variational autoencoder","paper",("vae","latent","reparameterization"),paper_vae,"semantic-redraw","Auto-Encoding Variational Bayes","https://arxiv.org/abs/1312.6114",None,"Original diagram of the paper's inference, reparameterization, and generative semantics."),
    Asset("gan","Generative adversarial network","paper",("gan","generator","discriminator"),paper_gan,"semantic-redraw","Generative Adversarial Networks","https://arxiv.org/abs/1406.2661",None,"Original diagram of the paper's two-player minimax framework."),
    Asset("resnet-block","Residual learning block","paper",("resnet","residual","skip"),paper_resnet,"semantic-redraw","Deep Residual Learning for Image Recognition","https://arxiv.org/abs/1512.03385","Figure 2","Modern editable redraw of the residual building-block semantics."),
    Asset("unet","U-Net architecture","paper",("unet","segmentation","skip"),paper_unet,"semantic-redraw","U-Net: Convolutional Networks for Biomedical Image Segmentation","https://arxiv.org/abs/1505.04597","Figure 1","Simplified semantic redraw of contracting, expanding, and skip paths."),
    Asset("transformer","Transformer encoder–decoder","paper",("transformer","attention","encoder-decoder"),paper_transformer,"semantic-redraw","Attention Is All You Need","https://arxiv.org/abs/1706.03762","Figure 1","Compact semantic redraw preserving block order and cross-attention."),
    Asset("neural-ode","Neural ODE","paper",("ode","continuous-depth","solver"),paper_neural_ode,"semantic-redraw","Neural Ordinary Differential Equations","https://arxiv.org/abs/1806.07366",None,"Original comparison of discrete residual updates and continuous dynamics."),
    Asset("simclr","SimCLR framework","paper",("contrastive","augmentation","representation"),paper_simclr,"semantic-redraw","A Simple Framework for Contrastive Learning of Visual Representations","https://arxiv.org/abs/2002.05709","Figure 2","Semantic redraw preserving paired augmentation, shared encoder, projection, and loss."),
    Asset("ddpm","Denoising diffusion process","paper",("diffusion","denoising","markov"),paper_ddpm,"semantic-redraw","Denoising Diffusion Probabilistic Models","https://arxiv.org/abs/2006.11239",None,"Original particle-based depiction of the paper's forward and reverse processes."),
    Asset("vit","Vision Transformer","paper",("vit","patches","transformer"),paper_vit,"semantic-redraw","An Image is Worth 16x16 Words","https://arxiv.org/abs/2010.11929","Figure 1","Simplified semantic redraw of patchification, token encoding, and classification."),
    Asset("double-descent","Double descent","curve",("double-descent","capacity","generalization"),curve_double_descent,"illustrative-normalized","Reconciling modern machine learning practice and the bias-variance trade-off","https://arxiv.org/abs/1812.11118",None,"Analytic normalized trend; not digitized or claimed as original measurements."),
    Asset("scaling-law","Neural scaling laws","curve",("scaling-law","power-law","loss"),curve_scaling_law,"illustrative-normalized","Scaling Laws for Neural Language Models","https://arxiv.org/abs/2001.08361",None,"Normalized log-log trends; slopes are illustrative, not fitted paper values."),
    Asset("cyclical-lr","Cyclical learning rate","curve",("learning-rate","schedule","triangular"),curve_cyclical_lr,"formula-derived","Cyclical Learning Rates for Training Neural Networks","https://arxiv.org/abs/1506.01186",None,"Generated directly from a triangular cyclical schedule."),
    Asset("cosine-restarts","Cosine warm restarts","curve",("learning-rate","cosine","restart"),curve_cosine_restarts,"formula-derived","SGDR: Stochastic Gradient Descent with Warm Restarts","https://arxiv.org/abs/1608.03983",None,"Generated from cosine annealing with increasing restart periods."),
    Asset("diffusion-schedules","Diffusion schedules","curve",("diffusion","noise-schedule","cosine"),curve_diffusion_schedules,"formula-derived","Improved Denoising Diffusion Probabilistic Models","https://arxiv.org/abs/2102.09672",None,"Cosine cumulative signal curve generated from the published schedule form."),
    Asset("grokking","Grokking dynamics","curve",("grokking","generalization","training"),curve_grokking,"illustrative-normalized","Grokking: Generalization Beyond Overfitting on Small Algorithmic Datasets","https://arxiv.org/abs/2201.02177",None,"Normalized conceptual timing; not digitized or claimed as experiment data."),
)


def build_manifest(assets: Iterable[Asset]) -> dict[str, object]:
    records=[]
    for asset in assets:
        records.append({
            "id": asset.slug,
            "title": asset.title,
            "category": asset.category,
            "path": asset.relative_path,
            "tags": list(asset.tags),
            "reproduction": asset.reproduction,
            "source": None if asset.source_title is None else {"title":asset.source_title,"url":asset.source_url,"figure":asset.source_figure},
            "note": asset.note,
            "editable": {"format":"svg","text_as_text":True,"named_groups":True,"embedded_raster":False},
            "reproduce": f"python scripts/generate_gallery.py --only {asset.slug}",
        })
    return {"schema_version":1,"license":"Generator code and generic primitives are MIT. Paper-inspired semantic redraws include citations; source papers retain their rights, and downstream reuse requirements must be checked.","assets":records}


def generate(output_root: Path = DEFAULT_ASSET_ROOT, selected: set[str] | None = None) -> list[Path]:
    chosen=[asset for asset in ASSETS if selected is None or asset.slug in selected]
    if selected:
        unknown=selected-{asset.slug for asset in ASSETS}
        if unknown:
            raise ValueError(f"Unknown asset ids: {', '.join(sorted(unknown))}")
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
