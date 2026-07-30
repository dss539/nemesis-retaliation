# Character Actions

## Shared action framework

- On a player Turn, resolve in order: (1) exactly two Actions, (2) oxygen loss, (3) fire damage. A player may repeat an Action. If unable to perform another Action, they must Pass.
  - **Source:** Rulebook p. 12, “Players’ Turns” / “Resolving Actions” (extracted text lines 2854–2927).
- Pay a Basic Action’s cost by discarding that many Action cards face-up to the discard pile; do not resolve discarded cards’ effects. Pay first, then resolve the selected Action.
  - **Source:** Rulebook p. 12, “Cost in Action Cards” (extracted text lines 2935–2938).
- An effect or action may be selected only if it can be resolved entirely.
  - **Source:** Rulebook p. 14, “Effects” (extracted text lines 3187–3197).
- “Not in Combat” means the acting Character is not in a Room containing at least one Intruder. The extracted text does not reliably preserve which individual action icons carry this restriction; preserve each printed action/card’s icon as data.
  - **Source:** Rulebook p. 12, “Not in Combat” (extracted text lines 2901–2920).
- General local-effect default: an unspecified target is in the acting Character’s Room.
  - **Source:** Rulebook p. 17, “Golden Rules — Local Effects.”

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
- **FAQ:** An action that prevents an Intruder Attack “during a Movement” prevents opportunity attacks only, not a Hazard-result attack from the Noise roll.
  - **Source:** FAQ v1.2, “Action cards” #3 (lines 86–89).

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
  - Orient the drawn Exploration card to the map’s orientation.
- **Resolution order:**
  1. Draw an Exploration card.
  2. Set up Room: draw a random Room of the card’s required type (A, B, or C) and place it in the destination slot. If that type is exhausted, use a random ? Room.
  3. Set up Corridors: add each indicated Corridor unless it would go outside the Facility border or connect to an already placed Room. Orient a new Corridor’s Door slot toward the newly explored Room.
  4. Set up markers and tokens: place exactly the markers/tokens depicted, except do not add Noise to a Corridor that was not placed or already has Noise.
  5. Move Character: move the explorer into the new Room; if the originating movement was cautious, place one Secure token there.
  6. Entrance Effect: resolve it, commonly a Noise roll.
  7. Discard the Exploration card, unless it was removed from the game by its text.
- **FAQ:** “Close all Doors around this Room” affects only Doors touching the new Room, never Hibernatorium Doors; exploration does not resolve in the Hibernatorium.
  - **Source:** FAQ v1.2, “General rules” #4 (lines 30–35).
- **FAQ:** “Remove this card from the game” is not part of the Entrance Effect; an effect that explores while ignoring Entrance Effects still removes such a card.
  - **Source:** FAQ v1.2, “General rules” #5 (lines 37–40).

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
  - Select a working, loaded Ranged Weapon in a Hand.
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
- **Preconditions:** Choose an Intruder in the acting Character’s Room. A weapon is not required.
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
  2. Choose exactly one drawn Item to keep.
  3. Place every unchosen drawn Item on the bottom of its respective deck.
  4. Do not reveal searched-but-unchosen Items to other players.
- **Item placement restrictions:**
  - Regular Items enter the Backpack; Backpack capacity is unlimited and its contents remain secret until used.
  - Heavy Items require a Hand slot. If both Hands are occupied when gaining one, the Character may discard a held Item first to make room.
  - Only one Armor may be worn; a newly gained Armor may replace the current Armor.
  - **Source:** Rulebook pp. 28–29, “Backpack,” “Heavy Items,” “Armor Items.”

## ACT-ITEM-001 — Use Item

- **Cost:** 1 Action card.
- **Source:** Rulebook p. 12, “Basic Actions List” (line 2889); Rulebook p. 28, “Regular Items.”
- **Plain rule:** Resolve the effect of a regular Item (vertical, without Armor keyword). The Item is used and its effect resolves as printed.

## ACT-ROBOT-001 — Activate Robot

- **Cost:** 1 Action card.
- **Source:** Rulebook p. 12, “Basic Actions List” (line 2891); Rulebook p. 37, “Robot.”
- **Plain rule:** Activate the Robot per its printed rules. Detailed Robot rules to be transcribed from Rulebook p. 37.

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
- **Preconditions:** The Room must not contain an Intruder. Maximum three Secure tokens per Room.
- **Effect:** Place one Secure token in the acting Character’s Room.
- **FAQ:** Secure tokens prevent attacks from Intruders being placed in the Room (consuming one token per entry).
  - **Source:** FAQ v1.2, “General rules” #11 (lines 70–72).

