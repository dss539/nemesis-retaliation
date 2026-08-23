#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
EXTRACT = REPO / 'docs/rules/source-extraction'
REPORT = EXTRACT / 'validation.json'
CORPUS = REPO / 'assets/tts-mod/extract/card-text-corpus.json'
SELECTED = REPO / 'assets/tts-mod/extract/selected-card-text-evidence.json'
QUEUE = REPO / 'assets/tts-mod/extract/low-confidence-review.json'
UNREADABLE_RE = re.compile(r'\[(?:illegible|clipped)(?:[^\]]*)\]', re.I)


def load(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pdf_pages(path: Path) -> int:
    output = subprocess.run(['pdfinfo', str(path)], check=True, text=True, capture_output=True).stdout
    match = re.search(r'^Pages:\s+(\d+)\s*$', output, re.M)
    if not match:
        raise ValueError(f'missing page count: {path}')
    return int(match.group(1))


def norm(value: str) -> str:
    return ' '.join(value.split())


def all_strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from all_strings(item)
    elif isinstance(value, dict):
        for item in value.values():
            yield from all_strings(item)


def main() -> None:
    failures = []
    required = [
        'README.md',
        'base-source-inventory.json',
        'card-gap-inventory.json',
        'extraction-roadmap.md',
        'intruder-help-sheet.json',
        'room-help-sheet-layout.json',
        'secondary-source-inventory.json',
    ]
    for name in required:
        if not (EXTRACT / name).is_file():
            failures.append({'check': 'required output', 'missing': name})

    inventory = load(EXTRACT / 'base-source-inventory.json')
    gaps = load(EXTRACT / 'card-gap-inventory.json')
    intruder = load(EXTRACT / 'intruder-help-sheet.json')
    room_layout = load(EXTRACT / 'room-help-sheet-layout.json')
    secondary = load(EXTRACT / 'secondary-source-inventory.json')
    corpus = load(CORPUS)
    selected = load(SELECTED)
    queue = load(QUEUE)

    # Verify every inventoried repository source byte-for-byte.
    repository_hashes = 0
    for row in inventory['officialSources']:
        path = REPO / row['path']
        if not path.is_file() or sha(path) != row['sha256'] or path.stat().st_size != row['bytes']:
            failures.append({'check': 'official source tuple', 'path': row['path']})
            continue
        repository_hashes += 1
        if row.get('pages') != pdf_pages(path):
            failures.append({'check': 'official PDF pages', 'path': row['path']})
        extraction = row.get('textExtraction')
        if extraction:
            tpath = REPO / extraction['path']
            if not tpath.is_file() or sha(tpath) != extraction['sha256']:
                failures.append({'check': 'official text extraction tuple', 'path': extraction['path']})
    for row in secondary['ttsStructuredEvidence']:
        path = REPO / row['path']
        if not path.is_file() or sha(path) != row['sha256'] or path.stat().st_size != row['bytes']:
            failures.append({'check': 'TTS structured tuple', 'path': row['path']})
        else:
            repository_hashes += 1

    # Verify card gap inventory is a deterministic projection of current corpus states.
    expected_gap_rows = [row for row in corpus['records'] if row['extractionState'] in {'draft-partial', 'no-transcription'}]
    expected_paths = {row['sourcePath'] for row in expected_gap_rows}
    actual_paths = {row['sourcePath'] for row in gaps['records']}
    if actual_paths != expected_paths or len(actual_paths) != len(gaps['records']):
        failures.append({'check': 'card gap paths', 'missing': sorted(expected_paths-actual_paths), 'extra': sorted(actual_paths-expected_paths)})
    recomputed = {
        'records': len(expected_gap_rows),
        'draftPartial': sum(row['extractionState'] == 'draft-partial' for row in expected_gap_rows),
        'noTranscription': sum(row['extractionState'] == 'no-transcription' for row in expected_gap_rows),
        'operativeTextGaps': 0,
        'nonbodyMarkerOrStructureGaps': 0,
        'noOperativeTranscription': 0,
    }
    corpus_by_path = {row['sourcePath']: row for row in corpus['records']}
    for row in gaps['records']:
        source = REPO / row['sourcePath']
        if not source.is_file() or sha(source) != row['sourceSha256']:
            failures.append({'check': 'card gap source tuple', 'path': row['sourcePath']})
        original = corpus_by_path.get(row['sourcePath'])
        if not original or original['sourceSha256'] != row['sourceSha256']:
            failures.append({'check': 'card gap corpus tuple', 'path': row['sourcePath']})
            continue
        body = ((original.get('printedData') or {}).get('body') or '') if isinstance(original.get('printedData'), dict) else ''
        has_body_marker = bool(UNREADABLE_RE.search(body))
        if original['extractionState'] == 'no-transcription':
            expected_class = 'no-operative-transcription'
            recomputed['noOperativeTranscription'] += 1
        elif has_body_marker:
            expected_class = 'operative-text-gap'
            recomputed['operativeTextGaps'] += 1
        else:
            expected_class = 'nonbody-marker-or-structure-gap'
            recomputed['nonbodyMarkerOrStructureGaps'] += 1
        if row['gapClass'] != expected_class:
            failures.append({'check': 'card gap class', 'path': row['sourcePath'], 'expected': expected_class, 'actual': row['gapClass']})
    if gaps['sourceCorpusSha256'] != sha(CORPUS):
        failures.append({'check': 'card gap corpus hash'})
    if gaps['counts'] != recomputed:
        failures.append({'check': 'card gap counts', 'expected': recomputed, 'actual': gaps['counts']})

    # Verify Intruder Help source pairs, extraction completeness, and selected evidence lineage.
    if intruder.get('component') != 'Intruder Help Sheet' or len(intruder.get('sides') or []) != 2:
        failures.append({'check': 'Intruder Help side count'})
    selected_by_path = {entry['sourcePath']: entry for entry in selected['entries']}
    queue_by_path = {entry['sourcePath']: entry for entry in queue['entries']}
    occurrence_ids = []
    source_instructions = 0
    for side in intruder['sides']:
        path = REPO / side['sourcePath']
        if not path.is_file() or sha(path) != side['sourceSha256']:
            failures.append({'check': 'Intruder Help source tuple', 'path': side['sourcePath']})
            continue
        entry = selected_by_path.get(side['sourcePath'])
        if not entry or entry['sourceSha256'] != side['sourceSha256']:
            failures.append({'check': 'Intruder Help selected tuple', 'path': side['sourcePath']})
            continue
        run = next((item for item in entry['runs'] if item['runIdentity'] == entry['selectedRunIdentity']), None)
        if not run:
            failures.append({'check': 'Intruder Help selected run', 'path': side['sourcePath']})
            continue
        evidence = side['evidence']
        if evidence['selectedRunIdentity'] != entry['selectedRunIdentity'] or evidence['runtime'] != run['runtime'] or evidence['artifactPaths'] != run['artifactPaths']:
            failures.append({'check': 'Intruder Help evidence projection', 'path': side['sourcePath']})
        runtime = evidence['runtime']
        expected_runtime = {'provider': 'openai-codex', 'model': 'gpt-5.6-sol', 'reasoningEffort': 'max', 'auxiliaryVisionUsed': False, 'qwenUsed': False, 'ocrCanonicalEvidenceUsed': False, 'modelDowngradeUsed': False}
        for key, value in expected_runtime.items():
            if runtime.get(key) != value:
                failures.append({'check': 'Intruder Help runtime', 'path': side['sourcePath'], 'field': key})
        selected_text = norm(' '.join(all_strings(run['visibleText'])))
        for column in side['columns']:
            for row in column['rows']:
                occurrence_ids.append(row['occurrenceId'])
                source_instructions += 1
                instruction = row['printedInstruction']
                if UNREADABLE_RE.search(instruction):
                    failures.append({'check': 'Intruder Help operative unreadable', 'occurrenceId': row['occurrenceId']})
                if norm(instruction) not in selected_text:
                    failures.append({'check': 'Intruder Help selected text mismatch', 'occurrenceId': row['occurrenceId']})
        bottom = side['bottomRow']
        occurrence_ids.append(bottom['occurrenceId'])
        source_instructions += 1
        if norm(bottom['printedInstruction']) not in selected_text:
            failures.append({'check': 'Intruder Help selected text mismatch', 'occurrenceId': bottom['occurrenceId']})
        qrow = queue_by_path.get(side['sourcePath'])
        refs = ((qrow or {}).get('provenance') or {}).get('objectRefs') or []
        if not any(ref.get('ttsGuid') == '1e58e7' and ref.get('roles') == ['intruderHelp'] for ref in refs):
            failures.append({'check': 'Intruder Help TTS role', 'path': side['sourcePath']})
    if len(occurrence_ids) != len(set(occurrence_ids)):
        failures.append({'check': 'Intruder Help occurrence IDs'})
    if source_instructions != 18:
        failures.append({'check': 'Intruder Help instruction count', 'expected': 18, 'actual': source_instructions})

    # Verify the visual Room Help Sheet layout inventory without interpreting effects.
    room_source = room_layout.get('source') or {}
    room_pdf = REPO / room_source.get('path', '')
    if not room_pdf.is_file() or sha(room_pdf) != room_source.get('sha256') or pdf_pages(room_pdf) != room_source.get('pages'):
        failures.append({'check': 'Room Help Sheet source tuple'})
    room_entries = room_layout.get('entries') or []
    room_numbers = [row.get('printedNumber') for row in room_entries]
    expected_numbers = [f'{number:02d}' for number in range(1, 26)]
    if sorted(room_numbers) != expected_numbers or len(room_numbers) != len(set(room_numbers)):
        failures.append({'check': 'Room Help Sheet printed numbers', 'expected': expected_numbers, 'actual': sorted(room_numbers)})
    room_grid = {(row.get('page'), row.get('gridColumn'), row.get('gridRow')) for row in room_entries}
    if len(room_grid) != 25 or any(not row.get('printedTitle') or row.get('effectExtractionStatus') != 'pending' for row in room_entries):
        failures.append({'check': 'Room Help Sheet layout entries'})
    room_counts = {
        'entries': len(room_entries),
        'byPrintedSectionMarker': {marker: sum(row.get('printedSectionMarker') == marker for row in room_entries) for marker in ['?', 'A', 'B', 'C']},
        'byPage': {str(page): sum(row.get('page') == page for row in room_entries) for page in [1, 2]},
    }
    if room_layout.get('counts') != room_counts or room_counts != {'entries': 25, 'byPrintedSectionMarker': {'?': 13, 'A': 4, 'B': 4, 'C': 4}, 'byPage': {'1': 13, '2': 12}}:
        failures.append({'check': 'Room Help Sheet layout counts', 'actual': room_counts})

    # Verify all BGA snapshots are byte-identical and still live.
    bga_hashes = set()
    for row in secondary['licensedDigitalSecondary']['copies']:
        path = Path(row['path'])
        if not path.is_file() or sha(path) != row['sha256'] or path.stat().st_size != row['bytes']:
            failures.append({'check': 'BGA snapshot tuple', 'path': row['path']})
        else:
            bga_hashes.add(row['sha256'])
    if sorted(bga_hashes) != secondary['licensedDigitalSecondary']['distinctSha256'] or len(bga_hashes) != 1:
        failures.append({'check': 'BGA snapshot dedupe', 'hashes': sorted(bga_hashes)})

    report = {
        'schemaVersion': 1,
        'passed': not failures,
        'checks': {
            'requiredOutputs': len(required),
            'repositorySourceHashesVerified': repository_hashes,
            'officialSources': len(inventory['officialSources']),
            'cardGapRecords': len(gaps['records']),
            'cardGapCounts': recomputed,
            'intruderHelpSides': len(intruder['sides']),
            'intruderHelpInstructions': source_instructions,
            'intruderHelpOccurrenceIds': len(set(occurrence_ids)),
            'roomHelpEntries': len(room_entries),
            'roomHelpCounts': room_counts,
            'bgaCopies': len(secondary['licensedDigitalSecondary']['copies']),
            'bgaDistinctHashes': len(bga_hashes),
        },
        'failureCount': len(failures),
        'failures': failures,
    }
    REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if failures:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
