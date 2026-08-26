#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,re
from collections import Counter
from pathlib import Path

REPO=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--output',type=Path,default=REPO/'docs/rules/semantics/backlog.json')
args=parser.parse_args()
OUT=args.output.resolve()
OUT.parent.mkdir(parents=True,exist_ok=True)

def load(rel): return json.loads((REPO/rel).read_text(encoding='utf-8'))
units=[]
def add(uid,channel,label,source_path,source_locator,status='pending',pilot_ids=None,authority=None,blockers=None):
 units.append({'semanticUnitId':uid,'channel':channel,'label':label,'sourcePath':source_path,'sourceLocator':source_locator,'authority':authority,'status':status,'pilotRuleIds':pilot_ids or [],'blockers':blockers or []})

# Human rule records.
for rel in ('docs/rules/00-foundations.md','docs/rules/01-round-and-turns.md','docs/rules/02-character-actions.md','docs/rules/03-intruders-and-survival.md','docs/rules/04-items-and-equipment.md'):
 text=(REPO/rel).read_text(encoding='utf-8')
 for match in re.finditer(r'^##\s+((?:FND|RT|ACT|INT|ITM)-[A-Z0-9-]+)\s+—\s+(.+)$',text,re.M):
  rid,title=match.groups(); add(f'RULE:{rid}','interpreted-rule-record',title,rel,rid,authority='project-interpretation')
# FAQ base-applicable obligations.
faq=load('docs/rules/source-extraction/faq-v1.2-source-extraction.json')
for page in faq['pages']:
 for row in page.get('units',[]):
  if row.get('applicability') in ('base-game','base-game-additional-mode'):
   add(f"FAQ:{row['sourceUnitId']}",'official-faq-unit',row.get('questionText') or row.get('title') or row['sourceUnitId'],faq['source']['path'],row['sourceUnitId'],authority='official-errata')
# Rulebook visual obligations.
rb=load('docs/rules/source-extraction/rulebook-visual-obligations.json')
for page in rb['pages']:
 for row in page.get('visualUnits',[]):
  add(f"VIS:{row['occurrenceId']}",'rulebook-visual-obligation',row.get('type') or row['occurrenceId'],rb['source']['path'],row['occurrenceId'],authority='official-primary')
# Room and Objective Help units.
rooms=load('docs/rules/source-extraction/room-help-sheet.json')
for row in rooms['entries']:
 add(f"ROOM:{row['printedNumber']}",'room-help-entry',row['printedTitle'],rooms['source']['path'],row['printedNumber'],authority='official-component-reference')
objectives=load('docs/rules/source-extraction/objective-help-sheet.json')
for row in objectives['units']:
 add(f"OBJ:{row['sourceUnitId']}",'objective-help-unit',row.get('printedTitle') or row.get('heading') or row['sourceUnitId'],objectives['source']['path'],row['sourceUnitId'],authority='official-component-reference',blockers=['physical-occlusion'] if row.get('visibility')=='partially-occluded' else [])
# Intruder Help instruction occurrences.
intruder=load('docs/rules/source-extraction/intruder-help-sheet.json')
for side in intruder['sides']:
 for column in side['columns']:
  for row in column['rows']:
   add(f"INTR:{row['occurrenceId']}",'intruder-help-instruction',row['printedInstruction'].replace('\n',' '),side['sourcePath'],row['occurrenceId'],authority='source-bound-component-scan')
 bottom=side['bottomRow']; add(f"INTR:{bottom['occurrenceId']}",'intruder-help-instruction',bottom['printedInstruction'].replace('\n',' '),side['sourcePath'],bottom['occurrenceId'],authority='source-bound-component-scan')
# Every rules-bearing card/reference source tuple remains independent.
corpus=load('assets/tts-mod/extract/card-text-corpus.json')
for row in corpus['records']:
 if not row.get('rulesTextPresent'): continue
 pd=row.get('printedData') or {}; identity=row.get('identity') or {}; label=pd.get('title') or identity.get('titleFromCanonicalSlug') or row['sourcePath'].rsplit('/',1)[-1]
 blockers=[]
 if row.get('extractionState')=='draft-partial': blockers.append('exact-source-operative-span')
 if row.get('canonicalPromotionBlocker'): blockers.append('source-variant-or-promotion-boundary')
 add(f"CARD:{row['sourceSha256'][:16]}",'card-reference-source-tuple',label,row['sourcePath'],row['sourceSha256'],authority='mixed-source-bound',blockers=blockers)

event_sources=load('docs/rules/semantics/event-source-index.json')
exploration_sources=load('docs/rules/semantics/exploration-source-index.json')
robot_sources=load('docs/rules/semantics/robot-source-index.json')
attack_sources=load('docs/rules/semantics/attack-source-index.json')
exploration_rule_ids=[row['semanticRuleId'] for row in exploration_sources['faces']]
robot_rule_ids=[row['semanticRuleId'] for row in robot_sources['faces']]
attack_rule_ids=[row['semanticRuleId'] for row in attack_sources['faces']]

