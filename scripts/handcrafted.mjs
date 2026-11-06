/** Native scientific figure primitives for an available @oai/artifact-tool runtime.
 * See assets/examples/handcrafted-usage.mjs. Not a bundled renderer/runtime.
 * Coordinates are canvas pixels. Paths are editable freeforms, not auto-attached
 * Office connectors: reroute their explicit endpoints when moving a node.
 */
import fs from 'node:fs/promises';
import { Presentation, PresentationFile } from '@oai/artifact-tool';

const profile = JSON.parse(await fs.readFile(new URL('../assets/styles/handcrafted-paper.json', import.meta.url), 'utf8'));
export const defaultStyle = { font: profile.font, ...profile.colors };

export function createFigure(width, height, style = {}) {
  const c = { ...defaultStyle, ...style };
  const p = Presentation.create({ slideSize: { width, height } });
  const s = p.slides.add();
  s.background.fill = c.paper;
  const ids = new Set();
  function unique(id) {
    if (!id || ids.has(id)) throw new Error(`Missing or duplicate object ID: ${id}`);
    ids.add(id);
  }
  function shape(id, x, y, w, h, fill = 'none', stroke = 'none', lw = 0, geometry = 'rect') {
    unique(id);
    return s.shapes.add({ name: id, geometry, position: { left: x, top: y, width: w, height: h }, fill, line: { fill: stroke, width: lw } });
  }
  function path(id, points, { color = c.ink, lw = 2.4, fill = 'none', closed = false, dashed = false } = {}) {
    unique(id);
    if (points.length < 2 || points.some(a => a.length !== 2 || a.some(v => !Number.isFinite(v)))) throw new Error('Invalid path coordinates');
    const x = Math.min(...points.map(a => a[0])), y = Math.min(...points.map(a => a[1]));
    const w = Math.max(.1, Math.max(...points.map(a => a[0])) - x), h = Math.max(.1, Math.max(...points.map(a => a[1])) - y);
    const commands = points.map((a, i) => ({ [i ? 'lineTo' : 'moveTo']: { x: a[0] - x, y: a[1] - y } }));
    if (closed) commands.push({ close: {} });
    return s.shapes.add({ name: id, geometry: 'custom', position: { left: x, top: y, width: w, height: h }, fill,
      line: { fill: color, width: lw, style: dashed ? 'dashed' : 'solid' }, customPaths: [{ width: w, height: h, commands }] });
  }
  function text(id, content, x, y, w, h, { size = 32, bold = false, color = c.ink, align = 'center' } = {}) {
    const q = shape(id, x, y, w, h, 'none', 'none', 0, 'textbox');
    q.text = content;
    q.text.style = { typeface: c.font, fontSize: size, bold, color, alignment: align,
      verticalAlignment: 'middle', wrap: 'none', autoFit: 'none', insets: 0 };
    return q;
  }
  function box(id, x, y, w, h, { fill = c.paper, color = c.ink, lw = 2.4 } = {}) {
    const e = Math.min(width / 2400, w / 40, h / 20);
    // One filled path avoids a rectangular fill peeking outside a chamfered outline.
    return path(id, [[x+10*e,y+e],[x+w*.48,y-e],[x+w-10*e,y+e],[x+w,y+10*e],
      [x+w-e,y+h*.52],[x+w+e,y+h-10*e],[x+w-10*e,y+h],[x+w*.46,y+h+e],
      [x+10*e,y+h-e],[x,y+h-10*e],[x+e,y+10*e]], { color, lw, fill, closed: true });
  }
  function arrow(id, points, { color = c.ink, lw = 3, dashed = false, halo = false, head = 13 } = {}) {
    if (points.length < 2) throw new Error('Arrow requires at least two points');
    const b = points.at(-1), a = points.at(-2);
    if (a[0] === b[0] && a[1] === b[1]) throw new Error('Arrow terminal segment has zero length');
    if (halo) path(id+'-halo', points, { color: c.paper, lw: lw+7 });
    path(id, points, { color, lw, dashed });
    const t = Math.atan2(b[1]-a[1], b[0]-a[0]);
    return path(id+'-head', [[b[0]-head*Math.cos(t-.48), b[1]-head*Math.sin(t-.48)], b,
      [b[0]-head*Math.cos(t+.48), b[1]-head*Math.sin(t+.48)]], { color, lw });
  }
  async function picture(id, file, x, y, w, h, { radius = 0, fit = 'contain', alt = id } = {}) {
    unique(id);
    const ext = file.split('.').pop().toLowerCase();
    if (!['png','jpg','jpeg'].includes(ext)) throw new Error('Use PNG/JPEG photos; keep diagrams native');
    return s.images.add({ name: id, blob: new Uint8Array(await fs.readFile(file)),
      contentType: ext === 'png' ? 'image/png' : 'image/jpeg', alt, fit,
      position: { left: x, top: y, width: w, height: h }, ...(radius ? { geometry: 'roundRect', borderRadius: radius } : {}) });
  }
  async function save(pptxPath, { previewPath, notes = '' } = {}) {
    s.speakerNotes.textFrame.setText(notes);
    await (await PresentationFile.exportPptx(p)).save(pptxPath);
    if (previewPath) await fs.writeFile(previewPath, new Uint8Array(await (await p.export({ slide: s, format: 'png', scale: 1 })).arrayBuffer()));
  }
  return { presentation: p, slide: s, style: c, shape, path, text, box, arrow, picture, save };
}

