# Character Actions

## Shared action framework

- On a player Turn, resolve in order: (1) exactly two Actions, (2) oxygen loss, (3) fire damage. A player may repeat an Action. If unable to perform another Action, they must Pass.
  - **Source:** Rulebook p. 12, “Players’ Turns” / “Resolving Actions” (extracted text lines 2854–2927).
- Pay a Basic Action’s cost by discarding that many Action cards face-up to the discard pile; do not resolve discarded cards’ effects. Pay first, then resolve the selected Action.
- Whenever an Action card is discarded as a result of any effect, place it on the discard pile without resolving that card's printed effect.
  - **Source:** Rulebook p. 12, “Cost in Action Cards” (extracted text lines 2935–2938).
- An effect or action may be selected only if it can be resolved entirely. Some cards offer more than one effect to choose from; the selected effect must satisfy that restriction.
  - **Source:** Rulebook p. 14, “Effects” (extracted text lines 3187–3197).
- “Not in Combat” means the acting Character is not in a Room containing at least one Intruder. Rulebook visual unit `RB-P12-V02` preserves the Basic Action associations: Place 1 Secure token, Activate the Robot, Trade, Use the Room, and Make a Move Cautiously carry the restriction glyph. Card-face associations remain source data on each extracted face (`printedData.upperRight`).
  - **Source:** Rulebook p. 12, “Not in Combat” (extracted text lines 2901–2920); `docs/rules/source-extraction/rulebook-visual-obligations.json`; `assets/tts-mod/extract/card-text-corpus.json`.
- General local-effect default: an unspecified target is in the acting Character’s Room. For an unspecified “Discard a Malfunction marker” effect, the local targets include a Malfunction marker on that Room or on any object in the Room, such as a Weapon the Character is holding.
  - **Boundary:** This example does not settle whether an effect that expressly says “from the Room with the Robot” reaches the Robot or Items there; see `SEM-Q-019`.
  - **Source:** Rulebook p. 16, “Golden Rules — Local Effects” (`RB-P16-003`–`RB-P16-006`).

## ACT-MOVE-001 — Move

- **Cost:** 1 Action card.
- **Source:** Rulebook p. 12, “Basic Actions List” (lines 2876–2878); Rulebook pp. 24–25, “Movement Sequence” and “Exploration Sequence.”
- **Preconditions:**
  - Choose an adjacent Corridor that is not blocked by a Closed Door.
  - Apply any printed “Not in Combat” restriction.
- **Movement sequence:**
  1. Choose Direction — choose an adjacent Corridor.
  2. Resolve Opportunity Attacks — for each Intruder in the departure Room and/or selected Corridor, starting with the largest, resolve an Intruder Attack; resolve at most three such attacks.
  3. Resolve Destination:
     - If the destination is an already Discovered Room: move the Character; if moving cautiously, place one Secure token there; then make a Noise roll.
     - If moving through an Unexplored Corridor to an Undiscovered Room: resolve the Exploration Sequence (ACT-EXPLORE-001).
- **Invariant:** Characters move Room-to-Room and are never placed in Corridors.
- **Restriction:** A Closed Door blocks Character movement; it must first be opened or destroyed by an appropriate effect.
- **Restriction:** Every Movement normally produces a Noise roll, including movement into a Room containing another Character and/or Intruder, unless a special effect explicitly permits movement without one.
  - **Source:** Rulebook p. 25, “Noise Roll After Every Movement” (lines 4702–4705).
- **Distance-ignoring Movement:** When an effect moves a Character to a specified Room regardless of distance, resolve the normal Movement sequence but skip Choose Direction. All other applicable steps and restrictions still resolve.
  - **Source:** Rulebook p. 24, “Secret Passages” (`RB-P24-014`).
- **FAQ:** An action that prevents an Intruder Attack “during a Movement” prevents opportunity attacks only, not a Hazard-result attack from the Noise roll.
  - **Source:** FAQ v1.2, “Action cards” #3 (lines 86–89).
- **Facility-wide exception:** Effects that specifically call out “any object in the Facility” still work even when the target is behind a Closed Door. **Source:** Rulebook p. 22, `BLOCKING PATH — Facility-wide exception`.
- **Destroy eligibility:** Only a Closed Door can be Destroyed. **Source:** Rulebook p. 22, `INTERACTING WITH DOORS — Destroy eligibility`.
- **Boundary:** The first bullet is an explicit source exception and remains visibly distinct from the existing general Closed-Door blocking bullet. No conflict is silently resolved by this proposal.

## ACT-MOVE-002 — Move Cautiously

- **Cost:** 2 Action cards.
- **Source:** Rulebook p. 12, “Basic Actions List” (line 2900); Rulebook pp. 24–25.
- **Procedure:** Same as ACT-MOVE-001, plus: place one Secure token in the destination Room after moving, whether discovered or newly explored.

## ACT-EXPLORE-001 — Exploration Sequence

- **Trigger:** Not a standalone basic action. Occurs whenever a Character moves through an Unexplored Corridor into its empty, Undiscovered Room slot.
- **Source:** Rulebook p. 24, “Exploration Sequence” (lines 4721–4760); Rulebook p. 22, “Common Corridor Keywords.”
- **Preconditions:**
  - The normal movement sequence reaches step 3b.
  - The chosen Corridor is Unexplored and leads to an Undiscovered Room.
  - Orient the drawn Exploration card to the map’s orientation, using the card's North icon and the map's top-left side as the alignment aid.
- **Resolution order:**
  1. Draw an Exploration card. If a draw is required while the deck is empty, shuffle all discarded Exploration cards except those removed from the game to rebuild the deck, then complete the draw.
  2. Set up Room: use the card header to determine its required type, which may be A, B, C, or `?`. Draw a random Room of that type and place it face-up in the destination slot. If a required A, B, or C stack is exhausted, use a random `?` Room instead. A card that directly requires `?` draws from the `?` stack.
  3. Set up Corridors: place a random Corridor face-up in every indicated unoccupied slot unless it would go outside the Facility border or connect to an already placed Room. Orient a new Corridor’s Door slot toward the newly explored Room.
  4. Set up markers and tokens: place exactly the markers/tokens depicted, except do not add Noise to a Corridor that was not placed or already has Noise.
  5. Move Character: move the explorer into the new Room; if the originating movement was cautious, place one Secure token there.
  6. Entrance Effect: resolve it, commonly a Noise roll.
  7. Discard the Exploration card, unless it was removed from the game by its text.
- **FAQ:** “Close all Doors around this Room” affects only Doors touching the new Room, never Hibernatorium Doors; exploration does not resolve in the Hibernatorium.
  - **Source:** FAQ v1.2, “General rules” #4 (lines 30–35).
- **FAQ:** “Remove this card from the game” is not part of the Entrance Effect; an effect that explores while ignoring Entrance Effects still removes such a card.
  - **Source:** FAQ v1.2, “General rules” #5 (lines 37–40).

### Exploration card source occurrences

| Source occurrence | Exact source text to add |
|---|---|
| `assets/tts-mod/extract/v2-dl/tree/cards/game/exploration-025.png` | `Place A/B/C Room`<br>`depending on your Section.`<br>`[character] [malfunction]`<br>`[noise]`<br>`Reminder:`<br>`Place 1 [secure] if you are Moving with [secure].`<br>`Make a Noise roll.` |
| `assets/tts-mod/extract/v2-dl/tree/cards/game/exploration-062.png` | `Place A/B/C Room`<br>`depending on your Section.`<br>`[character]`<br>`[noise]`<br>`Reminder:`<br>`Place 1 [secure] if you are Moving with [secure].`<br>`Entrance Effect:`<br>`Place 3 Adults in the Corridor`<br>`you have just passed through.`<br>`Then, make a Noise roll.` |
| `assets/tts-mod/extract/v2-dl/tree/cards/game/exploration-107.png` | `Place A/B/C Room`<br>`depending on your Section.`<br>`[noise]`<br>`[character]`<br>`[noise]`<br>`Reminder:`<br>`Place 1 [secure] if you are Moving with [secure].`<br>`Entrance Effect:`<br>`Place 2 Adults in the Corridor`<br>`you have just passed through.`<br>`Then, make a Noise roll.` |

