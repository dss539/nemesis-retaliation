# Items and Equipment

This record defines the itemization taxonomy: the card sources, the physical classes, the
Tactical Gear system, and the Item-Icon mechanic. It is the authority for how item cards
are categorized and named in the card database.

**Sources used in this record:**
- **RB** — official rulebook, `docs/rulebooks/Nemesis_RT_Rulebook_official.pdf` (extracted text `rulebook_text.txt`).
- **TTS** — extracted TTS mod, `assets/tts-mod/extract/v2/` (`lua_script.lua`, `objects.json`, `lua_roles.json`). Secondary reference only; the mod is not a complete or authoritative rules engine.
- **USER** — the project owner's direct assertions from experience with the physical game. Treated as a documented project interpretation under the authority order in [readme.md](readme.md).

---

## ITM-001 — Item card sources

- **Plain rule:** Item cards enter the game from three distinct sources:
  1. **Character Item cards** — per-character starting equipment (7 total; the Contractor starts with 2, all others 1).
  2. **Support Equipment deck** — a draft of 24 cards performed during setup by non-Contractor characters.
  3. **Item decks** — three color decks (red, green, yellow), 90 cards total, drawn via the Search Action / Item Icons.
- **Source:** RB p. 4 (setup, extracted lines 2692–2728); RB p. 29 (gaining items, lines 4849–4865); RB component list (lines 520–525, 2595).
- **Note:** The TTS mod models these as `startItemDeck` (equipment), `greenItemsDeck`, `redItemsDeck`, `yellowItemsDeck` (TTS `lua_roles.json`). The mod's `startItemDeck` holds the heavy weapons; the color decks hold the small backpack cards.

### Character-folder Item occurrences

| Exact source occurrence | Printed Item face text to add verbatim | Source / boundary |
|---|---|---|
| `assets/tts-mod/extract/v2-dl/tree/cards/character/contractor-044.jpg` | `title: BULLETPROOF VEST`<br>`typeLine: ARMOR`<br>`When you would receive a Serious Wound, discard this Item instead.` | `CARD-character-contractor-character-contractor-044.jpg`; extraction classification says non-rules/reference although the body is operative; retain as source evidence pending re-check. |
| `assets/tts-mod/extract/v2-dl/tree/cards/character/contractor-052.jpg` | `typeLine: RANGED WEAPON, HEAVY`<br>`Burst: -1 to Burst results.` | `CARD-character-contractor-character-contractor-052.jpg`; no title is present, so none is invented. |
| `assets/tts-mod/extract/v2-dl/tree/cards/character/medical-support-024.jpg` | `title: CARBINE`<br>`typeLine: RANGED WEAPON, HEAVY`<br>`Shoot: After you don't kill the [intruder], deal 1 Hit.` | `CARD-character-medical-support-character-medical-support-024.jpg`; source-scoped Weapon effect, not a rewrite of `ACT-SHOOT-001`. |
| `assets/tts-mod/extract/v2-dl/tree/cards/character/officer-041.png` | `title: SAWED-OFF SHOTGUN`<br>`typeLine: RANGED WEAPON`<br>`Shoot: Instead of a normal Shoot, you may spend [ICON: red outlined rectangular glyph with right-side double-lobed protrusion] to Repel 1 Adult from the Room.` | `CARD-character-officer-character-officer-041.png`; unresolved resource glyph remains literal and no Ammo alias is added. |

## ITM-002 — Physical classes of Item cards

- **Plain rule:** An Item card is classified by its physical layout and keywords into one of:
  - **Regular Item (Backpack card)** — vertical layout, no Armor keyword. Lives in the Backpack, secret until used. (RB lines 4882–4883, 4906–4910.)
  - **Heavy Item** — horizontal layout. Too big for the Backpack; held in a Hand slot, one per Hand. (RB lines 5024–5029.)
  - **Armor Item** — carries the "Armor" keyword. Worn on the Health track, not in the Backpack. (RB lines 5045–5057.)
