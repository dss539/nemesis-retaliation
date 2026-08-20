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
IDS = [f'W23-{i:03d}' for i in range(2, 9)]
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
    first = clean.find('{')
    last = clean.rfind('}')
    if first >= 0 and last > first:
        try:
            whole = json.loads(clean[first:last + 1])
        except json.JSONDecodeError:
            whole = None
        if isinstance(whole, dict):
            return whole
    decoder = json.JSONDecoder()
    objects: list[Any] = []
    for i, ch in enumerate(clean):
        if ch != '{':
            continue
        try:
            obj, _ = decoder.raw_decode(clean[i:])
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict):
            objects.append(obj)
    if not objects:
        raise RuntimeError('no JSON object in stdout')
    return objects[-1]


def probe(session_id: str, ordinal: int) -> dict[str, Any]:
    con = sqlite3.connect(f'file:{STATE_DB}?mode=ro', uri=True)
    con.row_factory = sqlite3.Row
    row = con.execute('select * from sessions where id=?', (session_id,)).fetchone()
    messages = con.execute('select role, tool_calls from messages where session_id=? order by timestamp, id', (session_id,)).fetchall()
    con.close()
    if row is None:
        raise RuntimeError(f'missing session {session_id}')
    r = dict(row)
    cfg = json.loads(r['model_config']) if r.get('model_config') else {}
    reasoning_cfg: dict[str, Any] = cfg.get('reasoning_config') or {}
    if not isinstance(reasoning_cfg, dict):
        reasoning_cfg = {}
    roles = Counter(str(m['role']) for m in messages)
    tool_payloads = [m['tool_calls'] for m in messages if m['tool_calls'] not in (None, '', '[]', '{}')]
    out = {
        'sessionId': session_id,
        'source': r.get('source'),
        'provider': r.get('billing_provider'),
        'model': r.get('model'),
        'reasoningEffort': cfg.get('reasoning_effort') or cfg.get('reasoning') or cfg.get('reasoningEffort') or reasoning_cfg.get('effort'),
        'apiCallCount': r.get('api_call_count'),
        'messageCount': r.get('message_count'),
        'toolCallCount': r.get('tool_call_count'),
        'messageRoles': dict(roles),
        'messageToolPayloadCount': len(tool_payloads),
    }
    expected = {
        'source': 'tool',
        'provider': MODEL['provider'],
        'model': MODEL['model'],
        'reasoningEffort': MODEL['reasoningEffort'],
        'apiCallCount': ordinal,
        'messageCount': ordinal * 2,
        'toolCallCount': 0,
        'messageRoles': {'user': ordinal, 'assistant': ordinal},
        'messageToolPayloadCount': 0,
    }
    for key, value in expected.items():
        if out.get(key) != value:
            raise RuntimeError(f'contact DB mismatch {key}: {out.get(key)!r} != {value!r}')
    return out


