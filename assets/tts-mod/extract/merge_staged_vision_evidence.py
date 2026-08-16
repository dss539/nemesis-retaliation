#!/usr/bin/env python3
"""Merge a validated staged deferred run into durable selected evidence."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path

import build_card_text_corpus as corpus_builder
import card_text_evidence_registry as selected_evidence


def load(path: Path):
    return json.loads(path.read_text())


def relative_to_repo(path: Path, repo: Path) -> str:
    try:
        return path.resolve().relative_to(repo).as_posix()
    except ValueError as exc:
        raise SystemExit(f"artifact is outside repository: {path}") from exc


def validated_worker(repo: Path, worker: Path) -> tuple[dict, dict, list[tuple[dict, dict, Path]]]:
    assignment_path = worker / "assignment.json"
    validation_path = worker / "metadata/validation.json"
    report_path = worker / "metadata/worker-report.json"
    assignment = load(assignment_path)
    validation = load(validation_path)
    report = load(report_path)
    worker_id = assignment.get("workerId")
    if not isinstance(worker_id, str) or not worker_id:
        raise SystemExit("assignment workerId is malformed")
    if validation.get("workerId") != worker_id or report.get("workerId") != worker_id:
        raise SystemExit("worker identity mismatch across assignment, validation, and report")
    if not validation.get("overallPassed") or not report.get("validationPassed"):
        raise SystemExit("worker validation did not pass")
    if validation.get("errors") or validation.get("parseFailures"):
        raise SystemExit("worker validation contains errors or parse failures")
    if report.get("sharedWritesPerformed") or report.get("canonicalPromotionClaimed"):
        raise SystemExit("worker report claims forbidden shared write or promotion")
    assignment_sha = hashlib.sha256(assignment_path.read_bytes()).hexdigest()
    if validation.get("assignmentSha256") != assignment_sha:
        raise SystemExit("assignment SHA-256 does not match worker validation")
    assets = assignment.get("assets")
    if not isinstance(assets, list) or not assets:
        raise SystemExit("assignment assets must be a non-empty list")
    ordered_tuples = []
    expected_ids = []
    for asset in assets:
        if not isinstance(asset, dict):
            raise SystemExit("assignment asset is malformed")
        try:
            ordered_tuples.append((asset["assetId"], asset["sourcePath"], asset["sourceSha256"]))
        except KeyError as exc:
            raise SystemExit(f"assignment asset missing {exc.args[0]}") from exc
        expected_ids.append(asset["assetId"])
    tuple_digest = hashlib.sha256(json.dumps(ordered_tuples, separators=(",", ":")).encode()).hexdigest()
    if validation.get("orderedTupleDigest") != tuple_digest:
        raise SystemExit("ordered source tuple digest mismatch")
    if validation.get("expectedIds") != expected_ids or validation.get("rawIds") != expected_ids or validation.get("resultIds") != expected_ids:
        raise SystemExit("worker validation IDs do not exactly match assignment order")
    if validation.get("decisions") != {"defer": len(expected_ids)}:
        raise SystemExit("worker validation decisions are not exactly all deferred")
    if report.get("decisionCounts") != validation.get("decisions"):
        raise SystemExit("worker report decision counts mismatch validation")
    run_id = assignment.get("runId")
    if not isinstance(run_id, str) or not run_id:
        raise SystemExit("assignment runId is malformed")
    expected_model = assignment.get("model")
    if not isinstance(expected_model, dict) or any(not isinstance(expected_model.get(key), str) for key in ("provider", "model", "reasoningEffort")):
        raise SystemExit("assignment model provenance is malformed")
    if report.get("actualRuntime") != expected_model:
        raise SystemExit("reported runtime does not match assignment model")

    results = []
    for asset in assets:
        asset_id = asset["assetId"]
        raw_path = worker / "raw" / f"{asset_id}.json"
        result_path = worker / "results" / f"{asset_id}.json"
        if not raw_path.is_file() or not result_path.is_file():
            raise SystemExit(f"{asset_id} is missing raw or result evidence")
        load(raw_path)
        result = load(result_path)
        if result.get("assetId") != asset_id:
            raise SystemExit(f"{asset_id} result identity mismatch")
        if result.get("promotionDecision") != "defer":
            raise SystemExit(f"{asset_id} is not deferred; promotion gate requires separate handling")
        if result.get("sourcePath") != asset["sourcePath"] or result.get("sourceSha256") != asset["sourceSha256"]:
            raise SystemExit(f"{asset_id} result tuple mismatch")
        source = repo / asset["sourcePath"]
        if not source.is_file() or hashlib.sha256(source.read_bytes()).hexdigest() != asset["sourceSha256"]:
            raise SystemExit(f"{asset_id} live source tuple mismatch")
        runtime = result.get("runtimeProvenance")
        if not isinstance(runtime, dict) or {key: runtime.get(key) for key in expected_model} != expected_model:
            raise SystemExit(f"{asset_id} runtime provenance mismatch")
        results.append((asset, result, result_path))
    return assignment, validation, results


def run_from_result(repo: Path, worker: Path, assignment: dict, validation: dict, asset: dict, result: dict, result_path: Path, prior_record: dict) -> dict:
    comparisons = result.get("authoritativeComparisons")
    if not isinstance(comparisons, list):
        raise SystemExit(f"{asset['assetId']} authoritativeComparisons is not a list")
    verified = []
    unresolved = []
    for comparison in comparisons:
        if not isinstance(comparison, dict):
            raise SystemExit(f"{asset['assetId']} contains a malformed authoritative comparison")
        token = comparison.get("canonicalToken")
        decision = comparison.get("matchDecision")
        row = {
            "cardLocation": comparison.get("cardLocation"),
            "referenceLabel": comparison.get("referenceLabel"),
            "matchDecision": decision,
            "canonicalToken": token,
            "closestAlternative": comparison.get("closestAlternative"),
            "visibleDiscriminator": comparison.get("visibleDiscriminator"),
            "evidenceRun": assignment["workerId"],
        }
        if decision == "match" and token:
            verified.append(row)
        else:
            unresolved.append(row)
    printed_data = prior_record.get("printedData")
    printed = printed_data if isinstance(printed_data, dict) else {}
    prior_upper = printed.get("upperRight")
    conflicts = []
    if prior_upper and any(
        isinstance(item.get("cardLocation"), str)
        and item["cardLocation"].lower().startswith("upper-right")
        and item.get("matchDecision") != "match"
        for item in unresolved
    ):
        conflicts.append({
            "field": "printedData.upperRight",
            "priorValue": prior_upper,
            "currentStatus": "unresolved/no-authorized-match",
            "resolution": "preserved prior snapshot; current staged evidence blocks canonical semantic use",
        })
    run_id = assignment["runId"]
    worker_id = assignment["workerId"]
    asset_id = asset["assetId"]
    raw_path = worker / "raw" / f"{asset_id}.json"
    run = {
        "runIdentity": selected_evidence.stable_run_identity(run_id, worker_id, asset_id),
        "runId": run_id,
        "workerId": worker_id,
        "assetId": asset_id,
        "assignmentSha256": validation["assignmentSha256"],
        "orderedTupleDigest": validation["orderedTupleDigest"],
        "runtime": result.get("runtimeProvenance"),
        "artifactPaths": {
            "blindObservationPath": relative_to_repo(raw_path, repo),
            "resultPath": relative_to_repo(result_path, repo),
            "contactSheetPath": result.get("contactSheetPath"),
        },
        "visibleText": result.get("visibleText"),
        "verifiedIconOccurrences": verified,
        "unresolvedIconOccurrences": unresolved,
        "canonicalTokensEmitted": sorted(result.get("canonicalTokensEmitted") or []),
        "allMaterialTextReadable": (result.get("adjudicationModelOutput") or {}).get("allMaterialTextReadable"),
        "allMaterialIconsAuthoritativelyMatched": (result.get("adjudicationModelOutput") or {}).get("allMaterialIconsAuthoritativelyMatched"),
        "promotionDecision": "defer",
        "decisionReasons": result.get("decisionReasons") or [],
        "conflictsWithPriorSnapshot": conflicts,
    }
    try:
        selected_evidence.validate_run(run, f"staged result {asset_id}")
    except selected_evidence.RegistryError as exc:
        raise SystemExit(str(exc)) from exc
    return run


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument("--worker-root", required=True)
    parser.add_argument("--registry", default="assets/tts-mod/extract/selected-card-text-evidence.json")
    parser.add_argument("--corpus", default="assets/tts-mod/extract/card-text-corpus.json")
    parser.add_argument("--output", default=None)
    args = parser.parse_args()
    repo = Path(args.repo).resolve()
    worker = (repo / args.worker_root).resolve()
    registry_path = (repo / args.registry).resolve()
    corpus_path = (repo / args.corpus).resolve()
    output = (repo / args.output).resolve() if args.output else corpus_path

    assignment, validation, results = validated_worker(repo, worker)
    registry = selected_evidence.load_registry(registry_path)
    baseline = corpus_builder.build_payload(registry=registry)
    baseline_by_tuple = {(record["sourcePath"], record["sourceSha256"]): record for record in baseline["records"]}
    updated = copy.deepcopy(registry)
    entries_by_tuple = {(entry["sourcePath"], entry["sourceSha256"]): entry for entry in updated["entries"]}
    changed = []
    for asset, result, result_path in results:
        key = (asset["sourcePath"], asset["sourceSha256"])
        if key not in baseline_by_tuple:
            raise SystemExit(f"corpus missing exact source tuple: {key}")
        run = run_from_result(repo, worker, assignment, validation, asset, result, result_path, baseline_by_tuple[key])
        entry = entries_by_tuple.get(key)
        if entry is None:
            entry = {
                "sourcePath": key[0],
                "sourceSha256": key[1],
                "status": selected_evidence.ENTRY_STATUS,
                "selectedRunIdentity": run["runIdentity"],
                "runs": [],
            }
            updated["entries"].append(entry)
            entries_by_tuple[key] = entry
        existing = next((item for item in entry["runs"] if item["runIdentity"] == run["runIdentity"]), None)
        run_added = existing is None
        if existing is not None and existing != run:
            raise SystemExit(f"stable run identity collision with different content: {run['runIdentity']}")
        if run_added:
            entry["runs"].append(run)
            entry["runs"].sort(key=lambda item: item["runIdentity"])
        selection_changed = entry["selectedRunIdentity"] != run["runIdentity"]
        entry["selectedRunIdentity"] = run["runIdentity"]
        entry["status"] = selected_evidence.ENTRY_STATUS
        changed.append({
            "sourcePath": key[0],
            "runIdentity": run["runIdentity"],
            "runAdded": run_added,
            "selectionChanged": selection_changed,
            "verifiedIconCount": len(run["verifiedIconOccurrences"]),
            "unresolvedIconCount": len(run["unresolvedIconOccurrences"]),
            "conflictCount": len(run["conflictsWithPriorSnapshot"]),
        })
    updated["entries"].sort(key=lambda entry: (entry["sourcePath"], entry["sourceSha256"]))
    try:
        selected_evidence.validate_registry(updated)
        corpus_builder.build_payload(registry=updated)
    except selected_evidence.RegistryError as exc:
        raise SystemExit(str(exc)) from exc
    registry_changed = selected_evidence.canonical_json_bytes(updated) != selected_evidence.canonical_json_bytes(registry)
    selected_evidence.atomic_write_registry(registry_path, updated)
    payload = corpus_builder.write_corpus(output, registry=updated)
    print(json.dumps({
        "registry": str(registry_path),
        "output": str(output),
        "workerId": assignment["workerId"],
        "registryChanged": registry_changed,
        "changed": changed,
        "recordCount": len(payload["records"]),
        "registrySha256": payload["metadata"]["selectedEvidenceRegistrySha256"],
        "corpusSha256": hashlib.sha256(output.read_bytes()).hexdigest(),
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
