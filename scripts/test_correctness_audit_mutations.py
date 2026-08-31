#!/usr/bin/env python3
"""Adversarial mutation controls for the Stage 1 audit harness."""

from __future__ import annotations

import binascii
import copy
import hashlib
import json
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
import zlib
from pathlib import Path
from unittest import mock

import validate_correctness_audit as target
import create_correctness_audit_lock as lock_target
import build_correctness_audit_manifest as manifest_target
import build_correctness_audit_prompt as prompt_target
import stage_correctness_audit_sources as stage_target
import advance_correctness_audit_progress as progress_target

ROOT = target.ROOT
AUDIT_DIR = target.AUDIT_DIR
MANIFEST = json.loads(target.MANIFEST_PATH.read_text(encoding="utf-8"))
PROGRESS = json.loads(target.PROGRESS_PATH.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def fixture_png(width: int = 64, height: int = 64) -> bytes:
    def chunk(kind: bytes, data: bytes) -> bytes:
        crc = binascii.crc32(kind + data) & 0xFFFFFFFF
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", crc)

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    scanlines = b"".join(b"\x00" + (b"\x80\x80\x80" * width) for _ in range(height))
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", zlib.compress(scanlines))
        + chunk(b"IEND", b"")
    )


def reviewer(name: str, prompt_path: Path, response_path: Path) -> dict[str, object]:
    return {
        "kind": "agent",
        "reviewerId": name,
        "provider": name,
        "requestedModel": name,
        "responseModel": name,
        "requestedReasoning": "max",
        "requestMode": "isolated-test",
        "promptPath": str(prompt_path.relative_to(ROOT)),
        "promptSha256": sha(prompt_path),
        "responsePath": str(response_path.relative_to(ROOT)),
        "responseSha256": sha(response_path),
        "thinkingRetained": False,
    }


class Harness:
    def __init__(self) -> None:
        for parent in (
            AUDIT_DIR / "packets",
            AUDIT_DIR / "blind",
            AUDIT_DIR / "comparisons",
            AUDIT_DIR / "adjudications",
            AUDIT_DIR / "reviews" / "raw",
        ):
            parent.mkdir(parents=True, exist_ok=True)
        self.packet_dir = Path(tempfile.mkdtemp(prefix=".mutation-", dir=AUDIT_DIR / "packets"))
        self.blind_dir = Path(tempfile.mkdtemp(prefix=".mutation-", dir=AUDIT_DIR / "blind"))
        self.comparison_dir = Path(tempfile.mkdtemp(prefix=".mutation-", dir=AUDIT_DIR / "comparisons"))
        self.adjudication_dir = Path(tempfile.mkdtemp(prefix=".mutation-", dir=AUDIT_DIR / "adjudications"))
        self.raw_dir = Path(tempfile.mkdtemp(prefix=".mutation-", dir=AUDIT_DIR / "reviews" / "raw"))
        self.temp = Path(tempfile.mkdtemp(prefix="correctness-audit-mutation-"))
        self.manifest_path = self.temp / "manifest.json"
        self.progress_path = self.temp / "progress.json"
        self.packet_path = self.packet_dir / "packet.json"
        self.review_path = self.packet_dir / "completeness.json"
        self.completeness_prompt_path = self.packet_dir / "completeness-prompt.txt"
        self.prompt_path = self.packet_dir / "blind-prompt.txt"
        self.visual_path = self.packet_dir / "visual.png"
        self.visual_path.write_bytes(fixture_png())
        self.blind_path = self.blind_dir / "blind.json"
        self.comparison_path = self.comparison_dir / "comparison.json"
        self.result_path = self.adjudication_dir / "result.json"
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
            "evidence": [{"evidenceId": "E1", "auditUnitIds": [unit_id], "sourcePath": source_rel, "sourceSha256": source_hash, "locator": "test locator", "evidenceKind": "official-text", "exactText": "fixture", "visualEvidencePath": str(self.visual_path.relative_to(ROOT)), "visualEvidenceSha256": sha(self.visual_path), "pdfPageIndex": 1, "renderDpi": 160}],
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
        self.completeness_prompt_path.write_bytes(
            target.canonical_prompt_bytes("completeness", self.packet_path)
        )
        self.completeness_response_path = self.raw_dir / "test-completeness-response.json"
        dump(self.completeness_response_path, {"reviewer": "test-completeness", "result": "accepted"})
        self.review = {
            "schemaVersion": 1,
            "recordType": "stage-1-packet-completeness-review",
            "reviewId": "mutation-review",
            "sealedAtUtc": "2026-08-29T00:01:00Z",
            "sealedAtGitHead": head,
            "packetPath": str(self.packet_path.relative_to(ROOT)),
            "packetSha256": sha(self.packet_path),
            "reviewer": reviewer(
                "test-completeness",
                self.completeness_prompt_path,
                self.completeness_response_path,
            ),
            "findings": [],
            "accepted": True,
            "unresolvedMaterialFindingIds": [],
        }
        dump(self.review_path, self.review)
        self.prompt_path.write_bytes(
            target.canonical_prompt_bytes("blind", self.packet_path, self.review_path)
        )
        self.blind_response_path = self.raw_dir / "test-blind-response.json"
        dump(self.blind_response_path, {"reviewer": "test-blind", "result": "derived"})
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
            "reviewer": reviewer("test-blind", self.prompt_path, self.blind_response_path),
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
        self.comparator_prompt_path = self.comparison_dir / "test-comparator-prompt.txt"
        self.comparator_prompt_path.write_text("Compare the sealed fixture.\n", encoding="utf-8")
        self.comparator_response_path = self.raw_dir / "test-comparator-response.json"
        dump(self.comparator_response_path, {"reviewer": "test-comparator", "result": "match"})
        self.comparison = {
            "schemaVersion": 2,
            "recordType": "stage-1-audit-comparison",
            "auditUnitId": unit_id,
            "sealedAtUtc": "2026-08-29T00:03:00Z",
            "sealedAtGitHead": head,
            "family": "concise-rule",
            "status": "compared",
            "blindDerivationRef": {
                "path": str(self.blind_path.relative_to(ROOT)),
                "sha256": sha(self.blind_path),
                "auditUnitId": unit_id,
            },
            "comparator": reviewer(
                "test-comparator",
                self.comparator_prompt_path,
                self.comparator_response_path,
            ),
            "comparison": {
                "revealedArtifacts": [
                    {
                        "path": self.manifest["units"][0]["downstreamPath"],
                        "sha256": self.manifest["frozenConciseRuleHashes"][
                            self.manifest["units"][0]["downstreamPath"]
                        ],
                        "role": "downstream-target",
                    },
                    {
                        "path": "docs/rules/semantics/pilots.json",
                        "sha256": self.manifest["frozenSemanticHashes"][
                            "docs/rules/semantics/pilots.json"
                        ],
                        "role": "semantic-projection",
                    },
                ],
                "semanticRecordIds": [],
                "questionIds": [],
                "conflictIds": [],
                "discrepancies": [{
                    "discrepancyId": "D1",
                    "classification": "match",
                    "severity": "none",
                    "rootCauseId": None,
                    "authorityOverride": False,
                    "hiddenDefault": False,
                    "claim": "fixture match",
                    "sourceFinding": "fixture",
                    "evidenceRefs": ["E1"],
                }],
            },
        }
        dump(self.comparison_path, self.comparison)
        self.result = {
            "schemaVersion": 1,
            "recordType": "stage-1-audit-adjudication",
            "auditUnitId": unit_id,
            "sealedAtUtc": "2026-08-29T00:04:00Z",
            "sealedAtGitHead": head,
            "family": "concise-rule",
            "status": "accepted",
            "comparisonRef": {
                "path": str(self.comparison_path.relative_to(ROOT)),
                "sha256": sha(self.comparison_path),
                "auditUnitId": unit_id,
            },
            "verificationReviews": [],
            "resolution": {
                "status": "not-required",
                "repairPaths": [],
                "verificationEvidenceRefs": [],
                "notes": "fixture",
            },
        }
        dump(self.result_path, self.result)
        row = self.progress["units"][0]
        row.update({
            "status": "accepted",
            "blindPath": str(self.blind_path.relative_to(ROOT)),
            "blindSha256": sha(self.blind_path),
            "blindUnitResultId": unit_id,
            "comparisonPath": str(self.comparison_path.relative_to(ROOT)),
            "comparisonSha256": sha(self.comparison_path),
            "resultPath": str(self.result_path.relative_to(ROOT)),
            "resultSha256": sha(self.result_path),
            "lastUpdatedUtc": "2026-08-29T00:03:00Z",
        })
        self.progress["counts"]["pendingBlindDerivation"] -= 1
        self.progress["counts"]["accepted"] += 1
        self.resign_packet_chain()

    def make_reviewer(self, name: str) -> dict[str, object]:
        prompt = self.comparison_dir / f"{name}-prompt.txt"
        response = self.raw_dir / f"{name}-response.json"
        prompt.write_text(f"Review fixture as {name}.\n", encoding="utf-8")
        dump(response, {"reviewer": name, "result": "fixture"})
        return reviewer(name, prompt, response)

    def write_reviewer_response(
        self,
        reviewer_record: dict[str, object],
        payload: dict[str, object],
    ) -> None:
        response_path = ROOT / str(reviewer_record["responsePath"])
        dump(response_path, payload)
        reviewer_record["responseSha256"] = sha(response_path)

    def write_inputs(self) -> None:
        dump(self.manifest_path, self.manifest)
        self.progress["manifestSha256"] = sha(self.manifest_path)
        dump(self.progress_path, self.progress)

    def resign_packet_chain(self, *, canonicalize_prompts: bool = True) -> None:
        dump(self.packet_path, self.packet)
        if canonicalize_prompts:
            self.completeness_prompt_path.write_bytes(
                target.canonical_prompt_bytes("completeness", self.packet_path)
            )
        self.review["packetSha256"] = sha(self.packet_path)
        self.review["reviewer"]["promptSha256"] = sha(self.completeness_prompt_path)
        self.write_reviewer_response(
            self.review["reviewer"],
            {
                "findings": self.review["findings"],
                "accepted": self.review["accepted"],
                "unresolvedMaterialFindingIds": self.review["unresolvedMaterialFindingIds"],
            },
        )
        dump(self.review_path, self.review)
        if canonicalize_prompts:
            self.prompt_path.write_bytes(
                target.canonical_prompt_bytes("blind", self.packet_path, self.review_path)
            )
        self.blind["packetSha256"] = sha(self.packet_path)
        self.blind["completenessReviewSha256"] = sha(self.review_path)
        self.blind["promptSha256"] = sha(self.prompt_path)
        self.blind["reviewer"]["promptSha256"] = sha(self.prompt_path)
        self.write_reviewer_response(
            self.blind["reviewer"],
            {"unitResults": self.blind["unitResults"]},
        )
        dump(self.blind_path, self.blind)
        self.comparison["blindDerivationRef"]["sha256"] = sha(self.blind_path)
        self.comparison["comparator"]["promptSha256"] = sha(self.comparator_prompt_path)
        self.write_reviewer_response(
            self.comparison["comparator"],
            {
                "auditUnitId": self.comparison["auditUnitId"],
                "comparison": self.comparison["comparison"],
            },
        )
        dump(self.comparison_path, self.comparison)
        self.result["comparisonRef"]["sha256"] = sha(self.comparison_path)
        for review in self.result.get("verificationReviews", []):
            if not isinstance(review, dict) or not isinstance(review.get("reviewer"), dict):
                continue
            reviewer_record = review["reviewer"]
            prompt_path = ROOT / str(reviewer_record["promptPath"])
            reviewer_record["promptSha256"] = sha(prompt_path)
            self.write_reviewer_response(
                reviewer_record,
                {
                    key: value
                    for key, value in review.items()
                    if key != "reviewer"
                },
            )
        dump(self.result_path, self.result)
        row = self.progress["units"][0]
        row["blindSha256"] = sha(self.blind_path)
        row["comparisonSha256"] = sha(self.comparison_path)
        row["resultSha256"] = sha(self.result_path)
        self.write_inputs()

    def resign_from_blind(self) -> None:
        dump(self.blind_path, self.blind)
        self.comparison["blindDerivationRef"]["sha256"] = sha(self.blind_path)
        dump(self.comparison_path, self.comparison)
        self.result["comparisonRef"]["sha256"] = sha(self.comparison_path)
        dump(self.result_path, self.result)
        row = self.progress["units"][0]
        row["blindSha256"] = sha(self.blind_path)
        row["comparisonSha256"] = sha(self.comparison_path)
        row["resultSha256"] = sha(self.result_path)
        self.write_inputs()

    def validate(self, *, enforce_seals: bool = False) -> dict[str, object]:
        return target.validate(
            self.manifest_path,
            self.progress_path,
            check_builder=False,
            require_lock=False,
            enforce_seals=enforce_seals,
        )

    def close(self) -> None:
        for path in (
            self.packet_dir,
            self.blind_dir,
            self.comparison_dir,
            self.adjudication_dir,
            self.raw_dir,
            self.temp,
        ):
            shutil.rmtree(path, ignore_errors=True)


class ArtifactSealGitTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="correctness-audit-seal-")
        self.root = Path(self.temp.name)
        self.git("init", "-q")
        self.git("config", "user.name", "Correctness Audit Test")
        self.git("config", "user.email", "audit-test@example.invalid")
        self.git("commit", "--allow-empty", "-q", "-m", "baseline")
        self.baseline = self.git("rev-parse", "HEAD").stdout.strip()
        self.artifact = self.root / "lane.json"

    def tearDown(self) -> None:
        self.temp.cleanup()

    def git(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", *args],
            cwd=self.root,
            text=True,
            capture_output=True,
            check=True,
        )

    def commit_artifact(self, preseal: str | None = None) -> tuple[dict[str, str], str]:
        record = {"sealedAtGitHead": preseal or self.baseline, "payload": "fixture"}
        dump(self.artifact, record)
        self.git("add", "lane.json")
        self.git("commit", "-q", "-m", "seal lane")
        return record, self.git("rev-parse", "HEAD").stdout.strip()

    def test_lock_creator_has_runnable_python_and_pinned_prelock_command(self) -> None:
        self.assertTrue(Path(lock_target.sys.executable).is_file())
        command = lock_target.prelock_validation_command("/test/uv")
        self.assertEqual(
            command,
            [
                "/test/uv",
                "run",
                "--isolated",
                "--with-requirements",
                str(lock_target.REQUIREMENTS),
                "python3",
                str(lock_target.ROOT / "scripts/validate_correctness_audit.py"),
                "--prelock",
            ],
        )

    def test_lock_creator_rejects_missing_and_nonancestor_starting_heads(self) -> None:
        self.assertEqual(
            lock_target.starting_head_failures("not-a-commit", self.baseline, root=self.root),
            ["lockedStartingHead is not a Git commit"],
        )
        main_branch = self.git("branch", "--show-current").stdout.strip()
        self.git("checkout", "-q", "--orphan", "unrelated-root")
        self.git("commit", "--allow-empty", "-q", "-m", "unrelated root")
        unrelated = self.git("rev-parse", "HEAD").stdout.strip()
        self.git("checkout", "-q", main_branch)
        self.assertEqual(
            lock_target.starting_head_failures(unrelated, self.baseline, root=self.root),
            ["lockedStartingHead is not an ancestor of baseline"],
        )
        self.git("checkout", "-q", "-b", "prebaseline-side")
        self.git("commit", "--allow-empty", "-q", "-m", "prebaseline side")
        self.git("checkout", "-q", main_branch)
        self.git("merge", "--no-ff", "-q", "-m", "prebaseline merge", "prebaseline-side")
        merge_baseline = self.git("rev-parse", "HEAD").stdout.strip()
        self.assertEqual(
            lock_target.starting_head_failures(
                self.baseline,
                merge_baseline,
                root=self.root,
            ),
            ["prebaseline audit history contains a merge commit"],
        )

    def test_required_lock_files_close_prelock_reviews_but_exclude_raw_lane(self) -> None:
        reviews = self.root / "docs/qa/implementation-readiness/correctness-audit/reviews"
        setup_review = reviews / "final-setup-review.json"
        raw_response = reviews / "raw" / "lane-response.json"
        setup_review.parent.mkdir(parents=True, exist_ok=True)
        raw_response.parent.mkdir(parents=True, exist_ok=True)
        setup_review.write_text("{}\n", encoding="utf-8")
        raw_response.write_text("{}\n", encoding="utf-8")
        locked = lock_target.required_locked_files(root=self.root)
        self.assertIn(setup_review.relative_to(self.root).as_posix(), locked)
        self.assertNotIn(raw_response.relative_to(self.root).as_posix(), locked)

    def test_committed_direct_child_seal_passes(self) -> None:
        record, seal_commit = self.commit_artifact()
        failures: list[str] = []
        actual = target.validate_artifact_seal(
            record,
            self.artifact,
            failures,
            "fixture",
            root=self.root,
        )
        self.assertEqual(actual, seal_commit)
        self.assertEqual(failures, [])

    def test_same_wave_artifacts_share_direct_child_seal(self) -> None:
        second_artifact = self.root / "lane-2.json"
        first_record = {"sealedAtGitHead": self.baseline, "payload": "first"}
        second_record = {"sealedAtGitHead": self.baseline, "payload": "second"}
        dump(self.artifact, first_record)
        dump(second_artifact, second_record)
        self.git("add", "lane.json", "lane-2.json")
        self.git("commit", "-q", "-m", "seal artifact wave")
        wave_commit = self.git("rev-parse", "HEAD").stdout.strip()
        for record, artifact in (
            (first_record, self.artifact),
            (second_record, second_artifact),
        ):
            failures: list[str] = []
            actual = target.validate_artifact_seal(
                record,
                artifact,
                failures,
                "fixture wave",
                root=self.root,
            )
            self.assertEqual(actual, wave_commit)
            self.assertEqual(failures, [])

    def test_multiple_commits_in_one_dependency_wave_are_rejected(self) -> None:
        self.assertEqual(
            target.single_wave_failures(
                {
                    "packet": {"a" * 40, "b" * 40},
                    "blind": {"c" * 40},
                }
            ),
            ["packet artifacts do not share one wave seal commit"],
        )

    def test_later_modified_artifact_is_rejected(self) -> None:
        record, _ = self.commit_artifact()
        changed = dict(record)
        changed["payload"] = "modified after seal"
        dump(self.artifact, changed)
        failures: list[str] = []
        target.validate_artifact_seal(record, self.artifact, failures, "fixture", root=self.root)
        self.assertTrue(any("current artifact bytes differ" in row for row in failures), failures)

    def test_committed_change_with_worktree_revert_is_rejected(self) -> None:
        record, _ = self.commit_artifact()
        changed = dict(record)
        changed["payload"] = "committed change"
        dump(self.artifact, changed)
        self.git("add", "lane.json")
        self.git("commit", "-q", "-m", "change artifact")
        dump(self.artifact, record)
        failures: list[str] = []
        target.validate_artifact_seal(record, self.artifact, failures, "fixture", root=self.root)
        self.assertTrue(any("current HEAD bytes differ" in row for row in failures), failures)

    def test_changed_then_reverted_commit_is_rejected(self) -> None:
        record, _ = self.commit_artifact()
        changed = dict(record)
        changed["payload"] = "temporary committed change"
        dump(self.artifact, changed)
        self.git("add", "lane.json")
        self.git("commit", "-q", "-m", "change artifact")
        dump(self.artifact, record)
        self.git("add", "lane.json")
        self.git("commit", "-q", "-m", "revert artifact bytes")
        failures: list[str] = []
        target.validate_artifact_seal(record, self.artifact, failures, "fixture", root=self.root)
        self.assertTrue(any("changed in Git history" in row for row in failures), failures)

    def test_merged_side_branch_mutation_is_rejected(self) -> None:
        record, seal_commit = self.commit_artifact()
        main_branch = self.git("branch", "--show-current").stdout.strip()
        self.git("checkout", "-q", "-b", "side-mutation")
        changed = dict(record)
        changed["payload"] = "side-branch mutation"
        dump(self.artifact, changed)
        self.git("add", "lane.json")
        self.git("commit", "-q", "-m", "mutate artifact on side branch")
        dump(self.artifact, record)
        self.git("add", "lane.json")
        self.git("commit", "-q", "-m", "restore artifact on side branch")
        self.git("checkout", "-q", main_branch)
        self.git("merge", "--no-ff", "-q", "-m", "merge restored side branch", "side-mutation")
        self.assertTrue(target.merge_commits_after(self.root, seal_commit))
        failures: list[str] = []
        target.validate_artifact_seal(record, self.artifact, failures, "fixture", root=self.root)
        self.assertTrue(any("changed in Git history" in row for row in failures), failures)
        self.assertIn(
            seal_commit,
            self.git("merge-base", "--all", seal_commit, "HEAD").stdout.split(),
        )

    def test_progress_transition_rejects_artifact_committed_later(self) -> None:
        artifact = {
            "sealedAtGitHead": self.baseline,
            "unitResults": [{"auditUnitId": "UNIT-1"}],
        }
        artifact_bytes = (json.dumps(artifact, indent=2) + "\n").encode()
        row = {
            "auditUnitId": "UNIT-1",
            "blindPath": "lane.json",
            "blindSha256": hashlib.sha256(artifact_bytes).hexdigest(),
        }
        failures = target.committed_transition_artifact_failures(
            row,
            "blind-derived",
            self.baseline,
            self.root,
            "fixture",
        )
        self.assertIn("fixture: transition artifact absent at progress commit", failures)
        self.artifact.write_bytes(artifact_bytes)
        self.git("add", "lane.json")
        self.git("commit", "-q", "-m", "seal artifact after transition")
        later = self.git("rev-parse", "HEAD").stdout.strip()
        self.assertEqual(
            target.committed_transition_artifact_failures(
                row,
                "blind-derived",
                later,
                self.root,
                "fixture",
            ),
            [],
        )

    def test_false_preseal_for_existing_path_is_rejected(self) -> None:
        _, seal_commit = self.commit_artifact()
        (self.root / "later.txt").write_text("later\n", encoding="utf-8")
        self.git("add", "later.txt")
        self.git("commit", "-q", "-m", "later commit")
        failures: list[str] = []
        target.validate_artifact_seal(
            {"sealedAtGitHead": seal_commit},
            self.artifact,
            failures,
            "fixture",
            root=self.root,
        )
        self.assertTrue(any("artifact path already existed" in row for row in failures), failures)

    def test_artifact_introduced_after_intervening_commit_is_rejected(self) -> None:
        (self.root / "intervening.txt").write_text("intervening\n", encoding="utf-8")
        self.git("add", "intervening.txt")
        self.git("commit", "-q", "-m", "intervening commit")
        record, _ = self.commit_artifact(self.baseline)
        failures: list[str] = []
        target.validate_artifact_seal(record, self.artifact, failures, "fixture", root=self.root)
        self.assertTrue(any("artifact was not committed directly" in row for row in failures), failures)

    def test_lane_preseal_must_equal_preceding_lane_commit(self) -> None:
        _, seal_commit = self.commit_artifact()
        failures: list[str] = []
        target.require_lane_preseal(
            {"sealedAtGitHead": self.baseline},
            seal_commit,
            failures,
            "fixture review",
        )
        self.assertEqual(
            failures,
            ["fixture review: pre-seal HEAD does not equal the preceding lane commit"],
        )

    def test_packet_cannot_share_the_audit_lock_commit(self) -> None:
        _, packet_commit = self.commit_artifact()
        failures: list[str] = []
        target.require_preseal_at_or_after(
            {"sealedAtGitHead": self.baseline},
            packet_commit,
            failures,
            "packet",
            root=self.root,
        )
        self.assertEqual(
            failures,
            ["packet: pre-seal HEAD predates the audit-lock commit"],
        )

    def test_adjudication_must_follow_every_comparison_commit(self) -> None:
        self.git("commit", "--allow-empty", "-q", "-m", "comparison a")
        comparison_a = self.git("rev-parse", "HEAD").stdout.strip()
        adjudication = {"sealedAtGitHead": comparison_a}
        self.artifact.write_text(json.dumps(adjudication) + "\n", encoding="utf-8")
        self.git("add", "lane.json")
        self.git("commit", "-q", "-m", "premature adjudication")
        self.git("commit", "--allow-empty", "-q", "-m", "comparison b")
        comparison_b = self.git("rev-parse", "HEAD").stdout.strip()
        failures: list[str] = []
        target.require_preseal_after_all(
            adjudication,
            (comparison_a, comparison_b),
            failures,
            "fixture adjudication",
            root=self.root,
        )
        self.assertEqual(
            failures,
            ["fixture adjudication: adjudication predates a Stage 1 comparison commit"],
        )

    def test_deleted_prebaseline_lane_artifact_is_still_detected(self) -> None:
        lane = self.root / lock_target.LANE_OUTPUT_ROOTS[0] / "leaked.json"
        lane.parent.mkdir(parents=True, exist_ok=True)
        lane.write_text("{}\n", encoding="utf-8")
        self.git("add", str(lane.relative_to(self.root)))
        self.git("commit", "-q", "-m", "premature lane artifact")
        lane.unlink()
        self.git("add", "-u")
        self.git("commit", "-q", "-m", "remove premature lane artifact")
        baseline = self.git("rev-parse", "HEAD").stdout.strip()
        self.assertEqual(
            lock_target.historical_lane_files(self.baseline, baseline, root=self.root),
            [str(lane.relative_to(self.root))],
        )
    def test_merged_deleted_prebaseline_lane_artifact_is_detected(self) -> None:
        main_branch = self.git("branch", "--show-current").stdout.strip()
        self.git("checkout", "-q", "-b", "prebaseline-lane-side")
        lane = self.root / lock_target.LANE_OUTPUT_ROOTS[0] / "side-leaked.json"
        lane.parent.mkdir(parents=True, exist_ok=True)
        lane.write_text("{}\n", encoding="utf-8")
        self.git("add", str(lane.relative_to(self.root)))
        self.git("commit", "-q", "-m", "side premature lane artifact")
        lane.unlink()
        self.git("add", "-u")
        self.git("commit", "-q", "-m", "remove side premature lane artifact")
        self.git("checkout", "-q", main_branch)
        self.git("merge", "--no-ff", "-q", "-m", "merge restored lane side", "prebaseline-lane-side")
        baseline = self.git("rev-parse", "HEAD").stdout.strip()
        self.assertEqual(
            lock_target.historical_lane_files(self.baseline, baseline, root=self.root),
            [str(lane.relative_to(self.root))],
        )