def prompt(asset_id: str, index_record: dict[str, Any]) -> str:
    occurrence_summary = [
        {
            'sourceIconMorphologyIndex': x['sourceIconMorphologyIndex'],
            'stagedCategory': x['category'],
            'blindMorphology': x['blindMorphology'],
        }
        for x in index_record['occurrences']
    ]
    official = index_record['officialCounterpart']
    return f'''Post-blind authoritative comparison for stable asset ID {asset_id}.
The attached image is a hash-recorded contact sheet built from: (1) the assigned source image, (2) exact source-occurrence crops sealed after a blind read, (3) current Awaken Realms Objectives Help Sheet pixels when a title counterpart exists, and (4) authoritative p.40 glossary candidates. Do not call tools and do not use unstated repository knowledge.

Evaluate every source morphology occurrence exactly once. Material icons must resolve to either "match" with an exact canonical glossary token, or explicit "no-match" with canonicalToken null. Keep staged non-text component graphics and artwork-only details non-semantic unless pixels falsify that category. For every match/no-match, state pixel observations first, the closest plausible alternative, and one visible discriminator. Surrounding card semantics or filenames cannot substitute for morphology. False promotion is worse than deferral.

Also compare assigned-art operative wording against the visible current official counterpart, if one exists. Preserve assigned text and official text separately; report conflicts, omissions, qualifier/count changes, or unreadable spans verbatim. Do not silently replace assigned wording with official wording. A matching title does not establish source fidelity. If the sheet is insufficient, say so.

Staged occurrence records:
{json.dumps(occurrence_summary, ensure_ascii=False)}
Official counterpart key shown on sheet: {official!r}

Return exactly one JSON object, no Markdown:
{{
  "assetId":"{asset_id}",
  "runtime":{{"sessionId":"exact current session ID","provider":"openai-codex","model":"gpt-5.6-sol","reasoningEffort":"max"}},
  "occurrences":[
    {{
      "sourceIconMorphologyIndex":0,
      "finalCategory":"match|no-match|non-text-component-graphic|artwork-only-detail",
      "canonicalToken":"exact glossary token or null",
      "referenceLabel":"exact visible reference label or null",
      "pixelObservations":"location, outer shape, internal marks, colors",
      "closestAlternative":"...",
      "visibleDiscriminator":"...",
      "uncertainty":"... or none"
    }}
  ],
  "occurrenceCount":{len(occurrence_summary)},
  "sourceFidelity":{{
    "assignedTitle":"exact source title or null",
    "officialCounterpartTitle":"exact visible official title or null",
    "comparisonStatus":"exact-match|material-conflict|no-counterpart|insufficient",
    "assignedOperativeText":"verbatim with [illegible] where needed",
    "officialOperativeText":"verbatim or null",
    "conflicts":["one exact conflict per item"],
    "uncertainties":["one item per uncertainty"]
  }},
  "promotionEvidence":"sufficient|insufficient",
  "promotionEvidenceReason":"pixel-evidence reason only"
}}
Return one row for every index and final occurrenceCount {len(occurrence_summary)}.'''