- **Weapon Item** — a subtype of Heavy Item (Ranged or Melee). Ranged Weapons are required to Shoot and Burst. (RB lines 5030–5033.)
- **Weapon-trait semantics** — the Ranged Weapon and Melee Weapon labels are descriptive and have no standalone effect, although Actions may refer to them. A Weapon with Requires No Ammo may Shoot or Burst without a physical Ammo token and always counts as having one for Action prerequisites.
- **Intruder Eggs** — Eggs count as Heavy Items.
- **Armor gain restriction** — if a Character is already Heavily Injured when they would gain Armor, they cannot gain it and discard it instead.
- **Heavy Armor** — whenever its Character would gain a Serious Wound, they may lose 2 Health instead.
- **Source:** RB p. 29 (extracted lines 5024–5057).
- **USER:** The physical classes are orthogonal to card color. A card's color (red/green/yellow) does not determine whether it is heavy, armor, or regular.

### Additional physical-class and Weapon-trait source rows

- **Plain rule:** A Character may “spend” Ammo from a Weapon with “Requires no Ammo” trait.
  - **Source:** FAQ v1.2, printed p. 3, `FQ-P03-U01`.
- **Plain rule:** Ammo cannot be spent from a malfunctioned Weapon.
  - **Source:** FAQ v1.2, printed p. 3, `FQ-P03-U02`.
- **Plain rule:** Every Character has 2 Hand slots at the top of the Character board.
  - **Source:** Official Rulebook p. 17, “D. HAND SLOTS,” `RB-P17-001`.
- **Plain rule:** Perimeter Security Device is a Heavy Item.
  - **Source:** Official Rulebook p. 28, “PERIMETER SECURITY DEVICE — trait,” `RB-P28-007`.
- **Plain rule:** Grenade Launcher is a Ranged Weapon and Heavy Item.
  - **Source:** Official Rulebook p. 29, “GRENADE LAUNCHER — traits,” `RB-P29-038`.

## ITM-003 — Color-deck membership does not determine physical class

- **Plain rule:** Red, green, and yellow are Search/source families. A card's physical class must be read from its exact source occurrence; color/root membership alone does not prove Regular, Heavy, or Armor class.
- **Official boundary:** The rulebook fixes 30 cards per color and separately defines Regular, Heavy, and Armor classes, but does not publish a per-color class partition in the checked prose.
- **Preserved source evidence:**
  - Green TTS root: 23 source-clear Regular occurrences and 7 Heavy occurrences; the licensed aggregate independently records 23 Regular / 7 Heavy.
  - Red TTS root: 21 source-clear Regular, 3 explicit Heavy, and 6 Military Taser class-conflict occurrences; the licensed aggregate independently records 21 Regular / 9 Heavy.
  - Yellow TTS root: 24 source-clear Regular and 6 Fire Extinguisher/Robot Controller class-conflict occurrences; the licensed aggregate independently records 24 Regular / 6 Heavy.
- **Source:** Rulebook component list and p. 29; exact roots and authority boundaries in `archive/obsolete/semantics/data/green-item-source-index.json`, `red-item-source-index.json`, `yellow-item-source-index.json`, and `equipment-source-index.json`.
- **Boundary:** Aggregate agreement does not identify a TTS physical copy with a licensed/current official copy. Class-conflict occurrences remain non-dispatchable until resolved source-scoped; they are not repaired by title, artwork, color, root, or count.

## ITM-004 — Search dispatches storage by the exact drawn Item class

- **Plain rule:** Search draws the top exact physical occurrence from each corresponding color deck. After the player selects the kept occurrence, gain/storage follows that occurrence's source-supported class: Regular to Backpack, Heavy to a Hand position, Armor to the Health-track Armor position.
- **Identity rule:** Repeated titles remain separate physical occurrences. Never select, store, or dispatch by title alone.
- **Unresolved boundary:** Exact class-conflict copies may not be made playable by importing another version's class. Empty-deck, random post-draw storage legality, and affected policy gaps remain explicit in the implementation-readiness pilot.
- **Source:** Rulebook lines 4849–4865, 4905–4910, and 5024–5057; exact occurrence indexes cited in ITM-003.

## ITM-005 — Tactical Gear tokens and slots