- **Diagram note:** Exploration cards do not always show the Corridor the Character has Moved through. **Source:** Rulebook p. 24, `EXPLORATION SEQUENCE — card purpose note`.
- **Base-game icon boundary:** The Insider icon has no base-game function. **Source:** Rulebook p. 24, `EXPLORATION SEQUENCE 6 — Insider icon`.
- **Base-game resolution:** Ignore the Insider icon in base-game play. **Source:** Rulebook p. 24, `EXPLORATION SEQUENCE 6 — ignore`.

- **Boundary:** The card rows remain source occurrences/variants; they do not replace the official Exploration Sequence. `SEM-Q-002` remains open on whether a Noise-roll Entrance Effect is additional to the universal post-Movement Noise requirement.

## ACT-SHOOT-001 — Shoot

- **Cost:** 1 Action card.
- **Source:** Rulebook p. 12, “Basic Actions List” (line 2883); Rulebook p. 33, “Shooting.”
- **Preconditions:**
  - Select a working Ranged Weapon in a Hand.
  - The Weapon has at least one Ammo token.
  - Select an Intruder in the acting Character’s Room.
- **Resolution:**
  1. Deal the target one Hit (place one Universal marker).
  2. Roll the Shoot die:
     - Critical: target dies.
     - Numeric 2–5: target dies if result is less than or equal to its current number of Hits.
     - Ammo-loss: spend one Ammo.
  3. Apply printed Weapon modifiers in addition to the standard result unless the Weapon says “instead.”
- **Clarification:** Shooting normally does not spend Ammo except on the specified die result.
  - **Source:** FAQ v1.2, “Items and tactical gear” #1 (lines 116–124).
- **Restriction:** Characters cannot directly attack other Characters.
  - **Source:** Rulebook p. 33, “Attacking Other Characters” (lines 5621–5626).

## ACT-BURST-001 — Burst

- **Cost:** 1 Action card.
- **Source:** Rulebook p. 12, “Basic Actions List” (line 2885); Rulebook p. 33, “Bursting.”
- **Preconditions:**
  - Select a working, loaded Ranged Weapon in a Hand. A Weapon with the Requires No Ammo trait may Burst without a physical Ammo token and counts as having one for this prerequisite.
  - Select an adjacent Corridor.
  - Closed Doors cannot be crossed to Burst.
- **Resolution:**
  1. Select Weapon and adjacent target Corridor.
  2. Spend Ammo and roll the Burst die.
  3. Apply the rolled number of Hits among Intruders in that Corridor:
     - At most 1 Hit per Adult/Larva.
     - Exactly 2 Hits may be applied to a Drone.
     - Any number up to the Queen’s track maximum may be applied to the Queen.
     - Unused Hits are lost.
  4. Resolve deaths/Queen-track advancement.
  5. On the special Burst result, also resolve any applicable Weapon/Action extra effect.
- **FAQ:** Bursting through Closed Doors is prohibited.
  - **Source:** FAQ v1.2, “General rules” #8 (lines 52–57).

## ACT-MELEE-001 — Melee Attack

- **Cost:** 1 Action card.
- **Source:** Rulebook p. 12, “Basic Actions List” (line 2887); Rulebook p. 34, “Melee Attack” (lines 5628–5667).
- **Preconditions:** Choose an Intruder in the acting Character’s Room. The attack may use a Ranged Weapon, a Melee Weapon, or no Weapon.
- **Resolution:**
  1. Gain one Contamination card.
  2. Choose target in the same Room.
  3. Deal one Hit (place one Universal marker).
  4. Roll the Shoot die and resolve lethal/nonlethal outcome:
     - Critical: Intruder dies — place it back in the Intruder pool.
     - Numeric 2–5: Intruder dies if result is less than or equal to its current number of Hits.
     - Ineffective: Nothing happens.
  5. If target survived: either place a Malfunction marker on one of the attacker’s Weapons to prevent the retaliatory attack, or resolve that Intruder Attack.
- **Note:** Placing a Malfunction marker on a Weapon that already had one destroys the Weapon.
- **Note:** Larvae and the Queen are dealt Hits the same way, but their Health is resolved differently.

## ACT-SEARCH-001 — Search

- **Status:** Search is an Action-card effect, played through the zero-cost “Play an Action card” basic action. It is not listed as a universal one-card Basic Action.
- **Source:** Rulebook p. 12, “Basic Actions List” (lines 2870–2900); Rulebook p. 28, “Gaining Items / Search” (lines 4849–4860).
- **Preconditions:**
  - The Character is in a Room.
  - The played Search card/action is legal under its printed restrictions.
- **Resolution:**
  1. For each Item icon in the acting Character’s Room, draw one Item from the matching Item deck.
  2. The player may choose at most one drawn Item to keep.
  3. Place every unchosen drawn Item on the bottom of its respective deck.
  4. Do not reveal searched-but-unchosen Items to other players.
- **Item placement restrictions:**
  - Regular Items enter the Backpack; Backpack capacity is unlimited and its contents remain secret until used.
  - Heavy Items require a Hand slot. If both Hands are occupied when gaining one, the Character may discard a held Item first to make room.
  - Only one Armor may be worn; a newly gained Armor may replace the current Armor.
  - Any Item discarded for displacement, replacement, or another effect goes to the Items discard pile.
  - **Source:** Rulebook pp. 17 and 28–29, “Discarding Items and Tactical Gear Tokens,” “Backpack,” “Heavy Items,” “Armor Items” (lines 3665–3673, 4849–4910, 5024–5057).
- **Rulebook example:** Life Support Control B has one green and one red Item icon, so Searching there draws one green Item and one red Item before the player decides whether to keep at most one.

## ACT-ITEM-001 — Use Item

- **Cost:** 1 Action card.
- **Source:** Rulebook p. 12, “Basic Actions List” (line 2889); Rulebook p. 28, “Regular Items.”
- **Plain rule:** Resolve the effect of a regular Item (vertical, without Armor keyword). The Item is used and its effect resolves as printed.

## ACT-ROBOT-001 — Activate Robot

- **Cost:** 1 Action card.
- **Setup:** Shuffle all Robot cards, draw 1 without looking at it, and leave every unselected Robot card unseen in the box. Place the Robot model on the Hibernatorium.
- **Restriction:** Not In Combat. The selected Robot card must have been revealed and the Robot must not have a Malfunction marker.
- **Source:** Rulebook p. 8, “Game Setup” (lines 2421–2459); p. 12, “Basic Actions List” and `RB-P12-V02`; pp. 14 and 17, “Effects” and “Golden Rules”; p. 37, “Robot”; exact component family in `docs/rules/semantics/robot-source-index.json`.
- **Activation route:**
  - **Local:** the acting Character is in the Robot’s Room; pay only the normal 1-card cost.
  - **Remote:** the acting Character is in a Computer Room; discard 1 additional Action card.
  - A Character with a Data token may Activate remotely without the additional card; the Data token is not spent.
