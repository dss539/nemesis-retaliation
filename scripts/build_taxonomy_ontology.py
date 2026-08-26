#!/usr/bin/env python3
from __future__ import annotations

import argparse
import collections
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
VOCAB_DIR = REPO / 'docs/rules/vocabulary'
parser = argparse.ArgumentParser()
parser.add_argument('--output-dir', type=Path, default=REPO / 'docs/rules/ontology')
args = parser.parse_args()
OUT = args.output_dir.resolve()
OUT.mkdir(parents=True, exist_ok=True)


def load(name: str) -> dict:
    return json.loads((VOCAB_DIR / name).read_text(encoding='utf-8'))


def write(name: str, data: dict) -> None:
    (OUT / name).write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


vocabulary = load('canonical-vocabulary.json')
identities = load('named-component-identities.json')
aliases = load('alias-registry.json')
review = load('vocabulary-review-gates.json')
if review['counts']['open'] != 0:
    raise SystemExit('Vocabulary review gates must be closed before taxonomy/ontology generation')

term_by_label = {entry['canonicalLabel']: entry for entry in vocabulary['entries']}
term_ids = {entry['termId'] for entry in vocabulary['entries']}

nodes: list[dict] = []

def node(taxon_id: str, label: str, parents: list[str], kind: str, boundary: str, *, term_labels: list[str] | None = None, source: list[str] | None = None, disjoint: list[str] | None = None) -> None:
    evidence_terms = []
    for label_value in term_labels or []:
        if label_value not in term_by_label:
            raise KeyError(f'unknown vocabulary label for {taxon_id}: {label_value}')
        evidence_terms.append(term_by_label[label_value]['termId'])
    nodes.append({
        'taxonId': taxon_id,
        'label': label,
        'parentTaxonIds': sorted(set(parents)),
        'ontologicalKind': kind,
        'definitionBoundary': boundary,
        'evidenceTermIds': evidence_terms,
        'sourceEvidence': source or [],
        'disjointWithTaxonIds': sorted(set(disjoint or [])),
    })

# Root kinds.
node('tax.entity', 'Entity', [], 'class', 'A persistent game-world, information, component, or spatial object.', source=['docs/rules/00-foundations.md:FND-004'])
node('tax.process', 'Process type', [], 'process-type', 'A temporally extended game occurrence; this layer names process types but does not encode executable procedures.', source=['docs/rules/01-round-and-turns.md'])
node('tax.state', 'State or status', [], 'class', 'A condition that may hold for an entity or information object; transitions are not encoded here.', source=['docs/rules/02-character-actions.md:Doors', 'docs/rules/03-intruders-and-survival.md'])
node('tax.role', 'Contextual role', [], 'role', 'A role held by an entity in a context rather than an intrinsic entity class.', source=['docs/rules/01-round-and-turns.md:RT-002'])
node('tax.rule', 'Rule or mode concept', [], 'meta-rule', 'A game-mode or cross-cutting rule concept, not a physical component.', source=['docs/rules/00-foundations.md:FND-001'])
node('tax.value', 'Value kind', [], 'class', 'An enumerated or quantitative value used by static game structure.', source=['docs/rules/00-foundations.md:FND-004'])
node('tax.symbol', 'Printed symbol kind', [], 'symbol-kind', 'A printed icon/glyph result. It may denote another taxon but is not identical to its artwork.', source=['docs/rules/icon-glossary.md'])
node('tax.identity', 'Named source identity kind', [], 'identity-kind', 'A source-local named component, face, label, or structured key; exact name equality alone does not establish gameplay equivalence.', source=['docs/rules/vocabulary/named-component-identities.json'])
node('tax.scaffold', 'Semantic-model scaffold', [], 'schema-class', 'Static ontology scaffolding for later timing, decision, visibility, zone, and lifecycle semantics; no effect instances are encoded.', source=['docs/rules/00-foundations.md:FND-002'])

# Agents.
node('tax.entity.agent', 'Agent', ['tax.entity'], 'class', 'An entity capable of acting, being targeted, or occupying game space.', source=['docs/rules/00-foundations.md:FND-004'])
node('tax.entity.agent.participant', 'Participant agent', ['tax.entity.agent'], 'class', 'Human participant or their controlled Character.', source=['docs/rules/00-foundations.md:FND-004'])
node('tax.entity.agent.player', 'Player', ['tax.entity.agent.participant'], 'class', 'Human participant controlling a Character.', term_labels=['Player'])
node('tax.entity.agent.character', 'Character', ['tax.entity.agent.participant'], 'class', 'In-game Character controlled by a Player.', source=['docs/rules/00-foundations.md:FND-004'], disjoint=['tax.entity.agent.intruder'])
node('tax.entity.agent.robot', 'Robot', ['tax.entity.agent'], 'class', 'Robot model/entity activated under Robot rules.', source=['docs/rules/02-character-actions.md:ACT-ROBOT-001'])
node('tax.entity.agent.intruder', 'Intruder', ['tax.entity.agent'], 'class', 'Primeblood Intruder entity; Characters are not Intruders.', source=['docs/rules/00-foundations.md:FND-004', 'docs/rulebooks/Nemesis_RT_Rulebook_official.pdf:printed page 8'], disjoint=['tax.entity.agent.character'])
node('tax.entity.agent.intruder.queen', 'Queen', ['tax.entity.agent.intruder'], 'class', 'Queen Intruder type.', term_labels=['Queen'])
node('tax.entity.agent.intruder.drone', 'Drone', ['tax.entity.agent.intruder'], 'class', 'Drone Intruder type.', term_labels=['Drone'])
node('tax.entity.agent.intruder.adult', 'Adult', ['tax.entity.agent.intruder'], 'class', 'Adult Intruder type.', term_labels=['Adult'])
node('tax.entity.agent.intruder.larva', 'Larva', ['tax.entity.agent.intruder'], 'class', 'Larva Intruder type.', term_labels=['Larva'])

# Spatial entities.
node('tax.entity.spatial', 'Spatial entity', ['tax.entity'], 'class', 'A map, Facility, location, slot, or structural connector.', source=['docs/rules/00-foundations.md:FND-005'])
node('tax.entity.spatial.map', 'Map', ['tax.entity.spatial'], 'class', 'The spatial play surface showing the Facility.', term_labels=['Map'])
node('tax.entity.spatial.facility', 'Facility', ['tax.entity.spatial'], 'class', 'The base-game Facility divided into Sections A, B, and C.', term_labels=['Facility'], source=['docs/rulebooks/Nemesis_RT_Rulebook_official.pdf:printed page 20'])
node('tax.entity.spatial.section', 'Section', ['tax.entity.spatial'], 'class', 'One of the three Facility Sections.', term_labels=['Section'])
node('tax.entity.spatial.section.a', 'Section A', ['tax.entity.spatial.section'], 'identity-kind', 'The enumerated printed Section A identity, not a subclass inferred from name alone.', term_labels=['Section A'])
node('tax.entity.spatial.section.b', 'Section B', ['tax.entity.spatial.section'], 'identity-kind', 'The enumerated printed Section B identity, not a subclass inferred from name alone.', term_labels=['Section B'])
node('tax.entity.spatial.section.c', 'Section C', ['tax.entity.spatial.section'], 'identity-kind', 'The enumerated printed Section C identity, not a subclass inferred from name alone.', term_labels=['Section C'])
node('tax.entity.spatial.location', 'Location', ['tax.entity.spatial'], 'class', 'A location capable of containing game entities.', source=['docs/rulebooks/Nemesis_RT_Rulebook_official.pdf:printed page 20'])
node('tax.entity.spatial.room', 'Room', ['tax.entity.spatial.location'], 'class', 'A Facility Room. Characters may occupy Rooms, not Corridors.', term_labels=['Room'])
node('tax.entity.spatial.room-slot', 'Room slot', ['tax.entity.spatial.location'], 'class', 'A Facility-map slot that may be empty/Undiscovered or hold a placed Room.', source=['docs/rules/00-foundations.md:FND-005', 'docs/rules/02-character-actions.md:ACT-EXPLORE-001'])
node('tax.entity.spatial.corridor', 'Corridor', ['tax.entity.spatial.location'], 'class', 'A connector between two adjacent Room/Room-slot endpoints; Intruders but not Characters may occupy it.', term_labels=['Corridor'])
node('tax.entity.spatial.door', 'Door', ['tax.entity.spatial'], 'class', 'A Door at a Corridor end against a Room.', term_labels=['Door'], source=['docs/rules/02-character-actions.md:Doors'])
node('tax.entity.spatial.room.nest', 'Nest Room identity', ['tax.entity.spatial.room'], 'identity-kind', 'The named Nest Room identity, not a general Room subclass.', term_labels=['Nest'])
node('tax.entity.spatial.room.hibernatorium', 'Hibernatorium Room identity', ['tax.entity.spatial.room'], 'identity-kind', 'The named Hibernatorium Room identity, not a general Room subclass.', term_labels=['Hibernatorium'])
node('tax.entity.spatial.room.landing-zone', 'Landing Zone Room identity', ['tax.entity.spatial.room'], 'identity-kind', 'The named Landing Zone Room identity, not a general Room subclass.', term_labels=['Landing Zone'])
node('tax.entity.spatial.room.escape-shuttle', 'Escape Shuttle Room identity', ['tax.entity.spatial.room'], 'identity-kind', 'The named Escape Shuttle Room identity, not a general Room subclass.', term_labels=['Escape Shuttle'])
node('tax.entity.spatial.room.reactor', 'Reactor Room identity', ['tax.entity.spatial.room'], 'identity-kind', 'The named Reactor Room identity, not a general Room subclass.', term_labels=['Reactor'])