def main() -> None:
    assignment_bytes = (ROOT / 'assignment.json').read_bytes()
    assignment_sha = sha(assignment_bytes)
    frozen_dispatch = json.loads((ROOT / 'supervisor-dispatch.json').read_text())
    if assignment_sha != frozen_dispatch['assignmentSha256']:
        raise RuntimeError('assignment drift before contact adjudication')
    assignment = json.loads(assignment_bytes)
    by_id = {x['assetId']: x for x in assignment['assets']}
    index_path = ROOT / 'qa/contact-sheets/index.json'
    index_bytes = index_path.read_bytes()
    index_sha = sha(index_bytes)
    index = json.loads(index_bytes)
    index_by_id = {x['assetId']: x for x in index['assets']}
    out_dir = ROOT / 'adjudication/contact-raw-retry-01'
    log_dir = ROOT / 'logs/adjudication-contact-retry-01'
    if out_dir.exists() and any(out_dir.iterdir()):
        raise RuntimeError('contact adjudication output not empty')
    if log_dir.exists() and any(log_dir.iterdir()):
        raise RuntimeError('contact adjudication logs not empty')
    out_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env['HERMES_SKIP_CLI_UPDATE_CHECK'] = '1'
    session_id: str | None = None
    wrappers = []
    for ordinal, asset_id in enumerate(IDS, start=1):
        current_assignment_bytes = (ROOT / 'assignment.json').read_bytes()
        if sha(current_assignment_bytes) != assignment_sha:
            raise RuntimeError(f'assignment drift before {asset_id}')
        current_index_bytes = index_path.read_bytes()
        if sha(current_index_bytes) != index_sha:
            raise RuntimeError(f'contact index drift before {asset_id}')
        asset = by_id[asset_id]
        record = index_by_id[asset_id]
        if record['sourceSha256'] != asset['sourceSha256']:
            raise RuntimeError(f'contact source tuple drift for {asset_id}')
        sheet = REPO / record['contactSheetPath']
        sheet_bytes = sheet.read_bytes()
        if sha(sheet_bytes) != record['contactSheetSha256']:
            raise RuntimeError(f'contact sheet drift for {asset_id}')
        with Image.open(sheet) as im:
            im.verify()
        text = prompt(asset_id, record)
        cmd = [
            'hermes', 'chat', '-Q',
            '--provider', MODEL['provider'], '-m', MODEL['model'], '--reasoning', 'max',
            '--max-turns', '4', '--toolsets', 'none', '--pass-session-id', '--source', 'tool',
            '--ignore-rules', '--in', str(ROOT),
        ]
        if session_id is not None:
            cmd.extend(['--resume', session_id, '--no-restore-cwd'])
        cmd.extend(['--image', str(sheet), '-q', text])
        started = now()
        proc = subprocess.run(cmd, cwd=str(ROOT), env=env, text=True, capture_output=True, timeout=1200)
        ended = now()
        stdout_path = log_dir / f'{asset_id}.stdout.log'
        stderr_path = log_dir / f'{asset_id}.stderr.log'
        write_immutable(stdout_path, proc.stdout.encode())
        write_immutable(stderr_path, proc.stderr.encode())
        if proc.returncode != 0:
            raise RuntimeError(f'{asset_id} contact call failed rc={proc.returncode}; see {stderr_path}')
        payload = parse_json(proc.stdout)
        if payload.get('assetId') != asset_id:
            raise RuntimeError(f'{asset_id} payload ID mismatch')
        runtime = payload.get('runtime') or {}
        observed_sid = runtime.get('sessionId')
        if not isinstance(observed_sid, str) or not observed_sid:
            raise RuntimeError(f'{asset_id} missing session ID')
        if session_id is None:
            session_id = observed_sid
        if observed_sid != session_id:
            raise RuntimeError(f'{asset_id} session drift {observed_sid} != {session_id}')
        if runtime.get('provider') != MODEL['provider'] or runtime.get('model') != MODEL['model'] or runtime.get('reasoningEffort') != 'max':
            raise RuntimeError(f'{asset_id} runtime echo mismatch')
        occurrences = payload.get('occurrences')
        expected_indices = [x['sourceIconMorphologyIndex'] for x in record['occurrences']]
        if not isinstance(occurrences, list) or len(occurrences) != len(expected_indices) or payload.get('occurrenceCount') != len(expected_indices):
            raise RuntimeError(f'{asset_id} occurrence count mismatch')
        got_indices = [x.get('sourceIconMorphologyIndex') for x in occurrences]
        if got_indices != expected_indices:
            raise RuntimeError(f'{asset_id} occurrence order mismatch {got_indices} != {expected_indices}')
        for row in occurrences:
            category = row.get('finalCategory')
            token = row.get('canonicalToken')
            if category not in {'match', 'no-match', 'non-text-component-graphic', 'artwork-only-detail'}:
                raise RuntimeError(f'{asset_id} invalid category {category}')
            if category == 'match' and token not in {'character', 'lander', 'general/character', 'map/lander'}:
                raise RuntimeError(f'{asset_id} invalid matched token {token}')
            if category != 'match' and token is not None:
                raise RuntimeError(f'{asset_id} non-match has token {token}')
        db = probe(session_id, ordinal)
        wrapper = {
            'schemaVersion': 1,
            'assetId': asset_id,
            'phase': 'post-blind-authoritative-contact-adjudication',
            'sourcePath': asset['sourcePath'],
            'sourceSha256': asset['sourceSha256'],
            'assignmentSha256': assignment_sha,
            'contactIndexSha256': index_sha,
            'contactSheetPath': record['contactSheetPath'],
            'contactSheetSha256': record['contactSheetSha256'],
            'startedAt': started,
            'endedAt': ended,
            'commandRoute': 'direct-hermes-chat-native-image',
            'cliFlags': {'provider': MODEL['provider'], 'model': MODEL['model'], 'reasoning': 'max', 'toolsets': 'none', 'passSessionId': True, 'resume': ordinal > 1},
            'payload': payload,
            'runtimeDatabaseProbe': db,
            'stdoutSha256': sha(stdout_path.read_bytes()),
            'stderrSha256': sha(stderr_path.read_bytes()),
        }
        wrapper_path = out_dir / f'{asset_id}.json'
        write_immutable(wrapper_path, canonical(wrapper))
        wrappers.append(wrapper)
        print(f'{asset_id} contact sealed session={session_id} api={ordinal}/7', flush=True)
    summary = {
        'schemaVersion': 1,
        'phase': 'post-blind-authoritative-contact-adjudication',
        'completedAt': now(),
        'sessionId': session_id,
        'assetCount': len(wrappers),
        'apiCallCount': 7,
        'messageCount': 14,
        'toolCallCount': 0,
        'provider': MODEL['provider'],
        'model': MODEL['model'],
        'reasoningEffort': 'max',
        'contactIndexSha256': index_sha,
        'wrapperPaths': [str((out_dir / f'{asset_id}.json').relative_to(REPO)) for asset_id in IDS],
    }
    write_immutable(ROOT / 'metadata/postblind-contact-session-segment-02.json', canonical(summary))
    print(json.dumps(summary))


if __name__ == '__main__':
    main()
