// Optional primitive demo; requires an existing @oai/artifact-tool environment.
// node assets/examples/handcrafted-usage.mjs /absolute/new-output-directory
// This illustrates parameterization, not a particular model's architecture.
import fs from 'node:fs/promises';
import path from 'node:path';
import { createFigure } from '../../scripts/handcrafted.mjs';
const out = process.argv[2];
if (!out) throw new Error('Supply a new output directory');
await fs.mkdir(out, { recursive: false });
const f = createFigure(1200, 600);
const c = f.style;
f.text('title', 'Low-rank adaptation', 75, 30, 1050, 65, { size: 44, bold: true });
f.text('input-label', 'x', 35, 255, 100, 50, { size: 36 });
f.box('frozen-weight', 290, 145, 530, 85, { fill: c.blueFill, color: c.blue });
f.text('weight-label', 'Frozen weight W0', 310, 158, 490, 60, { size: 32, bold: true, color: c.blue });
f.box('adapter-a', 290, 355, 190, 85, { fill: c.rustFill, color: c.rust });
f.box('adapter-b', 630, 355, 190, 85, { fill: c.rustFill, color: c.rust });
f.text('a-label', 'A', 310, 365, 150, 65, { size: 36, bold: true });
f.text('b-label', 'B', 650, 365, 150, 65, { size: 36, bold: true });
f.text('adapter-status', 'Trainable A, B', 420, 460, 270, 45, { size: 27, color: c.rust });
f.shape('sum-circle', 940, 260, 60, 60, c.paper, c.ink, 2.4, 'ellipse');
f.text('sum-label', '+', 940, 260, 60, 60, { size: 35 });
f.arrow('to-base', [[135,280],[220,280],[220,187],[290,187]], { color: c.blue });
f.arrow('to-adapter', [[220,280],[220,397],[290,397]], { color: c.rust });
f.shape('shared-input-junction', 216, 276, 8, 8, c.ink, 'none', 0, 'ellipse');
f.arrow('a-to-b', [[480,397],[630,397]], { color: c.rust });
f.arrow('base-to-sum', [[820,187],[970,187],[970,260]], { color: c.blue });
f.arrow('adapter-to-sum', [[820,397],[970,397],[970,320]], { color: c.rust });
f.arrow('sum-to-output', [[1000,290],[1090,290]]);
f.text('output-label', 'W0 x + B(Ax)', 800, 485, 350, 55, { size: 30 });
await f.save(path.join(out,'native-demo.pptx'), { previewPath: path.join(out,'native-demo.png'), notes: 'Illustrative standard low-rank parameterization. No experimental results.' });
