#!/usr/bin/env python3
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import subprocess
from typing import Any

from PIL import Image

REPO = Path('/home/smithers/projects/nemesis-card-corpus/repos/nemesis-retaliation').resolve()
ROOT = REPO / 'assets/tts-mod/extract/vision-workers/sol-max-persistent-worker-23-20260820T185027Z-p240642-4513b3'
STATE_DB = Path('/home/smithers/.hermes/state.db')
MODEL = {'provider': 'openai-codex', 'model': 'gpt-5.6-sol', 'reasoningEffort': 'max'}
IDS = [f'W23-{i:03d}' for i in range(1, 9)]
ANSI_RE = re.compile(r'\x1b\[[0-?]*[ -/]*[@-~]')


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(obj: Any) -> bytes:
    return (json.dumps(obj, indent=2, ensure_ascii=False) + '\n').encode()


def write_immutable(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise RuntimeError(f'refuse overwrite: {path}')
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_bytes(data)
    os.chmod(tmp, 0o400)
    os.replace(tmp, path)


def parse_json(text: str) -> dict[str, Any]:
    clean = ANSI_RE.sub('', text).strip()
    decoder = json.JSONDecoder()
    for idx, ch in enumerate(clean):
        if ch != '{':
            continue
        try:
            value, end = decoder.raw_decode(clean[idx:])
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict) and not clean[idx + end:].strip():
            return value
    raise RuntimeError('stdout was not exactly one JSON object')


def probe(session_id: str, expected_ordinal: int) -> dict[str, Any]:
    con = sqlite3.connect(f'file:{STATE_DB}?mode=ro', uri=True)
    con.row_factory = sqlite3.Row
    row = con.execute('select * from sessions where id=?', (session_id,)).fetchone()
    messages = con.execute('select role, tool_calls from messages where session_id=? order by timestamp, id', (session_id,)).fetchall()
    con.close()
    if row is None:
        raise RuntimeError(f'missing session {session_id}')
    r = dict(row)
    cfg = json.loads(r['model_config']) if r.get('model_config') else {}
    roles = Counter(str(m['role']) for m in messages)
    tool_payloads = [m['tool_calls'] for m in messages if m['tool_calls'] not in (None, '', '[]', '{}')]
    reasoning_cfg: dict[str, Any] = cfg.get('reasoning_config') or {}
    if not isinstance(reasoning_cfg, dict):
        reasoning_cfg = {}
    out = {
        'sessionId': session_id,
        'source': r.get('source'),
        'provider': r.get('billing_provider'),
        'model': r.get('model'),
        'reasoningEffort': cfg.get('reasoning_effort') or cfg.get('reasoning') or cfg.get('reasoningEffort') or reasoning_cfg.get('effort'),
        'apiCallCount': r.get('api_call_count'),
        'messageCount': r.get('message_count'),
        'toolCallCount': r.get('tool_call_count'),
        'messageRoleCounts': dict(roles),
        'nonemptyToolPayloadCount': len(tool_payloads),
    }
    expected_roles = {'user': expected_ordinal, 'assistant': expected_ordinal}
    if not (
        out['source'] == 'tool'
        and out['provider'] == MODEL['provider']
        and out['model'] == MODEL['model']
        and out['reasoningEffort'] == 'max'
        and out['apiCallCount'] == expected_ordinal
        and out['messageCount'] == expected_ordinal * 2
        and out['toolCallCount'] == 0
        and out['messageRoleCounts'] == expected_roles
        and out['nonemptyToolPayloadCount'] == 0
    ):
        raise RuntimeError(f'post-blind session provenance mismatch: {out}')
    return out


