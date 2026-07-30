/* Hex field, corrected geometry.
   Regular pointy-top hexes. For a REGULAR hexagon the apothem (centre -> edge
   midpoint) is identical for all six edges = HEX_W/2. So if we make the E/W and
   the diagonal centre-to-centre distances equal, every one of the six edges gets
   exactly the same corridor gap.
     E/W centre distance      = STEP_X
     diagonal centre distance = hypot(STEP_X/2, STEP_Y)
   Setting them equal gives STEP_Y = STEP_X * sqrt(3)/2.
   Gap on every edge = STEP_X - HEX_W, sized to hold a Door token AND Intruders. */
const HEX_W = 124;
const HEX_H = HEX_W * 2 / Math.sqrt(3);        // 143.2 — regular
const APOTHEM = HEX_W / 2;                      // 62
const STEP_X = 190;
const STEP_Y = STEP_X * Math.sqrt(3) / 2;       // 164.5
const GAP = STEP_X - HEX_W;                     // 66px of real corridor
const ORIGIN_X = 40, ORIGIN_Y = 30;
const FIELD_W = 700, FIELD_H = 600;

function hexPos(col, row) {
  return {
    x: ORIGIN_X + col * STEP_X + (row % 2 ? STEP_X / 2 : 0),
    y: ORIGIN_Y + row * STEP_Y
  };
}
function hexCentre(col, row) {
  const p = hexPos(col, row);
  return { cx: p.x + HEX_W / 2, cy: p.y + HEX_H / 2 };
}

/* True neighbours for odd-row-shifted pointy-top layout. Corridors may ONLY
   join these pairs — a corridor never spans a non-adjacent room. */
function neighbours(col, row) {
  const odd = row % 2 === 1;
  return {
    W:  [col - 1, row],
    E:  [col + 1, row],
    NW: [odd ? col : col - 1, row - 1],
    NE: [odd ? col + 1 : col, row - 1],
    SW: [odd ? col : col - 1, row + 1],
    SE: [odd ? col + 1 : col, row + 1]
  };
}
function isAdjacent(a, b) {
  return Object.values(neighbours(a.col, a.row))
    .some(([c, r]) => c === b.col && r === b.row);
}

const ROOMS = [
  { id:'server',  col:1, row:0, name:'Server Room',    type:'Section B',
    tokens:'<span class="tk sec">SEC 2</span>' },
  { id:'armory',  col:0, row:1, name:'Armory',         type:'Unassigned',
    tokens:'<span class="tk fire">FIRE</span>' },
  { id:'life',    col:1, row:1, name:'Life Support B', type:'Section B', here:true,
    tokens:'<span class="tk mal">MALF</span><span class="oc you">RCN</span>' },
  { id:'storage', col:2, row:1, name:'Storage',        type:'Unassigned',
    tokens:'<span class="oc">MED</span>' },
  { id:'unknown', col:0, row:2, name:'?',              type:'Undiscovered', dark:true, tokens:'' },
  { id:'nest',    col:1, row:2, name:'The Nest',       type:'Section C',
    tokens:'<span class="tk fire">FIRE</span><span class="oc itr"><span>ADT</span></span>' },
  { id:'reactor', col:2, row:2, name:'Reactor',        type:'Section C', tokens:'' }
];

const TARGETS = ['armory', 'storage'];   // only legal Move destinations

/* Corridors. door: which endpoint the Door slot touches (rulebook: a Door slot
   is oriented toward the Room placed last), state open|closed.
   intruders: occupants standing IN the corridor. */
const LINKS = [
  { a:'life', b:'server',  door:{ at:'server', state:'open' } },
  { a:'life', b:'armory',  noise:'1' },
  { a:'life', b:'storage', door:{ at:'life',   state:'closed' } },
  { a:'life', b:'nest',    intruders:[{ kind:'ADT', n:2 }] },
  { a:'life', b:'reactor', unexplored:true },
  { a:'armory',b:'server' },
  { a:'armory',b:'unknown',unexplored:true },
  { a:'armory',b:'nest',   intruders:[{ kind:'CRP', n:1 }], door:{ at:'armory', state:'open' } },
  { a:'nest', b:'reactor', noise:'2' },
  { a:'storage',b:'reactor' }
];

const byId = id => ROOMS.find(r => r.id === id);

