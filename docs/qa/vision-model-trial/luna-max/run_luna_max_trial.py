#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import time

ROOT = Path('/home/smithers/nemesis-retaliation')
TRIAL = ROOT / 'docs/qa/vision-model-trial/luna-max'
SCRATCH = Path('/tmp/nemesis-luna-max-vision-trial')


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def parse_json_object(text: str):
    cleaned = text.strip()
    cleaned = re.sub(r'^```(?:json)?\s*', '', cleaned, flags=re.I)
    cleaned = re.sub(r'\s*```\s*$', '', cleaned)
    start, end = cleaned.find('{'), cleaned.rfind('}')
    if start < 0 or end < start:
        return None, 'no JSON object found'
    try:
        return json.loads(cleaned[start:end + 1]), None
    except Exception as exc:
        return None, str(exc)


def run_case(case, rendered_prompt, force=False):
    runs_dir = TRIAL / 'runs'
    outputs_dir = TRIAL / 'outputs'
    runs_dir.mkdir(parents=True, exist_ok=True)
    outputs_dir.mkdir(parents=True, exist_ok=True)
    run_path = runs_dir / f"{case['id']}.json"
    if run_path.exists() and not force:
        existing = json.loads(run_path.read_text())
        if existing.get('returnCode') == 0 and existing.get('parsedJson'):
            print(f"SKIP {case['id']}: prior successful run exists", flush=True)
            return existing

    source = ROOT / case['source']
    actual_hash = sha256(source)
    if actual_hash != case['sourceSha256']:
        raise RuntimeError(f"{case['id']} source hash drift: {actual_hash}")
    if case.get('goldSidecar'):
        gold = ROOT / case['goldSidecar']
        gold_hash = sha256(gold)
        if gold_hash != case['goldSidecarSha256']:
            raise RuntimeError(f"{case['id']} gold sidecar hash drift: {gold_hash}")

    blind_dir = SCRATCH / case['id']
    blind_dir.mkdir(parents=True, exist_ok=True)
    blind_name = f"input-{case['sourceSha256'][:12]}{source.suffix.lower()}"
    blind_path = blind_dir / blind_name
    if blind_path.exists() or blind_path.is_symlink():
        blind_path.unlink()
    blind_path.symlink_to(source)

    cmd = [
        'hermes', 'chat', '-Q', '--safe-mode',
        '--provider', 'openai-codex',
        '-m', 'gpt-5.6-luna',
        '--reasoning', 'max',
        '--max-turns', '1',
        '--source', 'tool',
        '--in', str(blind_dir),
        '--image', str(blind_path),
        '-q', rendered_prompt,
    ]
    print(f"RUN {case['id']} ({case['tier']})", flush=True)
    started = time.time()
    proc = subprocess.run(cmd, text=True, capture_output=True, timeout=900)
    ended = time.time()
    parsed, parse_error = parse_json_object(proc.stdout)
    session_match = re.search(r'(?:Session ID|session_id)\s*[:=]\s*([A-Za-z0-9_-]+)', proc.stdout + '\n' + proc.stderr, re.I)
    record = {
        'schemaVersion': 1,
        'caseId': case['id'],
        'tier': case['tier'],
        'sourceSha256': actual_hash,
        'provider': 'openai-codex',
        'model': 'gpt-5.6-luna',
        'reasoning': 'max',
        'nativeImageAttachment': True,
        'safeMode': True,
        'promptSha256': hashlib.sha256(rendered_prompt.encode()).hexdigest(),
        'startedAtEpoch': started,
        'endedAtEpoch': ended,
        'durationSeconds': round(ended - started, 3),
        'returnCode': proc.returncode,
        'sessionId': session_match.group(1) if session_match else None,
        'stdout': proc.stdout,
        'stderr': proc.stderr,
        'parsedJson': parsed,
        'parseError': parse_error,
    }
    run_path.write_text(json.dumps(record, indent=2, ensure_ascii=False) + '\n')
    if parsed is not None:
        (outputs_dir / f"{case['id']}.json").write_text(json.dumps(parsed, indent=2, ensure_ascii=False) + '\n')
    print(f"DONE {case['id']}: rc={proc.returncode}, parsed={parsed is not None}, {record['durationSeconds']}s", flush=True)
    return record


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--case', action='append', dest='cases')
    parser.add_argument('--force', action='store_true')
    args = parser.parse_args()

    sample = json.loads((TRIAL / 'sample.json').read_text())
    template = (TRIAL / 'prompt-template.txt').read_text()
    glossary = (ROOT / 'docs/rules/icon-glossary.md').read_text()
    rendered_prompt = template.replace('{{ICON_GLOSSARY}}', glossary)
    (TRIAL / 'rendered-prompt.txt').write_text(rendered_prompt)
    selected = [c for c in sample['cases'] if not args.cases or c['id'] in args.cases]
    if args.cases and len(selected) != len(set(args.cases)):
        found = {c['id'] for c in selected}
        raise SystemExit(f"Unknown case(s): {sorted(set(args.cases) - found)}")
    records = []
    for case in selected:
        records.append(run_case(case, rendered_prompt, force=args.force))
    summary = {
        'model': sample['model'],
        'provider': sample['provider'],
        'reasoning': sample['reasoning'],
        'requestedCases': [c['id'] for c in selected],
        'successful': sum(r.get('returnCode') == 0 and r.get('parsedJson') is not None for r in records),
        'failed': sum(not (r.get('returnCode') == 0 and r.get('parsedJson') is not None) for r in records),
        'totalDurationSeconds': round(sum(r.get('durationSeconds', 0) for r in records), 3),
    }
    (TRIAL / 'run-summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == '__main__':
    main()
