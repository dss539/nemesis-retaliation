#!/usr/bin/env python3
"""Merge a validated staged native-vision run into the working text corpus.

This is an evidence overlay, not canonical promotion. It preserves the existing
ledger-derived printedData/symbols snapshot and materializes selected current
comparisons so consumers need not traverse worker files for the latest evidence.
"""
from __future__ import annotations
import argparse, hashlib, json
from datetime import datetime, timezone
from pathlib import Path


def now():
    return datetime.now(timezone.utc).isoformat().replace('+00:00','Z')


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--repo', required=True)
    ap.add_argument('--worker-root', required=True)
    ap.add_argument('--corpus', default='assets/tts-mod/extract/card-text-corpus.json')
    ap.add_argument('--output', default=None)
    args=ap.parse_args()
    repo=Path(args.repo).resolve()
    worker=(repo/args.worker_root).resolve()
    corpus_path=(repo/args.corpus).resolve()
    output=(repo/args.output).resolve() if args.output else corpus_path
    assignment=json.loads((worker/'assignment.json').read_text())
    validation=json.loads((worker/'metadata/validation.json').read_text())
    report=json.loads((worker/'metadata/worker-report.json').read_text())
    if not validation.get('overallPassed'):
        raise SystemExit('worker validation did not pass')
    if report.get('sharedWritesPerformed') or report.get('canonicalPromotionClaimed'):
        raise SystemExit('worker report claims forbidden shared write or promotion')
    results=[]
    for asset in assignment['assets']:
        p=worker/'results'/f"{asset['assetId']}.json"
        result=json.loads(p.read_text())
        if result.get('promotionDecision') != 'defer':
            raise SystemExit(f"{asset['assetId']} is not deferred; promotion gate requires separate handling")
        if result.get('sourcePath') != asset['sourcePath'] or result.get('sourceSha256') != asset['sourceSha256']:
            raise SystemExit(f"{asset['assetId']} result tuple mismatch")
        results.append((asset,result,p))
    doc=json.loads(corpus_path.read_text())
    records=doc.get('records')
    if not isinstance(records,list):
        raise SystemExit('corpus records is not a list')
    by_tuple={}
    for i,r in enumerate(records):
        key=(r.get('sourcePath'),r.get('sourceSha256'))
        if key in by_tuple:
            raise SystemExit(f'duplicate corpus tuple: {key}')
        by_tuple[key]=i
    changed=[]
    for asset,result,result_path in results:
        key=(asset['sourcePath'],asset['sourceSha256'])
        if key not in by_tuple:
            raise SystemExit(f'corpus missing exact source tuple: {key}')
        r=records[by_tuple[key]]
        comparisons=result.get('authoritativeComparisons',[])
        verified=[]
        unresolved=[]
        for cmp in comparisons:
            token=cmp.get('canonicalToken')
            decision=cmp.get('matchDecision')
            row={
                'cardLocation':cmp.get('cardLocation'),
                'referenceLabel':cmp.get('referenceLabel'),
                'matchDecision':decision,
                'canonicalToken':token,
                'closestAlternative':cmp.get('closestAlternative'),
                'visibleDiscriminator':cmp.get('visibleDiscriminator'),
                'evidenceRun':assignment['workerId'],
            }
            if decision == 'match' and token:
                verified.append(row)
            else:
                unresolved.append(row)
        prior_upper=r.get('printedData',{}).get('upperRight') if isinstance(r.get('printedData'),dict) else None
        conflicts=[]
        if prior_upper and any(x.get('cardLocation','').lower().startswith('upper-right') and x.get('matchDecision') != 'match' for x in unresolved):
            conflicts.append({'field':'printedData.upperRight','priorValue':prior_upper,'currentStatus':'unresolved/no-authorized-match','resolution':'preserved prior snapshot; current staged evidence blocks canonical semantic use'})
        overlay={
            'overlayVersion':1,
            'status':'selected-evidence-deferred',
            'workerId':assignment['workerId'],
            'sourcePath':asset['sourcePath'],
            'sourceSha256':asset['sourceSha256'],
            'runtime':result.get('runtimeProvenance'),
            'blindObservationPath':str((worker/'raw'/f"{asset['assetId']}.json").relative_to(repo)),
            'resultPath':str(result_path.relative_to(repo)),
            'contactSheetPath':result.get('contactSheetPath'),
            'visibleText':result.get('visibleText'),
            'verifiedIconOccurrences':verified,
            'unresolvedIconOccurrences':unresolved,
            'canonicalTokensEmitted':result.get('canonicalTokensEmitted',[]),
            'allMaterialTextReadable':result.get('adjudicationModelOutput',{}).get('allMaterialTextReadable'),
            'allMaterialIconsAuthoritativelyMatched':result.get('adjudicationModelOutput',{}).get('allMaterialIconsAuthoritativelyMatched'),
            'promotionDecision':'defer',
            'decisionReasons':result.get('decisionReasons',[]),
            'conflictsWithPriorSnapshot':conflicts,
            'mergedAt':now(),
        }
        r.setdefault('evidence',{})['selectedExtraction']= {
            'workerId':assignment['workerId'],
            'resultPath':overlay['resultPath'],
            'rawResultPath':overlay['blindObservationPath'],
            'contactSheetPath':overlay['contactSheetPath'],
            'promotionDecision':'defer',
            'runtime':overlay['runtime'],
        }
        r['selectedExtraction']=overlay
        r.setdefault('evidenceRuns',[])
        r['evidenceRuns'].append({
            'workerId':assignment['workerId'],
            'sourceSha256':asset['sourceSha256'],
            'blindSessionId':(result.get('runtimeProvenance') or {}).get('blindSessionId'),
            'adjudicationSessionId':(result.get('runtimeProvenance') or {}).get('adjudicationSessionId'),
            'promotionDecision':'defer',
            'resultPath':overlay['resultPath'],
            'selected':True,
        })
        changed.append({'sourcePath':asset['sourcePath'],'verifiedIconCount':len(verified),'unresolvedIconCount':len(unresolved),'conflictCount':len(conflicts)})
    meta=doc.setdefault('metadata',{})
    meta['selectedEvidenceLastMerged']={'workerId':assignment['workerId'],'mergedAt':now(),'recordCount':len(changed),'decision':'deferred-overlay-only','sourceTupleDigest':validation['orderedTupleDigest']}
    output.write_text(json.dumps(doc,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({'output':str(output),'workerId':assignment['workerId'],'changed':changed,'recordCount':len(records),'sha256':hashlib.sha256(output.read_bytes()).hexdigest()},indent=2,ensure_ascii=False))

if __name__=='__main__': main()