class PromptOutputPathTests(unittest.TestCase):
    def test_prompt_output_rejects_noncanonical_and_symlink_paths(self) -> None:
        with tempfile.TemporaryDirectory(prefix="correctness-audit-prompt-output-") as directory:
            original_root = prompt_target.ROOT
            original_audit = prompt_target.AUDIT_DIR
            try:
                prompt_target.ROOT = Path(directory)
                prompt_target.AUDIT_DIR = (
                    prompt_target.ROOT
                    / "docs/qa/implementation-readiness/correctness-audit"
                )
                prompt_root = prompt_target.AUDIT_DIR / "packets" / "prompts"
                prompt_root.mkdir(parents=True)
                (prompt_root / "real").mkdir()
                (prompt_root / "alias").symlink_to("real", target_is_directory=True)
                for value in (
                    "docs/qa/implementation-readiness/correctness-audit/packets/prompts/bad\\name.txt",
                    "docs/qa/implementation-readiness/correctness-audit/packets/prompts/sub/../bad.txt",
                    "docs/qa/implementation-readiness/correctness-audit/packets/prompts/alias/bad.txt",
                ):
                    with self.subTest(value=value):
                        with self.assertRaises(ValueError):
                            prompt_target.canonical_output_path(value)
            finally:
                prompt_target.ROOT = original_root
                prompt_target.AUDIT_DIR = original_audit


