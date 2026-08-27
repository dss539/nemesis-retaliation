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
FILES=('event-source-index.json','exploration-source-index.json','robot-source-index.json','attack-source-index.json','queen-health-source-index.json','serious-wound-source-index.json','green-item-source-index.json','red-item-source-index.json','yellow-item-source-index.json','equipment-source-index.json','action-source-index.json','objective-mission-source-index.json','combat-source-index.json','source-registry.json','semantic-rule.schema.json','semantic-vocabulary.json','room-icon-denotations.json','pilots.json','review-gates.json','contradictions.json','coverage.json','backlog.json')


def load(path): return json.loads(path.read_text(encoding='utf-8'))


class SemanticPilotTests(unittest.TestCase):
    def run_validator(self, root=None, skip=False):
        base=root or DIR
        command=['python3',str(VALIDATOR),'--event-source-index',str(base/'event-source-index.json'),'--exploration-source-index',str(base/'exploration-source-index.json'),'--robot-source-index',str(base/'robot-source-index.json'),'--attack-source-index',str(base/'attack-source-index.json'),'--queen-health-source-index',str(base/'queen-health-source-index.json'),'--serious-wound-source-index',str(base/'serious-wound-source-index.json'),'--green-item-source-index',str(base/'green-item-source-index.json'),'--red-item-source-index',str(base/'red-item-source-index.json'),'--yellow-item-source-index',str(base/'yellow-item-source-index.json'),'--equipment-source-index',str(base/'equipment-source-index.json'),'--action-source-index',str(base/'action-source-index.json'),'--objective-source-index',str(base/'objective-mission-source-index.json'),'--combat-source-index',str(base/'combat-source-index.json'),'--source-registry',str(base/'source-registry.json'),'--schema',str(base/'semantic-rule.schema.json'),'--semantic-vocabulary',str(base/'semantic-vocabulary.json'),'--room-icon-denotations',str(base/'room-icon-denotations.json'),'--pilots',str(base/'pilots.json'),'--review-gates',str(base/'review-gates.json'),'--contradictions',str(base/'contradictions.json'),'--coverage',str(base/'coverage.json'),'--backlog',str(base/'backlog.json')]
        if skip: command.append('--skip-reproducibility')
        run=subprocess.run(command,cwd=REPO,check=False,capture_output=True,text=True,timeout=300)
        return run,json.loads(run.stdout)

    def test_current_pilot_passes_and_rebuilds(self):
        run,report=self.run_validator()
        self.assertEqual(run.returncode,0,run.stdout+run.stderr)
        self.assertTrue(report['passed'])
        self.assertEqual(report['checks']['records'],520)
        self.assertEqual(report['checks']['operations'],2220)
        self.assertEqual(report['checks']['decisions'],336)
        self.assertEqual(report['checks']['targets'],556)
        self.assertEqual(report['checks']['conditions'],1541)
        self.assertEqual(report['checks']['openQuestionReferences'],576)
        self.assertEqual(report['checks']['openQuestions'],110)
        self.assertEqual(report['checks']['semanticNodes'],26)
        self.assertEqual(report['checks']['conflicts'],82)
        self.assertEqual(report['checks']['backlogUnits'],600)
        self.assertEqual(report['checks']['backlogPilotCovered'],510)
        self.assertEqual(report['checks']['sources'],468)
        self.assertEqual(report['checks']['systems'],25)
        self.assertEqual(report['checks']['equipmentTtsPhysicalFaceRecords'],39)
        self.assertEqual(report['checks']['equipmentOfficialFaceRecords'],6)
        self.assertEqual(report['checks']['equipmentClassConflictExclusions'],12)
        self.assertEqual(report['checks']['equipmentBacklogSourceFaceTuples'],52)
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
        self.assertEqual(report['checks']['seriousWoundPhysicalOccurrences'],27)
        self.assertEqual(report['checks']['seriousWoundUniqueTitles'],9)
        self.assertEqual(report['checks']['seriousWoundSelectedFaceAssets'],9)
        self.assertEqual(report['checks']['seriousWoundSourceFaceAssets'],11)
        self.assertEqual(report['checks']['seriousWoundPhysicalRegions'],81)
        self.assertEqual(report['checks']['seriousWoundPrintedSentences'],42)
        self.assertEqual(report['checks']['seriousWoundFunctionalIconOccurrences'],30)
        self.assertEqual(report['checks']['seriousWoundRecords'],27)
        self.assertEqual(report['checks']['seriousWoundBacklogTuples'],11)
        self.assertEqual(report['checks']['greenItemRootOccurrences'],30)
        self.assertEqual(report['checks']['greenItemPhysicalOccurrences'],23)
        self.assertEqual(report['checks']['greenItemExcludedHeavyOccurrences'],7)
        self.assertEqual(report['checks']['greenItemUniqueTitles'],8)
        self.assertEqual(report['checks']['greenItemSelectedFaceAssets'],8)
        self.assertEqual(report['checks']['greenItemSourceFaceAssets'],14)
        self.assertEqual(report['checks']['greenItemPhysicalPanels'],85)
        self.assertEqual(report['checks']['greenItemPrintedSentences'],46)
        self.assertEqual(report['checks']['greenItemFunctionalIconOccurrences'],46)
        self.assertEqual(report['checks']['greenItemRecords'],23)
        self.assertEqual(report['checks']['greenItemBacklogTuples'],12)
        self.assertEqual(report['checks']['redItemRootOccurrences'],30)
        self.assertEqual(report['checks']['redItemRegularOccurrences'],21)
        self.assertEqual(report['checks']['redItemExcludedHeavyOccurrences'],3)
        self.assertEqual(report['checks']['redItemClassConflictOccurrences'],6)
        self.assertEqual(report['checks']['redItemUniqueTitles'],7)
        self.assertEqual(report['checks']['redItemSelectedFaceAssets'],7)
        self.assertEqual(report['checks']['redItemSourceFaceAssets'],16)
        self.assertEqual(report['checks']['redItemPhysicalPanels'],87)
        self.assertEqual(report['checks']['redItemPrintedSentences'],45)
        self.assertEqual(report['checks']['redItemFunctionalIconOccurrences'],27)
        self.assertEqual(report['checks']['redItemRecords'],21)
        self.assertEqual(report['checks']['redItemBacklogTuples'],11)
        self.assertEqual(report['checks']['yellowItemRootOccurrences'],30)
        self.assertEqual(report['checks']['yellowItemRegularOccurrences'],24)
        self.assertEqual(report['checks']['yellowItemExplicitHeavyOccurrences'],0)
        self.assertEqual(report['checks']['yellowItemClassConflictOccurrences'],6)
        self.assertEqual(report['checks']['yellowItemUniqueTitles'],4)
        self.assertEqual(report['checks']['yellowItemSelectedFaceAssets'],4)
        self.assertEqual(report['checks']['yellowItemSourceFaceAssets'],11)
        self.assertEqual(report['checks']['yellowItemPhysicalPanels'],128)
        self.assertEqual(report['checks']['yellowItemPrintedSentences'],56)
        self.assertEqual(report['checks']['yellowItemFunctionalIconOccurrences'],48)
        self.assertEqual(report['checks']['yellowItemRecords'],24)
        self.assertEqual(report['checks']['yellowItemBacklogTuples'],7)
        self.assertEqual(report['checks']['actionPhysicalOccurrences'],60)
        self.assertEqual(report['checks']['actionCharacterDecks'],6)
        self.assertEqual(report['checks']['actionRootDecks'],7)
        self.assertEqual(report['checks']['actionSourceFaceAssets'],89)
        self.assertEqual(report['checks']['actionGeneratedOccurrences'],21)
        self.assertEqual(report['checks']['actionDirectOccurrences'],39)
        self.assertEqual(report['checks']['actionSelectorGaps'],29)
        self.assertEqual(report['checks']['actionSharedBackReferences'],273)
        self.assertEqual(report['checks']['actionUniqueTitles'],32)
        self.assertEqual(report['checks']['actionPhysicalPanels'],290)
        self.assertEqual(report['checks']['actionPrintedSentences'],164)
        self.assertEqual(report['checks']['actionFunctionalIconOccurrences'],143)
        self.assertEqual(report['checks']['actionResolvedNotInCombatOccurrences'],28)
        self.assertEqual(report['checks']['actionUnresolvedUpperRightOccurrences'],8)
        self.assertEqual(report['checks']['actionCommandHeadings'],8)
        self.assertEqual(report['checks']['actionReactionHeadings'],6)
        self.assertEqual(report['checks']['actionLicensedOccurrences'],60)
        self.assertEqual(report['checks']['actionRecords'],60)
        self.assertEqual(report['checks']['actionBacklogTuples'],89)
        self.assertEqual(report['checks']['objectivePhysicalOccurrences'],30)
        self.assertEqual(report['checks']['objectiveMissionPhysicalOccurrences'],7)
        self.assertEqual(report['checks']['objectivePrivatePhysicalOccurrences'],15)
        self.assertEqual(report['checks']['missionTaskPhysicalOccurrences'],8)
        self.assertEqual(report['checks']['objectiveSourceClearPhysicalOccurrences'],29)
        self.assertEqual(report['checks']['objectiveSourceBlockedPhysicalOccurrences'],1)
        self.assertEqual(report['checks']['objectiveGeneratedPhysicalOccurrences'],16)
        self.assertEqual(report['checks']['objectiveDirectPhysicalOccurrences'],14)
        self.assertEqual(report['checks']['objectivePrototypePhysicalExclusions'],9)
        self.assertEqual(report['checks']['objectiveSoloCoopPhysicalExclusions'],38)
        self.assertEqual(report['checks']['objectiveSourceFaceAssets'],50)
        self.assertEqual(report['checks']['objectiveSelectorGapAssets'],18)
        self.assertEqual(report['checks']['objectiveSourceSheetCells'],31)
        self.assertEqual(report['checks']['objectiveSharedBackReferences'],44)
        self.assertEqual(report['checks']['objectivePhysicalPanels'],149)
        self.assertEqual(report['checks']['objectivePrintedSentences'],53)
        self.assertEqual(report['checks']['objectiveFunctionalIconOccurrences'],39)
        self.assertEqual(report['checks']['objectiveOfficialHelpUnits'],45)
        self.assertEqual(report['checks']['objectiveOfficialVisibleUnits'],35)
        self.assertEqual(report['checks']['objectiveOfficialOccludedUnits'],10)
        self.assertEqual(report['checks']['objectiveLicensedRows'],38)
        self.assertEqual(report['checks']['objectiveLicensedCompetitiveRows'],26)
        self.assertEqual(report['checks']['objectiveSemanticFamilyRecords'],85)
        self.assertEqual(report['checks']['objectiveCardBacklogTuples'],50)
        self.assertEqual(report['checks']['objectiveCoveredCardBacklogTuples'],49)
        self.assertEqual(report['checks']['objectiveHelpBacklogUnits'],45)
        self.assertEqual(report['checks']['roomIconDenotations'],112)

    def test_high_risk_semantic_boundaries(self):
        pilots=load(DIR/'pilots.json'); by_id={r['ruleId']:r for r in pilots['records']}
        search_bottom=next(item for item in by_id['SEM-ACT-SEARCH-001']['operations'] if (item.get('transition') or {}).get('positionRef')=='sem.position.deck-bottom')
        self.assertEqual(search_bottom['transition']['to'],'tax.scaffold.zone.deck')
        self.assertIn('SEM-Q-040',by_id['SEM-ACT-SEARCH-001']['unresolvedQuestionRefs'])
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

    def test_endgame_larva_step_time_resolution_and_negative_controls(self):
        pilots=load(DIR/'pilots.json'); review=load(DIR/'review-gates.json')
        endgame=next(row for row in pilots['records'] if row['ruleId']=='SEM-ENDGAME-001')
        step=next(row for row in endgame['operations'] if row['stepId']=='S04')
        guard=next(row for row in endgame['preconditions'] if row['conditionId']=='S04-C01')
        self.assertEqual(endgame['unresolvedQuestionRefs'],['OQ-001','SEM-Q-077','SEM-Q-078'])
        self.assertNotIn('OQ-002',{row['questionId'] for row in review['questions']})
        self.assertIn('when the Eclosion cohort step is reached',step['subjectRef'])
        self.assertIn('during this Sequence',step['notes'])
        self.assertIn('preceding Infection step',guard['expression']['args'][0]['predicate'])

        def run_mutation(mutate):
            with tempfile.TemporaryDirectory(prefix='semantic-endgame-negative-') as temp_dir:
                root=Path(temp_dir)
                data={name:load(DIR/name) for name in FILES}
                mutate(data)
                for name,payload in data.items():
                    (root/name).write_text(json.dumps(payload,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
                run,report=self.run_validator(root,skip=True)
            self.assertNotEqual(run.returncode,0)
            return {failure['check'] for failure in report['failures']}

        def reintroduce_snapshot(data):
            record=next(row for row in data['pilots.json']['records'] if row['ruleId']=='SEM-ENDGAME-001')
            operation=next(row for row in record['operations'] if row['stepId']=='S04')
            operation['subjectRef']='each alive Escaped/Hibernated Character who had a Larva at the start of endgame'
            operation['notes']='Larva eligibility is snapshotted at the start of endgame.'
            condition=next(row for row in record['preconditions'] if row['conditionId']=='S04-C01')
            condition['expression']['args'][0]['predicate']='Character had a Larva on their Character board at the start of endgame'
            record['unresolvedQuestionRefs'].append('OQ-002')
            data['pilots.json']['counts']['openQuestionReferences']+=1
            review=data['review-gates.json']
            review['questions'].insert(1,{'questionId':'OQ-002','title':'Endgame Larva iteration timing','decisionClass':'official-clarification-preferred','blocksRuleIds':['SEM-ENDGAME-001'],'plannedRuleIds':[],'defaultProhibited':True,'sourceEvidenceRefs':['docs/rules/open-questions.md:OQ-002'],'alternatives':[{'alternativeId':'OQ-002-A','description':'Evaluate eligibility at the Eclosion cohort step.','support':'ordered source text'},{'alternativeId':'OQ-002-B','description':'Snapshot Larva status at the start of endgame.','support':'superseded alternative'}]})
            review['counts'].update({'questions':44,'officialClarificationPreferred':16,'open':44})
        self.assertIn('Endgame Larva step-time official-source lock',run_mutation(reintroduce_snapshot))

        def remove_during_sequence_eligibility(data):
            record=next(row for row in data['pilots.json']['records'] if row['ruleId']=='SEM-ENDGAME-001')
            assertion=next(row for row in record['sourceAssertions'] if row['assertionId']=='SA-END-1')
            assertion['sourceText']=assertion['sourceText'].replace('during this Sequence','earlier in the game')
            operation=next(row for row in record['operations'] if row['stepId']=='S04')
            operation['notes']='Eligibility is evaluated at S04 after S03.'
            condition=next(row for row in record['preconditions'] if row['conditionId']=='S04-C01')
            condition['expression']['args'][0]['predicate']='Character has a Larva on their Character board when the Eclosion cohort step is reached'
        self.assertIn('Endgame Larva step-time official-source lock',run_mutation(remove_during_sequence_eligibility))

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

    def test_base_green_item_family_source_closure(self):
        source=load(DIR/'green-item-source-index.json')
        registry={row['sourceId']:row for row in load(DIR/'source-registry.json')['sources']}
        backlog={row['semanticUnitId']:row for row in load(DIR/'backlog.json')['units']}
        self.assertEqual(source['counts']['rootPhysicalOccurrences'],30)
        self.assertEqual(source['counts']['physicalFaceOccurrences'],23)
        self.assertEqual(source['counts']['excludedHeavyPhysicalOccurrences'],7)
        self.assertEqual(source['counts']['uniquePrintedTitles'],8)
        self.assertEqual(source['counts']['uniqueSelectedFaceAssets'],8)
        self.assertEqual(source['counts']['sourceFaceAssets'],14)
        self.assertEqual(source['counts']['generatedPhysicalFaceOccurrences'],15)
        self.assertEqual(source['counts']['directPhysicalFaceOccurrences'],8)
        self.assertEqual(source['counts']['sourceSheetCells'],9)
        self.assertEqual(source['counts']['selectedGeneratedCells'],5)
        self.assertEqual(source['counts']['selectorGapCells'],4)
        self.assertEqual(source['counts']['sharedBackSelectorReferences'],31)
        self.assertEqual(source['counts']['sourceSheetSelectorReferences'],16)
        self.assertEqual(source['counts']['physicalPanels'],85)
        self.assertEqual(source['counts']['operativePanels'],62)
        self.assertEqual(source['counts']['printedSentenceOccurrences'],46)
        self.assertEqual(source['counts']['physicalFunctionalIconOccurrences'],46)
        self.assertEqual(source['counts']['physicalMatchedIconOccurrences'],37)
        self.assertEqual(source['counts']['physicalUnresolvedLocalGlyphOccurrences'],9)
        self.assertEqual(source['counts']['selectorGapFunctionalIconOccurrences'],11)
        self.assertEqual(source['counts']['licensedDigitalOccurrences'],10)
        self.assertEqual(source['counts']['licensedDigitalPhysicalCopies'],30)
        self.assertEqual(source['counts']['licensedRegularPhysicalCopies'],23)
        self.assertEqual(source['counts']['licensedHeavyPhysicalCopies'],7)
        self.assertEqual(source['titleMultiplicity'],{
            'ADRENALINE\nINJECTION':3,'ANTISEPTIC':3,'CAFFEINE PILLS':3,'CONTAMINATION\nCODES':1,
            'EMERGENCY LIFE\nSUPPORT CODES':1,'MEDICAL\nSTAPLER':5,'MEDKIT':4,'STIMULANTS':3,
        })
        self.assertEqual([row['generatedCell'] for row in source['sourceFaceAssets'] if row['sourceRole']=='generated-cell-selector-gap-variant'],[2,4,6,8])
        self.assertEqual([row['rootSequence'] for row in source['excludedHeavyFaces']],list(range(9,16)))
        self.assertTrue(all(row['physicalClass']=='heavy-item' and row['semanticRuleId'] is None for row in source['excludedHeavyFaces']))
        self.assertTrue(all(row['physicalClass']=='regular-item' and row['batchDisposition']=='included-regular-green-item-face' for row in source['faces']))
        self.assertEqual(len({row['greenItemOccurrenceId'] for row in source['faces']}),23)
        self.assertEqual(len({row['ttsCardGuid'] for row in [*source['faces'],*source['excludedHeavyFaces']]}),30)
        self.assertEqual(source['sharedBack']['rulesTextPresent'],False)
        self.assertEqual(source['sharedBack']['separateRulesFace'],False)
        self.assertEqual(source['sourceSheet']['selectedCells'],[0,1,3,5,7])
        self.assertEqual(source['sourceSheet']['selectorGapCells'],[2,4,6,8])
        self.assertTrue(all(row['licensedCrosswalk']['status']=='not-asserted' and row['officialCrosswalk']['status']=='not-asserted' for row in [*source['faces'],*source['excludedHeavyFaces']]))
        self.assertTrue(all(row['exactGreenRulesFace'] is False for row in source['officialVisibleCounterparts']))
        for row in [*source['faces'],*source['excludedHeavyFaces']]:
            self.assertEqual(registry[row['sourceId']]['occurrenceId'],row['greenItemOccurrenceId'])
        for unit_id in source['familyCountEvidence']['backlog']['linkedUnitIds']:
            self.assertEqual(backlog[unit_id]['status'],'pilot-covered')
        for unit_id in source['familyCountEvidence']['backlog']['excludedHeavyUnitIds']:
            self.assertEqual(backlog[unit_id]['status'],'pilot-covered')
            self.assertTrue(any(rule_id.startswith('SEM-HEAVY-GREEN-') for rule_id in backlog[unit_id]['pilotRuleIds']))

    def test_base_green_item_family_semantic_closure(self):
        source=load(DIR/'green-item-source-index.json')
        by_id={row['ruleId']:row for row in load(DIR/'pilots.json')['records']}
        questions={row['questionId']:row for row in load(DIR/'review-gates.json')['questions']}
        face_rule_ids=[row['semanticRuleId'] for row in source['faces']]
        use=by_id['SEM-USE-ITEM-001']
        self.assertEqual(next(op['dispatchRuleIds'] for op in use['operations'] if op.get('stepId')=='S05')[:len(face_rule_ids)],face_rule_ids)
        self.assertEqual([op['operationType'] for op in use['operations']],['select-target','resolve-open-alternative','pay-cost','reveal','invoke-selected-process','invoke-selected-process'])
        self.assertEqual(use['costs'][0]['quantity'],1)
        self.assertEqual(use['unresolvedQuestionRefs'],['SEM-Q-039'])
        deck=by_id['SEM-GREEN-ITEM-DECK-001']
        self.assertEqual(deck['operations'][0]['repeat'],{'rootPhysicalCardCount':30,'regularBatchFaceCount':23,'excludedHeavyCount':7})
        self.assertFalse(any(op['operationType']=='shuffle' and 'discard' in op['objectRef'].lower() for op in deck['operations'][1:]))
        self.assertEqual(by_id['SEM-GREEN-ITEM-ONE-USE-001']['operations'][1]['transition']['to'],'tax.scaffold.zone.discard-pile')
        self.assertEqual(by_id['SEM-RESTORE-HEALTH-001']['decisions'][0]['ownerRef'],'P-RULES')
        self.assertEqual(by_id['SEM-RESTORE-HEALTH-001']['decisions'][0]['selectionMode'],'unresolved')
        self.assertTrue(by_id['SEM-GREEN-ITEM-IMMEDIATE-USE-001']['decisions'][0]['declineAllowed'])
        self.assertEqual(by_id['SEM-GREEN-ITEM-IMMEDIATE-USE-001']['decisions'][0]['cardinality'],{'min':0,'max':1})
        self.assertTrue(any(decision['selectionMode']=='mutual-consent' for decision in by_id['SEM-ITEM-TRADE-GAIN-001']['decisions']))
        self.assertTrue(any(decision['selectionMode']=='consent' for decision in by_id['SEM-ITEM-INTERPLAY-001']['decisions']))
        self.assertFalse(any(op.get('invokeRuleId') for op in by_id['SEM-ITEM-VOLUNTARY-DISCARD-001']['operations']))
        self.assertEqual(len(by_id['SEM-GREEN-ITEM-VARIANT-BOUNDARIES-001']['sourceVariants']),21)
        for row in source['faces']:
            rule=by_id[row['semanticRuleId']]
            self.assertEqual(rule['authority']['highest'],'official-primary')
            self.assertEqual(rule['sourceVariants'],[])
            self.assertEqual(len(row['regions']),3)
            self.assertEqual([region['role'] for region in row['regions']],['artwork-and-interface','identity-trait-and-restriction','operative-effect-body'])
            self.assertEqual(len(row['panels']),len(next(asset for asset in source['sourceFaceAssets'] if asset['assetKey']==row['sourceAssetKey'])['panels']))
            self.assertTrue(all(op['sourceSentenceId'] in {sentence['sentenceId'] for sentence in row['sentences']} for op in rule['operations']))
        local_rules=[by_id[row['semanticRuleId']] for row in source['faces'] if row['effectKind'] in {'adrenaline-action-window','restore-or-local-draw'}]
        self.assertTrue(all('icon.actionCard' not in rule['termRefs'] and 'SEM-Q-041' in rule['unresolvedQuestionRefs'] for rule in local_rules))
        for question_id in [f'SEM-Q-{index:03d}' for index in range(39,46)]:
            self.assertTrue(questions[question_id]['defaultProhibited'])
            self.assertEqual(len(questions[question_id]['alternatives']),3)

    def test_green_item_specific_adversarial_corruptions_are_rejected(self):
        def run_mutation(mutate):
            with tempfile.TemporaryDirectory(prefix='semantic-green-item-negative-') as temp_dir:
                root=Path(temp_dir)
                data={name:load(DIR/name) for name in FILES}
                mutate(data)
                for name,payload in data.items():
                    (root/name).write_text(json.dumps(payload,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
                run,report=self.run_validator(root,skip=True)
            self.assertNotEqual(run.returncode,0)
            return {failure['check'] for failure in report['failures']}

        def drop_copy(data):
            source=data['green-item-source-index.json']; source['faces']=source['faces'][1:]
            source['counts']['physicalFaceOccurrences']-=1; source['counts']['directPhysicalFaceOccurrences']-=1
        self.assertIn('Green Item source-index exact physical/root/Heavy occurrence count',run_mutation(drop_copy))

        def duplicate_copy(data):
            source=data['green-item-source-index.json']; source['faces'].append(json.loads(json.dumps(source['faces'][0])))
            source['counts']['physicalFaceOccurrences']+=1; source['counts']['directPhysicalFaceOccurrences']+=1
        self.assertIn('Green Item source-index exact physical/root/Heavy occurrence count',run_mutation(duplicate_copy))

        def collapse_title(data): data['green-item-source-index.json']['titleMultiplicity']['MEDICAL\nSTAPLER']=1
        self.assertIn('Green Item repeated-title/copy multiplicity no-collapse lock',run_mutation(collapse_title))

        def swap_cells(data):
            assets=data['green-item-source-index.json']['sourceFaceAssets']; a=next(row for row in assets if row['assetKey']=='sheet-00'); b=next(row for row in assets if row['assetKey']=='sheet-01'); a['generatedCell'],b['generatedCell']=b['generatedCell'],a['generatedCell']
        self.assertIn('Green Item independently locked source-face asset tuple',run_mutation(swap_cells))

        def invent_join(data):
            join=data['green-item-source-index.json']['faces'][0]['joinEvidence']; join.update({'identityJoin':'title/color/modulo','titleOnlyJoin':True,'colorOnlyJoin':True,'cardIdModuloJoin':True,'basis':['title','green','cardId % 100']})
        self.assertIn('Green Item title/color/body/folder/order/cell/modulo/licensed join prohibited',run_mutation(invent_join))

        def drift_selector(data): data['green-item-source-index.json']['faces'][0]['sourceSelector']['guid']='ffffff'
        self.assertIn('Green Item exact CardID/GUID/FaceURL/BackURL selector projection',run_mutation(drift_selector))

        def invert_face_back(data):
            source=data['green-item-source-index.json']; face=source['faces'][0]; face['sourceSelector'].update({'key':'BackURL','url':source['sharedBack']['sourceSelector']['url'],'sideRole':'shared-non-operative-green-item-back'})
        self.assertIn('Green Item exact CardID/GUID/FaceURL/BackURL selector projection',run_mutation(invert_face_back))

        def leak_heavy(data):
            source=data['green-item-source-index.json']; source['faces'].append(source['excludedHeavyFaces'].pop(0)); source['counts']['physicalFaceOccurrences']+=1; source['counts']['excludedHeavyPhysicalOccurrences']-=1
        self.assertIn('Green Item source-index exact physical/root/Heavy occurrence count',run_mutation(leak_heavy))

        def swap_panels(data):
            panels=data['green-item-source-index.json']['faces'][0]['panels']; panels[1],panels[2]=panels[2],panels[1]
        self.assertIn('Green Item exact physical panel roles/order/region linkage',run_mutation(swap_panels))

        def swap_icons(data):
            icons=data['green-item-source-index.json']['faces'][0]['iconOccurrences']; icons[0]['semanticReferenceId'],icons[1]['semanticReferenceId']=icons[1]['semanticReferenceId'],icons[0]['semanticReferenceId']
        self.assertIn('Green Item exact physical sentence/panel/icon projection',run_mutation(swap_icons))

        def drift_body(data): data['green-item-source-index.json']['faces'][0]['printedBody']=data['green-item-source-index.json']['faces'][0]['printedBody'].replace('Section.','Section!')
        self.assertIn('Green Item exact physical title/body/punctuation/order lock',run_mutation(drift_body))

        def invent_owner(data):
            rule=next(row for row in data['pilots.json']['records'] if row['ruleId']=='SEM-RESTORE-HEALTH-001'); rule['decisions'][0]['ownerRef']='P-USING-PLAYER'; rule['decisions'][0]['selectionMode']='player-choice'
        self.assertIn('Green Item consent/restore-owner/immediate-option/voluntary-no-use lock',run_mutation(invent_owner))

        def invent_default(data): next(row for row in data['review-gates.json']['questions'] if row['questionId']=='SEM-Q-041')['defaultProhibited']=False
        self.assertIn('Green Item ambiguity no-default alternatives/linkage',run_mutation(invent_default))

        def invent_reshuffle(data):
            pilots=data['pilots.json']; rule=next(row for row in pilots['records'] if row['ruleId']=='SEM-GREEN-ITEM-DECK-001'); op=json.loads(json.dumps(rule['operations'][0])); op['objectRef']='Green Item discard pile into deck'; rule['operations'].append(op)
            for index,item in enumerate(rule['operations'],1): item['stepId']=f'S{index:02d}'; item['sequence']=index
            pilots['counts']['operations']+=1
        self.assertIn('Green Item finite deck/root-class/exhaustion/no-reshuffle lock',run_mutation(invent_reshuffle))

        def invent_title_stacking(data):
            rule=next(row for row in data['pilots.json']['records'] if row['ruleId'].startswith('SEM-GREEN-ITEM-536600-')); rule['stacking']['policy']='same title copies collapse to one runtime card'
        self.assertIn('Green Item physical-copy/no-title stacking lock',run_mutation(invent_title_stacking))

        def lose_variant(data):
            pilots=data['pilots.json']; rule=next(row for row in pilots['records'] if row['ruleId']=='SEM-GREEN-ITEM-VARIANT-BOUNDARIES-001'); rule['sourceVariants'].pop(); pilots['counts']['variantReferences']-=1
        self.assertIn('Green Item Heavy/gap/licensed variant preservation lock',run_mutation(lose_variant))

        def invert_authority(data):
            rule=next(row for row in data['pilots.json']['records'] if row['ruleId']=='SEM-GREEN-ITEM-536500-DC077A-001'); rule['authority']['highest']='source-bound-component-scan'
        self.assertIn('Green Item face exact scan/general/authority/no-variant projection',run_mutation(invert_authority))

        def lower_backlog_coordinated(data):
            target='CARD:59518a4d288b71cf'; backlog=data['backlog.json']; backlog['units']=[row for row in backlog['units'] if row['semanticUnitId']!=target]; backlog['counts']['units']-=1; backlog['counts']['byChannel']['card-reference-source-tuple']-=1; backlog['counts']['byStatus']['pilot-covered']-=1
            source=data['green-item-source-index.json']; ledger=source['familyCountEvidence']['backlog']; ledger['faceUnitIds'].remove(target); ledger['linkedUnitIds'].remove(target); ledger['faceTupleCount']-=1; ledger['obligationCount']-=1; source['counts']['backlogTuples']-=1; source['counts']['backlogObligationsLinked']-=1
        checks=run_mutation(lower_backlog_coordinated)
        self.assertIn('Green Item exact backlog tuple projection',checks)
        self.assertIn('Green Item exact overlapping backlog-obligation closure',checks)

    def test_base_red_item_family_source_closure(self):
        source=load(DIR/'red-item-source-index.json')
        registry={row['sourceId']:row for row in load(DIR/'source-registry.json')['sources']}
        backlog={row['semanticUnitId']:row for row in load(DIR/'backlog.json')['units']}
        self.assertEqual(source['counts']['rootPhysicalOccurrences'],30)
        self.assertEqual(source['counts']['regularPhysicalFaceOccurrences'],21)
        self.assertEqual(source['counts']['excludedHeavyPhysicalOccurrences'],3)
        self.assertEqual(source['counts']['physicalClassConflictOccurrences'],6)
        self.assertEqual(source['counts']['uniqueRegularPrintedTitles'],7)
        self.assertEqual(source['counts']['uniqueSelectedRegularFaceAssets'],7)
        self.assertEqual(source['counts']['sourceFaceAssets'],16)
        self.assertEqual(source['counts']['generatedRegularPhysicalFaceOccurrences'],7)
        self.assertEqual(source['counts']['directRegularPhysicalFaceOccurrences'],14)
        self.assertEqual(source['counts']['sourceSheetCells'],12)
        self.assertEqual(source['counts']['redSelectorGapCells'],4)
        self.assertEqual(source['counts']['crossFamilySelectorGapCells'],3)
        self.assertEqual(source['counts']['rootBackAssets'],2)
        self.assertEqual(source['counts']['redBackPhysicalSelectors'],24)
        self.assertEqual(source['counts']['yellowBackPhysicalSelectors'],6)
        self.assertEqual(source['counts']['physicalPanels'],87)
        self.assertEqual(source['counts']['operativePanels'],66)
        self.assertEqual(source['counts']['printedSentenceOccurrences'],45)
        self.assertEqual(source['counts']['physicalFunctionalIconOccurrences'],27)
        self.assertEqual(source['counts']['physicalMatchedIconOccurrences'],23)
        self.assertEqual(source['counts']['physicalUnresolvedLocalGlyphOccurrences'],4)
        self.assertEqual(source['counts']['licensedDigitalPhysicalCopies'],30)
        self.assertEqual(source['counts']['licensedRegularPhysicalCopies'],21)
        self.assertEqual(source['counts']['licensedHeavyPhysicalCopies'],9)
        self.assertEqual(source['titleMultiplicity'],{
            'AMMO MAGAZINE':7,'ANTI-AIRCRAFT\nCODES':1,'EXPLORING\nDRONE':2,
            'FLASHBANG':3,'GRENADE':5,'PERSONAL\nLOG CODES':1,'PORTABLE\nBARRIER':2,
        })
        self.assertEqual([row['rootSequence'] for row in source['physicalClassConflictFaces']],list(range(1,7)))
        self.assertEqual([row['rootSequence'] for row in source['excludedHeavyFaces']],[7,8,9])
        self.assertEqual([row['rootSequence'] for row in source['faces']],list(range(10,31)))
        self.assertTrue(all(row['semanticRuleId'] is None for row in [*source['excludedHeavyFaces'],*source['physicalClassConflictFaces']]))
        self.assertTrue(all(row['physicalClass']=='regular-item' and row['batchDisposition']=='included-regular-red-item-face' for row in source['faces']))
        self.assertEqual(len({row['ttsCardGuid'] for row in [*source['faces'],*source['excludedHeavyFaces'],*source['physicalClassConflictFaces']]}),30)
        self.assertEqual([(row['rootPhysicalSelectors'],row['rulesTextPresent']) for row in source['rootBacks']],[(24,False),(6,False)])
        self.assertEqual(source['sourceSheets'][0]['rootSelectedCells'],[1,4,6,7])
        self.assertEqual(source['sourceSheets'][0]['selectorGapCells'],[0,2,3,5])
        self.assertEqual(source['sourceSheets'][1]['redRootSelectedCells'],[0])
        self.assertEqual(source['sourceSheets'][1]['crossFamilySelectorGapCells'],[1,2,3])
        self.assertTrue(all(row['licensedCrosswalk']['status']=='not-asserted' and row['officialCrosswalk']['status']=='not-asserted' for row in [*source['faces'],*source['excludedHeavyFaces'],*source['physicalClassConflictFaces']]))
        for row in [*source['faces'],*source['excludedHeavyFaces'],*source['physicalClassConflictFaces']]:
            self.assertEqual(registry[row['sourceId']]['occurrenceId'],row['redItemOccurrenceId'])
        for unit_id in source['familyCountEvidence']['backlog']['linkedUnitIds']:
            self.assertEqual(backlog[unit_id]['status'],'pilot-covered')
        for unit_id in source['familyCountEvidence']['backlog']['excludedHeavyOrConflictUnitIds']:
            self.assertEqual(backlog[unit_id]['status'],'pilot-covered')
            self.assertIn('SEM-EQUIPMENT-VARIANT-BOUNDARIES-001',backlog[unit_id]['pilotRuleIds'])
        for unit_id in source['familyCountEvidence']['backlog']['crossFamilyPendingUnitIds']:
            self.assertEqual(backlog[unit_id]['status'],'pending')
        for unit_id in source['familyCountEvidence']['backlog']['crossFamilyCoveredByYellowUnitIds']:
            self.assertEqual(backlog[unit_id]['status'],'pilot-covered')

    def test_base_red_item_family_semantic_closure(self):
        source=load(DIR/'red-item-source-index.json')
        by_id={row['ruleId']:row for row in load(DIR/'pilots.json')['records']}
        questions={row['questionId']:row for row in load(DIR/'review-gates.json')['questions']}
        face_rule_ids=[row['semanticRuleId'] for row in source['faces']]
        use=by_id['SEM-USE-ITEM-001']
        use_dispatch=next(op['dispatchRuleIds'] for op in use['operations'] if op.get('stepId')=='S05')
        self.assertEqual(use_dispatch[-45:-24],face_rule_ids)
        self.assertEqual(use['operations'][-1]['dispatchRuleIds'],['SEM-GREEN-ITEM-ONE-USE-001','SEM-RED-ITEM-ONE-USE-001','SEM-YELLOW-ITEM-ONE-USE-001'])
        self.assertEqual(by_id['SEM-RED-ITEM-DECK-001']['operations'][0]['repeat'],{'rootPhysicalCardCount':30,'regularBatchFaceCount':21,'excludedHeavyCount':3,'physicalClassConflictCount':6})
        self.assertEqual(by_id['SEM-RED-ITEM-DECK-001']['unresolvedQuestionRefs'],['SEM-Q-040','SEM-Q-047'])
        self.assertEqual(by_id['SEM-RED-ITEM-ONE-USE-001']['operations'][1]['transition']['to'],'tax.scaffold.zone.discard-pile')
        self.assertTrue(by_id['SEM-RED-ITEM-IMMEDIATE-USE-001']['decisions'][0]['declineAllowed'])
        self.assertEqual(by_id['SEM-RED-ITEM-IMMEDIATE-USE-001']['decisions'][0]['cardinality'],{'min':0,'max':1})
        self.assertEqual([op['operationType'] for op in by_id['SEM-AMMO-TOKEN-LIFECYCLE-001']['operations']],['select-target','transition-zone','evaluate-condition','set-state','transition-zone'])
        self.assertIn('not a Burst Action',json.dumps(by_id['SEM-GRENADE-TOKEN-EFFECT-001']))
        self.assertIn('numeric Burst result plus 2',json.dumps(by_id['SEM-GRENADE-TOKEN-EFFECT-001']))
        self.assertIn('may be lies',json.dumps(by_id['SEM-ANTI-AIRCRAFT-TOKEN-STATE-001']))
        self.assertIn('cannot be shown',json.dumps(by_id['SEM-ANTI-AIRCRAFT-TOKEN-STATE-001']))
        self.assertEqual(len(by_id['SEM-RED-ITEM-VARIANT-BOUNDARIES-001']['sourceVariants']),25)
        self.assertEqual(by_id['SEM-RED-ITEM-VARIANT-BOUNDARIES-001']['unresolvedQuestionRefs'],[])
        for row in source['faces']:
            rule=by_id[row['semanticRuleId']]
            self.assertEqual(rule['authority']['highest'],'official-primary')
            self.assertEqual(rule['sourceVariants'],[])
            self.assertEqual(len(row['regions']),3)
            self.assertEqual([region['role'] for region in row['regions']],['artwork-and-interface','identity-trait-and-restriction','operative-effect-body'])
            self.assertEqual(len(row['panels']),len(next(asset for asset in source['sourceFaceAssets'] if asset['assetKey']==row['sourceAssetKey'])['panels']))
            self.assertTrue(all(op['sourceSentenceId'] in {sentence['sentenceId'] for sentence in row['sentences']} for op in rule['operations']))
            self.assertIn('same title/body/multiplicity creates no identity or stacking key',rule['stacking']['policy'])
        local_rules=[by_id[row['semanticRuleId']] for row in source['faces'] if row['sourceAssetKey'] in {'red-sheet-01','red-sheet-06','red-sheet-07'}]
        self.assertTrue(all('icon.notInCombat' not in rule['termRefs'] and 'SEM-Q-046' in rule['unresolvedQuestionRefs'] for rule in local_rules))
        for question_id in [f'SEM-Q-{index:03d}' for index in range(46,51)]:
            self.assertTrue(questions[question_id]['defaultProhibited'])
            self.assertEqual(len(questions[question_id]['alternatives']),3)

    def test_red_item_specific_adversarial_corruptions_are_rejected(self):
        def run_mutation(mutate):
            with tempfile.TemporaryDirectory(prefix='semantic-red-item-negative-') as temp_dir:
                root=Path(temp_dir)
                data={name:load(DIR/name) for name in FILES}
                mutate(data)
                for name,payload in data.items():
                    (root/name).write_text(json.dumps(payload,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
                run,report=self.run_validator(root,skip=True)
            self.assertNotEqual(run.returncode,0)
            return {failure['check'] for failure in report['failures']}

        def drop_copy(data):
            source=data['red-item-source-index.json']; source['faces']=source['faces'][1:]
            source['counts']['regularPhysicalFaceOccurrences']-=1; source['counts']['directRegularPhysicalFaceOccurrences']-=1
        self.assertIn('Red Item source-index exact physical/root/class occurrence count',run_mutation(drop_copy))

        def duplicate_copy(data):
            source=data['red-item-source-index.json']; source['faces'].append(json.loads(json.dumps(source['faces'][0])))
            source['counts']['regularPhysicalFaceOccurrences']+=1; source['counts']['directRegularPhysicalFaceOccurrences']+=1
        self.assertIn('Red Item source-index exact physical/root/class occurrence count',run_mutation(duplicate_copy))

        def collapse_title(data): data['red-item-source-index.json']['titleMultiplicity']['AMMO MAGAZINE']=1
        self.assertIn('Red Item repeated-title/copy multiplicity no-collapse lock',run_mutation(collapse_title))

        def swap_cells(data):
            assets=data['red-item-source-index.json']['sourceFaceAssets']; a=next(row for row in assets if row['assetKey']=='red-sheet-01'); b=next(row for row in assets if row['assetKey']=='red-sheet-04'); a['generatedCell'],b['generatedCell']=b['generatedCell'],a['generatedCell']
        self.assertIn('Red Item independently locked source-face asset tuple',run_mutation(swap_cells))

        def invent_join(data):
            join=data['red-item-source-index.json']['faces'][0]['joinEvidence']; join.update({'identityJoin':'title/red/weapon art/cardId modulo','titleOnlyJoin':True,'colorOnlyJoin':True,'weaponOrAmmoAppearanceJoin':True,'cardIdModuloJoin':True})
        self.assertIn('Red Item title/color/weapon-art/body/folder/order/cell/modulo/licensed join prohibited',run_mutation(invent_join))

        def drift_selector(data): data['red-item-source-index.json']['faces'][0]['sourceSelector']['guid']='ffffff'
        self.assertIn('Red Item exact CardID/GUID/FaceURL/BackURL selector projection',run_mutation(drift_selector))

        def invert_face_back(data):
            source=data['red-item-source-index.json']; face=source['faces'][0]; face['sourceSelector'].update({'key':'BackURL','url':source['rootBacks'][0]['sourceSelector']['url'],'sideRole':'shared-non-operative-red-item-back'})
        self.assertIn('Red Item exact CardID/GUID/FaceURL/BackURL selector projection',run_mutation(invert_face_back))

        def leak_heavy(data):
            source=data['red-item-source-index.json']; leaked=source['excludedHeavyFaces'].pop(0); leaked['batchDisposition']='included-regular-red-item-face'; leaked['semanticRuleId']=source['faces'][0]['semanticRuleId']; source['faces'].append(leaked); source['counts']['regularPhysicalFaceOccurrences']+=1; source['counts']['excludedHeavyPhysicalOccurrences']-=1
        checks=run_mutation(leak_heavy)
        self.assertIn('Red Item source-index exact physical/root/class occurrence count',checks)
        self.assertIn('Red Item regular/Heavy/class-conflict leakage',checks)

        def swap_panels(data):
            panels=data['red-item-source-index.json']['faces'][0]['panels']; panels[1],panels[2]=panels[2],panels[1]
        self.assertIn('Red Item exact physical panel/body/icon projection',run_mutation(swap_panels))

        def drift_body(data): data['red-item-source-index.json']['faces'][0]['printedBody']=data['red-item-source-index.json']['faces'][0]['printedBody'].replace('Gain 1','Gain 2')
        self.assertIn('Red Item exact physical panel/body/icon projection',run_mutation(drift_body))

        def infer_ammo_weapon(data):
            source=data['red-item-source-index.json']; asset=next(row for row in source['sourceFaceAssets'] if row['assetKey']=='red-sheet-01'); face=next(row for row in source['faces'] if row['sourceAssetKey']=='red-sheet-01'); asset['iconOccurrences'][0]['semanticReferenceId']='icon.ammoToken'; face['iconOccurrences'][0]['semanticReferenceId']='icon.ammoToken'
            rule=next(row for row in data['pilots.json']['records'] if row['ruleId']==face['semanticRuleId']); rule['termRefs'].append('icon.ammoToken'); rule['termRefs'].sort()
        checks=run_mutation(infer_ammo_weapon)
        self.assertIn('Red Item exact source-local icon occurrence projection',checks)
        self.assertIn('Red Item local glyph no-default/no-weapon-ammo inference lock',checks)

        def invent_owner_default(data):
            q=next(row for row in data['review-gates.json']['questions'] if row['questionId']=='SEM-Q-049'); q['defaultProhibited']=False
            rule=next(row for row in data['pilots.json']['records'] if row['ruleId']=='SEM-RED-ITEM-3606-EA89DA-001'); rule['decisions'][0]['ownerRef']='P-USING-PLAYER'; rule['decisions'][0]['selectionMode']='player-choice'
        self.assertIn('Red Item ambiguity no-default alternatives/linkage',run_mutation(invent_owner_default))

        def invent_reshuffle(data):
            pilots=data['pilots.json']; rule=next(row for row in pilots['records'] if row['ruleId']=='SEM-RED-ITEM-DECK-001'); op=json.loads(json.dumps(rule['operations'][0])); op['objectRef']='Red discard pile into deck'; rule['operations'].append(op)
            for index,item in enumerate(rule['operations'],1): item['stepId']=f'S{index:02d}'; item['sequence']=index
            pilots['counts']['operations']+=1
        self.assertIn('Red Item lifecycle/stacking/reshuffle lock',run_mutation(invent_reshuffle))

        def invent_title_stacking(data):
            rule=next(row for row in data['pilots.json']['records'] if row['ruleId'].startswith('SEM-RED-ITEM-543800-')); rule['stacking']['policy']='same title copies collapse to one effect'
        self.assertIn('Red Item physical-copy/no-title stacking lock',run_mutation(invent_title_stacking))

        def lose_variant(data):
            pilots=data['pilots.json']; rule=next(row for row in pilots['records'] if row['ruleId']=='SEM-RED-ITEM-VARIANT-BOUNDARIES-001'); rule['sourceVariants'].pop(); pilots['counts']['variantReferences']-=1
        self.assertIn('Red Item variant/authority closure',run_mutation(lose_variant))

        def invert_authority(data):
            rule=next(row for row in data['pilots.json']['records'] if row['ruleId']=='SEM-RED-ITEM-543800-01970B-001'); rule['authority']['highest']='source-bound-component-scan'
        self.assertIn('Red Item face exact scan/general/authority/no-variant projection',run_mutation(invert_authority))

        def lower_backlog_coordinated(data):
            backlog=data['backlog.json']; target='CARD:e9ca2730644b069e'; backlog['units']=[row for row in backlog['units'] if row['semanticUnitId']!=target]; backlog['counts']['units']-=1; backlog['counts']['byChannel']['card-reference-source-tuple']-=1; backlog['counts']['byStatus']['pilot-covered']-=1
            source=data['red-item-source-index.json']; ledger=source['familyCountEvidence']['backlog']; ledger['faceUnitIds'].remove(target); ledger['linkedUnitIds'].remove(target); ledger['faceTupleCount']-=1; ledger['obligationCount']-=1; source['counts']['backlogTuples']-=1; source['counts']['backlogObligationsLinked']-=1
        checks=run_mutation(lower_backlog_coordinated)
        self.assertIn('Red Item exact backlog tuple projection',checks)
        self.assertIn('Red Item exact overlapping backlog-obligation closure',checks)

    def test_base_yellow_item_family_source_and_semantic_closure(self):
        source=load(DIR/'yellow-item-source-index.json')
        registry={row['sourceId']:row for row in load(DIR/'source-registry.json')['sources']}
        backlog={row['semanticUnitId']:row for row in load(DIR/'backlog.json')['units']}
        by_id={row['ruleId']:row for row in load(DIR/'pilots.json')['records']}
        questions={row['questionId']:row for row in load(DIR/'review-gates.json')['questions']}
        self.assertEqual(source['counts']['rootPhysicalOccurrences'],30)
        self.assertEqual(source['counts']['regularPhysicalFaceOccurrences'],24)
        self.assertEqual(source['counts']['explicitHeavyPhysicalOccurrences'],0)
        self.assertEqual(source['counts']['physicalClassConflictOccurrences'],6)
        self.assertEqual(source['counts']['uniqueRegularPrintedTitles'],4)
        self.assertEqual(source['counts']['uniqueSelectedRegularFaceAssets'],4)
        self.assertEqual(source['counts']['sourceFaceAssets'],11)
        self.assertEqual(source['counts']['generatedRegularPhysicalFaceOccurrences'],11)
        self.assertEqual(source['counts']['directRegularPhysicalFaceOccurrences'],13)
        self.assertEqual(source['counts']['sourceSheetCells'],8)
        self.assertEqual(source['counts']['selectorGapCells'],5)
        self.assertEqual(source['counts']['rulesBearingSelectorGapCells'],4)
        self.assertEqual(source['counts']['rootBackAssets'],2)
        self.assertEqual(source['counts']['sharedBackPhysicalSelectors'],25)
        self.assertEqual(source['counts']['uniqueBackSheetPhysicalSelectors'],5)
        self.assertEqual(source['counts']['physicalPanels'],128)
        self.assertEqual(source['counts']['operativePanels'],104)
        self.assertEqual(source['counts']['printedSentenceOccurrences'],56)
        self.assertEqual(source['counts']['physicalFunctionalIconOccurrences'],48)
        self.assertEqual(source['counts']['physicalMatchedIconOccurrences'],32)
        self.assertEqual(source['counts']['physicalUnresolvedLocalGlyphOccurrences'],16)
        self.assertEqual(source['counts']['rootPhysicalPanels'],158)
        self.assertEqual(source['counts']['rootPrintedSentenceOccurrences'],68)
        self.assertEqual(source['counts']['rootFunctionalIconOccurrences'],60)
        self.assertEqual(source['counts']['rootMatchedIconOccurrences'],44)
        self.assertEqual(source['counts']['rootUnresolvedLocalGlyphOccurrences'],16)
        self.assertEqual(source['counts']['sameFamilyGapFunctionalIconOccurrences'],8)
        self.assertEqual(source['counts']['sameFamilyGapMatchedIconOccurrences'],6)
        self.assertEqual(source['counts']['sameFamilyGapUnresolvedLocalGlyphOccurrences'],2)
        self.assertEqual(source['counts']['crossFamilyGapFunctionalIconOccurrences'],2)
        self.assertEqual(source['counts']['crossFamilyGapMatchedIconOccurrences'],1)
        self.assertEqual(source['counts']['crossFamilyGapUnresolvedLocalGlyphOccurrences'],1)
        self.assertEqual(source['counts']['classConflictFunctionalIconOccurrences'],12)
        self.assertEqual(source['counts']['classConflictMatchedIconOccurrences'],12)
        self.assertEqual(source['counts']['licensedDigitalPhysicalCopies'],30)
        self.assertEqual(source['counts']['licensedRegularPhysicalCopies'],24)
        self.assertEqual(source['counts']['licensedHeavyPhysicalCopies'],6)
        self.assertEqual(source['titleMultiplicity'],{'DUCT TAPE':5,'OXYGEN TANK':8,'PHOSPHATES':5,'TOOLS':6})
        self.assertEqual([row['rootSequence'] for row in source['physicalClassConflictFaces']],list(range(1,7)))
        self.assertEqual([row['rootSequence'] for row in source['faces']],list(range(7,31)))
        self.assertTrue(all(row['semanticRuleId'] is None for row in source['physicalClassConflictFaces']))
        self.assertTrue(all(row['physicalClass']=='regular-item' and row['batchDisposition']=='included-regular-yellow-item-face' for row in source['faces']))
        self.assertEqual(len({row['ttsCardGuid'] for row in [*source['faces'],*source['physicalClassConflictFaces']]}),30)
        self.assertEqual([(row['rootPhysicalSelectors'],row['sourceSelector']['uniqueBack'],row['rulesTextPresent']) for row in source['rootBacks']],[(25,False,False),(5,True,False)])
        self.assertEqual(source['sourceSheets'][0]['yellowRootSelectedCells'],[1])
        self.assertEqual(source['sourceSheets'][0]['yellowSelectorGapCells'],[0,2,3])
        self.assertEqual(source['sourceSheets'][1]['yellowRootSelectedCells'],[0,3])
        self.assertEqual(source['sourceSheets'][1]['yellowSelectorGapCells'],[1,2])
        self.assertEqual(source['rootBacks'][1]['sourceSelector']['rootSelectedCell'],1)
        self.assertEqual([row['cell'] for row in source['rootBacks'][1]['visibleCellRoles']],[0,1,2,3])
        self.assertTrue(all(row['licensedCrosswalk']['status']=='not-asserted' and row['officialCrosswalk']['status']=='not-asserted' for row in [*source['faces'],*source['physicalClassConflictFaces']]))
        for row in [*source['faces'],*source['physicalClassConflictFaces']]:
            self.assertEqual(registry[row['sourceId']]['occurrenceId'],row['yellowItemOccurrenceId'])
        for unit_id in source['familyCountEvidence']['backlog']['linkedUnitIds']:
            self.assertEqual(backlog[unit_id]['status'],'pilot-covered')
        for unit_id in source['familyCountEvidence']['backlog']['excludedClassConflictUnitIds']:
            self.assertEqual(backlog[unit_id]['status'],'pilot-covered')
            self.assertIn('SEM-EQUIPMENT-VARIANT-BOUNDARIES-001',backlog[unit_id]['pilotRuleIds'])
        for unit_id in source['familyCountEvidence']['backlog']['crossFamilyPendingUnitIds']:
            self.assertEqual(backlog[unit_id]['status'],'pending')
        self.assertEqual(source['familyCountEvidence']['backlog']['crossFamilyCoveredByEquipmentUnitIds'],['CARD:41183eb8c34b083a'])

        face_rule_ids=[row['semanticRuleId'] for row in source['faces']]
        use=by_id['SEM-USE-ITEM-001']
        use_dispatch=next(op['dispatchRuleIds'] for op in use['operations'] if op.get('stepId')=='S05')
        self.assertEqual(use_dispatch[-24:],face_rule_ids)
        self.assertEqual(use['operations'][-1]['dispatchRuleIds'],['SEM-GREEN-ITEM-ONE-USE-001','SEM-RED-ITEM-ONE-USE-001','SEM-YELLOW-ITEM-ONE-USE-001'])
        self.assertEqual(by_id['SEM-YELLOW-ITEM-DECK-001']['operations'][0]['repeat'],{'rootPhysicalCardCount':30,'regularBatchFaceCount':24,'explicitHeavyCount':0,'physicalClassConflictCount':6})
        self.assertEqual(by_id['SEM-YELLOW-ITEM-DECK-001']['unresolvedQuestionRefs'],['SEM-Q-040','SEM-Q-052'])
        self.assertEqual(by_id['SEM-YELLOW-ITEM-ONE-USE-001']['operations'][2]['transition']['to'],'tax.scaffold.zone.discard-pile')
        self.assertTrue(by_id['SEM-YELLOW-ITEM-IMMEDIATE-USE-001']['decisions'][0]['declineAllowed'])
        self.assertEqual(by_id['SEM-YELLOW-ITEM-IMMEDIATE-USE-001']['decisions'][0]['cardinality'],{'min':0,'max':1})
        self.assertEqual([op['operationType'] for op in by_id['SEM-GAIN-OXYGEN-001']['operations']],['change-value','evaluate-condition'])
        self.assertIn('without exceeding 7',json.dumps(by_id['SEM-GAIN-OXYGEN-001']))
        self.assertEqual(by_id['SEM-OXYGEN-TOKEN-EFFECT-001']['operations'][0]['invokeRuleId'],'SEM-GAIN-OXYGEN-001')
        self.assertEqual([op['operationType'] for op in by_id['SEM-DISCARD-MALFUNCTION-001']['operations']],['select-target','evaluate-condition','transition-zone'])
        self.assertEqual([op['operationType'] for op in by_id['SEM-REINFORCE-CORRIDOR-001']['operations']],['remove-component','set-state'])
        self.assertEqual(len(by_id['SEM-YELLOW-ITEM-VARIANT-BOUNDARIES-001']['sourceVariants']),18)
        self.assertEqual(by_id['SEM-YELLOW-ITEM-VARIANT-BOUNDARIES-001']['unresolvedQuestionRefs'],[])
        self.assertIn('SEM-Q-054',by_id['SEM-ITEM-TRADE-GAIN-001']['unresolvedQuestionRefs'])
        self.assertTrue(any(row['conditionId']=='C-YI-TRADE-DUCT-STACK' for row in by_id['SEM-ITEM-TRADE-GAIN-001']['preconditions']))
        for row in source['faces']:
            rule=by_id[row['semanticRuleId']]
            self.assertEqual(rule['authority']['highest'],'official-primary')
            self.assertEqual(rule['sourceVariants'],[])
            self.assertEqual(len(row['regions']),3)
            self.assertEqual([region['role'] for region in row['regions']],['artwork-and-interface','identity-trait-and-restriction','operative-effect-body'])
            self.assertTrue(all(op['sourceSentenceId'] in {sentence['sentenceId'] for sentence in row['sentences']} for op in rule['operations']))
            self.assertIn('same title/body/multiplicity creates no identity or stacking key',rule['stacking']['policy'])
        local_rules=[by_id[row['semanticRuleId']] for row in source['faces'] if row['sourceAssetKey'] in {'sheet34-00','direct-phosphates','sheet34-03'}]
        self.assertTrue(all('icon.notInCombat' not in rule['termRefs'] and 'icon.computer' not in rule['termRefs'] and 'SEM-Q-051' in rule['unresolvedQuestionRefs'] for rule in local_rules))
        for question_id in [f'SEM-Q-{index:03d}' for index in range(51,57)]:
            self.assertTrue(questions[question_id]['defaultProhibited'])
            self.assertEqual(len(questions[question_id]['alternatives']),3)

    def test_yellow_item_specific_adversarial_corruptions_are_rejected(self):
        def run_mutation(mutate):
            with tempfile.TemporaryDirectory(prefix='semantic-yellow-item-negative-') as temp_dir:
                root=Path(temp_dir)
                data={name:load(DIR/name) for name in FILES}
                mutate(data)
                for name,payload in data.items():
                    (root/name).write_text(json.dumps(payload,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
                run,report=self.run_validator(root,skip=True)
            self.assertNotEqual(run.returncode,0)
            return {failure['check'] for failure in report['failures']}

        def drop_copy(data):
            source=data['yellow-item-source-index.json']; source['faces']=source['faces'][1:]
            source['counts']['regularPhysicalFaceOccurrences']-=1; source['counts']['generatedRegularPhysicalFaceOccurrences']-=1
        self.assertIn('Yellow Item source-index exact physical/root/class occurrence count',run_mutation(drop_copy))

        def duplicate_copy(data):
            source=data['yellow-item-source-index.json']; source['faces'].append(json.loads(json.dumps(source['faces'][0])))
            source['counts']['regularPhysicalFaceOccurrences']+=1; source['counts']['generatedRegularPhysicalFaceOccurrences']+=1
        self.assertIn('Yellow Item source-index exact physical/root/class occurrence count',run_mutation(duplicate_copy))

        def collapse_title(data): data['yellow-item-source-index.json']['titleMultiplicity']['OXYGEN TANK']=1
        self.assertIn('Yellow Item repeated-title/copy multiplicity no-collapse lock',run_mutation(collapse_title))

        def swap_cells(data):
            assets=data['yellow-item-source-index.json']['sourceFaceAssets']; a=next(row for row in assets if row['assetKey']=='sheet34-00'); b=next(row for row in assets if row['assetKey']=='sheet34-03'); a['generatedCell'],b['generatedCell']=b['generatedCell'],a['generatedCell']
        self.assertIn('Yellow Item independently locked source-face asset tuple',run_mutation(swap_cells))

        def invent_join(data):
            join=data['yellow-item-source-index.json']['faces'][0]['joinEvidence']; join.update({'identityJoin':'title/yellow/utility art/cardId modulo','titleOnlyJoin':True,'colorOnlyJoin':True,'utilityOrSystemAppearanceJoin':True,'cardIdModuloJoin':True})
        self.assertIn('Yellow Item title/color/utility-system/body/folder/order/cell/modulo/licensed join prohibited',run_mutation(invent_join))

        def invert_face_back(data):
            face=data['yellow-item-source-index.json']['physicalClassConflictFaces'][1]
            face['sourceSelector'].update({'key':'BackURL','url':face['sourceSelector']['backUrl'],'uniqueBack':False,'backGeneratedCell':None,'sideRole':'shared-non-operative-yellow-item-back'})
        self.assertIn('Yellow Item exact CardID/GUID/FaceURL/BackURL/UniqueBack selector projection',run_mutation(invert_face_back))

        def leak_class_conflict(data):
            source=data['yellow-item-source-index.json']; leaked=source['physicalClassConflictFaces'].pop(0); leaked['batchDisposition']='included-regular-yellow-item-face'; leaked['semanticRuleId']=source['faces'][0]['semanticRuleId']; source['faces'].append(leaked); source['counts']['regularPhysicalFaceOccurrences']+=1; source['counts']['physicalClassConflictOccurrences']-=1
        checks=run_mutation(leak_class_conflict)
        self.assertIn('Yellow Item source-index exact physical/root/class occurrence count',checks)
        self.assertIn('Yellow Item regular/class-conflict leakage',checks)

        def swap_panels(data):
            panels=data['yellow-item-source-index.json']['faces'][0]['panels']; panels[1],panels[2]=panels[2],panels[1]
        self.assertIn('Yellow Item exact physical panel/body/icon projection',run_mutation(swap_panels))

        def drift_body(data):
            face=next(row for row in data['yellow-item-source-index.json']['faces'] if row['sourceAssetKey']=='direct-oxygen'); face['printedBody']=face['printedBody'].replace('Gain 3','Gain 4')
        self.assertIn('Yellow Item exact physical panel/body/icon projection',run_mutation(drift_body))

        def infer_system_icon(data):
            source=data['yellow-item-source-index.json']; asset=next(row for row in source['sourceFaceAssets'] if row['assetKey']=='sheet34-03'); face=next(row for row in source['faces'] if row['sourceAssetKey']=='sheet34-03'); asset['iconOccurrences'][0]['semanticReferenceId']='icon.computer'; face['iconOccurrences'][0]['semanticReferenceId']='icon.computer'
            rule=next(row for row in data['pilots.json']['records'] if row['ruleId']==face['semanticRuleId']); rule['termRefs'].append('icon.computer'); rule['termRefs'].sort()
        checks=run_mutation(infer_system_icon)
        self.assertIn('Yellow Item exact source-local icon occurrence projection',checks)
        self.assertIn('Yellow Item local glyph no-default/no-system inference lock',checks)

        def invent_owner_default(data):
            q=next(row for row in data['review-gates.json']['questions'] if row['questionId']=='SEM-Q-055'); q['defaultProhibited']=False
            rule=next(row for row in data['pilots.json']['records'] if row['ruleId']=='SEM-YELLOW-ITEM-395400-6A29B0-001'); rule['decisions'][1]['ownerRef']='P-USING-PLAYER'; rule['decisions'][1]['selectionMode']='player-choice'
        self.assertIn('Yellow Item ambiguity no-default alternatives/linkage',run_mutation(invent_owner_default))

        def invent_optionality(data):
            q=next(row for row in data['review-gates.json']['questions'] if row['questionId']=='SEM-Q-051'); q['defaultProhibited']=False; q['alternatives']=q['alternatives'][:1]
        self.assertIn('Yellow Item ambiguity no-default alternatives/linkage',run_mutation(invent_optionality))

        def invent_reshuffle(data):
            pilots=data['pilots.json']; rule=next(row for row in pilots['records'] if row['ruleId']=='SEM-YELLOW-ITEM-DECK-001'); op=json.loads(json.dumps(rule['operations'][0])); op['objectRef']='Yellow discard pile into deck'; rule['operations'].append(op)
            for index,item in enumerate(rule['operations'],1): item['stepId']=f'S{index:02d}'; item['sequence']=index
            pilots['counts']['operations']+=1
        self.assertIn('Yellow Item lifecycle/class/reshuffle lock',run_mutation(invent_reshuffle))

        def invent_title_stacking(data):
            rule=next(row for row in data['pilots.json']['records'] if row['ruleId'].startswith('SEM-YELLOW-ITEM-532000-')); rule['stacking']['policy']='same title copies collapse to one effect'
        self.assertIn('Yellow Item physical-copy/no-title stacking lock',run_mutation(invent_title_stacking))

        def flatten_duct_lifecycle(data):
            q=next(row for row in data['review-gates.json']['questions'] if row['questionId']=='SEM-Q-054'); q['defaultProhibited']=False
            trade=next(row for row in data['pilots.json']['records'] if row['ruleId']=='SEM-ITEM-TRADE-GAIN-001'); trade['preconditions']=[row for row in trade['preconditions'] if row['conditionId']!='C-YI-TRADE-DUCT-STACK']; trade['operations']=[row for row in trade['operations'] if 'SEM-Q-054' not in row['objectRef']]
            for index,row in enumerate(trade['operations'],1): row['stepId']=f'S{index:02d}'; row['sequence']=index
            trade['unresolvedQuestionRefs'].remove('SEM-Q-054'); data['pilots.json']['counts']['conditions']-=1; data['pilots.json']['counts']['operations']-=1; data['pilots.json']['counts']['openQuestionReferences']-=1
        checks=run_mutation(flatten_duct_lifecycle)
        self.assertIn('Yellow Item Trade/immediate/Duct-stack no-default integration lock',checks)
        self.assertIn('Yellow Item ambiguity no-default alternatives/linkage',checks)

        def lose_variant(data):
            pilots=data['pilots.json']; rule=next(row for row in pilots['records'] if row['ruleId']=='SEM-YELLOW-ITEM-VARIANT-BOUNDARIES-001'); rule['sourceVariants'].pop(); pilots['counts']['variantReferences']-=1
        self.assertIn('Yellow Item variant/authority closure',run_mutation(lose_variant))

        def invert_authority(data):
            rule=next(row for row in data['pilots.json']['records'] if row['ruleId']=='SEM-YELLOW-ITEM-532000-CE55D9-001'); rule['authority']['highest']='licensed-digital-secondary'
        self.assertIn('Yellow Item face exact scan/general/authority/no-title-variant projection',run_mutation(invert_authority))

        def lower_backlog_coordinated(data):
            backlog=data['backlog.json']; target='CARD:1b05382453304c01'; backlog['units']=[row for row in backlog['units'] if row['semanticUnitId']!=target]; backlog['counts']['units']-=1; backlog['counts']['byChannel']['card-reference-source-tuple']-=1; backlog['counts']['byStatus']['pilot-covered']-=1
            source=data['yellow-item-source-index.json']; ledger=source['familyCountEvidence']['backlog']; ledger['faceUnitIds'].remove(target); ledger['linkedUnitIds'].remove(target); ledger['faceTupleCount']-=1; ledger['obligationCount']-=1; source['counts']['backlogTuples']-=1; source['counts']['backlogObligationsLinked']-=1
        checks=run_mutation(lower_backlog_coordinated)
        self.assertIn('Yellow Item exact backlog tuple projection',checks)
        self.assertIn('Yellow Item exact overlapping backlog-obligation closure',checks)

    def test_base_serious_wound_family_semantic_closure(self):
        source=load(DIR/'serious-wound-source-index.json')
        registry={row['sourceId']:row for row in load(DIR/'source-registry.json')['sources']}
        by_id={row['ruleId']:row for row in load(DIR/'pilots.json')['records']}
        backlog={row['semanticUnitId']:row for row in load(DIR/'backlog.json')['units']}
        self.assertEqual(source['counts']['physicalFaceOccurrences'],27)
        self.assertEqual(source['counts']['uniquePrintedTitles'],9)
        self.assertEqual(source['counts']['uniqueSelectedFaceAssets'],9)
        self.assertEqual(source['counts']['sourceFaceAssets'],11)
        self.assertEqual(source['counts']['generatedPhysicalFaceOccurrences'],21)
        self.assertEqual(source['counts']['directPhysicalFaceOccurrences'],6)
        self.assertEqual(source['counts']['sourceSheetCells'],9)
        self.assertEqual(source['counts']['selectedGeneratedCells'],7)
        self.assertEqual(source['counts']['selectorGapCells'],2)
        self.assertEqual(source['counts']['sharedBackSelectorReferences'],28)
        self.assertEqual(source['counts']['physicalRegions'],81)
        self.assertEqual(source['counts']['physicalPanels'],54)
        self.assertEqual(source['counts']['operativePanels'],27)
        self.assertEqual(source['counts']['printedSentenceOccurrences'],42)
        self.assertEqual(source['counts']['physicalFunctionalIconOccurrences'],30)
        self.assertEqual(source['counts']['physicalMatchedIconOccurrences'],24)
        self.assertEqual(source['counts']['physicalUnresolvedLocalGlyphOccurrences'],6)
        self.assertEqual(source['titleMultiplicity'],{title:3 for title in ('ARM','BLEEDING','BODY','EYES','GUTS','HAND','KNEE','LEG','LUNGS')})
        self.assertEqual([row['generatedCell'] for row in source['sourceFaceAssets'] if not row['selectedByRootDeck']],[4,6])
        self.assertTrue(all(row['licensedCrosswalk']['status']=='not-asserted' and row['officialCrosswalk']['status']=='not-asserted' for row in source['faces']))
        self.assertTrue(all(row['semanticBodyPartTraitOrSeverityInferred'] is False for row in source['faces']))
        self.assertEqual(len({row['seriousWoundOccurrenceId'] for row in source['faces']}),27)
        self.assertEqual(len({row['ttsCardGuid'] for row in source['faces']}),27)
        self.assertEqual(len({row['semanticRuleId'] for row in source['faces']}),27)
        self.assertEqual(source['sharedBack']['rulesTextPresent'],False)
        self.assertEqual(source['sharedBack']['separateRulesFace'],False)
        self.assertEqual(source['familyCountEvidence']['licensedDigital']['physicalIdentityCrosswalkAsserted'],False)
        self.assertEqual(source['faqSearchClosure']['baseApplicableOccurrences'],[])
        self.assertEqual(len(source['licensedDigitalOccurrences']),9)
        self.assertEqual(len(source['officialVisibleCounterparts']),5)
        self.assertEqual(sum(row['kind'] in {'face','partial-face'} for row in source['officialVisibleCounterparts']),3)
        self.assertEqual(sum(row['kind']=='shared-back' for row in source['officialVisibleCounterparts']),2)
        physical_rule_ids=[row['semanticRuleId'] for row in source['faces']]
        self.assertEqual(next(op['dispatchRuleIds'] for op in by_id['SEM-SERIOUS-WOUND-GAIN-001']['operations'] if op.get('dispatchRuleIds')),physical_rule_ids)
        self.assertFalse(any(op['operationType']=='shuffle' for op in by_id['SEM-SERIOUS-WOUND-GAIN-001']['operations']))
        self.assertEqual(by_id['SEM-SERIOUS-WOUND-SETUP-001']['operations'][0]['repeat']['physicalCardCount'],27)
        self.assertEqual(by_id['SEM-SERIOUS-WOUND-DISCARD-001']['decisions'][0]['ownerRef'],'P-OWNER')
        self.assertEqual(by_id['SEM-SERIOUS-WOUND-DISCARD-001']['operations'][1]['transition']['to'],'tax.scaffold.zone.discard-pile')
        self.assertEqual(len(by_id['SEM-SERIOUS-WOUND-VARIANT-BOUNDARIES-001']['sourceVariants']),14)
        for row in source['faces']:
            self.assertIn(row['semanticRuleId'],by_id)
            self.assertEqual(len(row['regions']),3)
            self.assertEqual([region['role'] for region in row['regions']],['artwork-and-diagnostic-interface','printed-heading','operative-effect'])
            self.assertEqual(len(row['panels']),2)
            self.assertEqual([panel['role'] for panel in row['panels']],['printed-title-panel','operative-effect-panel'])
            self.assertEqual(backlog[row['backlogUnitId']]['status'],'pilot-covered')
            self.assertEqual(registry[row['sourceId']]['occurrenceId'],row['seriousWoundOccurrenceId'])
        questions={row['questionId']:row for row in load(DIR/'review-gates.json')['questions']}
        for question_id in [f'SEM-Q-{index:03d}' for index in range(30,39)]:
            self.assertTrue(questions[question_id]['defaultProhibited'])

    def test_serious_wound_specific_adversarial_corruptions_are_rejected(self):
        def run_mutation(mutate):
            with tempfile.TemporaryDirectory(prefix='semantic-serious-wound-negative-') as temp_dir:
                root=Path(temp_dir)
                data={name:load(DIR/name) for name in FILES}
                mutate(data)
                for name,payload in data.items():
                    (root/name).write_text(json.dumps(payload,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
                run,report=self.run_validator(root,skip=True)
            self.assertNotEqual(run.returncode,0)
            return {failure['check'] for failure in report['failures']}

        def drop_face(data):
            source=data['serious-wound-source-index.json']; source['faces']=source['faces'][1:]
            source['counts']['physicalFaceOccurrences']-=1; source['counts']['generatedPhysicalFaceOccurrences']-=1
            source['counts']['physicalRegions']-=3; source['counts']['operativeRegions']-=1
        self.assertIn('Serious Wound source-index exact physical occurrence count',run_mutation(drop_face))

        def duplicate_face(data):
            source=data['serious-wound-source-index.json']; source['faces'].append(json.loads(json.dumps(source['faces'][0])))
            source['counts']['physicalFaceOccurrences']+=1; source['counts']['generatedPhysicalFaceOccurrences']+=1
            source['counts']['physicalRegions']+=3; source['counts']['operativeRegions']+=1
        self.assertIn('Serious Wound source-index exact physical occurrence count',run_mutation(duplicate_face))

        def collapse_repeated_title(data):
            data['serious-wound-source-index.json']['titleMultiplicity']['EYES']=1
        self.assertIn('Serious Wound repeated-title multiplicity/no-collapse lock',run_mutation(collapse_repeated_title))

        def swap_sheet_cells(data):
            assets=data['serious-wound-source-index.json']['sourceFaceAssets']
            first=next(row for row in assets if row['assetKey']=='sheet-00'); second=next(row for row in assets if row['assetKey']=='sheet-01')
            first['generatedCell'],second['generatedCell']=second['generatedCell'],first['generatedCell']
        self.assertIn('Serious Wound independently locked source-face asset tuple',run_mutation(swap_sheet_cells))

        def invent_modulo_join(data):
            join=data['serious-wound-source-index.json']['faces'][0]['joinEvidence']
            join.update({'identityJoin':'CardID modulo','cardIdModuloJoin':True,'basis':['cardId % 100']})
        self.assertIn('Serious Wound title/body/folder/sequence/modulo/licensed join prohibited',run_mutation(invent_modulo_join))

        def drift_selector(data):
            data['serious-wound-source-index.json']['faces'][0]['sourceSelector']['guid']='ffffff'
        self.assertIn('Serious Wound exact CardID/GUID/FaceURL/BackURL selector projection',run_mutation(drift_selector))

        def invert_face_back(data):
            face=data['serious-wound-source-index.json']['faces'][0]
            face['sourceSelector'].update({'key':'BackURL','url':data['serious-wound-source-index.json']['sharedBack']['sourceSelector']['url'],'sideRole':'shared-non-operative-back'})
        self.assertIn('Serious Wound exact CardID/GUID/FaceURL/BackURL selector projection',run_mutation(invert_face_back))

        def swap_regions(data):
            regions=data['serious-wound-source-index.json']['faces'][0]['regions']; regions[1],regions[2]=regions[2],regions[1]
        self.assertIn('Serious Wound exact physical region roles/order',run_mutation(swap_regions))

        def swap_panels(data):
            panels=data['serious-wound-source-index.json']['faces'][0]['panels']; panels[0],panels[1]=panels[1],panels[0]
        self.assertIn('Serious Wound exact physical panel roles/order/region linkage',run_mutation(swap_panels))

        def swap_health_slot(data):
            rule=next(row for row in data['pilots.json']['records'] if row['ruleId']=='SEM-SERIOUS-WOUND-GAIN-001')
            rule['operations'][4]['objectRef']='rightmost Health Section without a Serious Wound'
        self.assertIn('Serious Wound finite draw/place/displace/activate/dispatch operation order lock',run_mutation(swap_health_slot))

        def swap_icons(data):
            lungs=next(row for row in data['serious-wound-source-index.json']['faces'] if row['printedTitle']=='LUNGS')
            lungs['iconOccurrences'][0]['semanticReferenceId'],lungs['iconOccurrences'][1]['semanticReferenceId']=lungs['iconOccurrences'][1]['semanticReferenceId'],lungs['iconOccurrences'][0]['semanticReferenceId']
        self.assertIn('Serious Wound exact physical text/icon projection',run_mutation(swap_icons))

        def drift_body(data):
            data['serious-wound-source-index.json']['faces'][0]['printedBody']=data['serious-wound-source-index.json']['faces'][0]['printedBody'].replace('values.','values!')
        self.assertIn('Serious Wound exact body/punctuation/order lock',run_mutation(drift_body))

        def flatten_immediate_persistent(data):
            rule=next(row for row in data['pilots.json']['records'] if row['ruleId']=='SEM-SERIOUS-WOUND-3803-AA0B48-001')
            rule['duration']['kind']='instantaneous'
        self.assertIn('Serious Wound immediate/persistent duration and exact-duplicate stacking lock',run_mutation(flatten_immediate_persistent))

        def invent_title_stacking(data):
            rule=next(row for row in data['pilots.json']['records'] if row['ruleId']=='SEM-SERIOUS-WOUND-STACKING-001')
            rule['operations'][0]['objectRef']='whether owned Wounds share a display title'
            rule['operations'][2]['objectRef']='display title establishes stacking equivalence'
        self.assertIn('Serious Wound duplicate exact-asset stacking/no-title-default lock',run_mutation(invent_title_stacking))

        def invent_reshuffle(data):
            rule=next(row for row in data['pilots.json']['records'] if row['ruleId']=='SEM-SERIOUS-WOUND-GAIN-001')
            rule['operations'].insert(1,json.loads(json.dumps(rule['operations'][0])))
            for index,op in enumerate(rule['operations'],1): op['sequence']=index; op['stepId']=f'S{index:02d}'
            rule['operations'][1]['operationType']='shuffle'; rule['operations'][1]['objectRef']='Serious Wound discard into deck'
            data['pilots.json']['counts']['operations']+=1
        self.assertIn('Serious Wound lifecycle/no-reshuffle/no-default gain lock',run_mutation(invent_reshuffle))

        def lose_variant(data):
            rule=next(row for row in data['pilots.json']['records'] if row['ruleId']=='SEM-SERIOUS-WOUND-VARIANT-BOUNDARIES-001')
            rule['sourceVariants'].pop(); data['pilots.json']['counts']['variantReferences']-=1
        self.assertIn('Serious Wound selector-gap/licensed/official variant preservation lock',run_mutation(lose_variant))

        def invert_authority(data):
            rule=next(row for row in data['pilots.json']['records'] if row['ruleId']=='SEM-SERIOUS-WOUND-3800-EE102C-001')
            rule['authority']['highest']='source-bound-component-scan'
        self.assertIn('Serious Wound face authority/no-title-identity-join lock',run_mutation(invert_authority))

        def invent_default(data):
            question=next(row for row in data['review-gates.json']['questions'] if row['questionId']=='SEM-Q-033')
            question['defaultProhibited']=False
        self.assertIn('Serious Wound ambiguity no-default alternatives/linkage',run_mutation(invent_default))

        def lower_backlog_coordinated(data):
            target='CARD:522c29d0874334ca'; backlog=data['backlog.json']
            backlog['units']=[row for row in backlog['units'] if row['semanticUnitId']!=target]
            backlog['counts']['units']-=1; backlog['counts']['byChannel']['card-reference-source-tuple']-=1; backlog['counts']['byStatus']['pilot-covered']-=1
            source=data['serious-wound-source-index.json']; ledger=source['familyCountEvidence']['backlog']
            ledger['faceUnitIds'].remove(target); ledger['linkedUnitIds'].remove(target); ledger['faceTupleCount']-=1
            source['counts']['backlogTuples']-=1; source['counts']['backlogObligationsLinked']-=1
        checks=run_mutation(lower_backlog_coordinated)
        self.assertIn('Serious Wound exact backlog tuple projection',checks)
        self.assertIn('Serious Wound exact overlapping backlog-obligation closure',checks)

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

    def test_base_action_family_semantic_closure(self):
        source=load(DIR/'action-source-index.json')
        pilots=load(DIR/'pilots.json'); by_id={row['ruleId']:row for row in pilots['records']}
        registry={row['sourceId']:row for row in load(DIR/'source-registry.json')['sources']}
        backlog={row['semanticUnitId']:row for row in load(DIR/'backlog.json')['units']}
        self.assertEqual(len(source['faces']),60)
        self.assertEqual(len(source['characterDecks']),6)
        self.assertEqual({row['character']:len(row['physicalCopies']) for row in source['characterDecks']},{'Combat Engineer':10,'Heavy Gun Operator':10,'Medical Support':10,'Contractor':10,'Officer':10,'Recon':10})
        self.assertEqual(len(source['sourceFaceAssets']),89)
        self.assertEqual(sum(row['selectorGap'] is not None for row in source['sourceFaceAssets']),29)
        self.assertEqual([len(row['selectedCells']) for row in source['sourceSheets']],[16,5])
        self.assertEqual(len(source['sourceSheets'][1]['expansionCellsExcluded']),40)
        self.assertEqual(source['sharedBack']['globalReferenceCount'],273)
        self.assertEqual(len(source['licensedDigitalOccurrences']),60)
        self.assertTrue(all(not row['assertedTtsPhysicalIdentityLinks'] for row in source['licensedDigitalOccurrences']))
        face_rule_ids=[row['semanticRuleId'] for row in source['faces']]
        self.assertEqual(len(face_rule_ids),len(set(face_rule_ids)))
        self.assertTrue(all(rule_id in by_id for rule_id in face_rule_ids))
        self.assertEqual(next(op['dispatchRuleIds'] for op in by_id['SEM-ACTION-CARD-PLAY-001']['operations'] if op.get('dispatchRuleIds')),face_rule_ids)
        reaction_ids=['SEM-REACTION-DUCK-001',*sorted({row['reactionRuleId'] for row in source['faces'] if row.get('reactionRuleId') and row['reactionRuleId']!='SEM-REACTION-DUCK-001'})]
        self.assertEqual(next(op['dispatchRuleIds'] for op in by_id['SEM-ACTION-CARD-REACTION-001']['operations'] if op.get('dispatchRuleIds')),reaction_ids)
        self.assertEqual(sum((row['notInCombat']['status']=='source-resolved') for row in source['faces']),28)
        self.assertEqual(sum((row['notInCombat']['status']=='literal-unresolved') for row in source['faces']),8)
        self.assertEqual(sum(panel.get('heading')=='COMMAND' for row in source['faces'] for panel in row['panels']),8)
        self.assertEqual(sum(panel.get('heading')=='REACTION' for row in source['faces'] for panel in row['panels']),6)
        for face in source['faces']:
            registered=registry[face['sourceId']]
            self.assertEqual((registered['path'],registered['sha256'],registered['occurrenceId']),(face['sourcePath'],face['sourceSha256'],face['occurrenceId']))
            self.assertEqual(backlog[face['backlogUnitId']]['pilotRuleIds'],[face['semanticRuleId']])
            self.assertFalse(any(face['identityJoinEvidence'][key] for key in ('characterNameOnlyJoin','titleOnlyJoin','bodySimilarityJoin','folderOnlyJoin','sourceSheetOnlyJoin','generatedCellOnlyJoin','cardIdModuloJoin','licensedKeyJoin')))
        for asset in source['sourceFaceAssets']:
            if asset['selectorGap']:
                self.assertEqual(backlog[asset['backlogUnitId']]['pilotRuleIds'],['SEM-ACTION-CARD-VARIANT-BOUNDARIES-001'])
        self.assertIn('SEM-Q-059',by_id['SEM-ACTION-CARD-COMMAND-001']['unresolvedQuestionRefs'])
        self.assertIn('SEM-Q-060',by_id['SEM-ACTION-CARD-REACTION-001']['unresolvedQuestionRefs'])
        self.assertEqual([op['operationType'] for op in by_id['SEM-ACTION-CARD-DRAW-001']['operations']],['evaluate-condition','shuffle','draw-random','resolve-open-alternative'])

    def test_action_specific_adversarial_corruptions_are_rejected(self):
        def run_mutation(mutate):
            with tempfile.TemporaryDirectory(prefix='semantic-action-negative-') as temp_dir:
                root=Path(temp_dir)
                data={name:load(DIR/name) for name in FILES}
                mutate(data)
                for name,payload in data.items():
                    (root/name).write_text(json.dumps(payload,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
                run,report=self.run_validator(root,skip=True)
            self.assertNotEqual(run.returncode,0)
            return {failure['check'] for failure in report['failures']}

        def duplicate_copy(data):
            source=data['action-source-index.json']
            source['faces'][0]=json.loads(json.dumps(source['faces'][1]))
        checks=run_mutation(duplicate_copy)
        self.assertIn('Action dropped/duplicated physical copy closure',checks)
        self.assertIn('Action exact occurrence tuple/anatomy/text/cost/icon projection',checks)

        def cross_character_member_swap(data):
            first=data['action-source-index.json']['faces'][0]
            second=next(row for row in data['action-source-index.json']['faces'] if row['character']=='Recon')
            first['characterDeckId'],second['characterDeckId']=second['characterDeckId'],first['characterDeckId']
            first['copyId'],second['copyId']=second['copyId'],first['copyId']
        self.assertIn('Action exact occurrence tuple/anatomy/text/cost/icon projection',run_mutation(cross_character_member_swap))

        def title_cell_modulo_join(data):
            source=data['action-source-index.json']; first=source['faces'][0]; generated=next(row for row in source['faces'] if row['sourceSelector']['generatedSpriteSheetCell'])
            first['printedTitle']=source['faces'][1]['printedTitle']
            generated['sourceSelector']['generatedCell']=0
            generated['sourceSelector']['cardIdModuloJoinUsed']=True
            generated['identityJoinEvidence']['titleOnlyJoin']=True
            generated['identityJoinEvidence']['cardIdModuloJoin']=True
        checks=run_mutation(title_cell_modulo_join)
        self.assertIn('Action exact occurrence tuple/anatomy/text/cost/icon projection',checks)
        self.assertIn('Action prohibited title/Character/folder/sheet/cell/modulo join',checks)

        def selector_back_inversion(data):
            selector=data['action-source-index.json']['faces'][0]['sourceSelector']
            selector['url']=selector['backUrl']
        self.assertIn('Action selector/back inversion',run_mutation(selector_back_inversion))

        def drift_anatomy_cost_icon_order(data):
            face=data['action-source-index.json']['faces'][1]
            face['printedBody']+='!'
            face['printedCostClauses']=[]
            face['notInCombat']['status']='source-resolved'
            face['notInCombat']['semanticReferenceId']='icon.notInCombat'
            face['panels'][0]['readingOrder']=99
            face['sentences']=list(reversed(face['sentences']))
            face['iconOccurrences'][0]['semanticReferenceId']='icon.robot'
        checks=run_mutation(drift_anatomy_cost_icon_order)
        self.assertIn('Action exact occurrence tuple/anatomy/text/cost/icon projection',checks)
        self.assertIn('Action panel/sentence order closure',checks)

        def leak_and_change_owner(data):
            play=next(row for row in data['pilots.json']['records'] if row['ruleId']=='SEM-ACTION-CARD-PLAY-001')
            play['informationPolicy'][0]['audience']='public'
            face=next(row for row in data['pilots.json']['records'] if row['ruleId'].startswith('SEM-ACTION-CE-'))
            face['decisions'][0]['ownerRef']='P-RULES'
            if face['targets']:
                face['targets'][0]['selectionMode']='deterministic-state-filter'
        checks=run_mutation(leak_and_change_owner)
        self.assertIn('Action private-hand visibility/no-leakage lock',checks)
        self.assertIn('Action independently locked ordered semantic atoms',checks)

        def invent_default_and_flatten_dispatch(data):
            next(row for row in data['review-gates.json']['questions'] if row['questionId']=='SEM-Q-057')['defaultProhibited']=False
            reaction=next(row for row in data['pilots.json']['records'] if row['ruleId']=='SEM-ACTION-CARD-REACTION-001')
            dispatch=next(op['dispatchRuleIds'] for op in reaction['operations'] if op.get('dispatchRuleIds'))
            dispatch[1]=dispatch[2]
            command=next(row for row in data['pilots.json']['records'] if row['ruleId']=='SEM-ACTION-CARD-COMMAND-001')
            command['operations']=[op for op in command['operations'] if op['operationType']!='resolve-open-alternative']
            for index,op in enumerate(command['operations'],1): op['sequence']=index; op['stepId']=f'S{index:02d}'
        checks=run_mutation(invent_default_and_flatten_dispatch)
        self.assertIn('Action ambiguity owner/target/consent/default linkage',checks)
        self.assertIn('Action exact Reaction panel dispatcher/no-flattening lock',checks)
        self.assertIn('Action Command cost/owner/no-default lock',checks)

        def lifecycle_and_variant_loss(data):
            draw=next(row for row in data['pilots.json']['records'] if row['ruleId']=='SEM-ACTION-CARD-DRAW-001')
            draw['operations'][0],draw['operations'][1]=draw['operations'][1],draw['operations'][0]
            for index,op in enumerate(draw['operations'],1): op['sequence']=index; op['stepId']=f'S{index:02d}'
            licensed=data['action-source-index.json']['licensedDigitalOccurrences']
            licensed[0]=json.loads(json.dumps(licensed[1]))
        checks=run_mutation(lifecycle_and_variant_loss)
        self.assertIn('Action draw/reshuffle/shortage lifecycle lock',checks)
        self.assertIn('Action exact independent licensed row/variant closure',checks)

        def coordinated_backlog_lowering(data):
            source=data['action-source-index.json']; backlog=data['backlog.json']
            target=source['sourceFaceAssets'][0]['backlogUnitId']
            backlog['units']=[row for row in backlog['units'] if row['semanticUnitId']!=target]
            backlog['counts']['units']-=1
            backlog['counts']['byChannel']['card-reference-source-tuple']-=1
            backlog['counts']['byStatus']['pilot-covered']-=1
            source['familyCountEvidence']['backlog']['faceUnitIds'].remove(target)
            source['familyCountEvidence']['backlog']['linkedUnitIds'].remove(target)
            source['familyCountEvidence']['backlog']['faceTupleCount']-=1
            source['counts']['backlogTuples']-=1
            source['counts']['backlogObligationsLinked']-=1
        checks=run_mutation(coordinated_backlog_lowering)
        self.assertIn('Action exact backlog tuple projection',checks)
        self.assertIn('Action exact overlapping backlog-obligation closure',checks)

    def test_base_objective_mission_family_semantic_closure(self):
        source=load(DIR/'objective-mission-source-index.json')
        by_id={row['ruleId']:row for row in load(DIR/'pilots.json')['records']}
        backlog={row['semanticUnitId']:row for row in load(DIR/'backlog.json')['units']}
        registry={row['sourceId']:row for row in load(DIR/'source-registry.json')['sources']}
        self.assertEqual(len(source['physicalFaces']),30)
        self.assertEqual({category:sum(row['category']==category for row in source['physicalFaces']) for category in ('mission-objective','private-objective','mission-task')},{'mission-objective':7,'private-objective':15,'mission-task':8})
        self.assertEqual(sum(row['printedTitle']=='OFFICIAL ORDER' for row in source['physicalFaces']),5)
        self.assertEqual(len({row['copyId'] for row in source['physicalFaces']}),30)
        self.assertEqual(sum(row['semanticRuleId'] is not None for row in source['physicalFaces']),29)
        self.assertEqual(len(source['excludedPhysicalOccurrences']),9)
        self.assertEqual([row['physicalOccurrences'] for row in source['excludedSoloCoopRoots']],[12,26])
        self.assertEqual(len(source['sourceFaceAssets']),50)
        self.assertEqual(sum(row['baseSelectorGap'] is not None for row in source['sourceFaceAssets']),18)
        self.assertEqual([len(row['baseSelectedCells']) for row in source['sourceSheets']],[12,1])
        self.assertEqual([row['globalReferenceCount'] for row in source['sharedBacks']],[33,11])
        self.assertEqual(len(source['officialHelpOccurrences']),45)
        self.assertEqual(sum(row['visibility']=='fully-visible' for row in source['officialHelpOccurrences']),35)
        self.assertEqual(sum(row['visibility']=='partially-occluded' for row in source['officialHelpOccurrences']),10)
        self.assertEqual(len(source['licensedDigitalOccurrences']),38)
        self.assertEqual(sum(row['competitiveDisposition']=='base-competitive-licensed-occurrence' for row in source['licensedDigitalOccurrences']),26)
        self.assertTrue(all(not row['assertedTtsPhysicalIdentityLinks'] for row in source['licensedDigitalOccurrences']))
        for face in source['physicalFaces']:
            registered=registry[face['sourceId']]
            self.assertEqual((registered['path'],registered['sha256'],registered['occurrenceId']),(face['sourcePath'],face['sourceSha256'],face['occurrenceId']))
            self.assertFalse(any(face['identityJoinEvidence'][key] for key in ('titleOnlyJoin','bodySimilarityJoin','categoryLabelOnlyJoin','privatePersonalGlobalAliasJoin','folderOnlyJoin','sourceOrderOnlyJoin','sourceSheetOnlyJoin','generatedCellOnlyJoin','cardIdModuloJoin','licensedKeyJoin','officialHelpTitleJoin')))
            if face['semanticRuleId']:
                self.assertIn(face['semanticRuleId'],by_id)
            else:
                self.assertEqual(backlog[face['backlogUnitId']]['status'],'source-blocked')
        self.assertIn('logs',json.dumps(by_id['SEM-OBJECTIVE-SECRECY-001']))
        self.assertIn('accessibility',json.dumps(by_id['SEM-OBJECTIVE-SECRECY-001']))
        self.assertEqual(by_id['SEM-RT-010']['operations'][-1]['repeat']['drawCountByChoiceOrdinal'],{'1':3,'2':2,'3':2,'4':1,'5':1})
        self.assertEqual(by_id['SEM-ENDGAME-001']['unresolvedQuestionRefs'],['OQ-001','SEM-Q-077','SEM-Q-078'])
        self.assertEqual({row['questionId'] for row in load(DIR/'review-gates.json')['questions'] if row['questionId'].startswith('SEM-Q-07')},{'SEM-Q-070','SEM-Q-071','SEM-Q-072','SEM-Q-073','SEM-Q-074','SEM-Q-075','SEM-Q-076','SEM-Q-077','SEM-Q-078','SEM-Q-079'})

    def test_objective_specific_adversarial_corruptions_are_rejected(self):
        def run_mutation(mutate):
            with tempfile.TemporaryDirectory(prefix='semantic-objective-negative-') as temp_dir:
                root=Path(temp_dir)
                data={name:load(DIR/name) for name in FILES}
                mutate(data)
                for name,payload in data.items():
                    (root/name).write_text(json.dumps(payload,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
                run,report=self.run_validator(root,skip=True)
            self.assertNotEqual(run.returncode,0)
            return {failure['check'] for failure in report['failures']}

        def duplicate_copy(data):
            source=data['objective-mission-source-index.json']
            source['physicalFaces'][0]=json.loads(json.dumps(source['physicalFaces'][1]))
        checks=run_mutation(duplicate_copy)
        self.assertIn('Objective/Mission dropped/duplicated physical copy closure',checks)
        self.assertIn('Objective/Mission exact physical tuple/panel/text/icon/condition projection',checks)

        def collapse_category_title_alias(data):
            source=data['objective-mission-source-index.json']
            task=next(row for row in source['physicalFaces'] if row['category']=='mission-task')
            task['category']='mission-objective'; task['deckId']='BASE-MISSION-OBJECTIVE-DECK'; task['printedTitle']='OFFICIAL ORDER'
            private=next(row for row in source['physicalFaces'] if row['printedFooter']=='PERSONAL OBJECTIVE')
            private['identityJoinEvidence']['privatePersonalGlobalAliasJoin']=True
            private['privatePersonalAliasProjection']['globalAliasUsed']=True
        checks=run_mutation(collapse_category_title_alias)
        self.assertIn('Objective/Mission exact category/deck/copy partition',checks)
        self.assertIn('Objective title/body/category/alias/folder/order/sheet/cell/modulo join prohibited',checks)

        def sheet_cell_modulo_and_back_inversion(data):
            face=next(row for row in data['objective-mission-source-index.json']['physicalFaces'] if row['sourceSelector']['generatedSpriteSheetCell'])
            face['sourceSelector']['generatedCell']=0
            face['sourceSelector']['cardIdModuloJoinUsed']=True
            face['sourceSelector']['url']=face['sourceSelector']['backUrl']
            face['identityJoinEvidence']['generatedCellOnlyJoin']=True
            face['identityJoinEvidence']['cardIdModuloJoin']=True
        checks=run_mutation(sheet_cell_modulo_and_back_inversion)
        self.assertIn('Objective title/body/category/alias/folder/order/sheet/cell/modulo join prohibited',checks)
        self.assertIn('Objective selector/back inversion',checks)

        def player_count_panel_icon_checkbox_and_grouping_drift(data):
            source=data['objective-mission-source-index.json']
            face=next(row for row in source['physicalFaces'] if row['checkboxPanels'])
            face['playerCountMetadata']['ttsGmNotesMinimum']=5
            face['printedCondition']+='!'
            face['checkboxPanels']=[]
            face['conditionConnectorCounts']['AND']=0
            face['panels'][0]['readingOrder']=99
            face['iconOccurrences'][0]['semanticReferenceId']='icon.queen'
        checks=run_mutation(player_count_panel_icon_checkbox_and_grouping_drift)
        self.assertIn('Objective/Mission exact physical tuple/panel/text/icon/condition projection',checks)
        self.assertIn('Objective panel/body/punctuation/order closure',checks)

        def promote_occluded_text(data):
            row=next(item for item in data['objective-mission-source-index.json']['officialHelpOccurrences'] if item['visibility']=='partially-occluded')
            row['visibility']='fully-visible'; row['printedCondition']='borrowed licensed body'; row['semanticRuleId']='SEM-OBJECTIVE-BGA-OBJECTIVE-ANOLDFEUD-001'; row['boundaryRuleId']=None; row['occludedMetadataPromotedToVisibleEvidence']=True
        checks=run_mutation(promote_occluded_text)
        self.assertIn('Objective occluded-text non-promotion lock',checks)
        self.assertIn('Objective exact official Help visible/occluded projection',checks)

        def leak_identity_and_invent_default(data):
            secrecy=next(row for row in data['pilots.json']['records'] if row['ruleId']=='SEM-OBJECTIVE-SECRECY-001')
            secrecy['informationPolicy'][0]['audience']='public'
            question=next(row for row in data['review-gates.json']['questions'] if row['questionId']=='SEM-Q-075')
            question['defaultProhibited']=False
        checks=run_mutation(leak_identity_and_invent_default)
        self.assertIn('Objective private identity/removal/inspection/no-exposure lock',checks)
        self.assertIn('Objective ambiguity owner/timing/default linkage',checks)

        def lifecycle_and_fulfillment_drift(data):
            records={row['ruleId']:row for row in data['pilots.json']['records']}
            choice=records['SEM-RT-010']; choice['operations'][3],choice['operations'][4]=choice['operations'][4],choice['operations'][3]
            for index,op in enumerate(choice['operations'],1): op['sequence']=index; op['stepId']=f'S{index:02d}'
            endgame=records['SEM-ENDGAME-001']; endgame['operations']=[op for op in endgame['operations'] if op['stepId']!='S07']
            for index,op in enumerate(endgame['operations'],1): op['sequence']=index; op['stepId']=f'S{index:02d}'
            face=next(row for row in data['objective-mission-source-index.json']['physicalFaces'] if row['semanticRuleId'] and len(row['conditionTree']['clauses'])>1)
            face['conditionTree']['clauses']=list(reversed(face['conditionTree']['clauses']))
        checks=run_mutation(lifecycle_and_fulfillment_drift)
        self.assertIn('Objective Choice post-move track/draw/lifecycle lock',checks)
        self.assertIn('Objective late-choice/reveal/endgame lifecycle lock',checks)
        self.assertIn('Objective/Mission exact physical tuple/panel/text/icon/condition projection',checks)

        def lose_variant_authority_and_leak_solo(data):
            source=data['objective-mission-source-index.json']
            source['licensedDigitalOccurrences'][0]=json.loads(json.dumps(source['licensedDigitalOccurrences'][1]))
            solo=next(row for row in source['licensedDigitalOccurrences'] if row['competitiveDisposition']=='solo-coop-excluded')
            solo['competitiveDisposition']='base-competitive-licensed-occurrence'; solo['semanticRuleId']='SEM-OBJECTIVE-BGA-OBJECTIVE-OFFICIALORDER-001'
            source['officialHelpOccurrences']=[row for row in source['officialHelpOccurrences'] if row['sourceUnitId']!='P1-MO-OFFICIAL-ORDER-1']
        checks=run_mutation(lose_variant_authority_and_leak_solo)
        self.assertIn('Objective exact independent licensed row/variant closure',checks)
        self.assertIn('Objective exact official Help visible/occluded projection',checks)

        def promote_blocked_face(data):
            source=data['objective-mission-source-index.json']
            face=next(row for row in source['physicalFaces'] if row['sourcePath'].endswith('missionTaskDeck-023.png'))
            face['semanticRuleId']='SEM-MISSION-TASK-OFFICIAL-P1-MT-FACILITY-RESTART-001'
            face['printedCondition']=face['printedCondition'].replace('[illegible]','[lifeSupportActive]')
        checks=run_mutation(promote_blocked_face)
        self.assertIn('Objective FACILITY RESTART source-blocker/no-substitution lock',checks)

        def coordinated_backlog_lowering(data):
            source=data['objective-mission-source-index.json']; backlog=data['backlog.json']
            target=next(unit_id for unit_id in source['familyCountEvidence']['backlog']['linkedUnitIds'] if unit_id.startswith('CARD:') and unit_id!='CARD:eaa728ca02c48c33')
            backlog['units']=[row for row in backlog['units'] if row['semanticUnitId']!=target]
            backlog['counts']['units']-=1; backlog['counts']['byChannel']['card-reference-source-tuple']-=1; backlog['counts']['byStatus']['pilot-covered']-=1
            source['familyCountEvidence']['backlog']['linkedUnitIds'].remove(target)
            source['familyCountEvidence']['backlog']['cardUnitIds'].remove(target)
            source['counts']['cardBacklogTuples']-=1; source['counts']['overlappingBacklogObligationsLinked']-=1
        checks=run_mutation(coordinated_backlog_lowering)
        self.assertIn('Objective exact overlapping backlog-obligation closure',checks)
        self.assertIn('semantic backlog declared counts',checks)

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
            next(op for op in by_id['SEM-RT-011']['operations'] if op.get('invokeRuleId')=='SEM-IH-QA-B-01')['invokeRuleId']='SEM-IH-QD-B-02'
            hatch_assertion=next(row for row in by_id['SEM-EVENT-HATCHING-001']['sourceAssertions'] if row['assertionId']=='SA-EVT-5616-SCAN')
            hatch_assertion['supportsFields']=[field for field in hatch_assertion['supportsFields'] if field!='operations']
            (root/'room-icon-denotations.json').write_text(json.dumps(room_icons,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
            (root/'pilots.json').write_text(json.dumps({'schemaVersion':1,'recordType':'semantic-rule-pilot-corpus','scope':'test','counts':pilots['counts'],'records':list(by_id.values())},indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
            run,report=self.run_validator(root,skip=True)
        self.assertNotEqual(run.returncode,0)
        checks={failure['check'] for failure in report['failures']}
        self.assertTrue({'independently locked Room icon denotation map','Room-context exact Help dispatch','Bag Development exact Queen-side Help dispatch','Intruder Help token-back count/color','operation assertion support'}.issubset(checks),sorted(checks))


if __name__=='__main__': unittest.main()