# Components and information objects.
node('tax.entity.component', 'Component copy/runtime entity', ['tax.entity'], 'class', 'A physical component copy or runtime entity in one game, distinct from its definition and source occurrence.', source=['docs/rulebooks/Nemesis_RT_Rulebook_official.pdf:component list'])
node('tax.entity.component-set', 'Component set or supply', ['tax.entity'], 'class', 'A deck, pile, pool, insert, or finite set from which component copies are supplied.', source=['docs/rulebooks/Nemesis_RT_Rulebook_official.pdf:component list'])
node('tax.entity.component.card', 'Card', ['tax.entity.component'], 'class', 'A printed card component.', source=['docs/rulebooks/rulebook_text.txt:component list'])
node('tax.entity.component.card.action', 'Action card', ['tax.entity.component.card'], 'class', 'Character-specific Action card, distinct from a Basic Action.', source=['docs/rules/02-character-actions.md:ACT-CARD-001'])
node('tax.entity.component.card.contamination', 'Contamination card', ['tax.entity.component.card'], 'class', 'Contamination card sharing a back with Action cards but forming a separate deck.', term_labels=['Contamination card'])
node('tax.entity.component.card.event', 'Event card', ['tax.entity.component.card'], 'class', 'Event card resolved in Event Phase.', term_labels=['Event card'])
node('tax.entity.component.card.exploration', 'Exploration card', ['tax.entity.component.card'], 'class', 'Exploration card used in Exploration Sequence.', term_labels=['Exploration card'])
node('tax.entity.component.card.intruder-attack', 'Intruder Attack card', ['tax.entity.component.card'], 'class', 'Card containing effects by Intruder type.', term_labels=['Intruder Attack card'])
node('tax.entity.component.card.queen-health', 'Queen Health card', ['tax.entity.component.card'], 'class', 'Card in the Queen Health deck.', term_labels=['Queen Health card'])
node('tax.entity.component.card.serious-wound', 'Serious Wound card', ['tax.entity.component.card'], 'class', 'Persistent Serious Wound card.', term_labels=['Serious Wound card'])
node('tax.entity.component.card.robot', 'Robot card', ['tax.entity.component.card'], 'class', 'Card determining Robot rules/identity.', term_labels=['Robot card'])
node('tax.entity.component.card.mission-task', 'Mission Task card', ['tax.entity.component.card'], 'class', 'Card carrying a Mission Task.', term_labels=['Mission Task card'])
node('tax.entity.component.card.objective', 'Objective card', ['tax.entity.component.card'], 'class', 'Card carrying an Objective.', term_labels=['Objective card'])
node('tax.entity.component.card.objective.solo-coop', 'Solo/Coop Objective card', ['tax.entity.component.card.objective'], 'class', 'Objective card scoped to Solo/Coop rules.', term_labels=['Solo/Coop Objective card'])
node('tax.entity.component.card.character-draft', 'Character Draft card', ['tax.entity.component.card'], 'class', 'Card used in Character Draft.', term_labels=['Character Draft card'])
node('tax.entity.component.card.help', 'Help card', ['tax.entity.component.card'], 'class', 'Numbered Player Help card/reference component.', term_labels=['Help card'])

node('tax.entity.information', 'Information object', ['tax.entity'], 'class', 'Rules-bearing information that can be printed on a component.', source=['docs/rules/01-round-and-turns.md:RT-010'])
node('tax.entity.information.component-definition', 'Component definition', ['tax.entity.information'], 'class', 'Rules-bearing definition shared by one or more component copies; distinct from a source occurrence and runtime copy.', source=['docs/rules/source-extraction/README.md'])
node('tax.entity.information.component-definition.room', 'Room definition', ['tax.entity.information.component-definition'], 'class', 'Definition of a named Room effect/metadata entry.', source=['docs/rules/source-extraction/room-help-sheet.json'])
node('tax.entity.information.component-definition.card-face', 'Card-face definition', ['tax.entity.information.component-definition'], 'class', 'Definition of one scoped card face/version.', source=['assets/tts-mod/extract/card-text-corpus.json'])
node('tax.entity.information.component-definition.component-set', 'Component-set definition', ['tax.entity.information.component-definition'], 'class', 'Definition/inventory of a deck, pile, pool, or component set.', source=['docs/rulebooks/Nemesis_RT_Rulebook_official.pdf:component list'])
node('tax.entity.information.objective', 'Objective', ['tax.entity.information'], 'class', 'Endgame condition retained by a player.', term_labels=['Objective'])
node('tax.entity.information.objective.private', 'Private Objective', ['tax.entity.information.objective'], 'class', 'Private Objective information type.', term_labels=['Private Objective'])
node('tax.entity.information.objective.mission', 'Mission Objective', ['tax.entity.information.objective'], 'class', 'Mission Objective information type.', term_labels=['Mission Objective'])
node('tax.entity.information.mission-task', 'Mission Task', ['tax.entity.information'], 'class', 'Mission Task referenced by Mission Objectives; not itself an Objective subtype.', term_labels=['Mission Task'])

# Item cards can overlap by physical class, source family, and function; these are not declared disjoint.
node('tax.entity.component.card.item', 'Item card', ['tax.entity.component.card'], 'class', 'Card representing an Item.', term_labels=['Item'], source=['docs/rules/04-items-and-equipment.md:ITM-001'])
node('tax.entity.component.card.item.regular', 'Regular Item', ['tax.entity.component.card.item'], 'class', 'Vertical Backpack Item card without Armor keyword.', term_labels=['Regular Item'])
node('tax.entity.component.card.item.heavy', 'Heavy Item', ['tax.entity.component.card.item'], 'class', 'Horizontal Item card held in a Hand slot.', term_labels=['Heavy Item'])
node('tax.entity.component.card.item.armor', 'Armor Item', ['tax.entity.component.card.item'], 'class', 'Item card carrying the Armor keyword and worn on the Health track.', term_labels=['Armor Item'])
node('tax.entity.component.card.item.character', 'Character Item', ['tax.entity.component.card.item'], 'class', 'Per-character starting equipment source family.', term_labels=['Character Item'])
node('tax.entity.component.card.item.support', 'Support Equipment', ['tax.entity.component.card.item'], 'class', 'Support Equipment source family.', term_labels=['Support Equipment'])
node('tax.entity.component.card.item.weapon', 'Weapon', ['tax.entity.component.card.item.heavy'], 'class', 'Weapon Item; functional category that may overlap source families.', term_labels=['Weapon'])
node('tax.entity.component.card.item.weapon.ranged', 'Ranged Weapon', ['tax.entity.component.card.item.weapon'], 'class', 'Weapon usable for Shoot/Burst when otherwise legal.', term_labels=['Ranged Weapon'])
node('tax.entity.component.card.item.weapon.melee', 'Melee Weapon', ['tax.entity.component.card.item.weapon'], 'class', 'Melee Weapon functional category.', term_labels=['Melee Weapon'])

node('tax.entity.component.token', 'Token', ['tax.entity.component'], 'class', 'Physical token component.', source=['docs/rulebooks/rulebook_text.txt:component list'])
node('tax.entity.component.token.data', 'Data token', ['tax.entity.component.token'], 'class', 'Data token.', term_labels=['Data token'])
node('tax.entity.component.token.egg', 'Egg token', ['tax.entity.component.token'], 'class', 'Egg token.', term_labels=['Egg token'])
node('tax.entity.component.token.tactical-gear', 'Tactical Gear token', ['tax.entity.component.token'], 'class', 'Consumable Ammo, Grenade, Oxygen, or Medpack token.', term_labels=['Tactical Gear token'])
node('tax.entity.component.token.tactical-gear.ammo', 'Ammo Tactical Gear token', ['tax.entity.component.token.tactical-gear'], 'class', 'Ammo token.', source=['docs/rules/04-items-and-equipment.md:ITM-005'])
node('tax.entity.component.token.tactical-gear.grenade', 'Grenade Tactical Gear token', ['tax.entity.component.token.tactical-gear'], 'class', 'Grenade token.', source=['docs/rules/04-items-and-equipment.md:ITM-005'])
node('tax.entity.component.token.tactical-gear.oxygen', 'Oxygen Tactical Gear token', ['tax.entity.component.token.tactical-gear'], 'class', 'Oxygen token.', source=['docs/rules/04-items-and-equipment.md:ITM-005'])
node('tax.entity.component.token.tactical-gear.medpack', 'Medpack Tactical Gear token', ['tax.entity.component.token.tactical-gear'], 'class', 'Medpack token.', source=['docs/rules/04-items-and-equipment.md:ITM-005'])
node('tax.entity.component.token.round', 'Round marker', ['tax.entity.component.token'], 'class', 'Round marker on Round track.', term_labels=['Round marker'])
node('tax.entity.component.token.starting-player', 'Starting Player token', ['tax.entity.component.token'], 'class', 'Token identifying the Starting Player.', term_labels=['Starting Player token'])
node('tax.entity.component.token.suffocating', 'Suffocating token', ['tax.entity.component.token'], 'class', 'Suffocating status token.', term_labels=['Suffocating token'])
node('tax.entity.component.token.anti-aircraft', 'Anti-Aircraft token', ['tax.entity.component.token'], 'class', 'Anti-Aircraft status/order token.', term_labels=['Anti-Aircraft token'])
node('tax.entity.component.token.lander', 'Lander token', ['tax.entity.component.token'], 'class', 'Lander token on the Round track/map.', source=['docs/rules/01-round-and-turns.md:RT-012a'])
node('tax.entity.component.token.autodestruction', 'Autodestruction token', ['tax.entity.component.token'], 'class', 'Autodestruction token on the Round track.', source=['docs/rules/03-intruders-and-survival.md:INT-010'])
node('tax.entity.component.marker', 'Marker', ['tax.entity.component'], 'class', 'Marker component representing Hits, Fire, Malfunction, Noise, or similar state.', source=['docs/rulebooks/rulebook_text.txt:component list'])
node('tax.entity.component.marker.universal', 'Universal marker', ['tax.entity.component.marker'], 'class', 'General-purpose Universal marker.', term_labels=['Universal marker'])
node('tax.entity.component.marker.fire', 'Fire marker', ['tax.entity.component.marker'], 'class', 'Fire marker.', source=['docs/rules/01-round-and-turns.md:RT-008'])
node('tax.entity.component.marker.malfunction', 'Malfunction marker', ['tax.entity.component.marker'], 'class', 'Malfunction marker.', source=['docs/rules/02-character-actions.md'])
node('tax.entity.component.marker.noise', 'Noise marker', ['tax.entity.component.marker'], 'class', 'Noise marker placed in Corridors.', source=['docs/rules/02-character-actions.md:Noise'])
node('tax.entity.component.token.secure', 'Secure token', ['tax.entity.component.token'], 'class', 'Secure token placed in Rooms.', source=['docs/rules/02-character-actions.md:ACT-SECURE-001'])
node('tax.entity.component.slot', 'Component slot', ['tax.entity.component'], 'class', 'A printed slot that may hold a compatible component.', source=['docs/rules/04-items-and-equipment.md:ITM-005'])
node('tax.entity.component.slot.tactical-gear', 'Tactical Gear Slot', ['tax.entity.component.slot'], 'class', 'Slot accepting Tactical Gear tokens by type or Any.', term_labels=['Tactical Gear Slot'])
node('tax.entity.component.slot.hand', 'Hand Slot', ['tax.entity.component.slot'], 'class', 'Character Hand slot for Heavy Items.', term_labels=['Hand Slot'])
node('tax.entity.component.storage', 'Storage area', ['tax.entity.component'], 'class', 'Board/card-holder area that stores components or cards.', source=['docs/rules/02-character-actions.md:ACT-SEARCH-001'])
node('tax.entity.component.storage.backpack', 'Backpack', ['tax.entity.component.storage'], 'class', 'Secret unlimited storage for Regular Items.', term_labels=['Backpack'])
node('tax.entity.component.storage.tactical-belt', 'Tactical Belt', ['tax.entity.component.storage'], 'class', 'Four Any Tactical Gear slots on a Character board.', term_labels=['Tactical Belt'])

