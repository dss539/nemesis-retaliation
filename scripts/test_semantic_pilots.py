#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path
import unittest

REPO=Path(__file__).resolve().parents[1]
DIR=REPO/'docs/rules/semantics'
VALIDATOR=REPO/'scripts/validate_semantic_pilots.py'
FILES=('event-source-index.json','exploration-source-index.json','robot-source-index.json','attack-source-index.json','queen-health-source-index.json','source-registry.json','semantic-rule.schema.json','semantic-vocabulary.json','room-icon-denotations.json','pilots.json','review-gates.json','contradictions.json','coverage.json','backlog.json')


def load(path): return json.loads(path.read_text(encoding='utf-8'))


class SemanticPilotTests(unittest.TestCase):
    def run_validator(self, root=None, skip=False):
        base=root or DIR
        command=['python3',str(VALIDATOR),'--event-source-index',str(base/'event-source-index.json'),'--exploration-source-index',str(base/'exploration-source-index.json'),'--robot-source-index',str(base/'robot-source-index.json'),'--attack-source-index',str(base/'attack-source-index.json'),'--queen-health-source-index',str(base/'queen-health-source-index.json'),'--source-registry',str(base/'source-registry.json'),'--schema',str(base/'semantic-rule.schema.json'),'--semantic-vocabulary',str(base/'semantic-vocabulary.json'),'--room-icon-denotations',str(base/'room-icon-denotations.json'),'--pilots',str(base/'pilots.json'),'--review-gates',str(base/'review-gates.json'),'--contradictions',str(base/'contradictions.json'),'--coverage',str(base/'coverage.json'),'--backlog',str(base/'backlog.json')]
        if skip: command.append('--skip-reproducibility')
        run=subprocess.run(command,cwd=REPO,check=False,capture_output=True,text=True,timeout=300)
        return run,json.loads(run.stdout)

    def test_current_pilot_passes_and_rebuilds(self):
        run,report=self.run_validator()
        self.assertEqual(run.returncode,0,run.stdout+run.stderr)
        self.assertTrue(report['passed'])
        self.assertEqual(report['checks']['records'],167)
        self.assertEqual(report['checks']['operations'],773)
        self.assertEqual(report['checks']['decisions'],80)
        self.assertEqual(report['checks']['targets'],203)
        self.assertEqual(report['checks']['openQuestions'],35)
        self.assertEqual(report['checks']['semanticNodes'],26)
        self.assertEqual(report['checks']['conflicts'],22)
        self.assertEqual(report['checks']['backlogUnits'],600)
        self.assertEqual(report['checks']['backlogPilotCovered'],174)
        self.assertEqual(report['checks']['eventIdentities'],20)
        self.assertEqual(report['checks']['eventRecords'],20)
        self.assertEqual(report['checks']['eventBacklogTuples'],20)
        self.assertEqual(report['checks']['explorationIdentities'],12)
        self.assertEqual(report['checks']['explorationRecords'],12)
        self.assertEqual(report['checks']['explorationPrintedSentences'],46)
        self.assertEqual(report['checks']['explorationIconOccurrences'],60)
        self.assertEqual(report['checks']['explorationBacklogTuples'],12)
        self.assertEqual(report['checks']['robotIdentities'],6)
        self.assertEqual(report['checks']['robotRecords'],6)
        self.assertEqual(report['checks']['robotPhysicalPanels'],24)
        self.assertEqual(report['checks']['robotPrintedSentences'],16)
        self.assertEqual(report['checks']['robotIconOccurrences'],23)
        self.assertEqual(report['checks']['robotBacklogTuples'],6)
        self.assertEqual(report['checks']['attackIdentities'],20)
        self.assertEqual(report['checks']['attackRecords'],20)
        self.assertEqual(report['checks']['attackPhysicalPanels'],69)
        self.assertEqual(report['checks']['attackPrintedSentences'],54)
        self.assertEqual(report['checks']['attackBadgeOccurrences'],57)
        self.assertEqual(report['checks']['attackInlineIconOccurrences'],13)
        self.assertEqual(report['checks']['attackBacklogTuples'],20)
        self.assertEqual(report['checks']['queenHealthPhysicalOccurrences'],12)
        self.assertEqual(report['checks']['queenHealthUniqueFaceAssets'],10)
        self.assertEqual(report['checks']['queenHealthPhysicalPanels'],24)
        self.assertEqual(report['checks']['queenHealthPrintedSentences'],37)
        self.assertEqual(report['checks']['queenHealthFunctionalIconOccurrences'],28)
        self.assertEqual(report['checks']['queenHealthRecords'],12)
        self.assertEqual(report['checks']['queenHealthBacklogTuples'],10)
        self.assertEqual(report['checks']['roomIconDenotations'],112)

    def test_high_risk_semantic_boundaries(self):
        pilots=load(DIR/'pilots.json'); by_id={r['ruleId']:r for r in pilots['records']}
        search_steps={item['stepId']:item for item in by_id['SEM-ACT-SEARCH-001']['operations']}
        self.assertEqual(search_steps['S04']['transition']['to'],'tax.scaffold.zone.deck')
        self.assertEqual(search_steps['S04']['transition']['positionRef'],'sem.position.deck-bottom')
        self.assertIn('unchosen Items must not be revealed',json.dumps(by_id['SEM-ACT-SEARCH-001']))
        self.assertEqual(by_id['SEM-EVENT-HATCHING-001']['partialResolution']['policy'],'per-sentence-continue')
        self.assertIn('OQ-009',by_id['SEM-EVENT-HATCHING-001']['unresolvedQuestionRefs'])
        self.assertEqual(by_id['SEM-REACTION-DUCK-001']['ruleKind'],'reaction')
        self.assertIn('SEM-Q-001',by_id['SEM-REACTION-DUCK-001']['unresolvedQuestionRefs'])
        self.assertIn('SEM-Q-002',by_id['SEM-ACT-EXPLORE-001']['unresolvedQuestionRefs'])
        self.assertIn('SEM-Q-003',by_id['SEM-ACT-MOVE-001']['unresolvedQuestionRefs'])
        self.assertTrue(any(item['operationType']=='resolve-open-alternative' for item in by_id['SEM-ACT-EXPLORE-001']['operations']))
        self.assertTrue(any(item['operationType']=='end-action-window' for item in by_id['SEM-RT-007']['operations']))
        self.assertFalse(any(item.get('operationType')=='end-process' for item in by_id['SEM-RT-007']['operations']))
        self.assertTrue(all(r['implementationBoundary'].startswith('implementation-neutral') for r in pilots['records']))
        self.assertEqual({item.get('invokeRuleId') for item in by_id['SEM-RT-011']['operations'] if item.get('invokeRuleId')},{'SEM-IH-QA-B-01','SEM-IH-QD-B-01','SEM-IH-QA-B-02','SEM-IH-QD-B-02','SEM-IH-QA-B-03','SEM-IH-QD-B-03','SEM-IH-QA-BOTTOM-01','SEM-IH-QD-BOTTOM-01'})
        self.assertIn('dispatchRuleIds',json.dumps(by_id['SEM-NOISE-HAZARD-001']))
        self.assertIn('dispatchRuleIds',json.dumps(by_id['SEM-NOISE-MARKER-001']))

    def test_cross_cutting_general_rule_boundaries(self):
        by_id={r['ruleId']:r for r in load(DIR/'pilots.json')['records']}
        self.assertEqual([item['invokeRuleId'] for item in by_id['SEM-RT-009']['operations']],['SEM-EVENT-GENERAL-001','SEM-RT-011'])
        self.assertEqual(by_id['SEM-EVENT-GENERAL-001']['partialResolution']['policy'],'per-sentence-continue')
        self.assertIn('OQ-003',by_id['SEM-RT-012']['unresolvedQuestionRefs'])
        self.assertTrue(any(item['objectRef']=='sem.state.participation.dead' for item in by_id['SEM-INT-006']['operations']))
        self.assertTrue(any('Noise markers may still be placed/discarded' in item['objectRef'] for item in by_id['SEM-DOOR-001']['operations']))

    def test_intruder_help_semantic_closure(self):
        source=load(REPO/'docs/rules/source-extraction/intruder-help-sheet.json')
        by_id={r['ruleId']:r for r in load(DIR/'pilots.json')['records']}
        occurrences=[]
        for side in source['sides']:
            occurrences.extend(row['occurrenceId'] for column in side['columns'] for row in column['rows'])
            occurrences.append(side['bottomRow']['occurrenceId'])
        self.assertEqual(len(occurrences),18)
        self.assertIn('SEM-IH-QA-R-01',by_id)
        for occurrence_id in occurrences:
            rule_id=f'SEM-IH-{occurrence_id}'
            self.assertIn(rule_id,by_id)
            self.assertIn('C-TOKEN',{item['conditionId'] for item in by_id[rule_id]['preconditions']})
        for occurrence_id in ('QA-R-01','QA-R-02','QD-R-01','QD-R-02'):
            rule_id=f'SEM-IH-{occurrence_id}'
            self.assertTrue(any(item.get('invokeRuleId')=='SEM-SECURE-ENTRY-001' for item in by_id[rule_id]['operations']))

    def test_room_help_semantic_closure(self):
        source=load(REPO/'docs/rules/source-extraction/room-help-sheet.json')
        by_id={r['ruleId']:r for r in load(DIR/'pilots.json')['records']}
        icon_map={row['occurrenceId']:row['semanticReferenceId'] for row in load(DIR/'room-icon-denotations.json')['denotations']}
        self.assertEqual(len(source['entries']),25)
        self.assertIn('SEM-USE-ROOM-001',by_id)
        self.assertIn('SEM-ROOM-02-SECURE',by_id)
        self.assertIn('occupied Room has no Malfunction marker',json.dumps(by_id['SEM-USE-ROOM-001']))
        self.assertIn('sem.state.room.always-secured',json.dumps(by_id['SEM-ROOM-02-SECURE']))
        for entry in source['entries']:
            self.assertIn(f"SEM-ROOM-{entry['printedNumber']}",by_id)
        self.assertEqual([icon_map['R08-I05'],icon_map['R08-I06'],icon_map['R08-I07']],['icon.redItem','icon.malfunction','icon.ammoToken'])
        self.assertEqual([icon_map[f'R14-I0{i}'] for i in range(1,5)],['icon.ammoSlot','icon.grenadeSlot','icon.medpackSlot','icon.oxygenSlot'])
        room12=by_id['SEM-ROOM-12']['operations']
        self.assertLess(next(i for i,x in enumerate(room12) if x.get('invokeRuleId')=='SEM-INT-004'),next(i for i,x in enumerate(room12) if x.get('invokeRuleId')=='SEM-NOISE-001'))
        self.assertIn('SEM-Q-004',by_id['SEM-ROOM-04']['unresolvedQuestionRefs'])
        self.assertTrue(any(item['audience']=='owner-private' for item in by_id['SEM-ROOM-19']['informationPolicy']))
        self.assertEqual(by_id['SEM-ROOM-11']['decisions'][2]['cardinality'],{'min':0,'max':1})
        self.assertTrue(by_id['SEM-ROOM-11']['decisions'][2]['declineAllowed'])
        self.assertTrue(any(item.get('operationType')=='pay-cost' and item.get('objectRef')=='COST-ROOM-13-OXYGEN' for item in by_id['SEM-ROOM-13']['operations']))
        self.assertTrue(any(item.get('invokeRuleId')=='SEM-NEST-DESTROYED-001' for item in by_id['SEM-ROOM-25']['operations']))

    def test_base_exploration_family_semantic_closure(self):
        source=load(DIR/'exploration-source-index.json')
        registry={row['sourceId']:row for row in load(DIR/'source-registry.json')['sources']}
        by_id={row['ruleId']:row for row in load(DIR/'pilots.json')['records']}
        backlog={row['semanticUnitId']:row for row in load(DIR/'backlog.json')['units']}
        self.assertEqual(source['counts'],{
            'explorationIdentities':12,'ttsFaceOccurrences':12,'ttsSharedBackOccurrences':1,
            'directFaceSelectors':12,'generatedSpriteSheetCells':0,'selectorGaps':0,
            'untitledFaces':12,'sourceBoundDraftFaces':12,'licensedDigitalOccurrences':12,
            'officialVisibleComponentOccurrences':3,'officialVisibleComponentIdentities':2,
            'faqOccurrences':8,'printedSentences':46,'sourceLocalDiagrams':12,
            'functionalIconOccurrences':60,'backlogTuples':12,
        })
        self.assertEqual([row['ttsCardId'] for row in source['faces']],list(range(5629,5641)))
        self.assertEqual([row['bgaOccurrence']['key'] for row in source['faces']],[
            'ExplorationCard9','ExplorationCard10','ExplorationCard11','ExplorationCard5',
            'ExplorationCard4','ExplorationCard6','ExplorationCard12','ExplorationCard7',
            'ExplorationCard3','ExplorationCard2','ExplorationCard1','ExplorationCard8',
        ])
        self.assertEqual(source['sharedBack']['sourceSelector']['key'],'BackURL')
        self.assertFalse(source['sharedBack']['rulesTextPresent'])
        self.assertEqual({(row['role'],row['guid']) for row in source['excludedExpansionRoles']},{
            ('xyrianExplorationDeck','6b2b69'),('explorationDeck','a24dc8'),
            ('explorationDeck','dd1eda'),('explorationDeck','2e8e9d'),
        })
        face_rule_ids=[]
        for face in source['faces']:
            card_id=face['ttsCardId']; rule=by_id[face['semanticRuleId']]
            face_rule_ids.append(face['semanticRuleId'])
            self.assertEqual(face['printedTitle'],'')
            self.assertFalse(face['joinEvidence']['titleOnlyJoin'])
            self.assertEqual(face['sourceSelector']['key'],'FaceURL')
            self.assertFalse(face['sourceSelector']['generatedSpriteSheetCell'])
            registered=registry[face['sourceId']]
            self.assertEqual((registered['path'],registered['sha256'],registered['occurrenceId']),(face['sourcePath'],face['sourceSha256'],face['explorationOccurrenceId']))
            self.assertEqual(backlog[face['backlogUnitId']]['pilotRuleIds'],[face['semanticRuleId']])
            self.assertEqual(backlog[face['backlogUnitId']]['status'],'pilot-covered')
            unit_ids=[row['unitId'] for row in face['sourceUnits']]
            operation_units=[row['sourceUnitId'] for row in rule['operations']]
            self.assertEqual(list(dict.fromkeys(operation_units)),unit_ids)
            self.assertEqual(rule['title'],f'Untitled Exploration occurrence {card_id}')
            self.assertEqual(rule['unresolvedQuestionRefs'],['SEM-Q-011'])
            self.assertEqual(rule['sourceVariants'][0]['sourceId'],'SRC-BGA-EXPLORATION')
            transitions=[row for row in rule['operations'] if row['operationType']=='transition-zone']
            self.assertEqual(len(transitions),1)
            expected='tax.scaffold.zone.removed-from-game' if face['bgaOccurrence']['removeFromGame'] else 'tax.scaffold.zone.discard-pile'
            self.assertEqual(transitions[0]['transition']['to'],expected)
            corridor_op=next(row for row in rule['operations'] if row['objectRef']=='one random Corridor in each eligible source-local diagram slot')
            self.assertEqual(corridor_op['repeat']['assignmentOrder'],'SEM-Q-011 unresolved')
            self.assertNotIn('icon.lifeSupportActive',rule['termRefs'])
            self.assertNotIn('icon.lifeSupportInactive',rule['termRefs'])
        generic=by_id['SEM-ACT-EXPLORE-001']
        dispatch=next(row['dispatchRuleIds'] for row in generic['operations'] if row.get('dispatchRuleIds'))
        self.assertEqual(dispatch,face_rule_ids)
        self.assertIn('SEM-Q-002',generic['unresolvedQuestionRefs'])
        question=next(row for row in load(DIR/'review-gates.json')['questions'] if row['questionId']=='SEM-Q-011')
        self.assertTrue(question['defaultProhibited'])
        self.assertEqual(question['blocksRuleIds'],face_rule_ids)
        for card_id in (5630,5631,5635):
            operations=by_id[f'SEM-EXPLORATION-{card_id}-001']['operations']
            adult_ops=[row['operationType'] for row in operations if 'Corridor just passed through' in row['objectRef']]
            self.assertEqual(adult_ops,['remove-component','place-component'])
        for card_id in (5637,5638,5639):
            transition=next(row for row in by_id[f'SEM-EXPLORATION-{card_id}-001']['operations'] if row['operationType']=='transition-zone')
            self.assertEqual(transition['conditionRefs'],[])
            self.assertIn('still resolves when Entrance Effects are ignored',transition['notes'])

    def test_exploration_specific_adversarial_corruptions_are_rejected(self):
        def run_mutation(mutate):
            with tempfile.TemporaryDirectory(prefix='semantic-exploration-negative-') as temp_dir:
                root=Path(temp_dir)
                data={name:load(DIR/name) for name in FILES}
                mutate(data)
                for name,payload in data.items():
                    (root/name).write_text(json.dumps(payload,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
                run,report=self.run_validator(root,skip=True)
            self.assertNotEqual(run.returncode,0)
            return {failure['check'] for failure in report['failures']}

        def drop_face(data):
            source=data['exploration-source-index.json']
            source['faces']=source['faces'][1:]
            source['counts']['explorationIdentities']-=1
            source['counts']['ttsFaceOccurrences']-=1
        self.assertIn('Exploration source-index exact identity count',run_mutation(drop_face))

        def duplicate_face(data):
            source=data['exploration-source-index.json']
            source['faces'].append(json.loads(json.dumps(source['faces'][0])))
            source['counts']['explorationIdentities']+=1
            source['counts']['ttsFaceOccurrences']+=1
        self.assertIn('Exploration source-index exact identity count',run_mutation(duplicate_face))

        def title_only_join(data):
            join=data['exploration-source-index.json']['faces'][0]['joinEvidence']
            join.update({'identityJoin':'display title','titleOnlyJoin':True,'basis':['display title']})
        self.assertIn('Exploration title/folder/modulo join prohibited',run_mutation(title_only_join))

        def source_cell_swap(data):
            first,second=data['exploration-source-index.json']['faces'][:2]
            for key in ('sourcePath','sourceSha256','sourceSelector'):
                first[key],second[key]=second[key],first[key]
        self.assertIn('independently locked Exploration occurrence crosswalk',run_mutation(source_cell_swap))

        def invert_face_back(data):
            selector=data['exploration-source-index.json']['faces'][0]['sourceSelector']
            selector.update({'key':'BackURL','objectType':'Deck','guid':'63add2'})
        self.assertIn('Exploration exact FaceURL selector/provenance projection',run_mutation(invert_face_back))

        def reorder_source_units(data):
            units=data['exploration-source-index.json']['faces'][1]['sourceUnits']
            units[3],units[4]=units[4],units[3]
        self.assertIn('Exploration source-unit IDs/order',run_mutation(reorder_source_units))

        def drift_remove_scope(data):
            rule=next(row for row in data['pilots.json']['records'] if row['ruleId']=='SEM-EXPLORATION-5639-001')
            transition=next(row for row in rule['operations'] if row['operationType']=='transition-zone')
            transition['transition']['to']='tax.scaffold.zone.discard-pile'
            transition['conditionRefs']=[next(row['conditionId'] for row in rule['preconditions'] if 'ignore Entrance' in json.dumps(row))]
        checks=run_mutation(drift_remove_scope)
        self.assertIn('Exploration remove/discard lifecycle transition lock',checks)
        self.assertIn('Exploration remove-from-game scope outside Entrance effect',checks)

        def invent_title_icon_default(data):
            face=data['exploration-source-index.json']['faces'][0]
            face['printedTitle']='NORTH HAZARD'
            face['iconOccurrences'][0]['semanticReferenceId']='icon.lifeSupportActive'
            rule=next(row for row in data['pilots.json']['records'] if row['ruleId']=='SEM-EXPLORATION-5629-001')
            rule['title']='North Hazard Exploration Card 1 effect'
            rule['termRefs'].append('icon.lifeSupportActive'); rule['termRefs'].sort()
            question=next(row for row in data['review-gates.json']['questions'] if row['questionId']=='SEM-Q-011')
            question['defaultProhibited']=False
        checks=run_mutation(invent_title_icon_default)
        self.assertIn('Exploration closed-corpus untitled projection',checks)
        self.assertIn('Exploration exact source-local icon occurrence projection',checks)
        self.assertIn('Exploration multi-slot question no-default alternatives',checks)
        self.assertIn('Exploration no invented title/system icon',checks)

        def lose_variant(data):
            rule=next(row for row in data['pilots.json']['records'] if row['ruleId']=='SEM-EXPLORATION-5630-001')
            rule['sourceVariants']=[]
            data['pilots.json']['counts']['variantReferences']-=1
        self.assertIn('Exploration licensed/official source-variant closure',run_mutation(lose_variant))

        def invert_authority(data):
            rule=next(row for row in data['pilots.json']['records'] if row['ruleId']=='SEM-EXPLORATION-5632-001')
            rule['authority']['highest']='source-bound-component-scan'
        self.assertIn('Exploration authority lock',run_mutation(invert_authority))

        def lower_backlog(data):
            backlog=data['backlog.json']; target='CARD:3da198b348a70d64'
            backlog['units']=[row for row in backlog['units'] if row['semanticUnitId']!=target]
            backlog['counts']['units']-=1
            backlog['counts']['byChannel']['card-reference-source-tuple']-=1
            backlog['counts']['byStatus']['pilot-covered']-=1
        self.assertIn('Exploration exact backlog tuple projection',run_mutation(lower_backlog))

    def test_base_robot_family_semantic_closure(self):
        source=load(DIR/'robot-source-index.json')
        registry={row['sourceId']:row for row in load(DIR/'source-registry.json')['sources']}
        by_id={row['ruleId']:row for row in load(DIR/'pilots.json')['records']}
        backlog={row['semanticUnitId']:row for row in load(DIR/'backlog.json')['units']}
        self.assertEqual(source['counts'],{
            'robotIdentities':6,'ttsFaceOccurrences':6,'directCompositeFaceSelectors':6,
            'generatedSpriteSheetCells':0,'selectorGaps':0,'ttsSharedBackOccurrences':1,
            'baseBackSelectorReferences':7,'prototypeBackSelectorReferencesExcluded':2,
            'canonicalCorpusFaces':4,'sourceBoundDraftFaces':2,'licensedDigitalOccurrences':6,
            'officialVisibleComponentOccurrences':2,'officialVisibleComponentIdentities':2,
            'physicalPanels':24,'operativePanels':12,'actionOptions':13,'printedSentences':16,
            'functionalIconOccurrences':23,'officialVisibleFaceIconOccurrences':8,
            'licensedPlaceholderOccurrences':23,'rulebookTextOccurrences':27,
            'rulebookVisualOccurrences':8,'baseFaqOccurrences':1,'excludedExpansionFaqOccurrences':2,
            'prototypeRobotCardsExcluded':2,'expansionRobotCardsExcluded':3,
            'securityRobotRoomNameCollisionsExcluded':4,'backlogTuples':6,'backlogObligationsLinked':18,
        })
        card_ids=[506400,510800,529300,529400,529500,529600]
        self.assertEqual([row['ttsCardId'] for row in source['faces']],card_ids)
        self.assertEqual(source['familyCountEvidence']['ttsRole']['rootDeckNumbers'],['5064','5108','5293','5294','5295','5296'])
        self.assertEqual(source['sharedBack']['sourceSelector'],{
            'key':'BackURL','objectType':'DeckCustom','guid':'98925d',
            'url':'https://steamusercontent-a.akamaihd.net/ugc/2468613527880246407/895F8FE734520A2A146ED7B3557FB72CAA491CBF/',
            'sideRole':'shared-non-operative-back','rootDeckSelectorCount':1,
            'baseCardSelectorCount':6,'prototypeSelectorCountExcluded':2,
        })
        self.assertFalse(source['sharedBack']['rulesTextPresent'])
        self.assertFalse(source['sharedBack']['separateRulesFace'])
        self.assertEqual([(row['sourceOccurrenceId'],row['pixelMatch']['ransacInliers']) for face in source['faces'] for row in face['officialOccurrences']],[('RB-P03-V01-ROBOT-SERVER',62),('RB-P03-V01-ROBOT-TECHNICAL',46)])
        rule_ids=[]
        for face in source['faces']:
            rule=by_id[face['semanticRuleId']]
            rule_ids.append(face['semanticRuleId'])
            self.assertEqual(face['sourceSelector']['key'],'FaceURL')
            self.assertEqual(face['sourceSelector']['cardId'],face['ttsCardId'])
            self.assertEqual(face['sourceSelector']['guid'],face['ttsCardGuid'])
            self.assertEqual(face['sourceSelector']['parentDeckGuid'],'98925d')
            self.assertFalse(face['joinEvidence']['titleOnlyJoin'])
            self.assertEqual([row['panelId'] for row in face['panels']],['P1','P2','P3','P4'])
            sentence_ids=[row['sentenceId'] for row in face['sentences']]
            semantic_sentence_ids=[row['sourceSentenceId'] for row in rule['operations'] if row.get('sourceSentenceId')]
            self.assertEqual(list(dict.fromkeys(semantic_sentence_ids)),sentence_ids)
            self.assertEqual(backlog[face['backlogUnitId']]['pilotRuleIds'],[face['semanticRuleId']])
            self.assertEqual(backlog[face['backlogUnitId']]['status'],'pilot-covered')
            registered=registry[face['sourceId']]
            self.assertEqual((registered['path'],registered['sha256'],registered['occurrenceId']),(face['sourcePath'],face['sourceSha256'],face['robotOccurrenceId']))
            self.assertGreaterEqual(len(rule['sourceVariants']),1)
            self.assertEqual(rule['sourceVariants'][0]['sourceId'],'SRC-BGA-ROBOTS')
            self.assertIn('SEM-Q-013',rule['unresolvedQuestionRefs'])
        activate=by_id['SEM-ACT-ROBOT-001']
        dispatch=next(row['dispatchRuleIds'] for row in activate['operations'] if row.get('dispatchRuleIds'))
        self.assertEqual(dispatch,rule_ids)
        self.assertEqual(by_id['SEM-ROBOT-MOVEMENT-001']['decisions'][0]['selectionMode'],'unresolved')
        self.assertIn('SEM-Q-012',by_id['SEM-ROBOT-REVEAL-001']['unresolvedQuestionRefs'])
        self.assertEqual(by_id['SEM-ROBOT-MALFUNCTION-001']['unresolvedQuestionRefs'],['SEM-Q-010'])
        self.assertEqual(by_id['SEM-ROBOT-MALFUNCTION-PLACEMENT-001']['unresolvedQuestionRefs'],['SEM-Q-010','SEM-Q-012'])
        self.assertNotIn('destroyed Robot',json.dumps({rule_id:by_id[rule_id] for rule_id in rule_ids},ensure_ascii=False))
        questions={row['questionId']:row for row in load(DIR/'review-gates.json')['questions']}
        for question_id in [f'SEM-Q-{index:03d}' for index in range(10,20)]:
            self.assertTrue(questions[question_id]['defaultProhibited'])

    def test_robot_specific_adversarial_corruptions_are_rejected(self):
        def run_mutation(mutate):
            with tempfile.TemporaryDirectory(prefix='semantic-robot-negative-') as temp_dir:
                root=Path(temp_dir)
                data={name:load(DIR/name) for name in FILES}
                mutate(data)
                for name,payload in data.items():
                    (root/name).write_text(json.dumps(payload,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
                run,report=self.run_validator(root,skip=True)
            self.assertNotEqual(run.returncode,0)
            return {failure['check'] for failure in report['failures']}

        def drop_face(data):
            source=data['robot-source-index.json']
            source['faces']=source['faces'][1:]
            for key in ('robotIdentities','ttsFaceOccurrences','directCompositeFaceSelectors','backlogTuples'):
                source['counts'][key]-=1
        self.assertIn('Robot source-index exact identity count',run_mutation(drop_face))

        def duplicate_face(data):
            source=data['robot-source-index.json']
            source['faces'].append(json.loads(json.dumps(source['faces'][0])))
            for key in ('robotIdentities','ttsFaceOccurrences','directCompositeFaceSelectors','backlogTuples'):
                source['counts'][key]+=1
        self.assertIn('Robot source-index exact identity count',run_mutation(duplicate_face))

        def title_only_join(data):
            join=data['robot-source-index.json']['faces'][0]['joinEvidence']
            join.update({'identityJoin':'display title','titleOnlyJoin':True,'basis':['display title']})
        self.assertIn('Robot title/folder/modulo join prohibited',run_mutation(title_only_join))

        def invert_face_back(data):
            face=data['robot-source-index.json']['faces'][0]
            face['sourceSelector'].update({'key':'BackURL','sideRole':'shared-non-operative-back','url':data['robot-source-index.json']['sharedBack']['sourceSelector']['url']})
            face['cardStateRoles'].update({'initial':'face-up-revealed','afterRevealTrigger':'face-down-unrevealed','separateRulesFaceOnBack':True})
        checks=run_mutation(invert_face_back)
        self.assertIn('Robot exact CardID/GUID/FaceURL selector projection',checks)
        self.assertIn('Robot face/back and reveal-state role projection',checks)

        def wrong_guid_cardid(data):
            face=data['robot-source-index.json']['faces'][2]
            face['ttsCardGuid']='cd319d'
            face['ttsCardId']=506400
            face['sourceSelector'].update({'guid':'cd319d','cardId':506400})
        self.assertIn('independently locked Robot occurrence crosswalk',run_mutation(wrong_guid_cardid))

        def reorder_sentences_and_panels(data):
            face=data['robot-source-index.json']['faces'][1]
            face['sentences'][0],face['sentences'][1]=face['sentences'][1],face['sentences'][0]
            for sequence,row in enumerate(face['sentences'],1): row['sequence']=sequence
            face['panels'][2],face['panels'][3]=face['panels'][3],face['panels'][2]
            for reading,row in enumerate(face['panels'],1): row['readingOrder']=reading
        checks=run_mutation(reorder_sentences_and_panels)
        self.assertIn('Robot source sentence IDs/panel order',checks)
        self.assertIn('Robot exact panel roles/order',checks)

        def drop_icon_with_coordinated_count(data):
            source=data['robot-source-index.json']
            source['faces'][1]['iconOccurrences'].pop()
            source['counts']['functionalIconOccurrences']-=1
        self.assertIn('Robot exact source-local icon occurrence projection',run_mutation(drop_icon_with_coordinated_count))

        def invert_runtime_state(data):
            source=data['robot-source-index.json']
            source['ttsRuntimeStateProvenance']['reveal']['modelStateTransition']={'fromGmNotes':'active','toGmNotes':''}
            source['ttsRuntimeStateProvenance']['reveal']['helperTokenStateTransition']['toStateId']=2
        self.assertIn('Robot TTS runtime state/side provenance boundary',run_mutation(invert_runtime_state))

        def leak_reveal(data):
            rule=next(row for row in data['pilots.json']['records'] if row['ruleId']=='SEM-ROBOT-REVEAL-001')
            rule['informationPolicy'][0].update({'audience':'public','revealTrigger':'setup'})
        self.assertIn('Robot reveal/visibility no-leak boundary',run_mutation(leak_reveal))

        def flatten_malfunction(data):
            question=next(row for row in data['review-gates.json']['questions'] if row['questionId']=='SEM-Q-010')
            question['defaultProhibited']=False
            question['alternatives']=question['alternatives'][:1]
            rule=next(row for row in data['pilots.json']['records'] if row['ruleId']=='SEM-ROBOT-MALFUNCTION-001')
            rule['unresolvedQuestionRefs']=[]
            rule['status']='source-backed'
        self.assertIn('SEM-Q-010 exact unresolved contradiction preservation',run_mutation(flatten_malfunction))

        def invent_movement_owner(data):
            rule=next(row for row in data['pilots.json']['records'] if row['ruleId']=='SEM-ROBOT-MOVEMENT-001')
            rule['decisions'][0].update({'selectionMode':'player-choice','ownerRef':'P-MOVE-OWNER'})
            rule['targets'][0].update({'selectorRef':'P-MOVE-OWNER','selectionMode':'player-choice'})
            question=next(row for row in data['review-gates.json']['questions'] if row['questionId']=='SEM-Q-013')
            question['defaultProhibited']=False
        self.assertIn('Robot movement no invented owner/target/default',run_mutation(invent_movement_owner))

        def lose_variants(data):
            rule=next(row for row in data['pilots.json']['records'] if row['ruleId']=='SEM-ROBOT-SERVER-001')
            removed=len(rule['sourceVariants'])
            rule['sourceVariants']=[]
            data['pilots.json']['counts']['variantReferences']-=removed
        self.assertIn('Robot licensed/official source-variant closure',run_mutation(lose_variants))

        def invert_authority(data):
            rule=next(row for row in data['pilots.json']['records'] if row['ruleId']=='SEM-ROBOT-MILITARY-001')
            rule['authority']['highest']='source-bound-component-scan'
        self.assertIn('Robot authority lock',run_mutation(invert_authority))

        def lower_backlog(data):
            backlog=data['backlog.json']; target='CARD:e613b1e23d25d91e'
            backlog['units']=[row for row in backlog['units'] if row['semanticUnitId']!=target]
            backlog['counts']['units']-=1
            backlog['counts']['byChannel']['card-reference-source-tuple']-=1
            backlog['counts']['byStatus']['pilot-covered']-=1
            source=data['robot-source-index.json']
            source['familyCountEvidence']['backlog']['faceTupleCount']-=1
            source['familyCountEvidence']['backlog']['faceUnitIds'].remove(target)
            source['familyCountEvidence']['backlog']['linkedUnitIds'].remove(target)
            source['counts']['backlogTuples']-=1
            source['counts']['backlogObligationsLinked']-=1
        checks=run_mutation(lower_backlog)
        self.assertIn('Robot exact backlog tuple projection',checks)
        self.assertIn('Robot exact overlapping backlog-obligation closure',checks)

    def test_base_attack_family_semantic_closure(self):
        source=load(DIR/'attack-source-index.json')
        registry={row['sourceId']:row for row in load(DIR/'source-registry.json')['sources']}
        by_id={row['ruleId']:row for row in load(DIR/'pilots.json')['records']}
        backlog={row['semanticUnitId']:row for row in load(DIR/'backlog.json')['units']}
        self.assertEqual(source['counts'],{
            'attackOccurrences':20,'uniquePrintedTitles':8,'generatedFaceOccurrences':19,'directFaceOccurrences':1,
            'generatedSourceSheetCells':20,'selectedGeneratedCells':19,'excludedSelectorGaps':1,
            'sharedBackOccurrences':1,'sharedBackSelectorReferences':21,'sourceSheets':1,
            'canonicalCorpusFaces':1,'sourceBoundDraftFaces':19,'physicalPanels':69,'operativePanels':29,
            'printedSentences':54,'applicabilityBadgeOccurrences':57,'inlineIconOccurrences':13,
            'functionalSymbolOccurrences':70,'selectedEvidenceNoMatchOccurrences':55,
            'selectedEvidenceMatchedOccurrences':14,'licensedStructuredVariants':15,'licensedFaceLinks':20,
            'officialVisibleFaceCounterparts':3,'officialVisibleBackCounterparts':1,'officialFaceLinks':8,
            'officialRulebookTextOccurrences':9,'officialRulebookVisualObligations':2,'faqOccurrences':3,
            'excludedExpansionAttackDecks':3,'excludedUnusedGeneratedFaces':1,'backlogTuples':20,'backlogObligationsLinked':28,
        })
        self.assertEqual(source['titleMultiplicity'],{'BITE':6,'BLOOD SENSE':1,'DEADLY CLAWS':3,'FURY':2,'INFECTING':1,'MISS':1,'SCRATCH':4,'TAIL ATTACK':2})
        self.assertEqual([row['ttsCardId'] for row in source['faces']],[*range(394900,394917),394918,394919,399100])
        self.assertEqual(source['sourceSheet']['grid'],{'columns':5,'rows':4,'cellWidth':827,'cellHeight':1111})
        self.assertEqual(source['sharedBack']['sourceSelector']['referenceCount'],21)
        self.assertFalse(source['sharedBack']['rulesTextPresent'])
        self.assertEqual(source['excludedContent']['unusedGeneratedCell']['cellIndex'],17)
        self.assertEqual(source['excludedContent']['unusedGeneratedCell']['printedTitle'],'SUMMONING')
        self.assertIn('No root DeckID',source['excludedContent']['unusedGeneratedCell']['selectorGap'])
        rule_ids=[]
        for face in source['faces']:
            card_id=face['ttsCardId']; rule=by_id[face['semanticRuleId']]; rule_ids.append(face['semanticRuleId'])
            selector=face['sourceSelector']
            self.assertEqual(selector['fullCardId'],card_id)
            self.assertEqual(selector['guid'],face['ttsCardGuid'])
            self.assertEqual(selector['parentDeckGuid'],'34c73e')
            self.assertFalse(selector['cardIdModuloJoinUsed'])
            self.assertFalse(face['joinEvidence']['titleOnlyJoin'])
            self.assertFalse(face['joinEvidence']['sourceCellOnlyJoin'])
            self.assertEqual((registry[face['sourceId']]['path'],registry[face['sourceId']]['sha256'],registry[face['sourceId']]['occurrenceId']),(face['sourcePath'],face['sourceSha256'],face['attackOccurrenceId']))
            self.assertEqual(backlog[face['backlogUnitId']]['pilotRuleIds'],[face['semanticRuleId']])
            self.assertEqual(backlog[face['backlogUnitId']]['status'],'pilot-covered')
            self.assertEqual([row['sequence'] for row in face['sentences']],list(range(1,len(face['sentences'])+1)))
            self.assertEqual([row['sourceSentenceId'] for row in rule['operations'] if row.get('sourceSentenceId')][0],face['sentences'][0]['sentenceId'])
            self.assertEqual(rule['decisions'],[])
            self.assertGreaterEqual(len(rule['sourceVariants']),1)
            self.assertEqual(rule['sourceVariants'][0]['sourceId'],'SRC-BGA-INTRUDER-ATTACKS')
        attack=by_id['SEM-INT-004']
        dispatch=next(row['dispatchRuleIds'] for row in attack['operations'] if row.get('dispatchRuleIds'))
        self.assertEqual(dispatch,rule_ids)
        discard=next(row for row in attack['operations'] if row['operationType']=='transition-zone')
        self.assertIn('still in resolution',discard['objectRef'])
        self.assertTrue(discard['conditionRefs'])
        self.assertEqual([row['sourceScopedResolution']['intruderType'] for row in source['faces'][6]['applicabilityBadgeOccurrences']],['Adult','Drone','Queen'])
        self.assertEqual([row['sourceScopedResolution']['intruderType'] for row in source['faces'][11]['applicabilityBadgeOccurrences']],['Adult','Queen','Drone'])
        self.assertEqual(source['faces'][6]['inlineIconOccurrences'][0]['sourceToken'],'LOCAL_ICON:INLINE-1')
        self.assertEqual(source['faces'][6]['inlineIconOccurrences'][0]['semanticReferenceId'],'icon.characterHealth')
        miss=by_id['SEM-ATTACK-394912-001']
        self.assertIn('SEM-Q-024',miss['unresolvedQuestionRefs'])
        self.assertTrue(any(row['operationType']=='shuffle' and 'including this MISS card' in row['objectRef'] for row in miss['operations']))
        questions={row['questionId']:row for row in load(DIR/'review-gates.json')['questions']}
        for question_id in ('SEM-Q-020','SEM-Q-021','SEM-Q-022','SEM-Q-023','SEM-Q-024'):
            self.assertTrue(questions[question_id]['defaultProhibited'])

    def test_attack_specific_adversarial_corruptions_are_rejected(self):
        def run_mutation(mutate):
            with tempfile.TemporaryDirectory(prefix='semantic-attack-negative-') as temp_dir:
                root=Path(temp_dir)
                data={name:load(DIR/name) for name in FILES}
                mutate(data)
                for name,payload in data.items():
                    (root/name).write_text(json.dumps(payload,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
                run,report=self.run_validator(root,skip=True)
            self.assertNotEqual(run.returncode,0)
            return {failure['check'] for failure in report['failures']}

        def drop_occurrence(data):
            source=data['attack-source-index.json']; source['faces']=source['faces'][1:]
            source['counts']['attackOccurrences']-=1; source['counts']['generatedFaceOccurrences']-=1
        self.assertIn('Attack source-index exact occurrence count',run_mutation(drop_occurrence))

        def duplicate_occurrence(data):
            source=data['attack-source-index.json']; source['faces'].append(json.loads(json.dumps(source['faces'][0])))
            source['counts']['attackOccurrences']+=1; source['counts']['generatedFaceOccurrences']+=1
        self.assertIn('Attack source-index exact occurrence count',run_mutation(duplicate_occurrence))

        def collapse_repeated_title(data):
            data['attack-source-index.json']['titleMultiplicity']['BITE']=1
        self.assertIn('Attack repeated-title occurrence multiplicity lock',run_mutation(collapse_repeated_title))

        def swap_cells_and_sheets(data):
            first,second=data['attack-source-index.json']['faces'][:2]
            first['sourceSelector']['generatedCell'],second['sourceSelector']['generatedCell']=second['sourceSelector']['generatedCell'],first['sourceSelector']['generatedCell']
        checks=run_mutation(swap_cells_and_sheets)
        self.assertIn('independently locked Attack occurrence crosswalk',checks)
        self.assertIn('Attack generated sheet/hash/grid/cell selector projection',checks)

        def modulo_join(data):
            join=data['attack-source-index.json']['faces'][0]['joinEvidence']
            join.update({'identityJoin':'CardID modulo','cardIdModuloJoin':True,'basis':['cardId % 100']})
        self.assertIn('Attack title/cell/folder/modulo join prohibited',run_mutation(modulo_join))

        def selector_drift(data):
            selector=data['attack-source-index.json']['faces'][2]['sourceSelector']
            selector.update({'fullCardId':394900,'guid':'5afea3'})
        self.assertIn('Attack exact full CardID/GUID/CustomDeck selector projection',run_mutation(selector_drift))

        def invert_face_back(data):
            face=data['attack-source-index.json']['faces'][3]
            face['sourceSelector']['url'],face['sourceSelector']['backUrl']=face['sourceSelector']['backUrl'],face['sourceSelector']['url']
            face['sourceSelector']['key']='BackURL'
        self.assertIn('Attack FaceURL/BackURL role projection',run_mutation(invert_face_back))

        def swap_applicability(data):
            badges=data['attack-source-index.json']['faces'][6]['applicabilityBadgeOccurrences']
            badges[0]['sourceScopedResolution']['intruderType'],badges[1]['sourceScopedResolution']['intruderType']=badges[1]['sourceScopedResolution']['intruderType'],badges[0]['sourceScopedResolution']['intruderType']
        self.assertIn('Attack exact source-scoped applicability badge projection',run_mutation(swap_applicability))

        def move_badge_count_preserving(data):
            faces=data['attack-source-index.json']['faces']; moved=faces[0]['applicabilityBadgeOccurrences'].pop(); faces[1]['applicabilityBadgeOccurrences'].append(moved)
        self.assertIn('Attack exact source-scoped applicability badge projection',run_mutation(move_badge_count_preserving))

        def drift_body_punctuation(data):
            face=data['attack-source-index.json']['faces'][13]
            face['printedBody']=face['printedBody'].replace('Contamination.','Contamination!')
        self.assertIn('Attack exact body/punctuation/order drift',run_mutation(drift_body_punctuation))

        def flatten_branch(data):
            rule=next(row for row in data['pilots.json']['records'] if row['ruleId']=='SEM-ATTACK-394900-001')
            next(row for row in rule['operations'] if row['operationType']=='branch')['operationType']='evaluate-condition'
        self.assertIn('Attack condition/otherwise branch preservation',run_mutation(flatten_branch))

        def reorder_operations_cleanly(data):
            rule=next(row for row in data['pilots.json']['records'] if row['ruleId']=='SEM-ATTACK-394919-001')
            rule['operations'][0],rule['operations'][1]=rule['operations'][1],rule['operations'][0]
            for index,row in enumerate(rule['operations'],1): row['sequence']=index; row['stepId']=f'S{index:02d}'
        self.assertIn('Attack semantic sentence/panel order projection',run_mutation(reorder_operations_cleanly))

        def lose_variants(data):
            rule=next(row for row in data['pilots.json']['records'] if row['ruleId']=='SEM-ATTACK-394907-001')
            removed=len(rule['sourceVariants']); rule['sourceVariants']=[]; data['pilots.json']['counts']['variantReferences']-=removed
        self.assertIn('Attack licensed/official source-variant closure',run_mutation(lose_variants))

        def invert_authority(data):
            rule=next(row for row in data['pilots.json']['records'] if row['ruleId']=='SEM-ATTACK-394911-001')
            rule['authority']['highest']='source-bound-component-scan'
        self.assertIn('Attack authority lock',run_mutation(invert_authority))

        def invent_default_owner(data):
            question=next(row for row in data['review-gates.json']['questions'] if row['questionId']=='SEM-Q-020'); question['defaultProhibited']=False
            rule=next(row for row in data['pilots.json']['records'] if row['ruleId']=='SEM-ATTACK-394909-001')
            rule['decisions']=[{'decisionId':'D-ATK-INVENTED','ownerRef':'P-RULES','selectionMode':'deterministic','cardinality':{'min':1,'max':1},'declineAllowed':False,'visibility':'public','options':['attacking Room']}]
            data['pilots.json']['counts']['decisions']+=1
        checks=run_mutation(invent_default_owner)
        self.assertIn('Attack ambiguity no-default alternatives/linkage',checks)
        self.assertIn('Attack no invented face decision owner',checks)

        def invent_local_icon(data):
            icon=data['attack-source-index.json']['faces'][6]['inlineIconOccurrences'][0]
            icon['semanticReferenceId']='icon.intruder'; icon['templateMatchScore']=1.0
        self.assertIn('Attack local Character Health independent-resolution boundary',run_mutation(invent_local_icon))

        def lower_backlog_coordinated(data):
            target='CARD:72e8782d5b98ee1d'; backlog=data['backlog.json']
            backlog['units']=[row for row in backlog['units'] if row['semanticUnitId']!=target]
            backlog['counts']['units']-=1; backlog['counts']['byChannel']['card-reference-source-tuple']-=1; backlog['counts']['byStatus']['pilot-covered']-=1
            source=data['attack-source-index.json']; linked=source['familyCountEvidence']['backlog']['linkedUnitIds']; source['familyCountEvidence']['backlog']['linkedUnitIds']=[row for row in linked if row!=target]
            source['familyCountEvidence']['backlog']['faceUnitIds']=[row for row in source['familyCountEvidence']['backlog']['faceUnitIds'] if row!=target]
            source['familyCountEvidence']['backlog']['faceTupleCount']-=1; source['counts']['backlogTuples']-=1; source['counts']['backlogObligationsLinked']-=1
        checks=run_mutation(lower_backlog_coordinated)
        self.assertIn('Attack exact backlog tuple projection',checks)
        self.assertIn('Attack exact overlapping backlog-obligation closure',checks)

    def test_base_queen_health_family_semantic_closure(self):
        source=load(DIR/'queen-health-source-index.json')
        registry={row['sourceId']:row for row in load(DIR/'source-registry.json')['sources']}
        by_id={row['ruleId']:row for row in load(DIR/'pilots.json')['records']}
        backlog={row['semanticUnitId']:row for row in load(DIR/'backlog.json')['units']}
        self.assertEqual(source['counts']['physicalFaceOccurrences'],12)
        self.assertEqual(source['counts']['uniqueFaceAssets'],10)
        self.assertEqual(source['counts']['physicalPanels'],24)
        self.assertEqual(source['counts']['printedSentences'],37)
        self.assertEqual(source['counts']['functionalIconOccurrences'],28)
        self.assertEqual(source['discardNumberMultiplicity'],{'0':3,'1':4,'2':2,'3':3})
        expected_occurrences=[
            (424300,'615e22'),(424500,'0dd25f'),(503700,'e4ab1c'),(504100,'717b23'),
            (504200,'ca5827'),(504000,'919263'),(503900,'b42831'),(503800,'64ae0a'),
            (424100,'a10f34'),(458100,'6ba0a2'),(429200,'48a2ae'),(429200,'0fbf8d'),
        ]
        self.assertEqual([(row['ttsCardId'],row['ttsCardGuid']) for row in source['faces']],expected_occurrences)
        self.assertEqual(source['familyCountEvidence']['rawTtsDeck']['deckIdsInSavedOrder'],[row[0] for row in expected_occurrences])
        self.assertFalse(source['familyCountEvidence']['rawTtsDeck']['savedOrderIsGameplayDeckOrder'])
        self.assertTrue(source['familyCountEvidence']['rawTtsDeck']['setupRequiresShuffle'])
        self.assertEqual(source['sharedBack']['sourceSelector']['referenceCount'],13)
        self.assertFalse(source['sharedBack']['numberedBack'])
        self.assertFalse(source['sharedBack']['separateRulesFace'])
        self.assertEqual([row['printedValue'] for row in source['queenHitsTrack']['spacesInPrintedOrder']],[0,1,2,3,4,None])
        self.assertTrue(all(row['semanticReferenceId'] is None and not row['page40TokenAssigned'] for row in source['officialLocalSymbols']))
        self.assertEqual([row['key'] for row in source['licensedDigitalOccurrences']],[f'QueenHealthCard{index}' for index in range(1,13)])
        rule_ids=[]
        expected_backlog={}
        for face in source['faces']:
            occurrence=face['queenHealthOccurrenceId']; rule=by_id[face['semanticRuleId']]; rule_ids.append(face['semanticRuleId'])
            selector=face['sourceSelector']
            self.assertEqual(selector['key'],'FaceURL')
            self.assertEqual(selector['fullCardId'],face['ttsCardId'])
            self.assertEqual(selector['guid'],face['ttsCardGuid'])
            self.assertEqual(selector['parentDeckGuid'],'9acd7f')
            self.assertFalse(face['joinEvidence']['titleOnlyJoin'])
            self.assertFalse(face['joinEvidence']['bgaOrdinalJoin'])
            self.assertEqual([row['panelId'] for row in face['panels']],['P1','P2'])
            self.assertEqual(face['iconOccurrences'][0]['semanticReferenceId'],None)
            self.assertFalse(face['iconOccurrences'][0]['page40TokenAssigned'])
            self.assertEqual(face['iconOccurrences'][0]['printedNumericValue'],face['printedDiscardCount'])
            self.assertEqual((registry[face['sourceId']]['path'],registry[face['sourceId']]['sha256'],registry[face['sourceId']]['occurrenceId']),(face['sourcePath'],face['sourceSha256'],occurrence))
            expected_backlog.setdefault(face['backlogUnitId'],[]).append(face['semanticRuleId'])
            source_sentence_ids=[row['sentenceId'] for row in face['sentences']]
            semantic_sentence_ids=[row['sourceSentenceId'] for row in rule['operations']]
            self.assertEqual(list(dict.fromkeys(semantic_sentence_ids)),source_sentence_ids)
            self.assertEqual(rule['unresolvedQuestionRefs'][:2],['SEM-Q-026','SEM-Q-027'])
            self.assertEqual(rule['sourceVariants'][0]['sourceId'],'SRC-BGA-QUEEN-HEALTH')
        for unit_id,rule_ids_for_asset in expected_backlog.items():
            self.assertEqual(backlog[unit_id]['pilotRuleIds'],rule_ids_for_asset)
            self.assertEqual(backlog[unit_id]['status'],'pilot-covered')
        dispatch=next(row['dispatchRuleIds'] for row in by_id['SEM-QUEEN-HEALTH-RESOLUTION-001']['operations'] if row.get('dispatchRuleIds'))
        self.assertEqual(dispatch,rule_ids)
        self.assertFalse(any(row['operationType']=='shuffle' for row in by_id['SEM-QUEEN-HEALTH-RESOLUTION-001']['operations']))
        reset=next(row for row in by_id['SEM-QUEEN-HEALTH-RESOLUTION-001']['operations'] if row['operationType']=='change-value')
        self.assertFalse(reset['valueChange']['overflowCarry'])
        self.assertEqual(by_id['SEM-QUEEN-HEALTH-458100-6BA0A2-001']['decisions'][0]['selectionMode'],'unresolved')
        questions={row['questionId']:row for row in load(DIR/'review-gates.json')['questions']}
        for question_id in [f'SEM-Q-{index:03d}' for index in range(25,30)]:
            self.assertTrue(questions[question_id]['defaultProhibited'])

    def test_queen_health_specific_adversarial_corruptions_are_rejected(self):
        def run_mutation(mutate):
            with tempfile.TemporaryDirectory(prefix='semantic-queen-health-negative-') as temp_dir:
                root=Path(temp_dir)
                data={name:load(DIR/name) for name in FILES}
                mutate(data)
                for name,payload in data.items():
                    (root/name).write_text(json.dumps(payload,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
                run,report=self.run_validator(root,skip=True)
            self.assertNotEqual(run.returncode,0)
            return {failure['check'] for failure in report['failures']}

        def drop_face(data):
            source=data['queen-health-source-index.json']; source['faces']=source['faces'][1:]
            source['counts']['physicalFaceOccurrences']-=1; source['counts']['directFaceOccurrences']-=1
            source['counts']['physicalPanels']-=2; source['counts']['operativePanels']-=2
        self.assertIn('Queen Health source-index exact physical occurrence count',run_mutation(drop_face))

        def duplicate_face(data):
            source=data['queen-health-source-index.json']; source['faces'].append(json.loads(json.dumps(source['faces'][0])))
            source['counts']['physicalFaceOccurrences']+=1; source['counts']['directFaceOccurrences']+=1
            source['counts']['physicalPanels']+=2; source['counts']['operativePanels']+=2
        self.assertIn('Queen Health source-index exact physical occurrence count',run_mutation(duplicate_face))

        def title_join(data):
            join=data['queen-health-source-index.json']['faces'][0]['joinEvidence']
            join.update({'identityJoin':'Discard heading','titleOnlyJoin':True,'basis':['Discard']})
        self.assertIn('Queen Health title/folder/modulo/BGA-ordinal join prohibited',run_mutation(title_join))

        def invert_selector_back(data):
            face=data['queen-health-source-index.json']['faces'][1]; back=data['queen-health-source-index.json']['sharedBack']['sourceSelector']
            face['sourceSelector'].update({'key':'BackURL','url':back['url'],'sideRole':'shared-non-operative-back'})
        self.assertIn('Queen Health exact CardID/GUID/FaceURL selector projection',run_mutation(invert_selector_back))

        def reorder_faces(data):
            faces=data['queen-health-source-index.json']['faces']; faces[0],faces[1]=faces[1],faces[0]
            faces[0]['ttsSavedSequence']=1; faces[1]['ttsSavedSequence']=2
        checks=run_mutation(reorder_faces)
        self.assertIn('Queen Health source-index exact physical occurrence count',checks)
        self.assertIn('independently locked Queen Health physical occurrence crosswalk',checks)

        def invent_local_icon(data):
            icon=data['queen-health-source-index.json']['faces'][0]['iconOccurrences'][0]
            icon.update({'semanticReferenceId':'icon.burstDie1','page40TokenAssigned':True,'mappingStatus':'invented'})
        self.assertIn('Queen Health local number no-alias/value lock',run_mutation(invent_local_icon))

        def lose_local_icon(data):
            source=data['queen-health-source-index.json']; source['faces'][0]['iconOccurrences'].pop(0)
            source['counts']['localNumberDisplayOccurrences']-=1; source['counts']['functionalIconOccurrences']-=1
        self.assertIn('Queen Health exact local/icon occurrence projection',run_mutation(lose_local_icon))

        def swap_local_numbers(data):
            first=data['queen-health-source-index.json']['faces'][0]['iconOccurrences'][0]
            fourth=data['queen-health-source-index.json']['faces'][3]['iconOccurrences'][0]
            first['printedNumericValue'],fourth['printedNumericValue']=fourth['printedNumericValue'],first['printedNumericValue']
        self.assertIn('Queen Health local number no-alias/value lock',run_mutation(swap_local_numbers))

        def drift_track(data):
            data['queen-health-source-index.json']['queenHitsTrack']['spacesInPrintedOrder'][4]['printedValue']=5
        self.assertIn('Queen Health track/terminal local-symbol no-alias lock',run_mutation(drift_track))

        def drift_body_punctuation(data):
            face=data['queen-health-source-index.json']['faces'][2]
            face['printedBody']=face['printedBody'].replace('Activate the Queen.','Activate the Queen!')
        self.assertIn('Queen Health exact body/order/punctuation lock',run_mutation(drift_body_punctuation))

        def reorder_panels(data):
            panels=data['queen-health-source-index.json']['faces'][2]['panels']; panels[0],panels[1]=panels[1],panels[0]
            panels[0]['readingOrder']=1; panels[1]['readingOrder']=2
        self.assertIn('Queen Health exact two-panel roles/order',run_mutation(reorder_panels))

        def invent_reset_overflow(data):
            rule=next(row for row in data['pilots.json']['records'] if row['ruleId']=='SEM-QUEEN-HEALTH-RESOLUTION-001')
            reset=next(row for row in rule['operations'] if row['operationType']=='change-value')
            reset['valueChange']['overflowCarry']=True
        self.assertIn('Queen Health draw/hidden-discard/effect/drawn-discard/reset/no-reshuffle order lock',run_mutation(invent_reset_overflow))

        def lose_variants(data):
            rule=next(row for row in data['pilots.json']['records'] if row['ruleId']=='SEM-QUEEN-HEALTH-504100-717B23-001')
            removed=len(rule['sourceVariants']); rule['sourceVariants']=[]; data['pilots.json']['counts']['variantReferences']-=removed
        self.assertIn('Queen Health licensed/official source-variant closure',run_mutation(lose_variants))

        def lose_dispatch_source_assertion(data):
            rule=next(row for row in data['pilots.json']['records'] if row['ruleId']=='SEM-QUEEN-HEALTH-RESOLUTION-001')
            removed=rule['sourceAssertions'].pop(1)['assertionId']
            next(row for row in rule['operations'] if row.get('dispatchRuleIds'))['sourceAssertionIds'].remove(removed)
            data['pilots.json']['counts']['sourceAssertions']-=1
        self.assertIn('Queen Health exact dispatcher source-assertion closure',run_mutation(lose_dispatch_source_assertion))

        def invert_authority(data):
            rule=next(row for row in data['pilots.json']['records'] if row['ruleId']=='SEM-QUEEN-HEALTH-458100-6BA0A2-001')
            rule['authority']['highest']='licensed-digital-secondary'
        self.assertIn('Queen Health face authority/physical-title lock',run_mutation(invert_authority))

        def invent_branch_default(data):
            question=next(row for row in data['review-gates.json']['questions'] if row['questionId']=='SEM-Q-028')
            question['defaultProhibited']=False
            rule=next(row for row in data['pilots.json']['records'] if row['ruleId']=='SEM-QUEEN-HEALTH-458100-6BA0A2-001')
            rule['decisions'][0].update({'selectionMode':'player-choice','ownerRef':'P-DRAWING-CHARACTER'})
        checks=run_mutation(invent_branch_default)
        self.assertIn('Queen Health Malfunction/Unreinforce no invented branch owner/default',checks)
        self.assertIn('Queen Health ambiguity no-default alternatives/linkage',checks)

        def invent_duplicate_ordinal_pairing(data):
            candidates=data['queen-health-source-index.json']['faces'][3]['bgaVariantCandidates']
            candidates['candidateKeys']=['QueenHealthCard4']; candidates['candidates']=candidates['candidates'][:1]
            candidates['oneToOneCopyAssignmentAsserted']=True
        self.assertIn('Queen Health licensed variant/candidate-copy boundary',run_mutation(invent_duplicate_ordinal_pairing))

        def lower_backlog_coordinated(data):
            target='CARD:648b81223c8c8b65'; backlog=data['backlog.json']
            backlog['units']=[row for row in backlog['units'] if row['semanticUnitId']!=target]
            backlog['counts']['units']-=1; backlog['counts']['byChannel']['card-reference-source-tuple']-=1; backlog['counts']['byStatus']['pilot-covered']-=1
            source=data['queen-health-source-index.json']; ledger=source['familyCountEvidence']['backlog']
            ledger['faceUnitIds'].remove(target); ledger['linkedUnitIds'].remove(target); ledger['faceTupleCount']-=1
            source['counts']['backlogTuples']-=1; source['counts']['backlogObligationsLinked']-=1
        checks=run_mutation(lower_backlog_coordinated)
        self.assertIn('Queen Health exact backlog tuple projection',checks)
        self.assertIn('Queen Health exact overlapping backlog-obligation closure',checks)

    def test_base_event_family_semantic_closure(self):
        source=load(DIR/'event-source-index.json')
        registry={row['sourceId']:row for row in load(DIR/'source-registry.json')['sources']}
        pilots=load(DIR/'pilots.json'); by_id={row['ruleId']:row for row in pilots['records']}
        backlog={row['semanticUnitId']:row for row in load(DIR/'backlog.json')['units']}
        self.assertEqual(source['counts'],{
            'eventIdentities':20,'ttsFaceOccurrences':20,'ttsSharedBackOccurrencesExcluded':1,
            'canonicalCorpusFaces':19,'sourceBoundDraftFaces':1,'licensedDigitalOccurrences':20,
            'officialVisibleComponentOccurrences':4,'backlogTuples':20,
        })
        self.assertEqual([row['ttsCardId'] for row in source['events']],list(range(5609,5629)))
        event_rule_ids=[row['semanticRuleId'] for row in source['events']]
        self.assertEqual(len(event_rule_ids),len(set(event_rule_ids)))
        for event in source['events']:
            rule=by_id[event['semanticRuleId']]
            registered=registry[event['sourceId']]
            self.assertEqual((registered['path'],registered['sha256'],registered['occurrenceId']),(event['sourcePath'],event['sourceSha256'],event['eventOccurrenceId']))
            self.assertFalse(event['joinEvidence']['titleOnlyJoin'])
            self.assertEqual(backlog[event['backlogUnitId']]['pilotRuleIds'],[event['semanticRuleId']])
            self.assertEqual(backlog[event['backlogUnitId']]['status'],'pilot-covered')
            sentence_ids=[row['sentenceId'] for row in event['sentences']]
            operation_sentences=[row['sourceSentenceId'] for row in rule['operations']]
            self.assertEqual(list(dict.fromkeys(operation_sentences)),sentence_ids)
            self.assertEqual(rule['partialResolution']['policy'],'per-sentence-continue')
            self.assertEqual(len(rule['sourceVariants']),1)
            self.assertEqual(rule['sourceVariants'][0]['sourceId'],'SRC-BGA-EVENTS')
        generic=by_id['SEM-EVENT-GENERAL-001']
        dispatch=next(row['dispatchRuleIds'] for row in generic['operations'] if row.get('dispatchRuleIds'))
        self.assertEqual(dispatch,event_rule_ids)
        self.assertIn('OQ-009',by_id['SEM-EVENT-EGG-PROTECTION-001']['unresolvedQuestionRefs'])
        self.assertIn('OQ-007',by_id['SEM-EVENT-EGG-PROTECTION-001']['unresolvedQuestionRefs'])
        leaving=by_id['SEM-EVENT-LEAVING-THE-SHELL-001']
        self.assertIn('SEM-Q-006',leaving['unresolvedQuestionRefs'])
        self.assertNotIn('icon.actionCard',leaving['termRefs'])
        self.assertEqual(sum(row['operationType']=='resolve-open-alternative' and 'SEM-Q-006' in row['objectRef'] for row in leaving['operations']),3)
        for rule_id in ('SEM-EVENT-LEAVING-THE-SHELL-001','SEM-EVENT-REACTOR-OVERHEATING-001'):
            transitions=[row.get('transition') or {} for row in by_id[rule_id]['operations']]
            self.assertTrue(any(row.get('to')=='tax.scaffold.zone.deck' for row in transitions))

    def test_event_specific_adversarial_corruptions_are_rejected(self):
        def run_mutation(mutate):
            with tempfile.TemporaryDirectory(prefix='semantic-event-negative-') as temp_dir:
                root=Path(temp_dir)
                data={name:load(DIR/name) for name in FILES}
                mutate(data)
                for name,payload in data.items():
                    (root/name).write_text(json.dumps(payload,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
                run,report=self.run_validator(root,skip=True)
            self.assertNotEqual(run.returncode,0)
            return {failure['check'] for failure in report['failures']}

        def drop_event(data):
            pilots=data['pilots.json']; coverage=data['coverage.json']
            target='SEM-EVENT-SYSTEM-FAILURE-001'
            pilots['records']=[row for row in pilots['records'] if row['ruleId']!=target]
            pilots['counts']['records']-=1
            for system in coverage['systems']:
                system['ruleIds']=[rule_id for rule_id in system['ruleIds'] if rule_id!=target]
            coverage['counts']['pilotRecords']-=1
        self.assertIn('Event semantic record closure',run_mutation(drop_event))

        def swap_source(data):
            by_id={row['ruleId']:row for row in data['pilots.json']['records']}
            source_by_id={row['sourceId']:row for row in data['source-registry.json']['sources']}
            assertion=next(row for row in by_id['SEM-EVENT-SYSTEM-FAILURE-001']['sourceAssertions'] if row['assertionId']=='SA-EVT-5609-SCAN')
            replacement=source_by_id['SRC-EVENT-5610']
            assertion.update({'sourceId':replacement['sourceId'],'sourcePath':replacement['path'],'sourceSha256':replacement['sha256'],'sourceAuthority':replacement['authority'],'sourceVersion':replacement['version']})
        self.assertIn('Event exact scan assertion projection',run_mutation(swap_source))

        def title_only_join(data):
            join=data['event-source-index.json']['events'][0]['joinEvidence']
            join.update({'identityJoin':'display title','titleOnlyJoin':True,'basis':['display title']})
        self.assertIn('Event title-only join prohibited',run_mutation(title_only_join))

        def reorder_sentences(data):
            by_id={row['ruleId']:row for row in data['pilots.json']['records']}
            first,second=by_id['SEM-EVENT-SYSTEM-FAILURE-001']['operations'][:2]
            first['sourceSentenceId'],second['sourceSentenceId']=second['sourceSentenceId'],first['sourceSentenceId']
            first['sourceSection'],second['sourceSection']=second['sourceSection'],first['sourceSection']
        self.assertIn('Event semantic sentence-order projection',run_mutation(reorder_sentences))

        def invent_default(data):
            question=next(row for row in data['review-gates.json']['questions'] if row['questionId']=='SEM-Q-006')
            question['defaultProhibited']=False
            leaving=next(row for row in data['pilots.json']['records'] if row['ruleId']=='SEM-EVENT-LEAVING-THE-SHELL-001')
            leaving['termRefs'].append('icon.actionCard'); leaving['termRefs'].sort()
        checks=run_mutation(invent_default)
        self.assertIn('semantic question no-default/linkage',checks)
        self.assertIn('Leaving the Shell no invented glyph default',checks)

        def lose_variant(data):
            event=next(row for row in data['pilots.json']['records'] if row['ruleId']=='SEM-EVENT-NO-WAY-OUT-001')
            event['sourceVariants']=[]
            data['pilots.json']['counts']['variantReferences']-=1
        self.assertIn('Event licensed source-variant closure',run_mutation(lose_variant))

        def invert_authority(data):
            event=next(row for row in data['pilots.json']['records'] if row['ruleId']=='SEM-EVENT-SYSTEM-FAILURE-001')
            event['authority']['highest']='source-bound-component-scan'
        self.assertIn('Event authority lock',run_mutation(invert_authority))

        def lower_backlog(data):
            backlog=data['backlog.json']; target='CARD:0d5da2c8e1b6ccb6'
            backlog['units']=[row for row in backlog['units'] if row['semanticUnitId']!=target]
            backlog['counts']['units']-=1
            backlog['counts']['byChannel']['card-reference-source-tuple']-=1
            backlog['counts']['byStatus']['pilot-covered']-=1
        self.assertIn('Event exact backlog tuple projection',run_mutation(lower_backlog))

    def test_adversarial_corruptions_are_rejected(self):
        with tempfile.TemporaryDirectory(prefix='semantic-negative-') as temp_dir:
            root=Path(temp_dir)
            for name in FILES: (root/name).write_text((DIR/name).read_text(encoding='utf-8'),encoding='utf-8')
            sources=load(root/'source-registry.json'); room_icons=load(root/'room-icon-denotations.json'); pilots=load(root/'pilots.json'); review=load(root/'review-gates.json'); contradictions=load(root/'contradictions.json'); coverage=load(root/'coverage.json'); backlog=load(root/'backlog.json')
            sources['sources'][0]['sha256']='0'*64
            record=next(row for row in pilots['records'] if row['ruleId']=='SEM-ACTION-CARD-DRAW-001')
            record['unexpectedField']='implementation leak'
            record['termRefs'][0]='term.missing'
            record['taxonRefs'][0]='tax.missing'
            record['authority']['highest']='source-bound-component-scan'
            record['operations'][1]['sequence']=record['operations'][0]['sequence']
            record['operations'][0]['sourceAssertionIds']=['SA-MISSING']
            if record['decisions']:
                record['decisions'][0]['ownerRef']='P-MISSING'
                record['decisions'][0]['cardinality']={'min':2,'max':1}
            else:
                record['decisions']=[{'decisionId':'D-BAD','ownerRef':'P-MISSING','selectionMode':'player-choice','cardinality':{'min':2,'max':1},'declineAllowed':False,'visibility':'public','options':['bad']}]
            record['partialResolution']['policy']='invented-policy'
            record['implementationBoundary']='engine.js mapping'
            hatching=next(r for r in pilots['records'] if r['ruleId']=='SEM-EVENT-HATCHING-001')
            hatching['partialResolution']['policy']='all-or-nothing-selection'
            hatching['unresolvedQuestionRefs']=[]
            rest=next(r for r in pilots['records'] if r['ruleId']=='SEM-ACT-REST-001')
            rest['sourceVariants'][0]['sourceId']='SRC-MISSING'
            review['questions'][0]['defaultProhibited']=False
            contradictions['conflicts'][2]['questionId']='SEM-Q-MISSING'
            room_icons['denotations'][0]['semanticReferenceId']='icon.missing'
            coverage['systems'][0]['ruleIds'].append(coverage['systems'][1]['ruleIds'][0])
            pending=next(item for item in backlog['units'] if item['status']=='pending')
            pending['status']='pilot-covered'
            for name,data in [('source-registry.json',sources),('room-icon-denotations.json',room_icons),('pilots.json',pilots),('review-gates.json',review),('contradictions.json',contradictions),('coverage.json',coverage),('backlog.json',backlog)]:
                (root/name).write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
            run,report=self.run_validator(root,skip=True)
        self.assertNotEqual(run.returncode,0)
        checks={f['check'] for f in report['failures']}
        required={'source tuple','record schema fields','implementation boundary','controlled term references','taxon references','record authority precedence','operation IDs/order','operation source linkage','decision completeness','decision usage closure','partial-resolution completeness','source variant completeness','semantic question no-default/linkage','semantic conflict question linkage','Room Help icon denotation projection','Event partial/Nest ambiguity fidelity','semantic pilot coverage projection','semantic backlog status/link consistency','hard-coded semantic pilot counts'}
        self.assertTrue(required.issubset(checks),sorted(checks))

    def test_duplicate_json_keys_are_rejected(self):
        with tempfile.TemporaryDirectory(prefix='semantic-duplicate-') as temp_dir:
            root=Path(temp_dir)
            for name in FILES:
                text=(DIR/name).read_text(encoding='utf-8')
                if name=='pilots.json': text=text.replace('"schemaVersion": 1,','"schemaVersion": 1,\n  "schemaVersion": 1,',1)
                (root/name).write_text(text,encoding='utf-8')
            run,report=self.run_validator(root,skip=True)
        self.assertNotEqual(run.returncode,0)
        self.assertEqual(report['failures'][0]['check'],'strict JSON parsing')

    def test_audit_specific_semantic_corruptions_are_rejected(self):
        with tempfile.TemporaryDirectory(prefix='semantic-audit-negative-') as temp_dir:
            root=Path(temp_dir)
            for name in FILES: (root/name).write_text((DIR/name).read_text(encoding='utf-8'),encoding='utf-8')
            room_icons=load(root/'room-icon-denotations.json'); pilots=load(root/'pilots.json')
            next(row for row in room_icons['denotations'] if row['occurrenceId']=='R08-I05')['semanticReferenceId']='icon.robot'
            by_id={row['ruleId']:row for row in pilots['records']}
            token_repeat=next(op for op in by_id['SEM-IH-QA-C-02']['operations'] if op['operationType']=='place-component')['repeat']
            token_repeat['tokenFaceResolutions']['2']['adultCount']=99
            next(op for op in by_id['SEM-NOISE-HAZARD-001']['operations'] if op.get('dispatchRuleIds')).pop('dispatchRuleIds')
            by_id['SEM-RT-011']['operations'][2]['invokeRuleId']='SEM-IH-QD-B-02'
            hatch_assertion=next(row for row in by_id['SEM-EVENT-HATCHING-001']['sourceAssertions'] if row['assertionId']=='SA-EVT-5616-SCAN')
            hatch_assertion['supportsFields']=[field for field in hatch_assertion['supportsFields'] if field!='operations']
            (root/'room-icon-denotations.json').write_text(json.dumps(room_icons,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
            (root/'pilots.json').write_text(json.dumps({'schemaVersion':1,'recordType':'semantic-rule-pilot-corpus','scope':'test','counts':pilots['counts'],'records':list(by_id.values())},indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
            run,report=self.run_validator(root,skip=True)
        self.assertNotEqual(run.returncode,0)
        checks={failure['check'] for failure in report['failures']}
        self.assertTrue({'independently locked Room icon denotation map','Room-context exact Help dispatch','Bag Development exact Queen-side Help dispatch','Intruder Help token-back count/color','operation assertion support'}.issubset(checks),sorted(checks))


if __name__=='__main__': unittest.main()
