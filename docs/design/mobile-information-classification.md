# Mobile Information Classification

## Purpose

This document inventories the information a player can obtain from a physical base-game table and classifies it for a mobile-first digital UI.

This is an information architecture record, not a screen layout. The next design step should decide where each item lives and how it is compressed.

## Sources and authority

Primary sources:

- Official rulebook setup and component inventory, pp. 8–11.
- Character and Character board, pp. 16–18.
- Map, Rooms, Corridors, Doors, markers, and tokens, pp. 19–23.
- Items and Backpack privacy, pp. 28–29.
- Robot, Lander, and Anti-Aircraft information, p. 37.
- Objectives and Mission Task, p. 39.
- Official FAQ v1.2 where it clarifies the above.

Project rules records in `docs/rules/` are used as a source-backed operational index. The application is evidence of current behavior, not authority for the tabletop rules.

## Classification definitions

### Always

Information that must be available at a glance in the normal play view, with no tap required. It includes:

- state needed repeatedly to decide what to do;
- urgent state that can cause damage, death, blocked movement, or game end;
- public tabletop state represented by models, markers, tracks, or face-up components;
- the local player's private hand and persistent private goal summary;
- current turn ownership and remaining opportunity to act, which the physical table communicates socially rather than with a dedicated component.

“Always” means a compact, unambiguous representation is always present. It does not mean every paragraph of source text is permanently expanded.

### Sometimes

Information that is needed only in a specific context, during a resolution, or for deliberate reference. The UI should first attempt to surface it automatically when the context occurs. A tap should be reserved for optional inspection or uncommon reference.

Examples: full Room-effect wording, a newly drawn Event, legal targets for a chosen action, a dice result, or old log entries.

### Not visible

Secret or unrevealed information is not a third presentation tier. It is a privacy boundary and must not be exposed. It is listed separately because the current host-authoritative state contains information that individual players are not entitled to see.

## Physical information sources

| Physical source | Information it provides |
| --- | --- |
| Facility and Section border pieces | Facility boundary, Sections A/B/C, Life Support state, Hibernatorium state, Objective Choice track, Egg/Nest state, Robot area, Anti-Aircraft area, Queen Hits/Health area |
| Round track border pieces | Current Round, Lander timing, Autodestruction timing, face-up Mission Task |
| Room tiles | Name, effect, Item icons, Computer icon, Room type, Room ID, special restrictions |
| Corridor tiles | Connectivity, Noise value, Deadly-mode value when applicable, Door slot, Corridor ID, reinforced state |
| Models/standees and colored rings | Character, Intruder, and Robot locations; Character ownership; Intruder types and quantities |
| Map markers/tokens | Noise, Fire, Malfunction, Secure, Door, Hits, Eggs, Lander, and other local state |
| Character board and tile | Character identity, Rank, Health, Oxygen, Hands, Tactical Belt, basic Actions, statuses, Serious Wounds, Armor, Larva, Data, and related markers |
| Player card area | Action hand, Action deck/discard, Objectives, equipped Items, Support Equipment, secret Backpack Items |
| Shared cards/decks/discards | Mission Task, Events, Exploration, Intruder Attacks, Queen Health, Robot, Items, Serious Wounds, Contamination |
| Bag, token piles, and component pools | Hidden Intruder draw source; visible remaining models, tokens, markers, and other finite supplies |
| Dice and Scanner | Current random result and scanned Contamination result |
| Help cards/sheets | Player number, round sequence, Intruder bag outcomes, Room details, Objective terms, and icon/rule reference |

# Always information

## 1. Global flow and game-ending state