- **Effect:** Resolve one entirely resolvable option on the exact revealed Robot face. The six base faces and their variants remain keyed by source occurrence, not title alone.
- **Movement constraints:** Each Robot move is Room-to-neighboring-Room, cannot cross a Closed Door, ignores Intruders, and normally cannot traverse an Unexplored Corridor or make Noise. Exploration Robot is the sole printed exception.
- **Tactical Gear:** The Robot starts with 1 full Ammo and 1 Oxygen token. A co-located Character performing Use Any Tactical Gear may use Robot-held tokens and transfer tokens between compatible Character/Robot slots, even while the Robot is malfunctioned.
- **Open boundaries:** `SEM-Q-010` and `SEM-Q-012`–`SEM-Q-019` in `docs/rules/semantics/review-gates.json`; no default is adopted for the affected clauses.

### Source-backed Robot behavior

- **Autonomy:** The Robot does nothing on its own. **Source:** `RB-P37-005` / Rulebook p. 37, `ROBOT — no autonomy`.
- **Assigned Actions:** The Robot performs only Actions assigned by Characters. **Source:** `RB-P37-006` / Rulebook p. 37, `ROBOT — assigned Actions`.
- **Intruders:** Intruders always ignore the Robot. **Source:** `RB-P37-009` / Rulebook p. 37, `ROBOT — Intruder immunity`.
- **Malfunction source wording:** All game effects mentioning the Robot are unavailable while it has a Malfunction marker. **Source:** `RB-P37-020` / Rulebook p. 37, `MALFUNCTION MARKER ON THE ROBOT — effects unavailable`.

### Source-scoped Robot-card occurrences

| Exact source occurrence | Printed Robot-card face text to add verbatim | Source / boundary |
|---|---|---|
| `assets/tts-mod/extract/v2-dl/tree/cards/game/robotDeck-068.jpg` | `Move the [robot] up to 3 times.`<br>`OR`<br>`If the [robot] is in a [computer] Room, use the Room (even with a [malfunction]).` | `CARD-game-robotDeck-game-robotDeck-068.jpg`; preserve `SEM-Q-013`, `SEM-Q-018`, and `SEM-Q-010`; explicit “even with a [malfunction]” remains a source conflict, not a default. |
| `assets/tts-mod/extract/v2-dl/tree/cards/game/robotDeck-137.jpg` | `Move the [robot] up to 2 times.`<br>`OR`<br>`Discard a [malfunction] or a [fire] from the Room with the [robot].` | `CARD-game-robotDeck-game-robotDeck-137.jpg`; preserve `SEM-Q-013` and `SEM-Q-019`; do not choose the marker target scope. |

## ACT-TRADE-001 — Trade

- **Cost:** 1 Action card.
- **Source:** Rulebook p. 12, “Basic Actions List” (line 2893); Rulebook p. 29, “Trading”; FAQ v1.2, “Items and tactical gear” #5 (lines 141–143).
- **Preconditions:**
  - All participants are in the same Room as the acting Character.
  - Each transfer/exchange has the mutual consent required by the rule.
- **Effect:**
  - All co-located Characters may reveal and exchange Items and/or Tactical Gear tokens with the acting Character.
  - Multi-party exchanges are allowed if the active Character agrees.
  - A participant may give an Item/token without receiving anything in return.
  - A traded Item is gained immediately and may be used immediately where otherwise legal.
- **Interplay boundary:** An Item may be used directly on a consenting Character in the same Room only for: restoring Health, discarding Serious Wounds, discarding Malfunction markers, or gaining. For other effects, trade the Item first so the recipient uses it.
  - **Source:** Rulebook p. 29, “Interplay”; FAQ v1.2, “Items and tactical gear” #8 (lines 154–161).

## ACT-SECURE-001 — Place Secure Token

- **Cost:** 1 Action card.
- **Source:** Rulebook p. 12, “Basic Actions List” (line 2880); Rulebook p. 23, “Secure tokens.”
- **Preconditions:** The Room must not contain an Intruder. Some Rooms cannot be Secured; the Nest is one such Room. Maximum three Secure tokens per Room.
- **Effect:** Place one Secure token in the acting Character’s Room.
- **FAQ:** Secure tokens prevent attacks from Intruders being placed in the Room (consuming one token per entry).
  - **Source:** FAQ v1.2, “General rules” #11 (lines 70–72).

## ACT-ROOM-001 — Use Room

- **Cost:** 2 Action cards.
- **Source:** Rulebook p. 12, “Basic Actions List” (line 2898); Rulebook pp. 20–23, “Rooms.”
- **Plain rule:** Resolve the Room effect printed on the Room tile or its Exploration card. Each Room has a specific effect described in the Room section of the rulebook.

- **Drilling Room:** The Drilling Room permits new Corridors to be drilled. **Source:** Rulebook p. 19, `SECTION A — Drilling Room`.
- **Life Support Control A:** Life Support Control A can remove Fire. **Source:** Rulebook p. 19, `SECTION A — Life Support Control A fire`.
- **Surgery Room:** The Surgery Room can discard Serious Wounds. **Source:** Rulebook p. 19, `SECTION A — Surgery Room`.
- **Surgery Room infection:** The Surgery Room can remove a Larva Infection. **Source:** Rulebook p. 19, `SECTION A — Surgery Room infection`.
- **Life Support Control B:** Life Support Control B changes Section B’s Life Support state. **Source:** Rulebook p. 19, `SECTION B — Life Support Control B`.
- **Anti-Aircraft:** Life Support Control B can inspect and change the Anti-Aircraft system. **Source:** Rulebook p. 19, `SECTION B — Anti-Aircraft`.
- **Server Room:** The Server Room can provide a Data token used by some Objectives. **Source:** Rulebook p. 19, `SECTION B — Server Room`.
- **Room special icons:** Rooms may feature other icons showing special rules. A Room with the crossed-Secure special icon is never Secured. A Room with the crossed-Malfunction special icon cannot be broken and cannot receive a Malfunction marker. **Source:** Rulebook p. 20, `Room-tile anatomy F`, `Room special icon — no Securing`, `Room special icon — unbreakable`, and `Room special icon — no Malfunction marker`.
- **Life Support Control A printed effect:** `Flip an [Active/Inactive Life Support token glyph] in Section A.` **Source:** Rulebook p. 20, `LIFE SUPPORT CONTROL “A” tile — first effect`. The glyph remains source-local.
- **Nest pickup:** A Character may pick up an Egg with the Nest Room Action. **Source:** Rulebook p. 20, `NEST — pickup`.
- **Nest destruction method:** Use the Nest Room Action to remove Eggs for Nest destruction. **Source:** Rulebook p. 20, `NEST — destruction method`.
- **Nest destruction marker:** When the Eggs space is empty, place a Universal marker on it. A Universal marker on the empty Eggs space signifies that the Nest is destroyed. Once destroyed, the Nest remains destroyed even if Eggs are later added. **Source:** Rulebook p. 20, `NEST — destruction marker`, `NEST — marker meaning`, and `NEST — permanence`.

### Room Help source occurrences

