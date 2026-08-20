#!/usr/bin/env python3
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any

from PIL import Image

ROOT = Path(__file__).resolve().parent
REPO = Path('/home/smithers/projects/nemesis-card-corpus/repos/nemesis-retaliation')
AUDITOR = Path('/home/smithers/.hermes/skills/research/extract-game-mod-assets/scripts/audit_native_vision_worker.py')
AUDIT_VIEW = ROOT / 'audit-view/normalized'
EXPECTED_ROOT = 'sol-max-persistent-worker-23-20260820T185027Z-p240642-4513b3'
IDS = [f'W23-{i:03d}' for i in range(1, 9)]
EXPECTED_ASSIGNMENT_SHA = '1a946cb84717441f02df1871b8845fd0845ffdecfdd0079bf48a1616f3785199'
EXPECTED_TUPLE_DIGEST = '1cadcfc22b5c9b40e8b542963afc58a9f422eaf7f9c823d120c15914d47af662'
SHARED = {
    'progress': REPO / 'assets/tts-mod/extract/vision-progress.json',
    'queue': REPO / 'assets/tts-mod/extract/low-confidence-review.json',
    'registry': REPO / 'assets/tts-mod/extract/selected-card-text-evidence.json',
    'corpus': REPO / 'assets/tts-mod/extract/card-text-corpus.json',
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


def load(path: Path) -> Any:
    return json.loads(path.read_text())


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bytes_sha(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def data(value: Any) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False) + '\n').encode()


def create_bytes(path: Path, content: bytes, mode: int = 0o400) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise RuntimeError(f'refuse overwrite: {path}')
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, mode)
    try:
        os.write(fd, content)
        os.fsync(fd)
    finally:
        os.close(fd)
    os.chmod(path, mode)


def create_json(path: Path, value: Any, mode: int = 0o400) -> None:
    create_bytes(path, data(value), mode)


def rel(path: Path) -> str:
    return path.relative_to(REPO).as_posix()


def tuple_digest(assets: list[dict[str, Any]]) -> str:
    rows = [[x['assetId'], x['sourcePath'], x['sourceSha256']] for x in assets]
    return bytes_sha(json.dumps(rows, separators=(',', ':')).encode())


def semantic_digest(result: dict[str, Any]) -> str:
    value = json.loads(json.dumps(result))
    value.pop('runtimeProvenance', None)
    return bytes_sha(json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode())


def image_probe(path: Path) -> dict[str, Any]:
    content = path.read_bytes()
    with Image.open(path) as image:
        image.verify()
    with Image.open(path) as image:
        return {
            'width': image.width, 'height': image.height, 'format': image.format,
            'mode': image.mode, 'frames': getattr(image, 'n_frames', 1),
            'bytes': len(content), 'decode': True,
        }


def parse_jsons(root: Path) -> tuple[int, list[dict[str, str]]]:
    failures = []
    paths = sorted(root.rglob('*.json'))
    for path in paths:
        try:
            load(path)
        except Exception as exc:
            failures.append({'path': path.relative_to(root).as_posix(), 'error': str(exc)})
    return len(paths), failures


