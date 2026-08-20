#!/usr/bin/env python3
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import sys
from typing import Any

REPO = Path('/home/smithers/projects/nemesis-card-corpus/repos/nemesis-retaliation')
ROOT = Path(__file__).resolve().parent
STATE_DB = Path('/home/smithers/.hermes/state.db')
EXPECTED_IDS = [f'W23-{index:03d}' for index in range(1, 9)]
MODEL = {'provider': 'openai-codex', 'model': 'gpt-5.6-sol', 'reasoningEffort': 'max'}
EXPECTED_PAYLOAD_KEYS = {
    'assetId', 'runtime', 'orientation', 'blindPixelObservations', 'visibleText',
    'iconMorphology', 'proposedClassification', 'readConfidence',
    'classificationConfidence', 'uncertainties', 'preliminaryDecision',
}
EXPECTED_ORIENTATION_KEYS = {'observed', 'rotationRequired', 'basis'}


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    os.replace(tmp, path)


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def parse_jsonish(value: Any) -> Any:
    if isinstance(value, (dict, list)):
        return value
    if not value:
        return None
    try:
        return json.loads(value)
    except Exception:
        return None


def parse_calls(value: Any) -> list[dict[str, Any]]:
    parsed = parse_jsonish(value)
    if not parsed:
        return []
    return parsed if isinstance(parsed, list) else [parsed]


def reasoning_effort(config: dict[str, Any]) -> Any:
    nested = config.get('reasoning_config')
    return (
        config.get('reasoning_effort')
        or config.get('reasoning')
        or (nested.get('effort') if isinstance(nested, dict) else None)
    )


def unique_failure(value: dict[str, Any]) -> None:
    directory = ROOT / 'metadata/failures'
    directory.mkdir(parents=True, exist_ok=True)
    attempt = 1
    while (directory / f'blind-seal-audit-attempt-{attempt:02d}.json').exists():
        attempt += 1
    atomic_json(directory / f'blind-seal-audit-attempt-{attempt:02d}.json', value)