| Entry | Printed section marker | Printed number / title | Exact printed effect | Exact associated note or cross-reference |
|---|---|---|---|---|
| 0 | `?` | `01 — SPRINKLERS CONTROL` | `Discard all [R01-I04]`<br>`from a chosen Section.` | — |
| 12 | `?` | `13 — DECONTAMINATION ROOM` | `Discard all [R13-I04] and spend 2 [R13-I05]`<br>`to remove all Contaminations`<br>`from your deck`<br>`and discard pile`<br>`without scanning.` | `You may not perform this Room Action if you have 1 [R13-I06] or fewer (if you would gain a Suffocation token as a result).` |
| 14 | `A` | `15 — LIFE SUPPORT CONTROL \"A\"` | `Flip an [R15-I04] / [R15-I05] in Section A.`<br>`OR`<br>`Discard a [R15-I06] from any Room`<br>`in the Facility.` | `With this Room’s top effect you can activate or deactivate the Life Support System in the “A” Section.` |
| 15 | `A` | `16 — SURGERY ROOM` | `Discard all [R16-I04] to remove a Larva`<br>`from your Character board and scan`<br>`all Contaminations in your deck`<br>`and discard pile.`<br>`Remove the Infected ones from the game.`<br>`OR`<br>`Discard`<br>`1 Serious Wound.` | `You can’t perform this Room’s top effect if you don’t have a Larva on your Character board. However, you don’t need to have any Contamination cards to perform it. \| After performing the Action, place the remaining scanned Contaminations back in your deck and then reshuffle the whole deck.` |
| 16 | `A` | `17 — DRILLING STATION` | `Place a new Corridor`<br>`leading from the Room`<br>`with the [R17-I05].` | `This Corridor may be placed leading to an already Discovered Room or to an Undiscovered Room.` |
| 17 | `B` | `18 — HIBERNATORIUM` | `Make a Noise roll to Hibernate.` | `You can only perform this Room’s effect if the Hibernatorium is [R18-I01]. The Hibernatorium can be turned [R18-I02] in Life Support Control C. \| If there is an Intruder in your Room after the Noise roll, this Action fails.`<br>Cross-reference: `More on Hibernating - see Hibernating (page 38).` |
| 18 | `B` | `19 — LIFE SUPPORT CONTROL \"B\"` | `Flip an [R19-I03] / [R19-I04] in Section B.`<br>`OR`<br>`Look at both Anti-Aircraft tokens`<br>`and place them`<br>`in any order.` | `With this Room’s top effect you can activate or deactivate the Life Support System in the “B” Section. \| Remember that the top Anti-Aircraft token indicates the current status of the Anti-Aircraft system. \| You are not required to share how tokens are placed, nor if you have swapped them or not.` |
| 19 | `B` | `20 — SERVER ROOM` | `Use any Discovered [R20-I04] Room`<br>`in the Facility.`<br>`OR`<br>`Gain a Data token`<br>`(if you don’t have one).` | `Please note that you may not use a Room with a [R20-I05] in this way.` |
| 2 | `?` | `03 — EMERGENCY ROOM` | `Restore 2 [R03-I04].`<br>`OR`<br>`Discard`<br>`1 Serious Wound.` | — |
| 20 | `B` | `21 — COOLING SYSTEM` | `Activate the Autodestruction`<br>`Procedure.` | Cross-reference: `More on Autodestruction Procedure - see page 38.` |
| 22 | `C` | `23 — REACTOR` | `Remove`<br>`all [R23-I03], [R23-I04], [R23-I05],`<br>`and both Anti-Aircraft tokens`<br>`from the game.` | `After removing these tokens: treat all Sections as [R23-I06]. Treat the Anti-Aircraft System as Inactive. \| Remove the [R23-I07] token even if it is already on the Round track. \| [R23-I08], Anti-Aircraft and [R23-I09] cannot be turned on again.` |
| 23 | `C` | `24 — ESCAPE SHUTTLE` | `Make a Noise roll to get into`<br>`the Escape Shuttle.` | `If there is an Intruder in your Room after the Noise roll, this Action fails. \| When a Character Escapes using the Escape Shuttle, the Escape Shuttle cannot be used again in that game – there is only 1 shuttle available.`<br>Cross-reference: `More on “getting into the Escape Shuttle” – see Escaping (page 38).` |
| 3 | `?` | `04 — SUPPLY ROOM` | `Draw 1 Green, 1 Red, and 1 Yellow Item.`<br>`You may keep 2 of them`<br>`and discard`<br>`the rest.` | — |
| 4 | `?` | `05 — ARMORY` | `Gain any number`<br>`of [R05-I04] and [R05-I05].` | `All gained Tactical Gear tokens must be placed in empty Tactical Gear slots. You may discard any number of your Tactical Gear tokens once, before or during this Action.` |
| 6 | `?` | `07 — SECURITY ROBOT ROOM` | `Place 1 [R07-I04] in the Room with the [R07-I05].`<br>`OR`<br>`Reinforce an empty Corridor`<br>`adjacent to the Room`<br>`with the [R07-I06].` | — |
| 7 | `?` | `08 — GUNNERY ROOM` | `Choose a Corridor adjacent to a Room`<br>`with a [R08-I05] and without a [R08-I06].`<br>`Roll a Burst die and deal Hits equal`<br>`to the result in that Corridor.` | `Note that “roll a Burst die” does not mean a Burst Action, so it does not require spending [R08-I07].` |
| 9 | `?` | `10 — ALARM ROOM` | `Resolve or discard [R10-I04]`<br>`from a chosen Corridor`<br>`in the Facility.` | — |

- **Boundary:** `OQ-009` remains open for the physical resolution of official effects that target an Undiscovered Nest. `SEM-Q-005` remains open for the Drilling Station endpoint selector. The table does not translate any `[R..-I..]` placeholder into a canonical icon or effect beyond the exact source text.

## ACT-TACTICAL-001 — Use Tactical Gear

- **Cost:** 1 Action card.
- **Source:** Rulebook p. 12, “Basic Actions List” (line 2895); Rulebook p. 16, “Tactical Belt.”
- **Plain rule:** Use any Tactical Gear token. Multiple tokens may be used at once; the player chooses which token to use one by one.
- **Oxygen:** Gain 3 Oxygen and rotate the Oxygen dial to the new value, never above 7.
- **Grenade:** Choose an adjacent Corridor, roll one Burst die, add 2 to its result, and deal that many Hits in the chosen Corridor. The Ammo-loss face has no effect, this is not a Burst Action, and Weapon effects do not apply.
- **Medpack:** Restore 2 Health Points.
- **FAQ:** Grenade Launcher grenades may be thrown from a malfunctioning Grenade Launcher with the Use Any Tactical Gear action.
  - **Source:** FAQ v1.2, “Items and tactical gear” #4 (lines 135–139).
- **Plain rule:** Then, discard all chosen tokens (apart from Ammo tokens, which are moved to Weapons as a part of their effect). You may also move any number of your tokens between your Tactical slots.
- **Source:** Rulebook p. 16, `USE ANY TACTICAL GEAR ACTION` discard and rearrangement clauses (`RB-P16-027` and `RB-P16-029`).
- **Boundary:** Preserve `ITM-005` slot compatibility, the loaded-Ammo restriction, and the source-stated Ammo transfer exception.

## ACT-OXYGEN-001 — Personal Oxygen and Suffocating

- **Source:** Rulebook p. 17, “Oxygen,” “Oxygen tokens,” and “Suffocating” (`RB-P17-006`, `RB-P17-013`–`RB-P17-016`).
- **Range:** A Character's Oxygen supply cannot exceed 7. An Action that spends Oxygen is illegal if paying it would reduce Oxygen below 0.
- **Tracking:** Rotate the Character's Oxygen dial whenever Oxygen is spent or gained so it shows the new value.
- **Suffocating trigger:** When the Oxygen counter reaches the Suffocating space, gain a Suffocating token and immediately reset the Oxygen dial to 0.
- **Existing-token consequence:** A Character with a Suffocating token dies the next time they lose Oxygen.
- **Recovery:** Discard the Suffocating token when that Character gains Oxygen or ends a Turn in a Section with active Life Support.

## Malfunction markers