- **Plain rule:** Tactical Gear tokens are the four consumable resources: **Ammo**, **Grenade**, **Oxygen**, and **Medpack**. They are placed in Tactical Gear slots.
- **Tactical Belt:** Each Character has a Tactical Belt of 4 Tactical Gear slots on the left side of their Character board. (RB lines 3523–3525.)
- **Slots on Items:** Tactical Gear slots also appear on Weapons and other Items. Most Weapons have Ammo slots, since they require Ammo to be shot. (RB lines 5059–5061, 3527–3528.)
- **Slot color determines fit:** The color of a slot dictates which token it accepts. The token types are Ammo, Grenade, Oxygen, Medpack, and Any. Grey/Any slots accept any token; Tactical Belt slots count as Any. (RB lines 5062–5076.)
- **Placement rule:** When gaining a Tactical Gear token, it may be placed in any empty Tactical Gear slot that matches the token. (RB lines 5074–5076.)
- **Fully loaded:** Items are always found with all their Tactical Gear slots filled, if they have any. (RB lines 4900–4901.)
- **Ammo is two-sided:** Ammo tokens have a Full side and a Half-full side. Whenever an Ammo token enters the game, it enters full-side-up. Using an Ammo token Reloads a Weapon — move the Ammo token from a Tactical Gear slot onto the Weapon's slot. An Ammo token already loaded into a Weapon may not be moved. (RB lines 3477–3483; Rulebook p. 8, setup note.)
- **Landing Zone starting supply:** Place 4 Ammo tokens full-side-up, 4 Grenade tokens, 4 Oxygen tokens, and 4 Medpack tokens in their corresponding slots next to the Landing Zone.
- **Losing an Item loses its tokens:** As a result of losing an Item, the Character also loses all Tactical Gear tokens on that Item. (RB lines 5077–5078.)
- **Component limit:** Tactical Gear tokens are limited components. If all are already in players' possession, a Character cannot gain more (e.g. cannot gain Ammo tokens if all are held). (RB lines 3543–3548.)
- **Provided supply:** The game contains 80 Tactical Gear tokens: 20 Ammo, 20 Grenade, 20 Oxygen, and 20 Medpack tokens.
- **Source:** RB p. 8 (Landing Zone setup and full-side-up Ammo); p. 16 (Tactical Gear tokens); and p. 29 (Tactical Gear slots), extracted lines 3523–3528, 3477–3483, 3543–3548, 4900–4901, 5058–5078.
- **TTS:** The mod encodes slot counts in card GMNotes — `A`=1 Ammo, `AA`=2 Ammo, `AAA`=3 Ammo, `AGG`=Ammo+Grenade+Grenade, `M`=Melee/Malfunction (TTS `objects.json`, `startItemDeck` cards). Useful as a cross-check for the vision phase, not authoritative.

### Additional Oxygen, discarding, and Item-slot source rows

- **Plain rule:** Facility Oxygen is contaminated and cannot be used unless Life Support Systems are working.
  - **Source:** Official Rulebook p. 17, “E. OXYGEN — contamination,” `RB-P17-011`.
- **Plain rule:** A Character may discard any number of their Items or Tactical Gear tokens at any time.
  - **Source:** Official Rulebook p. 17, “DISCARDING ITEMS AND TACTICAL GEAR TOKENS — permission,” `RB-P17-031`.
- **Plain rule:** Return discarded Tactical Gear tokens to the token pool.
  - **Source:** Official Rulebook p. 17, “DISCARDING ITEMS AND TACTICAL GEAR TOKENS — tokens,” `RB-P17-032`.
- **Plain rule:** Grenade Launcher has 1 red Ammo-token slot.
  - **Source:** Official Rulebook p. 29, “GRENADE LAUNCHER — Ammo slot,” `RB-P29-040`.
- **Plain rule:** Grenade Launcher has 2 purple Grenade-token slots.
  - **Source:** Official Rulebook p. 29, “GRENADE LAUNCHER — Grenade slots,” `RB-P29-041`.
- **Plain rule:** If a Character has a full Ammo token and a rule instructs them to spend it, flip the token to its half-full side.
- **Plain rule:** If a Character has a half-full Ammo token and a rule instructs them to spend it, discard the token.
- **Plain rule:** An Ammo token can be spent twice before it is depleted.
- **Source:** Rulebook p. 33, `SPEND Ammo — full token`, `SPEND Ammo — half-full token`, and `SPEND Ammo — capacity` (`RB-P33-041`, `RB-P33-042`, and `RB-P33-043`).
- **Boundary:** Preserve the existing `ITM-005` full/half-side and loaded-Ammo restrictions; these sentences do not resolve any Weapon-specific trigger, allocation, or attached-token question.

