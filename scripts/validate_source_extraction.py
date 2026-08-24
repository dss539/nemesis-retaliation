#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import tempfile
from pathlib import Path

from PIL import Image

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
        'card-gap-adjudications.json',
        'card-gap-inventory.json',
        'extraction-roadmap.md',
        'intruder-help-sheet.json',
        'objective-help-sheet.json',
        'objective-help-sheet-layout.json',
        'room-help-sheet.json',
        'room-help-sheet-layout.json',
        'secondary-source-inventory.json',
    ]
    for name in required:
        if not (EXTRACT / name).is_file():
            failures.append({'check': 'required output', 'missing': name})

    inventory = load(EXTRACT / 'base-source-inventory.json')
    gaps = load(EXTRACT / 'card-gap-inventory.json')
    intruder = load(EXTRACT / 'intruder-help-sheet.json')
    objective_help = load(EXTRACT / 'objective-help-sheet.json')
    objective_layout = load(EXTRACT / 'objective-help-sheet-layout.json')
    room_help = load(EXTRACT / 'room-help-sheet.json')
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

    # Verify the closed 13-record card-gap review as a dedicated source-bound projection.
    card_gap_run = subprocess.run(
        ['python3', str(REPO / 'scripts/validate_card_gap_adjudications.py')],
        check=False,
        text=True,
        capture_output=True,
    )
    try:
        card_gap_report = json.loads(card_gap_run.stdout)
    except json.JSONDecodeError:
        card_gap_report = {'passed': False, 'checks': {}, 'failures': [{'check': 'invalid validator output', 'stderr': card_gap_run.stderr}]}
    if card_gap_run.returncode != 0 or not card_gap_report.get('passed'):
        failures.append({'check': 'card gap adjudications', 'report': card_gap_report})
    recomputed = card_gap_report.get('checks') or {}

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
    if len(room_grid) != 25 or any(
        not row.get('printedTitle')
        or row.get('effectExtractionStatus') != 'extracted'
        or row.get('effectExtractionPath') != 'docs/rules/source-extraction/room-help-sheet.json'
        or row.get('effectExtractionEntryNumber') != row.get('printedNumber')
        for row in room_entries
    ):
        failures.append({'check': 'Room Help Sheet layout entries'})
    room_counts = {
        'entries': len(room_entries),
        'byPrintedSectionMarker': {marker: sum(row.get('printedSectionMarker') == marker for row in room_entries) for marker in ['?', 'A', 'B', 'C']},
        'byPage': {str(page): sum(row.get('page') == page for row in room_entries) for page in [1, 2]},
    }
    if room_layout.get('counts') != room_counts or room_counts != {'entries': 25, 'byPrintedSectionMarker': {'?': 13, 'A': 4, 'B': 4, 'C': 4}, 'byPage': {'1': 13, '2': 12}}:
        failures.append({'check': 'Room Help Sheet layout counts', 'actual': room_counts})

    # Verify the complete Room Help extraction and regenerate every visual crop.
    help_source = room_help.get('source') or {}
    help_pdf = REPO / help_source.get('path', '')
    if not help_pdf.is_file() or sha(help_pdf) != help_source.get('sha256') or pdf_pages(help_pdf) != help_source.get('pages'):
        failures.append({'check': 'Room Help Sheet extraction source tuple'})
    help_entries = room_help.get('entries') or []
    help_numbers = [row.get('printedNumber') for row in help_entries]
    if help_numbers != expected_numbers or len(help_numbers) != len(set(help_numbers)):
        failures.append({'check': 'Room Help Sheet extraction numbers', 'actual': help_numbers})
    help_occurrences = []
    help_placeholders = 0
    unreadable_count = 0
    layout_by_number = {row['printedNumber']: row for row in room_entries}
    placeholder_re = re.compile(r'\[(R\d{2}-I\d{2})\]')
    with tempfile.TemporaryDirectory(prefix='validate-room-help-') as tmpdir:
        prefix = Path(tmpdir) / 'page'
        subprocess.run(['pdftoppm', '-f', '1', '-l', '2', '-png', '-r', str(help_source.get('renderDpi')), str(help_pdf), str(prefix)], check=True)
        pages = {page: Image.open(Path(tmpdir) / f'page-{page}.png').convert('RGB') for page in (1, 2)}
        for page, image in pages.items():
            expected_page_hash = (help_source.get('renderedPageSha256') or {}).get(str(page))
            if list(image.size) != help_source.get('renderDimensions') or sha(Path(tmpdir) / f'page-{page}.png') != expected_page_hash:
                failures.append({'check': 'Room Help rendered page', 'page': page})
        for row in help_entries:
            number = row.get('printedNumber')
            layout_row = layout_by_number.get(number)
            if not layout_row or row.get('printedTitle') != layout_row.get('printedTitle') or row.get('printedSectionMarker') != layout_row.get('printedSectionMarker'):
                failures.append({'check': 'Room Help extraction layout join', 'number': number})
            icons = row.get('functionalIconOccurrences') or []
            icon_ids = [icon.get('occurrenceId') for icon in icons]
            help_occurrences.extend(icon_ids)
            if len(icon_ids) != len(set(icon_ids)) or any(not isinstance(item, str) or not item.startswith(f'R{number}-I') for item in icon_ids):
                failures.append({'check': 'Room Help occurrence IDs', 'number': number})
            strings_to_scan = [row.get('printedEffect') or '', *(row.get('associatedNotes') or []), *(row.get('crossReferences') or [])]
            placeholders = [match for text in strings_to_scan for match in placeholder_re.findall(text)]
            help_placeholders += len(placeholders)
            if set(placeholders) - set(icon_ids):
                failures.append({'check': 'Room Help undefined placeholder', 'number': number, 'undefined': sorted(set(placeholders)-set(icon_ids))})
            unreadable_count += len(row.get('materialUnreadableSpans') or [])
            visual = row.get('visualEvidence') or {}
            page = visual.get('page')
            crop = pages[page].crop(tuple(visual.get('cropBox') or []))
            crop_path = Path(tmpdir) / f'room-{number}.png'
            crop.save(crop_path, 'PNG', optimize=True)
            if list(crop.size) != visual.get('cropDimensions') or sha(crop_path) != visual.get('cropSha256'):
                failures.append({'check': 'Room Help crop evidence', 'number': number})
        for image in pages.values():
            image.close()
    if len(help_occurrences) != len(set(help_occurrences)):
        failures.append({'check': 'Room Help global occurrence uniqueness'})
    recomputed_help_counts = {
        'entries': len(help_entries),
        'byPrintedSectionMarker': {marker: sum(row.get('printedSectionMarker') == marker for row in help_entries) for marker in ['?', 'A', 'B', 'C']},
        'byPage': {str(page): sum((row.get('visualEvidence') or {}).get('page') == page for row in help_entries) for page in [1, 2]},
        'functionalIconOccurrences': len(help_occurrences),
        'effectAndNoteIconReferences': help_placeholders,
        'entriesWithAssociatedNotes': sum(bool(row.get('associatedNotes')) for row in help_entries),
        'entriesWithCrossReferences': sum(bool(row.get('crossReferences')) for row in help_entries),
        'materialUnreadableSpans': unreadable_count,
    }
    if room_help.get('counts') != recomputed_help_counts or recomputed_help_counts.get('materialUnreadableSpans') != 0:
        failures.append({'check': 'Room Help extraction counts', 'expected': recomputed_help_counts, 'actual': room_help.get('counts')})

    # Verify the Objective Help layout/extraction, including repeated terms and physical occlusion boundaries.
    objective_source = objective_help.get('source') or {}
    objective_pdf = REPO / objective_source.get('path', '')
    if not objective_pdf.is_file() or sha(objective_pdf) != objective_source.get('sha256') or pdf_pages(objective_pdf) != objective_source.get('pages'):
        failures.append({'check': 'Objective Help source tuple'})
    layout_units = objective_layout.get('units') or []
    objective_units = objective_help.get('units') or []
    layout_ids = [row.get('sourceUnitId') for row in layout_units]
    objective_ids = [row.get('sourceUnitId') for row in objective_units]
    if objective_ids != layout_ids or len(objective_ids) != len(set(objective_ids)):
        failures.append({'check': 'Objective Help unit closure', 'layout': layout_ids, 'extraction': objective_ids})
    layout_by_id = {row['sourceUnitId']: row for row in layout_units}
    objective_icons = []
    objective_partial_icons = []
    objective_placeholders = 0
    objective_unreadable = 0
    objective_partial_units = 0
    objective_full_units = 0
    objective_placeholder_re = re.compile(r'\[([A-Z0-9-]+-I\d{2})\]')
    with tempfile.TemporaryDirectory(prefix='validate-objective-help-') as tmpdir:
        prefix = Path(tmpdir) / 'page'
        render = (objective_source.get('visualInspection') or {})
        subprocess.run(['pdftoppm', '-f', '1', '-l', '2', '-png', '-r', str(render.get('dpi')), str(objective_pdf), str(prefix)], check=True)
        pages = {page: Image.open(Path(tmpdir) / f'page-{page}.png').convert('RGB') for page in (1, 2)}
        for page, image in pages.items():
            expected_hash = (render.get('renderedPageSha256') or {}).get(str(page))
            if list(image.size) != render.get('renderDimensions') or sha(Path(tmpdir) / f'page-{page}.png') != expected_hash:
                failures.append({'check': 'Objective Help rendered page', 'page': page})
        for row in objective_units:
            unit_id = row.get('sourceUnitId')
            layout_row = layout_by_id.get(unit_id)
            if not layout_row or row.get('category') != layout_row.get('category'):
                failures.append({'check': 'Objective Help layout join', 'sourceUnitId': unit_id})
                continue
            icons = row.get('functionalIconOccurrences') or []
            partial_icons = row.get('partiallyVisibleIconOccurrences') or []
            icon_ids = [item.get('occurrenceId') for item in icons]
            partial_ids = [item.get('occurrenceId') for item in partial_icons]
            objective_icons.extend(icon_ids)
            objective_partial_icons.extend(partial_ids)
            if len(icon_ids) != len(set(icon_ids)) or len(partial_ids) != len(set(partial_ids)):
                failures.append({'check': 'Objective Help occurrence IDs', 'sourceUnitId': unit_id})
            strings_to_scan = []
            for key in ('printedDefinition', 'topInstruction', 'printedCondition', 'printedText'):
                if isinstance(row.get(key), str):
                    strings_to_scan.append(row[key])
            strings_to_scan.extend(row.get('associatedNotes') or [])
            placeholders = [match for text in strings_to_scan for match in objective_placeholder_re.findall(text)]
            objective_placeholders += len(placeholders)
            if set(placeholders) - set(icon_ids):
                failures.append({'check': 'Objective Help undefined placeholder', 'sourceUnitId': unit_id, 'undefined': sorted(set(placeholders)-set(icon_ids))})
            objective_unreadable += len(row.get('materialUnreadableSpans') or [])
            if row.get('visibility') == 'partially-occluded' or row.get('materialOccludedSpans'):
                objective_partial_units += 1
            else:
                objective_full_units += 1
            visual = row.get('visualEvidence') or {}
            page = visual.get('page')
            crop = pages[page].crop(tuple(visual.get('cropBox') or []))
            crop_path = Path(tmpdir) / f'{unit_id}.png'
            crop.save(crop_path, 'PNG', optimize=True)
            if list(crop.size) != visual.get('cropDimensions') or sha(crop_path) != visual.get('cropSha256'):
                failures.append({'check': 'Objective Help crop evidence', 'sourceUnitId': unit_id})
        for image in pages.values():
            image.close()
    if len(objective_icons) != len(set(objective_icons)) or len(objective_partial_icons) != len(set(objective_partial_icons)):
        failures.append({'check': 'Objective Help global occurrence uniqueness'})
    objective_categories = ('game-term', 'mission-objective', 'mission-task', 'private-objective', 'explanatory-note')
    recomputed_objective_counts = {
        'sourceUnits': len(objective_units),
        'pageOccurrences': {str(page): sum((row.get('visualEvidence') or {}).get('page') == page for row in objective_units) for page in [1, 2]},
        'byCategory': {category: sum(row.get('category') == category for row in objective_units) for category in objective_categories},
        'fullyVisibleAndExtracted': objective_full_units,
        'partiallyOccluded': objective_partial_units,
        'functionalIconOccurrences': len(objective_icons),
        'partiallyVisibleIconOccurrences': len(objective_partial_icons),
        'textIconReferences': objective_placeholders,
        'materialUnreadableSpans': objective_unreadable,
    }
    required_objective_counts = {
        'sourceUnits': 45,
        'pageOccurrences': {'1': 22, '2': 23},
        'byCategory': {'game-term': 14, 'mission-objective': 7, 'mission-task': 8, 'private-objective': 15, 'explanatory-note': 1},
        'fullyVisibleAndExtracted': 35,
        'partiallyOccluded': 10,
        'functionalIconOccurrences': 50,
        'partiallyVisibleIconOccurrences': 5,
        'textIconReferences': 30,
        'materialUnreadableSpans': 0,
    }
    if objective_help.get('counts') != recomputed_objective_counts or recomputed_objective_counts != required_objective_counts:
        failures.append({'check': 'Objective Help extraction counts', 'expected': required_objective_counts, 'actual': recomputed_objective_counts})
    # Repeated GAME TERMS are independent page occurrences but exact RGB duplicates.
    objective_by_id = {row['sourceUnitId']: row for row in objective_units}
    for index in range(1, 8):
        p1 = objective_by_id[f'P1-GT-{index:02d}']
        p2 = objective_by_id[f'P2-GT-{index:02d}']
        if p2.get('pixelIdenticalToSourceUnitId') != p1.get('sourceUnitId') or (p1.get('visualEvidence') or {}).get('cropSha256') != (p2.get('visualEvidence') or {}).get('cropSha256'):
            failures.append({'check': 'Objective Help repeated game term', 'index': index})

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
            'cardGapRecords': recomputed.get('reviewedRecords'),
            'cardGapCounts': recomputed,
            'intruderHelpSides': len(intruder['sides']),
            'intruderHelpInstructions': source_instructions,
            'intruderHelpOccurrenceIds': len(set(occurrence_ids)),
            'roomHelpEntries': len(room_entries),
            'roomHelpCounts': room_counts,
            'roomHelpEffectsExtracted': len(help_entries),
            'roomHelpFunctionalIconOccurrences': len(help_occurrences),
            'roomHelpEffectAndNoteIconReferences': help_placeholders,
            'roomHelpMaterialUnreadableSpans': unreadable_count,
            'objectiveHelpSourceUnits': len(objective_units),
            'objectiveHelpFullyVisibleAndExtracted': objective_full_units,
            'objectiveHelpPartiallyOccluded': objective_partial_units,
            'objectiveHelpFunctionalIconOccurrences': len(objective_icons),
            'objectiveHelpPartiallyVisibleIconOccurrences': len(objective_partial_icons),
            'objectiveHelpTextIconReferences': objective_placeholders,
            'objectiveHelpMaterialUnreadableSpans': objective_unreadable,
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