# Processes.
node('tax.process.temporal', 'Temporal structure', ['tax.process'], 'process-type', 'Round/Phase/Turn structural process.', source=['docs/rules/01-round-and-turns.md:RT-001'])
node('tax.process.temporal.round', 'Round', ['tax.process.temporal'], 'process-type', 'One ordered Player, Intruder, Event, and Cleanup phase cycle.', term_labels=['Round'])
node('tax.process.temporal.phase', 'Phase', ['tax.process.temporal'], 'process-type', 'Named Round phase.', source=['docs/rules/01-round-and-turns.md:RT-001'])
node('tax.process.temporal.phase.player', 'Player Phase', ['tax.process.temporal.phase'], 'process-type', 'Player Phase.', term_labels=['Player Phase'])
node('tax.process.temporal.phase.intruder', 'Intruder Phase', ['tax.process.temporal.phase'], 'process-type', 'Intruder Phase.', term_labels=['Intruder Phase'])
node('tax.process.temporal.phase.event', 'Event Phase', ['tax.process.temporal.phase'], 'process-type', 'Event Phase.', term_labels=['Event Phase'])
node('tax.process.temporal.phase.cleanup', 'Cleanup Phase', ['tax.process.temporal.phase'], 'process-type', 'Cleanup Phase.', term_labels=['Cleanup Phase'])
node('tax.process.temporal.turn', 'Turn', ['tax.process.temporal'], 'process-type', 'Player Turn during Player Phase.', term_labels=['Turn'])
node('tax.process.action', 'Action', ['tax.process'], 'process-type', 'Action process performed under Action timing/cost rules.', term_labels=['Action'])
node('tax.process.action.basic', 'Basic Action', ['tax.process.action'], 'process-type', 'Always-available option distinct from an Action card.', term_labels=['Basic Action'])
node('tax.process.card-effect', 'Card/effect process', ['tax.process'], 'process-type', 'Process invoked by printed card/effect text; it is not automatically an Action.', source=['docs/rules/02-character-actions.md:ACT-CARD-001'])
node('tax.process.card-effect.reaction', 'Reaction', ['tax.process.card-effect'], 'process-type', 'Reaction process; the rulebook explicitly says it is not an Action.', term_labels=['Reaction'])
node('tax.process.card-effect.command', 'Command', ['tax.process.card-effect'], 'process-type', 'Ordering process granted by an effect; the commanded Character may perform an Action.', term_labels=['Command'])
node('tax.process.action.pass', 'Pass', ['tax.process.action'], 'process-type', 'Pass Action ending participation in later Player-Phase rotations.', term_labels=['Pass'])
node('tax.process.action.move', 'Move', ['tax.process.action'], 'process-type', 'Movement Action.', term_labels=['Move'])
node('tax.process.action.make-a-move', 'Make a Move', ['tax.process.action.move'], 'process-type', 'Printed Make a Move Action label.', term_labels=['Make a Move'])
node('tax.process.action.move-cautiously', 'Moving Cautiously', ['tax.process.action.move'], 'process-type', 'Cautious movement variant.', term_labels=['Moving Cautiously'])
node('tax.process.attack', 'Attack', ['tax.process'], 'process-type', 'Generic attack process family; not every Attack is a player Action.', term_labels=['Attack'])
node('tax.process.attack.opportunity', 'Opportunity Attack', ['tax.process.attack'], 'process-type', 'Attack triggered during Movement before relocation; not a selected Action.', term_labels=['Opportunity Attack'])
node('tax.process.action.attack.shoot', 'Shoot', ['tax.process.action', 'tax.process.attack'], 'process-type', 'Shoot is both a player Action type and an attack process.', term_labels=['Shoot'])
node('tax.process.action.attack.burst', 'Burst', ['tax.process.action', 'tax.process.attack'], 'process-type', 'Burst is both a player Action type and an attack process.', term_labels=['Burst'])
node('tax.process.action.attack.melee', 'Melee Attack', ['tax.process.action', 'tax.process.attack'], 'process-type', 'Melee Attack is both a player Action type and an attack process.', term_labels=['Melee Attack'])
node('tax.process.operation.repel', 'Repel', ['tax.process.operation'], 'process-type', 'Movement operation produced by a source effect, not a universal Basic Action.', term_labels=['Repel'])
node('tax.process.card-effect.search', 'Search', ['tax.process.card-effect'], 'process-type', 'Search is an Action-card effect resolved through Play an Action card, not a universal Basic Action.', term_labels=['Search'])
node('tax.process.action.use-room', 'Use the Room', ['tax.process.action'], 'process-type', 'Use Room Action.', term_labels=['Use the Room'])
node('tax.process.action.trade', 'Trade', ['tax.process.action'], 'process-type', 'Trade Action.', term_labels=['Trade'])
node('tax.process.action.use-tactical-gear', 'Use Any Tactical Gear Action', ['tax.process.action'], 'process-type', 'Tactical Gear Action.', term_labels=['Use Any Tactical Gear Action'])
node('tax.process.sequence', 'Resolution sequence', ['tax.process'], 'process-type', 'Named ordered resolution sequence; individual steps are deferred to semantic modeling.', source=['docs/rules/02-character-actions.md'])
node('tax.process.sequence.movement', 'Movement Sequence', ['tax.process.sequence'], 'process-type', 'Movement Sequence.', term_labels=['Movement Sequence'])
node('tax.process.sequence.exploration', 'Exploration Sequence', ['tax.process.sequence'], 'process-type', 'Exploration Sequence.', term_labels=['Exploration Sequence'])
node('tax.process.sequence.noise-roll', 'Noise Roll', ['tax.process.sequence'], 'process-type', 'Noise Roll resolution.', term_labels=['Noise Roll'])
node('tax.process.operation', 'Resolution operation', ['tax.process'], 'process-type', 'Primitive operation label used by rules; its executable semantics are deferred.', source=['docs/rules/02-character-actions.md'])
node('tax.process.operation.hit', 'Hit', ['tax.process.operation'], 'process-type', 'Deal/record a Hit.', term_labels=['Hit'])
node('tax.process.operation.draw', 'Draw', ['tax.process.operation'], 'process-type', 'Draw a card/token/component from a source.', term_labels=['Draw'])
node('tax.process.operation.discard', 'Discard', ['tax.process.operation'], 'process-type', 'Move a component to a discard destination or source-defined discard location.', term_labels=['Discard'])
node('tax.process.procedure', 'Procedure', ['tax.process'], 'process-type', 'Named rules procedure.', source=['docs/rules/03-intruders-and-survival.md'])
node('tax.process.procedure.infection', 'Infection Procedure', ['tax.process.procedure'], 'process-type', 'Infection Procedure.', term_labels=['Infection Procedure'])
node('tax.process.procedure.eclosion', 'Eclosion Procedure', ['tax.process.procedure'], 'process-type', 'Eclosion Procedure.', term_labels=['Eclosion Procedure'])
node('tax.process.procedure.autodestruction', 'Autodestruction Procedure', ['tax.process.procedure'], 'process-type', 'Autodestruction Procedure.', term_labels=['Autodestruction Procedure'])
node('tax.process.procedure.endgame', 'End of the Game', ['tax.process.procedure'], 'process-type', 'End-of-game sequence.', term_labels=['End of the Game'])
node('tax.process.procedure.escape', 'Escape', ['tax.process.procedure'], 'process-type', 'Escape process/status transition.', term_labels=['Escape'])
node('tax.process.procedure.hibernate', 'Hibernate', ['tax.process.procedure'], 'process-type', 'Hibernation process/status transition.', term_labels=['Hibernate'])