function corridorSVG() {
  let out = '';
  for (const L of LINKS) {
    const A = byId(L.a), B = byId(L.b);
    if (!A || !B) continue;
    if (!isAdjacent(A, B)) continue;            // hard guard: never span non-neighbours

    const p = hexCentre(A.col, A.row), q = hexCentre(B.col, B.row);
    const dx = q.cx - p.cx, dy = q.cy - p.cy, len = Math.hypot(dx, dy);
    const ux = dx / len, uy = dy / len;
    // start/end exactly at each hex edge -> the visible corridor is only the gap
    const x1 = p.cx + ux * APOTHEM, y1 = p.cy + uy * APOTHEM;
    const x2 = q.cx - ux * APOTHEM, y2 = q.cy - uy * APOTHEM;
    const mx = (x1 + x2) / 2, my = (y1 + y2) / 2;
    const nx = -uy, ny = ux;                     // perpendicular

    out += L.unexplored
      ? `<path class="ln un" d="M${x1} ${y1} ${x2} ${y2}"/>`
      : `<path class="ln" d="M${x1} ${y1} ${x2} ${y2}"/>` +
        `<path class="cr" d="M${x1} ${y1} ${x2} ${y2}"/>`;

    // Door: sits at the END of the corridor, flush against its Room
    if (L.door) {
      const at = L.door.at === L.a ? { x: x1, y: y1, s: 1 } : { x: x2, y: y2, s: -1 };
      const dcx = at.x + ux * 11 * at.s, dcy = at.y + uy * 11 * at.s;
      const hw = 15;
      out += `<line class="door ${L.door.state}" x1="${dcx + nx * hw}" y1="${dcy + ny * hw}"
                x2="${dcx - nx * hw}" y2="${dcy - ny * hw}"/>`;
      out += `<text class="dlbl" x="${dcx + nx * 22}" y="${dcy + ny * 22 + 3}"
                text-anchor="middle">${L.door.state === 'closed' ? 'SHUT' : 'OPEN'}</text>`;
    }

    // Intruders standing in the corridor (up to 6 per rulebook -> show a count)
    if (L.intruders) {
      let off = 0;
      for (const g of L.intruders) {
        const gx = mx + ux * off, gy = my + uy * off;
        out += `<rect class="citr" x="${gx - 15}" y="${gy - 11}" width="30" height="22" rx="2"/>` +
               `<text class="citrt" x="${gx}" y="${gy + 4}" text-anchor="middle">${g.n}\u00D7${g.kind}</text>`;
        off += 26;
      }
    }

    if (L.noise) {
      out += `<circle class="no" cx="${mx}" cy="${my}" r="12"/>` +
             `<text class="nt" x="${mx}" y="${my + 4}" text-anchor="middle">${L.noise}</text>`;
    }
  }
  return `<svg class="cor" viewBox="0 0 ${FIELD_W} ${FIELD_H}" aria-hidden="true">${out}</svg>`;
}

function hexHTML(r, mode) {
  const tgt = mode === 'target' && TARGETS.includes(r.id);
  const mute = mode === 'target' && !tgt && !r.here;
  const cls = ['hex', r.here ? 'here' : '', r.dark ? 'dark' : '',
               tgt ? 'tgt' : '', mute ? 'mute' : ''].filter(Boolean).join(' ');
  const p = hexPos(r.col, r.row);
  const label = `${r.here ? 'Your Room. ' : ''}${r.name}. ${r.type}.${tgt ? ' Legal Move destination.' : ''}`;
  return `<div class="${cls}" style="left:${p.x}px;top:${p.y}px;width:${HEX_W}px;height:${HEX_H}px">
    <button type="button" aria-label="${label}"${mute ? ' aria-disabled="true" tabindex="-1"' : ''}>
      <span><span class="nm">${r.name}</span><span class="ty">${r.type}</span></span>
      ${tgt ? '<span class="go">MOVE</span>' : `<span class="tok">${r.tokens}</span>`}
    </button></div>`;
}

function fieldHTML(mode, zoom) {
  return `<div class="field" style="--z:${zoom};width:${FIELD_W}px;height:${FIELD_H}px">
    ${corridorSVG()}${ROOMS.map(r => hexHTML(r, mode)).join('')}</div>`;
}

function zoomHTML() {
  return `<div class="zoom">
    <button type="button" aria-label="Zoom out">&minus;</button>
    <button type="button" aria-label="Zoom in">+</button>
    <button type="button" class="w">FIT</button></div>`;
}
