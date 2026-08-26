from __future__ import annotations

INLINE_MAPPING={
 'R01-I04':'icon.fire',
 'R03-I04':'icon.characterHealth',
 'R05-I04':'icon.ammoToken','R05-I05':'icon.grenadeToken',
 'R07-I04':'icon.secure','R07-I05':'icon.robot','R07-I06':'icon.robot',
 'R08-I05':'icon.redItem','R08-I06':'icon.malfunction','R08-I07':'icon.ammoToken',
 'R09-I05':'icon.intruder',
 'R10-I04':'icon.noise',
 'R11-I03':'icon.ammoToken',
 'R13-I04':'icon.actionCard','R13-I05':'icon.oxygen','R13-I06':'icon.oxygen',
 'R14-I05':'icon.lander',
 'R15-I04':'icon.lifeSupportActive','R15-I05':'icon.lifeSupportInactive','R15-I06':'icon.fire',
 'R16-I04':'icon.actionCard',
 'R17-I05':'icon.robot',
 'R18-I01':'icon.hibernatoriumActive','R18-I02':'icon.hibernatoriumActive',
 'R19-I03':'icon.lifeSupportActive','R19-I04':'icon.lifeSupportInactive',
 'R20-I04':'icon.computer','R20-I05':'icon.malfunction',
 'R22-I03':'icon.lifeSupportActive','R22-I04':'icon.lifeSupportInactive','R22-I05':'icon.hibernatoriumInactive','R22-I06':'icon.hibernatoriumActive',
 'R23-I03':'icon.lifeSupportActive','R23-I04':'icon.lifeSupportInactive','R23-I05':'icon.autodestruction','R23-I06':'icon.lifeSupportInactive','R23-I07':'icon.autodestruction','R23-I08':'icon.lifeSupportInactive','R23-I09':'icon.autodestruction',
}
EXPLICIT_STATIC_MAPPING={
 'R02-I03':'sem.state.room.always-secured',
 'R04-I04':'sem.state.room.secure-prohibited','R12-I04':'sem.state.room.secure-prohibited','R25-I01':'sem.state.room.secure-prohibited',
 'R25-I02':'sem.state.room.malfunction-prohibited',
 'R14-I01':'icon.ammoSlot','R14-I02':'icon.grenadeSlot','R14-I03':'icon.medpackSlot','R14-I04':'icon.oxygenSlot',
}
LITERAL_MAPPING={
 'bright green chamfered square containing a centered white plus sign':'icon.greenItem',
 'gold-yellow chamfered square containing a diagonal white wrench silhouette':'icon.yellowItem',
 'red chamfered square containing three upright white cartridge-like shapes':'icon.redItem',
 'small cyan-blue glowing rectangular monitor-like outline with a pale inner screen and short base':'icon.computer',
}


def build_room_icon_denotations(room_source, vocabulary):
 term_ids={entry['termId'] for entry in vocabulary['entries']}
 occurrences={occ['occurrenceId']:occ for entry in room_source['entries'] for occ in entry['functionalIconOccurrences']}
 mapping=dict(INLINE_MAPPING)
 mapping.update(EXPLICIT_STATIC_MAPPING)
 for occurrence_id,occurrence in occurrences.items():
  if occurrence_id not in mapping and occurrence['literalAppearance'] in LITERAL_MAPPING:
   mapping[occurrence_id]=LITERAL_MAPPING[occurrence['literalAppearance']]
 assert set(mapping)==set(occurrences),(sorted(set(occurrences)-set(mapping)),sorted(set(mapping)-set(occurrences)))
 assert all(reference in term_ids or reference.startswith('sem.state.room.') for reference in mapping.values())

 reference_locations={}
 for entry in room_source['entries']:
  for field,value in [('printedEffect',entry['printedEffect']),*[(f'associatedNotes[{index}]',value) for index,value in enumerate(entry['associatedNotes'])]]:
   for occurrence_id in occurrences:
    if f'[{occurrence_id}]' in value:
     reference_locations.setdefault(occurrence_id,[]).append({'room':entry['printedNumber'],'field':field})

 rows=[]
 for occurrence_id in sorted(occurrences):
  occurrence=occurrences[occurrence_id]
  reference=mapping[occurrence_id]
  rows.append({'occurrenceId':occurrence_id,'semanticReferenceId':reference,'referenceKind':'semantic-node' if reference.startswith('sem.') else 'controlled-term','literalAppearance':occurrence['literalAppearance'],'sourceLocation':occurrence['location'],'referenceLocations':reference_locations.get(occurrence_id,[]),'mappingScope':'official Room Help source occurrence only','mappingStatus':'accepted-source-scoped-semantic-denotation','basis':'literal morphology, repeated source family, operative/room context, and accepted icon/state vocabulary; extraction record remains unchanged'})
 return {'schemaVersion':1,'recordType':'room-help-semantic-icon-denotations','policy':'Semantic-layer mapping for all 112 source-local functional Room Help occurrences. Source extraction remains literal and unchanged; state/prohibition graphics use semantic nodes rather than pretending they are physical tokens.','counts':{'functionalOccurrences':len(rows),'controlledTermDenotations':sum(row['referenceKind']=='controlled-term' for row in rows),'semanticNodeDenotations':sum(row['referenceKind']=='semantic-node' for row in rows),'uniqueSemanticReferences':len(set(mapping.values()))},'denotations':rows}