# States and roles.
node('tax.state.health', 'Health state', ['tax.state'], 'class', 'Character health/status condition.', term_labels=['Character Health'])
node('tax.state.health.point', 'Health Point value', ['tax.value'], 'class', 'Quantified Character Health point.', term_labels=['Health Point'])
node('tax.state.health.healthy', 'Healthy', ['tax.state.health'], 'state-value', 'Healthy Character state.', term_labels=['Healthy'])
node('tax.state.health.injured', 'Injured', ['tax.state.health'], 'state-value', 'Injured Character state.', term_labels=['Injured'])
node('tax.state.health.heavily-injured', 'Heavily Injured', ['tax.state.health'], 'state-value', 'Heavily Injured Character state.', term_labels=['Heavily Injured'])
node('tax.state.infection', 'Infection-related state', ['tax.state'], 'class', 'Infection/Contamination state family.', source=['docs/rules/03-intruders-and-survival.md:INT-008'])
node('tax.state.infection.infected', 'Infected', ['tax.state.infection'], 'state-value', 'Infected state determined by scanning.', term_labels=['Infected'])
node('tax.state.infection.contamination', 'Contamination', ['tax.state.infection'], 'class', 'Contamination condition/concept, distinct from a Contamination card component.', term_labels=['Contamination'])
node('tax.state.discovery', 'Discovery state', ['tax.state'], 'class', 'Discovered/Undiscovered spatial state.', source=['docs/rules/02-character-actions.md:ACT-EXPLORE-001'])
node('tax.state.discovery.discovered', 'Discovered', ['tax.state.discovery'], 'state-value', 'Discovered state.', term_labels=['Discovered'])
node('tax.state.discovery.undiscovered', 'Undiscovered', ['tax.state.discovery'], 'state-value', 'Undiscovered state.', term_labels=['Undiscovered'])
node('tax.state.door', 'Door state', ['tax.state'], 'class', 'Opened/Closed/Destroyed Door state.', source=['docs/rules/02-character-actions.md:Doors'])
node('tax.state.opened', 'Opened', ['tax.state'], 'state-value', 'Opened state; typically applied to Doors.', term_labels=['Opened'])
node('tax.state.closed', 'Closed', ['tax.state'], 'state-value', 'Closed state; typically applied to Doors.', term_labels=['Closed'])
node('tax.state.destroyed', 'Destroyed', ['tax.state'], 'state-value', 'Destroyed state applicable to Doors, Rooms, Nest, or Facility where sources say so.', term_labels=['Destroyed'])
node('tax.state.corridor', 'Corridor status', ['tax.state'], 'class', 'Corridor Empty/Unexplored/Reinforced status dimension.', source=['docs/rules/02-character-actions.md'])
node('tax.state.corridor.reinforced', 'Reinforced Corridor', ['tax.state.corridor'], 'state-value', 'Corridor reinforced status/value 0.', term_labels=['Reinforced Corridor'])
node('tax.state.corridor.empty', 'Empty Corridor', ['tax.state.corridor'], 'state-value', 'Corridor containing no Intruders; a Corridor with a Noise marker is still Empty.', term_labels=['Empty Corridor'], source=['docs/rulebooks/rulebook_text.txt:lines 4159–4161'])
node('tax.state.corridor.unexplored', 'Unexplored Corridor', ['tax.state.corridor'], 'state-value', 'Corridor connected with only one placed Room.', term_labels=['Unexplored Corridor'], source=['docs/rulebooks/rulebook_text.txt:lines 4162–4163'])
node('tax.state.objective', 'Objective status', ['tax.state'], 'class', 'Objective fulfillment state.', source=['docs/rules/03-intruders-and-survival.md:INT-011'])
node('tax.state.objective.fulfilled', 'Fulfilled', ['tax.state.objective'], 'state-value', 'Objective/Mission Task fulfilled state.', term_labels=['Fulfilled'])
node('tax.state.participation', 'Participation/endgame state', ['tax.state'], 'class', 'Character participation/survival state family.', source=['docs/rules/01-round-and-turns.md:RT-014','docs/rules/03-intruders-and-survival.md:INT-011'])
node('tax.state.participation.survivor', 'Survivor', ['tax.state.participation'], 'state-value', 'Character satisfies the Objective Help definition of Survivor.', term_labels=['Survivor'])
node('tax.state.participation.escaped', 'Escaped', ['tax.state.participation'], 'state-value', 'Character has Escaped according to Objective Help/endgame rules.', source=['docs/rules/03-intruders-and-survival.md:INT-009'])
node('tax.state.participation.hibernated', 'Hibernated', ['tax.state.participation'], 'state-value', 'Character has successfully Hibernated.', source=['docs/rules/03-intruders-and-survival.md:INT-009'])
node('tax.state.combat', 'Combat status', ['tax.state'], 'class', 'Character combat condition derived from sharing a Room with an Intruder.', source=['docs/rules/00-foundations.md:FND-004'])
node('tax.state.combat.not-in-combat', 'Not In Combat', ['tax.state.combat'], 'state-value', 'Restriction/status meaning the Character is not in a Room with an Intruder.', source=['docs/rules/02-character-actions.md'])
node('tax.state.activation', 'Activation state', ['tax.state'], 'class', 'Active/Inactive state for Life Support or Hibernatorium components.', source=['docs/rulebooks/rulebook_text.txt:setup'])
node('tax.state.activation.active', 'Active', ['tax.state.activation'], 'state-value', 'Active face/state.', source=['docs/rulebooks/rulebook_text.txt:setup'])
node('tax.state.activation.inactive', 'Inactive', ['tax.state.activation'], 'state-value', 'Inactive face/state.', source=['docs/rulebooks/rulebook_text.txt:setup'])
node('tax.role.starting-player', 'Starting Player', ['tax.role'], 'role', 'Player holding the Starting Player token.', term_labels=['Starting Player'])
node('tax.role.character', 'Character role/identity', ['tax.role'], 'role', 'Named Character role to which Action cards/decks and Character Items may belong.', source=['docs/rulebooks/rulebook_text.txt:Character setup'])

node('tax.value.turn-order', 'Turn Order', ['tax.value'], 'class', 'Clockwise ordering beginning at Starting Player.', term_labels=['Turn Order'])
node('tax.value.orientation', 'Corridor orientation value', ['tax.value'], 'class', 'E–W, NE–SW, or NW–SE printed Corridor orientation.', source=['docs/rules/00-foundations.md:FND-005'])
node('tax.value.resource', 'Resource value', ['tax.value'], 'class', 'Quantified resource such as Oxygen or Character Health.', source=['docs/rules/04-items-and-equipment.md'])
node('tax.value.resource.oxygen', 'Oxygen value', ['tax.value.resource'], 'class', 'Character Oxygen counter/resource value.', source=['docs/rules/01-round-and-turns.md:RT-005'])

# Modes/meta-rules.
node('tax.rule.mode', 'Game mode', ['tax.rule'], 'meta-rule', 'Rule-set mode or variant.', source=['docs/rules/00-foundations.md:FND-001'])
node('tax.rule.mode.deadly', 'Deadly Mode', ['tax.rule.mode'], 'meta-rule', 'Deadly Mode variant.', term_labels=['Deadly Mode'])
node('tax.rule.mode.solo-coop', 'Solo and Coop Rules', ['tax.rule.mode'], 'meta-rule', 'Solo/Coop rules mode.', term_labels=['Solo and Coop Rules'])
node('tax.rule.constraint', 'Cross-cutting rule constraint', ['tax.rule'], 'meta-rule', 'Rule constraint applied across components/effects.', source=['docs/rules/00-foundations.md'])
node('tax.rule.constraint.component-limits', 'Component Limits', ['tax.rule.constraint'], 'meta-rule', 'Finite physical component limits.', term_labels=['Component Limits'])
node('tax.rule.constraint.nightmare', 'Nightmare Rule', ['tax.rule.constraint'], 'meta-rule', 'Nightmare Rule.', term_labels=['Nightmare Rule'])
node('tax.rule.constraint.local-effects', 'Local Effects', ['tax.rule.constraint'], 'meta-rule', 'Default local-target rule.', term_labels=['Local Effects'])
node('tax.rule.constraint.interplay', 'Interplay', ['tax.rule.constraint'], 'meta-rule', 'Consent/direct-use interaction rule.', term_labels=['Interplay'])

# Symbols.
node('tax.symbol.die-result', 'Die-result symbol', ['tax.symbol'], 'symbol-kind', 'Printed Shoot/Burst/Noise die result identifier.', source=['docs/rules/icon-glossary.md'])
node('tax.symbol.item-icon', 'Item Icon', ['tax.symbol'], 'symbol-kind', 'Red/Yellow/Green Item search icon.', source=['docs/rules/04-items-and-equipment.md:ITM-006'])
node('tax.symbol.room-feature', 'Room-feature symbol', ['tax.symbol'], 'symbol-kind', 'Room feature such as Computer.', source=['docs/rules/icon-glossary.md'])
node('tax.symbol.component-reference', 'Component-reference symbol', ['tax.symbol'], 'symbol-kind', 'Printed icon denoting a component/token/slot.', source=['docs/rules/icon-glossary.md'])
node('tax.symbol.entity-reference', 'Entity-reference symbol', ['tax.symbol'], 'symbol-kind', 'Printed icon denoting Character, Robot, or Intruder.', source=['docs/rules/icon-glossary.md'])
node('tax.symbol.state-reference', 'State-reference symbol', ['tax.symbol'], 'symbol-kind', 'Printed icon denoting a state/restriction.', source=['docs/rules/icon-glossary.md'])
node('tax.symbol.orientation', 'Orientation symbol', ['tax.symbol'], 'symbol-kind', 'Printed Corridor orientation icon.', source=['docs/rules/icon-glossary.md'])
node('tax.symbol.metadata', 'Metadata symbol', ['tax.symbol'], 'symbol-kind', 'Printed metadata symbol such as Number of Characters.', source=['docs/rules/icon-glossary.md'])

# Static semantic scaffolding for the next layer.
node('tax.scaffold.zone', 'Zone', ['tax.scaffold'], 'schema-class', 'Named storage/location zone for components; zone transitions are deferred.', source=['docs/rules/01-round-and-turns.md', 'docs/rules/02-character-actions.md'])
for suffix, label, source_ref in [
    ('deck','Deck','docs/rules/01-round-and-turns.md:RT-012'),('discard-pile','Discard pile','docs/rules/01-round-and-turns.md:RT-012'),('hand','Hand','docs/rules/01-round-and-turns.md:RT-006'),('backpack','Backpack zone','docs/rules/02-character-actions.md:ACT-SEARCH-001'),('character-board','Character board zone','docs/rules/03-intruders-and-survival.md:INT-008'),('removed-from-game','Removed-from-game zone','docs/rules/01-round-and-turns.md:RT-010'),('intruder-bag','Intruder bag','docs/rules/03-intruders-and-survival.md:INT-001'),('token-pile','Token pile','docs/rules/03-intruders-and-survival.md:INT-001')]:
    node(f'tax.scaffold.zone.{suffix}', label, ['tax.scaffold.zone'], 'schema-class', f'{label} static zone class.', source=[source_ref])
