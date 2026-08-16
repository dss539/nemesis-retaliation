/* Field renderer: sockets, tiles, seams, corridors, four view modes. */

function hexPos(G, x, y) {
  return {
    px: x * G.STEP_X + (y % 2 ? G.STEP_X / 2 : 0),
    py: y * G.STEP_Y
  };
}
function hexCentre(G, x, y) {
  const p = hexPos(G, x, y);
  return { cx: p.px + G.HEX_W / 2, cy: p.py + G.HEX_H / 2 };
}
function fieldSize(G) {
  return { w: 4 * G.STEP_X + G.HEX_W + G.STEP_X / 2, h: 4 * G.STEP_Y + G.HEX_H };
}

/* Two bright straight VERTICAL seam lines dividing the field into thirds
   (verified from official playmat photo: seams at ≈0.38 and ≈0.63 of mat
   width, near-vertical). Positioned midway between the section column bands,
   through the corridor space. */
function seamSVG(G) {
  const sz = fieldSize(G);
  // boundary between effective columns 1.5|2 (A|B) and 3|3.5 (B|C):
  // even rows have centres at x, odd rows at x+0.5 — the seam sits at the
  // constant effective-column values 1.75 and 3.25.
  const xa = G.HEX_W / 2 + 1.25 * G.STEP_X;
  const xb = G.HEX_W / 2 + 2.75 * G.STEP_X;
  return `<line class="seam" x1="${xa}" y1="0" x2="${xa}" y2="${sz.h}"/>` +
         `<line class="seam" x1="${xb}" y1="0" x2="${xb}" y2="${sz.h}"/>`;
}

/* One corridor piece: passage body at mat-true width (G.BODY ≈ 0.78 × hex),
   printed noise value at the midpoint, tokens on top. */
function corridorPiece(G, A, Bc, L, out) {
  const p = hexCentre(G, A.x, A.y), q = Bc;
  const dx = q.cx - p.cx, dy = q.cy - p.cy, len = Math.hypot(dx, dy);
  const ux = dx / len, uy = dy / len, nx = -uy, ny = ux;
  const x1 = p.cx + ux * G.APOTHEM, y1 = p.cy + uy * G.APOTHEM;
  const x2 = q.cx - ux * G.APOTHEM, y2 = q.cy - uy * G.APOTHEM;
  const mx = (x1 + x2) / 2, my = (y1 + y2) / 2;
  const un = L.unexplored ? ' un' : '';
  // Passage body: filled slab + outline, same edge weight as a room.
  out.s += `<path class="crbo${un}" stroke-width="${G.BODY + 5}" d="M${x1} ${y1} ${x2} ${y2}"/>` +
           `<path class="crbf${un}" stroke-width="${G.BODY}" d="M${x1} ${y1} ${x2} ${y2}"/>`;
  // Printed corridor Noise value — always visible, like the physical print.
  if (L.val != null) {
    const vs = G.HEX_W < 80 ? 10 : 15;
    // shifted off-centre along the corridor so markers/intruders keep the middle;
    // pushed further out when intruders occupy the corridor
    const k = L.intruders ? 0.42 : 0.30;
    const vx = mx - ux * G.GAP * k, vy = my - uy * G.GAP * k;
    out.s += `<text class="cval${un}" font-size="${vs}" x="${vx}" y="${vy + vs * 0.36}" text-anchor="middle">${L.val}</text>`;
  }
  if (L.door) {
    const sc2 = G.HEX_W < 80 ? 0.72 : 1;
    const at = L.door.at === L.a ? { x: x1, y: y1, s: 1 } : { x: x2, y: y2, s: -1 };
    const dcx = at.x + ux * 8 * sc2 * at.s, dcy = at.y + uy * 8 * sc2 * at.s, hw = (G.BODY / 2) * 0.92;
    out.s += `<line class="door ${L.door.state}" x1="${dcx + nx * hw}" y1="${dcy + ny * hw}" x2="${dcx - nx * hw}" y2="${dcy - ny * hw}"/>` +
             `<text class="dlbl" font-size="${G.HEX_W < 80 ? 8 : 10}" x="${dcx + ux * 12 * sc2 * at.s}" y="${dcy + uy * 12 * sc2 * at.s + 3}" text-anchor="middle">${L.door.state === 'closed' ? 'SHUT' : 'OPEN'}</text>`;
  }
  if (L.intruders) {
    const sc2 = G.HEX_W < 80 ? 0.8 : 1.1;
    let off = (L.val != null) ? G.GAP * 0.14 : 0;
    for (const g of L.intruders) {
      const gx = mx + ux * off, gy = my + uy * off, w = 32 * sc2, h = 20 * sc2;
      out.s += `<rect class="citr" x="${gx - w / 2}" y="${gy - h / 2}" width="${w}" height="${h}" rx="2"/>` +
               `<text class="citrt" font-size="${11 * sc2}" x="${gx}" y="${gy + 4 * sc2}" text-anchor="middle">${g.n}\u00D7${g.k}</text>`;
      off += 24 * sc2;
    }
  }
  if (L.noise) {   // Noise MARKER (distinct from printed value)
    const r = G.HEX_W < 80 ? 8 : 12;
    const gx = mx + ux * G.GAP * 0.28, gy = my + uy * G.GAP * 0.28;
    out.s += `<circle class="no" cx="${gx}" cy="${gy}" r="${r}"/>` +
             `<text class="nt" font-size="${r + 1}" x="${gx}" y="${gy + r * 0.4}" text-anchor="middle">N</text>`;
  }
}

