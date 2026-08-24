#!/usr/bin/env python3
from __future__ import annotations
import collections,hashlib,json,subprocess,tempfile
from pathlib import Path
REPO=Path(__file__).resolve().parents[1]; SRC=REPO/'docs/rules/source-extraction'; RECORD=SRC/'secondary-evidence-index.json'; INVENTORY=SRC/'secondary-source-inventory.json'; CORPUS=REPO/'assets/tts-mod/extract/card-text-corpus.json'
def load(p): return json.loads(p.read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 d=load(RECORD); inv=load(INVENTORY); failures=[]; licensed=d.get('licensedDigital') or {}; snap=REPO/licensed.get('immutableSnapshotPath','')
 if not snap.is_file() or sha(snap)!=licensed.get('sha256') or snap.stat().st_size!=licensed.get('bytes'): failures.append({'check':'immutable BGA snapshot'})
 if licensed.get('collectedCopyCount')!=4 or licensed.get('distinctCollectedHashes')!=[licensed.get('sha256')] or licensed.get('allCollectedCopiesByteIdentical') is not True: failures.append({'check':'BGA copy closure'})
 # Historical runtime copies are optional after consolidation; if present, they must match.
 recorded=(inv.get('licensedDigitalSecondary') or {}).get('copies') or []
 for row in recorded:
  p=Path(row['path'])
  if p.exists() and (sha(p)!=row['sha256'] or p.stat().st_size!=row['bytes']): failures.append({'check':'historical BGA copy drift','path':row['path']})
 # Re-index the immutable JS and compare the complete mechanical projection.
 with tempfile.TemporaryDirectory(prefix='validate-bga-index-') as tmp:
  out=Path(tmp)/'index.json'; run=subprocess.run(['node',str(REPO/'scripts/index_bga_static.js'),str(snap),str(out)],check=False,capture_output=True,text=True)
  if run.returncode!=0: failures.append({'check':'BGA indexer execution','stderr':run.stderr}); regenerated={}
  else: regenerated=load(out)
 regenerated['source']='docs/rules/source-extraction/secondary/bga-staticData-260622-1220.js'; regenerated['sourceSha256']=sha(snap); regenerated['build']='260622-1220'
 if regenerated!=licensed.get('structuredIndex'): failures.append({'check':'BGA structured index reproducibility'})
 tts=d.get('ttsStructuredEvidence') or {}; expected_paths={
  'objects':'assets/tts-mod/extract/v2/objects.json','classification':'assets/tts-mod/extract/v2/classification.json','luaRoles':'assets/tts-mod/extract/v2/lua_roles.json','gmnotesTaxonomy':'assets/tts-mod/extract/v2/gmnotes_taxonomy.json','cardProvenanceInventory':'assets/tts-mod/extract/card-provenance-inventory.json','selectedEvidenceRegistry':'assets/tts-mod/extract/selected-card-text-evidence.json'}
 for key,rel in expected_paths.items():
  row=tts.get(key) or {}; p=REPO/rel
  if row.get('path')!=rel or not p.is_file() or sha(p)!=row.get('sha256'): failures.append({'check':'TTS source tuple','key':key})
 objects=load(REPO/expected_paths['objects']); classification=load(REPO/expected_paths['classification']); roles=load(REPO/expected_paths['luaRoles']); tags=load(REPO/expected_paths['gmnotesTaxonomy']); provenance=load(REPO/expected_paths['cardProvenanceInventory']); selected=load(REPO/expected_paths['selectedEvidenceRegistry']); corpus=load(CORPUS)
 if len(roles)!=159 or len({x['role'] for x in roles})!=117 or len({x['guid'] for x in roles})!=150: failures.append({'check':'Lua role closure'})
 if len(tags)!=172 or sum(x['count'] for x in tags)!=1267: failures.append({'check':'GMNotes closure'})
 if len(selected['entries'])!=384 or sum(len(x['runs']) for x in selected['entries'])!=384: failures.append({'check':'selected evidence closure'})
 verdicts=dict(sorted(collections.Counter(x.get('verdict') for x in classification).items(),key=lambda x:str(x[0])))
 if verdicts!=(tts.get('classification') or {}).get('verdictCounts'): failures.append({'check':'classification verdict counts'})
 bga_paths=[]
 for row in corpus['records']:
  text=json.dumps({'uncertainties':row.get('uncertainties'),'blocker':row.get('canonicalPromotionBlocker'),'selected':row.get('selectedExtraction')},ensure_ascii=False).lower()
  if 'bga' in text and ('conflict' in text or 'secondary' in text): bga_paths.append(row['sourcePath'])
 conflict=d.get('conflictInventory') or {}
 if bga_paths!=conflict.get('sourcePaths') or len(bga_paths)!=conflict.get('corpusRecordsExplicitlyMentioningBgaConflictOrSecondaryBoundary'): failures.append({'check':'BGA conflict boundary projection'})
 table_counts={x['name']:x['count'] for x in (licensed.get('structuredIndex') or {}).get('tables',[])}
 if table_counts!={'ACTION_CARDS_DATA':60,'EVENT_CARDS_DATA':20,'ROOMS_DATA':25,'CORRIDORS_DATA':44,'EXPLORATION_CARDS_DATA':12,'ITEMS_DATA':57,'MISSIONS_OBJECTIVES_DATA':38,'ROBOT_CARDS_DATA':6,'INTRUDER_ATTACKS_DATA':15,'QUEEN_CARDS_DATA':12,'SERIOUS_WOUNDS_DATA':9}: failures.append({'check':'BGA table counts','actual':table_counts})
 counts={'bgaCopiesVerified':4,'bgaDistinctHashes':1,'bgaTopLevelTables':11,'bgaStructuredRecords':298,'ttsStructuredFiles':6,'ttsLuaRoleRecords':159,'ttsGmnotesTagRows':172,'ttsGmnotesTaggedOccurrences':1267,'selectedEvidenceEntries':384,'selectedEvidenceRuns':384,'corpusRecordsWithBgaConflictBoundary':156}
 if d.get('counts')!=counts: failures.append({'check':'secondary counts','expected':counts,'actual':d.get('counts')})
 inv_lic=inv.get('licensedDigitalSecondary') or {}; inv_snap=inv_lic.get('immutableSnapshot') or {}; closure=inv.get('closureIndex') or {}
 if inv_snap.get('path')!=licensed.get('immutableSnapshotPath') or inv_snap.get('sha256')!=licensed.get('sha256') or inv_lic.get('status','').startswith('complete:') is False: failures.append({'check':'secondary inventory BGA closure'})
 if closure.get('path')!='docs/rules/source-extraction/secondary-evidence-index.json' or closure.get('sha256')!=sha(RECORD) or closure.get('status')!='complete': failures.append({'check':'secondary inventory closure index'})
 report={'schemaVersion':1,'passed':not failures,'checks':counts,'failureCount':len(failures),'failures':failures}; print(json.dumps(report,indent=2,ensure_ascii=False)); return 0 if not failures else 1
if __name__=='__main__': raise SystemExit(main())
