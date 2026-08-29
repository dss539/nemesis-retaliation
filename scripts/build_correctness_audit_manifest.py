#!/usr/bin/env python3
"""Build the locked Stage 1 rules-correctness audit manifest.

This builder deliberately reads source/extraction indexes and concise-record headings,
but never reads the frozen semantic records in semantics/pilots.json. Component
selection is deterministic by SHA-256 rank and is fixed before blind derivation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any, Callable, Iterable

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs/qa/implementation-readiness/correctness-audit/manifest.json"
PROGRESS = ROOT / "docs/qa/implementation-readiness/correctness-audit/progress.json"
LOCKED_STARTING_HEAD = "8d95b94f3e5c8d5ffb3a1c9835dd2512be88bc93"
SEED_MATERIAL = (
    "nemesis-retaliation-stage1-correctness-audit-v1|"
    + LOCKED_STARTING_HEAD
)
RULE_FILES = [
    "docs/rules/00-foundations.md",
    "docs/rules/01-round-and-turns.md",
    "docs/rules/02-character-actions.md",
    "docs/rules/03-intruders-and-survival.md",
    "docs/rules/04-items-and-equipment.md",
]
FROZEN_SEMANTIC_PATHS = [
    "docs/rules/semantics/pilots.json",
    "docs/rules/semantics/review-gates.json",
    "docs/rules/semantics/validation.json",
    "scripts/build_semantic_pilots.py",
    "scripts/validate_semantic_pilots.py",
]
SELECTION_INPUT_PATHS = RULE_FILES + [
    "docs/qa/implementation-readiness/correctness-audit/methodology.md",
    "docs/rules/implementation-readiness.md",
    "scripts/build_correctness_audit_manifest.py",
    "docs/rulebooks/Nemesis_RT_FAQ_v1.2.pdf",
    "docs/rules/source-extraction/faq-v1.2-source-extraction.json",
    "docs/rules/source-extraction/room-help-sheet.json",
    "docs/rules/source-extraction/intruder-help-sheet.json",
    "docs/rules/semantics/event-source-index.json",
    "docs/rules/semantics/exploration-source-index.json",
    "docs/rules/semantics/robot-source-index.json",
    "docs/rules/semantics/attack-source-index.json",
    "docs/rules/semantics/queen-health-source-index.json",
    "docs/rules/semantics/serious-wound-source-index.json",
    "docs/rules/semantics/green-item-source-index.json",
    "docs/rules/semantics/red-item-source-index.json",
    "docs/rules/semantics/yellow-item-source-index.json",
    "docs/rules/semantics/action-source-index.json",
    "docs/rules/semantics/objective-mission-source-index.json",
    "docs/rules/semantics/equipment-source-index.json",
]
RULE_HEADING = re.compile(
    r"^##\s+((?:FND|RT|ACT|INT|ITM)-[A-Za-z0-9-]+)\s+—\s+(.+)$"
)


def load_json(path: str) -> dict[str, Any]:
    with (ROOT / path).open(encoding="utf-8") as handle:
        return json.load(handle)


def file_sha256(path: str) -> str:
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def rank(stratum: str, candidate_id: str) -> str:
    material = f"{SEED_MATERIAL}|{stratum}|{candidate_id}".encode()
    return hashlib.sha256(material).hexdigest()


def select(
    candidates: Iterable[dict[str, Any]],
    count: int,
    stratum: str,
) -> list[dict[str, Any]]:
    rows = list(candidates)
    ids = [row["sourceIdentity"] for row in rows]
    assert len(ids) == len(set(ids)), f"duplicate candidates in {stratum}"
    assert len(rows) >= count, f"too few candidates in {stratum}"
    ordered = sorted(rows, key=lambda row: (rank(stratum, row["sourceIdentity"]), row["sourceIdentity"]))
    selected = ordered[:count]
    for row in selected:
        row["selection"] = {
            "method": "lowest SHA-256 rank",
            "stratum": stratum,
            "candidateCount": len(rows),
            "score": rank(stratum, row["sourceIdentity"]),
        }
    return selected


def clean_label(value: Any) -> str:
    return " ".join(str(value or "").split())


def source_candidate(
    family: str,
    source_identity: str,
    label: str,
    source_path: str,
    source_sha256: str,
    **extra: Any,
) -> dict[str, Any]:
    assert source_identity and source_path and source_sha256
    row: dict[str, Any] = {
        "auditUnitId": f"COMPONENT:{family}:{source_identity}",
        "unitClass": "sampled-component-effect",
        "family": family,
        "sourceIdentity": source_identity,
        "label": clean_label(label),
        "sourcePath": source_path,
        "sourceSha256": source_sha256,
        "status": "pending-blind-derivation",
    }
    row.update(extra)
    return row


def unique_source_effects(
    rows: Iterable[dict[str, Any]],
    family: str,
    id_field: str,
    label: Callable[[dict[str, Any]], str],
) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[(row["sourcePath"], row["sourceSha256"])].append(row)
    result = []
    for (source_path, source_sha256), copies in grouped.items():
        representative = min(copies, key=lambda row: row[id_field])
        result.append(
            source_candidate(
                family,
                representative[id_field],
                label(representative),
                source_path,
                source_sha256,
                identicalPhysicalCopies=len(copies),
            )
        )
    return result


def concise_rule_units() -> list[dict[str, Any]]:
    units: list[dict[str, Any]] = []
    for path in RULE_FILES:
        for line in (ROOT / path).read_text(encoding="utf-8").splitlines():
            match = RULE_HEADING.match(line)
            if not match:
                continue
            rule_id, label = match.groups()
            units.append(
                {
                    "auditUnitId": f"RULE:{rule_id}",
                    "unitClass": "concise-rule-record",
                    "sourceIdentity": rule_id,
                    "label": f"Concise rule unit {rule_id}",
                    "downstreamLabelWithheld": True,
                    "downstreamPath": path,
                    "status": "pending-blind-derivation",
                }
            )
    assert len(units) == 56, len(units)
    assert len({row["auditUnitId"] for row in units}) == 56
    return units


def faq_units() -> list[dict[str, Any]]:
    path = "docs/rules/source-extraction/faq-v1.2-source-extraction.json"
    data = load_json(path)
    rows = [
        (page["pdfPageIndex"], unit)
        for page in data["pages"]
        for unit in page.get("units", [])
        if unit.get("applicability", "").startswith("base-game")
    ]
    assert len(rows) == 28
    return [
        {
            "auditUnitId": f"FAQ:{row['sourceUnitId']}",
            "unitClass": "base-applicable-faq-unit",
            "sourceIdentity": row["sourceUnitId"],
            "label": clean_label(row.get("questionText") or row["printedText"].splitlines()[0]),
            "applicability": row["applicability"],
            "section": row["section"],
            "sourcePath": data["source"]["path"],
            "sourceSha256": data["source"]["sha256"],
            "extractionPath": path,
            "pdfPageIndex": page_index,
            "bbox": row["bbox"],
            "status": "pending-blind-derivation",
        }
        for page_index, row in rows
    ]


def room_sample() -> list[dict[str, Any]]:
    path = "docs/rules/source-extraction/room-help-sheet.json"
    data = load_json(path)
    candidates = [
        source_candidate(
            "room",
            f"ROOM-HELP-{int(row['printedNumber']):02d}",
            row["printedTitle"],
            data["source"]["path"],
            data["source"]["sha256"],
            printedNumber=int(row["printedNumber"]),
            printedSectionMarker=row["printedSectionMarker"],
            extractionPath=path,
        )
        for row in data["entries"]
    ]
    result = []
    result += select((row for row in candidates if row["printedSectionMarker"] == "?"), 2, "room:general")
    for marker in ("A", "B", "C"):
        result += select(
            (row for row in candidates if row["printedSectionMarker"] == marker),
            1,
            f"room:section-{marker}",
        )
    return result


def intruder_help_candidates() -> list[dict[str, Any]]:
    path = "docs/rules/source-extraction/intruder-help-sheet.json"
    data = load_json(path)
    candidates = []
    for side in data["sides"]:
        for column in side["columns"]:
            for row in column["rows"]:
                candidates.append(
                    source_candidate(
                        "intruder-help",
                        row["occurrenceId"],
                        row["printedInstruction"],
                        side["sourcePath"],
                        side["sourceSha256"],
                        sideId=side["sideId"],
                        context=column["columnId"],
                        extractionPath=path,
                    )
                )
        row = side["bottomRow"]
        candidates.append(
            source_candidate(
                "intruder-help",
                row["occurrenceId"],
                row["printedInstruction"],
                side["sourcePath"],
                side["sourceSha256"],
                sideId=side["sideId"],
                context="bottom-row",
                extractionPath=path,
            )
        )
    assert len(candidates) == 18
    return candidates


def intruder_help_sample() -> list[dict[str, Any]]:
    candidates = intruder_help_candidates()
    strata = [
        "corridor",
        "room",
        "bag-development",
        "bottom-row",
    ]
    result = []
    for context in strata:
        result += select(
            (row for row in candidates if row["context"] == context),
            1,
            f"intruder-help:context:{context}",
        )
    return result


def generic_family_sample(
    index_path: str,
    rows_key: str,
    family: str,
    id_field: str,
    label: Callable[[dict[str, Any]], str],
    count: int,
) -> list[dict[str, Any]]:
    data = load_json(index_path)
    candidates = unique_source_effects(data[rows_key], family, id_field, label)
    return select(candidates, count, f"{family}:unique-source-effect")


def attack_sample() -> list[dict[str, Any]]:
    path = "docs/rules/semantics/attack-source-index.json"
    rows = load_json(path)["faces"]
    occurrence_candidates = [
        source_candidate(
            "intruder-attack",
            row["attackOccurrenceId"],
            row["printedTitle"],
            row["sourcePath"],
            row["sourceSha256"],
            extractionPath=path,
        )
        for row in rows
    ]
    return select(occurrence_candidates, 2, "intruder-attack:source-occurrence")


def item_sample() -> list[dict[str, Any]]:
    specs = [
        ("green-item", "docs/rules/semantics/green-item-source-index.json", "greenItemOccurrenceId"),
        ("red-item", "docs/rules/semantics/red-item-source-index.json", "redItemOccurrenceId"),
        ("yellow-item", "docs/rules/semantics/yellow-item-source-index.json", "yellowItemOccurrenceId"),
    ]
    result = []
    for family, path, id_field in specs:
        data = load_json(path)
        candidates = unique_source_effects(
            data["faces"], family, id_field, lambda row: row["printedTitle"]
        )
        result += select(candidates, 2, f"item:{family}:unique-source-effect")
    return result


def action_sample() -> list[dict[str, Any]]:
    path = "docs/rules/semantics/action-source-index.json"
    data = load_json(path)
    by_character: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in data["faces"]:
        by_character[row["character"]].append(
            source_candidate(
                "action-card",
                row["occurrenceId"],
                row["printedTitle"],
                row["sourcePath"],
                row["sourceSha256"],
                character=row["character"],
                extractionPath=path,
            )
        )
    assert set(by_character) == {
        "Combat Engineer",
        "Contractor",
        "Heavy Gun Operator",
        "Medical Support",
        "Officer",
        "Recon",
    }
    result = []
    for character in sorted(by_character):
        result += select(by_character[character], 2, f"action-card:character:{character}")
    return result


def objective_sample() -> list[dict[str, Any]]:
    path = "docs/rules/semantics/objective-mission-source-index.json"
    data = load_json(path)
    by_category: dict[str, list[dict[str, Any]]] = defaultdict(list)
    grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in data["physicalFaces"]:
        grouped[(row["category"], row["sourcePath"], row["sourceSha256"])].append(row)
    for (category, source_path, source_sha256), copies in grouped.items():
        representative = min(copies, key=lambda row: row["occurrenceId"])
        by_category[category].append(
            source_candidate(
                "objective-mission",
                representative["occurrenceId"],
                representative["printedTitle"],
                source_path,
                source_sha256,
                category=category,
                disposition=representative["disposition"],
                identicalPhysicalCopies=len(copies),
                extractionPath=path,
            )
        )
    assert set(by_category) == {"mission-objective", "private-objective", "mission-task"}
    result = []
    for category in sorted(by_category):
        result += select(by_category[category], 2, f"objective-mission:category:{category}")
    return result


def equipment_sample() -> list[dict[str, Any]]:
    path = "docs/rules/semantics/equipment-source-index.json"
    data = load_json(path)

    def support(row: dict[str, Any]) -> dict[str, Any]:
        return source_candidate(
            "equipment-starting",
            row["supportEquipmentOccurrenceId"],
            row["printedTitle"],
            row["sourcePath"],
            row["sourceSha256"],
            equipmentStratum=f"support-{row['physicalClass']}",
            physicalClass=row["physicalClass"],
            extractionPath=path,
        )

    supports = [support(row) for row in data["supportEquipmentFaces"]]
    result = []
    result += select((row for row in supports if row["physicalClass"] == "ranged-weapon"), 1, "equipment:support-ranged")
    result += select((row for row in supports if row["physicalClass"] == "melee-weapon"), 1, "equipment:support-melee")
    result += select((row for row in supports if row["physicalClass"] == "heavy-item"), 1, "equipment:support-heavy-nonweapon")
    result += select((row for row in supports if row["physicalClass"] == "armor-item"), 1, "equipment:support-armor")

    starting = [
        source_candidate(
            "equipment-starting",
            row["characterItemOccurrenceId"],
            row["printedTitle"],
            row["sourcePath"],
            row["sourceSha256"],
            equipmentStratum="character-starting-source-clear",
            physicalClass=row["physicalClass"],
            disposition=row["batchDisposition"],
            extractionPath=path,
        )
        for row in data["characterItemTtsFaces"]
        if row["batchDisposition"] == "source-clear-tts-character-kit-variant"
    ]
    result += select(starting, 1, "equipment:character-starting-source-clear")

    # Red and Green records use different occurrence-ID keys. Group uniformly.
    grouped_heavy: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in data["colorRootHeavyFaces"]:
        grouped_heavy[(row["sourcePath"], row["sourceSha256"])].append(row)
    color_heavy = []
    for (source_path, source_sha256), copies in grouped_heavy.items():
        representative = min(
            copies,
            key=lambda row: clean_label(row.get("greenItemOccurrenceId") or row.get("redItemOccurrenceId") or row["sourceSelector"]),
        )
        identity = representative.get("greenItemOccurrenceId") or representative.get("redItemOccurrenceId") or f"COLOR-HEAVY:{source_sha256[:12]}"
        color_heavy.append(
            source_candidate(
                "equipment-starting",
                identity,
                representative["printedTitle"],
                source_path,
                source_sha256,
                equipmentStratum="color-root-heavy",
                physicalClass=representative["physicalClass"],
                identicalPhysicalCopies=len(copies),
                extractionPath=path,
            )
        )
    result += select(color_heavy, 1, "equipment:color-root-heavy")

    conflicts = [
        source_candidate(
            "equipment-starting",
            row["characterItemOccurrenceId"],
            row["printedTitle"],
            row["sourcePath"],
            row["sourceSha256"],
            equipmentStratum="source-variant-boundary",
            physicalClass=row["physicalClass"],
            disposition=row["batchDisposition"],
            extractionPath=path,
        )
        for row in data["characterItemTtsFaces"]
        if row["batchDisposition"] != "source-clear-tts-character-kit-variant"
    ]
    grouped_conflicts: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in data["physicalClassConflictExclusions"]:
        grouped_conflicts[(row["sourcePath"], row["sourceSha256"])].append(row)
    for (source_path, source_sha256), copies in grouped_conflicts.items():
        representative = min(
            copies,
            key=lambda row: json.dumps(row["sourceSelector"], sort_keys=True),
        )
        conflicts.append(
            source_candidate(
                "equipment-starting",
                f"CLASS-CONFLICT:{source_sha256[:16]}",
                representative["printedTitle"],
                source_path,
                source_sha256,
                equipmentStratum="source-variant-boundary",
                physicalClass=representative["physicalClass"],
                disposition=representative["batchDisposition"],
                identicalPhysicalCopies=len(copies),
                extractionPath=path,
            )
        )
    # Reserve two of eight equipment slots for the known-hard source/physical-
    # class boundary instead of diluting every conflict into one candidate.
    result += select(conflicts, 2, "equipment:source-variant-boundary")
    assert len(result) == 8
    return result


def component_units() -> list[dict[str, Any]]:
    units: list[dict[str, Any]] = []
    units += room_sample()
    units += intruder_help_sample()
    units += generic_family_sample(
        "docs/rules/semantics/event-source-index.json",
        "events",
        "event",
        "eventOccurrenceId",
        lambda row: row["visibleTitle"],
        4,
    )
    units += generic_family_sample(
        "docs/rules/semantics/exploration-source-index.json",
        "faces",
        "exploration",
        "explorationOccurrenceId",
        lambda row: row["identityLabel"],
        3,
    )
    units += generic_family_sample(
        "docs/rules/semantics/robot-source-index.json",
        "faces",
        "robot",
        "robotOccurrenceId",
        lambda row: row["printedTitle"],
        2,
    )
    units += attack_sample()
    units += generic_family_sample(
        "docs/rules/semantics/queen-health-source-index.json",
        "faces",
        "queen-health",
        "queenHealthOccurrenceId",
        lambda row: f"Discard {row['printedDiscardCount']}",
        2,
    )
    units += generic_family_sample(
        "docs/rules/semantics/serious-wound-source-index.json",
        "faces",
        "serious-wound",
        "seriousWoundOccurrenceId",
        lambda row: row["printedTitle"],
        2,
    )
    units += item_sample()
    units += action_sample()
    units += objective_sample()
    units += equipment_sample()
    assert len(units) == 56, len(units)
    assert len({row["auditUnitId"] for row in units}) == 56
    return units


def build() -> dict[str, Any]:
    concise = concise_rule_units()
    faq = faq_units()
    components = component_units()
    units = concise + faq + components
    assert len(units) == 140
    assert len({row["auditUnitId"] for row in units}) == 140
    by_family: dict[str, int] = defaultdict(int)
    for row in components:
        by_family[row["family"]] += 1
    expected_families = {
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
    assert dict(sorted(by_family.items())) == dict(sorted(expected_families.items()))
    selection_coverage: dict[str, dict[str, int]] = {}
    for row in components:
        stratum = row["selection"]["stratum"]
        candidate_count = row["selection"]["candidateCount"]
        existing = selection_coverage.setdefault(
            stratum,
            {"eligibleCandidates": candidate_count, "selectedUnits": 0},
        )
        assert existing["eligibleCandidates"] == candidate_count
        existing["selectedUnits"] += 1
    component_candidate_universes = {
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
    return {
        "schemaVersion": 1,
        "auditVersion": "stage1-v1",
        "recordType": "stage-1-blind-correctness-audit-manifest",
        "scope": "Base competitive game rewrite-readiness decision audit; Solo/Coop and expansions excluded except one FAQ applicability-boundary unit retained by the pre-existing 28-unit base-applicable count.",
        "lockedStartingHead": LOCKED_STARTING_HEAD,
        "seedMaterial": SEED_MATERIAL,
        "selectionMethod": "Candidates are sorted by SHA-256(seedMaterial|stratum|sourceIdentity); the lowest required ranks are selected. Byte-identical physical copies are one effect candidate, while source-different same-title occurrences remain separate.",
        "selectionScopeCaveat": "The fixed 56-effect sample supports findings only about audited units. It is not a probability sample and cannot establish an error-rate bound for unaudited effects. The attack quota samples source occurrences but is not guaranteed to include two variants of one title.",
        "blindnessBoundary": {
            "allowedBeforeDerivation": [
                "raw official rulebook/FAQ and rendered pages",
                "source-bound component faces/help sheets",
                "source extraction/provenance indexes",
                "audit IDs and source-local labels",
            ],
            "withheldUntilDerivationSealed": [
                "concise rule-record body under audit",
                "docs/rules/semantics/pilots.json records",
                "semantic review-gate conclusions",
                "semantic contradiction outcomes",
                "legacy implementation behavior",
            ],
        },
        "frozenSemanticHashes": {
            path: file_sha256(path) for path in FROZEN_SEMANTIC_PATHS
        },
        "frozenConciseRuleHashes": {
            path: file_sha256(path) for path in RULE_FILES
        },
        "selectionInputHashes": {
            path: file_sha256(path) for path in SELECTION_INPUT_PATHS
        },
        "counts": {
            "totalAuditUnits": len(units),
            "conciseRuleRecords": len(concise),
            "baseApplicableFaqUnits": len(faq),
            "sampledComponentEffects": len(components),
            "componentFamilies": dict(sorted(by_family.items())),
            "componentCandidateUniverses": component_candidate_universes,
        },
        "selectionCoverage": dict(sorted(selection_coverage.items())),
        "passThreshold": {
            "criticalErrors": 0,
            "inventedAuthorityOverrides": 0,
            "hiddenDefaults": 0,
            "recurringDefectPatterns": 0,
            "maximumIsolatedMaterialErrorsInComponentSample": 2,
            "sourceBlockedUnitsMustBeEnumerated": True,
            "readinessClaimMustEnumerateUnauditedComponentEffects": True,
        },
        "statusValues": [
            "pending-blind-derivation",
            "blind-derived",
            "compared",
            "accepted",
            "material-error",
            "critical-error",
            "source-blocked",
        ],
        "units": units,
    }


def serialized() -> bytes:
    return (json.dumps(build(), indent=2, ensure_ascii=False) + "\n").encode()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--init-progress", action="store_true")
    args = parser.parse_args()
    expected = serialized()
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_bytes() != expected:
            raise SystemExit("correctness-audit manifest is stale")
        print("correctness-audit manifest is current: 140 units")
        return 0
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_bytes(expected)
    print(f"wrote {OUTPUT.relative_to(ROOT)}: 140 units")
    if args.init_progress:
        if PROGRESS.exists():
            raise SystemExit("refusing to overwrite existing correctness-audit progress")
        manifest = json.loads(expected)
        progress = {
            "schemaVersion": 1,
            "recordType": "stage-1-correctness-audit-progress",
            "manifestPath": str(OUTPUT.relative_to(ROOT)),
            "manifestSha256": hashlib.sha256(expected).hexdigest(),
            "counts": {
                "total": len(manifest["units"]),
                "pendingBlindDerivation": len(manifest["units"]),
                "blindDerived": 0,
                "compared": 0,
                "accepted": 0,
                "materialErrors": 0,
                "criticalErrors": 0,
                "sourceBlocked": 0,
            },
            "units": [
                {
                    "auditUnitId": row["auditUnitId"],
                    "status": "pending-blind-derivation",
                    "blindPath": None,
                    "blindSha256": None,
                    "blindUnitResultId": None,
                    "resultPath": None,
                    "resultSha256": None,
                    "lastUpdatedUtc": None,
                }
                for row in manifest["units"]
            ],
        }
        PROGRESS.write_text(
            json.dumps(progress, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(f"initialized {PROGRESS.relative_to(ROOT)}: 140 pending units")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
