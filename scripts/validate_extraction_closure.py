#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
REPO=Path(__file__).resolve().parents[1]; SRC=REPO/'docs/rules/source-extraction'; RECORD=SRC/'extraction-closure-audit.json'
def load(p): return json.loads(p.read_text())
def main():
 d=load(RECORD); failures=[]; base=load(SRC/'base-source-inventory.json'); gaps=load(SRC/'card-gap-inventory.json')
 expected={'channels':9,'extractedOrIndexedChannels':9,'explicitBlockers':1,'gateCriteria':6,'passedGateCriteria':6,'remainingGraphicalSourceUnits':0}
 if d.get('counts')!=expected: failures.append({'check':'closure counts','expected':expected,'actual':d.get('counts')})
 channels=d.get('channels') or []
 if len(channels)!=9 or len({c.get('channelId') for c in channels})!=9: failures.append({'check':'channel closure'})
 for c in channels:
  path=c.get('evidencePath')
  if not path or not (REPO/path).is_file(): failures.append({'check':'channel evidence','channel':c.get('channelId'),'path':path})
  if c.get('status') not in {'extracted','extracted-with-explicit-physical-occlusion','extracted-with-source-conflicts','extracted-with-one-explicit-blocker','indexed-secondary'}: failures.append({'check':'channel status','channel':c.get('channelId')})
 blockers=d.get('explicitBlockers') or []
 if blockers!=gaps.get('remainingOpenSourceBlockers') or len(blockers)!=1 or blockers[0].get('sourcePath')!='assets/tts-mod/extract/v2-dl/tree/cards/game/missionTaskDeck-023.png': failures.append({'check':'explicit blocker closure'})
 criteria=d.get('gateCriteria') or []
 if len(criteria)!=6 or not all(x.get('passed') is True for x in criteria): failures.append({'check':'gate criteria'})
 decision=d.get('gateDecision') or {}
 if decision.get('passed') is not True or decision.get('nextPhase')!='canonical vocabulary and source-scoped aliases' or not decision.get('decision','').startswith('PASS'):
  failures.append({'check':'gate decision'})
 if base.get('remainingGraphicalSourceUnits')!=[] or d.get('authorityOrder')!=base.get('authorityOrder') or d.get('scope')!=base.get('scope'): failures.append({'check':'base inventory closure'})
 # Extraction JSONs may discuss future layers but must not define them structurally.
 forbidden={'canonicalVocabulary','aliasRegistry','taxonomy','ontology','semanticRules','semanticLayer'}
 found=[]
 def walk(v,path):
  if isinstance(v,dict):
   for k,x in v.items():
    if k in forbidden: found.append(f'{path}.{k}')
    walk(x,f'{path}.{k}')
  elif isinstance(v,list):
   for i,x in enumerate(v): walk(x,f'{path}[{i}]')
 for p in SRC.glob('*.json'):
  if p.name=='extraction-closure-audit.json': continue
  walk(load(p),p.name)
 if found: failures.append({'check':'future-layer structural leakage','paths':found})
 report={'schemaVersion':1,'passed':not failures,'checks':expected,'failureCount':len(failures),'failures':failures}; print(json.dumps(report,indent=2,ensure_ascii=False)); return 0 if not failures else 1
if __name__=='__main__': raise SystemExit(main())
