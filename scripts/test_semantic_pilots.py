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
FILES=('source-registry.json','semantic-rule.schema.json','semantic-vocabulary.json','room-icon-denotations.json','pilots.json','review-gates.json','contradictions.json','coverage.json','backlog.json')


def load(path): return json.loads(path.read_text(encoding='utf-8'))


class SemanticPilotTests(unittest.TestCase):
    def run_validator(self, root=None, skip=False):
        base=root or DIR
        command=['python3',str(VALIDATOR),'--source-registry',str(base/'source-registry.json'),'--schema',str(base/'semantic-rule.schema.json'),'--semantic-vocabulary',str(base/'semantic-vocabulary.json'),'--room-icon-denotations',str(base/'room-icon-denotations.json'),'--pilots',str(base/'pilots.json'),'--review-gates',str(base/'review-gates.json'),'--contradictions',str(base/'contradictions.json'),'--coverage',str(base/'coverage.json'),'--backlog',str(base/'backlog.json')]
        if skip: command.append('--skip-reproducibility')
        run=subprocess.run(command,cwd=REPO,check=False,capture_output=True,text=True,timeout=300)
        return run,json.loads(run.stdout)

    def test_current_pilot_passes_and_rebuilds(self):
        run,report=self.run_validator()
        self.assertEqual(run.returncode,0,run.stdout+run.stderr)
        self.assertTrue(report['passed'])
        self.assertEqual(report['checks']['records'],73)
        self.assertEqual(report['checks']['operations'],281)
        self.assertEqual(report['checks']['decisions'],48)
        self.assertEqual(report['checks']['targets'],20)
        self.assertEqual(report['checks']['openQuestions'],11)
        self.assertEqual(report['checks']['semanticNodes'],22)
        self.assertEqual(report['checks']['conflicts'],8)
        self.assertEqual(report['checks']['backlogUnits'],600)
        self.assertEqual(report['checks']['backlogPilotCovered'],71)
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
        self.assertIn('dispatchRuleIds',json.dumps(by_id['SEM-NOISE-001']))

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
            self.assertTrue(any(item.get('invokeRuleId')=='SEM-INT-004' for item in by_id[rule_id]['operations']))

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
            next(op for op in by_id['SEM-NOISE-001']['operations'] if op.get('dispatchRuleIds')).pop('dispatchRuleIds')
            by_id['SEM-RT-011']['operations'][2]['invokeRuleId']='SEM-IH-QD-B-02'
            hatch_assertion=next(row for row in by_id['SEM-EVENT-HATCHING-001']['sourceAssertions'] if row['assertionId']=='SA-HATCH-2')
            hatch_assertion['supportsFields']=[field for field in hatch_assertion['supportsFields'] if field!='operations']
            (root/'room-icon-denotations.json').write_text(json.dumps(room_icons,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
            (root/'pilots.json').write_text(json.dumps({'schemaVersion':1,'recordType':'semantic-rule-pilot-corpus','scope':'test','counts':pilots['counts'],'records':list(by_id.values())},indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
            run,report=self.run_validator(root,skip=True)
        self.assertNotEqual(run.returncode,0)
        checks={failure['check'] for failure in report['failures']}
        self.assertTrue({'independently locked Room icon denotation map','Room-context exact Help dispatch','Bag Development exact Queen-side Help dispatch','Intruder Help token-back count/color','operation assertion support'}.issubset(checks),sorted(checks))


if __name__=='__main__': unittest.main()