| Information | Physical source | Visibility | Required compact form |
| --- | --- | --- | --- |
| Current Round and time remaining | Round marker/track | Public | Current/maximum Round, not the entire track unless special timing requires it |
| Lander timing/status | Lander token on track or Landing Zone | Public once its outcome resolves | Arrival countdown or `pending`, `landed`, `destroyed`, `launched` |
| Autodestruction status/timing | Autodestruction token/track | Public | Inactive or rounds until detonation; urgent styling when active |
| Current phase/step | Ongoing physical resolution and Help card | Public | Player, Intruder, Event, or Cleanup; include substep only while resolving it |
| Starting Player and current player | Starting Player token and table turn order | Public | Character identity/color; never require opening the Players view |
| Actions remaining and Passed state | Current turn sequence | Public | Active player's remaining Actions; passed/finished state on player summary |
| Paused/disconnected state | Digital-only requirement | Public | Blocking reason and affected player |
| Mission Task summary and progress | Face-up Mission Task | Public | Name plus compact condition/progress; full wording belongs in Sometimes |
| Objective Choice track position | Border-piece track | Public | Current reward/position using the official term `Objective Choice` |

## 2. Shared Facility systems

| Information | Physical source | Visibility | Required compact form |
| --- | --- | --- | --- |
| Life Support A/B/C | Section border tokens | Public | Three labeled Active/Inactive states |
| Hibernatorium state | Hibernatorium token/tile | Public | Undiscovered/Inactive/Active as applicable |
| Nest/Egg state | Egg space and tokens | Public | Eggs remaining or Nest destroyed |
| Queen state | model, Hits track, Health deck | Public | Location, current Hits, Health cards remaining, or dead |
| Robot public state | model, revealed Robot card, markers/tokens | Public after reveal | Location, type/effect identity, malfunction, Tactical Gear |
| Lander occupants | models in Anti-Aircraft/Lander area | Public | Character identities and `in Lander` state |

The Anti-Aircraft status is not public before resolution. A Character may check it in secret and may lie about it. It therefore belongs in Sometimes and must be shown only to the checking player.

## 3. Tactical map

All map-local state should remain attached to the object it describes rather than duplicated in a separate panel.

| Information | Physical source | Visibility | Required compact form |
| --- | --- | --- | --- |
| Facility boundary and Sections | board/border pieces | Public | Clearly distinguish A/B/C and invalid off-board space |
| Discovered/undiscovered Room spaces | Room tiles and empty Facility slots | Public | Known Room or valid undiscovered slot; do not present invalid destinations |
| Room identity | Room tile | Public | Name, Section/type, and ID when the ID can affect a tie-breaker |
| Room search/reference icons | Room tile | Public | Item types, Computer, cannot-secure, cannot-break, and other rule icons |
| Room local state | markers/tokens | Public | Fire, Malfunction, Secure count, permanent Shelter security, Eggs where applicable |
| Corridor topology | Corridor tiles | Public | Which Rooms connect and whether a Corridor is unexplored |
| Corridor rules state | Corridor face/tokens | Public | Noise value, reinforced value/state, Door slot/state, Noise marker, Corridor ID when relevant |
| Character locations | models and colored rings | Public | Character identity/color, including multiple Characters in one Room |
| Intruder locations/types/quantity | models/standees | Public | Type and count in each Room/Corridor; Queen remains distinct |
| Intruder Hits | Universal markers/Queen track | Public | Hits attached to the affected Intruder or Queen state |
| Robot location | model | Public after reveal | Distinct Robot marker plus malfunction when present |
| Active tactical target set | legal physical choices, derived digitally | Acting player | Highlight only legal destinations/targets during the relevant action; omit invalid choices |

Room effect prose is not permanently expanded on the map. It belongs in Sometimes, but should appear automatically when the local Character enters/selects the Room or when `Use the Room` becomes relevant.

## 4. Local player's Character state