node('tax.scaffold.timing-window', 'Timing window', ['tax.scaffold'], 'schema-class', 'Named point/interval in Round, Phase, Turn, Action, or Procedure; specific effect timing is deferred.', source=['docs/rules/01-round-and-turns.md'])
node('tax.scaffold.decision', 'Decision', ['tax.scaffold'], 'schema-class', 'Actor-owned choice; specific options and legality are deferred.', source=['docs/rules/00-foundations.md:FND-002'])
node('tax.scaffold.audience-scope', 'Audience scope', ['tax.scaffold'], 'schema-class', 'Public/private/temporary visibility category; specific information policies are deferred.', source=['docs/rules/02-character-actions.md:ACT-SEARCH-001', 'docs/rules/02-character-actions.md:ACT-CARD-002'])
node('tax.scaffold.lifecycle-transition', 'Lifecycle transition', ['tax.scaffold'], 'schema-class', 'Transition between states/zones; trigger and procedure semantics are deferred.', source=['docs/rules/01-round-and-turns.md:RT-014'])
node('tax.scaffold.supply-pool', 'Finite supply pool', ['tax.scaffold'], 'schema-class', 'Physical finite supply/pile/deck limiting component availability.', source=['docs/rules/03-intruders-and-survival.md:INT-001', 'docs/rules/04-items-and-equipment.md:ITM-005'])

# Named identity kinds.
node('tax.identity.room', 'Named Room identity', ['tax.identity'], 'identity-kind', 'Exact-string Room title/source identity.', source=['docs/rules/vocabulary/named-component-identities.json'])
node('tax.identity.card-face', 'Named card/reference face identity', ['tax.identity'], 'identity-kind', 'Exact-string named card/reference face identity.', source=['docs/rules/vocabulary/named-component-identities.json'])
node('tax.identity.game-term-label', 'Named game-term/help label identity', ['tax.identity'], 'identity-kind', 'Exact-string game-term/help heading that is not necessarily a component identity.', source=['docs/rules/vocabulary/named-component-identities.json'])
node('tax.identity.structured-key', 'Secondary structured key identity', ['tax.identity'], 'identity-kind', 'BGA/TTS source-local technical object key.', source=['docs/rules/source-extraction/secondary-evidence-index.json'])
node('tax.identity.source-occurrence', 'Source occurrence', ['tax.identity'], 'identity-kind', 'One exact textual, visual, or structured occurrence in one source tuple.', source=['docs/rules/vocabulary/source-term-inventory.json'])
node('tax.identity.source-occurrence.help-entry', 'Help-sheet entry occurrence', ['tax.identity.source-occurrence'], 'identity-kind', 'One exact Room/Objective/Intruder Help entry occurrence.', source=['docs/rules/source-extraction/README.md'])
node('tax.identity.source-occurrence.icon', 'Printed icon occurrence', ['tax.identity.source-occurrence'], 'identity-kind', 'One source-local functional icon occurrence on a face/help entry.', source=['docs/rules/source-extraction/room-help-sheet.json'])

node_ids = {item['taxonId'] for item in nodes}
if len(node_ids) != len(nodes):
    raise AssertionError('duplicate taxon ID')
for item in nodes:
    if any(parent not in node_ids for parent in item['parentTaxonIds']):
        raise AssertionError(f'missing parent for {item["taxonId"]}')

# Controlled-term assignments.
assignments: dict[str, dict] = {}
def assign(label: str, primary: str, kind: str = 'denotes-taxon', denotes: list[str] | None = None, rationale: str | None = None) -> None:
    entry = term_by_label[label]
    if entry['termId'] in assignments:
        raise AssertionError(f'duplicate term assignment: {entry["termId"]}')
    assignments[entry['termId']] = {
        'termId': entry['termId'],
        'canonicalLabel': label,
        'primaryTaxonId': primary,
        'assignmentKind': kind,
        'alsoDenotesTaxonIds': denotes or [],
        'rationale': rationale or 'Direct controlled-term to taxonomy mapping.',
    }

# Assign all terms evidenced directly by nodes.
for item in nodes:
    for term_id in item['evidenceTermIds']:
        label = next(entry['canonicalLabel'] for entry in vocabulary['entries'] if entry['termId'] == term_id)
        if term_id not in assignments:
            assignments[term_id] = {'termId': term_id, 'canonicalLabel': label, 'primaryTaxonId': item['taxonId'], 'assignmentKind': 'denotes-taxon', 'alsoDenotesTaxonIds': [], 'rationale': 'Direct source-evidenced taxonomy node.'}

# Terms whose concept is represented by source evidence rather than direct node evidence.
for label, taxon in [
    ('Mission Task', 'tax.entity.information.mission-task'), ('Objective', 'tax.entity.information.objective'),
    ('Private Objective', 'tax.entity.information.objective.private'), ('Mission Objective', 'tax.entity.information.objective.mission'),
]:
    if term_by_label[label]['termId'] not in assignments:
        assign(label, taxon)

# Icon terms are printed-symbol identifiers with explicit denotations.
for label in ['Shoot die 2','Shoot die 3','Shoot die 4','Shoot die 5','Shoot die Ammo loss','Shoot die Critical hit','Burst die 1','Burst die 2','Burst die 3','Burst die 4','Burst die additional effects','Noise die 1','Noise die 2','Noise die 3','Noise die 4','Noise die Hazard result']:
    assign(label, 'tax.symbol.die-result', 'symbol-denotation')
for label in ['Red Item','Yellow Item','Green Item']:
    assign(label, 'tax.symbol.item-icon', 'symbol-denotation', ['tax.entity.component.card.item.regular'])
assign('Computer', 'tax.symbol.room-feature', 'symbol-denotation')
for label, target in [('Fire marker','tax.entity.component.marker.fire'),('Malfunction marker','tax.entity.component.marker.malfunction'),('Noise marker','tax.entity.component.marker.noise'),('Secure token','tax.entity.component.token.secure')]:
    assign(label, 'tax.symbol.component-reference', 'symbol-denotation', [target])
for label in ['Corridor (E–W)','Corridor (NE–SW)','Corridor (NW–SE)']:
    assign(label, 'tax.symbol.orientation', 'symbol-denotation', ['tax.value.orientation'])
for label, target in [('Active Life Support Systems','tax.state.activation.active'),('Inactive Life Support Systems','tax.state.activation.inactive'),('Active Hibernatorium','tax.state.activation.active'),('Inactive Hibernatorium','tax.state.activation.inactive')]:
    assign(label, 'tax.symbol.state-reference', 'symbol-denotation', [target])
for label, target in [('Lander token','tax.entity.component.token.lander'),('Autodestruction token','tax.entity.component.token.autodestruction'),('Oxygen Tactical Gear token','tax.entity.component.token.tactical-gear.oxygen'),('Ammo Tactical Gear token','tax.entity.component.token.tactical-gear.ammo'),('Grenade Tactical Gear token','tax.entity.component.token.tactical-gear.grenade'),('Medpack Tactical Gear token','tax.entity.component.token.tactical-gear.medpack')]:
    assign(label, 'tax.symbol.component-reference', 'symbol-denotation', [target])
for label in ['Tactical Gear slot for an Ammo token','Tactical Gear slot for a Grenade token','Tactical Gear slot for an Oxygen token','Tactical Gear slot for a Medpack token','Tactical Gear slot for any token']:
    assign(label, 'tax.symbol.component-reference', 'symbol-denotation', ['tax.entity.component.slot.tactical-gear'])
for label, target in [('Character','tax.entity.agent.character'),('Robot','tax.entity.agent.robot'),('Intruder','tax.entity.agent.intruder')]:
    assign(label, 'tax.symbol.entity-reference', 'symbol-denotation', [target])
assign('Oxygen', 'tax.symbol.state-reference', 'symbol-denotation', ['tax.value.resource.oxygen'])
assign('Character Health points', 'tax.symbol.state-reference', 'symbol-denotation', ['tax.state.health.point'])
assign('Action card', 'tax.symbol.component-reference', 'symbol-denotation', ['tax.entity.component.card.action'])
assign('Not In Combat', 'tax.symbol.state-reference', 'symbol-denotation', ['tax.state.combat.not-in-combat'])
assign('Number of Characters symbol', 'tax.symbol.metadata', 'symbol-denotation')

# Escape and Hibernate are printed both as procedures/verbs and as resulting
# participation states. Preserve the polysemy instead of forcing one branch.
assignments[term_by_label['Escape']['termId']]['alsoDenotesTaxonIds'] = ['tax.state.participation.escaped']
assignments[term_by_label['Escape']['termId']]['rationale'] = 'Denotes the Escape process and the resulting Escaped participation state.'
assignments[term_by_label['Hibernate']['termId']]['alsoDenotesTaxonIds'] = ['tax.state.participation.hibernated']
assignments[term_by_label['Hibernate']['termId']]['rationale'] = 'Denotes the Hibernate process and the resulting Hibernated participation state.'

if set(assignments) != term_ids:
    missing = sorted(term_ids - set(assignments))
    extra = sorted(set(assignments) - term_ids)
    raise AssertionError({'missingTermAssignments': missing, 'extra': extra})

# Named-identity assignments remain source identities, not class assertions.
game_term_identity_keys = {'data-token','escape','facility-destruction','fulfilled','nest-is-destroyed','queen-is-dead','survivor'}
identity_assignments = []
for record in identities['records']:
    roles = set(record['observedRoleCounts'])
    key = record['normalizedExactStringKey']
    if 'room-title' in roles:
        target = 'tax.identity.room'
    elif 'card-or-reference-title' in roles:
        target = 'tax.identity.card-face'
    elif 'objective-or-game-term-title' in roles and key not in game_term_identity_keys:
        target = 'tax.identity.card-face'
    elif 'objective-or-game-term-title' in roles:
        target = 'tax.identity.game-term-label'
    else:
        target = 'tax.identity.structured-key'
    identity_assignments.append({
        'identityObservationId': record['identityObservationId'],
        'normalizedExactStringKey': key,
        'primaryTaxonId': target,
        'assignmentKind': 'classifies-source-identity-only',
        'sourceOccurrenceCount': len(record['sourceOccurrences']),
        'boundary': 'Does not assert that matching display names are the same game object, class, card copy, or semantic effect.',
    })

