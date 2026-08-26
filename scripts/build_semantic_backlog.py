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
queen_health_sources=load('docs/rules/semantics/queen-health-source-index.json')
serious_wound_sources=load('docs/rules/semantics/serious-wound-source-index.json')
green_item_sources=load('docs/rules/semantics/green-item-source-index.json')
red_item_sources=load('docs/rules/semantics/red-item-source-index.json')
yellow_item_sources=load('docs/rules/semantics/yellow-item-source-index.json')
action_sources=load('docs/rules/semantics/action-source-index.json')
exploration_rule_ids=[row['semanticRuleId'] for row in exploration_sources['faces']]
robot_rule_ids=[row['semanticRuleId'] for row in robot_sources['faces']]
attack_rule_ids=[row['semanticRuleId'] for row in attack_sources['faces']]
queen_health_rule_ids=[row['semanticRuleId'] for row in queen_health_sources['faces']]
serious_wound_rule_ids=[row['semanticRuleId'] for row in serious_wound_sources['faces']]
green_item_rule_ids=[row['semanticRuleId'] for row in green_item_sources['faces']]
red_item_rule_ids=[row['semanticRuleId'] for row in red_item_sources['faces']]
yellow_item_rule_ids=[row['semanticRuleId'] for row in yellow_item_sources['faces']]
action_rule_ids=[row['semanticRuleId'] for row in action_sources['faces']]
action_reaction_rule_ids=[row['reactionRuleId'] for row in action_sources['faces'] if row.get('reactionRuleId')]

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
for face in queen_health_sources['faces']:
 links.setdefault(face['backlogUnitId'],[]).append(face['semanticRuleId'])
for asset in serious_wound_sources['sourceFaceAssets']:
 unit_id='CARD:'+asset['sourceSha256'][:16]
 physical_rule_ids=[row['semanticRuleId'] for row in serious_wound_sources['faces'] if row['sourcePath']==asset['sourcePath']]
 links[unit_id]=physical_rule_ids or ['SEM-SERIOUS-WOUND-VARIANT-BOUNDARIES-001']
for asset in green_item_sources['sourceFaceAssets']:
 unit_id='CARD:'+asset['sourceSha256'][:16]
 physical_rule_ids=[row['semanticRuleId'] for row in green_item_sources['faces'] if row['sourcePath']==asset['sourcePath']]
 if physical_rule_ids:
  links[unit_id]=physical_rule_ids
 elif asset['sourceRole']=='generated-cell-selector-gap-variant':
  links[unit_id]=['SEM-GREEN-ITEM-VARIANT-BOUNDARIES-001']
for asset in red_item_sources['sourceFaceAssets']:
 unit_id='CARD:'+asset['sourceSha256'][:16]
 physical_rule_ids=[row['semanticRuleId'] for row in red_item_sources['faces'] if row['sourcePath']==asset['sourcePath']]
 if physical_rule_ids:
  links[unit_id]=physical_rule_ids
 elif asset['selectedDisposition']=='red-selector-gap':
  links[unit_id]=['SEM-RED-ITEM-VARIANT-BOUNDARIES-001']
for asset in yellow_item_sources['sourceFaceAssets']:
 unit_id='CARD:'+asset['sourceSha256'][:16]
 physical_rule_ids=[row['semanticRuleId'] for row in yellow_item_sources['faces'] if row['sourcePath']==asset['sourcePath']]
 if physical_rule_ids:
  links[unit_id]=physical_rule_ids
 elif asset['selectedDisposition']=='yellow-selector-gap':
  links[unit_id]=['SEM-YELLOW-ITEM-VARIANT-BOUNDARIES-001']
