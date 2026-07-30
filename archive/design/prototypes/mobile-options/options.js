/* Shared HUD + three option bodies.

   BASIC ACTIONS — verbatim from rulebook p.13 with real costs:
     0 cards: Play an Action card, Pass
     1 card : Make a Move, Place Secure token, Fire a Shot, Fire a Burst,
              Melee Attack, Use an Item, Activate the Robot, Trade, Use Tactical Gear
     2 cards: Use the Room, Make a Move Cautiously

   ACTION CARDS — only names confirmed from official sources are used:
     "Sprint" (Recon, rulebook card image), "Duck and Cover" (Consultant, rulebook p.14).
   Unverified faces are labelled UNVERIFIED rather than invented, so a card can never
   be mistaken for a basic action. */

function hudHTML() {
  return `<header class="hud">
    <div class="hud-top">
      <div class="rnd"><b>R4</b><span class="sub"><i>PLAYER PHASE</i><s>Start: Recon</s></span></div>
      <div class="clockrow"><span class="chip warn">AUTO R10</span><span class="chip">LANDER R7</span></div>
      <div class="mine"><i>YOUR TURN</i><s>2 Actions</s></div>
    </div>
    <div class="hud-sys">
      <span><b>LS</b> A&#10003; B! C&times;</span>
      <span><b>EGGS</b> 3</span>
      <span><b>TASK</b> Primary Samples</span>
      <span><b>CHOICE</b> 3</span>
    </div>
    <div class="vit">
      <span class="face">RCN</span>
      <span class="who"><i>RECON</i><s>Life Support B &middot; Sprained Ankle</s></span>
      <span class="gauges">
        <span class="g"><b>7/9</b>HP<span class="pips">${'<i></i>'.repeat(7)}${'<i class="e"></i>'.repeat(2)}</span></span>
        <span class="g low"><b>2</b>O&#8322;<span class="pips low"><i></i><i></i><i class="e"></i><i class="e"></i></span></span>
      </span>
    </div>
  </header>`;
}

/* Real basic actions. cost = Action cards discarded. */
const BASIC = [
  { id:'move',    label:'Make a Move',      cost:1, why:'2 legal destinations' },
  { id:'shot',    label:'Fire a Shot',      cost:1, off:'No Intruder in your Room' },
  { id:'burst',   label:'Fire a Burst',     cost:1, why:'Corridor: 2&times;ADT' },
  { id:'melee',   label:'Melee Attack',     cost:1, off:'No Intruder in your Room' },
  { id:'secure',  label:'Place Secure',     cost:1, why:'Room allows Secure' },
  { id:'item',    label:'Use an Item',      cost:1, why:'Recon Scanner ready' },
  { id:'search',  label:'Search',           cost:1, off:'No Item icon here' },
  { id:'trade',   label:'Trade',            cost:1, off:'No Character in Room' },
  { id:'room',    label:'Use the Room',     cost:2, why:'Repair Malfunction' },
  { id:'caut',    label:'Move Cautiously',  cost:2, why:'Place 1 Secure en route' },
  { id:'play',    label:'Play an Action card', cost:0, why:'Sprint available' },
  { id:'pass',    label:'Pass',             cost:0, why:'Ends your Round' }
];

function actionRows(limit) {
  return BASIC.slice(0, limit).map(a => {
    const dis = a.off ? ' disabled' : '';
    const cls = a.off ? 'arow' : (a.cost === 2 ? 'arow hot' : 'arow');
    return `<button class="${cls}"${dis}>
      <span class="ic">${a.cost}</span>
      <span class="tx"><i>${a.label}</i><s>${a.off || a.why}</s></span>
      <span class="cost">${a.cost === 0 ? 'FREE' : a.cost + ' CARD' + (a.cost > 1 ? 'S' : '')}</span>
    </button>`;
  }).join('');
}

