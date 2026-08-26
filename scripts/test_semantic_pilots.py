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
FILES=('event-source-index.json','exploration-source-index.json','source-registry.json','semantic-rule.schema.json','semantic-vocabulary.json','room-icon-denotations.json','pilots.json','review-gates.json','contradictions.json','coverage.json','backlog.json')


def load(path): return json.loads(path.read_text(encoding='utf-8'))


class SemanticPilotTests(unittest.TestCase):
    def run_validator(self, root=None, skip=False):
        base=root or DIR
        command=['python3',str(VALIDATOR),'--event-source-index',str(base/'event-source-index.json'),'--exploration-source-index',str(base/'exploration-source-index.json'),'--source-registry',str(base/'source-registry.json'),'--schema',str(base/'semantic-rule.schema.json'),'--semantic-vocabulary',str(base/'semantic-vocabulary.json'),'--room-icon-denotations',str(base/'room-icon-denotations.json'),'--pilots',str(base/'pilots.json'),'--review-gates',str(base/'review-gates.json'),'--contradictions',str(base/'contradictions.json'),'--coverage',str(base/'coverage.json'),'--backlog',str(base/'backlog.json')]
        if skip: command.append('--skip-reproducibility')
        run=subprocess.run(command,cwd=REPO,check=False,capture_output=True,text=True,timeout=300)
        return run,json.loads(run.stdout)

    def test_current_pilot_passes_and_rebuilds(self):
        run,report=self.run_validator()
        self.assertEqual(run.returncode,0,run.stdout+run.stderr)
        self.assertTrue(report['passed'])
        self.assertEqual(report['checks']['records'],111)
        self.assertEqual(report['checks']['operations'],500)
        self.assertEqual(report['checks']['decisions'],49)
        self.assertEqual(report['checks']['targets'],142)
        self.assertEqual(report['checks']['openQuestions'],17)
        self.assertEqual(report['checks']['semanticNodes'],22)
        self.assertEqual(report['checks']['conflicts'],13)
        self.assertEqual(report['checks']['backlogUnits'],600)
        self.assertEqual(report['checks']['backlogPilotCovered'],119)
        self.assertEqual(report['checks']['eventIdentities'],20)
        self.assertEqual(report['checks']['eventRecords'],20)
        self.assertEqual(report['checks']['eventBacklogTuples'],20)
        self.assertEqual(report['checks']['explorationIdentities'],12)
        self.assertEqual(report['checks']['explorationRecords'],12)
        self.assertEqual(report['checks']['explorationPrintedSentences'],46)
        self.assertEqual(report['checks']['explorationIconOccurrences'],60)
        self.assertEqual(report['checks']['explorationBacklogTuples'],12)
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
            record=pilots['records'][0]
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