# Pilot-to-source obligation links. These are evidence coverage links, not claims
# that the entire channel/category is semantically complete.
links={
 'RULE:FND-003':['SEM-EVENT-GENERAL-001'],
 'RULE:RT-001':['SEM-RT-001'],'RULE:RT-004':['SEM-RT-004'],'RULE:RT-005':['SEM-RT-005'],'RULE:RT-007':['SEM-RT-007'],'RULE:RT-008':['SEM-RT-008'],'RULE:RT-009':['SEM-RT-009','SEM-EVENT-GENERAL-001'],'RULE:RT-010':['SEM-RT-010'],'RULE:RT-011':['SEM-RT-011'],'RULE:RT-012':['SEM-RT-012'],
 'RULE:ACT-MOVE-001':['SEM-ACT-MOVE-001'],'RULE:ACT-EXPLORE-001':['SEM-ACT-EXPLORE-001',*exploration_rule_ids],'RULE:ACT-SEARCH-001':['SEM-ACT-SEARCH-001'],'RULE:ACT-ROBOT-001':['SEM-ACT-ROBOT-001','SEM-ROBOT-SETUP-001','SEM-ROBOT-REVEAL-001','SEM-ROBOT-MOVEMENT-001','SEM-ROBOT-MALFUNCTION-001','SEM-ROBOT-MALFUNCTION-PLACEMENT-001',*robot_rule_ids],
 'RULE:ACT-TACTICAL-001':['SEM-ACT-TACTICAL-001','SEM-ROBOT-TACTICAL-GEAR-001'],'RULE:ACT-CARD-001':['SEM-ACT-SEARCH-001','SEM-ACT-REST-001'],'RULE:INT-001':['SEM-IH-QA-R-01'],'RULE:INT-004':['SEM-INT-004',*attack_rule_ids],'RULE:INT-006':['SEM-INT-006',*attack_rule_ids],'RULE:INT-008':['SEM-ACT-REST-001','SEM-ENDGAME-001','SEM-CONTAMINATION-GAIN-001',*attack_rule_ids],'RULE:INT-010':['SEM-AUTODESTRUCTION-001'],'RULE:INT-011':['SEM-ENDGAME-001'],'RULE:ITM-005':['SEM-ITM-005','SEM-ACT-TACTICAL-001','SEM-ROBOT-TACTICAL-GEAR-001'],
 'VIS:RB-P12-V02':['SEM-ACT-MOVE-001','SEM-ROOM-01'],'ROOM:01':['SEM-ROOM-01'],'INTR:QA-R-01':['SEM-IH-QA-R-01'],
 'CARD:b34d341ff67972b8':['SEM-ACT-SEARCH-001'],'CARD:69eee8ba31616f20':['SEM-ACT-REST-001'],'CARD:a3ad029d27fc444d':['SEM-REACTION-DUCK-001'],'CARD:45b5845d04f57b1':['SEM-EVENT-HATCHING-001'],
}
for event in event_sources['events']:
 links[event['backlogUnitId']]=[event['semanticRuleId']]
for face in exploration_sources['faces']:
 links[face['backlogUnitId']]=[face['semanticRuleId']]
for face in robot_sources['faces']:
 links[face['backlogUnitId']]=[face['semanticRuleId']]
for face in attack_sources['faces']:
 links[face['backlogUnitId']]=[face['semanticRuleId']]
