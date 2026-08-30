#!/usr/bin/env python3
"""Advance one audit unit through the mechanically enforced lane order."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import validate_correctness_audit as validation

ROOT = validation.ROOT
PROGRESS = validation.PROGRESS_PATH
AUDIT_DIR = validation.AUDIT_DIR
TRANSITIONS = {
    "pending-blind-derivation": {"blind-derived"},
    "blind-derived": {"compared"},
    "compared": {"accepted", "material-error", "critical-error", "source-blocked"},
    "accepted": set(),
    "material-error": set(),
    "critical-error": set(),
    "source-blocked": set(),
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative_artifact(value: str, parent: Path) -> tuple[str, str]:
    path = Path(value)
    if not path.is_absolute():
        path = ROOT / path
    resolved = path.resolve()
    resolved.relative_to(parent.resolve())
    if not resolved.is_file():
        raise SystemExit(f"artifact does not exist: {resolved}")
    return str(resolved.relative_to(ROOT)), sha(resolved)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--unit", required=True)
    parser.add_argument("--to", required=True, choices=sorted(TRANSITIONS))
    parser.add_argument("--blind")
    parser.add_argument("--comparison")
    parser.add_argument("--result")
    args = parser.parse_args()

    original = PROGRESS.read_bytes()
    progress = validation.strict_load(PROGRESS)
    rows = {row["auditUnitId"]: row for row in progress["units"]}
    if args.unit not in rows:
        raise SystemExit(f"unknown audit unit: {args.unit}")
    row = rows[args.unit]
    current = row["status"]
    if args.to not in TRANSITIONS[current]:
        raise SystemExit(f"invalid transition: {current} -> {args.to}")

    if args.to == "blind-derived":
        if not args.blind or args.comparison or args.result:
            raise SystemExit("--blind is required")
        blind_path, blind_hash = relative_artifact(args.blind, AUDIT_DIR / "blind")
        blind = validation.strict_load(ROOT / blind_path)
        ids = [item.get("auditUnitId") for item in blind.get("unitResults", [])]
        if args.unit not in ids:
            raise SystemExit("blind artifact does not contain the unit")
        row.update(
            {
                "blindPath": blind_path,
                "blindSha256": blind_hash,
                "blindUnitResultId": args.unit,
            }
        )
    elif args.to == "compared":
        if args.blind or not args.comparison or args.result:
            raise SystemExit("--comparison alone is required for the compared transition")
        comparison_path, comparison_hash = relative_artifact(
            args.comparison,
            AUDIT_DIR / "comparisons",
        )
        comparison = validation.strict_load(ROOT / comparison_path)
        if comparison.get("auditUnitId") != args.unit or comparison.get("status") != "compared":
            raise SystemExit("comparison unit/status does not match requested transition")
        row.update(
            {
                "comparisonPath": comparison_path,
                "comparisonSha256": comparison_hash,
            }
        )
    else:
        if args.blind or args.comparison or not args.result:
            raise SystemExit("--result alone is required for a final transition")
        if any(
            isinstance(candidate, dict)
            and candidate.get("status") in {"pending-blind-derivation", "blind-derived"}
            for candidate in progress.get("units", [])
        ):
            raise SystemExit("final adjudication is blocked until every Stage 1 unit is compared")
        result_path, result_hash = relative_artifact(args.result, AUDIT_DIR / "adjudications")
        result = validation.strict_load(ROOT / result_path)
        if result.get("auditUnitId") != args.unit or result.get("status") != args.to:
            raise SystemExit("result unit/status does not match requested transition")
        row.update({"resultPath": result_path, "resultSha256": result_hash})

    row["status"] = args.to
    row["lastUpdatedUtc"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    counts = {key: 0 for key in validation.STATUS_COUNT_KEYS.values()}
    for item in progress["units"]:
        counts[validation.STATUS_COUNT_KEYS[item["status"]]] += 1
    progress["counts"] = {"total": len(progress["units"]), **counts}

    PROGRESS.write_bytes(validation.canonical_progress_bytes(progress))
    try:
        report = validation.validate(
            require_lock=validation.LOCK_PATH.is_file(),
            allow_uncommitted_progress=True,
        )
        if not report["passed"]:
            raise RuntimeError("; ".join(report["failures"][:10]))
    except Exception as exc:
        PROGRESS.write_bytes(original)
        raise SystemExit(f"transition rolled back: {exc}") from exc
    print(f"advanced {args.unit}: {current} -> {args.to}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
