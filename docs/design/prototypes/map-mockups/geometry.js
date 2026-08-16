/* Map mockup geometry + fixture data.
   Derived, not hand-tuned (see docs/design/play-area-design.md + corpus geometry notes):
   regular pointy-top hex, equal corridor gap on all six edges requires
   STEP_Y = STEP_X * sqrt(3)/2, and HEX_H = HEX_W * 2/sqrt(3). */

/* Corridor proportions measured from official flat rulebook map pages
   (art-references/official-manual/.../page-019.jpg, 15 detected room hexes):
     centre-to-centre step  = 1.68 × hex width  (pairs clustered 1.65–1.74)
     => corridor gap length = 0.68 × hex width
     corridor body width    = 0.78 × hex width  (perpendicular wall-to-wall
                              profile at corridor midpoint: 38–41px vs 49px room)
   Corridors are stubby passages nearly as wide as rooms — not connector lines. */
const STEP_RATIO = 1.68;
const BODY_RATIO = 0.78;

function makeGeom(HEX_W) {
  const HEX_H = HEX_W * 2 / Math.sqrt(3);
  const STEP_X = HEX_W * STEP_RATIO;
  const STEP_Y = STEP_X * Math.sqrt(3) / 2;
  const APOTHEM = HEX_W / 2;
  const GAP = STEP_X - HEX_W;
  const BODY = HEX_W * BODY_RATIO;
  return { HEX_W, HEX_H, STEP_X, STEP_Y, APOTHEM, GAP, BODY };
}
const FAR = makeGeom(45);    // field = 4.5*75.6+45 ≈ 385px — fits 390 at mat-true proportions
const NEAR = makeGeom(116);  // gap ≈ 79px, body ≈ 90px — corridor holds door + 6 intruders + value

/* 23-slot fixed field, 5/4/5/4/5, odd rows offset half a step right
   (matches GAME_DATA.CONFIG.boardSlots + neighborPosition in js/data.js). */
const SLOTS = [];
for (let y = 0; y < 5; y++) {
  const cols = y % 2 === 0 ? 5 : 4;
  for (let x = 0; x < cols; x++) SLOTS.push({ x, y });
}

/* Section partition — VERIFIED vertical thirds.
   Official playmat photo (art-references/official-gamefound/update-35/003…jpg)
   shows two long near-vertical bright seams at x ≈ 0.38 and 0.63 of the mat
   (Hough/component detection, elongation 12-15, angles 88.5°-92.4°), i.e. the
   seams are straight vertical lines dividing the field into thirds:
   A = west, B = middle, C = east. Player-confirmed. Membership uses the
   rendered centre column (odd rows sit half a step right). Exact membership
   of boundary slots remains approximate. */
function sectionOf(x, y) {
  const c = x + (y % 2 ? 0.5 : 0);   // effective column of the slot centre
  if (c < 1.25) return 'A';
  if (c < 2.75) return 'B';
  return 'C';
}

function neighbours(x, y) {
  const odd = y % 2 === 1;
  return {
    W: [x - 1, y], E: [x + 1, y],
    NW: [odd ? x : x - 1, y - 1], NE: [odd ? x + 1 : x, y - 1],
    SW: [odd ? x : x - 1, y + 1], SE: [odd ? x + 1 : x, y + 1]
  };
}
const isAdjacent = (a, b) => Object.values(neighbours(a.x, a.y))
  .some(([c, r]) => c === b.x && r === b.y);

/* Mid-game fixture. Room names, sections, effects, occupant codes all verbatim
   from js/data.js (characters: RCN Recon, MED Medical Support, HGO Heavy Gun
   Operator, OFC Officer; intruders: ADT Adult, DRN Drone, LRV Larva).
   Placement respects vertical section thirds: A west (LZ fixed at 0,2),
   B middle (Hibernatorium fixed at 2,0), C east (Nest, Reactor). */