links['FAQ:FQ-P02-U06']=['SEM-ACT-EXPLORE-001',*[row['semanticRuleId'] for row in exploration_sources['faces'] if any(item['sourceUnitId']=='FQ-P02-U06' for item in row['faqOccurrences'])]]
links['FAQ:FQ-P02-U07']=['SEM-ACT-EXPLORE-001',*[row['semanticRuleId'] for row in exploration_sources['faces'] if any(item['sourceUnitId']=='FQ-P02-U07' for item in row['faqOccurrences'])]]
links['VIS:RB-P24-V01']=['SEM-ACT-EXPLORE-001','SEM-EXPLORATION-5639-001']
links['VIS:RB-P26-V01']=['SEM-ACT-EXPLORE-001','SEM-EXPLORATION-5634-001']
links['VIS:RB-P27-V01']=['SEM-ACT-EXPLORE-001','SEM-EXPLORATION-5634-001']
links['FAQ:FQ-P02-U08']=['SEM-NOISE-MARKER-001','SEM-EVENT-SYSTEM-FAILURE-001','SEM-EVENT-PANIC-001','SEM-EVENT-BREAKING-IN-001','SEM-EVENT-HATCHING-001']
links['FAQ:FQ-P02-U09']=['SEM-FIRE-SPREAD-001','SEM-EVENT-FIRE-BREATH-001','SEM-EVENT-DAMAGING-FIRE-001']
links['FAQ:FQ-P02-U11']=['SEM-EVENT-LEAVING-THE-SHELL-001','SEM-EVENT-REACTOR-OVERHEATING-001']
links['FAQ:FQ-P02-U11'].append('SEM-ATTACK-394912-001')
links['FAQ:FQ-P02-U12']=['SEM-EVENT-INTRUDER-MOVEMENT-001']
links['FAQ:FQ-P02-U13']=['SEM-SECURE-ENTRY-001']
links['FAQ:FQ-P02-U16']=['SEM-INT-004','SEM-REACTION-DUCK-001']
links['VIS:RB-P03-V01']=['SEM-EVENT-REACTOR-OVERHEATING-001','SEM-EVENT-SCENT-OF-PREY-001']
links['VIS:RB-P03-V01'].extend(['SEM-INT-004',*[row['semanticRuleId'] for row in attack_sources['faces'] if row['officialCounterpartRefs']]])
links['VIS:RB-P03-V01'].extend(['SEM-ROBOT-SETUP-001','SEM-ROBOT-SERVER-001','SEM-ROBOT-TECHNICAL-001'])
links['VIS:RB-P05-V01']=['SEM-ROBOT-SETUP-001','SEM-ROBOT-MALFUNCTION-PLACEMENT-001','SEM-ROBOT-SECURING-001','SEM-ROBOT-TACTICAL-GEAR-001']
links['VIS:RB-P05-V02']=['SEM-ROBOT-SETUP-001']
links['VIS:RB-P08-V03']=['SEM-ROBOT-SETUP-001','SEM-ROBOT-REVEAL-001']
links['VIS:RB-P09-V01']=['SEM-ROBOT-SETUP-001']
links['VIS:RB-P12-V02'].extend(['SEM-ACT-ROBOT-001','SEM-ACT-TACTICAL-001'])
links['VIS:RB-P37-V01']=['SEM-ACT-ROBOT-001','SEM-ROBOT-REVEAL-001','SEM-ROBOT-MOVEMENT-001','SEM-ROBOT-TACTICAL-GEAR-001','SEM-ROBOT-MALFUNCTION-001']
links['VIS:RB-P40-V02']=['SEM-ACT-ROBOT-001',*robot_rule_ids]
links['VIS:RB-P14-V01']=['SEM-EVENT-GENERAL-001','SEM-EVENT-RISE-OF-THE-MACHINE-001']
links['VIS:RB-P14-V02']=['SEM-EVENT-INTRUDER-MOVEMENT-001']
links['VIS:RB-P31-V01']=['SEM-EVENT-INTRUDER-MOVEMENT-001','SEM-EVENT-SHORT-CIRCUIT-001']
links['VIS:RB-P31-V02']=['SEM-EVENT-INTRUDER-MOVEMENT-001']
links['VIS:RB-P32-V01']=['SEM-INT-004','SEM-ATTACK-394911-001']
for unit in units:
 if unit['semanticUnitId'].startswith('INTR:'):
  occurrence_id=unit['semanticUnitId'].split(':',1)[1]
  links[unit['semanticUnitId']]=[f'SEM-IH-{occurrence_id}']
 elif unit['semanticUnitId'].startswith('ROOM:'):
  room_number=unit['semanticUnitId'].split(':',1)[1]
  room_extras=[]
  if room_number=='02': room_extras.append('SEM-ROOM-02-SECURE')
  if room_number in {'04','12','25'}: room_extras.append('SEM-ROOM-STATIC-PROHIBITIONS')
  if room_number in {'07','17'}: room_extras.append('SEM-ROBOT-MALFUNCTION-001')
  if room_number=='20': room_extras.append('SEM-DATA-TOKEN-001')
  links[unit['semanticUnitId']]=[f'SEM-ROOM-{room_number}',*room_extras]
links['FAQ:FQ-P02-U17']=['SEM-ROOM-17']
links['FAQ:FQ-P02-U18']=['SEM-ROOM-02-SECURE']
links['FAQ:FQ-P02-U19']=['SEM-ROOM-12']
for unit in units:
 if unit['semanticUnitId'] in links:
  unit['status']='pilot-covered'; unit['pilotRuleIds']=links[unit['semanticUnitId']]
 elif 'exact-source-operative-span' in unit['blockers']:
  unit['status']='source-blocked'

counts=Counter(unit['channel'] for unit in units); status_counts=Counter(unit['status'] for unit in units)
payload={'schemaVersion':1,'recordType':'semantic-source-obligation-backlog','policy':'Source-unit ledger. Counts intentionally retain overlapping source channels and variants; a pilot link means representative evidence use, not full semantic coverage.','counts':{'units':len(units),'byChannel':dict(sorted(counts.items())),'byStatus':dict(sorted(status_counts.items()))},'units':units}
OUT.write_text(json.dumps(payload,indent=2,ensure_ascii=False)+'\n')
print(json.dumps(payload['counts'],indent=2))