class SourceStagingPathTests(unittest.TestCase):
    def test_source_root_and_intermediate_symlinks_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory(prefix="correctness-audit-source-path-") as directory:
            root = Path(directory)
            real = root / "real-source"
            (real / "docs" / "rulebooks").mkdir(parents=True)
            direct_link = root / "source-link"
            direct_link.symlink_to(real, target_is_directory=True)
            with self.assertRaisesRegex(SystemExit, "--source-root contains a symlink component"):
                stage_target.reject_symlink_components(direct_link, "--source-root")
            with self.assertRaisesRegex(SystemExit, "source tree contains a symlink component"):
                stage_target.reject_symlink_components(
                    direct_link / "docs" / "rulebooks",
                    "source tree",
                )
            with self.assertRaisesRegex(SystemExit, "noncanonical source-relative path"):
                stage_target.target_path(Path("docs/rulebooks\\bad.pdf"))
            original_root = stage_target.ROOT
            try:
                stage_target.ROOT = root / "target"
                dangling = stage_target.ROOT / "docs" / "rulebooks" / "dangling.pdf"
                dangling.parent.mkdir(parents=True)
                dangling.symlink_to(root / "outside" / "created.pdf")
                with self.assertRaisesRegex(SystemExit, "target path contains a symlink"):
                    stage_target.target_path(Path("docs/rulebooks/dangling.pdf"))
                self.assertFalse((root / "outside" / "created.pdf").exists())
            finally:
                stage_target.ROOT = original_root


class PendingProgressRefreshTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="correctness-audit-refresh-")
        self.root = Path(self.temp.name)
        self.original_root = manifest_target.ROOT
        self.original_output = manifest_target.OUTPUT
        self.original_progress = manifest_target.PROGRESS
        manifest_target.ROOT = self.root
        manifest_target.OUTPUT = self.root / "manifest.json"
        manifest_target.PROGRESS = self.root / "progress.json"
        self.prior_manifest_bytes = (
            json.dumps(MANIFEST, indent=2, ensure_ascii=False) + "\n"
        ).encode()

    def tearDown(self) -> None:
        manifest_target.ROOT = self.original_root
        manifest_target.OUTPUT = self.original_output
        manifest_target.PROGRESS = self.original_progress
        self.temp.cleanup()

    def test_pending_v2_refresh_requires_exact_progress_contract(self) -> None:
        cases = (
            (
                "schemaVersion",
                lambda progress: progress.__setitem__("schemaVersion", 999),
                "schemaVersion drift",
            ),
            (
                "unexpected top-level field",
                lambda progress: progress.__setitem__("unexpected", True),
                "top-level fields drift",
            ),
            (
                "missing row field",
                lambda progress: progress["units"][0].pop("blindPath"),
                "row fields drift",
            ),
        )
        for label, mutate, expected in cases:
            with self.subTest(label=label):
                progress = json.loads(
                    manifest_target.progress_bytes(self.prior_manifest_bytes)
                )
                mutate(progress)
                manifest_target.PROGRESS.write_text(
                    json.dumps(progress, indent=2) + "\n",
                    encoding="utf-8",
                )
                with self.assertRaisesRegex(SystemExit, expected):
                    manifest_target.validate_progress_transition(
                        supersede_v1=False,
                        refresh_pending_v2=True,
                        prior_manifest_bytes=self.prior_manifest_bytes,
                    )


class ProgressHistoryContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.unit_ids = [row["auditUnitId"] for row in MANIFEST["units"]]
        self.baseline = copy.deepcopy(PROGRESS)

    @staticmethod
    def recount(progress: dict[str, object]) -> None:
        counts = {key: 0 for key in target.STATUS_COUNT_KEYS.values()}
        for row in progress["units"]:
            counts[target.STATUS_COUNT_KEYS[row["status"]]] += 1
        progress["counts"] = {"total": len(progress["units"]), **counts}

    def test_progress_history_accepts_one_step_and_rejects_skip_or_regression(self) -> None:
        blind = copy.deepcopy(self.baseline)
        row = blind["units"][0]
        row.update(
            {
                "status": "blind-derived",
                "blindPath": "docs/qa/implementation-readiness/correctness-audit/blind/unit.json",
                "blindSha256": "a" * 64,
                "blindUnitResultId": row["auditUnitId"],
                "lastUpdatedUtc": "2026-08-30T08:00:00Z",
            }
        )
        self.recount(blind)
        self.assertEqual(
            target.progress_snapshot_failures(
                self.baseline,
                blind,
                self.unit_ids,
                "legal blind transition",
            ),
            [],
        )

        skipped = copy.deepcopy(self.baseline)
        row = skipped["units"][0]
        row.update(
            {
                "status": "compared",
                "blindPath": "docs/qa/implementation-readiness/correctness-audit/blind/unit.json",
                "blindSha256": "a" * 64,
                "blindUnitResultId": row["auditUnitId"],
                "comparisonPath": "docs/qa/implementation-readiness/correctness-audit/comparisons/unit.json",
                "comparisonSha256": "b" * 64,
                "lastUpdatedUtc": "2026-08-30T08:00:00Z",
            }
        )
        self.recount(skipped)
        self.assertTrue(
            any(
                "invalid committed transition" in failure
                for failure in target.progress_snapshot_failures(
                    self.baseline,
                    skipped,
                    self.unit_ids,
                    "skipped transition",
                )
            )
        )

        compared = copy.deepcopy(blind)
        row = compared["units"][0]
        row.update(
            {
                "status": "compared",
                "comparisonPath": "docs/qa/implementation-readiness/correctness-audit/comparisons/unit.json",
                "comparisonSha256": "b" * 64,
                "lastUpdatedUtc": "2026-08-30T08:00:00Z",
            }
        )
        self.recount(compared)
        self.assertTrue(
            any(
                "non-increasing transition timestamp" in failure
                for failure in target.progress_snapshot_failures(
                    blind,
                    compared,
                    self.unit_ids,
                    "timestamp regression",
                )
            )
        )
        failures: list[str] = []
        self.assertIsNone(target.parse_time("2026-08-30", failures, "date-only"))
        self.assertTrue(any("invalid UTC date-time" in row for row in failures))
        reordered = {key: blind[key] for key in reversed(tuple(blind))}
        self.assertEqual(
            target.canonical_progress_bytes(blind),
            target.canonical_progress_bytes(reordered),
        )
        self.assertNotEqual(
            json.dumps(blind, indent=2).encode(),
            target.canonical_progress_bytes(blind),
        )