const ROOMS = [
  { id: 'landingZone', x: 0, y: 2, name: 'Landing Zone', sec: 'A',
    chars: [{ c: 'OFC' }] },
  { id: 'drillingRoom', x: 1, y: 2, name: 'Drilling Room', sec: 'A', fire: true },
  { id: 'lifeSupportControlA', x: 0, y: 1, name: 'Life Support "A"', sec: 'A' },
  { id: 'armory', x: 1, y: 1, name: 'Armory', sec: 'A' },
  { id: 'hibernatorium', x: 2, y: 0, name: 'Hibernatorium', sec: 'B' },
  { id: 'coolingSystem', x: 2, y: 1, name: 'Cooling System', sec: 'B', malf: true },
  { id: 'serverRoom', x: 2, y: 3, name: 'Server Room', sec: 'B', secure: 2 },
  { id: 'storageRoom', x: 2, y: 2, name: 'Storage Room', sec: 'B',
    fire: true, malf: true,
    chars: [{ c: 'RCN', you: true }, { c: 'MED', egg: true }, { c: 'HGO' }],
    intruders: [{ k: 'ADT', n: 2 }, { k: 'LRV', n: 1 }],
    items: ['red', 'green', 'blue'],
    effect: 'Draw 2 Items of any type, keep 1, discard the other.' },
  { id: 'reactor', x: 3, y: 2, name: 'Reactor', sec: 'C' },
  { id: 'nest', x: 3, y: 3, name: 'The Nest', sec: 'C',
    intruders: [{ k: 'ADT', n: 2 }], eggs: 3 }
];
const roomAt = (x, y) => ROOMS.find(r => r.x === x && r.y === y);

/* Corridors: adjacent pairs only (hard-guarded at render time).
   val = the corridor's PRINTED Noise value (1-4, physical print — always visible;
   engine deals these from CORRIDOR_VALUES in js/data.js).
   noise = a Noise MARKER placed on the corridor (distinct fact).
   door.at = endpoint room the Door slot touches; text label, never colour alone. */
const LINKS = [
  { a: 'landingZone', b: 'drillingRoom', val: 2, door: { at: 'drillingRoom', state: 'open' } },
  { a: 'landingZone', b: 'lifeSupportControlA', val: 4 },
  { a: 'lifeSupportControlA', b: 'armory', val: 1 },
  { a: 'armory', b: 'drillingRoom', val: 3 },
  { a: 'armory', b: 'coolingSystem', val: 2, door: { at: 'coolingSystem', state: 'closed' } },
  { a: 'armory', b: 'hibernatorium', val: 1, noise: true },
  { a: 'coolingSystem', b: 'hibernatorium', val: 3 },
  { a: 'coolingSystem', b: 'storageRoom', val: 4, intruders: [{ k: 'DRN', n: 1 }] },
  { a: 'storageRoom', b: 'drillingRoom', val: 3 },
  { a: 'storageRoom', b: 'serverRoom', val: 3 },
  { a: 'storageRoom', b: 'reactor', val: 2, noise: true },
  { a: 'reactor', b: 'nest', val: 1, door: { at: 'reactor', state: 'closed' } },
  { a: 'serverRoom', b: 'nest', val: 1 }
];
/* Unexplored corridors (connected to only 1 Room — rulebook keyword). Still
   real corridor pieces with a printed value. */
const STUBS = [
  { from: 'storageRoom', to: { x: 1, y: 3 }, val: 2 },
  { from: 'reactor', to: { x: 4, y: 2 }, val: 4 },
  { from: 'hibernatorium', to: { x: 3, y: 0 }, val: 1 }
];

/* Move targeting fixture: RCN (you) in Storage Room.
   Legal: Drilling Room, Cooling System, Server Room (open corridors; the
   Drone in the cooling corridor does not make the move illegal). Reactor is
   NOT highlighted — its door is irrelevant here, but the noise-marker corridor
   is open, so include it; the Nest is not adjacent. Socket (1,3) is a legal
   exploration move via the unexplored corridor. Invalid targets omitted. */
const MOVE_TARGETS = ['drillingRoom', 'coolingSystem', 'serverRoom', 'reactor'];
const EXPLORE_TARGETS = [{ x: 1, y: 3 }];

const LS_STATE = { A: 'ACTIVE', B: 'INACTIVE', C: 'ACTIVE' };
