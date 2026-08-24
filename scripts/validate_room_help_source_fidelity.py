#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import tempfile
import unicodedata
from pathlib import Path
from PIL import Image

REPO = Path(__file__).resolve().parents[1]
DEFAULT_RECORD = REPO / 'docs/rules/source-extraction/room-help-sheet.json'
DEFAULT_LAYOUT = REPO / 'docs/rules/source-extraction/room-help-sheet-layout.json'
LOCK = REPO / 'docs/rules/source-extraction/room-help-sheet-source-fidelity-lock.json'
PINNED_LOCK_SHA256 = '27c23c1c885e2ab851bef0bfb43b7471ea862af9d0308f9b3e70026320b4d8b4'
EXPECTED_COUNTS = {
    'entries': 25,
    'functionalIconOccurrences': 112,
    'effectAndNoteIconReferences': 39,
    'entriesWithAssociatedNotes': 18,
    'entriesWithCrossReferences': 5,
    'materialUnreadableSpans': 0,
}
PLACEHOLDER_RE = re.compile(r'\[(R\d{2}-I\d{2})\]')
UNREADABLE_RE = re.compile(r'\[(?:illegible|unreadable|clipped)(?::[^\]]*)?\]', re.IGNORECASE)
SEMANTIC_LANGUAGE_RE = re.compile(r'\b(?:canonical(?: token| term)?|means|represents|equivalent to|alias of)\b', re.IGNORECASE)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8'))


def exact_projection(entry: dict) -> dict:
    visual = entry.get('visualEvidence') or {}
    return {
        'printedNumber': entry.get('printedNumber'),
        'printedSectionMarker': entry.get('printedSectionMarker'),
        'printedTitle': entry.get('printedTitle'),
        'printedEffect': entry.get('printedEffect'),
        'associatedNotes': entry.get('associatedNotes', []),
        'crossReferences': entry.get('crossReferences', []),
        'functionalIconOccurrences': entry.get('functionalIconOccurrences', []),
        'materialUnreadableSpans': entry.get('materialUnreadableSpans', []),
        'visualEvidence': {
            'page': visual.get('page'),
            'gridColumn': visual.get('gridColumn'),
            'gridRow': visual.get('gridRow'),
            'renderDpi': visual.get('renderDpi'),
            'renderDimensions': visual.get('renderDimensions'),
            'renderedPageSha256': visual.get('renderedPageSha256'),
            'cropBox': visual.get('cropBox'),
            'cropDimensions': visual.get('cropDimensions'),
            'cropSha256': visual.get('cropSha256'),
        },
    }


