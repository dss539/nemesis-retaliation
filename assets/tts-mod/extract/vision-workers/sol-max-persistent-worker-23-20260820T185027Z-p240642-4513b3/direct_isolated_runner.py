#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sqlite3
import subprocess
import sys
from typing import Any

from PIL import Image

REPO = Path('/home/smithers/projects/nemesis-card-corpus/repos/nemesis-retaliation')
ROOT = Path(__file__).resolve().parent
ASSIGNMENT = ROOT / 'assignment.json'
IMMUTABLE_ASSIGNMENT = ROOT / 'assignment.immutable.json'
STATE_DB = Path('/home/smithers/.hermes/state.db')
ANSI_RE = re.compile(r'\x1b\[[0-?]*[ -/]*[@-~]')
EXPECTED_IDS = [f'W23-{index:03d}' for index in range(1, 9)]
MODEL = {'provider': 'openai-codex', 'model': 'gpt-5.6-sol', 'reasoningEffort': 'max'}


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def atomic_json(path: Path, value: Any) -> None:
    atomic_bytes(path, (json.dumps(value, indent=2, ensure_ascii=False) + '\n').encode('utf-8'))


def atomic_bytes(path: Path, data: bytes, *, immutable: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if immutable and path.exists():
        raise FileExistsError(f'immutable target already exists: {path}')
    tmp = path.with_name(path.name + f'.tmp-{os.getpid()}')
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    fd = os.open(tmp, flags, 0o600)
    try:
        view = memoryview(data)
        while view:
            written = os.write(fd, view)
            view = view[written:]
        os.fsync(fd)
    finally:
        os.close(fd)
    os.replace(tmp, path)
    if immutable:
        os.chmod(path, 0o400)
    directory_fd = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(directory_fd)
    finally:
        os.close(directory_fd)


def parse_payload(text: str, asset_id: str) -> dict[str, Any]:
    clean = ANSI_RE.sub('', text)
    decoder = json.JSONDecoder()
    parsed_count = 0
    for index, character in enumerate(clean):
        if character != '{':
            continue
        try:
            value, _ = decoder.raw_decode(clean[index:])
        except Exception:
            continue
        if isinstance(value, dict):
            parsed_count += 1
            if value.get('assetId') == asset_id:
                return value
    raise ValueError(f'no JSON object for {asset_id}; parsed objects={parsed_count}')


def prompt(asset_id: str) -> str:
    schema = {
        'assetId': asset_id,
        'runtime': {
            'sessionId': '<exact session ID supplied in system context>',
            'provider': 'openai-codex',
            'model': 'gpt-5.6-sol',
            'reasoningEffort': 'max',
        },
        'orientation': {'observed': 'upright|rotated', 'rotationRequired': False, 'basis': ''},
        'blindPixelObservations': [''],
        'visibleText': {
            'title': '',
            'typeLine': '',
            'body': '',
            'sections': [],
            'footer': '',
            'upperRight': '',
            'lowerCenter': '',
            'illegibleSpans': [],
            'clippedSpans': [],
        },
        'iconMorphology': [{
            'location': '',
            'outerShape': '',
            'internalMarks': '',
            'colors': [],
            'neighboringText': '',
            'closestPlausibleAlternative': '',
            'visibleDiscriminator': '',
            'semanticIdentityEstablished': False,
        }],
        'proposedClassification': {'componentFamily': '', 'componentType': '', 'basisFromPixelsOnly': ''},
        'readConfidence': {'materialText': '', 'punctuation': '', 'iconMorphology': ''},
        'classificationConfidence': {'componentFamily': '', 'exactComponent': ''},
        'uncertainties': [''],
        'preliminaryDecision': 'defer',
    }
    return (
        'You are a clean blind pixel reader in one persistent native-image session. You have no tools. '
        'Inspect only the single attached image. Do not use repository knowledge, metadata, filenames, folders, game knowledge, expected logic, previous images, or previous replies as evidence. '
        f'The stable asset ID for this turn is {asset_id}. '
        'Record layout and pixel morphology before interpretation, then transcribe every material printed word and punctuation exactly. Preserve meaningful panel/line structure. '
        'For each apparent functional symbol, state location, outer silhouette, internal marks, colors, neighboring printed text, closest plausible alternative, and one visible discriminator. '
        'Do not assign a semantic/canonical icon name from context; use a literal [ICON: ...] description unless a printed label in this image establishes it. '
        'Use [illegible] or [clipped] instead of completion. Keep read confidence, classification confidence, uncertainties, and preliminary decision separate. '
        'False promotion is worse than deferral; ambiguity is correct. Return exactly one JSON object, no Markdown or commentary, matching this shape: '
        + json.dumps(schema, ensure_ascii=False)
    )


def parse_jsonish(value: Any) -> Any:
    if isinstance(value, (dict, list)):
        return value
    if not value:
        return None
    try:
        return json.loads(value)
    except Exception:
        return None


def reasoning_effort(config: dict[str, Any]) -> Any:
    nested = config.get('reasoning_config')
    return (
        config.get('reasoning_effort')
        or config.get('reasoning')
        or (nested.get('effort') if isinstance(nested, dict) else None)
    )


def session_probe(session_id: str) -> dict[str, Any]:
    con = sqlite3.connect(f'file:{STATE_DB}?mode=ro', uri=True)
    con.row_factory = sqlite3.Row
    row = con.execute(
        'select id, source, model, model_config, billing_provider, message_count, tool_call_count, api_call_count, cwd, parent_session_id from sessions where id=?',
        (session_id,),
    ).fetchone()
    con.close()
    if row is None:
        raise RuntimeError(f'session {session_id} not found in read-only state DB')
    result = dict(row)
    result['model_config'] = parse_jsonish(result.get('model_config')) or {}
    result['reasoningEffortObserved'] = reasoning_effort(result['model_config'])
    return result


def image_probe(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    with Image.open(path) as image:
        image.verify()
    with Image.open(path) as image:
        return {
            'width': image.width,
            'height': image.height,
            'format': image.format,
            'mode': image.mode,
            'frames': getattr(image, 'n_frames', 1),
            'bytes': len(data),
            'decode': True,
        }


def unique_failure(stage: str, value: dict[str, Any]) -> None:
    directory = ROOT / 'metadata/failures'
    directory.mkdir(parents=True, exist_ok=True)
    attempt = 1
    while (directory / f'{stage}-attempt-{attempt:02d}.json').exists():
        attempt += 1
    atomic_json(directory / f'{stage}-attempt-{attempt:02d}.json', value)


def run() -> int:
    assignment_bytes = ASSIGNMENT.read_bytes()
    if assignment_bytes != IMMUTABLE_ASSIGNMENT.read_bytes():
        raise RuntimeError('assignment differs from immutable copy before dispatch')
    assignment = json.loads(assignment_bytes)
    assets = assignment.get('assets')
    if assignment.get('workerId') != ROOT.name:
        raise RuntimeError('worker ID/root mismatch')
    if assignment.get('model') != MODEL:
        raise RuntimeError('assignment model contract mismatch')
    if not isinstance(assets, list) or [item.get('assetId') for item in assets] != EXPECTED_IDS:
        raise RuntimeError('assignment stable ID/count/order mismatch')
    for directory in ['sealed-clean-raw', 'isolated-raw-output', 'logs/blind']:
        path = ROOT / directory
        if path.exists() and any(path.iterdir()):
            raise RuntimeError(f'fresh blind output directory is not empty: {directory}')
        path.mkdir(parents=True, exist_ok=True)
    preflight = json.loads((ROOT / 'metadata/preflight.json').read_text(encoding='utf-8'))
    if not all(preflight.get('checks', {}).values()):
        raise RuntimeError('metadata preflight is not fully passed')
    if not json.loads((ROOT / 'metadata/baseline-validation.json').read_text(encoding='utf-8')).get('overallPassed'):
        raise RuntimeError('baseline validation is not passed')
    smoke = json.loads((ROOT / 'metadata/smoke-audit.json').read_text(encoding='utf-8'))
    if not smoke.get('overallPassed') or smoke.get('session', {}).get('toolCallCount') != 0:
        raise RuntimeError('neutral zero-tool smoke audit is not passed')

    state: dict[str, Any] = {
        'schemaVersion': 1,
        'workerId': ROOT.name,
        'startedAt': now(),
        'status': 'running',
        'assignmentSha256': sha_bytes(assignment_bytes),
        'immutableAssignmentSha256': sha(IMMUTABLE_ASSIGNMENT),
        'sessionId': None,
        'requestedRuntime': MODEL,
        'toolsDisabled': True,
        'assets': [],
    }
    atomic_json(ROOT / 'metadata/isolated-blind-dispatch.json', state)
    supervisor_dispatch = {
        'schemaVersion': 1,
        'workerId': ROOT.name,
        'dispatchedAt': state['startedAt'],
        'assignmentSha256': state['assignmentSha256'],
        'orderedTupleDigest': preflight['evidence']['orderedTupleDigest'],
        'orderedAssetIds': EXPECTED_IDS,
        'route': 'direct hermes chat --image, persistent --resume session, tools disabled',
        'model': MODEL,
        'zeroToolSmoke': {
            'sessionId': smoke['session']['sessionId'],
            'auditPath': 'metadata/smoke-audit.json',
            'auditSha256': sha(ROOT / 'metadata/smoke-audit.json'),
            'apiCallCount': smoke['session']['apiCallCount'],
            'messageCount': smoke['session']['messageCount'],
            'toolCallCount': smoke['session']['toolCallCount'],
        },
        'semanticInputAllowedBeforeReaderExit': ['stable asset ID', 'native image pixels'],
    }
    atomic_bytes(
        ROOT / 'supervisor-dispatch.json',
        (json.dumps(supervisor_dispatch, indent=2, ensure_ascii=False) + '\n').encode('utf-8'),
        immutable=True,
    )

    session_id: str | None = None
    env = os.environ.copy()
    env['HERMES_SKIP_CLI_UPDATE_CHECK'] = '1'
    for ordinal, asset in enumerate(assets, 1):
        live_assignment_bytes = ASSIGNMENT.read_bytes()
        if live_assignment_bytes != assignment_bytes or live_assignment_bytes != IMMUTABLE_ASSIGNMENT.read_bytes():
            raise RuntimeError(f'assignment drift before turn {ordinal}')
        asset_id = asset['assetId']
        source = REPO / asset['sourcePath']
        observed_sha = sha(source)
        observed_meta = image_probe(source)
        if observed_sha != asset['sourceSha256'] or observed_meta != asset['sourceMetadata']:
            raise RuntimeError(f'{asset_id}: source tuple/metadata drift before attachment')
        command = [
            'hermes', 'chat', '-Q',
            '--provider', 'openai-codex',
            '-m', 'gpt-5.6-sol',
            '--reasoning', 'max',
            '--max-turns', '4',
            '--toolsets', 'none',
            '--pass-session-id',
            '--source', 'tool',
            '--ignore-rules',
            '--in', str(ROOT),
        ]
        if session_id is not None:
            command += ['--resume', session_id, '--no-restore-cwd']
        command += ['--image', str(source), '-q', prompt(asset_id)]
        started_at = now()
        proc = subprocess.run(
            command,
            cwd=ROOT,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=1200,
        )
        log_base = ROOT / 'logs/blind' / f'{asset_id}-clean-blind'
        log_base.with_suffix('.stdout.txt').write_text(proc.stdout, encoding='utf-8')
        log_base.with_suffix('.stderr.txt').write_text(proc.stderr, encoding='utf-8')
        if proc.returncode:
            raise RuntimeError(f'{asset_id}: hermes chat exit {proc.returncode}; stderr tail={proc.stderr[-2000:]}')
        payload = parse_payload(proc.stdout, asset_id)
        runtime = payload.get('runtime')
        if not isinstance(runtime, dict):
            raise RuntimeError(f'{asset_id}: runtime payload is not an object')
        returned_session = runtime.get('sessionId')
        if not isinstance(returned_session, str) or not returned_session:
            raise RuntimeError(f'{asset_id}: returned session ID missing')
        if session_id is None:
            session_id = returned_session
            state['sessionId'] = session_id
        if returned_session != session_id:
            raise RuntimeError(f'{asset_id}: persistent session changed')
        for key, expected in MODEL.items():
            if runtime.get(key) != expected:
                raise RuntimeError(f'{asset_id}: runtime echo mismatch for {key}')
        probe = session_probe(session_id)
        if probe.get('model') != MODEL['model']:
            raise RuntimeError(f'{asset_id}: DB model mismatch')
        if probe.get('billing_provider') != MODEL['provider']:
            raise RuntimeError(f'{asset_id}: DB provider mismatch: {probe.get("billing_provider")!r}')
        if probe.get('reasoningEffortObserved') != MODEL['reasoningEffort']:
            raise RuntimeError(f'{asset_id}: DB reasoning mismatch: {probe.get("reasoningEffortObserved")!r}')
        if probe.get('tool_call_count') != 0:
            raise RuntimeError(f'{asset_id}: isolated session used tools')
        if probe.get('api_call_count') != ordinal or probe.get('message_count') != ordinal * 2:
            raise RuntimeError(f'{asset_id}: session API/message count mismatch')
        read_at = now()
        wrapper = {
            'schemaVersion': 1,
            'recordType': 'blindNativePixelReadOriginalWrapper',
            'assetId': asset_id,
            'batchId': 'W23-clean-blind-persistent-01',
            'assignmentIndex': asset['assignmentIndex'],
            'sourcePath': asset['sourcePath'],
            'sourceSha256': asset['sourceSha256'],
            'sourceMetadata': observed_meta,
            'readAt': read_at,
            'runtime': runtime,
            'runtimeDatabaseProbe': probe,
            'attachment': {
                'mechanism': 'hermes chat native --image attachment in one isolated persistent tool-disabled session',
                'exactSourcePathUsed': str(source.resolve()),
                'submittedAssetIds': [asset_id],
                'returnedAssetIds': [asset_id],
                'submittedCount': 1,
                'returnedCount': 1,
                'countReconciled': True,
                'oneImageExceptionReason': 'Focused one-image turns preserve clean tuple-level attachment auditing while one persistent session is resumed for all eight assets.',
            },
            'modelOutput': payload,
        }
        wrapper_bytes = (json.dumps(wrapper, indent=2, ensure_ascii=False) + '\n').encode('utf-8')
        sealed_path = ROOT / 'sealed-clean-raw' / f'{asset_id}.json'
        atomic_bytes(sealed_path, wrapper_bytes, immutable=True)
        sealed_sha = sha(sealed_path)
        if sealed_sha != sha_bytes(wrapper_bytes) or (sealed_path.stat().st_mode & 0o777) != 0o400:
            raise RuntimeError(f'{asset_id}: immutable sealed wrapper verification failed')
        payload_path = ROOT / 'isolated-raw-output' / f'{asset_id}.json'
        atomic_bytes(payload_path, (json.dumps(payload, indent=2, ensure_ascii=False) + '\n').encode('utf-8'), immutable=True)
        state['assets'].append({
            'assetId': asset_id,
            'assignmentIndex': asset['assignmentIndex'],
            'sourcePath': asset['sourcePath'],
            'sourceSha256': asset['sourceSha256'],
            'startedAt': started_at,
            'completedAt': read_at,
            'returnedSessionId': session_id,
            'sealedRawWrapperPath': str(sealed_path.relative_to(ROOT)),
            'sealedRawWrapperSha256': sealed_sha,
            'sealedRawWrapperMode': '0400',
            'isolatedPayloadPath': str(payload_path.relative_to(ROOT)),
            'isolatedPayloadSha256': sha(payload_path),
            'databaseProbe': probe,
        })
        atomic_json(ROOT / 'metadata/isolated-blind-dispatch.json', state)
        print(f'{asset_id} sealed session={session_id} api={ordinal}/8', flush=True)
    state['status'] = 'completed'
    state['completedAt'] = now()
    state['sealedWrapperCount'] = len(state['assets'])
    state['allWrappersMode0400'] = all((ROOT / item['sealedRawWrapperPath']).stat().st_mode & 0o777 == 0o400 for item in state['assets'])
    atomic_json(ROOT / 'metadata/isolated-blind-dispatch.json', state)
    print(json.dumps({
        'status': state['status'],
        'sessionId': session_id,
        'assetCount': len(state['assets']),
        'apiCallCount': state['assets'][-1]['databaseProbe']['api_call_count'],
        'toolCallCount': state['assets'][-1]['databaseProbe']['tool_call_count'],
        'messageCount': state['assets'][-1]['databaseProbe']['message_count'],
        'sealedWrapperCount': state['sealedWrapperCount'],
        'allWrappersMode0400': state['allWrappersMode0400'],
    }))
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(run())
    except Exception as exc:
        failure = {
            'schemaVersion': 1,
            'failedAt': now(),
            'stage': 'isolated-blind-runner',
            'errorType': type(exc).__name__,
            'error': str(exc),
        }
        unique_failure('isolated-blind-runner', failure)
        print(json.dumps(failure), file=sys.stderr)
        raise
