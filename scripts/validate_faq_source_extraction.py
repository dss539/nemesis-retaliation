#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,re,subprocess,tempfile
from collections import Counter
from pathlib import Path
from PIL import Image

REPO=Path(__file__).resolve().parents[1]; RECORD=REPO/'docs/rules/source-extraction/faq-v1.2-source-extraction.json'
def load(p): return json.loads(p.read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
 d=load(RECORD); failures=[]; source=d.get('source') or {}; pdf=REPO/source.get('path',''); checked=source.get('checkedTextExtraction') or {}; checked_path=REPO/checked.get('path','')
 if not pdf.is_file() or sha(pdf)!=source.get('sha256') or source.get('pages')!=4: failures.append({'check':'source tuple'})
 if source.get('renderDpi')!=200 or source.get('renderDimensions')!=[1701,2386] or source.get('printedVersion')!='V1.2' or source.get('printedDate')!='8.06.2026': failures.append({'check':'source metadata'})
 if not checked_path.is_file() or sha(checked_path)!=checked.get('sha256') or checked.get('pageBoundariesPreserved') is not False: failures.append({'check':'checked text tuple'})
 pages=d.get('pages') or []
 if [p.get('pdfPageIndex') for p in pages]!=[1,2,3,4] or [len(p.get('units') or []) for p in pages]!=[0,21,25,13]: failures.append({'check':'page/unit closure'})
 ids=[]; icon_ids=[]
 for page in pages:
  for u in page.get('units') or []:
   ids.append(u.get('sourceUnitId')); bbox=u.get('bbox') or []
   if not re.fullmatch(rf'FQ-P{page["pdfPageIndex"]:02d}-U\d{{2}}',str(u.get('sourceUnitId'))): failures.append({'check':'unit ID','id':u.get('sourceUnitId')})
   if len(bbox)!=4 or not (0<=bbox[0]<bbox[2]<=1701 and 0<=bbox[1]<bbox[3]<=2386): failures.append({'check':'bbox','id':u.get('sourceUnitId')})
   if not u.get('section') or not u.get('printedText') or u.get('applicability') is None: failures.append({'check':'required unit data','id':u.get('sourceUnitId')})
   for occ in u.get('visualOccurrences') or []: icon_ids.append(occ.get('occurrenceId'))
   refs=set(re.findall(r'\[(FQ-P\d{2}-U\d{2}-I\d{2})\]',u.get('printedText','')))
   defined={x.get('occurrenceId') for x in u.get('visualOccurrences') or []}
   if refs-defined: failures.append({'check':'undefined visual placeholder','id':u.get('sourceUnitId'),'refs':sorted(refs-defined)})
   if (u.get('textLayerComparison') or {}).get('status') not in {'partial-column-scope-structure-lost','partial-inline-glyphs-and-column-scope-lost'}: failures.append({'check':'text comparison status','id':u.get('sourceUnitId')})
 if len(ids)!=len(set(ids)) or len(icon_ids)!=len(set(icon_ids)): failures.append({'check':'ID uniqueness'})
 # Regenerate all page renders and layout text.
 with tempfile.TemporaryDirectory(prefix='validate-faq-') as tmp:
  prefix=Path(tmp)/'page'; subprocess.run(['pdftoppm','-f','1','-l','4','-png','-r','200',str(pdf),str(prefix)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  layout=Path(tmp)/'layout.txt'; subprocess.run(['pdftotext','-layout',str(pdf),str(layout)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  texts=layout.read_text(errors='replace').split('\f')
  if texts and not texts[-1].strip(): texts=texts[:-1]
  if len(texts)!=4 or sha(layout)!=(source.get('freshComparisonExtraction') or {}).get('wholeFileSha256'): failures.append({'check':'fresh text extraction'})
  for page in pages:
   idx=page['pdfPageIndex']; evidence=page.get('renderEvidence') or {}; image=Path(tmp)/f'page-{idx}.png'
   with Image.open(image) as im: size=list(im.size); im.verify()
   tbytes=texts[idx-1].encode()
   if size!=evidence.get('dimensions') or sha(image)!=evidence.get('imageSha256'): failures.append({'check':'page render','page':idx})
   if hashlib.sha256(tbytes).hexdigest()!=evidence.get('freshPageTextSha256') or len(texts[idx-1])!=evidence.get('freshPageTextCharacters'): failures.append({'check':'page text','page':idx})
 all_units=[u for p in pages for u in p.get('units') or []]; counts={
  'pages':4,'coverPages':1,'rulingAndErrataUnits':len(all_units),
  'baseGameApplicableUnits':sum(u['applicability'].startswith('base-game') for u in all_units),
  'expansionSpecificUnits':sum(u['applicability'].startswith('expansion-') for u in all_units),
  'errataUnits':sum(u['unitKind']=='erratum' for u in all_units),'faqRulingUnits':sum(u['unitKind']=='faq-ruling' for u in all_units),
  'unitsWithVisualOccurrences':sum(bool(u.get('visualOccurrences')) for u in all_units),'visualOccurrences':len(icon_ids),
  'materialUnreadableSpans':sum(len(p.get('materialUnreadableSpans') or []) for p in pages),
 }
 expected={'pages':4,'coverPages':1,'rulingAndErrataUnits':59,'baseGameApplicableUnits':28,'expansionSpecificUnits':31,'errataUnits':15,'faqRulingUnits':44,'unitsWithVisualOccurrences':2,'visualOccurrences':4,'materialUnreadableSpans':0}
 if counts!=expected or d.get('counts')!=expected: failures.append({'check':'counts','expected':expected,'actual':counts,'stored':d.get('counts')})
 sections=Counter(u['section'] for u in all_units); expected_sections={'ERRATA':2,'GENERAL RULES':11,'ACTION CARDS':3,'ROOMS':4,'ITEMS AND TACTICAL GEAR':9,'CONTRACTORS AND SUPPORT SQUAD':3,'NEOFLESH CULT EXPANSION':6,'XYRIANS EXPANSION':2,'INSIDER EXPANSION':2,'SANGREVORES EXPANSION':3,'BIO-ENHANCEMENT SUPPORT':1,'COMIC':13}
 if dict(sections)!=expected_sections: failures.append({'check':'section counts','expected':expected_sections,'actual':dict(sections)})
 def unit(section,number): return next((u for u in all_units if u['section']==section and u['pageLocalNumber']==number),None)
 if 'before the end game sequence' not in (unit('GENERAL RULES',3) or {}).get('printedText',''): failures.append({'check':'required base ruling'})
 if 'FQ-P02-U21-I01' not in (unit('ITEMS AND TACTICAL GEAR',1) or {}).get('printedText',''): failures.append({'check':'base inline glyph recovery'})
 if 'FQ-P03-U13-I01' not in (unit('NEOFLESH CULT EXPANSION',2) or {}).get('printedText',''): failures.append({'check':'expansion inline glyph recovery'})
 cover=pages[0].get('coverMetadata') or {}
 if cover!={'printedVersion':'V1.2','printedDate':'8.06.2026','publisher':'AWAKEN REALMS'}: failures.append({'check':'cover metadata'})
 report={'schemaVersion':1,'passed':not failures,'checks':expected,'failureCount':len(failures),'failures':failures}; print(json.dumps(report,indent=2,ensure_ascii=False)); return 0 if not failures else 1
if __name__=='__main__': raise SystemExit(main())
