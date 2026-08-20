#!/usr/bin/env python3
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sqlite3
from typing import Any

from PIL import Image

REPO = Path('/home/smithers/projects/nemesis-card-corpus/repos/nemesis-retaliation')
ROOT = REPO / 'assets/tts-mod/extract/vision-workers/sol-max-persistent-worker-23-20260820T185027Z-p240642-4513b3'
STATE_DB = Path('/home/smithers/.hermes/state.db')


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(obj: Any) -> bytes:
    return (json.dumps(obj, indent=2, ensure_ascii=False) + '\n').encode()


def parse_tools(raw: Any) -> int:
    if raw is None:
        return 0
    try:
        data = json.loads(raw) if isinstance(raw, str) else raw
    except Exception:
        return 1
    if isinstance(data, list):
        return len(data)
    return 0 if not data else 1


def create(path: Path, obj: Any) -> None:
    if path.exists():
        raise RuntimeError(f'refuse overwrite {path}')
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_bytes(canonical(obj))
    os.replace(tmp, path)


def main() -> None:
    assignment = json.loads((ROOT / 'assignment.json').read_text())
    baseline = json.loads((ROOT / 'metadata/baseline.json').read_text())
    ids = [f'W23-{i:03d}' for i in range(1, 9)]
    assets = assignment['assets']
    results = [json.loads((ROOT / 'results' / f'{asset_id}.json').read_text()) for asset_id in ids]
    source_checks = []
    for asset, result in zip(assets, results):
        asset_id = asset['assetId']
        source = REPO / asset['sourcePath']
        with Image.open(source) as im:
            im.verify()
        raw = ROOT / 'raw' / f'{asset_id}.json'
        sealed = ROOT / 'sealed-clean-raw' / f'{asset_id}.json'
        reconciliation = result['morphologyReconciliation']
        source_checks.append({
            'assetId': asset_id,
            'tupleExact': (result['assetId'], result['sourcePath'], result['sourceSha256']) == (asset_id, asset['sourcePath'], asset['sourceSha256']),
            'liveSourceHashExact': sha(source) == asset['sourceSha256'],
            'decodePassed': True,
            'rawWrapperByteExact': raw.read_bytes() == sealed.read_bytes(),
            'morphologyIndexPartitionExact': sorted(x['sourceIconMorphologyIndex'] for x in reconciliation) == list(range(len(result['iconMorphology']))) and len({x['sourceIconMorphologyIndex'] for x in reconciliation}) == len(reconciliation),
        })
    counts = {
        'assigned': len(assets),
        'results': len(results),
        'morphologies': sum(len(x['iconMorphology']) for x in results),
        'matches': sum(c['matchDecision'] == 'match' for x in results for c in x['authoritativeComparisons']),
        'explicitNoMatches': sum(c['matchDecision'] == 'no-match' for x in results for c in x['authoritativeComparisons']),
        'unresolvedRows': sum(len(x['unresolvedLocalTokens']) for x in results),
        'nonTextGraphics': sum(len(x['nonTextComponentGraphics']) for x in results),
        'artworkMorphologies': sum(len(x['iconMorphologyArtDisplayDetails']) for x in results),
        'rulesBearing': sum(x['sourceProvenance']['rulesBearing'] is True for x in results),
        'deferred': sum(x['promotionDecision'] == 'defer' for x in results),
        'promoted': sum(x['promotionDecision'] == 'promote' for x in results),
    }
    expected_counts = {
        'assigned': 8, 'results': 8, 'morphologies': 15, 'matches': 2,
        'explicitNoMatches': 8, 'unresolvedRows': 8, 'nonTextGraphics': 4,
        'artworkMorphologies': 1, 'rulesBearing': 8, 'deferred': 8, 'promoted': 0,
    }
    runtime = json.loads((ROOT / 'metadata/runtime.json').read_text())
    expected_sessions = []
    expected_sessions.extend((sid, 8, 16) for sid in runtime['blind']['sessionIds'])
    expected_sessions.extend((sid, calls, messages) for sid, calls, messages in zip(runtime['bboxAdjudication']['sessionIds'], (1, 7), (2, 14)))
    expected_sessions.extend((sid, calls, messages) for sid, calls, messages in zip(runtime['contactAdjudication']['sessionIds'], (1, 7), (2, 14)))
    con = sqlite3.connect(f'file:{STATE_DB}?mode=ro', uri=True)
    con.row_factory = sqlite3.Row
    session_checks = []
    for session_id, expected_calls, expected_messages in expected_sessions:
        row = con.execute('select model,billing_provider,model_config from sessions where id=?', (session_id,)).fetchone()
        usage = con.execute("select api_call_count from session_model_usage where session_id=? and task=''", (session_id,)).fetchone()
        messages = con.execute('select role,tool_calls from messages where session_id=? order by timestamp,id', (session_id,)).fetchall()
        cfg = json.loads(row['model_config'])
        check = {
            'sessionId': session_id,
            'provider': row['billing_provider'],
            'model': row['model'],
            'reasoningEffort': (cfg.get('reasoning_config') or {}).get('effort'),
            'apiCallCount': int(usage['api_call_count']),
            'messageCount': len(messages),
            'toolCallCount': sum(parse_tools(x['tool_calls']) for x in messages),
            'expectedApiCallCount': expected_calls,
            'expectedMessageCount': expected_messages,
        }
        check['passed'] = (
            check['provider'] == 'openai-codex' and check['model'] == 'gpt-5.6-sol' and
            check['reasoningEffort'] == 'max' and check['apiCallCount'] == expected_calls and
            check['messageCount'] == expected_messages and check['toolCallCount'] == 0
        )
        session_checks.append(check)
    con.close()
    shared = {
        'progress': REPO / 'assets/tts-mod/extract/vision-progress.json',
        'queue': REPO / 'assets/tts-mod/extract/low-confidence-review.json',
        'registry': REPO / 'assets/tts-mod/extract/selected-card-text-evidence.json',
        'corpus': REPO / 'assets/tts-mod/extract/card-text-corpus.json',
    }
    checks = {
        'assetIdsExact': [x['assetId'] for x in results] == ids,
        'sourceChecksAllPassed': all(all(v for k, v in row.items() if k != 'assetId') for row in source_checks),
        'countsExact': counts == expected_counts,
        'sessionsExact': len(session_checks) == 5 and all(x['passed'] for x in session_checks),
        'sharedPreimageUntouched': {k: sha(v) for k, v in shared.items()} == baseline['sharedPreimageSha256'],
        'candidateDirectoriesEmpty': not any((ROOT / 'candidates/images').iterdir()) and not any((ROOT / 'candidates/sidecars').iterdir()),
        'allResultsDeferred': all(x['promotionDecision'] == 'defer' for x in results),
    }
    report = {
        'schemaVersion': 1,
        'recordedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        'workerId': ROOT.name,
        'checks': checks,
        'counts': counts,
        'sourceChecks': source_checks,
        'sessionChecks': session_checks,
        'resultSummary': [
            {
                'assetId': x['assetId'], 'title': x['visibleText']['title'],
                'sourceFidelityStatus': x['sourceFidelity']['sourceFidelityStatus'],
                'conflictCount': len(x['sourceFidelity']['conflicts']),
                'exactFaceSelectorResolved': x['sourceProvenance']['exactFaceSelectorResolved'],
                'canonicalTokensEmitted': x['canonicalTokensEmitted'],
                'promotionDecision': x['promotionDecision'],
            }
            for x in results
        ],
        'overallPassed': all(checks.values()),
    }
    if not report['overallPassed']:
        raise RuntimeError(json.dumps(report, indent=2))
    out = ROOT / 'validation/independent-core-validation.json'
    create(out, report)
    print(json.dumps({'status': 'passed', 'counts': counts, 'sessions': session_checks, 'sha256': sha(out)}))


if __name__ == '__main__':
    main()