def projection_sha(projection: dict) -> str:
    encoded = json.dumps(projection, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()
    return hashlib.sha256(encoded).hexdigest()


def text_tokens(text: str) -> list[str]:
    text = PLACEHOLDER_RE.sub(' ', text)
    text = unicodedata.normalize('NFKD', text).replace('’', "'").replace('“', '"').replace('”', '"')
    return re.findall(r"[a-z0-9]+(?:'[a-z0-9]+)?", text.casefold())


def is_subsequence(expected: list[str], actual: list[str]) -> bool:
    """Match PDF text tokens despite column bleed and PDF word fragmentation.

    Exact tokens advance normally. A source word split into fragments such as
    ``deacti ... vate`` also advances when the ordered fragments concatenate
    to the expected token; unrelated tokens from an adjacent column may occur
    between those fragments. Punctuation/capitalization remain enforced by the
    independently pinned exact source projection, not this lexical aid.
    """
    actual_index = 0
    for expected_token in expected:
        matched_at = None
        for start in range(actual_index, len(actual)):
            candidate = actual[start]
            if candidate == expected_token:
                matched_at = start + 1
                break
            if not expected_token.startswith(candidate) or not candidate:
                continue
            assembled = candidate
            for end in range(start + 1, len(actual)):
                extension = assembled + actual[end]
                if expected_token.startswith(extension):
                    assembled = extension
                    if assembled == expected_token:
                        matched_at = end + 1
                        break
            if matched_at is not None:
                break
        if matched_at is None:
            return False
        actual_index = matched_at
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--record', type=Path, default=DEFAULT_RECORD)
    parser.add_argument('--layout', type=Path, default=DEFAULT_LAYOUT)
    args = parser.parse_args()
    failures: list[dict] = []

    if sha256(LOCK) != PINNED_LOCK_SHA256:
        failures.append({'check': 'pinned independent fidelity lock', 'expected': PINNED_LOCK_SHA256, 'actual': sha256(LOCK)})
    lock = load(LOCK)
    record = load(args.record)
    layout = load(args.layout)
    source = record.get('source') or {}
    lock_source = lock.get('source') or {}
    pdf = REPO / source.get('path', '')
    if not pdf.is_file() or sha256(pdf) != source.get('sha256') or source.get('sha256') != lock_source.get('sha256'):
        failures.append({'check': 'official PDF source tuple'})
    if layout.get('source', {}).get('sha256') != source.get('sha256') or layout.get('source', {}).get('path') != source.get('path'):
        failures.append({'check': 'layout/PDF source tuple'})

    with tempfile.TemporaryDirectory(prefix='validate-room-help-fidelity-') as temp_dir:
        temp = Path(temp_dir)
        text_layer = temp / 'rooms-layout.txt'
        subprocess.run(['pdftotext', '-layout', str(pdf), str(text_layer)], check=True)
        if sha256(text_layer) != lock_source.get('pdftotextLayoutSha256'):
            failures.append({'check': 'official PDF text-layer identity', 'actual': sha256(text_layer)})
        prefix = temp / 'page'
        subprocess.run(['pdftoppm', '-f', '1', '-l', '2', '-png', '-r', str(lock_source['renderDpi']), str(pdf), str(prefix)], check=True)
        pages = {page: Image.open(temp / f'page-{page}.png').convert('RGB') for page in (1, 2)}
        for page, image in pages.items():
            page_path = temp / f'page-{page}.png'
            if list(image.size) != lock_source['renderDimensions'] or sha256(page_path) != lock_source['renderedPageSha256'][str(page)]:
                failures.append({'check': 'rendered source page identity', 'page': page})

        entries = record.get('entries') or []
        lock_entries = lock.get('entries') or []
        layout_entries = layout.get('entries') or []
        by_number = {entry.get('printedNumber'): entry for entry in entries}
        lock_by_number = {entry.get('printedNumber'): entry for entry in lock_entries}
        layout_by_number = {entry.get('printedNumber'): entry for entry in layout_entries}
        expected_numbers = [f'{number:02d}' for number in range(1, 26)]
        if list(by_number) != expected_numbers or list(lock_by_number) != expected_numbers or sorted(layout_by_number) != expected_numbers:
            failures.append({'check': 'entry number closure', 'record': list(by_number), 'lock': list(lock_by_number)})

        occurrence_ids: list[str] = []
        placeholder_count = 0
        unreadable_count = 0
        for number in expected_numbers:
            entry = by_number.get(number)
            locked = lock_by_number.get(number)
            layout_entry = layout_by_number.get(number)
            if not entry or not locked or not layout_entry:
                continue
            projection = exact_projection(entry)
            if projection != locked.get('expected') or projection_sha(projection) != locked.get('exactProjectionSha256'):
                failures.append({'check': 'independent exact source projection', 'number': number})
            if any(projection.get(key) != layout_entry.get(key) for key in ('printedNumber', 'printedSectionMarker', 'printedTitle')):
                failures.append({'check': 'layout identity join', 'number': number})
            visual = projection['visualEvidence']
            if (visual.get('page'), visual.get('gridColumn'), visual.get('gridRow')) != (layout_entry.get('page'), layout_entry.get('gridColumn'), layout_entry.get('gridRow')):
                failures.append({'check': 'per-entry grid provenance', 'number': number})
            if visual.get('renderDpi') != lock_source['renderDpi'] or visual.get('renderDimensions') != lock_source['renderDimensions'] or visual.get('renderedPageSha256') != lock_source['renderedPageSha256'][str(visual.get('page'))]:
                failures.append({'check': 'per-entry render provenance', 'number': number})
            box = visual.get('cropBox') or []
            required_box = locked.get('requiredEvidenceBox')
            if box != required_box or len(box) != 4 or not (0 <= box[0] < box[2] <= lock_source['renderDimensions'][0] and 0 <= box[1] < box[3] <= lock_source['renderDimensions'][1]):
                failures.append({'check': 'audited evidence coverage box', 'number': number, 'actual': box, 'required': required_box})
                continue
            crop = pages[visual['page']].crop(tuple(box))
            crop_path = temp / f'room-{number}.png'
            crop.save(crop_path, 'PNG', optimize=True)
            if list(crop.size) != visual.get('cropDimensions') or list(crop.size) != [box[2] - box[0], box[3] - box[1]] or sha256(crop_path) != visual.get('cropSha256'):
                failures.append({'check': 'audited crop identity', 'number': number})

            icons = projection['functionalIconOccurrences']
            ids = [icon.get('occurrenceId') for icon in icons]
            occurrence_ids.extend(ids)
            if ids != locked.get('expectedFunctionalOccurrenceIds') or len(ids) != len(set(ids)) or any(not re.fullmatch(fr'R{number}-I\d{{2}}', item or '') for item in ids):
                failures.append({'check': 'exact functional occurrence sequence', 'number': number, 'actual': ids})
            for icon in icons:
                location = icon.get('location')
                appearance = icon.get('literalAppearance')
                if not isinstance(location, str) or not location.strip() or not isinstance(appearance, str) or not appearance.strip():
                    failures.append({'check': 'icon literal description/location completeness', 'number': number, 'occurrenceId': icon.get('occurrenceId')})
                elif '[' in appearance or ']' in appearance or SEMANTIC_LANGUAGE_RE.search(appearance):
                    failures.append({'check': 'icon extraction-only language', 'number': number, 'occurrenceId': icon.get('occurrenceId'), 'literalAppearance': appearance})

            strings = [projection['printedEffect'], *projection['associatedNotes'], *projection['crossReferences']]
            placeholders = [match for text in strings for match in PLACEHOLDER_RE.findall(text)]
            placeholder_count += len(placeholders)
            if placeholders != locked.get('expectedPlaceholderSequence') or any(item not in ids for item in placeholders):
                failures.append({'check': 'exact inline placeholder sequence', 'number': number, 'actual': placeholders})
            unreadable_markers = [marker for text in strings for marker in UNREADABLE_RE.findall(text)]
            unreadable_spans = projection['materialUnreadableSpans']
            unreadable_count += len(unreadable_spans)
            if bool(unreadable_markers) != bool(unreadable_spans):
                failures.append({'check': 'unreadability accounting', 'number': number, 'markers': unreadable_markers, 'spans': unreadable_spans})

            # The source lock enforces punctuation; the cropped PDF text layer independently
            # confirms that every visible lexical token occurs in source reading order.
            region_text = temp / f'room-{number}.txt'
            subprocess.run([
                'pdftotext', '-f', str(visual['page']), '-l', str(visual['page']), '-r', str(lock_source['renderDpi']),
                '-x', str(box[0]), '-y', str(box[1]), '-W', str(box[2] - box[0]), '-H', str(box[3] - box[1]),
                '-layout', str(pdf), str(region_text),
            ], check=True)
            expected_tokens = text_tokens(' '.join([projection['printedTitle'], *strings]))
            actual_tokens = text_tokens(region_text.read_text(encoding='utf-8'))
            if not is_subsequence(expected_tokens, actual_tokens):
                failures.append({'check': 'cropped PDF text-layer lexical sequence', 'number': number, 'expectedTokens': expected_tokens, 'actualTokens': actual_tokens})

        for image in pages.values():
            image.close()

    recomputed = {
        'entries': len(record.get('entries') or []),
        'functionalIconOccurrences': len(occurrence_ids),
        'effectAndNoteIconReferences': placeholder_count,
        'entriesWithAssociatedNotes': sum(bool(entry.get('associatedNotes')) for entry in record.get('entries') or []),
        'entriesWithCrossReferences': sum(bool(entry.get('crossReferences')) for entry in record.get('entries') or []),
        'materialUnreadableSpans': unreadable_count,
    }
    if len(occurrence_ids) != len(set(occurrence_ids)):
        failures.append({'check': 'global occurrence uniqueness'})
    if recomputed != EXPECTED_COUNTS or lock.get('expectedCounts') != EXPECTED_COUNTS or record.get('counts', {}).get('entries') != 25:
        failures.append({'check': 'independent hard-coded completeness counts', 'expected': EXPECTED_COUNTS, 'actual': recomputed, 'recordCounts': record.get('counts')})
    for key, value in EXPECTED_COUNTS.items():
        if record.get('counts', {}).get(key) != value:
            failures.append({'check': 'declared Room Help count', 'key': key, 'expected': value, 'actual': record.get('counts', {}).get(key)})

    report = {
        'schemaVersion': 1,
        'passed': not failures,
        'checks': {
            **EXPECTED_COUNTS,
            'pinnedLockSha256': PINNED_LOCK_SHA256,
            'pdfTextLayerSha256': lock_source.get('pdftotextLayoutSha256'),
            'entryExactProjectionsVerified': 25 if not any(f['check'] == 'independent exact source projection' for f in failures) else None,
            'auditedCropCoverageBoxesVerified': 25 if not any(f['check'] == 'audited evidence coverage box' for f in failures) else None,
        },
        'failureCount': len(failures),
        'failures': failures,
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if not failures else 1


if __name__ == '__main__':
    raise SystemExit(main())