| Information | Physical source | Visibility | Required compact form |
| --- | --- | --- | --- |
| Character, player identity, and Rank | Character tile/board | Own and public | Identity and Rank |
| Health and injury band | Health track | Own and public | Current/max Health plus Healthy/Injured/Heavily Injured |
| Oxygen and Suffocating | Oxygen dial/token | Own and public | Current Oxygen and unmistakable Suffocating warning |
| Serious Wounds affecting play | face-up Wound cards on Health track | Own and public | Wound identity and active restriction/modifier; full wording in Sometimes |
| Larva | model on Character board | Own and public | Present/absent; do not label absence as scanned infection knowledge |
| Armor | face-up Armor on Health track | Own and public | Identity and state |
| Heavy Items in Hands | face-up Item cards | Own and public | Item identity, malfunction, Ammo/Tactical Gear, and current usability |
| Tactical Belt | visible tokens in four slots | Own and public | Token types/amounts and usable state |
| Data token | Character board token | Own and public | Present/absent |
| Participation state | model/board state | Own and public | Active, Passed, in Lander, Escaped, Hibernated, or Dead |
| Basic actions/costs | Character board | Own and public | Currently legal actions and costs for the active player; unavailable actions should not compete for attention |
| Action hand | cards held by player | Own only | Every card's identity and effect must be directly readable or represented faithfully; Contamination cannot be used as payment |
| Objective summary | Objective cards | Own only | Before choice: both candidate conditions. After choice: kept Objective condition/progress. Full card wording in Sometimes |

Persistent passive Item, Wound, Character, or card effects should be surfaced automatically at the moment they modify a decision or resolution. The player should not have to remember to inspect them.

## 5. Other players' public state

A physical player can see face-up Character-board state. Mobile should provide a compact roster summary without requiring a tab change for turn-critical facts.

Always show:

- player/Character identity, color, and Rank;
- current location and participation state;
- current/maximum Health and injury band;
- Oxygen and Suffocating;
- Starting Player/current player/Passed state;
- Larva and Data token;
- Serious Wound identities or at minimum their active public restrictions;
- face-up Armor, equipped Heavy Items, Malfunction, Ammo, and Tactical Gear;
- total cards in hand, but not their identities or type split.

Do not show another player's Objective, Action-card identities, Contamination-card count, scanned infection result, or Backpack contents.

# Sometimes information

The default for this category is “automatic when relevant, inspectable otherwise,” not “hide behind a menu.”

## 1. Contextual component detail

- Full Room effect and special rules.
- Full Action-card, Item, Support Equipment, Armor, Serious Wound, Character ability, Robot, Mission Task, and own Objective wording.
- Corridor ID or detailed rule explanation when a movement tie-break or rule makes it relevant.
- Intruder type rules, Health rules, and bag-token outcomes.
- Help-sheet and icon-glossary reference.

Automatic triggers should include occupying/selecting a Room, considering an action modified by an Item/Wound, targeting an Intruder, and resolving a rule that uses a special icon.

## 2. Action and decision context

- Why an action is legal, illegal, or modified.
- Card payment choice and resulting hand state.
- Legal destinations/targets, opportunity-attack exposure, Door blockage, and target capacity.
- Search draws and keep-one choice.
- Item/Tactical Gear use and target choice.
- Trade participants and offered Items/Tactical Gear.
- Robot activation options.
- Objective choice.
- Lander launch decision.
- Room effects with multiple options.
- Any prompt that requires ordering simultaneous effects or choosing among legal outcomes.

These should appear automatically when the decision point is reached. The player should not first open an Actions tab and then open another modal to discover their choices.

## 3. Transient resolution information

- Newly drawn Event card, including movement and both effects.
- Exploration card while its Room/Corridors/markers/Entrance Effect are being resolved.
- Intruder Attack card and targeted Character.
- Queen Health card and resulting effect.
- Intruder bag token while resolving Noise, Hazard, or Bag Development.
- Shoot, Burst, and Noise dice results.
- Infection/Eclosion scan or procedure result.
- Newly gained Serious Wound or Item.
- Damage, healing, Ammo, Oxygen, Fire, and other state changes.

Show the current result automatically, apply it visibly to the persistent state, then dismiss/collapse it without leaving a permanent overlay.

## 4. Conditional warnings and finite supplies

Physical players can see remaining models, markers, tokens, and deck thickness. Exact counts should not occupy the normal mobile view, but relevant limits must surface automatically:

- Fire pool low/empty, because an unavailable Fire marker destroys the Facility.
- Malfunction pool empty, because Fire is substituted.
- Intruder model/corridor capacity limits when placement is pending.
- Secure-token cap in a Room.
- Empty/reshuffling Action deck.
- Exhausted Room type during exploration.
- Empty Item, Contamination, Wound, Event, Attack, Exploration, or Queen Health deck when it changes resolution.
- Tactical Gear/model/token unavailable when an effect would gain or place one.

Optional inspection may show public remaining counts and face-up discard piles.

## 5. History and reference

- Recent event/action summary.
- Full game log and older resolutions.
- Face-up discard piles and deck counts.
- Room Help, Objective Help, Intruder Help, Help card, procedures, and icon glossary.
- Full status/detail view for another player or a remote map object.

Only the latest unresolved or tactically consequential result should interrupt the main view. History should never consume permanent play space.

## 6. Setup-only information

- Character draft choices.
- Support Equipment draft pool and order.
- Initial Tactical Gear selection.
- Player numbers/Help cards when setup or an Objective specifically uses them.

These disappear from the play UI once their purpose ends, except for the resulting state.

# Privacy boundary: information that must not be exposed

| Hidden information | Authorized viewer/timing |
| --- | --- |
| Objective card faces | Owner only until End of Game reveal |
| Action/Contamination card identities in hand | Owner only; other players may see only total hand size |
| Backpack contents | Owner only until an Item is used/revealed |
| Searched but unchosen Items | Searching player only during the choice; never reveal to others |
| Contamination `INFECTED` text | Owner only after that card is scanned |
| Intruder bag contents and token backs | Hidden until the specific draw/resolution exposes the relevant face |
| Face-down deck order/content | Hidden until drawn/revealed by a rule |
| Robot card | Hidden until a Room first connects to the Hibernatorium |
| Anti-Aircraft token faces/status | Checking player only when secretly checked; public only through the resolved Lander outcome; tokens may not be shown |
| Queen Health card numbers/effects | Hidden until the rule reveals/resolves a card |
| Unused draft/Objective/Mission Task cards returned to the box | Unseen |

Current UI privacy issue: `renderPlayerBoards()` displays every player's Action-versus-Contamination hand split and Backpack count. The common card back is specifically intended to hide Action versus Contamination identities, and Backpack Items are explicitly secret. The redesign must show only another player's total hand size and no Backpack information.

# Mobile design consequences

1. The tactical map is the primary play surface, not one tab among equally weighted tabs.
2. Map facts stay on the map. Do not duplicate Room, Corridor, occupant, or marker state in a permanent side panel.
3. A narrow persistent status layer should contain only global flow, urgent Facility state, the local Character's survival state, and compact other-player turn/status cues.
4. The local Action hand and current legal actions need direct access from the play surface; hiding them behind a `Cards` or `Actions` tab violates the Always category.
5. Sometimes information should be driven by game state and current intent. Automatic context is preferred over navigation.
6. Full prose is expanded only where it changes the current decision. Compact icons must retain labels or accessible names and never rely on color alone.
7. Secret information must be filtered by viewer before rendering. A hidden tab is not sufficient privacy.
8. Show one authoritative representation of each fact. Duplicated Round, turn, objective, or Room state wastes mobile space and invites disagreement.
9. Default camera behavior should keep the active Character, current threat, and legal targets visible where possible. Off-screen urgent changes need edge/location cues rather than requiring manual map searching.
10. Persistent UI should shrink when it has nothing new to say. Conditional warnings and resolution detail should disappear after the state change is understood.

# Classification checkpoint before layout design

The proposed boundary is:

- Always: compact state and identity needed for routine decisions, map-local facts, local private hand/goal summary, public Character-board state, turn flow, and urgent global systems.
- Sometimes: full wording, contextual choices, transient resolutions, finite-supply warnings, history, and reference.
- Never: information the physical rules keep secret or unrevealed.

The next design step should place the remaining Always groups into a mobile viewport budget, then define automatic presentation rules for each Sometimes group. The map-specific interaction and semantic-zoom model is defined in [mobile-tactical-map-interaction.md](mobile-tactical-map-interaction.md).