- **Source:** Rulebook p. 23, “Malfunction Markers” (`RB-P23-019`, `RB-P23-030`, `RB-P23-037`–`RB-P23-046`).
- **Meaning:** A Malfunction marker represents a broken component whose affected functionality is unavailable under the component-specific rules.
- **Heavy Item:** Its Action cannot be used. If an effect would place a second Malfunction marker on the Item, destroy and discard the Item instead.
- **Robot:** A Robot with a Malfunction marker cannot be activated or used by Room interactions or Robot Actions. Treat its card as having no text and no icons. It may still satisfy an effect that merely requires a Robot—for example, a Secure Action card—and Tactical Gear on it remains available under ACT-ROBOT-001. Ignore an instruction to place a second Malfunction marker on it.

## Doors

- **State model:** Open | Closed | Destroyed.
- A Door slot initially represents an Open Door.
- Close: only at a Door slot; place a Door token.
- Open: remove the Door token.
- Destroy: lay down the token; thereafter it behaves as Open but can never be Closed again.
- **Source:** Rulebook pp. 22–23, “Doors” / “Interacting with Doors.”
- **Blocking rule:** A Closed Door blocks access to every object/effect on the other side except Noise markers. Characters cannot move, Burst, reinforce a Corridor, command another Character, throw grenades, or otherwise affect objects through it. Noise markers may still be placed or discarded through Closed Doors.
  - **Source:** Rulebook p. 22, “Blocking Path”; FAQ v1.2, “General rules” #8 (lines 52–57).
- **Adjacency is preserved:** A Room and a Corridor joined by a Closed Door are still considered adjacent, and two Rooms with a Door between them are still considered neighboring. A Closed Door removes permission, not adjacency. Any rule that keys on “adjacent” or “neighboring” still applies across a Closed Door unless that rule is itself an access/effect the Door blocks.
  - **Source:** Rulebook p. 22, “Doors” (extracted text lines 4244–4252).
  - **Consequence for UI:** A Closed-Door destination must be presented as blocked-with-reason, not as non-adjacent. Omitting it entirely would misrepresent the map topology; see FND-005’s legal-target invariant, which excludes it from *Move choices* specifically.
- **Door slot placement:** A Door slot sits at the end of a Corridor, against a Room, not at the Corridor’s midpoint. When a Corridor is placed during Exploration, orient its Door slot toward the newly Explored Room.
  - **Source:** Rulebook p. 22, “Doors” note (line 4253–4255); Rulebook p. 24, “Exploration Sequence” (lines 4505–4508).
- **Intruder movement:** Intruders attempting to move through a Closed Door destroy the Door instead and do not move in that movement attempt.
  - **Source:** Rulebook p. 31, “Intruders Moving Through Doors.”
- **Fire:** When a card instructs Fire to spread, place Fire markers in neighboring Rooms exactly as that card directs. Closed Doors prevent Fire spreading between the blocked Rooms unless the responsible effect says otherwise.
  - **Source:** Rulebook p. 23, “Doors and Spreading Fire” (`RB-P23-017`).
- **Note:** The rules define Door states and say Doors are opened by an “appropriate Action,” but do not provide a universal `Open Door` Basic Action. Opening/closing is implemented only where a specific Room, Item, Action card, Exploration Entrance Effect, or other effect grants it.

## Noise

### Noise-roll procedure

- **Source:** Rulebook p. 25, “Noise Roll,” “Resolving Noise Markers,” “Surprise Attacks” (lines 4655–4710).
- **Procedure:**
  1. Roll the Noise die.
  2. For a numbered result (1–4), find every Corridor adjacent to the acting Character’s Room with that Noise value and resolve each:
     1. If it contains Intruder(s), move its largest Intruder to the Character’s Room.
     2. Else if it contains a Noise marker, resolve that marker: remove it, draw and resolve an Intruder token in that Corridor, then discard the token as instructed.
     3. Else place a Noise marker there.
  3. For a Hazard result, draw/resolve an Intruder token using its type icon only; ordinarily it places an Intruder in the Character’s Room. Ignore the token’s numeric reverse side, then discard the token as instructed.
  4. Whenever an Intruder enters a Room with a Character, it immediately attempts an Intruder Attack, subject to protections such as Secure tokens.

### Noise-marker constraints

- A Corridor with an Intruder cannot receive a Noise marker.
- If an Intruder enters a Corridor containing Noise, discard the Noise marker first.
- A Reinforced Corridor has Noise value 0, so a normal numbered Noise roll cannot place Noise there; Intruders can still enter it.
- Movement and other Actions may place Noise markers in Corridors, subject to these constraints.
- **FAQ:** “Resolve a Noise marker in each Unexplored Corridor” only resolves markers that already exist—it does not create them.
  - **Source:** FAQ v1.2, “General rules” #6 (lines 42–46).
- **Source:** Rulebook pp. 21–22, “Reinforced Corridor” / “Intruders and Noise Markers.”

## Actions not found in the base game

### Craft

- **Status:** No generic Craft action exists in the base-game Basic Actions list or rulebook.
- **Guidance:** Treat any crafting-like effect as a specific card/Room/expansion rule, not an assumed system.

### Rest

- **Status:** Source extraction is complete. Rest is an Action-card effect, not a Basic Action. The project-owner-reviewed canonical face is `assets/tts-mod/extract/v2-dl/tree/cards/game/action/rest.png`; it carries `notInCombat` and instructs the Character to resolve the Infection Procedure and remove all Uninfected cards from the game. A separate TTS Medical Support face and the licensed-digital six-character records preserve their wording/version differences independently.
- **Source:** Rulebook p. 38, “Infection Procedure” (lines 6079–6098); `assets/tts-mod/extract/card-text-corpus.json` source tuple `69eee8ba…`; `docs/rules/source-extraction/secondary/bga-staticData-260622-1220.js`.
- **Boundary:** This closes the former transcription blocker. Exact cross-version wording reconciliation belongs to source-variant/semantic review; do not rewrite one source from another.

## ACT-CARD-001 — Action card identity and anatomy

- **Classification:** Source-backed rule record. Added from the rulebook’s Action-card anatomy passage and card images.
- **Source:** Rulebook p. 13, “Playing Action Cards”; p. 14, “Action cards” anatomy list A–E (extracted text lines 3161–3179); Rulebook p. 12, “Basic Actions List” (lines 2870–2900).
- **Plain rule:** An Action card is a distinct game object from a Basic Action. A Basic Action is a always-available option printed on the Character board and paid for by discarding Action cards. An Action card is a named, Character-specific card with its own printed effect, resolved only through the zero-cost `Play an Action card` Basic Action.
- **Playing procedure:** Reveal the chosen Action card from hand, resolve its printed Action effect, then place the card on top of its discard pile.
- **Card anatomy:** Each Action card has these printed parts:
  1. **Not In Combat** symbol, when present — the card cannot be used in a Room with an Intruder.
  2. **Title** — the card’s name.
  3. **Action Card’s Effects** — the effect resolved when the card is played.
  4. **Reaction Effect**, when present — see RT-003; a Reaction is not an Action.
  5. **Character** — the Character whose deck the card belongs to.
- **Dual roles of one card:** The same physical card may be spent two different ways, and only one of them resolves its printed text:
  - Discarded as *payment* for a Basic Action cost — its printed effect is **not** resolved (see the shared action framework, “Cost in Action Cards”).
  - Played via `Play an Action card` — its printed effect **is** resolved, then it goes to the discard pile.