for asset in action_sources['sourceFaceAssets']:
 unit_id='CARD:'+asset['sourceSha256'][:16]
 physical_rule_ids=[row['semanticRuleId'] for row in action_sources['faces'] if row['sourcePath']==asset['sourcePath']]
 if physical_rule_ids:
  links[unit_id]=physical_rule_ids
 elif asset.get('selectorGap'):
  links[unit_id]=['SEM-ACTION-CARD-VARIANT-BOUNDARIES-001']
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
links['RULE:ACT-SHOOT-001']=['SEM-ACT-SHOOT-001','SEM-QUEEN-HIT-001','SEM-QUEEN-HEALTH-RESOLUTION-001']
links['RULE:ACT-BURST-001']=['SEM-ACT-BURST-001','SEM-QUEEN-HIT-001','SEM-QUEEN-HEALTH-RESOLUTION-001']
links['RULE:INT-001']=[*links.get('RULE:INT-001',[]),'SEM-QUEEN-HEALTH-SETUP-001',*[rule_id for rule_id in queen_health_rule_ids if rule_id in {'SEM-QUEEN-HEALTH-504000-919263-001'}]]
links['RULE:INT-003']=['SEM-INTRUDER-REPEL-001','SEM-QUEEN-ACTIVATION-001']
links['RULE:INT-007']=['SEM-ACT-SHOOT-001','SEM-ACT-BURST-001','SEM-QUEEN-HIT-001','SEM-QUEEN-HEALTH-RESOLUTION-001','SEM-QUEEN-DEATH-001',*queen_health_rule_ids]
links['RULE:INT-010']=[*links.get('RULE:INT-010',[]),'SEM-QUEEN-DEATH-001']
links['RULE:INT-011']=[*links.get('RULE:INT-011',[]),'SEM-QUEEN-DEATH-001']
links['RULE:RT-011']=[*links.get('RULE:RT-011',[]),'SEM-QUEEN-ACTIVATION-001']
links['FAQ:FQ-P02-U03']=['SEM-ACT-SHOOT-001','SEM-QUEEN-HIT-001','SEM-QUEEN-HEALTH-RESOLUTION-001']
links['VIS:RB-P03-V01']=[*links.get('VIS:RB-P03-V01',[]),'SEM-QUEEN-HEALTH-SETUP-001',*queen_health_rule_ids]
links['VIS:RB-P35-V01']=['SEM-QUEEN-HEALTH-SETUP-001','SEM-QUEEN-HIT-001','SEM-QUEEN-HEALTH-RESOLUTION-001','SEM-QUEEN-DEATH-001']
links['VIS:RB-P35-V02']=['SEM-QUEEN-HEALTH-RESOLUTION-001',*queen_health_rule_ids]
links['VIS:RB-P35-V03']=['SEM-QUEEN-HIT-001','SEM-QUEEN-HEALTH-RESOLUTION-001']
links['OBJ:P1-GT-06']=['SEM-QUEEN-DEATH-001']
links['OBJ:P2-GT-06']=['SEM-QUEEN-DEATH-001']
serious_wound_setup_ids=['SEM-SERIOUS-WOUND-SETUP-001','SEM-SERIOUS-WOUND-GAIN-001','SEM-SERIOUS-WOUND-DISCARD-001','SEM-SERIOUS-WOUND-STACKING-001','SEM-SERIOUS-WOUND-VARIANT-BOUNDARIES-001']
serious_wound_pass_ids=[row['semanticRuleId'] for row in serious_wound_sources['faces'] if row['effectKind'] in {'pass-oxygen-or-local-glyph','pass-contamination','pass-health-loss'}]
serious_wound_body_ids=[row['semanticRuleId'] for row in serious_wound_sources['faces'] if row['effectKind']=='hand-size-modifier']
serious_wound_move_ids=[row['semanticRuleId'] for row in serious_wound_sources['faces'] if row['effectKind'] in {'move-cost-modifier','local-action-cost-modifier'}]
serious_wound_hand_ids=[row['semanticRuleId'] for row in serious_wound_sources['faces'] if row['effectKind']=='use-item-cost-modifier']
serious_wound_guts_ids=[row['semanticRuleId'] for row in serious_wound_sources['faces'] if row['effectKind']=='pass-contamination']
serious_wound_lungs_ids=[row['semanticRuleId'] for row in serious_wound_sources['faces'] if row['effectKind']=='pass-oxygen-or-local-glyph']
links['RULE:INT-006']=[*links.get('RULE:INT-006',[]),*serious_wound_setup_ids,*serious_wound_rule_ids]
links['RULE:RT-007']=[*links.get('RULE:RT-007',[]),*serious_wound_pass_ids]
links['RULE:RT-012']=[*links.get('RULE:RT-012',[]),*serious_wound_body_ids]
links['RULE:ACT-MOVE-001']=[*links.get('RULE:ACT-MOVE-001',[]),*serious_wound_move_ids]
links['RULE:ACT-CARD-001']=[*links.get('RULE:ACT-CARD-001',[]),*serious_wound_hand_ids]
links['RULE:INT-008']=[*links.get('RULE:INT-008',[]),*serious_wound_guts_ids]
links['ROOM:03']=[*links.get('ROOM:03',[]),'SEM-SERIOUS-WOUND-DISCARD-001']
links['ROOM:16']=[*links.get('ROOM:16',[]),'SEM-SERIOUS-WOUND-DISCARD-001']
links['VIS:RB-P03-V01']=[*links.get('VIS:RB-P03-V01',[]),'SEM-SERIOUS-WOUND-SETUP-001','SEM-SERIOUS-WOUND-VARIANT-BOUNDARIES-001']
links['VIS:RB-P09-V01']=[*links.get('VIS:RB-P09-V01',[]),'SEM-SERIOUS-WOUND-SETUP-001']
links['VIS:RB-P17-V03']=[*serious_wound_lungs_ids]
links['VIS:RB-P18-V01']=['SEM-SERIOUS-WOUND-GAIN-001','SEM-SERIOUS-WOUND-DISCARD-001','SEM-SERIOUS-WOUND-STACKING-001']
links['VIS:RB-P18-V02']=['SEM-SERIOUS-WOUND-GAIN-001']
links['VIS:RB-P18-V03']=['SEM-SERIOUS-WOUND-SETUP-001','SEM-SERIOUS-WOUND-GAIN-001','SEM-SERIOUS-WOUND-VARIANT-BOUNDARIES-001']
links['VIS:RB-P40-V02']=[*links.get('VIS:RB-P40-V02',[]),*serious_wound_rule_ids]
green_restore_ids=[row['semanticRuleId'] for row in green_item_sources['faces'] if row['effectKind'] in {'restore-or-gain-medpack','discard-wound-or-restore','restore-or-local-draw'}]
green_medkit_ids=[row['semanticRuleId'] for row in green_item_sources['faces'] if row['effectKind']=='restore-or-gain-medpack']
green_life_support_ids=[row['semanticRuleId'] for row in green_item_sources['faces'] if row['effectKind']=='flip-life-support']
links['RULE:ACT-ITEM-001']=['SEM-USE-ITEM-001','SEM-GREEN-ITEM-ONE-USE-001','SEM-REGULAR-ITEM-BACKPACK-001',*green_item_rule_ids]
links['RULE:ACT-TRADE-001']=['SEM-ITEM-TRADE-GAIN-001','SEM-REGULAR-ITEM-BACKPACK-001','SEM-GREEN-ITEM-IMMEDIATE-USE-001']
links['RULE:ITM-001']=['SEM-GREEN-ITEM-DECK-001']
links['RULE:ITM-002']=['SEM-REGULAR-ITEM-BACKPACK-001','SEM-GREEN-ITEM-VARIANT-BOUNDARIES-001']
links['RULE:ITM-003']=['SEM-GREEN-ITEM-DECK-001','SEM-GREEN-ITEM-VARIANT-BOUNDARIES-001']
links['RULE:ITM-004']=['SEM-GREEN-ITEM-DECK-001','SEM-GREEN-ITEM-VARIANT-BOUNDARIES-001']
links['RULE:ITM-006']=[*links.get('RULE:ITM-006',[]),'SEM-ACT-SEARCH-001','SEM-GREEN-ITEM-DECK-001']
links['RULE:ITM-008']=['SEM-GREEN-ITEM-VARIANT-BOUNDARIES-001',*green_item_rule_ids]
links['FAQ:FQ-P02-U04']=[*links.get('FAQ:FQ-P02-U04',[]),*green_life_support_ids]
links['FAQ:FQ-P03-U04']=['SEM-ITEM-TRADE-GAIN-001','SEM-GREEN-ITEM-IMMEDIATE-USE-001',*green_medkit_ids]
links['FAQ:FQ-P03-U07']=['SEM-ITEM-INTERPLAY-001','SEM-RESTORE-HEALTH-001',*green_restore_ids]
links['VIS:RB-P03-V01']=[*links.get('VIS:RB-P03-V01',[]),'SEM-GREEN-ITEM-DECK-001','SEM-GREEN-ITEM-VARIANT-BOUNDARIES-001']
links['VIS:RB-P09-V01']=[*links.get('VIS:RB-P09-V01',[]),'SEM-GREEN-ITEM-DECK-001']
links['VIS:RB-P12-V02']=[*links.get('VIS:RB-P12-V02',[]),'SEM-USE-ITEM-001','SEM-ITEM-TRADE-GAIN-001']
links['VIS:RB-P28-V02']=['SEM-ACT-SEARCH-001','SEM-GREEN-ITEM-DECK-001','SEM-REGULAR-ITEM-BACKPACK-001']
links['VIS:RB-P28-V03']=['SEM-USE-ITEM-001','SEM-GREEN-ITEM-ONE-USE-001','SEM-REGULAR-ITEM-BACKPACK-001']
links['VIS:RB-P29-V01']=['SEM-GREEN-ITEM-DECK-001','SEM-GREEN-ITEM-VARIANT-BOUNDARIES-001']
links['VIS:RB-P40-V02']=[*links.get('VIS:RB-P40-V02',[]),'SEM-GREEN-ITEM-DECK-001',*green_item_rule_ids]
red_ammo_ids=[row['semanticRuleId'] for row in red_item_sources['faces'] if row['effectKind']=='gain-ammo']
red_anti_ids=[row['semanticRuleId'] for row in red_item_sources['faces'] if row['effectKind']=='reorder-anti-aircraft']
red_exploring_ids=[row['semanticRuleId'] for row in red_item_sources['faces'] if row['effectKind']=='remote-exploration']
red_flashbang_ids=[row['semanticRuleId'] for row in red_item_sources['faces'] if row['effectKind']=='flashbang-movement']
red_grenade_ids=[row['semanticRuleId'] for row in red_item_sources['faces'] if row['effectKind']=='grenade-effect-or-gain']
red_personal_ids=[row['semanticRuleId'] for row in red_item_sources['faces'] if row['effectKind']=='inspect-objectives']
red_portable_ids=[row['semanticRuleId'] for row in red_item_sources['faces'] if row['effectKind']=='place-closed-door']
links['RULE:ACT-ITEM-001']=[*links.get('RULE:ACT-ITEM-001',[]),'SEM-RED-ITEM-ONE-USE-001',*red_item_rule_ids]
links['RULE:ACT-MOVE-001']=[*links.get('RULE:ACT-MOVE-001',[]),*red_flashbang_ids]
links['RULE:ACT-EXPLORE-001']=[*links.get('RULE:ACT-EXPLORE-001',[]),*red_exploring_ids]
links['RULE:ACT-TRADE-001']=[*links.get('RULE:ACT-TRADE-001',[]),'SEM-RED-ITEM-IMMEDIATE-USE-001']
links['RULE:ACT-TACTICAL-001']=[*links.get('RULE:ACT-TACTICAL-001',[]),'SEM-AMMO-TOKEN-LIFECYCLE-001','SEM-GRENADE-TOKEN-EFFECT-001']
links['RULE:ITM-001']=[*links.get('RULE:ITM-001',[]),'SEM-RED-ITEM-DECK-001']
links['RULE:ITM-002']=[*links.get('RULE:ITM-002',[]),'SEM-RED-ITEM-VARIANT-BOUNDARIES-001']
links['RULE:ITM-003']=[*links.get('RULE:ITM-003',[]),'SEM-RED-ITEM-DECK-001','SEM-RED-ITEM-VARIANT-BOUNDARIES-001']
links['RULE:ITM-004']=[*links.get('RULE:ITM-004',[]),'SEM-RED-ITEM-DECK-001','SEM-RED-ITEM-VARIANT-BOUNDARIES-001']
links['RULE:ITM-005']=[*links.get('RULE:ITM-005',[]),'SEM-AMMO-TOKEN-LIFECYCLE-001','SEM-GRENADE-TOKEN-EFFECT-001',*red_ammo_ids,*red_grenade_ids]
links['RULE:ITM-006']=[*links.get('RULE:ITM-006',[]),'SEM-RED-ITEM-DECK-001']
links['RULE:ITM-008']=[*links.get('RULE:ITM-008',[]),'SEM-RED-ITEM-VARIANT-BOUNDARIES-001',*red_item_rule_ids]
links['FAQ:FQ-P02-U04']=[*links.get('FAQ:FQ-P02-U04',[]),*red_anti_ids,*red_personal_ids]
links['FAQ:FQ-P02-U10']=['SEM-DOOR-001','SEM-GRENADE-TOKEN-EFFECT-001',*red_grenade_ids,*red_portable_ids]
links['FAQ:FQ-P03-U04']=[*links.get('FAQ:FQ-P03-U04',[]),'SEM-RED-ITEM-IMMEDIATE-USE-001',*red_ammo_ids,*red_grenade_ids]
links['FAQ:FQ-P03-U06']=['SEM-ACT-TACTICAL-001','SEM-GRENADE-TOKEN-EFFECT-001']
links['FAQ:FQ-P03-U07']=[*links.get('FAQ:FQ-P03-U07',[]),'SEM-ITEM-INTERPLAY-001',*red_ammo_ids,*red_grenade_ids]
links['FAQ:FQ-P03-U08']=['SEM-RED-ITEM-VARIANT-BOUNDARIES-001',*red_portable_ids]
links['VIS:RB-P03-V01']=[*links.get('VIS:RB-P03-V01',[]),'SEM-RED-ITEM-DECK-001','SEM-RED-ITEM-VARIANT-BOUNDARIES-001']
links['VIS:RB-P05-V01']=[*links.get('VIS:RB-P05-V01',[]),'SEM-ITM-005','SEM-AMMO-TOKEN-LIFECYCLE-001','SEM-GRENADE-TOKEN-EFFECT-001']
links['VIS:RB-P09-V01']=[*links.get('VIS:RB-P09-V01',[]),'SEM-RED-ITEM-DECK-001']
links['VIS:RB-P12-V02']=[*links.get('VIS:RB-P12-V02',[]),'SEM-USE-ITEM-001']
links['VIS:RB-P16-V02']=['SEM-ITM-005',*red_ammo_ids]
links['VIS:RB-P16-V03']=['SEM-AMMO-TOKEN-LIFECYCLE-001']
links['VIS:RB-P17-V01']=['SEM-GRENADE-TOKEN-EFFECT-001',*red_grenade_ids]
links['VIS:RB-P28-V02']=[*links.get('VIS:RB-P28-V02',[]),'SEM-RED-ITEM-DECK-001']
links['VIS:RB-P28-V03']=[*links.get('VIS:RB-P28-V03',[]),'SEM-RED-ITEM-ONE-USE-001']
links['VIS:RB-P29-V01']=[*links.get('VIS:RB-P29-V01',[]),'SEM-RED-ITEM-VARIANT-BOUNDARIES-001']
links['VIS:RB-P29-V03']=['SEM-ITM-005','SEM-AMMO-TOKEN-LIFECYCLE-001','SEM-GRENADE-TOKEN-EFFECT-001']
links['VIS:RB-P33-V03']=['SEM-AMMO-TOKEN-LIFECYCLE-001']
links['VIS:RB-P37-V02']=['SEM-ANTI-AIRCRAFT-TOKEN-STATE-001',*red_anti_ids]
links['VIS:RB-P40-V02']=[*links.get('VIS:RB-P40-V02',[]),'SEM-RED-ITEM-DECK-001','SEM-AMMO-TOKEN-LIFECYCLE-001','SEM-GRENADE-TOKEN-EFFECT-001',*red_item_rule_ids]
yellow_tools_ids=[row['semanticRuleId'] for row in yellow_item_sources['faces'] if row['effectKind']=='discard-malfunction-or-door']
yellow_phosphates_ids=[row['semanticRuleId'] for row in yellow_item_sources['faces'] if row['effectKind']=='reinforce-or-discard-fire']
yellow_oxygen_ids=[row['semanticRuleId'] for row in yellow_item_sources['faces'] if row['effectKind']=='gain-oxygen-or-token']
yellow_duct_ids=[row['semanticRuleId'] for row in yellow_item_sources['faces'] if row['effectKind']=='discard-malfunction-or-stack-heavy']
links['RULE:ACT-ITEM-001']=[*links.get('RULE:ACT-ITEM-001',[]),'SEM-YELLOW-ITEM-ONE-USE-001',*yellow_item_rule_ids]
links['RULE:ACT-TRADE-001']=[*links.get('RULE:ACT-TRADE-001',[]),'SEM-YELLOW-ITEM-IMMEDIATE-USE-001',*yellow_duct_ids]
links['RULE:ACT-TACTICAL-001']=[*links.get('RULE:ACT-TACTICAL-001',[]),'SEM-OXYGEN-TOKEN-EFFECT-001']
links['RULE:ITM-001']=[*links.get('RULE:ITM-001',[]),'SEM-YELLOW-ITEM-DECK-001']
links['RULE:ITM-002']=[*links.get('RULE:ITM-002',[]),'SEM-YELLOW-ITEM-VARIANT-BOUNDARIES-001',*yellow_duct_ids]
links['RULE:ITM-003']=[*links.get('RULE:ITM-003',[]),'SEM-YELLOW-ITEM-DECK-001','SEM-YELLOW-ITEM-VARIANT-BOUNDARIES-001']
links['RULE:ITM-004']=[*links.get('RULE:ITM-004',[]),'SEM-YELLOW-ITEM-DECK-001','SEM-YELLOW-ITEM-VARIANT-BOUNDARIES-001']
links['RULE:ITM-005']=[*links.get('RULE:ITM-005',[]),'SEM-OXYGEN-TOKEN-EFFECT-001',*yellow_oxygen_ids]
links['RULE:ITM-006']=[*links.get('RULE:ITM-006',[]),'SEM-YELLOW-ITEM-DECK-001']
links['RULE:ITM-008']=[*links.get('RULE:ITM-008',[]),'SEM-YELLOW-ITEM-VARIANT-BOUNDARIES-001',*yellow_item_rule_ids]
links['FAQ:FQ-P02-U10']=[*links.get('FAQ:FQ-P02-U10',[]),'SEM-REINFORCE-CORRIDOR-001',*yellow_phosphates_ids,*yellow_tools_ids]
links['FAQ:FQ-P02-U18']=[*links.get('FAQ:FQ-P02-U18',[]),'SEM-YELLOW-ITEM-VARIANT-BOUNDARIES-001']
links['FAQ:FQ-P03-U04']=[*links.get('FAQ:FQ-P03-U04',[]),'SEM-YELLOW-ITEM-IMMEDIATE-USE-001',*yellow_oxygen_ids]
links['FAQ:FQ-P03-U05']=[*yellow_duct_ids,'SEM-YELLOW-ITEM-ONE-USE-001','SEM-YELLOW-ITEM-VARIANT-BOUNDARIES-001']
links['FAQ:FQ-P03-U06']=[*links.get('FAQ:FQ-P03-U06',[]),'SEM-OXYGEN-TOKEN-EFFECT-001']
links['FAQ:FQ-P03-U07']=[*links.get('FAQ:FQ-P03-U07',[]),'SEM-DISCARD-MALFUNCTION-001',*yellow_duct_ids,*yellow_tools_ids,*yellow_oxygen_ids]
links['VIS:RB-P03-V01']=[*links.get('VIS:RB-P03-V01',[]),'SEM-YELLOW-ITEM-DECK-001','SEM-YELLOW-ITEM-VARIANT-BOUNDARIES-001']
links['VIS:RB-P05-V01']=[*links.get('VIS:RB-P05-V01',[]),'SEM-OXYGEN-TOKEN-EFFECT-001','SEM-DISCARD-MALFUNCTION-001']
links['VIS:RB-P09-V01']=[*links.get('VIS:RB-P09-V01',[]),'SEM-YELLOW-ITEM-DECK-001']
links['VIS:RB-P12-V02']=[*links.get('VIS:RB-P12-V02',[]),'SEM-USE-ITEM-001']
links['VIS:RB-P16-V02']=[*links.get('VIS:RB-P16-V02',[]),'SEM-OXYGEN-TOKEN-EFFECT-001',*yellow_oxygen_ids]
links['VIS:RB-P17-V01']=[*links.get('VIS:RB-P17-V01',[]),'SEM-GAIN-OXYGEN-001','SEM-OXYGEN-TOKEN-EFFECT-001',*yellow_oxygen_ids]
links['VIS:RB-P21-V01']=['SEM-REINFORCE-CORRIDOR-001',*yellow_phosphates_ids]
links['VIS:RB-P22-V01']=['SEM-DOOR-001',*yellow_tools_ids]
links['VIS:RB-P23-V02']=['SEM-DISCARD-MALFUNCTION-001',*yellow_tools_ids,*yellow_phosphates_ids]
links['VIS:RB-P28-V02']=[*links.get('VIS:RB-P28-V02',[]),'SEM-YELLOW-ITEM-DECK-001']
links['VIS:RB-P28-V03']=[*links.get('VIS:RB-P28-V03',[]),'SEM-YELLOW-ITEM-ONE-USE-001','SEM-YELLOW-ITEM-VARIANT-BOUNDARIES-001',*yellow_duct_ids]
links['VIS:RB-P29-V01']=[*links.get('VIS:RB-P29-V01',[]),'SEM-YELLOW-ITEM-VARIANT-BOUNDARIES-001']
links['VIS:RB-P29-V03']=[*links.get('VIS:RB-P29-V03',[]),'SEM-OXYGEN-TOKEN-EFFECT-001',*yellow_oxygen_ids]
links['VIS:RB-P37-V01']=[*links.get('VIS:RB-P37-V01',[]),'SEM-YELLOW-ITEM-VARIANT-BOUNDARIES-001']
links['VIS:RB-P40-V02']=[*links.get('VIS:RB-P40-V02',[]),'SEM-YELLOW-ITEM-DECK-001','SEM-OXYGEN-TOKEN-EFFECT-001','SEM-DISCARD-MALFUNCTION-001',*yellow_item_rule_ids]
action_by_kind={}
for face in action_sources['faces']:
 action_by_kind.setdefault(face['effectKind'],[]).append(face['semanticRuleId'])
