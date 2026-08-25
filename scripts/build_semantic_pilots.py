#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--output-dir', type=Path, default=REPO / 'docs/rules/semantics')
args = parser.parse_args()
OUT = args.output_dir.resolve()
OUT.mkdir(parents=True, exist_ok=True)


def sha(path: str) -> str:
    return hashlib.sha256((REPO / path).read_bytes()).hexdigest()


def write(name: str, value: dict) -> None:
    (OUT / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


sources = {
    'SRC-RULEBOOK': {
        'sourceId': 'SRC-RULEBOOK', 'authority': 'official-primary', 'version': 'base rulebook, local official PDF',
        'path': 'docs/rulebooks/Nemesis_RT_Rulebook_official.pdf', 'sha256': sha('docs/rulebooks/Nemesis_RT_Rulebook_official.pdf'),
        'evidenceIndexPath': 'docs/rules/source-extraction/rulebook-visual-obligations.json',
    },
    'SRC-FAQ': {
        'sourceId': 'SRC-FAQ', 'authority': 'official-errata', 'version': 'v1.2 / 2026-06-08',
        'path': 'docs/rulebooks/Nemesis_RT_FAQ_v1.2.pdf', 'sha256': sha('docs/rulebooks/Nemesis_RT_FAQ_v1.2.pdf'),
        'evidenceIndexPath': 'docs/rules/source-extraction/faq-v1.2-source-extraction.json',
    },
    'SRC-ROOM-HELP': {
        'sourceId': 'SRC-ROOM-HELP', 'authority': 'official-component-reference', 'version': 'base Room Help Sheet',
        'path': 'docs/rulebooks/Nemesis_RT_Rooms_Sheet.pdf', 'sha256': sha('docs/rulebooks/Nemesis_RT_Rooms_Sheet.pdf'),
        'evidenceIndexPath': 'docs/rules/source-extraction/room-help-sheet.json',
    },
    'SRC-INTRUDER-HELP-QA': {
        'sourceId': 'SRC-INTRUDER-HELP-QA', 'authority': 'source-bound-component-scan', 'version': 'TTS Queen Alive face',
        'path': 'assets/tts-mod/extract/v2-dl/tree/cards/reference/card-053.png', 'sha256': sha('assets/tts-mod/extract/v2-dl/tree/cards/reference/card-053.png'),
        'evidenceIndexPath': 'docs/rules/source-extraction/intruder-help-sheet.json',
    },
    'SRC-CARD-SEARCH-MEDICAL': {
        'sourceId': 'SRC-CARD-SEARCH-MEDICAL', 'authority': 'source-bound-component-scan', 'version': 'Medical Support Search face',
        'path': 'assets/tts-mod/extract/v2-dl/tree/cards/character/medical-support-047.jpg', 'sha256': sha('assets/tts-mod/extract/v2-dl/tree/cards/character/medical-support-047.jpg'),
        'evidenceIndexPath': 'assets/tts-mod/extract/card-text-corpus.json',
    },
    'SRC-CARD-REST': {
        'sourceId': 'SRC-CARD-REST', 'authority': 'source-bound-component-scan', 'version': 'project-owner-reviewed canonical Rest face',
        'path': 'assets/tts-mod/extract/v2-dl/tree/cards/game/action/rest.png', 'sha256': sha('assets/tts-mod/extract/v2-dl/tree/cards/game/action/rest.png'),
        'evidenceIndexPath': 'assets/tts-mod/extract/card-text-corpus.json',
    },
    'SRC-CARD-REST-MEDICAL': {
        'sourceId': 'SRC-CARD-REST-MEDICAL', 'authority': 'source-bound-component-scan', 'version': 'Medical Support Rest source variant',
        'path': 'assets/tts-mod/extract/v2-dl/tree/cards/character/medical-support-022.jpg', 'sha256': sha('assets/tts-mod/extract/v2-dl/tree/cards/character/medical-support-022.jpg'),
        'evidenceIndexPath': 'assets/tts-mod/extract/card-text-corpus.json',
    },
    'SRC-CARD-DUCK': {
        'sourceId': 'SRC-CARD-DUCK', 'authority': 'source-bound-component-scan', 'version': 'Contractor: Consultant Duck and Cover face',
        'path': 'assets/tts-mod/extract/v2-dl/tree/cards/character/contractor-026.jpg', 'sha256': sha('assets/tts-mod/extract/v2-dl/tree/cards/character/contractor-026.jpg'),
        'evidenceIndexPath': 'assets/tts-mod/extract/card-text-corpus.json',
    },
    'SRC-EVENT-HATCHING': {
        'sourceId': 'SRC-EVENT-HATCHING', 'authority': 'source-bound-component-scan', 'version': 'canonical Hatching Event face',
        'path': 'assets/tts-mod/extract/v2-dl/tree/cards/game/event-090.png', 'sha256': sha('assets/tts-mod/extract/v2-dl/tree/cards/game/event-090.png'),
        'evidenceIndexPath': 'assets/tts-mod/extract/card-text-corpus.json',
    },
}
source_registry = {
    'schemaVersion': 1, 'recordType': 'semantic-source-registry',
    'authorityOrder': ['official-errata', 'official-primary', 'official-component-reference', 'source-bound-component-scan', 'licensed-digital-secondary', 'project-interpretation'],
    'counts': {'sources': len(sources)}, 'sources': [sources[source_id] for source_id in sorted(sources)],
}

# JSON Schema is intentionally explicit enough for external consumers while the
# project validator adds cross-file/reference/authority checks without a third-party package.
semantic_schema = {
    '$schema': 'https://json-schema.org/draft/2020-12/schema',
    '$id': 'https://example.invalid/nemesis-retaliation/semantic-rule.schema.json',
    'title': 'Nemesis Retaliation semantic rule record',
    'type': 'object',
    'required': ['ruleId','title','status','ruleKind','applicability','authority','sourceAssertions','termRefs','taxonRefs','namedIdentityRefs','timing','participants','modality','preconditions','decisions','informationPolicy','costs','targets','operations','partialResolution','duration','stacking','outcomes','unresolvedQuestionRefs','sourceVariants','implementationBoundary'],
    'additionalProperties': False,
    'properties': {
        'ruleId': {'type':'string','pattern':'^SEM-[A-Z0-9-]+$'},
        'title': {'type':'string','minLength':1},
        'status': {'enum':['source-backed','source-backed-with-open-question','source-variant']},
        'ruleKind': {'enum':['sequence','procedure','action','reaction','component-effect','event','dispatcher','endgame']},
        'applicability': {'type':'object','required':['game','mode','playerCount'], 'properties':{'game':{'const':'Nemesis: Retaliation'},'mode':{'enum':['base','base-standard']},'playerCount':{'type':['object','null']}}},
        'authority': {'type':'object','required':['highest','interpretation'], 'properties':{'highest':{'enum':['official-errata','official-primary','official-component-reference','source-bound-component-scan']},'interpretation':{'enum':['verbatim-structure','source-composed','open-alternatives']}}},
        'sourceAssertions': {'type':'array','minItems':1},
        'termRefs': {'type':'array'}, 'taxonRefs': {'type':'array'}, 'namedIdentityRefs': {'type':'array'},
        'timing': {'type':'object'}, 'participants': {'type':'array'}, 'modality': {'enum':['must','may','cannot','if-able','mixed']},
        'preconditions': {'type':'array'}, 'decisions': {'type':'array'}, 'informationPolicy': {'type':'array'}, 'costs': {'type':'array'}, 'targets': {'type':'array'}, 'operations': {'type':'array','minItems':1},
        'partialResolution': {'type':'object'}, 'duration': {'type':'object'}, 'stacking': {'type':'object'}, 'outcomes': {'type':'array'}, 'unresolvedQuestionRefs': {'type':'array'}, 'sourceVariants': {'type':'array'},
        'implementationBoundary': {'const':'implementation-neutral; no engine, UI, network, storage, or serialization mapping'},
    },
}


def assertion(assertion_id, source_id, locator, supports, excerpt=None, evidence_record=None):
    return {'assertionId': assertion_id, 'sourceId': source_id, 'locator': locator, 'supportsFields': supports, 'sourceText': excerpt, 'textKind': 'normalized-paraphrase', 'evidenceRecord': evidence_record}


def timing(window_id, anchor, relation, recurrence='once-per-invocation'):
    return {'windowId': window_id, 'anchorTaxonId': anchor, 'relation': relation, 'recurrence': recurrence}


def participant(pid, kind, taxon=None, role=None):
    return {'participantId': pid, 'participantKind': kind, 'taxonId': taxon, 'role': role}


def condition(cid, operator, args, sources, scope='record-precondition'):
    return {'conditionId': cid, 'scope': scope, 'expression': {'operator': operator, 'args': args}, 'sourceAssertionIds': sources}


def decision(did, owner, mode, minimum, maximum, decline, visibility, options):
    return {'decisionId': did, 'ownerRef': owner, 'selectionMode': mode, 'cardinality': {'min': minimum, 'max': maximum}, 'declineAllowed': decline, 'visibility': visibility, 'options': options}


def operation(step, order, op_type, modality, subject, obj, sources, *, conditions=None, decision_ref=None, target_ref=None, transition=None, value_change=None, invoke=None, repeat=None, notes=None):
    return {'stepId': step, 'sequence': order, 'operationType': op_type, 'modality': modality, 'subjectRef': subject, 'objectRef': obj, 'conditionRefs': conditions or [], 'decisionRef': decision_ref, 'targetRef': target_ref, 'transition': transition, 'valueChange': value_change, 'invokeRuleId': invoke, 'repeat': repeat, 'sourceAssertionIds': sources, 'notes': notes}


def record(rule_id, title, status, rule_kind, authority_highest, authority_interpretation, source_assertions, term_refs, taxon_refs, named_refs, timing_value, participants, modality, preconditions, decisions, information, costs, targets, operations, partial, duration, stacking, outcomes, unresolved, variants):
    known_conditions = {item['conditionId'] for item in preconditions}
    generated_conditions = []
    for op in operations:
        normalized_refs = []
        for index, reference in enumerate(op['conditionRefs'], 1):
            if reference in known_conditions:
                normalized_refs.append(reference)
                continue
            condition_id = f"{op['stepId']}-C{index:02d}"
            generated_conditions.append(condition(condition_id, 'predicate', [{'predicate': reference}], op['sourceAssertionIds'], scope='operation-guard'))
            known_conditions.add(condition_id)
            normalized_refs.append(condition_id)
        op['conditionRefs'] = normalized_refs
    preconditions = [*preconditions, *generated_conditions]
    return {'ruleId':rule_id,'title':title,'status':status,'ruleKind':rule_kind,'applicability':{'game':'Nemesis: Retaliation','mode':'base-standard','playerCount':None},'authority':{'highest':authority_highest,'interpretation':authority_interpretation},'sourceAssertions':source_assertions,'termRefs':sorted(set(term_refs)),'taxonRefs':sorted(set(taxon_refs)),'namedIdentityRefs':sorted(set(named_refs)),'timing':timing_value,'participants':participants,'modality':modality,'preconditions':preconditions,'decisions':decisions,'informationPolicy':information,'costs':costs,'targets':targets,'operations':operations,'partialResolution':partial,'duration':duration,'stacking':stacking,'outcomes':outcomes,'unresolvedQuestionRefs':unresolved,'sourceVariants':variants,'implementationBoundary':'implementation-neutral; no engine, UI, network, storage, or serialization mapping'}

records = []

records.append(record(
    'SEM-RT-001','Round phase sequence','source-backed','sequence','official-primary','verbatim-structure',
    [assertion('SA-RT001-1','SRC-RULEBOOK','printed pages 12–15 / rulebook_text lines 2939–2986',['timing','operations'],'The game is played in a series of Rounds. Each Round contains Player, Intruder, Event, and Cleanup Phases in that order.','docs/rules/01-round-and-turns.md:RT-001')],
    ['term.round','term.player-phase','term.intruder-phase','term.event-phase','term.cleanup-phase'],
    ['tax.process.temporal.round','tax.process.temporal.phase.player','tax.process.temporal.phase.intruder','tax.process.temporal.phase.event','tax.process.temporal.phase.cleanup'],[],
    timing('TW-ROUND','tax.process.temporal.round','during','once-per-round'),[participant('P-RULES','rules-system')],'must',[],[],[{'informationId':'I-ROUND-STATE','subjectRef':'current phase/round','audience':'public','revealTrigger':'continuous','secrecy':'none'}],[],[],
    [operation('S01',1,'invoke-process','must','rules-system','Player Phase',['SA-RT001-1']),operation('S02',2,'invoke-process','must','rules-system','Intruder Phase',['SA-RT001-1']),operation('S03',3,'invoke-process','must','rules-system','Event Phase',['SA-RT001-1']),operation('S04',4,'invoke-process','must','rules-system','Cleanup Phase',['SA-RT001-1'])],
    {'policy':'ordered-complete','unit':'phase','onImpossible':'not-specified'}, {'kind':'round'}, {'policy':'not-applicable'}, [], [], []))

records.append(record(
    'SEM-RT-004','Player Phase rotation','source-backed','sequence','official-primary','verbatim-structure',
    [assertion('SA-RT004-1','SRC-RULEBOOK','printed page 13 / lines 2987–3004',['timing','operations','targets'],'During this Phase players take their Turns in clockwise order, beginning with the Starting Player. If a given player has Passed, they are skipped.','docs/rules/01-round-and-turns.md:RT-004')],
    ['term.player-phase','term.turn','term.turn-order','term.starting-player','term.pass'],['tax.process.temporal.phase.player','tax.process.temporal.turn','tax.value.turn-order','tax.role.starting-player'],[],
    timing('TW-PLAYER-PHASE','tax.process.temporal.phase.player','during','once-per-round'),[participant('P-RULES','rules-system'),participant('P-PLAYERS','collection','tax.entity.agent.player')],'must',
    [condition('C-ALL-PASSED','predicate',[{'predicate':'all eligible players have Passed'}],['SA-RT004-1'])],[],[{'informationId':'I-TURN-ORDER','subjectRef':'turn order and passed status','audience':'public','revealTrigger':'continuous','secrecy':'none'}],[],
    [{'targetId':'T-NEXT-PLAYER','selectorRef':'rules-system','eligibleTaxonIds':['tax.entity.agent.player'],'cardinality':{'min':1,'max':1},'selectionMode':'deterministic-turn-order','visibility':'public'}],
    [operation('S01',1,'set-state','must','rules-system','Turn-order cursor at Starting Player',['SA-RT004-1']),operation('S02',2,'invoke-process','must','next non-Passed Player','Turn',['SA-RT004-1'],target_ref='T-NEXT-PLAYER',repeat={'afterEach':'advance clockwise to next non-Passed Player','untilConditionRef':'C-ALL-PASSED'}),operation('S03',3,'invoke-process','must','rules-system','Intruder Phase',['SA-RT004-1'],conditions=['C-ALL-PASSED'])],
    {'policy':'ordered-complete','unit':'turn rotation','onImpossible':'skip players who have Passed'}, {'kind':'phase'}, {'policy':'not-applicable'}, [], [], []))

records.append(record(
    'SEM-RT-005','Player Turn','source-backed-with-open-question','sequence','official-primary','open-alternatives',
    [assertion('SA-RT005-1','SRC-RULEBOOK','printed pages 12–13 / lines 2854–2864, 2929–2934',['operations','decisions'],'Perform exactly two Actions, then resolve Oxygen loss, then Fire damage.','docs/rules/01-round-and-turns.md:RT-005'),assertion('SA-RT005-2','SRC-RULEBOOK','printed page 18 / death',['unresolvedQuestionRefs'],'A dead Character no longer takes part in the game.','docs/rules/open-questions.md:OQ-004')],
    ['term.turn','term.action','term.pass','icon.oxygen','icon.fire','icon.characterHealth'],['tax.process.temporal.turn','tax.process.action','tax.value.resource.oxygen','tax.entity.component.marker.fire'],[],
    timing('TW-TURN','tax.process.temporal.turn','during','once-per-player-turn'),[participant('P-ACTIVE-PLAYER','actor','tax.entity.agent.player'),participant('P-ACTIVE-CHARACTER','controlled-actor','tax.entity.agent.character')],'must',[],
    [decision('D-ACTION-1','P-ACTIVE-PLAYER','player-choice',1,1,False,'public-on-declaration',['any fully resolvable legal Action']),decision('D-ACTION-2','P-ACTIVE-PLAYER','player-choice',1,1,False,'public-on-declaration',['any fully resolvable legal Action, including Pass'])],
    [{'informationId':'I-HAND','subjectRef':'unselected hand cards','audience':'owner-private','revealTrigger':'source-specific play/discard','secrecy':'identities hidden from other players'}],[],[],
    [operation('S01',1,'invoke-selected-process','must','P-ACTIVE-CHARACTER','selected Action',['SA-RT005-1'],decision_ref='D-ACTION-1'),operation('S02',2,'invoke-selected-process','if-able','P-ACTIVE-CHARACTER','selected Action',['SA-RT005-1'],conditions=['current Player has not Passed and Character remains participating'],decision_ref='D-ACTION-2'),operation('S03',3,'change-value','if-able','P-ACTIVE-CHARACTER','Oxygen',['SA-RT005-1'],conditions=['Character is in a Section with inactive Life Support'],value_change={'amount':-1,'valueTaxonId':'tax.value.resource.oxygen'}),operation('S04',4,'change-value','if-able','P-ACTIVE-CHARACTER','Character Health',['SA-RT005-1'],conditions=['Character is in a Room with Fire'],value_change={'amount':-1,'valueTaxonId':'tax.state.health.point'})],
    {'policy':'ordered-complete','unit':'turn step','onImpossible':'Pass remains an Action option; mid-Turn death continuation is unresolved'}, {'kind':'turn'}, {'policy':'not-applicable'}, [], ['OQ-004'], []))

records.append(record(
    'SEM-RT-007','Pass Action','source-backed','action','official-primary','verbatim-structure',
    [assertion('SA-RT007-1','SRC-RULEBOOK','printed pages 13–14 / Passing',['decisions','operations','duration'],'A player may discard any number of Action and Contamination cards from hand; the Turn ends and the player is skipped for the rest of the Player Phase.','docs/rules/01-round-and-turns.md:RT-007')],
    ['term.pass','icon.actionCard','term.contamination-card'],['tax.process.action.pass','tax.entity.component.card.action','tax.entity.component.card.contamination'],[],
    timing('TW-PASS','tax.process.temporal.turn','during','once-when-chosen'),[participant('P-ACTIVE-PLAYER','actor','tax.entity.agent.player')],'may',[],
    [decision('D-DISCARD-SUBSET','P-ACTIVE-PLAYER','player-choice',0,None,True,'owner-private-until-discard',['any subset of Action and Contamination cards in own hand'])],
    [{'informationId':'I-PASS-HAND','subjectRef':'unselected hand cards','audience':'owner-private','revealTrigger':'never by Pass','secrecy':'identities hidden'},{'informationId':'I-PASS-DISCARDS','subjectRef':'selected discarded cards','audience':'public','revealTrigger':'discard','secrecy':'none'}],[],[],
    [operation('S01',1,'transition-zone','may','P-ACTIVE-PLAYER','selected cards',['SA-RT007-1'],decision_ref='D-DISCARD-SUBSET',transition={'from':'tax.scaffold.zone.hand','to':'tax.scaffold.zone.discard-pile'}),operation('S02',2,'set-state','must','P-ACTIVE-PLAYER','Passed for current Player Phase',['SA-RT007-1']),operation('S03',3,'end-action-window','must','P-ACTIVE-PLAYER','remaining Action opportunities in current Turn',['SA-RT007-1'],notes='Return to the parent Turn so mandatory oxygen loss and fire damage still resolve.')],
    {'policy':'all-or-nothing-selection','unit':'Pass Action','onImpossible':'not applicable; zero-card subset is legal'}, {'kind':'until-end-of-current-player-phase'}, {'policy':'one Passed state per Player Phase'}, [], [], []))

records.append(record(
    'SEM-ACT-MOVE-001','Move Action and Movement Sequence','source-backed','action','official-errata','source-composed',
    [assertion('SA-MOVE-1','SRC-RULEBOOK','printed pages 12 and 24–25',['costs','preconditions','targets','operations'],'Move costs 1 Action card; choose an adjacent Corridor, resolve opportunity attacks, resolve destination, then make a Noise roll.','docs/rules/02-character-actions.md:ACT-MOVE-001'),assertion('SA-MOVE-2','SRC-FAQ','Action cards #3',['outcomes'],'Attack prevention during Movement applies to opportunity attacks, not a Hazard-result attack.','docs/rules/02-character-actions.md:ACT-MOVE-001')],
    ['term.move','term.movement-sequence','term.opportunity-attack','term.noise-roll','term.corridor','term.room','term.closed'],['tax.process.action.move','tax.process.sequence.movement','tax.process.attack.opportunity','tax.entity.spatial.corridor','tax.entity.spatial.room','tax.state.closed'],[],
    timing('TW-MOVE','tax.process.temporal.turn','during','per-selected-Move'),[participant('P-ACTIVE-PLAYER','decision-owner','tax.entity.agent.player'),participant('P-MOVING-CHARACTER','actor','tax.entity.agent.character')],'must',
    [condition('C-LEGAL-CORRIDOR','all',[{'predicate':'Corridor is adjacent to origin Room'},{'predicate':'path is not blocked by a Closed Door'},{'predicate':'destination branch is fully resolvable'}],['SA-MOVE-1'])],
    [decision('D-PAYMENT','P-ACTIVE-PLAYER','player-choice',1,1,False,'owner-private-until-discard',['own Action cards in hand']),decision('D-CORRIDOR','P-ACTIVE-PLAYER','player-choice',1,1,False,'public-on-declaration',['adjacent Corridors satisfying C-LEGAL-CORRIDOR'])],
    [{'informationId':'I-MOVE-PAYMENT','subjectRef':'paid Action card identity','audience':'public','revealTrigger':'payment discard','secrecy':'none'}],
    [{'costId':'COST-MOVE','payerRef':'P-ACTIVE-PLAYER','resourceTermId':'icon.actionCard','quantity':1,'selectionDecisionRef':'D-PAYMENT','transition':{'from':'tax.scaffold.zone.hand','to':'tax.scaffold.zone.discard-pile'}}],
    [{'targetId':'T-CORRIDOR','selectorRef':'P-ACTIVE-PLAYER','eligibleTaxonIds':['tax.entity.spatial.corridor'],'cardinality':{'min':1,'max':1},'selectionMode':'player-choice','visibility':'public'}],
    [operation('S01',1,'pay-cost','must','P-ACTIVE-PLAYER','COST-MOVE',['SA-MOVE-1'],decision_ref='D-PAYMENT'),operation('S02',2,'select-target','must','P-ACTIVE-PLAYER','adjacent Corridor',['SA-MOVE-1'],decision_ref='D-CORRIDOR',target_ref='T-CORRIDOR'),operation('S03',3,'resolve-attacks','if-able','Intruders in origin Room and selected Corridor','P-MOVING-CHARACTER',['SA-MOVE-1'],repeat={'order':'largest-first','max':3}),operation('S04',4,'branch','must','rules-system','destination branch',['SA-MOVE-1'],conditions=['destination is Discovered Room OR destination is Undiscovered Room slot']),operation('S05',5,'move-entity','must','P-MOVING-CHARACTER','destination Room',['SA-MOVE-1'],conditions=['destination is Discovered Room']),operation('S06',6,'invoke-process','must','P-MOVING-CHARACTER','Exploration Sequence',['SA-MOVE-1'],conditions=['selected Corridor is Unexplored'],invoke='SEM-ACT-EXPLORE-001'),operation('S07',7,'invoke-process','must','P-MOVING-CHARACTER','Noise Roll',['SA-MOVE-1'],conditions=['movement completed'],notes='Occurs after every Movement unless an explicit special effect says otherwise.')],
    {'policy':'all-or-nothing-selection','unit':'Move Action','onImpossible':'Action may be selected only if fully resolvable'}, {'kind':'instantaneous-action'}, {'policy':'repeatable Action'}, [], [], []))

records.append(record(
    'SEM-ACT-EXPLORE-001','Exploration Sequence','source-backed','sequence','official-errata','source-composed',
    [assertion('SA-EXP-1','SRC-RULEBOOK','printed page 24 / Exploration Sequence',['timing','operations','partialResolution'],'Draw an Exploration card, set up Room/Corridors/markers, move Character, resolve Entrance Effect, discard card. Invalid additional Corridors are omitted.','docs/rules/02-character-actions.md:ACT-EXPLORE-001'),assertion('SA-EXP-2','SRC-FAQ','General rules #4–5',['operations','partialResolution'],'Close Doors applies only around the new Room; remove-from-game text is outside Entrance Effect.','docs/rules/02-character-actions.md:ACT-EXPLORE-001')],
    ['term.exploration-sequence','term.exploration-card','term.unexplored-corridor','term.undiscovered','term.discovered'],['tax.process.sequence.exploration','tax.entity.component.card.exploration','tax.state.corridor.unexplored','tax.state.discovery.undiscovered','tax.state.discovery.discovered'],[],
    timing('TW-EXPLORE','tax.process.sequence.movement','when-triggered','per-Unexplored-destination'),[participant('P-EXPLORER','actor','tax.entity.agent.character'),participant('P-RULES','rules-system')],'must',
    [condition('C-EXPLORE','all',[{'predicate':'Movement reaches an Unexplored Corridor'},{'predicate':'destination Room slot is empty and Undiscovered'}],['SA-EXP-1'])],[],[{'informationId':'I-EXPLORATION-CARD','subjectRef':'drawn Exploration card','audience':'public','revealTrigger':'draw','secrecy':'none'}],[],[],
    [operation('S01',1,'draw-random','must','P-RULES','top/random Exploration card',['SA-EXP-1']),operation('S02',2,'place-component','must','P-RULES','random Room of required A/B/C type; use ? if exhausted',['SA-EXP-1']),operation('S03',3,'place-component','if-able','P-RULES','each indicated Corridor',['SA-EXP-1'],notes='Omit a Corridor that would leave the Facility or connect to an already placed Room.'),operation('S04',4,'place-component','if-able','P-RULES','depicted markers/tokens',['SA-EXP-1']),operation('S05',5,'move-entity','must','P-EXPLORER','newly placed Room',['SA-EXP-1']),operation('S06',6,'invoke-process','if-able','P-RULES','Entrance Effect',['SA-EXP-1']),operation('S07',7,'transition-zone','must','P-RULES','Exploration card',['SA-EXP-1','SA-EXP-2'],transition={'from':'resolved-card','to':'discard-or-removed-as-printed'})],
    {'policy':'source-conditional-steps','unit':'indicated Corridor/marker and sentence','onImpossible':'Omit only source-defined invalid Corridors; remove-from-game instruction still resolves when Entrance Effect is ignored'}, {'kind':'instantaneous-sequence'}, {'policy':'not-applicable'}, [], [], []))

records.append(record(
    'SEM-ACT-SEARCH-001','Search Action-card effect','source-backed','component-effect','official-primary','source-composed',
    [assertion('SA-SEARCH-1','SRC-RULEBOOK','printed page 28 / lines 4849–4865',['preconditions','decisions','informationPolicy','operations'],'Draw 1 Item for each Item Icon, keep 1, put the rest on the bottoms of their respective decks, and do not reveal unchosen Items.','docs/rules/02-character-actions.md:ACT-SEARCH-001'),assertion('SA-SEARCH-2','SRC-CARD-SEARCH-MEDICAL','exact card face',['timing','operations','sourceVariants'],'For each Item Icon in your Room draw 1 Item of the corresponding type. You may keep 1 of them and discard the rest.','assets/tts-mod/extract/card-text-corpus.json'),assertion('SA-SEARCH-3','SRC-RULEBOOK','printed page 13 / Playing Action Cards',['operations'],'After resolving an Action card, discard that card.','docs/rules/02-character-actions.md:ACT-CARD-001')],
    ['term.search','term.item','term.room','term.backpack','term.hand-slot','term.armor-item','icon.notInCombat'],['tax.process.card-effect.search','tax.entity.component.card.item','tax.entity.spatial.room','tax.scaffold.zone.backpack','tax.entity.component.slot.hand','tax.entity.component.card.item.armor','tax.state.combat.not-in-combat'],['NI-0426'],
    timing('TW-SEARCH','tax.process.action.basic','when-action-card-played','per-played-Search-card'),[participant('P-SEARCHER','actor','tax.entity.agent.character'),participant('P-OWNER','decision-owner','tax.entity.agent.player')],'must',
    [condition('C-SEARCH-LEGAL','all',[{'predicate':'Searcher is Not In Combat'},{'predicate':'Room has at least 1 Item Icon'},{'predicate':'the draw/keep/return sequence is fully resolvable'}],['SA-SEARCH-1','SA-SEARCH-2'])],
    [decision('D-KEEP-ITEM','P-OWNER','player-choice',1,1,False,'owner-private',['drawn Item cards'])],
    [{'informationId':'I-SEARCH-CANDIDATES','subjectRef':'drawn Item identities','audience':'owner-private','revealTrigger':'chosen Item enters a public area or is used','secrecy':'unchosen Items must not be revealed'},{'informationId':'I-BACKPACK-ITEM','subjectRef':'chosen Regular Item in Backpack','audience':'owner-private','revealTrigger':'use or source-defined reveal','secrecy':'Backpack contents hidden'}],[],
    [{'targetId':'T-KEPT-ITEM','selectorRef':'P-OWNER','eligibleTaxonIds':['tax.entity.component.card.item'],'cardinality':{'min':1,'max':1},'selectionMode':'player-choice','visibility':'owner-private'}],
    [operation('S01',1,'draw-random','must','P-SEARCHER','1 Item from corresponding deck per Room Item Icon',['SA-SEARCH-1']),operation('S02',2,'select-target','must','P-OWNER','one drawn Item',['SA-SEARCH-1'],decision_ref='D-KEEP-ITEM',target_ref='T-KEPT-ITEM'),operation('S03',3,'transition-zone','must','P-OWNER','chosen Item',['SA-SEARCH-1'],transition={'from':'temporary-private-inspection','to':'Backpack, Hand slot, or Armor position according to Item class'}),operation('S04',4,'transition-zone','must','P-OWNER','each unchosen Item',['SA-SEARCH-1'],transition={'from':'temporary-private-inspection','to':'bottom of its respective deck'}),operation('S05',5,'transition-zone','must','P-OWNER','played Search Action card',['SA-SEARCH-2','SA-SEARCH-3'],transition={'from':'tax.scaffold.zone.hand','to':'tax.scaffold.zone.discard-pile'})],
    {'policy':'all-or-nothing-selection','unit':'Search effect','onImpossible':'Action/card effect may be selected only if fully resolvable'}, {'kind':'instantaneous-card-effect'}, {'policy':'one chosen Item; unchosen returns are independent per deck'}, [], [],
    [{'variantId':'SV-SEARCH-CARD-SHORTHAND','sourceId':'SRC-CARD-SEARCH-MEDICAL','difference':'Card says discard the rest; higher-authority rulebook defines discard here as bottom of respective decks and prohibits revealing unchosen Items.','resolution':'official-primary rulebook controls general Search procedure while exact card wording remains preserved'}]))

records.append(record(
    'SEM-ACT-REST-001','Rest card modifier over Infection Procedure','source-backed','component-effect','official-primary','source-composed',
    [assertion('SA-REST-1','SRC-CARD-REST','exact card face',['preconditions','operations','sourceVariants'],'Resolve the Infection Procedure. Remove all Uninfected cards from the game.','assets/tts-mod/extract/card-text-corpus.json'),assertion('SA-REST-2','SRC-RULEBOOK','printed page 38 / lines 6079–6098',['operations'],'Scan all Contamination cards in hand; place a Larva if any is Infected and none is present; place Contaminations on top of discard pile.','docs/rules/03-intruders-and-survival.md:INT-008'),assertion('SA-REST-3','SRC-RULEBOOK','printed page 13 / Playing Action Cards',['operations'],'After resolving an Action card, discard that card.','docs/rules/02-character-actions.md:ACT-CARD-001')],
    ['term.infection-procedure','term.contamination-card','term.infected','icon.notInCombat'],['tax.process.procedure.infection','tax.entity.component.card.contamination','tax.state.infection.infected','tax.state.combat.not-in-combat'],['NI-0410'],
    timing('TW-REST','tax.process.action.basic','when-action-card-played','per-played-Rest-card'),[participant('P-RESTING','actor','tax.entity.agent.character'),participant('P-OWNER','controller','tax.entity.agent.player')],'must',
    [condition('C-REST-LEGAL','all',[{'predicate':'Character is Not In Combat'},{'predicate':'Rest/Infection sequence is fully resolvable'}],['SA-REST-1','SA-REST-2'])],[],
    [{'informationId':'I-SCAN','subjectRef':'hidden Contamination text/result','audience':'scanning-player','revealTrigger':'scan instruction','secrecy':'hidden before scan; post-scan disclosure is not specified by the checked source'}],[],[],
    [operation('S01',1,'inspect-private','must','P-OWNER','all Contamination cards in hand',['SA-REST-2']),operation('S02',2,'evaluate-condition','must','P-OWNER','exact word INFECTED on each scanned card',['SA-REST-2']),operation('S03',3,'place-component','if-able','P-RESTING','1 Larva on Character board',['SA-REST-2'],conditions=['at least one scanned card is Infected','Character board has no Larva']),operation('S04',4,'transition-zone','must','P-OWNER','all scanned Uninfected Contamination cards',['SA-REST-1'],transition={'from':'tax.scaffold.zone.hand','to':'tax.scaffold.zone.removed-from-game'}),operation('S05',5,'transition-zone','must','P-OWNER','remaining Infected Contamination cards',['SA-REST-2'],transition={'from':'tax.scaffold.zone.hand','to':'top of tax.scaffold.zone.discard-pile'}),operation('S06',6,'transition-zone','must','P-OWNER','played Rest Action card',['SA-REST-1','SA-REST-3'],transition={'from':'tax.scaffold.zone.hand','to':'tax.scaffold.zone.discard-pile'})],
    {'policy':'all-or-nothing-selection','unit':'Rest card effect','onImpossible':'card may be selected only if fully resolvable'}, {'kind':'instantaneous-card-effect'}, {'policy':'non-Infected removal replaces normal Infection Procedure discard destination for those cards'}, [], [],
    [{'variantId':'SV-REST-MEDICAL','sourceId':'SRC-CARD-REST-MEDICAL','difference':'Medical Support source face says non-Infected and “instead of discarding them”; exact punctuation and footer remain separate.','resolution':'pilot encodes only the reviewed canonical source tuple plus the official Procedure; the Medical Support variant is not substituted'}]))

records.append(record(
    'SEM-REACTION-DUCK-001','Duck and Cover Reaction redirect','source-backed-with-open-question','reaction','official-primary','open-alternatives',
    [assertion('SA-DUCK-1','SRC-CARD-DUCK','Reaction panel',['timing','preconditions','targets','operations'],'When you would be Attacked by an Intruder in a Room with another Character: The Intruder Attacks the other Character instead.','assets/tts-mod/extract/card-text-corpus.json'),assertion('SA-DUCK-2','SRC-RULEBOOK','printed pages 13–14 / Reactions',['timing','duration'],'A player may use a Reaction when its condition is met; resolve it, then discard the card; it is not an Action.','docs/rules/01-round-and-turns.md:RT-003')],
    ['term.reaction','term.attack','icon.intruder','icon.character'],['tax.process.card-effect.reaction','tax.process.attack','tax.entity.agent.intruder','tax.entity.agent.character'],[],
    timing('TW-DUCK','tax.process.attack','before-attack-resolution','when-trigger-condition-met'),[participant('P-ORIGINAL-TARGET','actor','tax.entity.agent.character'),participant('P-OWNER','decision-owner','tax.entity.agent.player'),participant('P-INTRUDER','affected','tax.entity.agent.intruder')],'may',
    [condition('C-DUCK','all',[{'predicate':'P-ORIGINAL-TARGET would be Attacked by P-INTRUDER'},{'predicate':'same Room contains at least one other Character'}],['SA-DUCK-1'])],
    [decision('D-USE-REACTION','P-OWNER','player-choice',0,1,True,'public-on-play',['decline','play Duck and Cover'])],
    [{'informationId':'I-REACTION-CARD','subjectRef':'Duck and Cover identity','audience':'public','revealTrigger':'play','secrecy':'hidden in hand before play'}],[],
    [{'targetId':'T-OTHER-CHARACTER','selectorRef':'unresolved-by-source-when-multiple','eligibleTaxonIds':['tax.entity.agent.character'],'cardinality':{'min':1,'max':1},'selectionMode':'unresolved-when-multiple','visibility':'public'}],
    [operation('S01',1,'play-card','may','P-OWNER','Duck and Cover',['SA-DUCK-1','SA-DUCK-2'],decision_ref='D-USE-REACTION'),operation('S02',2,'replace-target','must','P-INTRUDER','T-OTHER-CHARACTER',['SA-DUCK-1'],conditions=['Reaction played'],target_ref='T-OTHER-CHARACTER'),operation('S03',3,'invoke-process','must','P-INTRUDER','Intruder Attack against replacement target',['SA-DUCK-1'],conditions=['Reaction played']),operation('S04',4,'transition-zone','must','P-OWNER','Duck and Cover card',['SA-DUCK-2'],conditions=['Reaction played'],transition={'from':'tax.scaffold.zone.hand','to':'tax.scaffold.zone.discard-pile'})],
    {'policy':'replacement-effect','unit':'one pending Attack','onImpossible':'source does not specify replacement selection when multiple other Characters exist'}, {'kind':'one-pending-attack'}, {'policy':'one Reaction card play per copy'}, [], ['SEM-Q-001'], []))

records.append(record(
    'SEM-ROOM-01','Sprinklers Control Room effect','source-backed','component-effect','official-primary','verbatim-structure',
    [assertion('SA-ROOM01-1','SRC-ROOM-HELP','entry 01 SPRINKLERS CONTROL',['decisions','targets','operations'],'Discard all Fire markers from a chosen Section.','docs/rules/source-extraction/room-help-sheet.json:01'),assertion('SA-ROOM01-2','SRC-RULEBOOK','printed page 12 / Basic Actions List',['costs','preconditions'],'Use the Room costs 2 Action cards and carries Not In Combat.','docs/rules/source-extraction/rulebook-visual-obligations.json:RB-P12-V02')],
    ['term.use-the-room','term.section','icon.fire','icon.notInCombat'],['tax.process.action.use-room','tax.entity.spatial.section','tax.entity.component.marker.fire','tax.state.combat.not-in-combat'],['NI-0447'],
    timing('TW-ROOM01','tax.process.action.use-room','during','per-Use-Room'),[participant('P-ACTIVE-PLAYER','decision-owner','tax.entity.agent.player'),participant('P-ACTIVE-CHARACTER','actor','tax.entity.agent.character')],'must',
    [condition('C-ROOM01','all',[{'predicate':'Character occupies Sprinklers Control'},{'predicate':'Character is Not In Combat'},{'predicate':'effect is fully resolvable'}],['SA-ROOM01-1','SA-ROOM01-2'])],
    [decision('D-ROOM01-PAY','P-ACTIVE-PLAYER','player-choice',2,2,False,'owner-private-until-discard',['own Action cards in hand']),decision('D-SECTION','P-ACTIVE-PLAYER','player-choice',1,1,False,'public-on-declaration',['Section A','Section B','Section C'])],
    [{'informationId':'I-ROOM01','subjectRef':'selected Section and Fire markers','audience':'public','revealTrigger':'declaration','secrecy':'none'}],
    [{'costId':'COST-ROOM01','payerRef':'P-ACTIVE-PLAYER','resourceTermId':'icon.actionCard','quantity':2,'selectionDecisionRef':'D-ROOM01-PAY','transition':{'from':'tax.scaffold.zone.hand','to':'tax.scaffold.zone.discard-pile'}}],
    [{'targetId':'T-SECTION','selectorRef':'P-ACTIVE-PLAYER','eligibleTaxonIds':['tax.entity.spatial.section'],'cardinality':{'min':1,'max':1},'selectionMode':'player-choice','visibility':'public'}],
    [operation('S01',1,'pay-cost','must','P-ACTIVE-PLAYER','COST-ROOM01',['SA-ROOM01-2'],decision_ref='D-ROOM01-PAY'),operation('S02',2,'select-target','must','P-ACTIVE-PLAYER','one Section',['SA-ROOM01-1'],decision_ref='D-SECTION',target_ref='T-SECTION'),operation('S03',3,'remove-component','must','rules-system','all Fire markers in selected Section',['SA-ROOM01-1'],target_ref='T-SECTION',repeat={'scope':'all matching markers'})],
    {'policy':'all-or-nothing-selection','unit':'Use Room Action','onImpossible':'Action may be selected only if fully resolvable'}, {'kind':'instantaneous-room-effect'}, {'policy':'repeatable via separate Actions'}, [], [], []))

records.append(record(
    'SEM-EVENT-HATCHING-001','Hatching Event resolution','source-backed-with-open-question','event','official-primary','open-alternatives',
    [assertion('SA-HATCH-1','SRC-EVENT-HATCHING','canonical Event face',['operations','unresolvedQuestionRefs'],'All Intruders in each NE–SW Corridor move. Place a Larva in the Nest; place 1 Larva in each Unexplored Corridor adjacent to a Character. Resolve each Noise in Unexplored Corridors.','assets/tts-mod/extract/card-text-corpus.json'),assertion('SA-HATCH-2','SRC-RULEBOOK','printed page 15 / Event card resolution',['timing','partialResolution'],'Resolve movement, main effect, secondary effect, then discard; ignore an impossible sentence and continue.','docs/rules/01-round-and-turns.md:RT-009')],
    ['term.event-card','icon.corridorNESW','term.nest','term.unexplored-corridor','icon.noise','term.noise-roll'],['tax.entity.component.card.event','tax.value.orientation','tax.entity.spatial.room.nest','tax.state.corridor.unexplored','tax.entity.component.marker.noise'],[],
    timing('TW-HATCH','tax.process.temporal.phase.event','during-event-card-resolution','when-drawn'),[participant('P-RULES','rules-system')],'must',[],[],[{'informationId':'I-EVENT','subjectRef':'drawn Event card and all results','audience':'public','revealTrigger':'draw','secrecy':'none'}],[],[],
    [operation('S01',1,'move-entity','if-able','each Intruder in NE–SW Corridors','toward closest Character',['SA-HATCH-1','SA-HATCH-2'],repeat={'order':'source Event movement order'}),operation('S02',2,'place-component','if-able','rules-system','1 Larva in the Nest',['SA-HATCH-1'],notes='If a Character is there, the entry immediately Attacks.'),operation('S03',3,'place-component','if-able','rules-system','1 Larva in each Unexplored Corridor adjacent to a Character',['SA-HATCH-1'],repeat={'scope':'each matching Corridor'}),operation('S04',4,'invoke-process','if-able','rules-system','each existing Noise marker in Unexplored Corridors',['SA-HATCH-1'],repeat={'order':'Facility top-left row by row'}),operation('S05',5,'transition-zone','must','rules-system','Hatching Event card',['SA-HATCH-2'],transition={'from':'resolved Event','to':'tax.scaffold.zone.discard-pile'})],
    {'policy':'per-sentence-continue','unit':'Event-card sentence','onImpossible':'ignore only the impossible sentence and continue the card'}, {'kind':'instantaneous-event-resolution'}, {'policy':'not-applicable'}, [], ['OQ-009'], []))

records.append(record(
    'SEM-INTRUDER-HELP-QA-R01','Queen Alive token resolved in a Room','source-backed','dispatcher','official-primary','verbatim-structure',
    [assertion('SA-IH-QA-R01','SRC-INTRUDER-HELP-QA','queen-alive / room / QA-R-01',['preconditions','operations'],'Activate the Queen. If not possible – place her in the Room.','docs/rules/source-extraction/intruder-help-sheet.json:QA-R-01'),assertion('SA-IH-CONTEXT','SRC-RULEBOOK','printed pages 25, 30, 35',['timing'],'Resolve the drawn token in the context directed by the caller/Help Sheet column.','docs/rules/03-intruders-and-survival.md:INT-001')],
    ['term.queen','term.room'],['tax.entity.agent.intruder.queen','tax.entity.spatial.room'],[],
    timing('TW-IH-QA-R01','tax.process.sequence.noise-roll','when-triggered','per-drawn-Queen-token-in-Room-context'),[participant('P-RULES','rules-system')],'must',
    [condition('C-IH-SIDE','predicate',[{'predicate':'Intruder Help side is Queen Alive'}],['SA-IH-QA-R01']),condition('C-IH-CONTEXT','predicate',[{'predicate':'caller requests Room context'}],['SA-IH-CONTEXT'])],[],[{'informationId':'I-DRAWN-TOKEN','subjectRef':'drawn Intruder token and resolved result','audience':'public','revealTrigger':'draw','secrecy':'none'}],[],[],
    [operation('S01',1,'invoke-process','if-able','Queen','Activate Queen',['SA-IH-QA-R01']),operation('S02',2,'place-component','must','rules-system','Queen in caller-supplied Room',['SA-IH-QA-R01'],conditions=['Queen activation is not possible'])],
    {'policy':'if-not-possible-fallback','unit':'Help Sheet row','onImpossible':'use the printed placement fallback'}, {'kind':'instantaneous-dispatch-row'}, {'policy':'one row per token/context'}, [], [], []))

records.append(record(
    'SEM-ENDGAME-001','End-of-game triggers and checks','source-backed-with-open-question','endgame','official-errata','open-alternatives',
    [assertion('SA-END-1','SRC-RULEBOOK','printed page 39 / lines 6238–6273',['preconditions','operations','outcomes','unresolvedQuestionRefs'],'Game ends at Round 14, when all players are dead/Escaped/Hibernated, or Facility destruction; then resolve Infection, Eclosion, Objective reveal/check, and winners.','docs/rules/03-intruders-and-survival.md:INT-011'),assertion('SA-END-2','SRC-FAQ','General rules #3',['operations'],'Pending Autodestruction happens before the endgame sequence.','docs/rules/03-intruders-and-survival.md:INT-010')],
    ['term.end-of-the-game','term.infection-procedure','term.eclosion-procedure','term.objective','term.fulfilled','term.survivor'],['tax.process.procedure.endgame','tax.process.procedure.infection','tax.process.procedure.eclosion','tax.entity.information.objective','tax.state.objective.fulfilled','tax.state.participation.survivor'],[],
    timing('TW-ENDGAME','tax.process.procedure.endgame','when-triggered','once-per-game'),[participant('P-RULES','rules-system'),participant('P-CHARACTERS','collection','tax.entity.agent.character'),participant('P-PLAYERS','collection','tax.entity.agent.player')],'must',
    [condition('C-END-TRIGGER','any',[{'predicate':'Round 14 ends'},{'predicate':'all players died, Escaped, or Hibernated'},{'predicate':'Facility is Destroyed'}],['SA-END-1'])],
    [decision('D-LATE-OBJECTIVE','P-PLAYERS','player-choice',1,1,False,'owner-private-until-reveal',['each still-alive eligible Player chooses from their two Objective cards'])],
    [{'informationId':'I-OBJECTIVES','subjectRef':'unselected/chosen Objective identities','audience':'owner-private','revealTrigger':'endgame Objective check','secrecy':'hidden until reveal'},{'informationId':'I-END-RESULT','subjectRef':'survival and winners','audience':'public','revealTrigger':'resolution','secrecy':'none'}],[],[],
    [operation('S01',1,'invoke-process','if-able','rules-system','pending Autodestruction',['SA-END-2']),operation('S02',2,'set-state','if-able','onboard Characters at Round-14 expiry','dead',['SA-END-1'],conditions=['Round 14 trigger']),operation('S03',3,'invoke-process','must','each alive Escaped/Hibernated Character without Larva','Infection Procedure',['SA-END-1']),operation('S04',4,'invoke-process','must','each alive Escaped/Hibernated Character currently with Larva','Eclosion Procedure',['SA-END-1'],notes='Whether “currently” includes a Larva gained in S03 is OQ-002.'),operation('S05',5,'choose','if-able','each still-alive Player lacking chosen Objective','one Objective',['SA-END-1'],decision_ref='D-LATE-OBJECTIVE'),operation('S06',6,'reveal','must','each still-alive Character','chosen Objective',['SA-END-1']),operation('S07',7,'evaluate-condition','must','each still-alive Character','Objective fulfilled',['SA-END-1']),operation('S08',8,'set-state','if-able','Character with fulfilled Objective','winner',['SA-END-1'])],
    {'policy':'ordered-complete','unit':'endgame sequence step','onImpossible':'source-specific; unresolved iteration questions remain explicit'}, {'kind':'end-of-game'}, {'policy':'once per game'}, [{'condition':'Character remains alive and chosen Objective is Fulfilled','result':'wins'}], ['OQ-001','OQ-002'], []))

records.sort(key=lambda item: item['ruleId'])

semantic_questions = {
    'schemaVersion':1,'recordType':'semantic-review-gates','status':'pilot built with deferred questions; no default answer adopted',
    'counts':{'questions':7,'officialClarificationPreferred':6,'sourceAmbiguitiesIntroducedByPilot':1,'resolved':0,'open':7},
    'questions':[
        {'questionId':'OQ-001','title':'Eclosion existing-hand behavior','decisionClass':'official-clarification-preferred','blocksRuleIds':['SEM-ENDGAME-001'],'defaultProhibited':True},
        {'questionId':'OQ-002','title':'Endgame Larva iteration timing','decisionClass':'official-clarification-preferred','blocksRuleIds':['SEM-ENDGAME-001'],'defaultProhibited':True},
        {'questionId':'OQ-003','title':'Starting Player token passing over nonparticipants','decisionClass':'official-clarification-preferred','blocksRuleIds':['future Cleanup semantic record'],'defaultProhibited':True},
        {'questionId':'OQ-004','title':'Player Phase recalculation after mid-Turn death','decisionClass':'official-clarification-preferred','blocksRuleIds':['SEM-RT-005'],'defaultProhibited':True},
        {'questionId':'OQ-007','title':'Secure tokens and simultaneous multi-Intruder entry','decisionClass':'official-clarification-preferred','blocksRuleIds':['future Secure semantic record'],'defaultProhibited':True},
        {'questionId':'OQ-009','title':'Nest placement before discovery','decisionClass':'official-clarification-preferred','blocksRuleIds':['SEM-EVENT-HATCHING-001'],'defaultProhibited':True},
        {'questionId':'SEM-Q-001','title':'Duck and Cover replacement target when multiple other Characters share the Room','decisionClass':'source-ambiguity-owner-decision-after-source-search','blocksRuleIds':['SEM-REACTION-DUCK-001'],'defaultProhibited':True},
    ],
}

pilot = {
    'schemaVersion':1,'recordType':'semantic-rule-pilot-corpus','schemaPath':'docs/rules/semantics/semantic-rule.schema.json',
    'scope':'base-game representative pilot; not full semantic coverage',
    'counts':{'records':len(records),'sourceBacked':sum(r['status']=='source-backed' for r in records),'withOpenQuestion':sum(r['status']=='source-backed-with-open-question' for r in records),'sourceVariants':sum(r['status']=='source-variant' for r in records),'sourceAssertions':sum(len(r['sourceAssertions']) for r in records),'conditions':sum(len(r['preconditions']) for r in records),'operations':sum(len(r['operations']) for r in records),'decisions':sum(len(r['decisions']) for r in records),'informationPolicies':sum(len(r['informationPolicy']) for r in records),'costs':sum(len(r['costs']) for r in records),'targets':sum(len(r['targets']) for r in records),'openQuestionReferences':sum(len(r['unresolvedQuestionRefs']) for r in records),'variantReferences':sum(len(r['sourceVariants']) for r in records)},
    'records':records,
}
coverage = {
    'schemaVersion':1,'recordType':'semantic-pilot-coverage','status':'representative pilot only',
    'systems':[
        {'system':'round/phase/turn','ruleIds':['SEM-RT-001','SEM-RT-004','SEM-RT-005','SEM-RT-007']},
        {'system':'movement/exploration','ruleIds':['SEM-ACT-MOVE-001','SEM-ACT-EXPLORE-001']},
        {'system':'private search/zone handling','ruleIds':['SEM-ACT-SEARCH-001']},
        {'system':'infection/card modifier','ruleIds':['SEM-ACT-REST-001']},
        {'system':'reaction/replacement target','ruleIds':['SEM-REACTION-DUCK-001']},
        {'system':'Room effect','ruleIds':['SEM-ROOM-01']},
        {'system':'Event partial resolution','ruleIds':['SEM-EVENT-HATCHING-001']},
        {'system':'Intruder Help dispatcher','ruleIds':['SEM-INTRUDER-HELP-QA-R01']},
        {'system':'endgame/open alternatives','ruleIds':['SEM-ENDGAME-001']},
    ],
    'counts':{'systems':9,'pilotRecords':len(records),'fullBaseSemanticCoverageClaimed':False},
    'notYetCovered':['complete card corpus','all 25 Room effects','all 20 Events','all Intruder Help rows','all Objectives/Mission Tasks','all Item/Robot/Attack/Queen Health/Serious Wound effects','remaining general rules and procedures'],
}

write('source-registry.json', source_registry)
write('semantic-rule.schema.json', semantic_schema)
write('pilots.json', pilot)
write('review-gates.json', semantic_questions)
write('coverage.json', coverage)
print(json.dumps({'sources':source_registry['counts'],'pilots':pilot['counts'],'questions':semantic_questions['counts'],'coverage':coverage['counts']},indent=2))
