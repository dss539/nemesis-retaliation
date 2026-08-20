#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sqlite3
from typing import Any

import run_w23_contact_adjudication as runner

REPO = Path('/home/smithers/projects/nemesis-card-corpus/repos/nemesis-retaliation').resolve()
ROOT = REPO / 'assets/tts-mod/extract/vision-workers/sol-max-persistent-worker-23-20260820T185027Z-p240642-4513b3'
ASSET_ID = 'W23-001'
SESSION_ID = '20260820_194841_5f9531'


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(obj: Any) -> bytes:
    return (json.dumps(obj, indent=2, ensure_ascii=False) + '\n').encode()


def immutable(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise RuntimeError(f'refuse overwrite: {path}')
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_bytes(data)
    os.chmod(tmp, 0o400)
    os.replace(tmp, path)


def iso(ts: float) -> str:
    return datetime.fromtimestamp(ts, timezone.utc).isoformat().replace('+00:00', 'Z')


def main() -> None:
    assignment_bytes = (ROOT / 'assignment.json').read_bytes()
    assignment_sha = sha(assignment_bytes)
    dispatch = json.loads((ROOT / 'supervisor-dispatch.json').read_text())
    if assignment_sha != dispatch['assignmentSha256']:
        raise RuntimeError('assignment drift')
    assignment = json.loads(assignment_bytes)
    asset = next(x for x in assignment['assets'] if x['assetId'] == ASSET_ID)
    index_path = ROOT / 'qa/contact-sheets/index.json'
    index_bytes = index_path.read_bytes()
    index_sha = sha(index_bytes)
    record = next(x for x in json.loads(index_bytes)['assets'] if x['assetId'] == ASSET_ID)
    sheet = REPO / record['contactSheetPath']
    if sha(sheet.read_bytes()) != record['contactSheetSha256']:
        raise RuntimeError('contact sheet drift')
    stdout_path = ROOT / 'logs/adjudication-contact/W23-001.stdout.log'
    stderr_path = ROOT / 'logs/adjudication-contact/W23-001.stderr.log'
    payload = runner.parse_json(stdout_path.read_text(encoding='utf-8'))
    if payload['assetId'] != ASSET_ID or payload['runtime']['sessionId'] != SESSION_ID:
        raise RuntimeError('contact payload identity mismatch')
    expected_indices = [x['sourceIconMorphologyIndex'] for x in record['occurrences']]
    occurrences = payload.get('occurrences') or []
    if [x.get('sourceIconMorphologyIndex') for x in occurrences] != expected_indices or payload.get('occurrenceCount') != len(expected_indices):
        raise RuntimeError('contact occurrence mismatch')
    db = runner.probe(SESSION_ID, 1)
    con = sqlite3.connect('file:/home/smithers/.hermes/state.db?mode=ro', uri=True)
    rows = con.execute('select role,timestamp from messages where session_id=? order by timestamp,id', (SESSION_ID,)).fetchall()
    con.close()
    if len(rows) != 2:
        raise RuntimeError('unexpected contact message count')
    wrapper = {
        'schemaVersion': 1,
        'assetId': ASSET_ID,
        'phase': 'post-blind-authoritative-contact-adjudication',
        'sourcePath': asset['sourcePath'],
        'sourceSha256': asset['sourceSha256'],
        'assignmentSha256': assignment_sha,
        'contactIndexSha256': index_sha,
        'contactSheetPath': record['contactSheetPath'],
        'contactSheetSha256': record['contactSheetSha256'],
        'startedAt': iso(rows[0][1]),
        'endedAt': iso(rows[1][1]),
        'commandRoute': 'direct-hermes-chat-native-image',
        'cliFlags': {'provider': 'openai-codex', 'model': 'gpt-5.6-sol', 'reasoning': 'max', 'toolsets': 'none', 'passSessionId': True, 'resume': False},
        'payload': payload,
        'runtimeDatabaseProbe': db,
        'stdoutSha256': sha(stdout_path.read_bytes()),
        'stderrSha256': sha(stderr_path.read_bytes()),
        'recovery': {
            'salvaged': True,
            'reason': 'API call and outer JSON were valid; the original local parser incorrectly selected the last nested JSON object.',
            'failureRecord': 'metadata/failures/postblind-contact-attempt-1.json',
        },
    }
    out_path = ROOT / 'adjudication/contact-raw/W23-001.json'
    immutable(out_path, canonical(wrapper))
    failure = {
        'schemaVersion': 1,
        'attempt': 'postblind-contact-attempt-1',
        'recordedAt': now(),
        'stage': 'post-call outer-payload parsing before wrapper serialization',
        'errorType': 'local parser selection error',
        'error': 'fallback decoder selected the final nested object rather than the enclosing valid JSON object',
        'validApiCallsPreserved': 1,
        'validAssetIdsPreserved': [ASSET_ID],
        'sessionId': SESSION_ID,
        'sessionRuntime': db,
        'providerCallSucceeded': True,
        'wrapperSalvagedPath': str(out_path.relative_to(ROOT)),
        'wrapperSha256': sha(out_path.read_bytes()),
        'sharedFilesModified': False,
        'immutableBlindEvidenceAffected': False,
        'nextAction': 'Retry only W23-002 through W23-008 in a fresh contact session and fresh output/log directories.',
    }
    immutable(ROOT / 'metadata/failures/postblind-contact-attempt-1.json', canonical(failure))
    segment = {
        'schemaVersion': 1,
        'phase': 'post-blind-authoritative-contact-adjudication',
        'segment': 1,
        'sessionId': SESSION_ID,
        'assetIds': [ASSET_ID],
        'apiCallCount': 1,
        'messageCount': 2,
        'toolCallCount': 0,
        'provider': 'openai-codex',
        'model': 'gpt-5.6-sol',
        'reasoningEffort': 'max',
        'wrapperPath': str(out_path.relative_to(REPO)),
        'wrapperSha256': sha(out_path.read_bytes()),
        'recoveryApplied': True,
    }
    immutable(ROOT / 'metadata/postblind-contact-session-segment-01.json', canonical(segment))
    print(json.dumps({'status': 'salvaged', 'assetId': ASSET_ID, 'sessionId': SESSION_ID, 'wrapperSha256': sha(out_path.read_bytes())}))


if __name__ == '__main__':
    main()