/** Dense result montage. Supply already selected chronological genuine frames.
 * groups: [{label, frames: ['/abs/frame0.png', ...]}]; all groups same count.
 * Optional mosaic: independent background photos for the separate title strip.
 * This arranges evidence; it does not establish provenance or research claims.
 */
export async function composeTeaser({ title, groups, mosaic = [], columns = 2,
  width = 2400, frameAspect = 16/9, style = {} }) {
  if (!title || !Array.isArray(groups) || !groups.length || !Number.isInteger(columns) || columns < 1 || columns > groups.length)
    throw new Error('Supply a title, nonempty groups and a valid column count');
  const count = groups[0].frames?.length;
  if (!count || groups.some(g => !g.label || !Array.isArray(g.frames) || g.frames.length !== count))
    throw new Error('Each labelled group needs the same nonzero number of chronological frame paths');
  if (!Number.isFinite(width) || width < 320 || !Number.isFinite(frameAspect) || frameAspect <= 0)
    throw new Error('Invalid canvas width or frame aspect');
  const k = width / 2400, margin = 12*k, gap = 7*k;
  const tileW = (width-2*margin-(columns*count-1)*gap)/(columns*count), tileH = tileW/frameAspect;
  const rows = Math.ceil(groups.length/columns), titleH = 150*k, split = Math.ceil(rows/2);
  const height = 2*margin+rows*tileH+(rows-1)*gap+titleH+2*gap;
  const f = createFigure(width, height, style), c = f.style;
  for (let i = 0; i < groups.length; i++) {
    const g = groups[i], row = Math.floor(i/columns), col = i%columns;
    const x = margin+col*count*(tileW+gap);
    const y = margin+row*(tileH+gap)+(row >= split ? titleH+2*gap : 0);
    for (let j=0; j<count; j++) {
      const fx = x+j*(tileW+gap);
      await f.picture(`result-${i}-${j}`, g.frames[j], fx, y, tileW, tileH, { fit: 'cover', radius: 10*k, alt: `${g.label}, temporal frame ${j+1}` });
    }
    const tabW = Math.min(count*(tileW+gap)-gap-20*k, Math.max(230*k, (g.label.length*21+32)*k));
    f.box(`capability-tab-${i}`, x+8*k, y+8*k, tabW, 57*k, { fill: c.paper+'/94', color: 'none', lw: 0 });
    f.text(`capability-label-${i}`, g.label, x+20*k, y+12*k, tabW-24*k, 44*k, { size: 37*k, bold: true, align: 'left' });
    f.path(`capability-rule-${i}`, [[x+21*k,y+62*k],[x+tabW*.5,y+64*k],[x+tabW-7*k,y+61*k]], { color: c.rust, lw: 2.7*k });
  }
  const ty = margin+split*(tileH+gap);
  if (mosaic.length) {
    const mw = (width-2*margin-(mosaic.length-1)*gap)/mosaic.length;
    for (let i=0;i<mosaic.length;i++) await f.picture(`title-mosaic-${i}`, mosaic[i], margin+i*(mw+gap),ty,mw,titleH,{ fit:'cover',radius:8*k });
  }
  f.box('title-paper', width*.19,ty+17*k,width*.62,titleH-34*k,{ fill:c.ink+'/94',color:c.paper,lw:2.4*k });
  f.text('project-title',title,width*.20,ty+15*k,width*.60,titleH-30*k,{ size:Math.min(109,1450/Math.max(title.length,1)*1.6)*k,bold:true,color:c.paper });
  return f;
}