def run() -> None:
    assignment_bytes = (ROOT / 'assignment.json').read_bytes()
    immutable_assignment_bytes = (ROOT / 'assignment.immutable.json').read_bytes()
    if assignment_bytes != immutable_assignment_bytes:
        raise RuntimeError('assignment immutable-copy mismatch')
    assignment = json.loads(assignment_bytes)
    assets = assignment['assets']
    if [item['assetId'] for item in assets] != EXPECTED_IDS:
        raise RuntimeError('assignment stable IDs/order mismatch')
    dispatch = load(ROOT / 'metadata/isolated-blind-dispatch.json')
    if dispatch.get('status') != 'completed' or dispatch.get('sealedWrapperCount') != 8:
        raise RuntimeError('blind dispatch is not completed with eight wrappers')
    session_id = dispatch.get('sessionId')
    if not isinstance(session_id, str) or not session_id:
        raise RuntimeError('dispatch session ID missing')
    dispatch_by_id = {item['assetId']: item for item in dispatch['assets']}

    wrappers: list[dict[str, Any]] = []
    payloads: list[dict[str, Any]] = []
    for ordinal, asset in enumerate(assets, 1):
        asset_id = asset['assetId']
        path = ROOT / 'sealed-clean-raw' / f'{asset_id}.json'
        if not path.is_file() or path.is_symlink():
            raise RuntimeError(f'{asset_id}: sealed wrapper missing/nonregular')
        mode = path.stat().st_mode & 0o777
        if mode != 0o400:
            raise RuntimeError(f'{asset_id}: sealed wrapper mode is {mode:o}, expected 400')
        data = path.read_bytes()
        wrapper = json.loads(data)
        payload = wrapper.get('modelOutput')
        if not isinstance(payload, dict):
            raise RuntimeError(f'{asset_id}: modelOutput is not an object')
        if set(payload) != EXPECTED_PAYLOAD_KEYS:
            raise RuntimeError(f'{asset_id}: payload keys drift: {sorted(payload)}')
        orientation = payload.get('orientation')
        if not isinstance(orientation, dict) or set(orientation) != EXPECTED_ORIENTATION_KEYS:
            raise RuntimeError(f'{asset_id}: orientation keys drift: {sorted(orientation) if isinstance(orientation, dict) else type(orientation).__name__}')
        if wrapper.get('readAt') is None:
            raise RuntimeError(f'{asset_id}: original wrapper readAt missing')
        if (
            wrapper.get('assetId') != asset_id
            or wrapper.get('assignmentIndex') != asset['assignmentIndex']
            or wrapper.get('sourcePath') != asset['sourcePath']
            or wrapper.get('sourceSha256') != asset['sourceSha256']
            or wrapper.get('sourceMetadata') != asset['sourceMetadata']
        ):
            raise RuntimeError(f'{asset_id}: wrapper tuple/metadata mismatch')
        runtime = payload.get('runtime')
        if runtime != {**MODEL, 'sessionId': session_id}:
            raise RuntimeError(f'{asset_id}: payload runtime mismatch')
        attachment = wrapper.get('attachment') or {}
        if (
            attachment.get('submittedAssetIds') != [asset_id]
            or attachment.get('returnedAssetIds') != [asset_id]
            or attachment.get('submittedCount') != 1
            or attachment.get('returnedCount') != 1
            or attachment.get('countReconciled') is not True
        ):
            raise RuntimeError(f'{asset_id}: attachment reconciliation mismatch')
        row = dispatch_by_id.get(asset_id)
        if not row or row.get('sealedRawWrapperSha256') != sha_bytes(data):
            raise RuntimeError(f'{asset_id}: dispatch wrapper hash mismatch')
        probe = wrapper.get('runtimeDatabaseProbe') or {}
        if (
            probe.get('id') != session_id
            or probe.get('model') != MODEL['model']
            or probe.get('billing_provider') != MODEL['provider']
            or probe.get('reasoningEffortObserved') != 'max'
            or probe.get('api_call_count') != ordinal
            or probe.get('message_count') != ordinal * 2
            or probe.get('tool_call_count') != 0
        ):
            raise RuntimeError(f'{asset_id}: incremental DB probe mismatch')
        wrappers.append({
            'assetId': asset_id,
            'path': str(path.relative_to(ROOT)),
            'sha256': sha_bytes(data),
            'bytes': len(data),
            'mode': '0400',
            'readAtPresent': True,
            'payloadKeys': sorted(payload),
            'orientationKeys': sorted(orientation),
            'incrementalApiCallCount': ordinal,
            'incrementalMessageCount': ordinal * 2,
            'incrementalToolCallCount': 0,
        })
        payloads.append(payload)

    if len(list((ROOT / 'sealed-clean-raw').glob('*.json'))) != 8:
        raise RuntimeError('sealed wrapper directory contains an unexpected JSON count')

    con = sqlite3.connect(f'file:{STATE_DB}?mode=ro', uri=True)
    con.row_factory = sqlite3.Row
    session = con.execute(
        'select id, source, model, model_config, billing_provider, message_count, tool_call_count, api_call_count, cwd, parent_session_id from sessions where id=?',
        (session_id,),
    ).fetchone()
    if session is None:
        raise RuntimeError('blind session missing from state DB')
    session_row = dict(session)
    config = parse_jsonish(session_row.get('model_config')) or {}
    messages = [dict(row) for row in con.execute(
        'select id, role, tool_name, tool_call_id, tool_calls, content from messages where session_id=? order by id',
        (session_id,),
    ).fetchall()]
    con.close()
    roles = Counter(message['role'] for message in messages)
    if (
        session_row.get('model') != MODEL['model']
        or session_row.get('billing_provider') != MODEL['provider']
        or reasoning_effort(config) != 'max'
        or session_row.get('message_count') != 16
        or session_row.get('api_call_count') != 8
        or session_row.get('tool_call_count') != 0
        or roles != Counter({'user': 8, 'assistant': 8})
    ):
        raise RuntimeError('final session identity/count/role audit mismatch')
    if any(parse_calls(message.get('tool_calls')) for message in messages):
        raise RuntimeError('session message rows contain tool calls')
    assistant_payloads = []
    for message in messages:
        if message['role'] != 'assistant':
            continue
        parsed = parse_jsonish(message.get('content'))
        if not isinstance(parsed, dict):
            raise RuntimeError(f'assistant message {message["id"]} is not exact JSON')
        assistant_payloads.append(parsed)
    if [item.get('assetId') for item in assistant_payloads] != EXPECTED_IDS:
        raise RuntimeError('assistant stable IDs/order mismatch')
    if assistant_payloads != payloads:
        raise RuntimeError('session assistant payloads differ from sealed wrappers')

    assignment_sha = sha_bytes(assignment_bytes)
    tuple_digest = sha_bytes(json.dumps([
        [item['assetId'], item['sourcePath'], item['sourceSha256']]
        for item in assets
    ], separators=(',', ':')).encode())
    preservation = {
        'schemaVersion': 1,
        'recordedAt': now(),
        'workerId': ROOT.name,
        'assignmentSha256': assignment_sha,
        'orderedTupleDigest': tuple_digest,
        'records': wrappers,
        'exactPreservedCount': len(wrappers),
        'disclosedWrapperLossCount': 0,
        'originalWrappersNeverNormalized': True,
        'originalWrappersImmutableMode': '0400',
        'allReadAtTimestampsPreserved': True,
        'overallPassed': True,
    }
    atomic_json(ROOT / 'metadata/raw-wrapper-preservation.json', preservation)
    audit = {
        'schemaVersion': 1,
        'recordedAt': now(),
        'workerId': ROOT.name,
        'session': {
            'sessionId': session_id,
            'source': session_row.get('source'),
            'model': session_row.get('model'),
            'billingProvider': session_row.get('billing_provider'),
            'reasoningEffort': reasoning_effort(config),
            'messageCount': session_row.get('message_count'),
            'apiCallCount': session_row.get('api_call_count'),
            'toolCallCount': session_row.get('tool_call_count'),
            'cwd': session_row.get('cwd'),
            'parentSessionId': session_row.get('parent_session_id'),
        },
        'messageRoleCounts': dict(roles),
        'returnedAssetIds': [item['assetId'] for item in assistant_payloads],
        'payloadSchema': {
            'topLevelKeys': sorted(EXPECTED_PAYLOAD_KEYS),
            'orientationKeys': sorted(EXPECTED_ORIENTATION_KEYS),
        },
        'checks': {
            'modelProviderMatched': True,
            'reasoningMaxFromModelConfig': True,
            'onePersistentSession': True,
            'exactlyEightApiCalls': True,
            'exactlySixteenMessages': True,
            'zeroToolCalls': True,
            'stableIdsAndOrderMatched': True,
            'sessionPayloadsEqualSealedWrappers': True,
            'eightWrappersMode0400': True,
            'allOriginalReadAtTimestampsPreserved': True,
            'assignmentAndSourcesReconciled': True,
        },
        'overallPassed': True,
    }
    atomic_json(ROOT / 'metadata/direct-session-audit.json', audit)
    print(json.dumps({
        'overallPassed': True,
        'session': audit['session'],
        'messageRoleCounts': audit['messageRoleCounts'],
        'returnedAssetIds': audit['returnedAssetIds'],
        'sealedWrapperCount': preservation['exactPreservedCount'],
        'wrapperLossCount': preservation['disclosedWrapperLossCount'],
        'allReadAtTimestampsPreserved': preservation['allReadAtTimestampsPreserved'],
        'assignmentSha256': assignment_sha,
        'orderedTupleDigest': tuple_digest,
        'payloadSchema': audit['payloadSchema'],
    }, indent=2))


if __name__ == '__main__':
    try:
        run()
    except Exception as exc:
        failure = {
            'schemaVersion': 1,
            'recordedAt': now(),
            'stage': 'blind-seal-audit',
            'errorType': type(exc).__name__,
            'error': str(exc),
        }
        unique_failure(failure)
        print(json.dumps(failure, indent=2), file=sys.stderr)
        raise