/* Card rail: real names where verified, explicit UNVERIFIED otherwise. */
function cardRail(cls) {
  return `<div class="${cls}" aria-label="Your hand, private">
    <button class="card"><span class="k">ACTION</span><span class="n">Sprint</span>
      <span class="ce">Move, then may spend 1 to Move again</span></button>
    <button class="card"><span class="k">ACTION &middot; REACTION</span><span class="n">Duck and Cover</span>
      <span class="ce">Discard 1 to Move; prevent 1 Attack</span></button>
    <button class="card unv"><span class="k">ACTION</span><span class="n">Unverified face</span>
      <span class="ce">Real card data not yet imported</span></button>
    <button class="card con"><span class="k">CONTAMINATION</span><span class="n">Contamination</span>
      <span class="ce">Cannot be discarded for Actions</span></button>
  </div>`;
}

/* ---------- OPTION 1: Command Deck ---------- */
function optionOne(mode) {
  const ctx = mode === 'target'
    ? `<div class="ctx act"><span><i>Make a Move &middot; pick a destination</i>
         <s>2 legal Rooms lit. Storage is hidden &mdash; Door SHUT.</s></span>
         <span class="bb"><button class="bt">Cancel</button></span></div>`
    : `<div class="ctx"><span><i>Life Support B &middot; Malfunction</i>
         <s>Use the Room repairs it. Corridor to Nest holds 2&times;ADT.</s></span></div>`;
  return `<div class="app">${hudHTML()}
    <main class="stage">${fieldHTML(mode, .3)}${zoomHTML()}</main>
    <footer class="dock">${ctx}
      <div class="acts-scroll" aria-label="Basic Actions">${actionRows(12)}</div>
      ${cardRail('rail')}
    </footer></div>`;
}

/* ---------- OPTION 2: Action Sheet over full-bleed map ---------- */
function optionTwo(mode) {
  const toast = mode === 'target'
    ? `<div class="toast"><b>Make a Move</b>Tap a lit hex. Nothing commits until you do.</div>`
    : `<div class="toast"><b>Life Support B &middot; Malfunction</b>Room effect shown because you stand here.</div>`;
  return `<div class="app">${hudHTML()}
    <main class="stage">${fieldHTML(mode, .44)}${zoomHTML()}${toast}
      <section class="floatpanel">
        <div class="fp-head"><i>ACTIONS</i><s>2 left</s></div>
        <div class="fp-body">${actionRows(12)}</div>
        <div class="fp-foot">${cardRail('mini')}</div>
      </section>
    </main></div>`;
}

/* ---------- OPTION 3: Two-Surface Sheet ---------- */
function optionThree(mode, collapsed) {
  const body = mode === 'target'
    ? `<div class="turnhead"><i>MAKE A MOVE &middot; CHOOSE DESTINATION</i>
         <s>Sheet shrinks so lit hexes stay visible.</s></div>
       <button class="arow hot"><span class="ic">1</span><span class="tx"><i>Armory</i>
         <s>Corridor clear &middot; Noise marker 1</s></span><span class="cost">1 CARD</span></button>
       <button class="arow hot"><span class="ic">1</span><span class="tx"><i>Server Room</i>
         <s>Door OPEN &middot; corridor empty</s></span><span class="cost">1 CARD</span></button>
       <button class="arow" disabled><span class="ic">&#10005;</span><span class="tx"><i>Storage</i>
         <s>Door SHUT &mdash; Movement blocked</s></span><span class="cost"></span></button>
       <button class="arow"><span class="ic">&#8592;</span><span class="tx"><i>Cancel</i>
         <s>No game state changes</s></span><span class="cost"></span></button>`
    : `<div class="turnhead"><i>YOUR TURN &middot; 2 ACTIONS LEFT</i>
         <s>Basic Actions with real rulebook costs. Blocked ones say why.</s></div>
       ${actionRows(12)}`;
  return `<div class="app">${hudHTML()}
    <main class="stage">${fieldHTML(mode, mode === 'target' ? .4 : .36)}${zoomHTML()}
      <section class="sheet ${collapsed ? 'collapsed' : ''}" style="${mode === 'target' ? 'max-height:42%' : ''}">
        <div class="grab"><i></i></div>
        <div class="sheet-tabs">
          <button class="on">ACT<span class="bdg">2 left</span></button>
          <button>HAND<span class="bdg">4</span></button>
          <button>CREW<span class="bdg">3</span></button>
          <button>LOG</button>
        </div>
        <div class="sheet-body">${body}</div>
      </section>
    </main></div>`;
}
