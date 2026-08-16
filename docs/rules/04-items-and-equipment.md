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

## ITM-002 — Physical classes of Item cards

- **Plain rule:** An Item card is classified by its physical layout and keywords into one of:
  - **Regular Item (Backpack card)** — vertical layout, no Armor keyword. Lives in the Backpack, secret until used. (RB lines 4882–4883, 4906–4910.)
  - **Heavy Item** — horizontal layout. Too big for the Backpack; held in a Hand slot, one per Hand. (RB lines 5024–5029.)
  - **Armor Item** — carries the "Armor" keyword. Worn on the Health track, not in the Backpack. (RB lines 5045–5057.)
- **Weapon Item** — a subtype of Heavy Item (Ranged or Melee). Ranged Weapons are required to Shoot and Burst. (RB lines 5030–5033.)
- **Source:** RB p. 29 (extracted lines 5024–5057).
- **USER:** The physical classes are orthogonal to card color. A card's color (red/green/yellow) does not determine whether it is heavy, armor, or regular.

## ITM-003 — Color decks are always Backpack cards

- **Plain rule:** The red, green, and yellow Item decks contain only Regular (Backpack) cards. No color-deck card is a Heavy Item or an Armor Item.
- **Source:** RB p. 29 — the "gaining items" section immediately defines the drawn cards as "regular items" (lines 4849–4883). TTS — the color decks (`redItemsDeck`/`greenItemsDeck`/`yellowItemsDeck`) contain 30 anonymous cards each tagged `reditem`/`greenitem`/`yellowitem`, none carrying heavy/weapon/armor tags; the heavy weapons (GATLING GUN, ASSAULT SHOTGUN, PLASMA GUN, FLAMETHROWER, TACTICAL HATCHET, etc.) all live in the separate `startItemDeck` (TTS `objects.json`).
- **USER:** Confirmed from the physical game — the color-deck cards are small cards; the heavy items are physically larger, horizontal cards from the equipment deck, held in a Hand slot.

## ITM-004 — Heavy Items are not drawn from the color decks

- **Plain rule:** No red, green, or yellow Item-deck card is itself a Heavy Item or an Armor Item. Heavy Items (including Weapons) are obtained as physical cards from the Character Item cards and the Support Equipment deck, not from the color Item decks.
- **Scope boundary:** This rule concerns the *physical class of the card drawn*. It does NOT restrict what a color-deck card's *effect* may do. A color-deck card's effect may grant, place, or otherwise produce a Heavy Item (e.g. an effect that says "gain a Weapon"); that is a separate matter from the card's own physical class.
- **Source:** RB p. 4 setup (lines 2692–2714) — Character Items and Support Equipment are placed as Heavy Items in Hand slots or Armor on the Health track. RB p. 29 (lines 5024–5034) — Heavy Items are horizontal and held in Hands.
- **TTS:** The `startItemDeck` (equipment) is the deck that contains the heavy weapons; the color decks contain only backpack cards.
- **USER:** A color-deck card does not itself become a heavy item; heavy items are separate, larger cards. (Whether a color-deck effect can grant a heavy item is left open pending card inspection.)

## ITM-005 — Tactical Gear tokens and slots

- **Plain rule:** Tactical Gear tokens are the four consumable resources: **Ammo**, **Grenade**, **Oxygen**, and **Medpack**. They are placed in Tactical Gear slots.
- **Tactical Belt:** Each Character has a Tactical Belt of 4 Tactical Gear slots on the left side of their Character board. (RB lines 3523–3525.)
- **Slots on Items:** Tactical Gear slots also appear on Weapons and other Items. Most Weapons have Ammo slots, since they require Ammo to be shot. (RB lines 5059–5061, 3527–3528.)
- **Slot color determines fit:** The color of a slot dictates which token it accepts. The token types are Ammo, Grenade, Oxygen, Medpack, and Any. Grey/Any slots accept any token; Tactical Belt slots count as Any. (RB lines 5062–5076.)
- **Placement rule:** When gaining a Tactical Gear token, it may be placed in any empty Tactical Gear slot that matches the token. (RB lines 5074–5076.)
- **Fully loaded:** Items are always found with all their Tactical Gear slots filled, if they have any. (RB lines 4900–4901.)
- **Ammo is two-sided:** Ammo tokens have a Full side and a Half-full side. Using an Ammo token Reloads a Weapon — move the Ammo token from a Tactical Gear slot onto the Weapon's slot. An Ammo token already loaded into a Weapon may not be moved. (RB lines 3477–3483.)
- **Losing an Item loses its tokens:** As a result of losing an Item, the Character also loses all Tactical Gear tokens on that Item. (RB lines 5077–5078.)
- **Component limit:** Tactical Gear tokens are limited components. If all are already in players' possession, a Character cannot gain more (e.g. cannot gain Ammo tokens if all are held). (RB lines 3543–3548.)
- **Source:** RB p. 16 (Tactical Gear tokens) and p. 29 (Tactical Gear slots), extracted lines 3523–3528, 3477–3483, 3543–3548, 4900–4901, 5058–5078.
- **TTS:** The mod encodes slot counts in card GMNotes — `A`=1 Ammo, `AA`=2 Ammo, `AAA`=3 Ammo, `AGG`=Ammo+Grenade+Grenade, `M`=Melee/Malfunction (TTS `objects.json`, `startItemDeck` cards). Useful as a cross-check for the vision phase, not authoritative.

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