def main() -> None:
    assignment_bytes = (ROOT / 'assignment.json').read_bytes()
    assignment = json.loads(assignment_bytes)
    assignment_sha = sha(assignment_bytes)
    frozen_dispatch = json.loads((ROOT / 'supervisor-dispatch.json').read_text(encoding='utf-8'))
    if assignment_sha != frozen_dispatch['assignmentSha256']:
        raise RuntimeError('assignment hash disagrees with frozen supervisor dispatch')
    by_id = {x['assetId']: x for x in assignment['assets']}
    out_dir = ROOT / 'adjudication/bbox-raw-retry-01'
    log_dir = ROOT / 'logs/adjudication-bbox-retry-01'
    if out_dir.exists() and any(out_dir.iterdir()):
        raise RuntimeError('bbox output dir not empty')
    if log_dir.exists() and any(log_dir.iterdir()):
        raise RuntimeError('bbox log dir not empty')
    out_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)
    session_id: str | None = None
    wrappers: list[dict[str, Any]] = []
    for ordinal, asset_id in enumerate(IDS, start=1):
        current_assignment = (ROOT / 'assignment.json').read_bytes()
        if current_assignment != assignment_bytes:
            raise RuntimeError(f'assignment drift before {asset_id}')
        asset = by_id[asset_id]
        source = REPO / asset['sourcePath']
        source_bytes = source.read_bytes()
        if sha(source_bytes) != asset['sourceSha256']:
            raise RuntimeError(f'source drift before {asset_id}')
        blind = json.loads((ROOT / 'isolated-raw-output' / f'{asset_id}.json').read_text(encoding='utf-8'))
        morph = blind['iconMorphology']
        with Image.open(source) as im:
            width, height = im.size
        prompt = (
            'Post-blind pixel-coordinate adjudication only. The blind record is already sealed. '
            'Inspect the attached source image directly and return exactly one JSON object, no Markdown. '
            f'assetId is {asset_id}; original pixel dimensions are {width}x{height}. '
            'For each supplied blind morphology index, locate the described visible occurrence and return a tight '
            'but non-clipping integer bbox [x1,y1,x2,y2] in ORIGINAL image pixels. Preserve indices exactly. '
            'Classify each only as material-icon, non-text-component-graphic, artwork-only-detail, or unresolved. '
            'Do not infer an icon name from rules semantics. If morphology is not separately visible, use bbox null '
            'and explain. False localization is worse than abstention. Required schema: '
            '{"assetId":"...","runtime":{"sessionId":"...","provider":"openai-codex",'
            '"model":"gpt-5.6-sol","reasoningEffort":"max"},"image":{"width":N,"height":N},'
            '"occurrences":[{"sourceIconMorphologyIndex":0,"bbox":[x1,y1,x2,y2] or null,'
            '"category":"...","pixelBasis":"..."}],"occurrenceCount":N}. '
            'Blind morphologies, indexed in order: ' + json.dumps([
                {
                    'sourceIconMorphologyIndex': i,
                    'location': m.get('location'),
                    'outerShape': m.get('outerShape'),
                    'internalMarks': m.get('internalMarks'),
                    'colors': m.get('colors'),
                    'neighboringText': m.get('neighboringText'),
                }
                for i, m in enumerate(morph)
            ], ensure_ascii=False)
        )
        cmd = [
            'hermes', 'chat', '-Q',
            '--provider', MODEL['provider'], '-m', MODEL['model'], '--reasoning', 'max',
            '--max-turns', '4', '--toolsets', 'none', '--pass-session-id', '--source', 'tool',
            '--ignore-rules', '--in', str(ROOT),
        ]
        if session_id is not None:
            cmd.extend(['--resume', session_id, '--no-restore-cwd'])
        cmd.extend(['--image', str(source), '-q', prompt])
        env = os.environ.copy()
        env['HERMES_SKIP_CLI_UPDATE_CHECK'] = '1'
        started = now()
        proc = subprocess.run(cmd, cwd=str(ROOT), env=env, text=True, capture_output=True, timeout=1200)
        ended = now()
        write_immutable(log_dir / f'{asset_id}.stdout.log', proc.stdout.encode())
        write_immutable(log_dir / f'{asset_id}.stderr.log', proc.stderr.encode())
        if proc.returncode != 0:
            raise RuntimeError(f'{asset_id} bbox call failed rc={proc.returncode}')
        payload = parse_json(proc.stdout)
        if payload.get('assetId') != asset_id:
            raise RuntimeError(f'{asset_id} returned wrong assetId')
        rt = payload.get('runtime') or {}
        returned_sid = rt.get('sessionId')
        if not isinstance(returned_sid, str) or not returned_sid:
            raise RuntimeError(f'{asset_id} missing sessionId')
        if session_id is None:
            session_id = returned_sid
        elif returned_sid != session_id:
            raise RuntimeError(f'{asset_id} changed session')
        if (rt.get('provider'), rt.get('model'), rt.get('reasoningEffort')) != ('openai-codex', 'gpt-5.6-sol', 'max'):
            raise RuntimeError(f'{asset_id} runtime echo mismatch')
        if payload.get('image') != {'width': width, 'height': height}:
            raise RuntimeError(f'{asset_id} image dimensions mismatch')
        occ = payload.get('occurrences')
        if not isinstance(occ, list) or len(occ) != len(morph) or payload.get('occurrenceCount') != len(morph):
            raise RuntimeError(f'{asset_id} occurrence count mismatch')
        if [x.get('sourceIconMorphologyIndex') for x in occ] != list(range(len(morph))):
            raise RuntimeError(f'{asset_id} occurrence indices mismatch')
        for item in occ:
            bbox = item.get('bbox')
            if bbox is not None:
                if not (isinstance(bbox, list) and len(bbox) == 4 and all(isinstance(v, int) for v in bbox)):
                    raise RuntimeError(f'{asset_id} invalid bbox')
                x1, y1, x2, y2 = bbox
                if not (0 <= x1 < x2 <= width and 0 <= y1 < y2 <= height):
                    raise RuntimeError(f'{asset_id} bbox out of range: {bbox}')
        db = probe(session_id, ordinal)
        wrapper = {
            'schemaVersion': 1,
            'assetId': asset_id,
            'phase': 'post-blind-bbox-adjudication',
            'sourcePath': asset['sourcePath'],
            'sourceSha256': asset['sourceSha256'],
            'assignmentSha256': assignment_sha,
            'startedAt': started,
            'endedAt': ended,
            'commandRoute': 'direct-hermes-chat-native-image',
            'cliFlags': {'provider': 'openai-codex', 'model': 'gpt-5.6-sol', 'reasoning': 'max', 'toolsets': 'none', 'passSessionId': True, 'resume': ordinal > 1},
            'payload': payload,
            'runtimeDatabaseProbe': db,
            'stdoutSha256': sha(proc.stdout.encode()),
            'stderrSha256': sha(proc.stderr.encode()),
        }
        write_immutable(out_dir / f'{asset_id}.json', canonical(wrapper))
        wrappers.append(wrapper)
        print(f'{asset_id} bbox sealed session={session_id} api={ordinal}/8', flush=True)
    summary = {
        'schemaVersion': 1,
        'phase': 'post-blind-bbox-adjudication',
        'completedAt': now(),
        'sessionId': session_id,
        'assetCount': len(wrappers),
        'apiCallCount': 8,
        'messageCount': 16,
        'toolCallCount': 0,
        'provider': 'openai-codex',
        'model': 'gpt-5.6-sol',
        'reasoningEffort': 'max',
        'wrapperPaths': [str((out_dir / f'{x["assetId"]}.json').relative_to(REPO)) for x in wrappers],
    }
    write_immutable(ROOT / 'metadata/postblind-bbox-session-retry-01.json', canonical(summary))
    print(json.dumps(summary))


if __name__ == '__main__':
    main()