- **Invariant:** An Action card’s Title must never be presented as if it were a Basic Action, and a Basic Action must never be presented as if it were a card in hand. A player choosing what to do selects a Basic Action; a player choosing what to spend or play selects a card.
- **Naming invariant:** Action card identifiers must not reuse Basic Action names (`move`, `shoot`, `useRoom`, and similar). Reusing them makes the two categories indistinguishable in state, logs, and UI. See BUG-023.
- **Rulebook-illustrated faces:** These faces are directly illustrated in the rulebook:
  - **Sprint** (Recon) — “Move. Then, you may spend 1 to Move again.” Source: Rulebook Recon card image (extracted text lines ~332–338).
  - **Duck and Cover** (Contractor: Consultant) — “Discard 1 Action card to Move. During that Movement, Prevent 1 Intruder Attack.” Its Reaction triggers when an Intruder would Attack this Character in a Room with another Character; that Intruder Attacks the other Character instead. Source: Rulebook pp. 14 and 13 card image (`RB-P13-009`–`RB-P13-010`; extracted lines 3118–3127, 3190–3196).
- **Deck size:** Each Character has their own 10-card Action deck; the rulebook lists 60 Action cards total (line 528). `semantics/action-source-index.json` mechanically reconciles six exact Character memberships from seven TTS root segments (including the five-card Shared Contractor root), while preserving component scans/selector gaps and all 60 licensed-digital rows independently.
- **Authority boundary:** The former missing-data blocker (OQ-010) is resolved. All 60 exact physical occurrences now have occurrence-keyed semantic records, but licensed rows, current official examples, TTS variants, and unresolved local glyph/Command/Reaction questions remain source-scoped and must not be silently collapsed. This family closure is not full base-game semantic coverage.

### Source-scoped Action-card occurrences

