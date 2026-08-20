#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sqlite3
from typing import Any

from PIL import Image
import run_w23_bbox_adjudication as bbox_runner

REPO = Path('/home/smithers/projects/nemesis-card-corpus/repos/nemesis-retaliation').resolve()
ROOT = REPO / 'assets/tts-mod/extract/vision-workers/sol-max-persistent-worker-23-20260820T185027Z-p240642-4513b3'
ASSET_ID = 'W23-001'
SESSION_ID = '20260820_193010_a77e8d'


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
    source = REPO / asset['sourcePath']
    source_bytes = source.read_bytes()
    if sha(source_bytes) != asset['sourceSha256']:
        raise RuntimeError('source drift')
    stdout_path = ROOT / 'logs/adjudication-bbox-retry-01/W23-001.stdout.log'
    stderr_path = ROOT / 'logs/adjudication-bbox-retry-01/W23-001.stderr.log'
    payload = bbox_runner.parse_json(stdout_path.read_text(encoding='utf-8'))
    if payload['assetId'] != ASSET_ID or payload['runtime']['sessionId'] != SESSION_ID:
        raise RuntimeError('salvage payload identity mismatch')
    with Image.open(source) as im:
        expected_image = {'width': im.width, 'height': im.height}
    if payload['image'] != expected_image:
        raise RuntimeError('salvage image dimensions mismatch')
    blind = json.loads((ROOT / 'isolated-raw-output/W23-001.json').read_text())
    if payload['occurrenceCount'] != len(blind['iconMorphology']):
        raise RuntimeError('salvage occurrence count mismatch')
    db = bbox_runner.probe(SESSION_ID, 1)
    con = sqlite3.connect('file:/home/smithers/.hermes/state.db?mode=ro', uri=True)
    rows = con.execute('select role,timestamp from messages where session_id=? order by timestamp,id', (SESSION_ID,)).fetchall()
    con.close()
    if len(rows) != 2:
        raise RuntimeError('unexpected salvage message count')
    wrapper = {
        'schemaVersion': 1,
        'assetId': ASSET_ID,
        'phase': 'post-blind-bbox-adjudication',
        'sourcePath': asset['sourcePath'],
        'sourceSha256': asset['sourceSha256'],
        'assignmentSha256': assignment_sha,
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
            'reason': 'API call and payload validation succeeded before the original wrapper step failed on a local DB timestamp-column query.',
            'failureRecord': 'metadata/failures/postblind-bbox-attempt-3.json',
            'semanticLookupBetweenCallAndSeal': False,
        },
    }
    out_path = ROOT / 'adjudication/bbox-raw-retry-01/W23-001.json'
    immutable(out_path, canonical(wrapper))
    failure = {
        'schemaVersion': 1,
        'attempt': 'postblind-bbox-attempt-3',
        'recordedAt': now(),
        'stage': 'post-call runtime DB probe before wrapper serialization',
        'errorType': 'sqlite3.OperationalError',
        'error': 'no such column: created_at',
        'validApiCallsPreserved': 1,
        'validAssetIdsPreserved': [ASSET_ID],
        'sessionId': SESSION_ID,
        'sessionRuntime': db,
        'providerCallSucceeded': True,
        'wrapperSalvagedPath': str(out_path.relative_to(ROOT)),
        'wrapperSha256': sha(out_path.read_bytes()),
        'wrapperMode': oct(out_path.stat().st_mode & 0o777),
        'sharedFilesModified': False,
        'immutableBlindEvidenceAffected': False,
        'nextAction': 'Retry only W23-002 through W23-008 in a fresh session and fresh output/log directories.',
    }
    immutable(ROOT / 'metadata/failures/postblind-bbox-attempt-3.json', canonical(failure))
    segment = {
        'schemaVersion': 1,
        'phase': 'post-blind-bbox-adjudication',
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
    immutable(ROOT / 'metadata/postblind-bbox-session-segment-01.json', canonical(segment))
    print(json.dumps({'status': 'salvaged', 'assetId': ASSET_ID, 'sessionId': SESSION_ID, 'wrapperSha256': sha(out_path.read_bytes())}))


if __name__ == '__main__':
    main()
