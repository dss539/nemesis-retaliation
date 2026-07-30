# Foundations and Conventions

## FND-001 — Game-rule scope

- **Source:** Rulebook pp. 12–15, “Game Round Structure”; FAQ v1.2, “General rules.”
- **Plain rule:** This corpus describes the base-game rules as interpreted from the official rulebook and FAQ. Expansion, solo/co-op, and variant rules are out of scope unless a record says otherwise.
- **Authority:** Apply the precedence order in [README.md](README.md). The FAQ is a clarification/errata source, not a substitute for unaddressed rulebook text.

## FND-002 — Resolution language

- **Plain rule:** A rule procedure is resolved in the order written. Where the source directs a player to choose, the choice belongs to that player unless the source assigns it differently.
- **Tie-breaking:** When a rule calls for the Character first in turn order, begin with the current Starting Player and proceed clockwise.
- **Source:** Rulebook p. 13, “Turn order as tiebreaker” (extracted text lines 2995–3004).

## FND-003 — Impossible instructions

- **Plain rule:** If an Event-card sentence is impossible to resolve, ignore that sentence and continue with the remainder of that card.
- **Boundary:** This explicit partial-resolution rule is cited for Event cards. Do not generalize it to other actions without a source.
- **Source:** Rulebook p. 15, “Event card resolution” (extracted text lines 3269–3277).

## FND-004 — Official terms used in this corpus

- **Character:** an in-game player character.
- **Player:** the human participant controlling a Character.
- **Turn:** one player’s ordered opportunity to perform actions and resolve turn-end effects.
- **Round:** Player Phase, Intruder Phase, Event Phase, then Cleanup Phase.
- **Room / Corridor:** map spaces referred to by the rulebook. Their mandatory project geometry and relationship are defined by FND-005.
- **In Combat:** a Character is in a Room with at least one Intruder.
- **Source:** Rulebook pp. 12–13 (round/turn) and p. 13, “Not in Combat” (extracted text lines 2901–2906).

## FND-005 — Room geometry and Corridor spacing

- **Classification:** Project fidelity invariant from the established physical Facility-map and Room-tile interpretation, re-confirmed by the user. This is not an optional digital adaptation.
- **Plain rule:** Every Room and empty Room slot must be represented as a regular pointy-top hexagon. Rooms are never octagonal.
- **Six directions:** The only Room-edge directions are `NE`, `E`, `SE`, `SW`, `W`, and `NW`.
- **Corridor spacing:** Every Room slot preserves visible space beyond all six hex edges for possible Corridors, including edges where no Corridor currently exists. An absent Corridor leaves that reserved gap empty; it does not collapse neighboring Room geometry.
- **Uniform-gap derivation:** For a regular hexagon the centre-to-edge distance (apothem) is identical on all six edges and equals half the hexagon's across-flats width. Therefore a layout produces an equal Corridor gap on all six edges only when the centre-to-centre distance is the same for E/W neighbours and for the four diagonal neighbours. With an odd-row half-step offset, that holds when `row_step = col_step × √3 ⁄ 2`, and the resulting gap on every edge is `col_step − hex_width`. A layout that sets the row step to the naive `0.75 × hex_height` yields unequal gaps and is a geometry defect.
- **Corridor extent:** A Corridor occupies only the reserved gap between two adjacent Room edges. It begins at one Room's hex edge and ends at the neighbouring Room's hex edge, and must never be drawn spanning, crossing, or passing over intervening Room slots. A Corridor connects exactly two immediately adjacent Rooms.
- **Corridor gap budget:** The reserved gap is not decorative. It must remain large enough to legibly display, simultaneously: a Door token at the Corridor end against a Room, up to six Intruder-equivalents standing in the Corridor (see 03-intruders-and-survival.md, Corridor capacity), a Noise marker, and the Corridor's Noise/reinforced value. A gap sized only for a thin connector line cannot represent legal game state and is a fidelity defect.
- **Adjacency invariant:** Hex proximity alone never makes two Rooms adjacent. Characters move between neighboring Rooms only through a legal connecting Corridor. Room and Corridor topology remains authoritative over visual proximity.
- **Legal-target invariant:** A UI must not present off-board, unconnected, direction-mismatched, Closed-Door-blocked, or otherwise illegal destinations as Move choices. Exploration additionally requires an empty valid Room slot, so an occupied slot is not a legal Exploration destination. This does not prohibit an ordinary Move into a discovered Room merely because another Character or an Intruder occupies it. The authoritative rules engine must independently reject illegal targets.
- **Rendering invariant:** Room outlines, empty slots, status overlays, interaction hit regions, focus treatments, movement targets, and semantic-zoom representations must all preserve the same six-sided boundary. An octagonal or eight-direction representation is a rules-fidelity defect.
- **Official source boundary:** Rulebook p. 20, “Map” and “Rooms” (extracted text lines 3915–3921 and 4007–4015), establishes that the Facility consists of Rooms connected by adjacent Corridors. Rulebook p. 24, “Exploration Sequence” (extracted text lines 4501–4516), requires Corridors indicated by an Exploration card to be omitted when they would extend outside the Facility border or lead to an already placed Room. The regular pointy-top hexagon and six named directions normalize the physical component geometry as a documented project interpretation under the authority order in [README.md](README.md); they are not inferred from those extracted prose passages alone.
