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
FILES=('source-registry.json','semantic-rule.schema.json','pilots.json','review-gates.json','coverage.json','backlog.json')


def load(path): return json.loads(path.read_text(encoding='utf-8'))


class SemanticPilotTests(unittest.TestCase):
    def run_validator(self, root=None, skip=False):
        base=root or DIR
        command=['python3',str(VALIDATOR),'--source-registry',str(base/'source-registry.json'),'--schema',str(base/'semantic-rule.schema.json'),'--pilots',str(base/'pilots.json'),'--review-gates',str(base/'review-gates.json'),'--coverage',str(base/'coverage.json'),'--backlog',str(base/'backlog.json')]
        if skip: command.append('--skip-reproducibility')
        run=subprocess.run(command,cwd=REPO,check=False,capture_output=True,text=True,timeout=300)
        return run,json.loads(run.stdout)

    def test_current_pilot_passes_and_rebuilds(self):
        run,report=self.run_validator()
        self.assertEqual(run.returncode,0,run.stdout+run.stderr)
        self.assertTrue(report['passed'])
        self.assertEqual(report['checks']['records'],13)
        self.assertEqual(report['checks']['operations'],61)
        self.assertEqual(report['checks']['openQuestions'],7)
        self.assertEqual(report['checks']['backlogUnits'],600)

    def test_high_risk_semantic_boundaries(self):
        pilots=load(DIR/'pilots.json'); by_id={r['ruleId']:r for r in pilots['records']}
        self.assertIn('bottom of its respective deck',json.dumps(by_id['SEM-ACT-SEARCH-001']))
        self.assertIn('unchosen Items must not be revealed',json.dumps(by_id['SEM-ACT-SEARCH-001']))
        self.assertEqual(by_id['SEM-EVENT-HATCHING-001']['partialResolution']['policy'],'per-sentence-continue')
        self.assertIn('OQ-009',by_id['SEM-EVENT-HATCHING-001']['unresolvedQuestionRefs'])
        self.assertEqual(by_id['SEM-REACTION-DUCK-001']['ruleKind'],'reaction')
        self.assertIn('SEM-Q-001',by_id['SEM-REACTION-DUCK-001']['unresolvedQuestionRefs'])
        self.assertTrue(all(r['implementationBoundary'].startswith('implementation-neutral') for r in pilots['records']))

    def test_adversarial_corruptions_are_rejected(self):
        with tempfile.TemporaryDirectory(prefix='semantic-negative-') as temp_dir:
            root=Path(temp_dir)
            for name in FILES: (root/name).write_text((DIR/name).read_text(encoding='utf-8'),encoding='utf-8')
            sources=load(root/'source-registry.json'); pilots=load(root/'pilots.json'); review=load(root/'review-gates.json'); coverage=load(root/'coverage.json'); backlog=load(root/'backlog.json')
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
            coverage['systems'][0]['ruleIds'].append(coverage['systems'][1]['ruleIds'][0])
            pending=next(item for item in backlog['units'] if item['status']=='pending')
            pending['status']='pilot-covered'
            for name,data in [('source-registry.json',sources),('pilots.json',pilots),('review-gates.json',review),('coverage.json',coverage),('backlog.json',backlog)]:
                (root/name).write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
            run,report=self.run_validator(root,skip=True)
        self.assertNotEqual(run.returncode,0)
        checks={f['check'] for f in report['failures']}
        required={'source tuple','record schema fields','implementation boundary','controlled term references','taxon references','record authority precedence','operation IDs/order','operation source linkage','decision completeness','partial-resolution completeness','source variant completeness','semantic question no-default/linkage','Event partial/Nest ambiguity fidelity','semantic pilot coverage projection','semantic backlog status/link consistency','hard-coded semantic pilot counts'}
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


if __name__=='__main__': unittest.main()
