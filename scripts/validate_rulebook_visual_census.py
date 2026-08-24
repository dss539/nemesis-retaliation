#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,re,subprocess,tempfile
from pathlib import Path
from PIL import Image

REPO=Path(__file__).resolve().parents[1]
RECORD=REPO/'docs/rules/source-extraction/rulebook-visual-obligations.json'

def load(p): return json.loads(p.read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
 d=load(RECORD); failures=[]; source=d.get('source') or {}; pdf=REPO/source.get('path','')
 if not pdf.is_file() or sha(pdf)!=source.get('sha256'):
  failures.append({'check':'source tuple'})
 if source.get('pages')!=40 or source.get('renderDpi')!=160 or source.get('renderDimensions')!=[1361,1834]:
  failures.append({'check':'source render metadata'})
 checked=(source.get('checkedTextExtraction') or {}); checked_path=REPO/checked.get('path','')
 if not checked_path.is_file() or sha(checked_path)!=checked.get('sha256') or checked.get('pageBoundariesPreserved') is not False:
  failures.append({'check':'checked text extraction tuple'})
 pages=d.get('pages') or []
 if [p.get('pdfPageIndex') for p in pages]!=list(range(1,41)):
  failures.append({'check':'page closure'})
 ids=[]
 for page in pages:
  idx=page['pdfPageIndex']; visual=page.get('visualUnits') or []
  for unit in visual:
   oid=unit.get('occurrenceId'); ids.append(oid)
   if not re.fullmatch(rf'RB-P{idx:02d}-V\d{{2}}',str(oid)):
    failures.append({'check':'occurrence ID','page':idx,'id':oid})
   box=unit.get('bbox') or []
   if len(box)!=4 or not (0<=box[0]<box[2]<=1361 and 0<=box[1]<box[3]<=1834):
    failures.append({'check':'bbox','id':oid,'bbox':box})
   if unit.get('obligationClass') not in {'normative-visual-obligation','worked-example-visual','reference-visual-unit'}:
    failures.append({'check':'obligation class','id':oid})
   comp=unit.get('textLayerComparison') or {}
   if comp.get('status')!='partial-visual-structure-lost' or not unit.get('spatialRelationshipLostInPlainText'):
    failures.append({'check':'text-layer classification','id':oid})
 if len(ids)!=len(set(ids)):
  failures.append({'check':'occurrence uniqueness'})
 # Regenerate page renders and page-local layout text deterministically.
 with tempfile.TemporaryDirectory(prefix='validate-rulebook-visual-') as tmp:
  prefix=Path(tmp)/'page'
  subprocess.run(['pdftoppm','-f','1','-l','40','-png','-r','160',str(pdf),str(prefix)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  layout=Path(tmp)/'layout.txt'; subprocess.run(['pdftotext','-layout',str(pdf),str(layout)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  texts=layout.read_text(errors='replace').split('\f')
  if texts and not texts[-1].strip(): texts=texts[:-1]
  if len(texts)!=40: failures.append({'check':'fresh text page count','actual':len(texts)})
  if sha(layout)!=(source.get('freshComparisonExtraction') or {}).get('wholeFileSha256'):
   failures.append({'check':'fresh text whole-file hash'})
  for page in pages:
   idx=page['pdfPageIndex']; evidence=page.get('renderEvidence') or {}; image=Path(tmp)/f'page-{idx:02d}.png'
   if not image.exists():
    alt=Path(tmp)/f'page-{idx}.png'
    if alt.exists(): alt.rename(image)
   with Image.open(image) as im:
    size=list(im.size); im.verify()
   text_bytes=texts[idx-1].encode()
   if size!=evidence.get('dimensions') or sha(image)!=evidence.get('imageSha256'):
    failures.append({'check':'page render evidence','page':idx})
   if hashlib.sha256(text_bytes).hexdigest()!=evidence.get('freshPageTextSha256') or len(texts[idx-1])!=evidence.get('freshPageTextCharacters'):
    failures.append({'check':'page text evidence','page':idx})
 classes=('normative-visual-obligation','worked-example-visual','reference-visual-unit')
 coverage=('partial-visual-structure-lost','absent-from-text-layer','fully-retained')
 recomputed={
  'pages':len(pages),
  'pagesWithVisualObligations':sum(p.get('pageCensusStatus')=='visual-obligations-extracted' for p in pages),
  'pagesWithoutNormativeVisualUnits':sum(p.get('pageCensusStatus')=='no-normative-visual-units' for p in pages),
  'visualUnits':sum(len(p.get('visualUnits') or []) for p in pages),
  'byObligationClass':{c:sum(u.get('obligationClass')==c for p in pages for u in p.get('visualUnits') or []) for c in classes},
  'byTextLayerCoverage':{c:sum((u.get('textLayerComparison') or {}).get('status')==c for p in pages for u in p.get('visualUnits') or []) for c in coverage},
  'materialUnreadableSpans':sum(len(p.get('materialUnreadableSpans') or []) for p in pages),
  'printedPageNumbersVisible':sum(isinstance(p.get('visiblePrintedPageNumber'),int) for p in pages),
 }
 expected={
  'pages':40,'pagesWithVisualObligations':36,'pagesWithoutNormativeVisualUnits':4,'visualUnits':80,
  'byObligationClass':{'normative-visual-obligation':72,'worked-example-visual':5,'reference-visual-unit':3},
  'byTextLayerCoverage':{'partial-visual-structure-lost':80,'absent-from-text-layer':0,'fully-retained':0},
  'materialUnreadableSpans':0,'printedPageNumbersVisible':35,
 }
 if recomputed!=expected or d.get('counts')!=expected:
  failures.append({'check':'counts','expected':expected,'recomputed':recomputed,'stored':d.get('counts')})
 required={'RB-P03-V01','RB-P08-V03','RB-P13-V01','RB-P19-V01','RB-P20-V01','RB-P24-V01','RB-P36-V02','RB-P40-V02'}
 if not required.issubset(ids): failures.append({'check':'required representative obligations','missing':sorted(required-set(ids))})
 glossary=next((u for p in pages for u in p.get('visualUnits') or [] if u.get('occurrenceId')=='RB-P40-V02'),None)
 if not glossary or glossary.get('totalOccurrenceCount')!=49 or sum(g.get('occurrenceCount',0) for g in glossary.get('groups',[]))!=49:
  failures.append({'check':'icon glossary closure'})
 report={'schemaVersion':1,'passed':not failures,'checks':expected,'failureCount':len(failures),'failures':failures}
 print(json.dumps(report,indent=2,ensure_ascii=False)); return 0 if not failures else 1

if __name__=='__main__': raise SystemExit(main())