class ProgressUpdaterRollbackTests(unittest.TestCase):
    def test_updater_restores_progress_bytes_after_validation_failure(self) -> None:
        harness = Harness()
        original_progress_path = progress_target.PROGRESS
        try:
            progress = copy.deepcopy(PROGRESS)
            dump(harness.progress_path, progress)
            original = harness.progress_path.read_bytes()
            unit_id = progress["units"][0]["auditUnitId"]
            progress_target.PROGRESS = harness.progress_path
            argv = [
                "advance_correctness_audit_progress.py",
                "--unit",
                unit_id,
                "--to",
                "blind-derived",
                "--blind",
                str(harness.blind_path.relative_to(ROOT)),
            ]
            with mock.patch.object(sys, "argv", argv), mock.patch.object(
                progress_target.validation,
                "validate",
                return_value={"passed": False, "failures": ["forced failure"]},
            ):
                with self.assertRaisesRegex(SystemExit, "transition rolled back"):
                    progress_target.main()
            self.assertEqual(harness.progress_path.read_bytes(), original)
        finally:
            progress_target.PROGRESS = original_progress_path
            harness.close()


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
        report = self.h.validate()
        self.assertTrue(report["passed"], report["failures"])

    def test_hash_pinned_but_unrelated_completeness_response_is_rejected(self) -> None:
        dump(self.h.completeness_response_path, {"unrelated": True})
        self.h.review["reviewer"]["responseSha256"] = sha(self.h.completeness_response_path)
        dump(self.h.review_path, self.h.review)
        self.h.prompt_path.write_bytes(
            target.canonical_prompt_bytes("blind", self.h.packet_path, self.h.review_path)
        )
        self.h.blind["completenessReviewSha256"] = sha(self.h.review_path)
        self.h.blind["promptSha256"] = sha(self.h.prompt_path)
        self.h.blind["reviewer"]["promptSha256"] = sha(self.h.prompt_path)
        self.h.resign_from_blind()
        self.assertFails("completeness response content differs from sealed review")

    def test_hash_pinned_but_unrelated_blind_response_is_rejected(self) -> None:
        dump(self.h.blind_response_path, {"unrelated": True})
        self.h.blind["reviewer"]["responseSha256"] = sha(self.h.blind_response_path)
        self.h.resign_from_blind()
        self.assertFails("blind response content differs from sealed derivation")

    def test_hash_pinned_but_unrelated_verification_response_is_rejected(self) -> None:
        self.h.result["verificationReviews"] = [{
            "reviewId": "VR-UNRELATED",
            "reviewer": self.h.make_reviewer("unrelated-verifier"),
            "reviewedDiscrepancyIds": ["D1"],
            "sourceChecked": True,
            "finding": "confirmed",
            "disposition": "confirmed",
            "evidenceRefs": ["E1"],
        }]
        self.h.resign_packet_chain()
        review = self.h.result["verificationReviews"][0]
        response_path = ROOT / review["reviewer"]["responsePath"]
        dump(response_path, {"unrelated": True})
        review["reviewer"]["responseSha256"] = sha(response_path)
        dump(self.h.result_path, self.h.result)
        self.h.progress["units"][0]["resultSha256"] = sha(self.h.result_path)
        self.h.write_inputs()
        self.assertFails("verification response content differs from sealed review")

    def test_hash_pinned_but_unrelated_comparator_response_is_rejected(self) -> None:
        dump(
            self.h.comparator_response_path,
            {
                "auditUnitId": self.h.comparison["auditUnitId"],
                "comparison": {"unrelated": True},
            },
        )
        self.h.comparison["comparator"]["responseSha256"] = sha(
            self.h.comparator_response_path
        )
        dump(self.h.comparison_path, self.h.comparison)
        self.h.result["comparisonRef"]["sha256"] = sha(self.h.comparison_path)
        dump(self.h.result_path, self.h.result)
        self.h.progress["units"][0]["comparisonSha256"] = sha(self.h.comparison_path)
        self.h.progress["units"][0]["resultSha256"] = sha(self.h.result_path)
        self.h.write_inputs()
        self.assertFails("comparator response content differs from sealed comparison")

    def test_threshold_tamper_rejected(self) -> None:
        self.h.manifest["passThreshold"]["criticalErrors"] = 1
        self.h.write_inputs()
        self.assertFails("pass threshold drift")

    def test_candidate_universe_tamper_rejected(self) -> None:
        self.h.manifest["counts"]["componentCandidateUniverses"]["room"] = 24
        self.h.write_inputs()
        self.assertFails("candidate universe counts")

    def test_sampled_component_without_comparison_target_is_rejected(self) -> None:
        component = next(
            row
            for row in self.h.manifest["units"]
            if row.get("unitClass") == "sampled-component-effect"
        )
        component.pop("extractionPath", None)
        self.h.write_inputs()
        self.assertFails("sampled component lacks comparison target")

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

    def test_progress_schema_version_downgrade_rejected(self) -> None:
        self.h.progress["schemaVersion"] = 1
        self.h.write_inputs()
        self.assertFails("progress schemaVersion")

    def test_progress_timestamp_must_be_valid_datetime(self) -> None:
        self.h.progress["units"][0]["lastUpdatedUtc"] = "not-a-date"
        self.h.write_inputs()
        self.assertFails("progress update time: invalid UTC date-time")

    def test_comparison_cannot_embed_verification(self) -> None:
        self.h.comparison["verificationReviews"] = []
        self.h.resign_packet_chain()
        self.assertFails("verificationReviews")

    def test_revealed_artifact_hash_must_match_frozen_manifest(self) -> None:
        self.h.comparison["comparison"]["revealedArtifacts"][0]["sha256"] = "0" * 64
        self.h.resign_packet_chain()
        self.assertFails("revealed artifact hash differs from frozen source")

    def test_required_downstream_target_must_be_revealed(self) -> None:
        self.h.comparison["comparison"]["revealedArtifacts"] = [
            self.h.comparison["comparison"]["revealedArtifacts"][1]
        ]
        self.h.resign_packet_chain()
        self.assertFails("required downstream target was not revealed")

    def test_unknown_semantic_record_id_is_rejected(self) -> None:
        self.h.comparison["comparison"]["semanticRecordIds"] = ["SEM-FAKE"]
        self.h.resign_packet_chain()
        self.assertFails("unknown semanticRecordIds")

    def test_semantic_projection_is_required_for_every_comparison(self) -> None:
        self.h.comparison["comparison"]["revealedArtifacts"] = [
            self.h.comparison["comparison"]["revealedArtifacts"][0]
        ]
        self.h.resign_packet_chain()
        self.assertFails("required behavior projection was not revealed")

    def test_source_index_cannot_masquerade_as_semantic_projection(self) -> None:
        semantic = self.h.comparison["comparison"]["revealedArtifacts"][1]
        semantic.update(
            {
                "path": "docs/rules/semantics/facility-source-index.json",
                "sha256": self.h.manifest["frozenSemanticHashes"][
                    "docs/rules/semantics/facility-source-index.json"
                ],
                "role": "semantic-projection",
            }
        )
        self.h.resign_packet_chain()
        report = self.h.validate()
        self.assertFalse(report["passed"])
        self.assertTrue(
            any("semantic-projection role names a non-projection artifact" in row for row in report["failures"]),
            report["failures"],
        )
        self.assertTrue(
            any("required behavior projection was not revealed" in row for row in report["failures"]),
            report["failures"],
        )

    def test_adjudication_cannot_embed_comparison_payload(self) -> None:
        self.h.result["comparison"] = copy.deepcopy(self.h.comparison["comparison"])
        self.h.resign_packet_chain()
        self.assertFails("comparison")

    def test_compared_progress_cannot_attach_adjudication(self) -> None:
        row = self.h.progress["units"][0]
        row["status"] = "compared"
        self.h.progress["counts"]["accepted"] -= 1
        self.h.progress["counts"]["compared"] += 1
        self.h.write_inputs()
        self.assertFails("compared unit has final adjudication")

    def test_adjudication_verifier_must_differ_from_comparator(self) -> None:
        discrepancy_id = self.h.comparison["comparison"]["discrepancies"][0]["discrepancyId"]
        self.h.result["verificationReviews"] = [{
            "reviewId": "VR-SAME",
            "reviewer": copy.deepcopy(self.h.comparison["comparator"]),
            "reviewedDiscrepancyIds": [discrepancy_id],
            "sourceChecked": True,
            "finding": "same reviewer",
            "disposition": "confirmed",
            "evidenceRefs": ["E1"],
        }]
        self.h.resign_packet_chain()
        self.assertFails("verification reviewer equals comparator")

    def test_unconfirmed_verification_requires_superseding_comparison(self) -> None:
        discrepancy_id = self.h.comparison["comparison"]["discrepancies"][0]["discrepancyId"]
        self.h.result["verificationReviews"] = [{
            "reviewId": "VR-NOT-CONFIRMED",
            "reviewer": self.h.make_reviewer("independent-verifier"),
            "reviewedDiscrepancyIds": [discrepancy_id],
            "sourceChecked": True,
            "finding": "the comparison is not confirmed",
            "disposition": "not-confirmed",
            "evidenceRefs": ["E1"],
        }]
        self.h.resign_packet_chain()
        self.assertFails("unconfirmed comparison requires a superseding comparison")

    def test_result_status_downgrade_rejected(self) -> None:
        discrepancy = self.h.comparison["comparison"]["discrepancies"][0]
        discrepancy.update({"classification": "downstream-omission", "severity": "material", "rootCauseId": "RC-1"})
        self.h.resign_packet_chain()
        self.assertFails("material status mismatch")

    def test_packet_semantic_field_rejected_by_schema(self) -> None:
        self.h.packet["physicalClass"] = "ranged-weapon"
        dump(self.h.packet_path, self.h.packet)
        with self.assertRaisesRegex(ValueError, "forbidden identifier key physicalClass"):
            target.canonical_prompt_bytes("completeness", self.h.packet_path)

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
        self.assertFails("path is not a canonical repository-relative POSIX path")

    def test_backslash_paths_are_rejected_by_validator_and_prompt_builder(self) -> None:
        failures: list[str] = []
        self.assertIsNone(
            target.repo_path("docs/rulebooks\\fixture.pdf", failures, "backslash fixture")
        )
        self.assertTrue(any("canonical repository-relative POSIX path" in row for row in failures))
        with self.assertRaisesRegex(ValueError, "noncanonical path"):
            prompt_target.canonical_repo_file(
                ROOT / "docs" / "rulebooks\\fixture.pdf",
                ROOT / "docs" / "rulebooks",
            )

    def test_source_allowlist_traversal_rejected(self) -> None:
        traversal = "docs/rulebooks/../rules/semantics/event-source-index.json"
        target_path = target.ROOT / "docs/rules/semantics/event-source-index.json"
        target_hash = sha(target_path)
        self.h.packet["sourceDocuments"][0].update({"sourcePath": traversal, "sourceSha256": target_hash})
        self.h.packet["evidence"][0].update({"sourcePath": traversal, "sourceSha256": target_hash})
        self.h.packet["searchCoverage"]["searchedSourcePaths"][0].update({"sourcePath": traversal, "sourceSha256": target_hash})
        self.h.blind["unitResults"][0]["requirements"][0]["citations"][0]["sourcePath"] = traversal
        self.h.blind["unitResults"][0]["acceptanceScenarios"][0]["citations"][0]["sourcePath"] = traversal
        self.h.resign_packet_chain()
        self.assertFails("disallowed source document")

    def test_manifest_bound_source_evidence_cannot_be_substituted(self) -> None:
        manifest_bound = next(
            row
            for row in self.h.manifest["units"]
            if isinstance(row.get("sourcePath"), str)
            and isinstance(row.get("sourceSha256"), str)
        )
        fixture_unit = self.h.manifest["units"][0]
        fixture_unit["sourcePath"] = manifest_bound["sourcePath"]
        fixture_unit["sourceSha256"] = manifest_bound["sourceSha256"]
        self.h.resign_packet_chain()
        self.assertFails("lacks manifest-bound source evidence")

    def test_symlink_artifact_path_rejected(self) -> None:
        link = self.h.packet_dir / "packet-link.json"
        link.symlink_to(self.h.packet_path.name)
        link_rel = str(link.relative_to(target.ROOT))
        self.h.review["packetPath"] = link_rel
        self.h.review["packetSha256"] = sha(link)
        dump(self.h.review_path, self.h.review)
        self.h.blind["packetPath"] = link_rel
        self.h.blind["packetSha256"] = sha(link)
        self.h.blind["completenessReviewSha256"] = sha(self.h.review_path)
        dump(self.h.blind_path, self.h.blind)
        self.h.comparison["blindDerivationRef"]["sha256"] = sha(self.h.blind_path)
        dump(self.h.comparison_path, self.h.comparison)
        self.h.result["comparisonRef"]["sha256"] = sha(self.h.comparison_path)
        dump(self.h.result_path, self.h.result)
        self.h.progress["units"][0]["blindSha256"] = sha(self.h.blind_path)
        self.h.progress["units"][0]["comparisonSha256"] = sha(self.h.comparison_path)
        self.h.progress["units"][0]["resultSha256"] = sha(self.h.result_path)
        self.h.write_inputs()
        self.assertFails("symlink path component is forbidden")

    def test_canonical_source_only_prompts_reject_downstream_payloads(self) -> None:
        self.h.packet["searchCoverage"]["searchTerms"] = [
            "docs/rules/semantics/pilots.json"
        ]
        dump(self.h.packet_path, self.h.packet)
        with self.assertRaisesRegex(ValueError, "forbidden (?:path|identifier)"):
            prompt_target.canonical_prompt_bytes("completeness", self.h.packet_path)

        self.h.packet["searchCoverage"]["searchTerms"] = ["fixture"]
        dump(self.h.packet_path, self.h.packet)
        self.h.review["findings"] = [{
            "findingId": "F-LEAK",
            "severity": "minor",
            "claim": "js/engine.js downstreamPath",
            "evidenceRefs": ["E1"],
            "disposition": "rejected",
            "dispositionReason": "fixture",
        }]
        self.h.review["packetSha256"] = sha(self.h.packet_path)
        dump(self.h.review_path, self.h.review)
        with self.assertRaisesRegex(ValueError, "forbidden (?:path|identifier)"):
            prompt_target.canonical_prompt_bytes(
                "blind",
                self.h.packet_path,
                self.h.review_path,
            )

    def test_source_only_inventory_covers_frozen_paths_and_post_reveal_ids(self) -> None:
        forbidden_paths, forbidden_ids = prompt_target.source_only_forbidden_inventory()
        self.assertIn("scripts/build_semantic_pilots.py", forbidden_paths)
        self.assertTrue(
            {
                "rootCauseId",
                "authorityOverride",
                "classification",
                "hiddenDefault",
                "verificationEvidenceRefs",
                "reviewedDiscrepancyIds",
            }.issubset(forbidden_ids)
        )
        for identifier in sorted(forbidden_ids):
            self.assertTrue(
                prompt_target.source_only_payload_failures(
                    {"value": f"fixture {identifier} fixture"}
                )
            )
            self.assertTrue(
                prompt_target.source_only_payload_failures({identifier: "fixture"})
            )
        for path_token in sorted(forbidden_paths):
            self.assertTrue(
                prompt_target.source_only_payload_failures(
                    {"value": f"fixture {path_token} fixture"}
                )
            )
            self.assertTrue(
                prompt_target.source_only_payload_failures({path_token: "fixture"})
            )

    def test_duplicate_packet_evidence_ids_are_rejected(self) -> None:
        duplicate = copy.deepcopy(self.h.packet["evidence"][0])
        duplicate["locator"] = "different locator"
        self.h.packet["evidence"].append(duplicate)
        self.h.resign_packet_chain()
        self.assertFails("duplicate packet evidence ID")

    def test_packet_evidence_indexes_are_unit_scoped(self) -> None:
        packet = {
            "evidence": [
                {
                    "evidenceId": "E1",
                    "auditUnitIds": ["UNIT-A"],
                    "sourcePath": "source-a",
                    "sourceSha256": "a" * 64,
                },
                {
                    "evidenceId": "E2",
                    "auditUnitIds": ["UNIT-B"],
                    "sourcePath": "source-b",
                    "sourceSha256": "b" * 64,
                },
            ]
        }
        failures: list[str] = []
        ids, sources = target.packet_evidence_indexes(packet, failures, "fixture")
        self.assertEqual(failures, [])
        self.assertEqual(ids, {"UNIT-A": {"E1"}, "UNIT-B": {"E2"}})
        self.assertEqual(sources["UNIT-A"], {"source-a": "a" * 64})
        self.assertNotIn("source-b", sources["UNIT-A"])

    def test_blind_citation_must_be_exact_packet_evidence(self) -> None:
        self.h.blind["unitResults"][0]["requirements"][0]["citations"][0]["locator"] = "invented locator"
        self.h.resign_packet_chain()
        self.assertFails("citation is not exact packet evidence")

    def test_result_evidence_reference_must_resolve_to_packet(self) -> None:
        self.h.comparison["comparison"]["discrepancies"][0]["evidenceRefs"] = ["NOT-IN-PACKET"]
        self.h.resign_packet_chain()
        self.assertFails("cites evidence outside the source packet")

    def test_nonmatch_cannot_use_none_severity(self) -> None:
        self.h.comparison["comparison"]["discrepancies"][0]["classification"] = "downstream-omission"
        self.h.resign_packet_chain()
        self.assertFails("is not one of")

    def test_unknown_severity_does_not_fall_through_to_accepted(self) -> None:
        self.h.comparison["comparison"]["discrepancies"][0]["severity"] = "mystery"
        self.h.resign_packet_chain()
        self.assertFails("is not one of")

    def test_unhashable_discrepancy_id_reports_failure_instead_of_crashing(self) -> None:
        self.h.comparison["comparison"]["discrepancies"][0]["discrepancyId"] = []
        self.h.resign_packet_chain()
        self.assertFails("is not of type 'string'")

    def test_unhashable_verification_review_id_reports_failure(self) -> None:
        discrepancy_id = self.h.comparison["comparison"]["discrepancies"][0]["discrepancyId"]
        self.h.result["verificationReviews"] = [{
            "reviewId": [],
            "reviewer": self.h.make_reviewer("independent-verifier-invalid-id"),
            "reviewedDiscrepancyIds": [discrepancy_id],
            "sourceChecked": True,
            "finding": "invalid review id",
            "disposition": "confirmed",
            "evidenceRefs": ["E1"],
        }]
        self.h.resign_packet_chain()
        self.assertFails("is not of type 'string'")

    def test_repaired_verified_is_forbidden_in_frozen_audit_version(self) -> None:
        self.h.result["resolution"]["status"] = "repaired-verified"
        self.h.resign_packet_chain()
        self.assertFails("is not one of")

    def test_forbidden_prompt_token_rejected(self) -> None:
        self.h.prompt_path.write_text('Use "physicalClass" from downstream.\n', encoding="utf-8")
        self.h.resign_packet_chain(canonicalize_prompts=False)
        self.assertFails("forbidden blind-prompt token")

    def test_hand_edited_canonical_prompt_rejected(self) -> None:
        self.h.prompt_path.write_text(
            self.h.prompt_path.read_text(encoding="utf-8") + "\nbenign hand edit\n",
            encoding="utf-8",
        )
        self.h.resign_packet_chain(canonicalize_prompts=False)
        self.assertFails("prompt is not canonical")

    def test_unknown_completeness_evidence_reference_rejected(self) -> None:
        self.h.review["findings"] = [{
            "findingId": "F1",
            "severity": "material",
            "claim": "fixture",
            "evidenceRefs": ["NOT-IN-PACKET"],
            "disposition": "rejected",
            "dispositionReason": "fixture",
        }]
        self.h.resign_packet_chain()
        self.assertFails("cites evidence outside the source packet")

    def test_pdf_visual_must_equal_deterministic_page_render(self) -> None:
        source = ROOT / "docs/rulebooks/Nemesis_RT_Rulebook_official.pdf"
        manifest_units = {
            row["auditUnitId"]: row
            for row in self.h.manifest["units"]
        }
        schema_failures: list[str] = []
        validators = target.schema_validators(schema_failures)
        self.assertEqual(schema_failures, [])

        failures: list[str] = []
        target.validate_packet(
            self.h.packet_path,
            validators,
            manifest_units,
            failures,
            enforce_seals=True,
        )
        self.assertTrue(
            any("not the deterministic cited PDF page render" in row for row in failures),
            failures,
        )

        with tempfile.TemporaryDirectory(prefix="independent-pdf-render-") as directory:
            prefix = Path(directory) / "page"
            subprocess.run(
                [
                    "pdftoppm",
                    "-f",
                    "1",
                    "-l",
                    "1",
                    "-singlefile",
                    "-png",
                    "-r",
                    "160",
                    str(source),
                    str(prefix),
                ],
                check=True,
                capture_output=True,
            )
            self.h.visual_path.write_bytes(prefix.with_suffix(".png").read_bytes())
        self.h.packet["evidence"][0]["visualEvidenceSha256"] = sha(self.h.visual_path)
        dump(self.h.packet_path, self.h.packet)
        failures = []
        target.validate_packet(
            self.h.packet_path,
            validators,
            manifest_units,
            failures,
            enforce_seals=True,
        )
        self.assertFalse(
            any("not the deterministic cited PDF page render" in row for row in failures),
            failures,
        )

        with tempfile.TemporaryDirectory(prefix="wrong-pdf-render-") as directory:
            prefix = Path(directory) / "page"
            subprocess.run(
                [
                    "pdftoppm",
                    "-f",
                    "2",
                    "-l",
                    "2",
                    "-singlefile",
                    "-png",
                    "-r",
                    "160",
                    str(source),
                    str(prefix),
                ],
                check=True,
                capture_output=True,
            )
            self.h.visual_path.write_bytes(prefix.with_suffix(".png").read_bytes())
        self.h.packet["evidence"][0]["visualEvidenceSha256"] = sha(self.h.visual_path)
        dump(self.h.packet_path, self.h.packet)
        failures = []
        target.validate_packet(
            self.h.packet_path,
            validators,
            manifest_units,
            failures,
            enforce_seals=True,
        )
        self.assertTrue(
            any("not the deterministic cited PDF page render" in row for row in failures),
            failures,
        )

        with tempfile.TemporaryDirectory(prefix="wrong-dpi-pdf-render-") as directory:
            prefix = Path(directory) / "page"
            subprocess.run(
                [
                    "pdftoppm",
                    "-f",
                    "1",
                    "-l",
                    "1",
                    "-singlefile",
                    "-png",
                    "-r",
                    "161",
                    str(source),
                    str(prefix),
                ],
                check=True,
                capture_output=True,
            )
            self.h.visual_path.write_bytes(prefix.with_suffix(".png").read_bytes())
        self.h.packet["evidence"][0]["visualEvidenceSha256"] = sha(self.h.visual_path)
        dump(self.h.packet_path, self.h.packet)
        failures = []
        target.validate_packet(
            self.h.packet_path,
            validators,
            manifest_units,
            failures,
            enforce_seals=True,
        )
        self.assertTrue(
            any("not the deterministic cited PDF page render" in row for row in failures),
            failures,
        )

    def test_visual_evidence_requires_hash(self) -> None:
        evidence = self.h.packet["evidence"][0]
        evidence["visualEvidencePath"] = str(self.h.prompt_path.relative_to(ROOT))
        evidence["visualEvidenceSha256"] = None
        self.h.resign_packet_chain()
        self.assertFails("is not of type 'string'")

    def test_text_file_masquerading_as_png_is_rejected(self) -> None:
        self.h.visual_path.write_text("not a rendered image\n", encoding="utf-8")
        self.h.packet["evidence"][0]["visualEvidenceSha256"] = sha(self.h.visual_path)
        self.h.resign_packet_chain()
        self.assertFails("missing PNG signature")

    def test_nonexistent_seal_commit_rejected(self) -> None:
        self.h.packet["sealedAtGitHead"] = "f" * 40
        self.h.resign_packet_chain()
        report = self.h.validate(enforce_seals=True)
        self.assertFalse(report["passed"])
        self.assertTrue(
            any("seal Git HEAD does not exist" in item for item in report["failures"]),
            report["failures"],
        )

    def test_uncommitted_lane_artifacts_rejected(self) -> None:
        report = self.h.validate(enforce_seals=True)
        self.assertFalse(report["passed"])
        self.assertTrue(
            any("artifact was not committed directly after its declared pre-seal HEAD" in item for item in report["failures"]),
            report["failures"],
        )

    def test_unresolved_material_completeness_finding_rejected(self) -> None:
        self.h.review["findings"] = [{
            "findingId": "F1",
            "severity": "material",
            "claim": "missing source",
            "evidenceRefs": ["E1"],
            "disposition": "unresolved",
            "dispositionReason": "fixture remains unresolved",
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
        self.h.resign_from_blind()
        self.assertFails("is not of type 'string'")

    def test_empty_agent_response_rejected(self) -> None:
        self.h.blind_response_path.write_bytes(b"")
        self.h.blind["reviewer"]["responseSha256"] = sha(self.h.blind_response_path)
        self.h.resign_from_blind()
        self.assertFails("reviewer response is empty")

    def test_packet_scope_and_hollow_evidence_rejected(self) -> None:
        self.h.packet["scope"] = "the concise rule is correct"
        evidence = self.h.packet["evidence"][0]
        evidence["exactText"] = ""
        evidence["visualEvidencePath"] = None
        evidence["visualEvidenceSha256"] = None
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
        discrepancy = self.h.comparison["comparison"]["discrepancies"][0]
        discrepancy.update({"classification": "downstream-omission", "severity": "material", "rootCauseId": None})
        self.h.result["status"] = "material-error"
        self.h.result["verificationReviews"] = [{
            "reviewId": "VR1",
            "reviewer": self.h.make_reviewer("test-verifier"),
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
        self.assertFails("is not of type 'string'")

    def test_classification_flags_are_required(self) -> None:
        discrepancy = self.h.comparison["comparison"]["discrepancies"][0]
        discrepancy.update({"classification": "authority-inversion", "severity": "critical", "rootCauseId": "RC1", "authorityOverride": False})
        self.h.resign_packet_chain()
        self.assertFails("True was expected")

    def test_final_nonmatch_requires_independent_verification(self) -> None:
        discrepancy = self.h.comparison["comparison"]["discrepancies"][0]
        discrepancy.update({"classification": "presentation-only", "severity": "minor", "rootCauseId": None})
        self.h.resign_packet_chain()
        self.assertFails("mandatory discrepancy lacks independent verification")

    def test_same_model_with_different_response_paths_is_not_independent(self) -> None:
        first = {
            "kind": "model-assisted",
            "reviewerId": "run-a",
            "provider": "ollama-cloud",
            "requestedModel": "same-model",
            "responseModel": "same-model:cloud",
            "responsePath": "reviews/raw/a.json",
        }
        second = dict(first, reviewerId="run-b", responsePath="reviews/raw/b.json")
        self.assertEqual(target.reviewer_identity(first), target.reviewer_identity(second))

    def test_agent_identity_ignores_provider_and_model_alias_fields(self) -> None:
        first = {
            "kind": "agent",
            "reviewerId": "stable-agent-42",
            "provider": "provider-a",
            "requestedModel": "alias-a",
            "responseModel": "resolved-a",
        }
        second = dict(
            first,
            provider="provider-b",
            requestedModel="alias-b",
            responseModel="resolved-b",
        )
        self.assertEqual(target.reviewer_identity(first), target.reviewer_identity(second))

    def test_model_identity_does_not_fall_back_to_requested_alias(self) -> None:
        first = {
            "kind": "model-assisted",
            "reviewerId": "run-a",
            "provider": "ollama-cloud",
            "requestedModel": "alias-a",
            "responseModel": "",
        }
        second = dict(first, reviewerId="run-b", requestedModel="alias-b")
        self.assertEqual(target.reviewer_identity(first), target.reviewer_identity(second))
        self.h.blind["reviewer"]["responseModel"] = ""
        self.h.resign_packet_chain()
        self.assertFails("should be non-empty")

    def test_schema_invalid_containers_fail_without_crashing(self) -> None:
        mutations = (
            lambda harness: harness.packet.__setitem__("auditUnitIds", [[]]),
            lambda harness: harness.packet.__setitem__("sourceDocuments", None),
            lambda harness: harness.packet.__setitem__("searchCoverage", []),
            lambda harness: harness.comparison["comparison"]["discrepancies"][0].__setitem__("evidenceRefs", [[]]),
            lambda harness: harness.comparison.__setitem__("comparison", []),
        )
        for mutation in mutations:
            harness = Harness()
            try:
                mutation(harness)
                harness.resign_packet_chain()
                report = harness.validate()
                self.assertFalse(report["passed"], report)
            finally:
                harness.close()

    def test_nonobject_manifest_and_progress_fail_without_crashing(self) -> None:
        for manifest_value, progress_value in (([], PROGRESS), (MANIFEST, [])):
            with tempfile.TemporaryDirectory(prefix="audit-nonobject-") as directory:
                root = Path(directory)
                manifest_path = root / "manifest.json"
                progress_path = root / "progress.json"
                dump(manifest_path, manifest_value)
                dump(progress_path, progress_value)
                report = target.validate(
                    manifest_path,
                    progress_path,
                    check_builder=False,
                    require_lock=False,
                    enforce_seals=False,
                )
                self.assertFalse(report["passed"], report)
                self.assertTrue(
                    any("must both be JSON objects" in row for row in report["failures"]),
                    report,
                )

    def test_model_response_envelope_rejects_type_and_key_drift(self) -> None:
        body = {
            "schemaVersion": [],
            "recordType": "ollama-cloud-audit-review",
            "provider": "ollama-cloud",
            "requestedModel": "model-a",
            "responseModel": "model-a:cloud",
            "requestedReasoning": "max",
            "stream": False,
            "format": "json",
            "promptPath": "prompt.txt",
            "promptSha256": "a" * 64,
            "responseCreatedAt": "2026-08-30T00:00:00Z",
            "done": True,
            "doneReason": "stop",
            "review": {},
            "thinkingRetained": False,
            "unexpected": True,
        }
        failures: list[str] = []
        self.assertFalse(target.valid_model_response_envelope(body, failures, "fixture"))
        self.assertTrue(any("keys drift" in failure for failure in failures))
        self.assertTrue(any("schemaVersion drift" in failure for failure in failures))
        body.pop("unexpected")
        body["schemaVersion"] = True
        failures = []
        self.assertFalse(target.valid_model_response_envelope(body, failures, "fixture"))
        self.assertTrue(any("schemaVersion drift" in failure for failure in failures))

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
                "stream": False,
                "format": "json",
                "promptPath": str(prompt.relative_to(target.ROOT)),
                "promptSha256": sha(prompt),
                "responseCreatedAt": "2026-08-30T00:00:00Z",
                "done": True,
                "doneReason": "stop",
                "review": {"verdict": "accept", "findings": []},
                "thinkingRetained": False,
            }
            dump(response, envelope)
            reviewer = {
                "kind": "model-assisted",
                "reviewerId": "model-reviewer-a",
                "provider": "ollama-cloud",
                "requestedModel": "model-a",
                "responseModel": "model-a:cloud",
                "requestedReasoning": "max",
                "requestMode": "isolated-test",
                "promptPath": str(prompt.relative_to(target.ROOT)),
                "promptSha256": sha(prompt),
                "responsePath": str(response.relative_to(target.ROOT)),
                "responseSha256": sha(response),
                "thinkingRetained": False,
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