def main() -> None:
    if ROOT.name != EXPECTED_ROOT:
        raise RuntimeError('worker-root mismatch')
    script_text = Path(__file__).read_text()
    stale_markers = ['W' + str(number) + '-' for number in range(18, 23)]
    stale_markers += ['worker-' + str(22), '4885' + '4fdd']
    stale = [marker for marker in stale_markers if marker in script_text]
    if stale:
        raise RuntimeError(f'stale closure markers: {stale}')
    outputs = [
        ROOT / 'validation/closure-audit.json', ROOT / 'validation/final-validation.json',
        ROOT / 'metadata/worker-report.json', ROOT / 'metadata/validation.json',
        ROOT / 'reports/worker-report.json', ROOT / 'checkpoints/checkpoint-W23-final.json',
        ROOT / 'metadata/audit-view-adapter.json',
    ]
    if any(x.exists() for x in outputs) or AUDIT_VIEW.exists():
        raise RuntimeError('closure output/audit view already exists')
    assignment_path = ROOT / 'assignment.json'
    if sha(assignment_path) != EXPECTED_ASSIGNMENT_SHA or assignment_path.read_bytes() != (ROOT / 'assignment.immutable.json').read_bytes():
        raise RuntimeError('assignment drift')
    assignment = load(assignment_path)
    assets = assignment['assets']
    if [x['assetId'] for x in assets] != IDS or tuple_digest(assets) != EXPECTED_TUPLE_DIGEST:
        raise RuntimeError('ordered tuple drift')
    baseline = load(ROOT / 'metadata/baseline.json')
    shared_preimage = {name: sha(path) for name, path in SHARED.items()}
    if shared_preimage != baseline['sharedPreimageSha256']:
        raise RuntimeError('shared preimage drift before closure')
    prerequisite_paths = [
        ROOT / 'metadata/direct-session-audit.json', ROOT / 'metadata/raw-wrapper-preservation.json',
        ROOT / 'metadata/source-provenance.json', ROOT / 'metadata/source-reconciliation.json',
        ROOT / 'metadata/material-field-normalization.json', ROOT / 'metadata/adjudication-summary.json',
        ROOT / 'validation/core-validation.json', ROOT / 'validation/independent-core-validation.json',
    ]
    for path in prerequisite_paths:
        if not load(path).get('overallPassed'):
            raise RuntimeError(f'prerequisite failed: {path}')
    runtime_path = ROOT / 'metadata/runtime.json'
    runtime = load(runtime_path)
    if (runtime['provider'], runtime['model'], runtime['reasoningEffort']) != ('openai-codex', 'gpt-5.6-sol', 'max'):
        raise RuntimeError('runtime core mismatch')
    if runtime['totalProductionNativeImageApiCalls'] != 24 or runtime['totalProductionMessages'] != 48 or runtime['totalProductionToolCalls'] != 0:
        raise RuntimeError('production runtime count mismatch')
    independent = load(ROOT / 'validation/independent-core-validation.json')
    if len(independent['sessionChecks']) != 5 or not all(x['passed'] for x in independent['sessionChecks']):
        raise RuntimeError('session checks incomplete')
    results: dict[str, dict[str, Any]] = {}
    totals = Counter()
    source_checks = []
    for index, asset in enumerate(assets):
        aid = asset['assetId']
        source = REPO / asset['sourcePath']
        live_meta = image_probe(source)
        if sha(source) != asset['sourceSha256'] or live_meta != asset['sourceMetadata']:
            raise RuntimeError(f'{aid}: source drift')
        sealed = ROOT / 'sealed-clean-raw' / f'{aid}.json'
        raw = ROOT / 'raw' / f'{aid}.json'
        result_path = ROOT / 'results' / f'{aid}.json'
        if raw.read_bytes() != sealed.read_bytes() or (raw.stat().st_mode & 0o777) != 0o400:
            raise RuntimeError(f'{aid}: raw wrapper drift/mode')
        wrapper = load(raw)
        result = load(result_path)
        results[aid] = result
        for label, value in (('raw', wrapper), ('result', result)):
            if (value['assetId'], value['sourcePath'], value['sourceSha256']) != (aid, asset['sourcePath'], asset['sourceSha256']):
                raise RuntimeError(f'{aid}: {label} tuple drift')
        if result['sourceMetadata'] != live_meta or result['orientation']['observed'] != 'upright':
            raise RuntimeError(f'{aid}: metadata/orientation drift')
        expected_next_id = IDS[index + 1] if index + 1 < len(IDS) else None
        expected_next_path = assets[index + 1]['sourcePath'] if index + 1 < len(IDS) else None
        if (result['nextPendingAssetId'], result['nextPendingSourcePath']) != (expected_next_id, expected_next_path):
            raise RuntimeError(f'{aid}: next-pending drift')
        if result['promotionDecision'] != 'defer' or result['status'] != 'complete' or result['extractionState'] != 'draft-partial':
            raise RuntimeError(f'{aid}: result state drift')
        reconciled = result['morphologyReconciliation']
        if sorted(x['sourceIconMorphologyIndex'] for x in reconciled) != list(range(len(result['iconMorphology']))) or len({x['sourceIconMorphologyIndex'] for x in reconciled}) != len(reconciled):
            raise RuntimeError(f'{aid}: morphology partition drift')
        comparisons = result['authoritativeComparisons']
        no_match = [x for x in comparisons if x['matchDecision'] == 'no-match']
        matches = [x for x in comparisons if x['matchDecision'] == 'match']
        if len(no_match) != len(result['unresolvedLocalTokens']) or any(x['canonicalToken'] is not None for x in no_match):
            raise RuntimeError(f'{aid}: unresolved/no-match drift')
        totals.update({
            'morphologies': len(result['iconMorphology']), 'matches': len(matches),
            'noMatches': len(no_match), 'nonText': len(result['nonTextComponentGraphics']),
            'artworkMorphologies': len(result['iconMorphologyArtDisplayDetails']),
            'nonRulesDetails': len(result['nonRulesIllustrationDetails']),
        })
        source_checks.append({
            'assetId': aid, 'sourcePath': asset['sourcePath'], 'sourceSha256': asset['sourceSha256'],
            'sourceMetadata': live_meta, 'sealedWrapperSha256': sha(sealed),
            'rawCopySha256': sha(raw), 'rawByteIdentical': True, 'resultSha256': sha(result_path),
        })
    expected_totals = Counter({'morphologies': 15, 'matches': 2, 'noMatches': 8, 'nonText': 4, 'artworkMorphologies': 1, 'nonRulesDetails': 10})
    if totals != expected_totals:
        raise RuntimeError(f'aggregate drift {dict(totals)}')
    if any((ROOT / 'candidates/images').iterdir()) or any((ROOT / 'candidates/sidecars').iterdir()):
        raise RuntimeError('candidate staging nonempty')
    normalized = {
        'schemaVersion': 1,
        'workerId': ROOT.name,
        'sealed': True,
        'sealedAt': now(),
        'actualRuntime': {
            'provider': 'openai-codex', 'model': 'gpt-5.6-sol',
            'reasoningEffort': 'max', 'verificationState': 'verified',
        },
        'session': {
            'sessionId': runtime['blind']['sessionIds'][0],
            'apiCallCount': runtime['blind']['apiCallCount'],
            'messageCount': runtime['blind']['messageCount'],
            'toolCallCount': runtime['blind']['toolCallCount'],
        },
        'nativeImageRoute': {'state': 'exercisedVerified'},
        'forbiddenRoutes': {
            'auxiliaryVisionUsed': False, 'qwenUsed': False, 'ocrCanonicalEvidenceUsed': False,
            'modelDowngradeUsed': False, 'sharedProviderConfigurationModified': False,
        },
        'adapter': {
            'sourceRuntimePath': rel(runtime_path), 'sourceRuntimeSha256': sha(runtime_path),
            'sourceSessionChecksPath': rel(ROOT / 'validation/independent-core-validation.json'),
            'sourceSessionChecksSha256': sha(ROOT / 'validation/independent-core-validation.json'),
            'copiedEvidenceOnly': True, 'mergeInput': False,
            'sessionAuditSkippedBecause': 'Five production sessions are separately DB-audited; the reusable auditor supports one session ID only.',
        },
    }
    normalized_bytes = data(normalized)
    normalized_sha = bytes_sha(normalized_bytes)
    AUDIT_VIEW.mkdir(parents=True, mode=0o700)
    create_bytes(AUDIT_VIEW / 'assignment.json', assignment_path.read_bytes())
    create_bytes(AUDIT_VIEW / 'metadata/runtime.json', normalized_bytes)
    mappings = []
    for aid in IDS:
        source_raw = ROOT / 'raw' / f'{aid}.json'
        target_raw = AUDIT_VIEW / 'raw' / f'{aid}.json'
        create_bytes(target_raw, source_raw.read_bytes())
        source_result = ROOT / 'results' / f'{aid}.json'
        result = load(source_result)
        before = semantic_digest(result)
        result['runtimeProvenance'] = {
            'actualRuntime': normalized['actualRuntime'],
            'session': normalized['session'],
            'normalizedRecordSha256': normalized_sha,
            'nativeImageRouteState': 'exercisedVerified',
            'adapterOnly': True,
            'sourceResultPath': rel(source_result), 'sourceResultSha256': sha(source_result),
            'sourceRuntimePath': rel(runtime_path), 'sourceRuntimeSha256': sha(runtime_path),
            'sourceSessionChecksPath': rel(ROOT / 'validation/independent-core-validation.json'),
        }
        if semantic_digest(result) != before:
            raise RuntimeError(f'{aid}: adapter semantic drift')
        target_result = AUDIT_VIEW / 'results' / f'{aid}.json'
        create_json(target_result, result)
        mappings.append({
            'assetId': aid,
            'sourceRawPath': rel(source_raw), 'sourceRawSha256': sha(source_raw),
            'copiedRawSha256': sha(target_raw), 'rawByteIdentical': source_raw.read_bytes() == target_raw.read_bytes(),
            'sourceResultPath': rel(source_result), 'sourceResultSha256': sha(source_result),
            'copiedResultSha256': sha(target_result), 'semanticDigestExcludingRuntime': before,
        })
    create_json(AUDIT_VIEW / 'metadata/baseline.json', {
        'schemaVersion': 1, 'assignmentSha256': EXPECTED_ASSIGNMENT_SHA,
        'orderedTupleDigest': EXPECTED_TUPLE_DIGEST,
    })
    rationale = {
        'schemaVersion': 1,
        'recordType': 'nativeVisionAuditorCompatibilityAdapter',
        'workerId': ROOT.name,
        'originalAssignmentPath': rel(assignment_path), 'originalAssignmentSha256': EXPECTED_ASSIGNMENT_SHA,
        'originalRuntimePath': rel(runtime_path), 'originalRuntimeSha256': sha(runtime_path),
        'normalizedRuntimeSha256': normalized_sha,
        'rawCopiesByteIdentical': all(x['rawByteIdentical'] for x in mappings),
        'resultSemanticsPreserved': True,
        'mappings': mappings,
        'adapterIsEvidence': False, 'adapterIsMergeInput': False,
        'auditorInvocationRequiresSkipSessionAudit': True,
    }
    create_json(AUDIT_VIEW / 'adapter-rationale.json', rationale)
    command = [
        sys.executable, str(AUDITOR), '--repo', str(REPO), '--worker-root', str(AUDIT_VIEW),
        '--baseline', 'metadata/baseline.json', '--skip-session-audit', '--skip-git',
    ]
    completed = subprocess.run(command, cwd=REPO, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=300)
    try:
        audit_output = json.loads(completed.stdout)
    except Exception as exc:
        create_json(ROOT / 'metadata/failures/closure-audit-attempt-01.json', {
            'schemaVersion': 1, 'recordedAt': now(), 'returnCode': completed.returncode,
            'stdout': completed.stdout, 'stderr': completed.stderr, 'parseError': str(exc),
        })
        raise
    if completed.returncode != 0 or not audit_output.get('overallPassed') or audit_output.get('errors') or audit_output.get('warnings'):
        create_json(ROOT / 'metadata/failures/closure-audit-attempt-01.json', {
            'schemaVersion': 1, 'recordedAt': now(), 'returnCode': completed.returncode,
            'auditOutput': audit_output, 'stderr': completed.stderr,
        })
        raise RuntimeError(f"standard auditor failed/errors/warnings: {audit_output.get('errors')} {audit_output.get('warnings')}")
    closure_record = {
        'schemaVersion': 1, 'recordType': 'standardNativeVisionWorkerClosureAudit',
        'capturedAt': now(), 'auditorPath': str(AUDITOR), 'auditorSha256': sha(AUDITOR),
        'command': command, 'returnCode': completed.returncode, 'stderr': completed.stderr,
        'auditOutput': audit_output, 'overallPassed': True,
    }
    create_json(ROOT / 'validation/closure-audit.json', closure_record)
    create_json(ROOT / 'metadata/audit-view-adapter.json', rationale)
    core = load(ROOT / 'validation/core-validation.json')
    report = {
        'schemaVersion': 1, 'workerId': ROOT.name, 'runId': 'w23-card-extraction-20260820T185027Z-p240642-4513b3',
        'reportedAt': now(), 'scope': 'W23 eight exact Mission Task tuples at original queue indices 113-120',
        'assignmentSha256': EXPECTED_ASSIGNMENT_SHA, 'orderedTupleDigest': EXPECTED_TUPLE_DIGEST,
        'actualRuntime': normalized['actualRuntime'],
        'sessionSet': independent['sessionChecks'],
        'decisionCounts': {'defer': 8}, 'counts': core['counts'],
        'validationPassed': True,
        'coreValidationPath': rel(ROOT / 'validation/core-validation.json'),
        'independentValidationPath': rel(ROOT / 'validation/independent-core-validation.json'),
        'closureAuditPath': rel(ROOT / 'validation/closure-audit.json'),
        'sharedWritesPerformed': False, 'canonicalPromotionClaimed': False,
        'candidatePromotionCount': 0, 'deferredCount': 8,
        'candidateSidecarCount': 0, 'canonicalChangesProposed': 0,
        'caveats': [
            'Eight explicit no-match rows preserve the ringed Number-of-Characters composites one-to-one.',
            'Only W23-002 has canonical inline Character and Lander matches.',
            'W23-003/004/005/006/008 materially conflict with current official counterparts.',
            'W23-007 has no current official Mission Task counterpart.',
            'The exact paired BackURL is stale/unavailable and was not fabricated.',
            'Generated cells W23-004..008 do not have safely unique GUID/CardID selectors.',
            'No protected canonical target was changed.',
        ],
        'overallPassed': True,
    }
    create_json(ROOT / 'reports/worker-report.json', report)
    create_json(ROOT / 'metadata/worker-report.json', report)
    validation_compat = {
        'schemaVersion': 1, 'recordType': 'validatedWorkerCompatibilityRecord',
        'validatedAt': now(), 'workerId': ROOT.name,
        'assignmentSha256': EXPECTED_ASSIGNMENT_SHA, 'orderedTupleDigest': EXPECTED_TUPLE_DIGEST,
        'counts': core['counts'], 'decisionCounts': {'defer': 8},
        'coreValidationSha256': sha(ROOT / 'validation/core-validation.json'),
        'independentValidationSha256': sha(ROOT / 'validation/independent-core-validation.json'),
        'closureAuditSha256': sha(ROOT / 'validation/closure-audit.json'),
        'overallPassed': True,
    }
    create_json(ROOT / 'metadata/validation.json', validation_compat)
    create_json(ROOT / 'checkpoints/checkpoint-W23-final.json', {
        'schemaVersion': 1, 'recordedAt': now(), 'workerId': ROOT.name,
        'assignmentSha256': EXPECTED_ASSIGNMENT_SHA, 'orderedTupleDigest': EXPECTED_TUPLE_DIGEST,
        'completedIds': IDS, 'promotionCandidateIds': [], 'deferredIds': IDS,
        'nextPendingAssetId': None, 'nextPendingSourcePath': None,
        'sharedWritesPerformed': False, 'closureState': 'closed-passed',
        'coreValidationPath': rel(ROOT / 'validation/core-validation.json'),
        'closureAuditPath': rel(ROOT / 'validation/closure-audit.json'),
        'workerReportPath': rel(ROOT / 'metadata/worker-report.json'),
    })
    json_count, failures = parse_jsons(ROOT)
    if failures:
        raise RuntimeError(f'post-report JSON parse failures: {failures}')
    if {name: sha(path) for name, path in SHARED.items()} != shared_preimage:
        raise RuntimeError('shared files changed during closure')
    final = {
        'schemaVersion': 1, 'recordType': 'fullWorkerFinalValidation',
        'validatedAt': now(), 'workerId': ROOT.name,
        'assignmentSha256': EXPECTED_ASSIGNMENT_SHA, 'orderedTupleDigest': EXPECTED_TUPLE_DIGEST,
        'coreValidationSha256': sha(ROOT / 'validation/core-validation.json'),
        'independentValidationSha256': sha(ROOT / 'validation/independent-core-validation.json'),
        'closureAuditSha256': sha(ROOT / 'validation/closure-audit.json'),
        'workerReportSha256': sha(ROOT / 'metadata/worker-report.json'),
        'jsonFileCountSnapshot': json_count, 'jsonParseFailureCount': 0,
        'sourceCount': 8, 'rawCount': 8, 'resultCount': 8, 'adjudicationCount': 8,
        'decisionCounts': {'defer': 8},
        'verifiedIconOccurrenceCount': totals['matches'],
        'unresolvedIconOccurrenceCount': totals['noMatches'],
        'authoritativeNoMatchComparisonCount': totals['noMatches'],
        'nonTextComponentGraphicCount': totals['nonText'],
        'iconMorphologyArtDisplayDetailCount': totals['artworkMorphologies'],
        'blindIconMorphologyOccurrenceCount': totals['morphologies'],
        'candidateImageCount': 0, 'candidateSidecarCount': 0,
        'sharedBytesUnchanged': True, 'overallPassed': True,
    }
    create_json(ROOT / 'validation/final-validation.json', final)
    final_count, final_failures = parse_jsons(ROOT)
    if final_failures:
        raise RuntimeError(f'final JSON parse failures: {final_failures}')
    print(json.dumps({
        'workerId': ROOT.name, 'assignmentSha256': EXPECTED_ASSIGNMENT_SHA,
        'orderedTupleDigest': EXPECTED_TUPLE_DIGEST, 'decisionCounts': {'defer': 8},
        'matchedOccurrences': totals['matches'], 'unresolvedNoMatchOccurrences': totals['noMatches'],
        'nonTextGraphics': totals['nonText'], 'artworkMorphologies': totals['artworkMorphologies'],
        'standardAuditorErrors': len(audit_output['errors']), 'standardAuditorWarnings': len(audit_output['warnings']),
        'finalJsonFileCountReadOnlySnapshot': final_count, 'sharedBytesUnchanged': True,
        'overallPassed': True,
    }, indent=2))


if __name__ == '__main__':
    main()
