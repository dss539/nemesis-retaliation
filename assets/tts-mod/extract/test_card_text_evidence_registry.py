#!/usr/bin/env python3
"""Focused strict-schema tests for the selected-evidence registry."""
from __future__ import annotations

import copy
from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import analyze_unresolved_symbols as unresolved_symbols
import card_text_evidence_registry as selected_evidence
from build_card_text_corpus import DEFAULT_OUTPUT, REGISTRY
import validate_card_text_corpus as corpus_validator


class SelectedEvidenceRegistryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.registry = selected_evidence.load_registry(REGISTRY)

    def assert_rejected(self, registry: dict) -> None:
        with self.assertRaises(selected_evidence.RegistryError):
            selected_evidence.validate_registry(registry)

    def assert_corpus_validator_rejects(self, corpus: dict, registry: dict) -> None:
        with tempfile.TemporaryDirectory(prefix="card-corpus-validator-") as temp_dir:
            root = Path(temp_dir)
            corpus_path = root / "corpus.json"
            registry_path = root / "registry.json"
            report_path = root / "report.json"
            corpus_path.write_text(json.dumps(corpus, indent=2, ensure_ascii=False) + "\n")
            registry_path.write_text(json.dumps(registry, indent=2, ensure_ascii=False) + "\n")
            with mock.patch.object(corpus_validator, "CORPUS", corpus_path), \
                    mock.patch.object(corpus_validator, "REGISTRY", registry_path), \
                    mock.patch.object(corpus_validator, "REPORT", report_path), \
                    redirect_stdout(io.StringIO()):
                with self.assertRaisesRegex(SystemExit, "1"):
                    corpus_validator.main()
            report = json.loads(report_path.read_text())
            self.assertFalse(report["passed"])
            self.assertGreater(report["failureCount"], 0)

    def test_current_registry_is_valid(self) -> None:
        self.assertEqual(selected_evidence.validate_registry(copy.deepcopy(self.registry)), self.registry)

    def test_duplicate_tuple_is_rejected(self) -> None:
        registry = copy.deepcopy(self.registry)
        registry["entries"].append(copy.deepcopy(registry["entries"][0]))
        self.assert_rejected(registry)

    def test_malformed_entry_is_rejected(self) -> None:
        registry = copy.deepcopy(self.registry)
        del registry["entries"][0]["selectedRunIdentity"]
        self.assert_rejected(registry)

    def test_unsupported_entry_status_is_rejected(self) -> None:
        registry = copy.deepcopy(self.registry)
        registry["entries"][0]["status"] = "promoted"
        self.assert_rejected(registry)

    def test_unsupported_run_decision_is_rejected(self) -> None:
        registry = copy.deepcopy(self.registry)
        registry["entries"][0]["runs"][0]["promotionDecision"] = "promote"
        self.assert_rejected(registry)

    def test_duplicate_stable_run_identity_is_rejected(self) -> None:
        registry = copy.deepcopy(self.registry)
        registry["entries"][1]["runs"][0] = copy.deepcopy(registry["entries"][0]["runs"][0])
        registry["entries"][1]["selectedRunIdentity"] = registry["entries"][1]["runs"][0]["runIdentity"]
        self.assert_rejected(registry)

    def test_registry_tuple_absent_from_corpus_is_rejected(self) -> None:
        entry = self.registry["entries"][0]
        wrong_tuple_record = {"sourcePath": entry["sourcePath"], "sourceSha256": "0" * 64, "evidence": {}}
        with self.assertRaises(selected_evidence.RegistryError):
            selected_evidence.apply_registry([wrong_tuple_record], copy.deepcopy(self.registry))

    def test_validator_rejects_corpus_selected_evidence_absent_from_registry(self) -> None:
        corpus = json.loads(DEFAULT_OUTPUT.read_text())
        registry = copy.deepcopy(self.registry)
        registry["entries"].pop()
        self.assert_corpus_validator_rejects(corpus, registry)

    def test_validator_rejects_selected_evidence_tuple_mismatch(self) -> None:
        corpus = json.loads(DEFAULT_OUTPUT.read_text())
        selected_row = next(row for row in corpus["records"] if row.get("selectedExtraction"))
        selected_row["selectedExtraction"]["sourceSha256"] = "0" * 64
        self.assert_corpus_validator_rejects(corpus, copy.deepcopy(self.registry))

    def test_selected_unresolved_occurrences_supersede_legacy_tokens_one_for_one(self) -> None:
        row = {
            "sourcePath": "example.png",
            "symbols": {"unresolvedOrLocalTokens": ["legacy token that must not survive"]},
            "selectedExtraction": {
                "unresolvedIconOccurrences": [
                    {
                        "cardLocation": "upper left",
                        "referenceLabel": "Observed white ringed silhouette",
                        "matchDecision": "no-match",
                        "canonicalToken": None,
                        "closestAlternative": "character",
                        "visibleDiscriminator": "The source has concentric blue rings absent from the candidate.",
                        "evidenceRun": "worker-1",
                    },
                    {
                        "cardLocation": "body line 2",
                        "referenceLabel": "No authoritative label",
                        "matchDecision": "no-match",
                        "canonicalToken": None,
                        "closestAlternative": "life support",
                        "visibleDiscriminator": "A white three-section capsule with paired gray loops.",
                        "evidenceRun": "worker-1",
                    },
                    {
                        "cardLocation": "body line 3",
                        "referenceLabel": "Official morphology match without a semantic label",
                        "matchDecision": "match",
                        "canonicalToken": None,
                        "closestAlternative": "plain cross",
                        "visibleDiscriminator": "The same waveform morphology is visible, but no source names it.",
                        "evidenceRun": "worker-1",
                    },
                ]
            },
        }
        occurrences = unresolved_symbols.unresolved_occurrences(row)
        self.assertEqual(len(occurrences), 3)
        self.assertEqual(
            [item["token"] for item in occurrences],
            [
                "Observed white ringed silhouette",
                "A white three-section capsule with paired gray loops.",
                "Official morphology match without a semantic label",
            ],
        )
        self.assertEqual(
            [item["occurrenceSource"] for item in occurrences],
            [
                "selected-explicit-authoritative-no-match",
                "selected-explicit-authoritative-no-match",
                "selected-authoritative-morphology-match-semantic-unresolved",
            ],
        )
        row["selectedExtraction"]["unresolvedIconOccurrences"] = []
        self.assertEqual(unresolved_symbols.unresolved_occurrences(row), [])

    def test_validator_rejects_malformed_registry(self) -> None:
        corpus = json.loads(DEFAULT_OUTPUT.read_text())
        registry = copy.deepcopy(self.registry)
        registry["entries"].append(copy.deepcopy(registry["entries"][0]))
        self.assert_corpus_validator_rejects(corpus, registry)


if __name__ == "__main__":
    unittest.main(verbosity=2)