identity_assignment_by_id = {item['identityObservationId']: item for item in identity_assignments}
alias_mappings = []
for alias in aliases['aliases']:
    if not alias['status'].startswith('accepted-'):
        raise AssertionError(f'unresolved alias reached ontology generation: {alias["aliasId"]}')
    target_term = alias.get('targetTermId')
    target_identity = alias.get('targetNamedIdentityId')
    if bool(target_term) == bool(target_identity):
        raise AssertionError(f'alias must target exactly one layer: {alias["aliasId"]}')
    target_taxa = []
    if target_term:
        assignment = assignments[target_term]
        target_taxa = [assignment['primaryTaxonId'], *assignment['alsoDenotesTaxonIds']]
    else:
        target_taxa = [identity_assignment_by_id[target_identity]['primaryTaxonId']]
    alias_mappings.append({
        'aliasId': alias['aliasId'],
        'aliasText': alias['aliasText'],
        'status': alias['status'],
        'scope': alias['scope'],
        'targetTermId': target_term,
        'targetNamedIdentityId': target_identity,
        'targetTaxonIds': sorted(set(target_taxa)),
        'sourceTupleCount': len(alias.get('sourceTuples') or []),
        'boundary': 'Projection of the accepted scoped alias only; never owl:sameAs and never broader than alias-registry scope.',
    })

# Static relationship vocabulary. Effect steps/targets/cost values are not instantiated here.
relations = []
def relation(rel_id: str, label: str, domain: list[str], range_: list[str], *, inverse: str | None = None, symmetric: bool = False, transitive: bool = False, cardinality: dict | None = None, source: list[str] | None = None, boundary: str) -> None:
    relations.append({'relationId': rel_id, 'label': label, 'domainTaxonIds': sorted(set(domain)), 'rangeTaxonIds': sorted(set(range_)), 'inverseRelationId': inverse, 'symmetric': symmetric, 'transitive': transitive, 'cardinalityShape': cardinality or {}, 'sourceEvidence': source or [], 'semanticBoundary': boundary})