## ITM-006 — Item Icons and the Search mechanic

- **Plain rule:** Room tiles display Item Icons showing which types of Items can be found there. The Search Action draws 1 Item card for each Item Icon in the Room, then the player keeps 1 and discards the rest. (RB lines 4022–4023, 4853–4860.)
- **Icon types:** The Item Icons are color-coded pictographs:
  - **Green** — white plus — health / support.
  - **Yellow** — white wrench — mechanical / utility / repair.
  - **Red** — three white bullets — attack / ammo / offense.
- **Provisional naming:** For now these are called **green card / yellow card / red card** (or green/yellow/red Item). A better name may be derived after all cards are analyzed.
- **Source:** RB p. 20 (Room tiles, lines 4022–4023) and p. 29 (gaining items, lines 4853–4860). Icon pictograph descriptions are **USER** assertions from the physical game.
- **TTS:** The mod does not model the Item-Icon → color-deck mapping for Search; it only tags cards by deck and plays a sound. The Search/icon mechanic is therefore taken from the rulebook, not the mod.

## ITM-007 — Tactical Gear token colors (for vision guidance)

- **Plain rule:** For vision-extraction guidance only, the Tactical Gear tokens are color-coded: **Grenade** (purple), **Medpack** (green), **Ammo** (red), **Oxygen** (yellow; some assets may appear yellow-orange). These colors are an extraction aid for the vision model and are not part of the canonical stored names.
- **Source:** Official rulebook p. 40 icon glossary; TTS token assets (`tokens/grenade-003.png`, `tokens/medpack-006.png`, `tokens/ammo-008.png`, `tokens/oxygen-005.png`) are secondary references whose rendering may differ slightly. Native GPT-5.6 independently reverified `ammo-008.png` as deep red/crimson and `grenade-003.png` as purple/violet on 2026-08-14 after earlier Qwen use was audited; see `docs/qa/qwen-derived-vision-cleanup.md`. **USER** confirmed the type-based naming (Grenade, Medpack, Ammo, Oxygen) is sufficient for the glossary; colors are only needed to disambiguate glyphs during vision reads.
- **Note:** Red and green each appear in BOTH the item-icon set (red/green card) and the gear-token set (red Ammo, green Medpack). The type word (card vs Ammo/Medpack) disambiguates them; the color key is a vision aid only.

## ITM-008 — Canonical item icon vocabulary

- **Plain rule:** The canonical placeholders for item-related card data are:
  - Item types: `[greenItem]`, `[yellowItem]`, `[redItem]`.
  - Tactical Gear tokens: `[grenadeToken]`, `[medpackToken]`, `[ammoToken]`, `[oxygenToken]`.
  - Not In Combat restriction: `[notInCombat]` — an Action with this icon cannot be performed in a Room with Intruders.
- **Ship/Dropship icon:** The silhouette some vision reads described as an "alien head" is the **Lander**, not an Intruder. Canonical name: `[lander]`.
- **Scope boundary:** The complete vocabulary, including Tactical Gear slots, markers, Corridor axes, die faces, and general icons, is defined in `docs/rules/icon-glossary.md` and extracted under `assets/icons/`.
- **Source:** Official rulebook p. 40 icon glossary; ITM-006 and ITM-007.

## ITM-009 — Rulebook-illustrated Item effects

- **Source:** Rulebook p. 28, illustrated Item faces (`RB-P28-009`, `RB-P28-040`).
- **Perimeter Security Device:** Whenever its Character Discovers a new Room, ignore Hazard results from all sources.
- **Duct Tape:** One printed option discards 1 Malfunction marker. Its other printed option and exact One Use Only/Not In Combat boundaries remain source-scoped and are not rewritten here.

### Exact Item-card source occurrences