function corridorSVG(G, opts) {
  const out = { s: seamSVG(G) };
  for (const L of LINKS) {
    const A = ROOMS.find(r => r.id === L.a), B = ROOMS.find(r => r.id === L.b);
    if (!A || !B || !isAdjacent(A, B)) continue;   // hard adjacency guard
    corridorPiece(G, A, hexCentre(G, B.x, B.y), L, out);
  }
  for (const S of STUBS) {
    const A = ROOMS.find(r => r.id === S.from);
    if (!A || !isAdjacent(A, S.to)) continue;
    corridorPiece(G, A, hexCentre(G, S.to.x, S.to.y), { ...S, a: S.from, unexplored: true }, out);
  }
  const sz = fieldSize(G);
  return `<svg class="cor" viewBox="0 0 ${sz.w} ${sz.h}" width="${sz.w}" height="${sz.h}" aria-hidden="true">${out.s}</svg>`;
}

/* Room tile / socket at one slot. mode: 'far' | 'near' | 'target' */
function hexHTML(G, slot, mode) {
  const r = roomAt(slot.x, slot.y);
  const p = hexPos(G, slot.x, slot.y);
  const style = `left:${p.px}px;top:${p.py}px;width:${G.HEX_W}px;height:${G.HEX_H}px`;
  const sec = sectionOf(slot.x, slot.y);

  if (!r) {   // unexplored printed socket, jigsaw nubs
    const exp = mode === 'target' && EXPLORE_TARGETS.some(t => t.x === slot.x && t.y === slot.y);
    return `<div class="hx socket${exp ? ' tgt' : ''}" style="${style}">
      <button type="button" aria-label="Empty socket, Section ${sec}.${exp ? ' Legal exploration destination.' : ''}"${exp ? '' : ' tabindex="-1" aria-disabled="true"'}>
        <span class="nub n1"></span><span class="nub n2"></span>
        ${exp ? '<span class="go">EXPLORE</span>' : ''}
      </button></div>`;
  }

  const isTgt = mode === 'target' && MOVE_TARGETS.includes(r.id);
  const here = (r.chars || []).some(c => c.you);
  const mute = mode === 'target' && !isTgt && !here;
  const cls = ['hx', 'tile', here ? 'here' : '', isTgt ? 'tgt' : '', mute ? 'mute' : ''].filter(Boolean).join(' ');

  // Hazard badges — glyph + text, fixed corner zone.
  let haz = '';
  if (r.fire) haz += '<span class="tk fire">\u25B2 FIRE</span>';
  if (r.malf) haz += '<span class="tk mal">\u2716 MALF</span>';
  if (r.secure) haz += `<span class="tk sec">\u25A0 SEC ${r.secure}</span>`;

  // Occupants — center zone, cap 3 + overflow.
  const occ = [];
  for (const c of (r.chars || [])) occ.push(`<span class="oc${c.you ? ' you' : ''}">${c.c}${c.egg ? '<i class="egg" title="carrying Egg">E</i>' : ''}</span>`);
  for (const g of (r.intruders || [])) occ.push(`<span class="oc itr">${g.n}\u00D7${g.k}</span>`);
  const shown = occ.slice(0, 3);
  if (occ.length > 3) shown.push(`<span class="oc more">+${occ.length - 3}</span>`);

  // Markers zone (near only): floor items, eggs.
  let mk = '';
  if (mode !== 'far') {
    if (r.items) mk += r.items.map(i => `<span class="it">${i[0].toUpperCase()}</span>`).join('');
    if (r.eggs) mk += `<span class="tk eggm">\u25CF EGG ${r.eggs}</span>`;
  }

  const far = mode === 'far' || mode === 'target';
  const label = (`${here ? 'Your Room. ' : ''}${r.name}. Section ${r.sec}.` +
    (isTgt ? ' Legal Move destination.' : '')).replace(/"/g, '&quot;');
  return `<div class="${cls}" style="${style}">
    <button type="button" aria-label="${label}"${mute ? ' aria-disabled="true" tabindex="-1"' : ''}>
      <span class="zone-haz">${haz}</span>
      <span class="zone-occ">${far
        ? occFar(r)
        : shown.join('')}</span>
      <span class="zone-mk">${mk}</span>
      ${far ? '' : `<span class="zone-nm"><span class="nm">${r.name}</span><span class="ty">SECTION ${r.sec}</span></span>`}
      ${isTgt ? '<span class="go">MOVE</span>' : ''}
    </button></div>`;
}

/* Far-zoom occupant summary: character dots + intruder silhouette + count. */
function occFar(r) {
  let out = '';
  const cs = r.chars || [];
  if (cs.length) out += `<span class="cdots">${cs.map(c => `<i class="${c.you ? 'you' : ''}${c.egg ? ' eggd' : ''}"></i>`).join('')}</span>`;
  const n = (r.intruders || []).reduce((s, g) => s + g.n, 0);
  if (n) out += `<span class="oc itr">${n}\u00D7ITR</span>`;
  return out;
}

function fieldHTML(G, mode) {
  const sz = fieldSize(G);
  return `<div class="mapwrap">
    <div class="lsrow">
      <span class="seclbl">SECTION A <i class="ls ${LS_STATE.A.toLowerCase()}">LS ${LS_STATE.A}</i></span>
      <span class="seclbl">SECTION B <i class="ls ${LS_STATE.B.toLowerCase()}">LS ${LS_STATE.B}</i></span>
      <span class="seclbl">SECTION C <i class="ls ${LS_STATE.C.toLowerCase()}">LS ${LS_STATE.C}</i></span>
    </div>
    <div class="field" style="width:${sz.w}px;height:${sz.h}px">
      ${corridorSVG(G, { tiny: G === FAR })}
      ${SLOTS.map(s => hexHTML(G, s, mode)).join('')}
    </div>
  </div>`;
}
