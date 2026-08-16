/* Assemble the four phones. */

function topbarHTML() {
  return `<div class="topbar">
    <span>ROUND 6/14 <span class="ph">· PLAYER PHASE</span></span>
    <span class="ph">LANDER R8 · O2 5/7</span>
  </div>`;
}

/* Action list — real basic actions + costs from the rulebook corpus.
   Blocked entries show a reason, never disappear. */
function actionsHTML(mode) {
  const rows = mode === 'target'
    ? [['Move', '1 card', '', true],
       ['Cancel targeting', '—', '', true]]
    : [['Move', '1 card', '', true],
       ['Move Cautiously', '2 cards', '', true],
       ['Shot', '1 card', 'No Ranged Weapon in Hand', false],
       ['Melee Attack', '1 card', 'No Intruder in your Room', false],
       ['Secure the Room', '1 card', '', true],
       ['Use the Room', '2 cards', 'Room has Malfunction', false],
       ['Trade', '1 card', 'No other Character here', false],
       ['Pass', '0 cards', '', true]];
  return `<div class="chrome">
    <ul class="acts" aria-label="Actions">
      ${rows.map(([n, c, why, on]) =>
        `<li class="${on ? 'on' : ''}"><span>${n}${why ? ` <span class="why">${why}</span>` : ''}</span><span class="cost">${c}</span></li>`).join('')}
    </ul>
    <div class="drawer-peek">\u25B2 CARDS \u2014 5 IN HAND · DECK 3 · DISCARD 2</div>
  </div>`;
}

function focusedHTML() {
  const r = ROOMS.find(x => x.id === 'storageRoom');
  const occ = [];
  for (const c of r.chars) occ.push(`<span class="oc${c.you ? ' you' : ''}">${c.c}${c.egg ? '<i class="egg">EGG</i>' : ''}</span>`);
  for (const g of r.intruders) occ.push(`<span class="oc itr">${g.n}\u00D7${g.k === 'ADT' ? 'ADULT' : g.k === 'LRV' ? 'LARVA' : g.k}</span>`);
  return `<div class="viewport"><div class="focus-wrap">
    <div class="focus-hex" role="group" aria-label="Storage Room, focused view">
      <span class="zone-haz"><span class="tk fire">\u25B2 FIRE</span><span class="tk mal">\u2716 MALFUNCTION</span></span>
      <span class="zone-occ">${occ.join('')}</span>
      <span class="zone-mk"><span class="it">RED</span><span class="it">GREEN</span><span class="it">BLUE</span></span>
      <span class="focus-eff"><b>STORAGE ROOM · SECTION B · USE (2 CARDS)</b>
        Draw 2 Items of any type, keep 1, discard the other.</span>
    </div>
    <span class="focus-adj" style="left:14px;top:14px">W: corridor 3 — no noise</span>
    <span class="focus-adj" style="right:14px;top:14px">NE: corridor 4 — 1\u00D7DRN</span>
    <span class="focus-adj" style="left:14px;bottom:14px">SW: unexplored corridor 2</span>
    <span class="focus-adj" style="right:14px;bottom:14px">E: corridor 2 — Noise marker</span>
  </div></div>`;
}

function phone(el, inner, mode) {
  el.insertAdjacentHTML('beforeend', topbarHTML() + inner + actionsHTML(mode));
}

phone(document.getElementById('p1'), `<div class="viewport">${fieldHTML(FAR, 'far')}</div>`);
phone(document.getElementById('p2'), `<div class="viewport scroll">${fieldHTML(NEAR, 'near')}</div>`);
phone(document.getElementById('p3'), `<div class="viewport">${fieldHTML(FAR, 'target')}</div>`, 'target');
phone(document.getElementById('p4'), focusedHTML());

document.getElementById('btn-gray').addEventListener('click', e => {
  const on = document.body.classList.toggle('gray');
  e.target.setAttribute('aria-pressed', String(on));
});
