#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path
from PIL import Image

REPO=Path(__file__).resolve().parents[1]
SRC=REPO/'docs/rules/source-extraction'
CORPUS=REPO/'assets/tts-mod/extract/card-text-corpus.json'
QUEUE=REPO/'assets/tts-mod/extract/low-confidence-review.json'

def load(p): return json.loads(p.read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
 failures=[]
 review=load(SRC/'card-gap-adjudications.json'); inv=load(SRC/'card-gap-inventory.json')
 corpus=load(CORPUS); queue=load(QUEUE)
 rows={r['sourcePath']:r for r in corpus['records']}; qrows={r['sourcePath']:r for r in queue['entries']}
 entries=review.get('entries') or []; ids=[r.get('assetId') for r in entries]
 if ids != [f'G{i:02d}' for i in range(1,14)]: failures.append({'check':'review asset IDs','actual':ids})
 expected_counts={'records':13,'rulesTextComplete':9,'explicitOperativeSourceBlockers':1,'classifiedNonRules':3,'recoveredOperativeCorrections':1,'materialUnreadableVisibleRulesSpans':1}
 if review.get('counts')!=expected_counts: failures.append({'check':'review counts','expected':expected_counts,'actual':review.get('counts')})
 for e in entries:
  path=REPO/e['sourcePath']; row=rows.get(e['sourcePath']); qrow=qrows.get(e['sourcePath'])
  if not path.is_file() or sha(path)!=e['sourceSha256']: failures.append({'check':'source tuple','assetId':e['assetId']}); continue
  with Image.open(path) as im: dimensions=list(im.size)
  if dimensions!=e['dimensions']: failures.append({'check':'source dimensions','assetId':e['assetId']})
  if not row or row['sourceSha256']!=e['sourceSha256'] or row['extractionState']!=e['expectedExtractionState']:
   failures.append({'check':'corpus projection','assetId':e['assetId']})
  if not qrow or (qrow.get('sourceExtractionReview') or {}).get('evidencePath')!='docs/rules/source-extraction/card-gap-adjudications.json':
   failures.append({'check':'queue review evidence','assetId':e['assetId']})
  if row and (row.get('evidence') or {}).get('sourceExtractionReview')!=(qrow or {}).get('sourceExtractionReview'):
   failures.append({'check':'corpus review evidence','assetId':e['assetId']})
 review_by={e['assetId']:e for e in entries}
 # Nine complete rules reads contain no operative unreadable marker in projected text.
 for aid in ('G01','G03','G04','G05','G07','G08','G09','G10','G11'):
  row=rows[review_by[aid]['sourcePath']]
  if row['extractionState']!='draft-full' or '[illegible]' in json.dumps(row['printedData'],ensure_ascii=False) or '[clipped]' in json.dumps(row['printedData'],ensure_ascii=False):
   failures.append({'check':'rules-complete projection','assetId':aid})
 # G02 remains the exact smallest source-local blocker.
 g02=rows[review_by['G02']['sourcePath']]
 if g02['extractionState']!='draft-partial' or 'Systems must be [illegible]' not in g02['printedData']['body']:
  failures.append({'check':'G02 source blocker'})
 q02=qrows[review_by['G02']['sourcePath']]
 if (q02.get('sourcePixelBlocker') or {}).get('handling','').find('Retain [illegible]')<0:
  failures.append({'check':'G02 blocker evidence'})
 # G11 is punctuation-only recovery; immutable selected overlay remains historical.
 g11=rows[review_by['G11']['sourcePath']]
 if '[shootDie2]: treat this result' not in g11['printedData']['body'] or '[shootDie2][illegible] treat' not in g11['selectedExtraction']['visibleText']['body']:
  failures.append({'check':'G11 colon correction'})
 source=Image.open(REPO/review_by['G11']['sourcePath'])
 import tempfile
 with tempfile.TemporaryDirectory(prefix='validate-g11-') as tmp:
  out=Path(tmp)/'upright.png'; source.transpose(Image.Transpose.ROTATE_90).save(out,'PNG',optimize=True)
  if sha(out)!=(review.get('focusedDerivatives') or {}).get('G11',{}).get('uprightSha256'):
   failures.append({'check':'G11 upright derivative'})
 source.close()
 # Three non-rules sources are closed without invented printed text.
 expected_nonrules={'G06':'generic-card-back','G12':'near-uniform-black-placeholder','G13':'near-uniform-black-placeholder'}
 for aid,classification in expected_nonrules.items():
  row=rows[review_by[aid]['sourcePath']]; cls=(row.get('evidence') or {}).get('sourceComponentClassification') or {}
  if row['extractionState']!='non-rules-or-reference' or row['rulesTextPresent'] or cls.get('classification')!=classification or cls.get('rulesBearing') is not False:
   failures.append({'check':'non-rules classification','assetId':aid})
 # Exact near-black pixel inventories remain true.
 for aid,expected in {'G12':(10,509920),'G13':(2,905453)}.items():
  with Image.open(REPO/review_by[aid]['sourcePath']).convert('RGBA') as im:
   colors=im.getcolors(maxcolors=im.width*im.height+1) or []
   exact_black=next((count for count,color in colors if color==(0,0,0,255)),0)
  if len(colors)!=expected[0] or exact_black!=expected[1]: failures.append({'check':'black placeholder pixels','assetId':aid,'colors':len(colors),'exactBlack':exact_black})
 # Closure inventory must project this exact review and current corpus.
 inv_rows=inv.get('records') or []; inv_by={r['assetId']:r for r in inv_rows}
 expected_inv={'reviewedRecords':13,'rulesTextComplete':9,'explicitOperativeSourceBlockers':1,'classifiedNonRules':3,'remainingDraftPartial':1,'remainingNoTranscription':0,'recoveredOperativeCorrections':1}
 if inv.get('counts')!=expected_inv or set(inv_by)!=set(review_by) or inv.get('sourceCorpusSha256')!=sha(CORPUS):
  failures.append({'check':'closure inventory','expected':expected_inv,'actual':inv.get('counts')})
 for aid,e in review_by.items():
  r=inv_by.get(aid)
  if not r or r['sourcePath']!=e['sourcePath'] or r['resultingExtractionState']!=e['expectedExtractionState'] or r['disposition']!=e['disposition']:
   failures.append({'check':'closure inventory row','assetId':aid})
 result={'schemaVersion':1,'passed':not failures,'checks':{
  'reviewedRecords':len(entries),'rulesTextComplete':review['counts']['rulesTextComplete'],
  'explicitOperativeSourceBlockers':review['counts']['explicitOperativeSourceBlockers'],
  'classifiedNonRules':review['counts']['classifiedNonRules'],'recoveredOperativeCorrections':review['counts']['recoveredOperativeCorrections'],
  'remainingDraftPartial':inv['counts']['remainingDraftPartial'],'remainingNoTranscription':inv['counts']['remainingNoTranscription'],
 },'failureCount':len(failures),'failures':failures}
 print(json.dumps(result,indent=2,ensure_ascii=False)); return 0 if not failures else 1

if __name__=='__main__': raise SystemExit(main())
