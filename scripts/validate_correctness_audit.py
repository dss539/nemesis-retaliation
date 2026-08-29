#!/usr/bin/env python3
"""Validate the frozen Stage 1 correctness-audit harness and artifacts.

Run through uv so JSON Schema 2020-12 and date-time formats are actually
validated:

    uv run --isolated --with-requirements \
      docs/qa/implementation-readiness/correctness-audit/requirements-audit.txt \
      python3 scripts/validate_correctness_audit.py
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    from jsonschema import Draft202012Validator, FormatChecker
except ImportError as exc:  # pragma: no cover - exercised by the documented runner
    raise SystemExit(
        "jsonschema is required; run with uv and requirements-audit.txt"
    ) from exc

ROOT = Path(__file__).resolve().parents[1]
AUDIT_DIR = ROOT / "docs/qa/implementation-readiness/correctness-audit"
MANIFEST_PATH = AUDIT_DIR / "manifest.json"
PROGRESS_PATH = AUDIT_DIR / "progress.json"
LOCK_PATH = AUDIT_DIR / "audit-lock.json"
REPORT_PATH = AUDIT_DIR / "validation.json"
SCHEMA_PATHS = {
    "packet": AUDIT_DIR / "source-packet.schema.json",
    "completeness": AUDIT_DIR / "packet-completeness-review.schema.json",
    "blind": AUDIT_DIR / "blind-derivation.schema.json",
    "result": AUDIT_DIR / "audit-result.schema.json",
}
HEX64 = re.compile(r"^[0-9a-f]{64}$")
HEX40 = re.compile(r"^[0-9a-f]{40}$")
EXPECTED_FAMILIES = {
    "room": 5,
    "intruder-help": 4,
    "event": 4,
    "exploration": 3,
    "robot": 2,
    "intruder-attack": 2,
    "queen-health": 2,
    "serious-wound": 2,
    "green-item": 2,
    "red-item": 2,
    "yellow-item": 2,
    "action-card": 12,
    "objective-mission": 6,
    "equipment-starting": 8,
}
EXPECTED_UNIVERSES = {
    "room": 25,
    "intruder-help": 18,
    "event": 20,
    "exploration": 12,
    "robot": 6,
    "intruder-attack": 20,
    "queen-health": 10,
    "serious-wound": 9,
    "green-item": 8,
    "red-item": 7,
    "yellow-item": 4,
    "action-card": 60,
    "objective-mission": 27,
    "equipment-starting": 37,
}
EXPECTED_THRESHOLDS = {
    "criticalErrors": 0,
    "inventedAuthorityOverrides": 0,
    "hiddenDefaults": 0,
    "recurringDefectPatterns": 0,
    "maximumIsolatedMaterialErrorsInComponentSample": 2,
    "sourceBlockedUnitsMustBeEnumerated": True,
    "readinessClaimMustEnumerateUnauditedComponentEffects": True,
}
STATUS_COUNT_KEYS = {
    "pending-blind-derivation": "pendingBlindDerivation",
    "blind-derived": "blindDerived",
    "compared": "compared",
    "accepted": "accepted",
    "material-error": "materialErrors",
    "critical-error": "criticalErrors",
    "source-blocked": "sourceBlocked",
}
ALLOWED_SOURCE_PREFIXES = (
    "docs/rulebooks/",
    "docs/rules/source-extraction/",
    "assets/tts-mod/extract/",
)
FORBIDDEN_PROMPT_TOKENS = (
    "docs/rules/semantics/",
    "docs/rules/00-foundations.md",
    "docs/rules/01-round-and-turns.md",
    "docs/rules/02-character-actions.md",
    "docs/rules/03-intruders-and-survival.md",
    "docs/rules/04-items-and-equipment.md",
    '"physicalClass"',
    '"batchDisposition"',
    '"equipmentStratum"',
    '"semanticRecordIds"',
)
TRACE_KEYS = {"thinking", "reasoningtrace", "chainofthought", "chain_of_thought"}


class DuplicateKeyError(ValueError):
    pass


def strict_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in pairs:
        if key in out:
            raise DuplicateKeyError(f"duplicate JSON key: {key}")
        out[key] = value
    return out


def strict_load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=strict_pairs)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def add(failures: list[str], condition: bool, message: str) -> None:
    if not condition:
        failures.append(message)


def repo_path(value: Any, failures: list[str], label: str, parent: Path = ROOT) -> Path | None:
    if not isinstance(value, str) or not value:
        failures.append(f"{label}: missing path")
        return None
    path = ROOT / value
    try:
        path.resolve().relative_to(parent.resolve())
    except ValueError:
        failures.append(f"{label}: path escapes {parent.relative_to(ROOT) if parent != ROOT else 'repository'}")
        return None
    return path


def checked_file(
    value: Any,
    expected_hash: Any,
    failures: list[str],
    label: str,
    parent: Path = ROOT,
) -> Path | None:
    path = repo_path(value, failures, label, parent)
    if path is None:
        return None
    add(failures, path.is_file(), f"{label}: file missing")
    add(failures, isinstance(expected_hash, str) and bool(HEX64.fullmatch(expected_hash)), f"{label}: invalid SHA-256")
    if path.is_file() and isinstance(expected_hash, str):
        add(failures, sha256_path(path) == expected_hash, f"{label}: SHA-256 mismatch")
    return path


def schema_validators(failures: list[str]) -> dict[str, Draft202012Validator]:
    validators: dict[str, Draft202012Validator] = {}
    for name, path in SCHEMA_PATHS.items():
        try:
            schema = strict_load(path)
            Draft202012Validator.check_schema(schema)
            validators[name] = Draft202012Validator(schema, format_checker=FormatChecker())
        except Exception as exc:
            failures.append(f"{name} schema invalid: {exc}")
    return validators


def apply_schema(
    name: str,
    value: Any,
    validators: dict[str, Draft202012Validator],
    failures: list[str],
    label: str,
) -> bool:
    validator = validators.get(name)
    if validator is None:
        return False
    errors = sorted(validator.iter_errors(value), key=lambda err: list(err.absolute_path))
    for err in errors:
        location = "/".join(str(part) for part in err.absolute_path) or "<root>"
        failures.append(f"{label}: schema {location}: {err.message}")
    return not errors


def git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=ROOT, text=True, capture_output=True)


def validate_lock(manifest: dict[str, Any], failures: list[str], require_lock: bool) -> None:
    if not LOCK_PATH.is_file():
        add(failures, not require_lock, "audit-lock.json is required after setup checkpoint")
        return
    try:
        lock = strict_load(LOCK_PATH)
    except Exception as exc:
        failures.append(f"audit lock parse: {exc}")
        return
    expected_keys = {
        "schemaVersion",
        "recordType",
        "auditVersion",
        "baselineCommit",
        "lockedStartingHead",
        "manifestSha256",
        "initialProgressSha256",
        "lockedFiles",
        "changePolicy",
    }
    add(failures, set(lock) == expected_keys, "audit lock top-level keys drift")
    add(failures, lock.get("schemaVersion") == 1, "audit lock schemaVersion")
    add(failures, lock.get("recordType") == "stage-1-correctness-audit-git-lock", "audit lock recordType")
    add(failures, lock.get("auditVersion") == manifest.get("auditVersion"), "audit lock version mismatch")
    add(failures, lock.get("lockedStartingHead") == manifest.get("lockedStartingHead"), "audit lock starting HEAD mismatch")
    add(failures, lock.get("manifestSha256") == sha256_path(MANIFEST_PATH), "audit lock manifest hash mismatch")
    baseline = lock.get("baselineCommit")
    if not isinstance(baseline, str) or not HEX40.fullmatch(baseline):
        failures.append("audit lock baseline commit invalid")
        return
    add(failures, git("cat-file", "-e", f"{baseline}^{{commit}}").returncode == 0, "audit lock baseline commit missing")
    add(failures, git("merge-base", "--is-ancestor", baseline, "HEAD").returncode == 0, "audit baseline is not an ancestor of HEAD")
    starting = str(lock.get("lockedStartingHead", ""))
    add(failures, bool(HEX40.fullmatch(starting)), "lockedStartingHead invalid")
    if HEX40.fullmatch(starting):
        add(failures, git("merge-base", "--is-ancestor", starting, baseline).returncode == 0, "starting HEAD is not an ancestor of baseline")
    tracked = git("ls-files", "--error-unmatch", str(LOCK_PATH.relative_to(ROOT)))
    add(failures, tracked.returncode == 0, "audit lock is not tracked")
    add(failures, git("diff", "--quiet", "HEAD", "--", str(LOCK_PATH.relative_to(ROOT))).returncode == 0, "audit lock has uncommitted drift")

    locked_files = lock.get("lockedFiles", {})
    add(failures, isinstance(locked_files, dict) and bool(locked_files), "audit lock files absent")
    if isinstance(locked_files, dict):
        for relative, expected_hash in locked_files.items():
            current = ROOT / relative
            add(failures, current.is_file(), f"locked file missing: {relative}")
            if current.is_file():
                add(failures, sha256_path(current) == expected_hash, f"locked file drift: {relative}")
            shown = git("show", f"{baseline}:{relative}")
            add(failures, shown.returncode == 0, f"locked file absent from baseline: {relative}")
            if shown.returncode == 0:
                add(failures, sha256_bytes(shown.stdout.encode()) == expected_hash, f"baseline hash mismatch: {relative}")
    shown_progress = git("show", f"{baseline}:{PROGRESS_PATH.relative_to(ROOT)}")
    add(failures, shown_progress.returncode == 0, "initial progress absent from baseline")
    if shown_progress.returncode == 0:
        add(
            failures,
            sha256_bytes(shown_progress.stdout.encode()) == lock.get("initialProgressSha256"),
            "initial progress baseline hash mismatch",
        )


def contains_trace_key(value: Any) -> bool:
    if isinstance(value, dict):
        return any(str(key).lower() in TRACE_KEYS or contains_trace_key(child) for key, child in value.items())
    if isinstance(value, list):
        return any(contains_trace_key(child) for child in value)
    return False


def reviewer_identity(reviewer: Any) -> tuple[Any, ...]:
    if not isinstance(reviewer, dict):
        return (None,)
    return (
        reviewer.get("kind"),
        reviewer.get("provider"),
        reviewer.get("responseModel"),
        reviewer.get("responsePath"),
    )


def validate_reviewer(reviewer: Any, failures: list[str], label: str) -> dict[str, Any] | None:
    if not isinstance(reviewer, dict):
        failures.append(f"{label}: reviewer missing")
        return None
    if reviewer.get("kind") != "model-assisted":
        return None
    response = checked_file(
        reviewer.get("responsePath"),
        reviewer.get("responseSha256"),
        failures,
        f"{label} response",
        AUDIT_DIR / "reviews" / "raw",
    )
    if reviewer.get("provider") == "ollama-cloud":
        add(failures, reviewer.get("requestedReasoning") == "max", f"{label}: Ollama review was not max reasoning")
    if response and response.is_file():
        try:
            body = strict_load(response)
            add(failures, not contains_trace_key(body), f"{label}: retained provider reasoning trace")
            add(failures, body.get("recordType") == "ollama-cloud-audit-review", f"{label}: response is not a successful review envelope")
            add(failures, body.get("provider") == reviewer.get("provider"), f"{label}: provider provenance mismatch")
            add(failures, body.get("requestedModel") == reviewer.get("requestedModel"), f"{label}: requested-model provenance mismatch")
            add(failures, body.get("responseModel") == reviewer.get("responseModel"), f"{label}: response-model provenance mismatch")
            add(failures, body.get("requestedReasoning") == reviewer.get("requestedReasoning"), f"{label}: reasoning provenance mismatch")
            add(failures, body.get("thinkingRetained") is False, f"{label}: response did not attest to discarded reasoning")
            checked_file(
                body.get("promptPath"),
                body.get("promptSha256"),
                failures,
                f"{label} prompt provenance",
                ROOT,
            )
            return body
        except Exception as exc:
            failures.append(f"{label}: response parse: {exc}")
    return None


def is_allowed_source(relative: str) -> bool:
    return any(relative.startswith(prefix) for prefix in ALLOWED_SOURCE_PREFIXES)


def validate_packet(
    path: Path,
    validators: dict[str, Draft202012Validator],
    manifest_ids: set[str],
    failures: list[str],
) -> dict[str, Any] | None:
    try:
        packet = strict_load(path)
    except Exception as exc:
        failures.append(f"packet parse {path}: {exc}")
        return None
    apply_schema("packet", packet, validators, failures, str(path.relative_to(ROOT)))
    validate_seal_head(packet, failures, f"{path}: packet")
    packet_ids = packet.get("auditUnitIds", [])
    add(failures, set(packet_ids).issubset(manifest_ids), f"{path}: unknown audit unit")
    for index, row in enumerate(packet.get("sourceDocuments", [])):
        relative = row.get("sourcePath", "") if isinstance(row, dict) else ""
        add(failures, is_allowed_source(relative), f"{path}: disallowed source document {relative}")
        checked_file(relative, row.get("sourceSha256") if isinstance(row, dict) else None, failures, f"{path}: sourceDocument[{index}]")
    for index, row in enumerate(packet.get("evidence", [])):
        if not isinstance(row, dict):
            continue
        relative = row.get("sourcePath", "")
        add(failures, is_allowed_source(relative), f"{path}: disallowed evidence source {relative}")
        checked_file(relative, row.get("sourceSha256"), failures, f"{path}: evidence[{index}]")
        visual = row.get("visualEvidencePath")
        if visual is not None:
            checked_file(
                visual,
                row.get("visualEvidenceSha256"),
                failures,
                f"{path}: visualEvidence[{index}]",
                AUDIT_DIR / "packets",
            )
    for index, row in enumerate(packet.get("searchCoverage", {}).get("searchedSourcePaths", [])):
        if not isinstance(row, dict):
            continue
        relative = row.get("sourcePath", "")
        add(failures, is_allowed_source(relative), f"{path}: disallowed searched source {relative}")
        checked_file(relative, row.get("sourceSha256"), failures, f"{path}: searchedSource[{index}]")
    add(failures, packet.get("sourceOnlyAttestation") is True, f"{path}: no source-only attestation")
    add(failures, packet.get("forbiddenDownstreamSourcesIncluded") == [], f"{path}: downstream source included")
    return packet


def parse_time(value: Any, failures: list[str], label: str) -> datetime | None:
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except Exception:
        failures.append(f"{label}: invalid date-time")
        return None


def validate_seal_head(value: Any, failures: list[str], label: str) -> None:
    head = value.get("sealedAtGitHead") if isinstance(value, dict) else None
    if not isinstance(head, str) or not HEX40.fullmatch(head):
        failures.append(f"{label}: invalid seal Git HEAD")
        return
    add(
        failures,
        git("cat-file", "-e", f"{head}^{{commit}}").returncode == 0,
        f"{label}: seal Git HEAD does not exist",
    )
    if LOCK_PATH.is_file():
        try:
            baseline = strict_load(LOCK_PATH).get("baselineCommit")
        except Exception:
            baseline = None
        if isinstance(baseline, str) and HEX40.fullmatch(baseline):
            add(
                failures,
                git("merge-base", "--is-ancestor", baseline, head).returncode == 0,
                f"{label}: seal Git HEAD predates audit baseline",
            )


def validate_blind(
    path: Path,
    validators: dict[str, Draft202012Validator],
    manifest_ids: set[str],
    failures: list[str],
) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    try:
        blind = strict_load(path)
    except Exception as exc:
        failures.append(f"blind parse {path}: {exc}")
        return None, None
    apply_schema("blind", blind, validators, failures, str(path.relative_to(ROOT)))
    validate_seal_head(blind, failures, f"{path}: blind derivation")
    packet_path = checked_file(blind.get("packetPath"), blind.get("packetSha256"), failures, f"{path}: packet", AUDIT_DIR / "packets")
    packet = validate_packet(packet_path, validators, manifest_ids, failures) if packet_path and packet_path.is_file() else None
    review_path = checked_file(
        blind.get("completenessReviewPath"),
        blind.get("completenessReviewSha256"),
        failures,
        f"{path}: completeness review",
        AUDIT_DIR / "packets",
    )
    review = None
    if review_path and review_path.is_file():
        try:
            review = strict_load(review_path)
            apply_schema("completeness", review, validators, failures, str(review_path.relative_to(ROOT)))
            validate_seal_head(review, failures, f"{path}: completeness review")
            finding_rows = [row for row in review.get("findings", []) if isinstance(row, dict)]
            finding_ids = [row.get("findingId") for row in finding_rows]
            add(failures, len(finding_ids) == len(set(finding_ids)), f"{path}: duplicate completeness finding ID")
            unresolved_material = {
                row.get("findingId")
                for row in finding_rows
                if row.get("severity") in {"material", "critical"} and row.get("disposition") == "unresolved"
            }
            declared_unresolved = set(review.get("unresolvedMaterialFindingIds", []))
            add(failures, declared_unresolved == unresolved_material, f"{path}: unresolved material finding index mismatch")
            add(failures, review.get("accepted") is (not unresolved_material), f"{path}: completeness acceptance contradicts findings")
            add(failures, review.get("packetPath") == blind.get("packetPath"), f"{path}: completeness packet path mismatch")
            add(failures, review.get("packetSha256") == blind.get("packetSha256"), f"{path}: completeness packet hash mismatch")
            add(failures, review.get("accepted") is True, f"{path}: packet completeness not accepted")
            add(failures, review.get("unresolvedMaterialFindingIds") == [], f"{path}: unresolved packet findings")
            validate_reviewer(review.get("reviewer"), failures, f"{path}: completeness reviewer")
        except Exception as exc:
            failures.append(f"completeness review parse {review_path}: {exc}")
    prompt_path = checked_file(blind.get("promptPath"), blind.get("promptSha256"), failures, f"{path}: prompt", AUDIT_DIR / "packets")
    if prompt_path and prompt_path.is_file():
        text = prompt_path.read_text(encoding="utf-8")
        for token in FORBIDDEN_PROMPT_TOKENS:
            add(failures, token not in text, f"{path}: forbidden blind-prompt token {token}")
    blind_response = validate_reviewer(blind.get("reviewer"), failures, f"{path}: blind reviewer")
    if blind_response:
        add(failures, blind_response.get("promptPath") == blind.get("promptPath"), f"{path}: blind response prompt path mismatch")
        add(failures, blind_response.get("promptSha256") == blind.get("promptSha256"), f"{path}: blind response prompt hash mismatch")
    if review:
        add(
            failures,
            reviewer_identity(review.get("reviewer")) != reviewer_identity(blind.get("reviewer")),
            f"{path}: completeness and blind reviewer are not independent",
        )
    result_ids = [row.get("auditUnitId") for row in blind.get("unitResults", []) if isinstance(row, dict)]
    add(failures, len(result_ids) == len(set(result_ids)), f"{path}: duplicate blind unit result")
    if packet:
        add(failures, result_ids == packet.get("auditUnitIds"), f"{path}: submitted/returned unit IDs or order differ")
    packet_time = parse_time(packet.get("sealedAtUtc"), failures, f"{path}: packet time") if packet else None
    review_time = parse_time(review.get("sealedAtUtc"), failures, f"{path}: review time") if review else None
    blind_time = parse_time(blind.get("sealedAtUtc"), failures, f"{path}: blind time")
    if packet_time and review_time:
        add(failures, packet_time < review_time, f"{path}: completeness does not strictly follow packet seal")
    if review_time and blind_time:
        add(failures, review_time < blind_time, f"{path}: blind seal does not strictly follow completeness")
    return blind, packet


def expected_family(unit: dict[str, Any]) -> str:
    if unit.get("unitClass") == "sampled-component-effect":
        return str(unit.get("family"))
    if unit.get("unitClass") == "concise-rule-record":
        return "concise-rule"
    return "faq"


def validate_result(
    path: Path,
    blind: dict[str, Any],
    unit: dict[str, Any],
    validators: dict[str, Draft202012Validator],
    failures: list[str],
) -> dict[str, Any] | None:
    try:
        result = strict_load(path)
    except Exception as exc:
        failures.append(f"result parse {path}: {exc}")
        return None
    apply_schema("result", result, validators, failures, str(path.relative_to(ROOT)))
    validate_seal_head(result, failures, f"{path}: result")
    unit_id = unit["auditUnitId"]
    add(failures, result.get("auditUnitId") == unit_id, f"{unit_id}: result ID mismatch")
    add(failures, result.get("family") == expected_family(unit), f"{unit_id}: result family mismatch")
    ref = result.get("blindDerivationRef", {})
    add(failures, ref.get("path") == str(path_from_root_for(blind)), f"{unit_id}: blind path mismatch")
    add(failures, ref.get("sha256") == sha256_path(ROOT / ref.get("path", "")) if isinstance(ref.get("path"), str) and (ROOT / ref.get("path", "")).is_file() else False, f"{unit_id}: blind ref hash mismatch")
    add(failures, ref.get("auditUnitId") == unit_id, f"{unit_id}: blind unit ref mismatch")
    validate_reviewer(result.get("comparator"), failures, f"{unit_id}: comparator")
    add(
        failures,
        reviewer_identity(result.get("comparator")) != reviewer_identity(blind.get("reviewer")),
        f"{unit_id}: comparator is not independent of blind reviewer",
    )
    discrepancies = result.get("comparison", {}).get("discrepancies", [])
    severities = [row.get("severity") for row in discrepancies if isinstance(row, dict)]
    classifications = [row.get("classification") for row in discrepancies if isinstance(row, dict)]
    authority_override = any(row.get("authorityOverride") is True for row in discrepancies if isinstance(row, dict))
    hidden_default = any(row.get("hiddenDefault") is True for row in discrepancies if isinstance(row, dict))
    status = result.get("status")
    if "critical" in severities or authority_override or hidden_default:
        add(failures, status == "critical-error" or status == "compared", f"{unit_id}: critical/authority/default status mismatch")
    elif "material" in severities:
        add(failures, status == "material-error" or status == "compared", f"{unit_id}: material status mismatch")
    elif "blocked" in severities:
        add(failures, status == "source-blocked" or status == "compared", f"{unit_id}: blocked status mismatch")
    elif status != "compared":
        add(failures, status == "accepted", f"{unit_id}: clean status mismatch")
    for index, row in enumerate(discrepancies):
        if not isinstance(row, dict):
            continue
        if row.get("severity") in {"material", "critical"}:
            add(failures, isinstance(row.get("rootCauseId"), str) and bool(row.get("rootCauseId")), f"{unit_id}: discrepancy {index} lacks root cause")
        if row.get("classification") == "authority-inversion":
            add(failures, row.get("authorityOverride") is True, f"{unit_id}: authority inversion flag false")
        if row.get("classification") == "hidden-default":
            add(failures, row.get("hiddenDefault") is True, f"{unit_id}: hidden-default flag false")
    discrepancy_ids = {row.get("discrepancyId") for row in discrepancies if isinstance(row, dict)}
    reviewed_ids: set[str] = set()
    for review in result.get("verificationReviews", []):
        if not isinstance(review, dict):
            continue
        validate_reviewer(review.get("reviewer"), failures, f"{unit_id}: verification reviewer")
        identity = reviewer_identity(review.get("reviewer"))
        add(failures, identity != reviewer_identity(result.get("comparator")), f"{unit_id}: verification reviewer equals comparator")
        add(failures, identity != reviewer_identity(blind.get("reviewer")), f"{unit_id}: verification reviewer equals blind reviewer")
        ids = set(review.get("reviewedDiscrepancyIds", []))
        add(failures, ids.issubset(discrepancy_ids), f"{unit_id}: verification references unknown discrepancy")
        reviewed_ids.update(ids)
    mandatory = {
        row.get("discrepancyId")
        for row in discrepancies
        if isinstance(row, dict)
        and (
            row.get("severity") in {"minor", "material", "critical", "blocked"}
            or row.get("classification")
            in {
                "source-ambiguity-preserved",
                "source-conflict-preserved",
                "presentation-only",
            }
        )
    }
    if status not in {"compared"}:
        add(failures, mandatory.issubset(reviewed_ids), f"{unit_id}: mandatory discrepancy lacks independent verification")
    blind_time = parse_time(blind.get("sealedAtUtc"), failures, f"{unit_id}: blind time")
    result_time = parse_time(result.get("sealedAtUtc"), failures, f"{unit_id}: result time")
    if blind_time and result_time:
        add(failures, blind_time < result_time, f"{unit_id}: comparison does not strictly follow blind seal")
    return result


def path_from_root_for(value: dict[str, Any]) -> str:
    marker = value.get("__validatedPath")
    return str(marker) if isinstance(marker, str) else ""


def validate(
    manifest_path: Path = MANIFEST_PATH,
    progress_path: Path = PROGRESS_PATH,
    check_builder: bool = True,
    require_lock: bool = True,
) -> dict[str, Any]:
    failures: list[str] = []
    if check_builder:
        check = subprocess.run(
            [sys.executable, str(ROOT / "scripts/build_correctness_audit_manifest.py"), "--check"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        add(failures, check.returncode == 0, f"manifest rebuild check failed: {check.stdout}{check.stderr}".strip())
    try:
        manifest = strict_load(manifest_path)
        progress = strict_load(progress_path)
    except Exception as exc:
        return {"passed": False, "failureCount": 1, "failures": [f"input parse: {exc}"]}
    validators = schema_validators(failures)

    add(failures, manifest.get("schemaVersion") == 1, "manifest schemaVersion")
    add(failures, manifest.get("auditVersion") == "stage1-v1", "manifest auditVersion")
    add(failures, manifest.get("recordType") == "stage-1-blind-correctness-audit-manifest", "manifest recordType")
    units = manifest.get("units", [])
    add(failures, isinstance(units, list) and len(units) == 140, "manifest must have 140 units")
    unit_ids = [row.get("auditUnitId") for row in units if isinstance(row, dict)]
    add(failures, len(unit_ids) == len(set(unit_ids)) == 140, "manifest unit IDs not unique/complete")
    unit_map = {row["auditUnitId"]: row for row in units if isinstance(row, dict) and "auditUnitId" in row}
    classes = Counter(row.get("unitClass") for row in units if isinstance(row, dict))
    add(failures, classes == Counter({"concise-rule-record": 56, "base-applicable-faq-unit": 28, "sampled-component-effect": 56}), "audit class counts")
    families = Counter(row.get("family") for row in units if isinstance(row, dict) and row.get("unitClass") == "sampled-component-effect")
    add(failures, dict(families) == EXPECTED_FAMILIES, "component family distribution")
    counts = manifest.get("counts", {})
    add(failures, counts.get("totalAuditUnits") == 140, "declared total count")
    add(failures, counts.get("conciseRuleRecords") == 56, "declared concise count")
    add(failures, counts.get("baseApplicableFaqUnits") == 28, "declared FAQ count")
    add(failures, counts.get("sampledComponentEffects") == 56, "declared component count")
    add(failures, counts.get("componentFamilies") == EXPECTED_FAMILIES, "declared family counts")
    add(failures, counts.get("componentCandidateUniverses") == EXPECTED_UNIVERSES, "candidate universe counts")
    add(failures, manifest.get("passThreshold") == EXPECTED_THRESHOLDS, "pass threshold drift")

    seed = manifest.get("seedMaterial")
    coverage: dict[str, dict[str, int]] = {}
    for row in units:
        if not isinstance(row, dict) or row.get("unitClass") != "sampled-component-effect":
            continue
        selection = row.get("selection", {})
        stratum = selection.get("stratum")
        expected_score = hashlib.sha256(f"{seed}|{stratum}|{row.get('sourceIdentity')}".encode()).hexdigest()
        add(failures, selection.get("score") == expected_score, f"selection score drift: {row.get('auditUnitId')}")
        candidate_count = selection.get("candidateCount")
        bucket = coverage.setdefault(str(stratum), {"eligibleCandidates": candidate_count, "selectedUnits": 0})
        add(failures, bucket["eligibleCandidates"] == candidate_count, f"candidate count differs within stratum: {stratum}")
        bucket["selectedUnits"] += 1
        checked_file(row.get("sourcePath"), row.get("sourceSha256"), failures, f"selected source: {row.get('auditUnitId')}")
    add(failures, manifest.get("selectionCoverage") == dict(sorted(coverage.items())), "selection coverage drift")

    for section in ("frozenSemanticHashes", "frozenConciseRuleHashes", "selectionInputHashes"):
        mapping = manifest.get(section, {})
        add(failures, isinstance(mapping, dict) and bool(mapping), f"{section} absent")
        if isinstance(mapping, dict):
            for relative, expected_hash in mapping.items():
                checked_file(relative, expected_hash, failures, f"{section}: {relative}")
    validate_lock(manifest, failures, require_lock)

    add(failures, progress.get("schemaVersion") == 1, "progress schemaVersion")
    add(failures, progress.get("recordType") == "stage-1-correctness-audit-progress", "progress recordType")
    add(failures, progress.get("manifestSha256") == sha256_path(manifest_path), "progress manifest hash")
    progress_units = progress.get("units", [])
    add(failures, isinstance(progress_units, list) and len(progress_units) == 140, "progress must have 140 units")
    progress_ids = [row.get("auditUnitId") for row in progress_units if isinstance(row, dict)]
    add(failures, progress_ids == unit_ids, "progress order/IDs differ from manifest")

    blind_cache: dict[str, dict[str, Any]] = {}
    status_counts = Counter()
    for row in progress_units:
        if not isinstance(row, dict):
            failures.append("non-object progress row")
            continue
        expected_keys = {
            "auditUnitId",
            "status",
            "blindPath",
            "blindSha256",
            "blindUnitResultId",
            "resultPath",
            "resultSha256",
            "lastUpdatedUtc",
        }
        unit_id = row.get("auditUnitId")
        add(failures, set(row) == expected_keys, f"progress keys drift: {unit_id}")
        status = row.get("status")
        add(failures, status in STATUS_COUNT_KEYS, f"invalid status: {unit_id}")
        status_counts[status] += 1
        blind_values = (row.get("blindPath"), row.get("blindSha256"), row.get("blindUnitResultId"))
        result_values = (row.get("resultPath"), row.get("resultSha256"))
        if status == "pending-blind-derivation":
            add(failures, all(value is None for value in blind_values + result_values), f"pending artifact attached: {unit_id}")
            add(failures, row.get("lastUpdatedUtc") is None, f"pending timestamp attached: {unit_id}")
            continue
        blind_path = checked_file(row.get("blindPath"), row.get("blindSha256"), failures, f"{unit_id}: blind", AUDIT_DIR / "blind")
        blind = None
        if blind_path and blind_path.is_file():
            relative = str(blind_path.relative_to(ROOT))
            blind = blind_cache.get(relative)
            if blind is None:
                blind, _ = validate_blind(blind_path, validators, set(unit_ids), failures)
                if blind is not None:
                    blind["__validatedPath"] = relative
                    blind_cache[relative] = blind
        if blind:
            blind_ids = [item.get("auditUnitId") for item in blind.get("unitResults", []) if isinstance(item, dict)]
            add(failures, unit_id in blind_ids, f"{unit_id}: blind batch lacks unit")
            add(failures, row.get("blindUnitResultId") == unit_id, f"{unit_id}: blind unit result key mismatch")
        if status == "blind-derived":
            add(failures, all(value is None for value in result_values), f"blind-derived unit has comparison result: {unit_id}")
            continue
        result_path = checked_file(row.get("resultPath"), row.get("resultSha256"), failures, f"{unit_id}: result", AUDIT_DIR / "comparisons")
        if result_path and result_path.is_file() and blind:
            result = validate_result(result_path, blind, unit_map[unit_id], validators, failures)
            if result:
                add(failures, result.get("status") == status, f"{unit_id}: progress/result status mismatch")
        add(failures, isinstance(row.get("lastUpdatedUtc"), str), f"{unit_id}: update timestamp missing")

    declared = progress.get("counts", {})
    add(failures, declared.get("total") == 140, "progress declared total")
    for status, key in STATUS_COUNT_KEYS.items():
        add(failures, declared.get(key) == status_counts.get(status, 0), f"progress count mismatch: {key}")

    return {
        "passed": not failures,
        "failureCount": len(failures),
        "counts": {
            "manifestUnits": len(units),
            "progressUnits": len(progress_units),
            "statuses": dict(sorted(status_counts.items())),
            "componentFamilies": dict(sorted(families.items())),
        },
        "auditDecisionReady": len(progress_units) == 140
        and all(row.get("status") in {"accepted", "material-error", "critical-error", "source-blocked"} for row in progress_units if isinstance(row, dict)),
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prelock", action="store_true", help="allow the one setup run before audit-lock.json is committed")
    args = parser.parse_args()
    report = validate(require_lock=not args.prelock)
    REPORT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