| Exact source occurrence | Printed face text to add verbatim | Source / boundary |
|---|---|---|
| `assets/tts-mod/extract/v2-dl/tree/cards/character/combat-engineer-017.png` | `Move the [lander] by 1 space in any direction.`<br>`OR`<br>`COMMAND` `Choose a lower ranking [character] in your Room or neighbouring one. Make the chosen [character] Move, Shoot, or Burst. (you make all choices).`<br>`REACTION` `When a [character] with a higher Rank plays a Command on you: Cancel the effect of that Command. That [character] must still pay the Action's cost.` | `CARD-character-combat-engineer-character-combat-engineer-017.png`; preserve `RT-003`, `RT-013`, `SEM-Q-059`, `SEM-Q-060`, and `SEM-Q-074`. |
| `assets/tts-mod/extract/v2-dl/tree/cards/character/combat-engineer-021.png` | `Shoot: On Hit deal 1 more. [shootDieCritical]: Spend [ammoToken].` | `CARD-character-combat-engineer-character-combat-engineer-021.png`; source tokens remain literal. |
| `assets/tts-mod/extract/v2-dl/tree/cards/character/combat-engineer-034.png` | `Discard 1 [actionCard] and spend [ammoToken] from a Weapon to Move through an empty Corridor.`<br>`You may Move another [character] with you if they agree`<br>`- they do not make a Noise roll.`<br>`During that Movement, prevent all [intruder] Attacks.` | `CARD-character-combat-engineer-character-combat-engineer-034.png`; preserve `SEM-Q-073`. |
| `assets/tts-mod/extract/v2-dl/tree/cards/character/heavy-gun-operator-002.png` | `Spend [ammoToken] from your Ranged Weapon, Repel all [intruder] from your Room.` | `CARD-character-heavy-gun-operator-character-heavy-gun-operator-002.png`; no Repel scope beyond the face. |
| `assets/tts-mod/extract/v2-dl/tree/cards/character/heavy-gun-operator-005.png` | `Choose a Weapon with [ammoToken] and Burst using it.`<br>`Then, you may Move through the Corridor you have Bursted at, prevent [intruder] Attacks.` | `CARD-character-heavy-gun-operator-character-heavy-gun-operator-005.png`; preserve `SEM-Q-073`. |
| `assets/tts-mod/extract/v2-dl/tree/cards/character/heavy-gun-operator-045_cards/card-02.png` | `title: DEMOLITION`<br>`Remove 1 Door.`<br>`OR`<br>`Place a [malfunction] in your Room.` | `CARD-character-heavy-gun-operator-character-heavy-gun-operator-045_cards-card-02.png`; `RECON` section metadata retained; separate occurrence. |
| `assets/tts-mod/extract/v2-dl/tree/cards/character/heavy-gun-operator-045_cards/card-03.png` | `Discard 1 [actionCard].`<br>`Discard a [malfunction].`<br>`OR`<br>`Open or Close 1 Door.` | `CARD-character-heavy-gun-operator-character-heavy-gun-operator-045_cards-card-03.png`; separate occurrence. |
| `assets/tts-mod/extract/v2-dl/tree/cards/character/heavy-gun-operator-045_cards/card-05.png` | `title: SCOUTING`<br>`Move.`<br>`Before the Noise roll, place 1 [secure] in the Room you are Moving to.`<br>`section: [ICON: red diagonal X over a white horizontal bar with short red inset marks]` | `CARD-character-heavy-gun-operator-character-heavy-gun-operator-045_cards-card-05.png`; retain `RECON` section and unresolved glyph; preserve `SEM-Q-057`/`SEM-Q-073`. |
| `assets/tts-mod/extract/v2-dl/tree/cards/character/heavy-gun-operator-045_cards/card-07.png` | `title: SECURE`<br>`Place 2 [secure].`<br>`OR`<br>`Reinforce 1 empty Corridor that leads to a Room with a Character or [robot].` | `CARD-character-heavy-gun-operator-character-heavy-gun-operator-045_cards-card-07.png`; source tokens remain literal. |
| `assets/tts-mod/extract/v2-dl/tree/cards/character/heavy-gun-operator-045_cards/card-08.png` | `title: SHOOT FIRST`<br>`typeLine: Move.`<br>`If there is an [intruder] in your Room or an adjacent Corridor, you may Shoot or Burst.`<br>`Resolve it before that Intruder Attacks.` | `CARD-character-heavy-gun-operator-character-heavy-gun-operator-045_cards-card-08.png`; preserve `SEM-Q-073`. |
| `assets/tts-mod/extract/v2-dl/tree/cards/character/heavy-gun-operator-045_cards/card-10.png` | `title: BREAKTHROUGH`<br>`Choose a Rifle with [ammoToken] and Burst using it.`<br>`Then, you may Move through the Corridor you have Bursted at.`<br>`section: [ICON: red X over a white stepped horizontal bar-like glyph]` | `CARD-character-heavy-gun-operator-character-heavy-gun-operator-045_cards-card-10.png`; retain `HEAVY GUN OPERATOR` section and unresolved glyph; preserve `SEM-Q-057`/`SEM-Q-073`. |
| `assets/tts-mod/extract/v2-dl/tree/cards/character/heavy-gun-operator-045_cards/card-13.png` | `title: DEMOLITION`<br>`Remove 1 Door.`<br>`OR`<br>`Place a [malfunction] in your Room.`<br>`footer: HEAVY GUN OPERATOR` | `CARD-character-heavy-gun-operator-character-heavy-gun-operator-045_cards-card-13.png`; generated sheet-cell source variant; `sourceSha256: b3b209538a4ac8554ae6e5230f4a98b1fa1ff3bd8f89b3ccfbee53d115997e9e`; `1052x1433`; functional icon evidence is the source-bound annular cog matching `malfunction`, but promotion remains deferred; no selected base-root CardID/GUID selector. |
| `assets/tts-mod/extract/v2-dl/tree/cards/character/heavy-gun-operator-045_cards/card-14.png` | `Choose a Weapon and perform in any order:`<br>`• Reload the Weapon.`<br>`• Shoot or Burst.` | `CARD-character-heavy-gun-operator-character-heavy-gun-operator-045_cards-card-14.png`; preserve “in any order”. |
| `assets/tts-mod/extract/v2-dl/tree/cards/character/heavy-gun-operator-045_cards/card-16.png` | `title: REPAIRS`<br>`Discard 1 [actionCard]. Discard a [malfunction].`<br>`OR`<br>`Open or Close 1 Door.` | `CARD-character-heavy-gun-operator-character-heavy-gun-operator-045_cards-card-16.png`; separate occurrence. |
| `assets/tts-mod/extract/v2-dl/tree/cards/character/heavy-gun-operator-045_cards/card-19.png` | `title: SECURE`<br>`Place 2 [secure].`<br>`OR`<br>`Reinforce 1 empty Corridor that leads to a Room with a Character or [robot].` | `CARD-character-heavy-gun-operator-character-heavy-gun-operator-045_cards-card-19.png`; separate occurrence. |
| `assets/tts-mod/extract/v2-dl/tree/cards/character/heavy-gun-operator-045_cards/card-20.png` | `title: CHAIN` / `OF COMMAND`<br>`Move the [intruder] by 1 space in any direction.`<br>`OR`<br>`COMMAND` `Choose a Character with a lower Rank. Then, Move, Shoot, or Burst using this Character.`<br>`REACTION` `When a Character with a higher Rank plays a Command on you: Cancel the effect of that Command. That Character must still pay the Action’s cost.` | `CARD-character-heavy-gun-operator-character-heavy-gun-operator-045_cards-card-20.png`; preserve `RT-003`, `RT-013`, `SEM-Q-059`, `SEM-Q-060`, and `SEM-Q-074`. |
| `assets/tts-mod/extract/v2-dl/tree/cards/character/heavy-gun-operator-045_cards/card-21.png` | `title: COMPUTER SKILLS`<br>`If you are in [computer] Room, use the Room.`<br>`OR`<br>`Open or Close 1 chosen Door in the Facility.` | `CARD-character-heavy-gun-operator-character-heavy-gun-operator-045_cards-card-21.png`; no extra Room or Door scope. |
| `assets/tts-mod/extract/v2-dl/tree/cards/character/heavy-gun-operator-045_cards/card-22.png` | `title: DEMOLITION`<br>`Remove 1 Door.`<br>`OR`<br>`Place a [malfunction] in your Room.` | `CARD-character-heavy-gun-operator-character-heavy-gun-operator-045_cards-card-22.png`; separate occurrence. |
| `assets/tts-mod/extract/v2-dl/tree/cards/character/heavy-gun-operator-045_cards/card-24.png` | `title: FAST REPAIRS`<br>`Discard a [ICON: white gear glyph].`<br>`OR`<br>`Open or Close 1 Door.` | `CARD-character-heavy-gun-operator-character-heavy-gun-operator-045_cards-card-24.png`; preserve unresolved glyph literally. |
| `assets/tts-mod/extract/v2-dl/tree/cards/character/heavy-gun-operator-045_cards/card-27.png` | `title: SEARCH`<br>`Draw 1 Item for each [ICON: white filled octagonal glyph] in your Room.`<br>`Keep 1 and discard the rest.` | `CARD-character-heavy-gun-operator-character-heavy-gun-operator-045_cards-card-27.png`; preserve `SEM-Q-058`; generic `ACT-SEARCH-001` is not an icon crosswalk. |
| `assets/tts-mod/extract/v2-dl/tree/cards/character/heavy-gun-operator-045_cards/card-29.png` | `title: TACTICAL RETREAT`<br>`Spend [ICON: red clipped-corner badge with black cartridge-like glyph] from your Ranged Weapon.`<br>`Move. You may Move another Character with you if they agree — only you make a Noise roll.`<br>`Ignore all Opportunity Attacks during that Movement.` | `CARD-character-heavy-gun-operator-character-heavy-gun-operator-045_cards-card-29.png`; preserve `SEM-Q-073`; unresolved resource glyph remains literal. |
| `assets/tts-mod/extract/v2-dl/tree/cards/character/heavy-gun-operator-045_cards/card-31.png` | `title: DEMOLITION`<br>`Remove 1 Door.`<br>`OR`<br>`Place a [malfunction] in your Room.` | `CARD-character-heavy-gun-operator-character-heavy-gun-operator-045_cards-card-31.png`; separate occurrence. |
| `assets/tts-mod/extract/v2-dl/tree/cards/character/heavy-gun-operator-045_cards/card-32.png` | `title: FIRE AT WILL`<br>`Move the [ICON: white jagged silhouette glyph with tall central spike] by 1 in any direction.`<br>`OR`<br>`COMMAND` `All Characters in your Room (including you) Burst at the Corridor of your choice.` | `CARD-character-heavy-gun-operator-character-heavy-gun-operator-045_cards-card-32.png`; preserve `RT-013` and `SEM-Q-059`; unresolved silhouette remains literal. |
| `assets/tts-mod/extract/v2-dl/tree/cards/character/heavy-gun-operator-045_cards/card-33.png` | `title: LET'S GO!`<br>`Move the [ICON: white three-lobed upright silhouette] by 1 in any direction.`<br>`OR`<br>`Move with another Character.`<br>`Only you make a Noise Roll.` | `CARD-character-heavy-gun-operator-character-heavy-gun-operator-045_cards-card-33.png`; preserve `SEM-Q-073`; no consent or glyph default. |
| `assets/tts-mod/extract/v2-dl/tree/cards/character/heavy-gun-operator-045_cards/card-38.png` | `title: SECURE`<br>`Place 2 [secure].`<br>`OR`<br>`Reinforce 1 empty Corridor that leads to a Room with a Character or [robot].` | `CARD-character-heavy-gun-operator-character-heavy-gun-operator-045_cards-card-38.png`; separate occurrence. |
| `assets/tts-mod/extract/v2-dl/tree/cards/character/heavy-gun-operator-045_cards/card-42.png` | `Remove 1 Door.`<br>`OR`<br>`Place a [malfunction] in your Room.` | `CARD-character-heavy-gun-operator-character-heavy-gun-operator-045_cards-card-42.png`; separate occurrence. |
| `assets/tts-mod/extract/v2-dl/tree/cards/character/heavy-gun-operator-045_cards/card-44.png` | `title: FIRST AID`<br>`Restore 1 [characterHealth].`<br>`OR`<br>`If you are in a Room with [greenItem]: Gain 1 [medpackToken].` | `CARD-character-heavy-gun-operator-character-heavy-gun-operator-045_cards-card-44.png`; source tokens remain literal. |
| `assets/tts-mod/extract/v2-dl/tree/cards/character/medical-support-023.jpg` | `title: FIELD SURGERY`<br>`Discard 1 [actionCard] to discard 1 Serious Wound from a [character] of your choice in your Room.`<br>`Discard 1 [medpackToken] or that [character] gains 1 Contamination.` | `CARD-character-medical-support-character-medical-support-023.jpg`; preserve `SEM-Q-065`; no choice/consent default. |
| `assets/tts-mod/extract/v2-dl/tree/cards/character/medical-support-028.jpg` | `title: FIRST AID`<br>`Restore 1 [characterHealth].`<br>`OR`<br>`If you are in a Room with a [greenItem]: Gain 1 [medpackToken].` | `CARD-character-medical-support-character-medical-support-028.jpg`; preserve `SEM-Q-065`; distinct occurrence from HGO card 44. |
| `assets/tts-mod/extract/v2-dl/tree/cards/character/medical-support-033.jpg` | `title: COMBAT DRUGS`<br>`Discard 1 [greenItem] to choose a [character] in your Room.`<br>`They draw [actionCard] until they have 3 [actionCard] in hand.` | `CARD-character-medical-support-character-medical-support-033.jpg`; preserve `SEM-Q-065` and `SEM-Q-072`. |
| `assets/tts-mod/extract/v2-dl/tree/cards/character/medical-support-039.jpg` | `Place 2 [secure].`<br>`OR`<br>`Discard 1 [actionCard] to Reinforce 1 empty, adjacent Corridor that leads to a Room with a [character] or the [robot].` | `CARD-character-medical-support-character-medical-support-039.jpg`; retain “empty, adjacent” and source tokens. |
| `assets/tts-mod/extract/v2-dl/tree/cards/character/medical-support-048.jpg` | `Discard 1 [actionCard] to discard a [malfunction].`<br>`OR`<br>`Open or Close 1 accessible Door.` | `CARD-character-medical-support-character-medical-support-048.jpg`; “accessible Door” remains undefined beyond the face. |
| `assets/tts-mod/extract/v2-dl/tree/cards/character/medical-support-049.jpg` | `title: DEMOLITION`<br>`Destroy 1 accessible Door.`<br>`OR`<br>`Place a [malfunction] in your Room.` | `CARD-character-medical-support-character-medical-support-049.jpg`; separate occurrence; preserve “accessible Door”. |
| `assets/tts-mod/extract/v2-dl/tree/cards/character/officer-009.png` | `title: SECURE`<br>`Place 2 [secure].`<br>`OR`<br>`Discard 1 [actionCard]. Reinforce 1 empty Corridor that leads to a Room with a Character or [robot].` | `CARD-character-officer-character-officer-009.png`; separate occurrence. |
| `assets/tts-mod/extract/v2-dl/tree/cards/character/officer-014.png` | `title: FIRE AT WILL`<br>`Move the [intruder] by 1 in any direction.`<br>`OR`<br>`COMMAND` `Choose your Room or a neighbouring one, each [character] in that Room Burst at an adjacent Corridor of your choice.` | `CARD-character-officer-character-officer-014.png`; preserve `RT-013` and `SEM-Q-059`; no Command-target default. |
| `assets/tts-mod/extract/v2-dl/tree/cards/character/recon-007.png` | `Place 2 [secure].`<br>`OR`<br>`Discard 1 [actionCard]. Reinforce 1 empty Corridor that leads to a Room with a Character or [robot].` | `CARD-character-recon-character-recon-007.png`; separate occurrence. |
| `assets/tts-mod/extract/v2-dl/tree/cards/character/recon-019.png` | `Move the [intruder] by 1 space in any direction.`<br>`OR`<br>`COMMAND` `Choose a lower ranking [character] in your Room or neighbouring one. Make the chosen [character] Move, Shoot, or Burst. (you make all choices).`<br>`REACTION` `When a [character] with a higher Rank plays a Command on you: Cancel the effect of that Command. That [character] must still pay the Action's cost.` | `CARD-character-recon-character-recon-019.png`; preserve `RT-003`, `RT-013`, `SEM-Q-059`, `SEM-Q-060`, and `SEM-Q-074`. |
| `assets/tts-mod/extract/v2-dl/tree/cards/character/recon-043.png` | `title: SCOUTING`<br>`Move Cautiously to a Discovered Room.`<br>`OR`<br>`Move through an Unexplored Corridor for Exploration. Then, draw Items in your Room based on its icons. You may keep 1 of them and discard the rest.` | `CARD-character-recon-character-recon-043.png`; related generic records do not replace this exact combined occurrence; no icon/draw-shortage default. |
| `assets/tts-mod/extract/v2-dl/tree/cards/game/action/action-001.png` | `title: SEARCH`<br>`Draw 1 Item for each [ICON: white octagonal glyph] in your Room.`<br>`Keep 1 and discard the rest.` | `CARD-game-action-game-action-action-001.png`; preserve `SEM-Q-058`; unresolved octagon remains literal. |
| `assets/tts-mod/extract/v2-dl/tree/cards/game/action/action-002.png` | `Discard 1 [actionCard]. Place 2 [secure].`<br>`OR`<br>`Discard 1 [actionCard]. Reinforce 1 empty Corridor that leads to a Room with a Character or [robot].` | `CARD-game-action-game-action-action-002.png`; retain separate costs and OR structure. |
| `assets/tts-mod/extract/v2-dl/tree/cards/game/action/action-135.png` | `title: DEMOLITION`<br>`Destroy 1 accessible Door.`<br>`OR`<br>`Place a [malfunction] in your Room.` | `CARD-game-action-game-action-action-135.png`; preserve “accessible Door” and exact occurrence identity. |

