#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,math,re
from pathlib import Path
import numpy as np
from PIL import Image
REPO=Path(__file__).resolve().parents[1]; RECORD=REPO/'docs/rules/source-extraction/player-help-source-extraction.json'; CORPUS=REPO/'assets/tts-mod/extract/card-text-corpus.json'
def load(p): return json.loads(p.read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
 d=load(RECORD); corpus=load(CORPUS); rows={r['sourcePath']:r for r in corpus['records']}; failures=[]; fronts=d.get('fronts') or []
 expected_counts={'frontOccurrences':10,'distinctPlayerNumbers':10,'sharedBackOccurrences':1,'instructionTextVariants':1,'rasterTemplateGroups':2,'functionalIconOccurrences':0,'materialUnreadableSpans':0}
 if d.get('counts')!=expected_counts: failures.append({'check':'counts','expected':expected_counts,'actual':d.get('counts')})
 if [f.get('playerNumber') for f in fronts]!=list(range(1,11)) or [f.get('sourceUnitId') for f in fronts]!=[f'PH-FRONT-{n:02d}' for n in range(1,11)]: failures.append({'check':'front closure'})
 shared=d.get('sharedInstructionText'); seen=set(); back=d.get('sharedBack') or {}; back_path=REPO/back.get('sourcePath','')
 if not back_path.is_file() or sha(back_path)!=back.get('sourceSha256') or back.get('classification')!='functional pass-state face' or back.get('visibleText')!='PASS': failures.append({'check':'shared PASS side'})
 for f in fronts:
  n=f['playerNumber']; path=REPO/f['sourcePath']; row=rows.get(f['sourcePath'])
  if not path.is_file() or sha(path)!=f['sourceSha256']: failures.append({'check':'front source tuple','player':n}); continue
  with Image.open(path) as im: dims=list(im.size); im.verify()
  if dims!=f['dimensions'] or f.get('sourceRole')!='FaceURL player-number Help reference face': failures.append({'check':'front metadata','player':n})
  pd=f.get('printedData') or {}; seen.add(pd.get('instructionText'))
  if pd.get('playerNumber')!=str(n) or pd.get('instructionText')!=shared or pd.get('functionalIconOccurrences')!=[]: failures.append({'check':'front printed data','player':n})
  refs=f.get('objectRefs') or []
  if not refs or any(r.get('urlRole')!='FaceURL' or ['Bag','d8a0fb','playerHelpCards'] not in (r.get('parent') or []) for r in refs): failures.append({'check':'TTS role','player':n})
  if n<=5 and len(refs)!=5: failures.append({'check':'sheet reference set','player':n})
  if n>=6 and len(refs)!=1: failures.append({'check':'individual reference','player':n})
  pair=f.get('pairedBack') or {}
  if pair.get('sourcePath')!=back.get('sourcePath') or pair.get('sourceSha256')!=back.get('sourceSha256') or pair.get('urlRole')!='BackURL': failures.append({'check':'paired back','player':n})
  if not row or row['sourceSha256']!=f['sourceSha256']: failures.append({'check':'corpus tuple','player':n})
  if n==6:
   if (f.get('corpusProjection') or {}).get('canonicalPath')!='cards/reference/help-card-player-6.png' or row['extractionState']!='verified-canonical': failures.append({'check':'canonical player 6'})
  elif row['extractionState']!='complete-non-rules-or-reference': failures.append({'check':'noncanonical source state','player':n})
 if seen!={shared}: failures.append({'check':'instruction text equivalence'})
 # Recompute stored template comparison metrics exactly.
 groups=d.get('rasterTemplateGroups') or []
 if [g.get('players') for g in groups]!=[[1,2,3,4,5],[6,7,8,9,10]]: failures.append({'check':'template groups'})
 by_num={f['playerNumber']:f for f in fronts}
 for group in groups:
  comp=group['comparison']; size=tuple(comp['normalizedDimensions']); x1,y1,x2,y2=comp['comparisonRegion']; numbers=group['players']; ims={n:Image.open(REPO/by_num[n]['sourcePath']).convert('RGB').resize(size,Image.Resampling.LANCZOS) for n in numbers}; base=np.asarray(ims[comp['baselinePlayerNumber']],dtype=np.int16)[y1:y2,x1:x2]
  stored={m['playerNumber']:m for m in comp['metrics']}
  for n,im in ims.items():
   a=np.asarray(im,dtype=np.int16)[y1:y2,x1:x2]; diff=np.abs(a-base); actual=(float(diff.mean()),float(np.sqrt((diff.astype(np.float64)**2).mean())),float(np.all(a==base,axis=2).mean())); expected=(stored[n]['meanAbsoluteError'],stored[n]['rootMeanSquareError'],stored[n]['exactPixelRatio'])
   if any(not math.isclose(x,y,rel_tol=1e-12,abs_tol=1e-12) for x,y in zip(actual,expected)): failures.append({'check':'template metric','group':group['groupId'],'player':n})
  for im in ims.values(): im.close()
 if group:=next((g for g in groups if g.get('groupId')=='PH-TEMPLATE-SHEET-1-5'),None):
  if max(m['meanAbsoluteError'] for m in group['comparison']['metrics'])>0.52: failures.append({'check':'sheet template similarity'})
 if group:=next((g for g in groups if g.get('groupId')=='PH-TEMPLATE-INDIVIDUAL-6-10'),None):
  if min(m['exactPixelRatio'] for m in group['comparison']['metrics'])<0.994: failures.append({'check':'individual template similarity'})
 conflicts=d.get('sourceConflicts') or []
 if {c.get('conflictId') for c in conflicts}!={'player-help-count-tts-vs-official-inventory','player-help-phase-sequence-vs-current-rulebook'}: failures.append({'check':'source conflicts'})
 report={'schemaVersion':1,'passed':not failures,'checks':expected_counts,'failureCount':len(failures),'failures':failures}; print(json.dumps(report,indent=2,ensure_ascii=False)); return 0 if not failures else 1
if __name__=='__main__': raise SystemExit(main())