## ACT-ROOM-001 — Use Room

- **Cost:** 2 Action cards.
- **Source:** Rulebook p. 12, “Basic Actions List” (line 2898); Rulebook pp. 20–23, “Rooms.”
- **Plain rule:** Resolve the Room effect printed on the Room tile or its Exploration card. Each Room has a specific effect described in the Room section of the rulebook.

## ACT-TACTICAL-001 — Use Tactical Gear

- **Cost:** 1 Action card.
- **Source:** Rulebook p. 12, “Basic Actions List” (line 2895); Rulebook p. 16, “Tactical Belt.”
- **Plain rule:** Use any Tactical Gear token. Multiple tokens may be used at once; the player chooses which token to use one by one.
- **FAQ:** Grenade Launcher grenades may be thrown from a malfunctioning Grenade Launcher with the Use Any Tactical Gear action.
  - **Source:** FAQ v1.2, “Items and tactical gear” #4 (lines 135–139).

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
- **Fire:** Closed Doors prevent fire spreading between the blocked Rooms.
  - **Source:** Rulebook p. 23, “Doors and Spreading Fire.”
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
- **FAQ:** “Resolve a Noise marker in each Unexplored Corridor” only resolves markers that already exist—it does not create them.
  - **Source:** FAQ v1.2, “General rules” #6 (lines 42–46).
- **Source:** Rulebook pp. 21–22, “Reinforced Corridor” / “Intruders and Noise Markers.”

## Actions not found in the base game

### Craft

- **Status:** No generic Craft action exists in the base-game Basic Actions list or rulebook.
- **Guidance:** Treat any crafting-like effect as a specific card/Room/expansion rule, not an assumed system.

### Rest

- **Status:** Only partially recoverable from the extracted text. The base Basic Actions list does not contain Rest as a basic action. The rulebook references the Rest Action card in connection with the Infection Procedure.
- **Source:** Rulebook p. 38, “Infection Procedure” (lines 6079–6098).
- **Reliable minimum:** If a valid Rest Action card instructs the player to resolve the Infection Procedure:
  1. Scan all Contamination cards in hand.
  2. For each card containing “INFECTED,” treat it as Infected; if the Character has no Larva, place one Larva on their Character board.
  3. Move all Contamination cards from hand to the top of the discard pile.
- **Open issue:** The complete printed Rest card should be visually inspected before formalizing its full effect, cost, or restrictions.

## ACT-CARD-001 — Action card identity and anatomy

- **Classification:** Source-backed rule record. Added from the rulebook’s Action-card anatomy passage and card images.
- **Source:** Rulebook p. 14, “Action cards” anatomy list A–E (extracted text lines 3161–3179); Rulebook p. 12, “Basic Actions List” (lines 2870–2900).
- **Plain rule:** An Action card is a distinct game object from a Basic Action. A Basic Action is a always-available option printed on the Character board and paid for by discarding Action cards. An Action card is a named, Character-specific card with its own printed effect, resolved only through the zero-cost `Play an Action card` Basic Action.
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
- **Confirmed card faces:** Only these base-box Action card faces are currently confirmed from official sources. All other faces are unverified and must not be invented:
  - **Sprint** (Recon) — “Move. Then, you may spend 1 to Move again.” Source: Rulebook Recon card image (extracted text lines ~332–338).
  - **Duck and Cover** (Contractor: Consultant) — “Discard 1 Action card to Move. During that Movement, Prevent 1 Intruder Attack.” Has a Reaction effect. Source: Rulebook pp. 14 and 13 card image (lines 3118–3127, 3190–3196).
- **Deck size:** Each Character has their own Action deck; the project currently models 10 cards per Character. The rulebook lists 60 Action cards as a component total (line 528). The per-Character composition of named faces is not established by the extracted text.
- **Open interpretation:** The full per-Character list of Action card faces, and each face’s printed cost/effect/Reaction/Not-In-Combat state, is not recoverable from the extracted rulebook text. Recorded as OQ-009.

## ACT-CARD-002 — Contamination cards cannot pay Action costs

- **Classification:** Source-backed rule record.
- **Source:** Rulebook Contamination card face (extracted text lines ~352–360, “Can’t be discarded for Actions. You may discard this card when you Pass.”); Rulebook p. 14, “Passing.”
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
- **Then:** Draw the corresponding three Items, keep one, and return the other two face-down to the bottoms of their respective decks.

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