Every row in this table satisfies the corresponding Action-card ID listed above; repeated titles are not merged. `RT-003` and `RT-013` remain the shared Reaction/Command cross-references for the three Chain of Command faces and the other printed Command faces, without resolving `SEM-Q-059`, `SEM-Q-060`, or `SEM-Q-074`.

## ACT-CARD-002 — Contamination deck identity and Action-cost restriction

- **Classification:** Source-backed rule record.
- **Source:** Rulebook PDF p. 3, “Standard-sized cards — Contamination cards”; Rulebook Contamination card face (extracted text lines ~352–360, “Can’t be discarded for Actions. You may discard this card when you Pass.”); Rulebook p. 14, “Passing.”
- **Deck identity and supply:** The base-game component inventory contains 27 Contamination cards. Although they share a common back with Action cards, the Contamination cards form a separate deck.
- **Plain rule:** A Contamination card in hand cannot be discarded to pay a Basic Action’s Action-card cost.
- **Exception:** When a player Passes, they may discard any number of Action **and** Contamination cards (see RT-007).
- **Invariant:** Contamination cards share a common card back with Action cards specifically so other players cannot tell them apart. A player’s own hand may distinguish them; another player’s view must show only total hand size.

## Examples

### EX-ACT-001 — Basic move with opportunity attacks

- **Given:** A Character has one Action card and an adjacent discovered Room through an open Corridor with one Adult Intruder.
- **When:** They Move.
- **Then:** Pay one card, resolve up to three applicable opportunity attacks, enter the Room, and make a Noise roll.

### EX-ACT-002 — Cautious move into a discovered Room

- **Given:** A Character Cautiously Moves into a discovered Room.
- **When:** Movement resolves.
- **Then:** Place one Secure token in that destination before the required Noise roll.

### EX-ACT-003 — Closed door blocks movement

- **Given:** A Character attempts to move through a Corridor with a Closed Door.
- **When:** No effect has opened or destroyed that Door.
- **Then:** The Move is illegal.

### EX-ACT-004 — Melee retaliation prevention

- **Given:** A Character’s melee target survives the attack.
- **When:** The Character does not malfunction one of their Weapons.
- **Then:** Resolve the target’s retaliatory Intruder Attack.

### EX-ACT-005 — Search and choose

- **Given:** A Room has three Item icons.
- **When:** Its occupant resolves Search.
- **Then:** Draw the corresponding three Items, optionally keep at most one, and return every unchosen card face-down to the bottom of its respective deck.

### EX-ACT-006 — Trade and immediate use

- **Given:** Characters A, B, and C share a Room.
- **When:** A spends an Action card to Trade and agrees.
- **Then:** B and C may exchange Items/Tactical Gear through A, including gifts; a received Ammo-related Item is considered gained and may be used immediately if otherwise legal.

### EX-ACT-007 — Noise roll resolves existing marker

- **Given:** A Character rolls 3, and two adjacent Corridors have value 3.
- **When:** One is empty and one contains Noise.
- **Then:** Place Noise in the empty Corridor and resolve the existing Noise marker in the other, in the specified per-Corridor order.

### EX-ACT-008 — Hazard attack cannot be prevented by movement prevention

- **Given:** The Character rolls Hazard during Movement.
- **When:** An Intruder is placed in their Room.
- **Then:** Resolve its immediate attack; a prevention limited to movement opportunity attacks does not prevent this Hazard attack.