| ID | Exact occurrence metadata | Final proposed row |
|---|---|---|
| CARD-game-greenitem-game-greenitem-029.png | `HEAVY OXYGEN TANK`; `ONE USE ONLY, SPECIAL WEAPON` | **Plain rule:** Gain 7 [oxygen].<br>**Source:** TTS source-bound variant, `assets/tts-mod/extract/v2-dl/tree/cards/game/greenitem-029.png`; not an official replacement. |
| CARD-game-greenitem-game-greenitem-035.png | title not present in fragment; `ONE USE ONLY` | **Plain rule:** Discard 1 Serious Wound and/or restore 3 [characterHealth].<br>**Source:** TTS source-bound variant, `assets/tts-mod/extract/v2-dl/tree/cards/game/greenitem-035.png`; not an official replacement. |
| CARD-game-greenitem-game-greenitem-120.png | `MEDKIT`; `ONE USE ONLY` | **Plain rule:** You can use this Item for free immediately after gaining it. Restore 2 [characterHealth]. OR Gain 1 [medpackToken].<br>**Source:** TTS source-bound variant, `assets/tts-mod/extract/v2-dl/tree/cards/game/greenitem-120.png`; not an official replacement. |
| CARD-game-greenitem-game-greenitem-181_cards-card-01.png | title not present in fragment; `ONE USE ONLY` | **Plain rule:** Remove 1 Contamination card from your hand without scanning it.<br>**Source:** TTS source-bound variant, `assets/tts-mod/extract/v2-dl/tree/cards/game/greenitem-181_cards/card-01.png`; not an official replacement. |
| CARD-game-greenitem-game-greenitem-181_cards-card-03.png | title not present in fragment; `ONE USE ONLY` | **Plain rule:** Only in a [computer] Room without [malfunction]. Choose any Room in the Facility and place a closed Door in each adjacent Corridor.<br>**Source:** TTS source-bound variant, `assets/tts-mod/extract/v2-dl/tree/cards/game/greenitem-181_cards/card-03.png`; not an official replacement. |
| CARD-game-greenitem-game-greenitem-181_cards-card-04.png | `EMERGENCY LIFE SUPPORT CODES`; `ONE USE ONLY` | **Plain rule:** Only in [computer] Room without [malfunction]. Flip all [ICON: white three-lobed horizontal cluster with cyan center and an outlined upright rounded rectangle]. Flip 1 [ICON: white three-lobed horizontal cluster with gray center and a pale outlined upright rounded rectangle].<br>**Source:** TTS source-bound variant, `assets/tts-mod/extract/v2-dl/tree/cards/game/greenitem-181_cards/card-04.png`; not an official replacement. |
| CARD-game-greenitem-game-greenitem-181_cards-card-05.png | title not present in fragment; `ONE USE ONLY` | **Plain rule:** Discard 1 Serious Wound. OR Restore 2 [characterHealth].<br>**Source:** TTS source-bound variant, `assets/tts-mod/extract/v2-dl/tree/cards/game/greenitem-181_cards/card-05.png`; not an official replacement. |
| CARD-game-reditem-game-reditem-148_cards-card-01.png | `ANTI-AIRCRAFT CODES`; `ONE USE ONLY` | **Plain rule:** Only in [computer] Room without [malfunction]. Take both Anti-Aircraft tokens and place them in any order.<br>**Source:** TTS source-bound variant, `assets/tts-mod/extract/v2-dl/tree/cards/game/reditem-148_cards/card-01.png`; not an official replacement. |
| CARD-game-reditem-game-reditem-148_cards-card-02.png | `CLAYMORE MINE`; `ONE USE ONLY` | **Plain rule:** Place 1 [ICON: red rounded rectangular tile with white upright bulb-shaped inset] in an empty Corridor. When any number of [intruder] are placed in that Corridor, remove the [ICON: red rounded rectangular tile with white upright bulb-shaped inset] and resolve the token effect there.<br>**Source:** TTS source-bound variant, `assets/tts-mod/extract/v2-dl/tree/cards/game/reditem-148_cards/card-02.png`; not an official replacement. |
| CARD-game-reditem-game-reditem-148_cards-card-04.png | title not present in fragment; `ONE USE ONLY, SPECIAL WEAPON` | **Plain rule:** Move. Ignore all Opportunity Attacks during that Movement.<br>**Source:** TTS source-bound variant, `assets/tts-mod/extract/v2-dl/tree/cards/game/reditem-148_cards/card-04.png`; not an official replacement. |
| CARD-game-reditem-game-reditem-148_cards-card-07.png | `PORTABLE BARRIER`; `ONE USE ONLY` | **Plain rule:** Place a closed Door.<br>**Source:** TTS source-bound variant, `assets/tts-mod/extract/v2-dl/tree/cards/game/reditem-148_cards/card-07.png`; not an official replacement. |
| CARD-game-startItemDeck-game-startItemDeck-005.png | `TACTICAL ARMOR`; `ARMOR` | **Plain rule:** Whenever you lose [characterHealth] as a result of an Intruder Attack, lose 1 [characterHealth] less.<br>**Source:** TTS source-bound variant, `assets/tts-mod/extract/v2-dl/tree/cards/game/startItemDeck-005.png`; not an official replacement. |
| CARD-game-startItemDeck-game-startItemDeck-046.jpg | `BAYONET`; `MELEE WEAPON, HEAVY` | **Plain rule:** You may hold this Item in the same Hand slot as a Ranged Weapon. Whenever you would be Attacked by an [intruder], you may place a [malfunction] on the Bayonet to Prevent the Attack.<br>**Source:** TTS source-bound variant, `assets/tts-mod/extract/v2-dl/tree/cards/game/startItemDeck-046.jpg`; not an official replacement. |
| CARD-game-startItemDeck-game-startItemDeck-055.jpg | `FLAMETHROWER`; `RANGED WEAPON, REQUIRES NO AMMO, HEAVY` | **Plain rule:** Burst and Shoot: If you are in a Section with an [lifeSupportInactive], spend 1 [oxygen] to use this Weapon. [burstDieAdditionalEffects], [shootDieAmmoLoss]: Place a [fire] in your Room.<br>**Source:** TTS source-bound variant, `assets/tts-mod/extract/v2-dl/tree/cards/game/startItemDeck-055.jpg`; not an official replacement. |
| CARD-game-startItemDeck-game-startItemDeck-073.jpg | `HAND CANNON`; `RANGED WEAPON, HEAVY` | **Plain rule:** Burst: -1 to Burst results. Shoot: -1 to Shoot results.<br>**Source:** TTS source-bound variant, `assets/tts-mod/extract/v2-dl/tree/cards/game/startItemDeck-073.jpg`; not an official replacement. |
| CARD-game-startItemDeck-game-startItemDeck-098.jpg | `TACTICAL HATCHET`; `MELEE WEAPON, HEAVY` | **Plain rule:** Melee Attack: Deal [ICON: white crested bulbous silhouette with two dark openings and a notched lower edge] instead of rolling the Shoot die, and place a [malfunction] on this Weapon.<br>**Source:** TTS source-bound variant, `assets/tts-mod/extract/v2-dl/tree/cards/game/startItemDeck-098.jpg`; not an official replacement. |
| CARD-game-startItemDeck-game-startItemDeck-114.jpg | `PLASMA GUN`; `RANGED WEAPON, REQUIRES NO AMMO, HEAVY` | **Plain rule:** [burstDieAdditionalEffects], [shootDieAmmoLoss]: Lose 2 [characterHealth] for each Universal marker on this Weapon, and then place 1 Universal marker there.<br>**Source:** TTS source-bound variant, `assets/tts-mod/extract/v2-dl/tree/cards/game/startItemDeck-114.jpg`; not an official replacement. |
| CARD-game-startItemDeck-game-startItemDeck-131.png | `GATLING GUN`; `RANGED WEAPON, RIFLE` | **Plain rule:** Burst: After Bursting, you may Burst a second time at the same Corridor without spending [ammoToken]. [burstDieAdditionalEffects]: Place [malfunction] on this Weapon.<br>**Source:** TTS source-bound variant, `assets/tts-mod/extract/v2-dl/tree/cards/game/startItemDeck-131.png`; not an official replacement. |
| CARD-game-startItemDeck-game-startItemDeck-144_cards-card-03.png | `ENGINEERING EQUIPMENT` | **Plain rule:** Remove a [malfunction]. OR Remove this Item and Reinforce an empty Corridor.<br>**Source:** TTS source-bound variant, `assets/tts-mod/extract/v2-dl/tree/cards/game/startItemDeck-144_cards/card-03.png`; not an official replacement. |
| CARD-game-startItemDeck-game-startItemDeck-144_cards-card-04.png | title not present in fragment; `MELEE WEAPON` | **Plain rule:** Destroy 1 Door. OR Place a [malfunction] in your Room.<br>**Source:** TTS source-bound variant, `assets/tts-mod/extract/v2-dl/tree/cards/game/startItemDeck-144_cards/card-04.png`; not an official replacement. |
| CARD-game-startItemDeck-game-startItemDeck-144_cards-card-05.png | `FLAMETHROWER`; `RANGED WEAPON, REQUIRES NO AMMO` | **Plain rule:** Shoot and Burst: If you are in a Section with an [ICON: white horizontal three-lobed capsule with a gray outlined central vertical block and short top stem] lose 1 [oxygen]. [burstDieAdditionalEffects], [shootDieAmmoLoss]: Place a [fire].<br>**Source:** TTS source-bound variant, `assets/tts-mod/extract/v2-dl/tree/cards/game/startItemDeck-144_cards/card-05.png`; not an official replacement. |
| CARD-game-startItemDeck-game-startItemDeck-144_cards-card-08.png | `HEAVY HANDGUN`; `RANGED WEAPON` | **Plain rule:** Burst: Reduce Burst roll values by 1. Shoot: Reduce Shoot roll values by 1.<br>**Source:** TTS source-bound variant, `assets/tts-mod/extract/v2-dl/tree/cards/game/startItemDeck-144_cards/card-08.png`; not an official replacement. |
| CARD-game-startItemDeck-game-startItemDeck-144_cards-card-11.png | `PLASMA GUN`; `RANGED WEAPON. REQUIRES NO AMMO` | **Plain rule:** This Weapon can be used even with a [malfunction] on it and is not discarded when another [malfunction] is placed. [burstDieAdditionalEffects], [shootDieAmmoLoss]: Place a [malfunction] on this Weapon and then lose 2 [characterHealth] for each [malfunction].<br>**Source:** TTS source-bound variant, `assets/tts-mod/extract/v2-dl/tree/cards/game/startItemDeck-144_cards/card-11.png`; not an official replacement. |
| CARD-game-startItemDeck-game-startItemDeck-144_cards-card-12.png | `PORTABLE DEVICE` | **Plain rule:** You may treat your Room as a [computer] Room.<br>**Source:** TTS source-bound variant, `assets/tts-mod/extract/v2-dl/tree/cards/game/startItemDeck-144_cards/card-12.png`; not an official replacement. |
| CARD-game-startItemDeck-game-startItemDeck-144_cards-card-14.png | `SUBMACHINE GUN`; `RANGED WEAPON` | **Plain rule:** [shootDie2]: treat this result as a [shootDieCritical] and spend 1 [ICON: red near-square with a split dark rectangular inset] as normal.<br>**Source:** TTS source-bound variant, `assets/tts-mod/extract/v2-dl/tree/cards/game/startItemDeck-144_cards/card-14.png`; not an official replacement. |
| CARD-game-startItemDeck-game-startItemDeck-144_cards-card-16.png | `TACTICAL HATCHET.`; `MELEE WEAPON` | **Plain rule:** When you Melee attack deal 2 Hits before the Attack roll.<br>**Source:** TTS source-bound variant, `assets/tts-mod/extract/v2-dl/tree/cards/game/startItemDeck-144_cards/card-16.png`; not an official replacement. |
| CARD-game-startItemDeck-game-startItemDeck-144_cards-card-17.png | `SONIC GUN`; `RANGED WEAPON. REQUIRES NO AMMO` | **Plain rule:** Burst: Treat [burstDie3] and [burstDie4] as [burstDie2]. [burstDieAdditionalEffects], [shootDieAmmoLoss] - Place a [malfunction] in your Room.<br>**Source:** TTS source-bound variant, `assets/tts-mod/extract/v2-dl/tree/cards/game/startItemDeck-144_cards/card-17.png`; not an official replacement. |
| CARD-game-startItemDeck-game-startItemDeck-163.png | `SECURITY SYSTEM CONTROL`; `HEAVY` | **Plain rule:** Discard 1 [secure] from any Room in your Section to choose a Corridor adjacent to that Room. Roll a Burst die and deal Hits equal to the result in the chosen Corridor. [burstDieAdditionalEffects]: Place a [malfunction] on this Item.<br>**Source:** TTS source-bound variant, `assets/tts-mod/extract/v2-dl/tree/cards/game/startItemDeck-163.png`; not an official replacement. |
| CARD-game-yellowitem-game-yellowitem-050.png | `OXYGEN TANK`; `ONE USE ONLY, SPECIAL WEAPON` | **Plain rule (extracted text; choice relation not stated):** You can use this Item for free immediately after gaining it. The occurrence contains “Gain 3 [oxygen].” and “Gain 1 [oxygenToken].”<br>**Source:** TTS source-bound variant, `assets/tts-mod/extract/v2-dl/tree/cards/game/yellowitem-050.png`; not an official replacement. |
| CARD-game-yellowitem-game-yellowitem-097.png | title not present in fragment | **Plain rule:** Use the [robot] from anywhere in the Facility. OR Discard this Item to place corresponding Tactical Gear tokens on empty Robot slots.<br>**Source:** TTS source-bound variant, `assets/tts-mod/extract/v2-dl/tree/cards/game/yellowitem-097.png`; not an official replacement. |
| CARD-game-yellowitem-game-yellowitem-146_cards-card-01.png | title not present in fragment; `ONE USE ONLY. SPECIAL WEAPON` | **Plain rule (literal source text):** Discard a [fire]. OR 1 chosen [intruder] in your Room Escapes.<br>**Source:** TTS source-bound variant, `assets/tts-mod/extract/v2-dl/tree/cards/game/yellowitem-146_cards/card-01.png`; not an official replacement. |
| CARD-game-yellowitem-game-yellowitem-146_cards-card-02.png | `ROBOT CONTROLLER` | **Plain rule:** Use the [robot] from anywhere in the Facility. OR If [robot] is not on the board yet, place it in your Room.<br>**Source:** TTS source-bound variant, `assets/tts-mod/extract/v2-dl/tree/cards/game/yellowitem-146_cards/card-02.png`; not an official replacement. |
| RB-P29-002.rule | official `MILITARY TASER` occurrence | **Plain rule:** Military Taser may Repel 1 Intruder from the Room.<br>**Source:** Official Rulebook p. 29, “MILITARY TASER — first option,” `RB-P29-002`. |
| RB-P29-039.rule | official `GRENADE LAUNCHER` occurrence | **Plain rule:** When Bursting with Grenade Launcher, the Character may use any number of Grenade tokens from this Weapon before or instead of a normal Burst.<br>**Source:** Official Rulebook p. 29, “GRENADE LAUNCHER — Burst effect,” `RB-P29-039`. |