links['RULE:RT-002']=['SEM-ACTION-CARD-REACTION-001',*action_by_kind.get('fire-at-will',[]),*action_by_kind.get('stay-calm-reaction',[])]
links['RULE:RT-003']=['SEM-ACTION-CARD-REACTION-001','SEM-REACTION-DUCK-001',*[rule_id for rule_id in action_reaction_rule_ids if rule_id!='SEM-REACTION-DUCK-001']]
links['RULE:RT-006']=['SEM-ACTION-CARD-PLAY-001','SEM-ACTION-CARD-PAYMENT-001']
links['RULE:RT-012']=[*links.get('RULE:RT-012',[]),'SEM-ACTION-DECK-SETUP-001','SEM-ACTION-CARD-DRAW-001']
links['RULE:RT-013']=['SEM-ACTION-CARD-COMMAND-001',*action_by_kind.get('chain-command',[]),*action_by_kind.get('chain-command-reaction',[]),*action_by_kind.get('fire-at-will',[]),*action_by_kind.get('officer-channel',[]),*action_by_kind.get('stay-calm-reaction',[])]
links['RULE:ACT-MOVE-002']=[*action_by_kind.get('scouting',[])]
links['RULE:ACT-MELEE-001']=[*action_by_kind.get('weak-spots',[]),*action_by_kind.get('hippocratic-oath',[])]
links['RULE:ACT-CARD-001']=[*links.get('RULE:ACT-CARD-001',[]),'SEM-ACTION-DECK-SETUP-001','SEM-ACTION-CARD-PLAY-001','SEM-ACTION-CARD-PAYMENT-001','SEM-ACTION-CARD-REACTION-001','SEM-ACTION-CARD-COMMAND-001','SEM-ACTION-CARD-VARIANT-BOUNDARIES-001','SEM-ACTION-CARD-DRAW-001',*action_rule_ids]
links['RULE:ACT-CARD-002']=['SEM-ACTION-CARD-PAYMENT-001','SEM-RT-007']
links['RULE:ACT-SECURE-001']=[*action_by_kind.get('secure',[]),*action_by_kind.get('secure-no-cost',[]),*action_by_kind.get('basic-secure',[])]
links['RULE:ACT-ROOM-001']=[*action_by_kind.get('computer-skills',[]),*action_by_kind.get('always-prepared',[])]
links['FAQ:FQ-P02-U10']=[*links.get('FAQ:FQ-P02-U10',[]),'SEM-ACTION-CARD-COMMAND-001']
links['FAQ:FQ-P02-U11']=[*links.get('FAQ:FQ-P02-U11',[]),'SEM-ACTION-CARD-PLAY-001','SEM-ACTION-CARD-DRAW-001']
links['FAQ:FQ-P02-U14']=[*action_by_kind.get('fire-at-will',[])]
links['FAQ:FQ-P02-U15']=[*action_by_kind.get('shoot-first',[])]
links['FAQ:FQ-P02-U16']=[*links.get('FAQ:FQ-P02-U16',[]),*action_by_kind.get('duck-and-cover',[]),*action_by_kind.get('tactical-retreat',[]),*action_by_kind.get('breakthrough',[])]
links['FAQ:FQ-P03-U01']=[*action_by_kind.get('forcing-fire',[]),*action_by_kind.get('tactical-retreat',[])]
links['FAQ:FQ-P03-U02']=[*action_by_kind.get('forcing-fire',[]),*action_by_kind.get('tactical-retreat',[]),*action_by_kind.get('breakthrough',[]),*action_by_kind.get('continuous-fire',[])]
links['FAQ:FQ-P03-U07']=[*links.get('FAQ:FQ-P03-U07',[]),*action_by_kind.get('field-surgery',[]),*action_by_kind.get('first-aid',[]),*action_by_kind.get('combat-drugs',[])]
links['VIS:RB-P03-V01']=[*links.get('VIS:RB-P03-V01',[]),'SEM-ACTION-DECK-SETUP-001','SEM-ACTION-CARD-VARIANT-BOUNDARIES-001',*action_by_kind.get('weak-spots',[])]
links['VIS:RB-P11-V01']=['SEM-ACTION-DECK-SETUP-001','SEM-ACTION-CARD-PLAY-001','SEM-ACTION-CARD-PAYMENT-001']
links['VIS:RB-P12-V02']=[*links.get('VIS:RB-P12-V02',[]),'SEM-ACTION-CARD-PLAY-001','SEM-ACTION-CARD-PAYMENT-001']
links['VIS:RB-P13-V01']=['SEM-ACTION-CARD-PLAY-001','SEM-ACTION-CARD-REACTION-001','SEM-REACTION-DUCK-001',*action_by_kind.get('duck-and-cover',[]),*action_by_kind.get('sprint',[])]
links['VIS:RB-P28-V02']=[*links.get('VIS:RB-P28-V02',[]),'SEM-ACT-SEARCH-001',*action_by_kind.get('search',[])]
links['VIS:RB-P36-V01']=['SEM-ACTION-DECK-SETUP-001','SEM-ACTION-CARD-PAYMENT-001']
links['VIS:RB-P40-V02']=[*links.get('VIS:RB-P40-V02',[]),'SEM-ACTION-CARD-VARIANT-BOUNDARIES-001',*action_rule_ids]
for unit_id,rule_ids in links.items():
 links[unit_id]=list(dict.fromkeys(rule_ids))
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