relation('rel.part-of','part of',['tax.entity'],['tax.entity'],inverse='rel.has-part',transitive=True,source=['docs/rulebooks/rulebook_text.txt:printed page 20'],boundary='Static composition only; creation/removal procedures are deferred.')
relation('rel.has-part','has part',['tax.entity'],['tax.entity'],inverse='rel.part-of',transitive=True,source=['docs/rulebooks/rulebook_text.txt:printed page 20'],boundary='Static composition only.')
relation('rel.controls-character','controls Character',['tax.entity.agent.player'],['tax.entity.agent.character'],inverse='rel.controlled-by-player',cardinality={'baseSetupPerPlayer':{'min':1,'max':1}},source=['docs/rulebooks/rulebook_text.txt:Character setup'],boundary='The control association is structural; player decisions are separate.')
relation('rel.controlled-by-player','controlled by Player',['tax.entity.agent.character'],['tax.entity.agent.player'],inverse='rel.controls-character',cardinality={'baseSetupPerCharacter':{'min':1,'max':1}},source=['docs/rulebooks/rulebook_text.txt:Character setup'],boundary='The control association is structural.')
relation('rel.located-in-section','located in Section',['tax.entity.spatial.room'],['tax.entity.spatial.section'],inverse='rel.has-room',cardinality={'placedRoom':{'min':1,'max':1}},source=['docs/rulebooks/rulebook_text.txt:lines 3915–3918'],boundary='Applies to placed Rooms; placement procedure is deferred.')
relation('rel.has-room','has Room',['tax.entity.spatial.section'],['tax.entity.spatial.room'],inverse='rel.located-in-section',source=['docs/rulebooks/rulebook_text.txt:lines 3915–3918'],boundary='Static containment after Room placement.')
relation('rel.connects-endpoint','connects endpoint',['tax.entity.spatial.corridor'],['tax.entity.spatial.room-slot'],inverse='rel.endpoint-connected-by',cardinality={'placedCorridor':{'min':2,'max':2}},source=['docs/rules/00-foundations.md:FND-005'],boundary='Topology only; exploration placement legality is deferred.')
relation('rel.endpoint-connected-by','endpoint connected by',['tax.entity.spatial.room-slot'],['tax.entity.spatial.corridor'],inverse='rel.connects-endpoint',source=['docs/rules/00-foundations.md:FND-005'],boundary='Topology only.')
relation('rel.adjacent-to','adjacent to',['tax.entity.spatial.location'],['tax.entity.spatial.location'],symmetric=True,source=['docs/rules/00-foundations.md:FND-005','docs/rules/02-character-actions.md:Doors'],boundary='Adjacency does not imply access; Closed Doors preserve adjacency while blocking effects.')
relation('rel.door-at-corridor-end','Door at Corridor end',['tax.entity.spatial.door'],['tax.entity.spatial.corridor'],inverse='rel.has-end-door',cardinality={'door':{'min':1,'max':1}},source=['docs/rules/02-character-actions.md:Doors'],boundary='Static placement relation; Door state transitions are deferred.')
relation('rel.has-end-door','has endpoint Door',['tax.entity.spatial.corridor'],['tax.entity.spatial.door'],inverse='rel.door-at-corridor-end',source=['docs/rules/02-character-actions.md:Doors'],boundary='A Corridor may have endpoint Door slots; exact per-tile count is source data.')
relation('rel.occupies-location','occupies location',['tax.entity.agent'],['tax.entity.spatial.location'],inverse='rel.contains-agent',source=['docs/rulebooks/rulebook_text.txt:lines 3919–3921'],boundary='Dynamic location slot only; movement transitions are deferred.')
relation('rel.contains-agent','contains agent',['tax.entity.spatial.location'],['tax.entity.agent'],inverse='rel.occupies-location',source=['docs/rulebooks/rulebook_text.txt:lines 3919–3921'],boundary='Dynamic containment only.')
relation('rel.has-state','has state',['tax.entity'],['tax.state'],inverse='rel.state-of',source=['docs/rules/02-character-actions.md:Doors','docs/rules/03-intruders-and-survival.md'],boundary='State association only; triggers/transitions are deferred.')
relation('rel.state-of','state of',['tax.state'],['tax.entity'],inverse='rel.has-state',source=['docs/rules/02-character-actions.md:Doors'],boundary='State association only.')
relation('rel.has-role','has role',['tax.entity.agent'],['tax.role'],inverse='rel.role-held-by',source=['docs/rules/01-round-and-turns.md:RT-002'],boundary='Role assignment only; acquisition/transfer procedures are deferred.')
relation('rel.role-held-by','role held by',['tax.role'],['tax.entity.agent'],inverse='rel.has-role',source=['docs/rules/01-round-and-turns.md:RT-002'],boundary='Role assignment only.')
relation('rel.card-carries-content','card carries content',['tax.entity.component.card'],['tax.entity.information'],inverse='rel.content-printed-on-card',source=['docs/rules/01-round-and-turns.md:RT-010','docs/rules/source-extraction/objective-help-sheet.json'],boundary='Printed information relation; fulfillment evaluation is deferred.')
relation('rel.content-printed-on-card','content printed on card',['tax.entity.information'],['tax.entity.component.card'],inverse='rel.card-carries-content',source=['docs/rules/source-extraction/objective-help-sheet.json'],boundary='Printed information relation.')
relation('rel.belongs-to-deck','belongs to deck',['tax.entity.component.card'],['tax.scaffold.zone.deck'],inverse='rel.deck-contains-card',source=['docs/rulebooks/rulebook_text.txt:setup'],boundary='Deck membership identity only; draw/shuffle/discard transitions are deferred.')
relation('rel.deck-contains-card','deck contains card',['tax.scaffold.zone.deck'],['tax.entity.component.card'],inverse='rel.belongs-to-deck',source=['docs/rulebooks/rulebook_text.txt:setup'],boundary='Deck membership identity only.')
relation('rel.component-in-zone','component in zone',['tax.entity.component'],['tax.scaffold.zone'],inverse='rel.zone-contains-component',source=['docs/rules/01-round-and-turns.md','docs/rules/02-character-actions.md'],boundary='Current/static zone relation; transition operations are deferred.')
relation('rel.zone-contains-component','zone contains component',['tax.scaffold.zone'],['tax.entity.component'],inverse='rel.component-in-zone',source=['docs/rules/01-round-and-turns.md'],boundary='Zone membership only.')
relation('rel.item-stored-in','Item stored in',['tax.entity.component.card.item'],['tax.entity.component.storage'],inverse='rel.storage-contains-item',source=['docs/rules/04-items-and-equipment.md:ITM-002'],boundary='Storage legality class relation; specific movement between storage areas is deferred.')
relation('rel.storage-contains-item','storage contains Item',['tax.entity.component.storage'],['tax.entity.component.card.item'],inverse='rel.item-stored-in',source=['docs/rules/04-items-and-equipment.md:ITM-002'],boundary='Storage relation only.')
relation('rel.token-occupies-slot','token occupies slot',['tax.entity.component.token.tactical-gear'],['tax.entity.component.slot.tactical-gear'],inverse='rel.slot-contains-token',cardinality={'perToken':{'min':0,'max':1},'perSlot':{'min':0,'max':1}},source=['docs/rules/04-items-and-equipment.md:ITM-005'],boundary='Occupancy/compatibility only; gain/use/discard effects are deferred.')
relation('rel.slot-contains-token','slot contains token',['tax.entity.component.slot.tactical-gear'],['tax.entity.component.token.tactical-gear'],inverse='rel.token-occupies-slot',cardinality={'perSlot':{'min':0,'max':1}},source=['docs/rules/04-items-and-equipment.md:ITM-005'],boundary='Occupancy only.')
relation('rel.symbol-denotes','symbol denotes',['tax.symbol'],['tax.entity','tax.process','tax.state','tax.role','tax.value'],inverse='rel.denoted-by-symbol',source=['docs/rules/icon-glossary.md'],boundary='Canonical denotation only; source artwork equivalence remains governed by alias-registry source tuples.')
relation('rel.denoted-by-symbol','denoted by symbol',['tax.entity','tax.process','tax.state','tax.role','tax.value'],['tax.symbol'],inverse='rel.symbol-denotes',source=['docs/rules/icon-glossary.md'],boundary='Canonical denotation only.')
relation('rel.named-identity-instantiates','named identity instantiates',['tax.identity'],['tax.entity','tax.process','tax.state','tax.role','tax.rule'],inverse='rel.has-named-identity',source=['docs/rules/vocabulary/named-component-identities.json'],boundary='Must be explicitly asserted; exact display-name equality never creates this relation automatically.')
relation('rel.has-named-identity','has named identity',['tax.entity','tax.process','tax.state','tax.role','tax.rule'],['tax.identity'],inverse='rel.named-identity-instantiates',source=['docs/rules/vocabulary/named-component-identities.json'],boundary='Must be explicitly asserted.')
relation('rel.map-depicts-facility','Map depicts Facility',['tax.entity.spatial.map'],['tax.entity.spatial.facility'],inverse='rel.facility-depicted-by-map',cardinality={'baseMap':{'min':1,'max':1}},source=['docs/rulebooks/rulebook_text.txt:lines 3915–3918'],boundary='Static representation relation, not map rendering or setup procedure.')
relation('rel.facility-depicted-by-map','Facility depicted by Map',['tax.entity.spatial.facility'],['tax.entity.spatial.map'],inverse='rel.map-depicts-facility',cardinality={'baseFacility':{'min':1,'max':1}},source=['docs/rulebooks/rulebook_text.txt:lines 3915–3918'],boundary='Static representation relation.')
relation('rel.section-part-of-facility','Section part of Facility',['tax.entity.spatial.section'],['tax.entity.spatial.facility'],inverse='rel.facility-has-section',cardinality={'baseSection':{'min':1,'max':1}},source=['docs/rulebooks/rulebook_text.txt:lines 3915–3918'],boundary='Static base-map composition only.')
relation('rel.facility-has-section','Facility has Section',['tax.entity.spatial.facility'],['tax.entity.spatial.section'],inverse='rel.section-part-of-facility',cardinality={'baseFacility':{'min':3,'max':3}},source=['docs/rulebooks/rulebook_text.txt:lines 3915–3918'],boundary='Base Facility has Sections A, B, and C; phase/mode variants remain separately scoped.')
relation('rel.corridor-located-in-section','Corridor located in Section',['tax.entity.spatial.corridor'],['tax.entity.spatial.section'],inverse='rel.section-has-corridor',cardinality={'placedCorridor':{'min':1,'max':2}},source=['docs/rulebooks/rulebook_text.txt:lines 4138–4140'],boundary='A border Corridor belongs to both bordering Sections; placement procedure is deferred.')
relation('rel.section-has-corridor','Section has Corridor',['tax.entity.spatial.section'],['tax.entity.spatial.corridor'],inverse='rel.corridor-located-in-section',source=['docs/rulebooks/rulebook_text.txt:lines 4138–4140'],boundary='Static Section membership only.')
relation('rel.door-bounds-room','Door bounds Room',['tax.entity.spatial.door'],['tax.entity.spatial.room'],inverse='rel.room-bounded-by-door',cardinality={'placedDoor':{'min':1,'max':1}},source=['docs/rules/02-character-actions.md:Doors'],boundary='Door is at a Corridor end against one Room; state/access effects are deferred.')
relation('rel.room-bounded-by-door','Room bounded by Door',['tax.entity.spatial.room'],['tax.entity.spatial.door'],inverse='rel.door-bounds-room',source=['docs/rules/02-character-actions.md:Doors'],boundary='Static boundary relation only.')
relation('rel.source-occurrence-documents-definition','source occurrence documents definition',['tax.identity.source-occurrence'],['tax.entity.information.component-definition'],inverse='rel.definition-documented-by-source-occurrence',source=['docs/rules/source-extraction/README.md'],boundary='Provenance relation only; it does not merge versions or assert semantic equivalence.')
relation('rel.definition-documented-by-source-occurrence','definition documented by source occurrence',['tax.entity.information.component-definition'],['tax.identity.source-occurrence'],inverse='rel.source-occurrence-documents-definition',source=['docs/rules/source-extraction/README.md'],boundary='Provenance relation only.')
relation('rel.component-copy-realizes-definition','component copy realizes definition',['tax.entity.component'],['tax.entity.information.component-definition'],inverse='rel.definition-realized-by-copy',cardinality={'componentCopy':{'min':1,'max':1}},source=['docs/rulebooks/Nemesis_RT_Rulebook_official.pdf:component list','docs/rules/source-extraction/README.md'],boundary='Definition/copy separation; multiple physical copies may realize one definition.')
relation('rel.definition-realized-by-copy','definition realized by component copy',['tax.entity.information.component-definition'],['tax.entity.component'],inverse='rel.component-copy-realizes-definition',source=['docs/rulebooks/Nemesis_RT_Rulebook_official.pdf:component list'],boundary='Definition/copy separation.')
relation('rel.component-copy-member-of-set','component copy member of set',['tax.entity.component'],['tax.entity.component-set'],inverse='rel.component-set-has-copy',source=['docs/rulebooks/Nemesis_RT_Rulebook_official.pdf:component list'],boundary='Static inventory/deck/pool membership; draw/removal transitions are deferred.')
relation('rel.component-set-has-copy','component set has copy',['tax.entity.component-set'],['tax.entity.component'],inverse='rel.component-copy-member-of-set',source=['docs/rulebooks/Nemesis_RT_Rulebook_official.pdf:component list'],boundary='Static inventory membership only.')
relation('rel.help-entry-describes-room-definition','Help entry describes Room definition',['tax.identity.source-occurrence.help-entry'],['tax.entity.information.component-definition.room'],inverse='rel.room-definition-described-by-help-entry',source=['docs/rules/source-extraction/room-help-sheet.json'],boundary='Exact source occurrence to definition relation; aliases and semantics remain separately reviewed.')
relation('rel.room-definition-described-by-help-entry','Room definition described by Help entry',['tax.entity.information.component-definition.room'],['tax.identity.source-occurrence.help-entry'],inverse='rel.help-entry-describes-room-definition',cardinality={'officialRoomHelpDefinition':{'min':1,'max':1}},source=['docs/rules/source-extraction/room-help-sheet.json'],boundary='Official Room Help source relation only.')
relation('rel.action-deck-for-character-role','Action deck for Character role',['tax.scaffold.zone.deck'],['tax.role.character'],inverse='rel.character-role-has-action-deck',cardinality={'baseCharacterRole':{'min':1,'max':1}},source=['docs/rulebooks/rulebook_text.txt:lines 2684–2689'],boundary='Deck-role association only; individual face effects and deck transitions are deferred.')
relation('rel.character-role-has-action-deck','Character role has Action deck',['tax.role.character'],['tax.scaffold.zone.deck'],inverse='rel.action-deck-for-character-role',cardinality={'baseCharacterRole':{'min':1,'max':1}},source=['docs/rulebooks/rulebook_text.txt:lines 2684–2689'],boundary='Deck-role association only.')
relation('rel.icon-occurrence-appears-on-definition','icon occurrence appears on definition',['tax.identity.source-occurrence.icon'],['tax.entity.information.component-definition'],inverse='rel.definition-has-icon-occurrence',source=['docs/rules/source-extraction/room-help-sheet.json','assets/tts-mod/extract/card-text-corpus.json'],boundary='Source-local occurrence placement only; semantic denotation is a separate reviewed relation.')
relation('rel.definition-has-icon-occurrence','definition has icon occurrence',['tax.entity.information.component-definition'],['tax.identity.source-occurrence.icon'],inverse='rel.icon-occurrence-appears-on-definition',source=['docs/rules/source-extraction/room-help-sheet.json','assets/tts-mod/extract/card-text-corpus.json'],boundary='Source-local occurrence inventory only.')
relation('rel.room-definition-designated-for-section','Room definition designated for Section',['tax.entity.information.component-definition.room'],['tax.entity.spatial.section'],inverse='rel.section-has-designated-room-definition',cardinality={'typedRoomDefinition':{'min':0,'max':1}},source=['docs/rules/source-extraction/room-help-sheet.json'],boundary='A/B/C printed designation only; “?” remains unassigned and placement is deferred.')
relation('rel.section-has-designated-room-definition','Section has designated Room definition',['tax.entity.spatial.section'],['tax.entity.information.component-definition.room'],inverse='rel.room-definition-designated-for-section',source=['docs/rules/source-extraction/room-help-sheet.json'],boundary='Printed Room-type designation only.')
# Temporal ordering, decision ownership, visibility, and lifecycle transition
# properties are deliberately deferred to the semantic layer. The scaffold
# taxa above reserve their types without pretending that static ontology is an
# executable timing/effect model.
relation('rel.limited-by-supply','limited by supply',['tax.entity.component'],['tax.scaffold.supply-pool'],inverse='rel.supply-limits',source=['docs/rules/03-intruders-and-survival.md:INT-001','docs/rules/04-items-and-equipment.md:ITM-005'],boundary='Finite-supply relation; exhaustion resolution remains source-specific.')
relation('rel.supply-limits','supply limits',['tax.scaffold.supply-pool'],['tax.entity.component'],inverse='rel.limited-by-supply',source=['docs/rules/03-intruders-and-survival.md:INT-001'],boundary='Finite-supply relation.')

