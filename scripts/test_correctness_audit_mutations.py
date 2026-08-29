#!/usr/bin/env python3
"""Adversarial mutation controls for the Stage 1 audit harness."""

from __future__ import annotations

import copy
import hashlib
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

import validate_correctness_audit as target

ROOT = target.ROOT
AUDIT_DIR = target.AUDIT_DIR
MANIFEST = json.loads(target.MANIFEST_PATH.read_text(encoding="utf-8"))
PROGRESS = json.loads(target.PROGRESS_PATH.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def reviewer(name: str) -> dict[str, object]:
    return {
        "kind": "agent",
        "provider": name,
        "requestedModel": name,
        "responseModel": name,
        "requestedReasoning": "max",
        "requestMode": "isolated-test",
        "responsePath": None,
        "responseSha256": None,
        "thinkingRetained": False,
    }


class Harness:
    def __init__(self) -> None:
        for parent in (AUDIT_DIR / "packets", AUDIT_DIR / "blind", AUDIT_DIR / "comparisons"):
            parent.mkdir(parents=True, exist_ok=True)
        self.packet_dir = Path(tempfile.mkdtemp(prefix=".mutation-", dir=AUDIT_DIR / "packets"))
        self.blind_dir = Path(tempfile.mkdtemp(prefix=".mutation-", dir=AUDIT_DIR / "blind"))
        self.comparison_dir = Path(tempfile.mkdtemp(prefix=".mutation-", dir=AUDIT_DIR / "comparisons"))
        self.temp = Path(tempfile.mkdtemp(prefix="correctness-audit-mutation-"))
        self.manifest_path = self.temp / "manifest.json"
        self.progress_path = self.temp / "progress.json"
        self.packet_path = self.packet_dir / "packet.json"
        self.review_path = self.packet_dir / "completeness.json"
        self.prompt_path = self.packet_dir / "prompt.txt"
        self.blind_path = self.blind_dir / "blind.json"
        self.result_path = self.comparison_dir / "result.json"
        self.manifest = copy.deepcopy(MANIFEST)
        self.progress = copy.deepcopy(PROGRESS)
        head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, capture_output=True, check=True).stdout.strip()
        source = ROOT / "docs/rulebooks/Nemesis_RT_Rulebook_official.pdf"
        source_rel = str(source.relative_to(ROOT))
        source_hash = sha(source)
        unit_id = self.manifest["units"][0]["auditUnitId"]
        self.packet = {
            "schemaVersion": 1,
            "recordType": "stage-1-source-only-audit-packet",
            "packetId": "mutation-packet",
            "sealedAtUtc": "2026-08-29T00:00:00Z",
            "sealedAtGitHead": head,
            "auditUnitIds": [unit_id],
            "scope": "base-competitive-stage1",
            "authorityOrder": ["official-rulebook"],
            "sourceDocuments": [{"sourcePath": source_rel, "sourceSha256": source_hash, "authority": "official-rulebook", "version": "test", "role": "primary-rule-text"}],
            "evidence": [{"evidenceId": "E1", "auditUnitIds": [unit_id], "sourcePath": source_rel, "sourceSha256": source_hash, "locator": "test locator", "evidenceKind": "official-text", "exactText": "fixture", "visualEvidencePath": None, "visualEvidenceSha256": None}],
            "searchCoverage": {
                "searchedSourcePaths": [{"sourcePath": source_rel, "sourceSha256": source_hash}],
                "searchTerms": ["fixture"],
                "neighboringSectionsChecked": ["neighbor fixture"],
                "faqUnitIdsChecked": [],
                "componentChannelsChecked": ["rulebook text and render"],
                "exclusions": [{"scope": "expansions", "reason": "out of scope"}],
            },
            "sourceOnlyAttestation": True,
            "forbiddenDownstreamSourcesIncluded": [],
        }
        dump(self.packet_path, self.packet)
        self.review = {
            "schemaVersion": 1,
            "recordType": "stage-1-packet-completeness-review",
            "reviewId": "mutation-review",
            "sealedAtUtc": "2026-08-29T00:01:00Z",
            "sealedAtGitHead": head,
            "packetPath": str(self.packet_path.relative_to(ROOT)),
            "packetSha256": sha(self.packet_path),
            "reviewer": reviewer("test-completeness"),
            "findings": [],
            "accepted": True,
            "unresolvedMaterialFindingIds": [],
        }
        dump(self.review_path, self.review)
        self.prompt_path.write_text("Derive the requested unit only from the attached packet.\n", encoding="utf-8")
        citation = {"sourcePath": source_rel, "locator": "test locator"}
        self.blind = {
            "schemaVersion": 1,
            "recordType": "stage-1-sealed-blind-derivation",
            "derivationId": "mutation-blind",
            "sealedAtUtc": "2026-08-29T00:02:00Z",
            "sealedAtGitHead": head,
            "packetPath": str(self.packet_path.relative_to(ROOT)),
            "packetSha256": sha(self.packet_path),
            "completenessReviewPath": str(self.review_path.relative_to(ROOT)),
            "completenessReviewSha256": sha(self.review_path),
            "promptPath": str(self.prompt_path.relative_to(ROOT)),
            "promptSha256": sha(self.prompt_path),
            "reviewer": reviewer("test-blind"),
            "unitResults": [{
                "auditUnitId": unit_id,
                "derivationStatus": "derived",
                "blocker": None,
                "requirements": [{
                    "requirementId": "R1",
                    "modality": "must",
                    "behavior": "fixture behavior",
                    "triggerTiming": "fixture timing",
                    "actorDecisionOwner": "fixture actor",
                    "targetCardinalityDecline": "no target; decline not applicable",
                    "visibility": "public",
                    "costsAndPayment": "no cost",
                    "orderedOperations": ["fixture operation"],
                    "finiteSupply": "not applicable",
                    "impossibleInstructions": "not applicable",
                    "partialResolution": "not applicable",
                    "citations": [citation],
                    "uncertainties": [],
                }],
                "ambiguities": [],
                "acceptanceScenarios": [{"scenarioId": "S1", "given": "fixture state", "when": "fixture action", "then": ["fixture outcome"], "citations": [citation]}],
                "unsafeAssumptions": [],
            }],
        }
        dump(self.blind_path, self.blind)
        self.result = {
            "schemaVersion": 2,
            "recordType": "stage-1-post-reveal-correctness-audit-result",
            "auditUnitId": unit_id,
            "sealedAtUtc": "2026-08-29T00:03:00Z",
            "sealedAtGitHead": head,
            "family": "concise-rule",
            "status": "accepted",
            "blindDerivationRef": {"path": str(self.blind_path.relative_to(ROOT)), "sha256": sha(self.blind_path), "auditUnitId": unit_id},
            "comparator": reviewer("test-comparator"),
            "comparison": {"revealedPaths": [], "semanticRecordIds": [], "questionIds": [], "conflictIds": [], "discrepancies": [{"discrepancyId": "D1", "classification": "match", "severity": "none", "rootCauseId": None, "authorityOverride": False, "hiddenDefault": False, "claim": "fixture match", "sourceFinding": "fixture", "evidenceRefs": ["E1"]}]},
            "verificationReviews": [],
            "resolution": {"status": "not-required", "repairPaths": [], "verificationEvidenceRefs": [], "notes": "fixture"},
        }
        dump(self.result_path, self.result)
        row = self.progress["units"][0]
        row.update({
            "status": "accepted",
            "blindPath": str(self.blind_path.relative_to(ROOT)),
            "blindSha256": sha(self.blind_path),
            "blindUnitResultId": unit_id,
            "resultPath": str(self.result_path.relative_to(ROOT)),
            "resultSha256": sha(self.result_path),
            "lastUpdatedUtc": "2026-08-29T00:03:00Z",
        })
        self.progress["counts"]["pendingBlindDerivation"] -= 1
        self.progress["counts"]["accepted"] += 1
        self.write_inputs()

    def write_inputs(self) -> None:
        dump(self.manifest_path, self.manifest)
        self.progress["manifestSha256"] = sha(self.manifest_path)
        dump(self.progress_path, self.progress)

    def resign_packet_chain(self) -> None:
        dump(self.packet_path, self.packet)
        self.review["packetSha256"] = sha(self.packet_path)
        dump(self.review_path, self.review)
        self.blind["packetSha256"] = sha(self.packet_path)
        self.blind["completenessReviewSha256"] = sha(self.review_path)
        self.blind["promptSha256"] = sha(self.prompt_path)
        dump(self.blind_path, self.blind)
        self.result["blindDerivationRef"]["sha256"] = sha(self.blind_path)
        dump(self.result_path, self.result)
        row = self.progress["units"][0]
        row["blindSha256"] = sha(self.blind_path)
        row["resultSha256"] = sha(self.result_path)
        self.write_inputs()

    def validate(self) -> dict[str, object]:
        return target.validate(self.manifest_path, self.progress_path, check_builder=False, require_lock=False)

    def close(self) -> None:
        for path in (self.packet_dir, self.blind_dir, self.comparison_dir, self.temp):
            shutil.rmtree(path, ignore_errors=True)


class AuditMutationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.h = Harness()

    def tearDown(self) -> None:
        self.h.close()

    def assertFails(self, needle: str) -> None:
        report = self.h.validate()
        self.assertFalse(report["passed"])
        self.assertTrue(any(needle in item for item in report["failures"]), report["failures"])

    def test_control_fixture_passes(self) -> None:
        self.assertTrue(self.h.validate()["passed"])

    def test_threshold_tamper_rejected(self) -> None:
        self.h.manifest["passThreshold"]["criticalErrors"] = 1
        self.h.write_inputs()
        self.assertFails("pass threshold drift")

    def test_candidate_universe_tamper_rejected(self) -> None:
        self.h.manifest["counts"]["componentCandidateUniverses"]["room"] = 24
        self.h.write_inputs()
        self.assertFails("candidate universe counts")

    def test_selection_coverage_tamper_rejected(self) -> None:
        first = next(iter(self.h.manifest["selectionCoverage"]))
        self.h.manifest["selectionCoverage"][first]["eligibleCandidates"] += 1
        self.h.write_inputs()
        self.assertFails("selection coverage drift")

    def test_pending_artifact_rejected(self) -> None:
        self.h.progress = copy.deepcopy(PROGRESS)
        self.h.progress["units"][0]["blindPath"] = str(self.h.blind_path.relative_to(ROOT))
        self.h.write_inputs()
        self.assertFails("pending artifact attached")

    def test_result_status_downgrade_rejected(self) -> None:
        discrepancy = self.h.result["comparison"]["discrepancies"][0]
        discrepancy.update({"classification": "downstream-omission", "severity": "material", "rootCauseId": "RC-1"})
        dump(self.h.result_path, self.h.result)
        self.h.progress["units"][0]["resultSha256"] = sha(self.h.result_path)
        self.h.write_inputs()
        self.assertFails("material status mismatch")

    def test_packet_semantic_field_rejected_by_schema(self) -> None:
        self.h.packet["physicalClass"] = "ranged-weapon"
        self.h.resign_packet_chain()
        self.assertFails("Additional properties are not allowed")

    def test_incomplete_search_record_rejected(self) -> None:
        self.h.packet["searchCoverage"]["searchTerms"] = []
        self.h.resign_packet_chain()
        self.assertFails("should be non-empty")

    def test_empty_derived_result_rejected(self) -> None:
        unit = self.h.blind["unitResults"][0]
        unit["requirements"] = []
        unit["acceptanceScenarios"] = []
        self.h.resign_packet_chain()
        self.assertFails("should be non-empty")

    def test_one_alternative_ambiguity_rejected(self) -> None:
        citation = self.h.blind["unitResults"][0]["requirements"][0]["citations"][0]
        self.h.blind["unitResults"][0]["ambiguities"] = [{"ambiguityId": "A1", "question": "fixture?", "alternatives": ["one"], "defaultProhibited": True, "citations": [citation]}]
        self.h.resign_packet_chain()
        self.assertFails("is too short")

    def test_packet_path_escape_rejected(self) -> None:
        outside = self.h.temp / "outside.json"
        outside.write_text("{}\n", encoding="utf-8")
        self.h.blind["packetPath"] = str(outside)
        self.h.blind["packetSha256"] = sha(outside)
        self.h.resign_packet_chain()
        self.assertFails("path escapes")

    def test_forbidden_prompt_token_rejected(self) -> None:
        self.h.prompt_path.write_text('Use "physicalClass" from downstream.\n', encoding="utf-8")
        self.h.resign_packet_chain()
        self.assertFails("forbidden blind-prompt token")

    def test_visual_evidence_requires_hash(self) -> None:
        evidence = self.h.packet["evidence"][0]
        evidence["visualEvidencePath"] = str(self.h.prompt_path.relative_to(ROOT))
        evidence["visualEvidenceSha256"] = None
        self.h.resign_packet_chain()
        self.assertFails("is not of type 'string'")

    def test_nonexistent_seal_commit_rejected(self) -> None:
        self.h.packet["sealedAtGitHead"] = "f" * 40
        self.h.resign_packet_chain()
        self.assertFails("seal Git HEAD does not exist")

    def test_unresolved_material_completeness_finding_rejected(self) -> None:
        self.h.review["findings"] = [{
            "findingId": "F1",
            "severity": "material",
            "claim": "missing source",
            "evidence": ["fixture"],
            "disposition": "unresolved",
        }]
        self.h.review["accepted"] = True
        self.h.review["unresolvedMaterialFindingIds"] = []
        self.h.resign_packet_chain()
        self.assertFails("unresolved material finding index mismatch")

    def test_blind_unit_omission_rejected(self) -> None:
        self.h.packet["auditUnitIds"].append("RULE:FND-002")
        self.h.resign_packet_chain()
        self.assertFails("submitted/returned unit IDs or order differ")

    def test_reviewer_path_without_hash_rejected(self) -> None:
        self.h.blind["reviewer"]["responsePath"] = str(self.h.prompt_path.relative_to(target.ROOT))
        self.h.blind["reviewer"]["responseSha256"] = None
        self.h.resign_packet_chain()
        self.assertFails("is not of type 'string'")

    def test_packet_scope_and_hollow_evidence_rejected(self) -> None:
        self.h.packet["scope"] = "the concise rule is correct"
        self.h.packet["evidence"][0]["exactText"] = ""
        self.h.resign_packet_chain()
        report = self.h.validate()
        self.assertFalse(report["passed"])
        joined = "\n".join(report["failures"])
        self.assertIn("base-competitive-stage1", joined)
        self.assertIn("is not valid under any of the given schemas", joined)

    def test_empty_blind_behavior_dimension_rejected(self) -> None:
        self.h.blind["unitResults"][0]["requirements"][0]["actorDecisionOwner"] = ""
        self.h.resign_packet_chain()
        self.assertFails("should be non-empty")

    def test_material_root_cause_is_required(self) -> None:
        discrepancy = self.h.result["comparison"]["discrepancies"][0]
        discrepancy.update({"classification": "downstream-omission", "severity": "material", "rootCauseId": None})
        self.h.result["status"] = "material-error"
        self.h.result["verificationReviews"] = [{
            "reviewId": "VR1",
            "reviewer": reviewer("test-verifier"),
            "reviewedDiscrepancyIds": ["D1"],
            "sourceChecked": True,
            "finding": "confirmed",
            "disposition": "confirmed",
            "evidenceRefs": ["E1"],
        }]
        row = self.h.progress["units"][0]
        row["status"] = "material-error"
        self.h.progress["counts"]["accepted"] -= 1
        self.h.progress["counts"]["materialErrors"] += 1
        self.h.resign_packet_chain()
        self.assertFails("lacks root cause")

    def test_classification_flags_are_required(self) -> None:
        discrepancy = self.h.result["comparison"]["discrepancies"][0]
        discrepancy.update({"classification": "authority-inversion", "severity": "critical", "rootCauseId": "RC1", "authorityOverride": False})
        self.h.resign_packet_chain()
        self.assertFails("authority inversion flag false")

    def test_final_nonmatch_requires_independent_verification(self) -> None:
        discrepancy = self.h.result["comparison"]["discrepancies"][0]
        discrepancy.update({"classification": "presentation-only", "severity": "minor", "rootCauseId": None})
        self.h.resign_packet_chain()
        self.assertFails("mandatory discrepancy lacks independent verification")

    def test_model_reviewer_provenance_mismatch_rejected(self) -> None:
        raw_root = target.AUDIT_DIR / "reviews" / "raw"
        raw_root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix=".reviewer-mutation-", dir=raw_root) as directory:
            directory = Path(directory)
            prompt = directory / "prompt.txt"
            response = directory / "response.json"
            prompt.write_text("Review this fixture.\n", encoding="utf-8")
            envelope = {
                "schemaVersion": 1,
                "recordType": "ollama-cloud-audit-review",
                "provider": "ollama-cloud",
                "requestedModel": "model-a",
                "responseModel": "model-a:cloud",
                "requestedReasoning": "max",
                "promptPath": str(prompt.relative_to(target.ROOT)),
                "promptSha256": sha(prompt),
                "review": {"verdict": "accept", "findings": []},
                "thinkingRetained": False,
            }
            dump(response, envelope)
            reviewer = {
                "kind": "model-assisted",
                "provider": "ollama-cloud",
                "requestedModel": "model-a",
                "responseModel": "model-a:cloud",
                "requestedReasoning": "max",
                "responsePath": str(response.relative_to(target.ROOT)),
                "responseSha256": sha(response),
            }
            failures: list[str] = []
            target.validate_reviewer(reviewer, failures, "fixture")
            self.assertEqual(failures, [])
            reviewer["responseModel"] = "substituted-model"
            failures = []
            target.validate_reviewer(reviewer, failures, "fixture")
            self.assertTrue(any("response-model provenance mismatch" in row for row in failures))

    def test_completeness_and_blind_reviewer_must_differ(self) -> None:
        self.h.blind["reviewer"] = copy.deepcopy(self.h.review["reviewer"])
        self.h.resign_packet_chain()
        self.assertFails("not independent")

    def test_seal_order_rejected(self) -> None:
        self.h.blind["sealedAtUtc"] = "2026-08-28T00:00:00Z"
        self.h.resign_packet_chain()
        self.assertFails("does not strictly follow completeness")

    def test_duplicate_json_key_rejected(self) -> None:
        path = self.h.temp / "duplicate.json"
        path.write_text('{"a": 1, "a": 2}\n', encoding="utf-8")
        with self.assertRaises(target.DuplicateKeyError):
            target.strict_load(path)


if __name__ == "__main__":
    unittest.main(verbosity=2)