#### General, passive, and Duct Tape source rows

| ID | Final proposed row |
|---|---|
| RB-P28-005.fact | **Plain rule:** A passive Item applies its effect at the timing printed on the card.<br>**Source:** Official Rulebook p. 28, “ITEMS — passive Items,” `RB-P28-005`. |
| RB-P28-006.rule | **Plain rule:** A passive-effect Item cannot be Used through the Use an Item Basic Action.<br>**Source:** Official Rulebook p. 28, “ITEMS — passive-use prohibition,” `RB-P28-006`. |
| RB-P28-038.fact | **Plain rule:** Duct Tape is a One Use Only Item.<br>**Source:** Official Rulebook p. 28, “DUCT TAPE — trait,” `RB-P28-038`. |
| RB-P28-041.rule | **Plain rule:** Duct Tape may place 1 Heavy Item above another Heavy Item in your Hand slot.<br>**Source:** Official Rulebook p. 28, “DUCT TAPE — second option,” `RB-P28-041`. |
| RB-P28-042.fact | **Plain rule:** Duct Tape’s stacking option allows 2 Heavy Items to occupy one Hand slot.<br>**Source:** Official Rulebook p. 28, “DUCT TAPE — capacity effect,” `RB-P28-042`. |
| FAQ-FQ-P03-U05 | **Plain rule:** Duct Tape may place a third Item in a single Hand slot.<br>**Source:** FAQ v1.2, printed p. 3, `FQ-P03-U05` (Q: “Can I Duct Tape a 3rd Item in a single hand?” A: “Yes.”). |