# Static assertions/constraints; not executable effect records.
assertions = [
    {'assertionId':'AS-001','kind':'closed-enumeration','subjectTaxonId':'tax.entity.spatial.section','memberTaxonIds':['tax.entity.spatial.section.a','tax.entity.spatial.section.b','tax.entity.spatial.section.c'],'scope':'base Facility','sourceEvidence':['docs/rulebooks/rulebook_text.txt:lines 3915–3918']},
    {'assertionId':'AS-002','kind':'ontology-level-separation','taxonIds':['tax.identity.source-occurrence','tax.entity.information.component-definition','tax.entity.component'],'sourceEvidence':['docs/rules/source-extraction/README.md','docs/rulebooks/Nemesis_RT_Rulebook_official.pdf:component list'],'boundary':'Source occurrences document definitions; runtime/physical copies realize definitions. No pair is automatically identical or owl:sameAs.'},
    {'assertionId':'AS-003','kind':'placement-constraint','subjectTaxonId':'tax.entity.agent.character','allowedLocationTaxonIds':['tax.entity.spatial.room'],'forbiddenLocationTaxonIds':['tax.entity.spatial.corridor'],'scope':'while on Facility map','sourceEvidence':['docs/rulebooks/rulebook_text.txt:lines 3919–3921']},
    {'assertionId':'AS-004','kind':'placement-constraint','subjectTaxonId':'tax.entity.agent.intruder','allowedLocationTaxonIds':['tax.entity.spatial.room','tax.entity.spatial.corridor'],'scope':'while on Facility map','sourceEvidence':['docs/rulebooks/rulebook_text.txt:lines 3919–3921']},
    {'assertionId':'AS-005','kind':'capacity-constraint','subjectTaxonId':'tax.entity.spatial.room','capacity':'unlimited Intruders','sourceEvidence':['docs/rules/03-intruders-and-survival.md:INT-001']},
    {'assertionId':'AS-006','kind':'weighted-capacity-constraint','subjectTaxonId':'tax.entity.spatial.corridor','capacity':6,'weightByTaxonId':{'tax.entity.agent.intruder.queen':4,'tax.entity.agent.intruder.drone':1,'tax.entity.agent.intruder.adult':1,'tax.entity.agent.intruder.larva':1},'sourceEvidence':['docs/rules/03-intruders-and-survival.md:INT-001']},
    {'assertionId':'AS-007','kind':'state-exclusive-set','subjectTaxonId':'tax.entity.spatial.door','stateTaxonIds':['tax.state.opened','tax.state.closed','tax.state.destroyed'],'cardinality':{'min':1,'max':1},'sourceEvidence':['docs/rules/02-character-actions.md:Doors']},
    {'assertionId':'AS-008','kind':'non-disjoint-classification-dimensions','subjectTaxonId':'tax.entity.component.card.item','taxonIds':['tax.entity.component.card.item.regular','tax.entity.component.card.item.heavy','tax.entity.component.card.item.armor','tax.entity.component.card.item.character','tax.entity.component.card.item.support','tax.entity.component.card.item.weapon'],'sourceEvidence':['docs/rules/04-items-and-equipment.md:ITM-001','docs/rules/04-items-and-equipment.md:ITM-002'],'boundary':'Physical class, source family, and function are distinct dimensions; no disjointness is inferred except where a source states it.'},
    {'assertionId':'AS-009','kind':'storage-class-rule','subjectTaxonId':'tax.entity.component.card.item.regular','targetTaxonId':'tax.entity.component.storage.backpack','sourceEvidence':['docs/rules/04-items-and-equipment.md:ITM-002']},
    {'assertionId':'AS-010','kind':'storage-class-rule','subjectTaxonId':'tax.entity.component.card.item.heavy','targetTaxonId':'tax.entity.component.slot.hand','sourceEvidence':['docs/rules/04-items-and-equipment.md:ITM-002'],'cardinality':{'ordinaryPerHandSlotMax':1,'exceptionPolicy':'Specific effects may override; exceptions belong to semantic data.'}},
    {'assertionId':'AS-011','kind':'component-distinction','taxonIds':['tax.process.action.basic','tax.entity.component.card.action'],'sourceEvidence':['docs/rules/02-character-actions.md:ACT-CARD-001'],'boundary':'Basic Actions are process/options; Action cards are physical cards. They must never be merged by name.'},
    {'assertionId':'AS-012','kind':'component-distinction','taxonIds':['tax.entity.component.card.contamination','tax.entity.component.card.action'],'sourceEvidence':['docs/rules/02-character-actions.md:ACT-CARD-002'],'boundary':'They share a back but form separate card/deck classes.'},
    {'assertionId':'AS-013','kind':'identity-alias','sourceIdentityLabel':'Drilling Room','targetNamedIdentityId':'NI-0133','sourceEvidence':['docs/rules/vocabulary/alias-registry.json:AL-004'],'boundary':'Both official labels remain preserved; the alias does not rename source evidence.'},
    {'assertionId':'AS-014','kind':'source-scoped-alias','sourceIdentityLabel':'PERSONAL OBJECTIVE','targetTermId':'term.private-objective','sourceEvidence':['docs/rules/vocabulary/alias-registry.json:AL-003'],'boundary':'Applies only to exact listed source tuples.'},
]

# Review gates: no owner decision is invented here. Technical/source questions can be
# carried as deferred semantic issues rather than blocking the static ontology.
review_gates = {
    'schemaVersion': 1,
    'recordType': 'taxonomy-ontology-review-gates',
    'status': 'independent taxonomy, relationship, ambiguity, and validator audits incorporated; no owner gate blocks static ontology approval',
    'counts': {'reviewGates': 0, 'resolved': 0, 'open': 0},
    'gates': [],
    'independentAudit': {
        'delegationId': 'deleg_0cdda6e9',
        'workstreams': 4,
        'incorporatedFindings': [
            'separate source occurrence, component definition, component set, and runtime/physical copy levels',
            'Reaction is not an Action; generic Attack and Opportunity Attack are not automatically player Actions',
            'retain carrier/card versus printed-content distinction',
            'defer timing, decision ownership, visibility, and lifecycle transition relations to semantic modeling',
            'add missing Facility/Section/Corridor/Door/definition/copy/set/deck-role/icon-occurrence structural edges',
            'correct Empty Corridor: Noise is allowed; only Intruders make it non-empty',
            'harden mapping, inverse-signature, alias-projection, provenance, cardinality, phase-boundary, and reproducibility validation',
        ],
    },
    'deferredSemanticRelationIds': [
        'rel.phase-part-of-round', 'rel.round-has-phase', 'rel.precedes', 'rel.follows',
        'rel.turn-occurs-in-phase', 'rel.phase-has-turn', 'rel.process-has-timing-window',
        'rel.decision-owned-by', 'rel.owns-decision', 'rel.information-visible-to',
        'rel.transition-from', 'rel.transition-to',
    ],
    'deferredNonBlockingQuestions': [
        {'questionId':'ONTO-DQ-001','sourceQuestionId':'OQ-001','classification':'semantic-procedure ambiguity','reason':'Eclosion existing-hand scope does not alter static classes or relations.'},
        {'questionId':'ONTO-DQ-003','sourceQuestionId':'OQ-003','classification':'semantic role-transfer ambiguity','reason':'Starting Player eligibility/transfer algorithm is not needed to define Player, role, or token classes.'},
        {'questionId':'ONTO-DQ-004','sourceQuestionId':'OQ-004','classification':'semantic timing ambiguity','reason':'Mid-Turn death advancement belongs to turn-resolution semantics.'},
        {'questionId':'ONTO-DQ-005','sourceQuestionId':'OQ-007','classification':'semantic cardinality-per-event ambiguity','reason':'Secure consumption during simultaneous entry is effect resolution, not static component cardinality.'},
        {'questionId':'ONTO-DQ-006','sourceQuestionId':'OQ-009','classification':'semantic placement ambiguity','reason':'Nest event before discovery concerns effect timing/placement.'},
    ],
}

# Validate inverses now so generated artifacts cannot encode one-way mismatches.
relation_by_id = {item['relationId']: item for item in relations}
for item in relations:
    inverse = item['inverseRelationId']
    if inverse:
        if inverse not in relation_by_id or relation_by_id[inverse]['inverseRelationId'] != item['relationId']:
            raise AssertionError(f'bad inverse for {item["relationId"]}')

kind_counts = collections.Counter(item['ontologicalKind'] for item in nodes)
term_assignment_rows = [assignments[term_id] for term_id in sorted(assignments)]
identity_counts = collections.Counter(item['primaryTaxonId'] for item in identity_assignments)

taxonomy = {
    'schemaVersion': 1,
    'recordType': 'source-traceable-taxonomy-proposal',
    'phaseBoundary': 'Classification only. Multiple parents do not imply disjointness unless declared. No executable effects, triggers, costs, choices, targets, or state transitions are encoded.',
    'counts': {
        'taxa': len(nodes),
        'rootTaxa': sum(not item['parentTaxonIds'] for item in nodes),
        'controlledTermAssignments': len(term_assignment_rows),
        'namedIdentityAssignments': len(identity_assignments),
        'byOntologicalKind': dict(sorted(kind_counts.items())),
        'namedIdentityAssignmentsByTaxon': dict(sorted(identity_counts.items())),
    },
    'taxa': nodes,
}

mappings = {
    'schemaVersion': 1,
    'recordType': 'taxonomy-mappings',
    'counts': {'controlledTerms': len(term_assignment_rows), 'namedIdentities': len(identity_assignments), 'symbolDenotations': sum(item['assignmentKind'] == 'symbol-denotation' for item in term_assignment_rows), 'acceptedAliases': len(alias_mappings)},
    'controlledTermAssignments': term_assignment_rows,
    'namedIdentityAssignments': identity_assignments,
    'acceptedAliasMappings': alias_mappings,
}

ontology = {
    'schemaVersion': 1,
    'recordType': 'static-ontology-proposal',
    'phaseBoundary': 'Static classes, relationship shapes, source-backed constraints, and scaffolding only. No effect instances, ordered mutations, legality algorithms, target selection, costs, or visibility decisions are encoded.',
    'counts': {'relations': len(relations), 'inversePairs': sum(bool(item['inverseRelationId']) for item in relations) // 2, 'staticAssertions': len(assertions), 'semanticScaffoldTaxa': sum(item['taxonId'].startswith('tax.scaffold') for item in nodes)},
    'relations': relations,
    'staticAssertions': assertions,
}

write('taxonomy.json', taxonomy)
write('mappings.json', mappings)
write('ontology.json', ontology)
write('review-gates.json', review_gates)
print(json.dumps({'taxonomy': taxonomy['counts'], 'mappings': mappings['counts'], 'ontology': ontology['counts'], 'review': review_gates['counts']}, indent=2))
