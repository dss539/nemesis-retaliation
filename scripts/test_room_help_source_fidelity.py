#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest

REPO = Path(__file__).resolve().parents[1]
VALIDATOR = REPO / 'scripts/validate_room_help_source_fidelity.py'
RECORD = REPO / 'docs/rules/source-extraction/room-help-sheet.json'
LAYOUT = REPO / 'docs/rules/source-extraction/room-help-sheet-layout.json'
LOCK = REPO / 'docs/rules/source-extraction/room-help-sheet-source-fidelity-lock.json'


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8'))


class RoomHelpSourceFidelityTests(unittest.TestCase):
    def run_validator(self, record: Path = RECORD, layout: Path = LAYOUT) -> tuple[subprocess.CompletedProcess[str], dict]:
        run = subprocess.run(
            ['python3', str(VALIDATOR), '--record', str(record), '--layout', str(layout)],
            cwd=REPO,
            check=False,
            capture_output=True,
            text=True,
            timeout=300,
        )
        return run, json.loads(run.stdout)

    def test_current_source_fidelity_lock_passes(self):
        run, report = self.run_validator()
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertTrue(report['passed'])
        self.assertEqual(report['failureCount'], 0)
        self.assertEqual(report['checks']['entryExactProjectionsVerified'], 25)
        self.assertEqual(report['checks']['auditedCropCoverageBoxesVerified'], 25)

    def test_lock_hash_is_pinned_in_validator(self):
        spec = importlib.util.spec_from_file_location('room_fidelity_validator', VALIDATOR)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader
        spec.loader.exec_module(module)
        self.assertEqual(hashlib.sha256(LOCK.read_bytes()).hexdigest(), module.PINNED_LOCK_SHA256)

    def test_coordinated_and_structural_corruptions_are_rejected(self):
        record = load(RECORD)
        layout = load(LAYOUT)
        by_number = {entry['printedNumber']: entry for entry in record['entries']}
        layout_by_number = {entry['printedNumber']: entry for entry in layout['entries']}

        # Verbatim effect corruption.
        by_number['01']['printedEffect'] = by_number['01']['printedEffect'].replace('chosen', 'corrupted')
        # Empty icon location and semantic language in a morphology-only field.
        by_number['02']['functionalIconOccurrences'][0]['location'] = ''
        by_number['02']['functionalIconOccurrences'][1]['literalAppearance'] = 'canonical token that means Fire'
        # Coordinated self-referential count reduction after deleting a source icon.
        by_number['03']['functionalIconOccurrences'].pop()
        record['counts']['functionalIconOccurrences'] = 111
        # Unaccounted operative unreadability marker.
        by_number['04']['printedEffect'] += ' [illegible]'
        # Truncated evidence crop with internally coordinated dimensions.
        box = by_number['05']['visualEvidence']['cropBox']
        by_number['05']['visualEvidence']['cropBox'] = [box[0], box[1], box[2], box[3] - 300]
        by_number['05']['visualEvidence']['cropDimensions'][1] -= 300
        # Per-entry provenance corruption.
        by_number['06']['visualEvidence']['gridRow'] = 99
        by_number['06']['visualEvidence']['renderedPageSha256'] = '0' * 64
        # Coordinated extraction/layout title edit must still fail against the independent lock.
        by_number['07']['printedTitle'] = 'COORDINATED FALSE TITLE'
        layout_by_number['07']['printedTitle'] = 'COORDINATED FALSE TITLE'
        # Placeholder order corruption.
        effect = by_number['08']['printedEffect']
        by_number['08']['printedEffect'] = effect.replace('[R08-I05]', '[SWAP]', 1).replace('[R08-I06]', '[R08-I05]', 1).replace('[SWAP]', '[R08-I06]', 1)
        # Note corruption/cross-reference invention.
        by_number['11']['associatedNotes'][0] += ' CORRUPTED NOTE.'
        by_number['11']['crossReferences'] = ['Invented page 99.']

        with tempfile.TemporaryDirectory(prefix='room-help-negative-control-') as temp_dir:
            record_path = Path(temp_dir) / 'room-help-sheet.json'
            layout_path = Path(temp_dir) / 'room-help-sheet-layout.json'
            record_path.write_text(json.dumps(record, indent=2, ensure_ascii=False) + '\n')
            layout_path.write_text(json.dumps(layout, indent=2, ensure_ascii=False) + '\n')
            run, report = self.run_validator(record_path, layout_path)

        self.assertNotEqual(run.returncode, 0)
        self.assertFalse(report['passed'])
        checks = {failure['check'] for failure in report['failures']}
        required = {
            'independent exact source projection',
            'icon literal description/location completeness',
            'icon extraction-only language',
            'exact functional occurrence sequence',
            'unreadability accounting',
            'audited evidence coverage box',
            'per-entry grid provenance',
            'per-entry render provenance',
            'exact inline placeholder sequence',
            'independent hard-coded completeness counts',
            'declared Room Help count',
        }
        self.assertTrue(required.issubset(checks), sorted(checks))


if __name__ == '__main__':
    unittest.main()
