#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
STATUS = REPO / "PROJECT_STATUS.md"
AGENTS = REPO / "AGENTS.md"
SUPPLEMENT = REPO / "AGENTS-SUPPLEMENT.md"
README = REPO / "readme.md"
CORPUS = REPO / "assets/tts-mod/extract/card-text-corpus.json"
SOURCE_VALIDATION = REPO / "docs/rules/source-extraction/validation.json"


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def main() -> None:
    failures: list[str] = []
    status = STATUS.read_text(encoding="utf-8")
    agents = AGENTS.read_text(encoding="utf-8")
    supplement = SUPPLEMENT.read_text(encoding="utf-8")
    readme = README.read_text(encoding="utf-8")
    corpus = json.loads(CORPUS.read_text(encoding="utf-8"))
    source_validation = json.loads(SOURCE_VALIDATION.read_text(encoding="utf-8"))

    require("PROJECT_STATUS.md" in agents, "AGENTS.md must point to PROJECT_STATUS.md", failures)
    require("Current implementation work is out of scope" in agents, "AGENTS.md must freeze legacy implementation work", failures)
    require("PROJECT_STATUS.md" in supplement, "AGENTS-SUPPLEMENT.md must name PROJECT_STATUS.md as current status home", failures)
    require("PROJECT_STATUS.md" in readme, "readme.md must link to PROJECT_STATUS.md", failures)
    require("legacy implementation is frozen" in readme.lower(), "readme.md must state the legacy implementation boundary", failures)
    require(source_validation.get("passed") is True and source_validation.get("failureCount") == 0,
            "source-extraction validation must pass", failures)

    counts = corpus["counts"]
    expected_fragments = [
        f"- {counts['records']} card/reference records",
        f"- {counts['rulesTextPresent']} records with rules/effect text",
        f"- {counts['extractionStates']['verified-canonical']} canonical image/sidecar pairs",
        f"- {counts['extractionStates']['draft-full']} full drafts",
        f"- {counts['extractionStates']['draft-partial']} partial record" + ("" if counts['extractionStates']['draft-partial'] == 1 else "s"),
        f"- {counts['extractionStates'].get('no-transcription', 0)} no-transcription record" + ("" if counts['extractionStates'].get('no-transcription', 0) == 1 else "s"),
        f"- {counts['extractionStates']['complete-non-rules-or-reference'] + counts['extractionStates']['non-rules-or-reference']} non-rules/reference records",
        f"- Intruder Help instructions: **{source_validation['checks']['intruderHelpInstructions']}/{source_validation['checks']['intruderHelpInstructions']}**",
        f"- Room Help Sheet: **{source_validation['checks']['roomHelpEffectsExtracted']}/{source_validation['checks']['roomHelpEffectsExtracted']} entries extracted source-bound**",
        f"  - {source_validation['checks']['roomHelpFunctionalIconOccurrences']} literal functional-icon occurrences",
        f"  - {source_validation['checks']['roomHelpEffectAndNoteIconReferences']} effect/note icon references",
        f"  - {source_validation['checks']['roomHelpMaterialUnreadableSpans']} unreadable operative spans",
        f"- Objective Help Sheet: **{source_validation['checks']['objectiveHelpSourceUnits']}/{source_validation['checks']['objectiveHelpSourceUnits']} source units inventoried**",
        f"  - {source_validation['checks']['objectiveHelpFullyVisibleAndExtracted']} fully visible units extracted source-bound",
        f"  - {source_validation['checks']['objectiveHelpPartiallyOccluded']} physically occluded units retained with explicit visibility boundaries",
        f"  - {source_validation['checks']['objectiveHelpFunctionalIconOccurrences']} full and {source_validation['checks']['objectiveHelpPartiallyVisibleIconOccurrences']} partially visible icon occurrences",
        f"  - {source_validation['checks']['objectiveHelpMaterialUnreadableSpans']} unreadable visible spans",
        f"- Card-gap review: **{source_validation['checks']['cardGapRecords']}/{source_validation['checks']['cardGapRecords']} source tuples adjudicated**",
        f"  - {source_validation['checks']['cardGapCounts']['rulesTextComplete']} rules-text-complete records",
        f"  - {source_validation['checks']['cardGapCounts']['explicitOperativeSourceBlockers']} explicit exact-source operative blocker",
        f"  - {source_validation['checks']['cardGapCounts']['classifiedNonRules']} classified non-rules components/placeholders",
        f"  - {source_validation['checks']['cardGapCounts']['recoveredOperativeCorrections']} operative correction recovered (`SUBMACHINE GUN`: colon)",
        f"  - {source_validation['checks']['cardGapCounts']['remainingNoTranscription']} remaining no-transcription records",
        f"- Rulebook visual census: **{source_validation['checks']['rulebookVisualPages']}/{source_validation['checks']['rulebookVisualPages']} rendered pages classified**",
        f"  - {source_validation['checks']['rulebookVisualUnits']} non-decorative visual units",
        f"  - {source_validation['checks']['rulebookNormativeVisualObligations']} normative visual obligations",
        f"  - {source_validation['checks']['rulebookWorkedExampleVisuals']} worked-example visuals",
        f"  - {source_validation['checks']['rulebookReferenceVisualUnits']} reference/navigation units",
        f"  - {source_validation['checks']['rulebookMaterialUnreadableSpans']} unreadable visual spans",
        f"  - all {source_validation['checks']['rulebookVisualUnits']} only partially represented by text extraction because graphical structure is lost",
        f"- FAQ/errata v1.2: **{source_validation['checks']['faqPages']}/{source_validation['checks']['faqPages']} rendered pages extracted**",
        f"  - {source_validation['checks']['faqRulingAndErrataUnits']} ruling/errata units",
        f"  - {source_validation['checks']['faqBaseGameApplicableUnits']} base-game-applicable units",
        f"  - {source_validation['checks']['faqExpansionSpecificUnits']} expansion-specific units retained out of base conclusions",
        f"  - {source_validation['checks']['faqErrataUnits']} errata units and {source_validation['checks']['faqRulingUnits']} FAQ rulings",
        f"  - {source_validation['checks']['faqVisualOccurrences']} inline visual occurrences",
        f"  - {source_validation['checks']['faqMaterialUnreadableSpans']} unreadable spans",
        f"- Player Help source: **{source_validation['checks']['playerHelpFrontOccurrences']}/{source_validation['checks']['playerHelpFrontOccurrences']} numbered fronts extracted**",
        f"  - {source_validation['checks']['playerHelpSharedBackOccurrences']} shared functional `PASS` side",
        f"  - {source_validation['checks']['playerHelpInstructionTextVariants']} identical instruction-text variant",
        f"  - {source_validation['checks']['playerHelpRasterTemplateGroups']} measured raster-template groups",
        f"  - {source_validation['checks']['playerHelpFunctionalIconOccurrences']} functional icons and {source_validation['checks']['playerHelpMaterialUnreadableSpans']} unreadable spans",
        "  - explicit conflicts: TTS 10 fronts vs official 5-card inventory; obsolete phase sequence vs current rulebook",
    ]
    for fragment in expected_fragments:
        require(fragment in status, f"PROJECT_STATUS.md count drift: expected {fragment!r}", failures)

    linked_paths = sorted(set(re.findall(r"`([^`]+(?:\.md|\.json|\.py))`", status + "\n" + agents + "\n" + readme)))
    for path in linked_paths:
        if path.startswith("/") or " " in path or "*" in path or path.startswith("work/"):
            continue
        require((REPO / path).exists(), f"referenced path does not exist: {path}", failures)

    report = {
        "schemaVersion": 1,
        "passed": not failures,
        "checks": {
            "statusFile": str(STATUS.relative_to(REPO)),
            "corpusRecords": counts["records"],
            "sourceExtractionPassed": source_validation["passed"],
            "linkedPathsChecked": len(linked_paths),
        },
        "failureCount": len(failures),
        "failures": failures,
    }
    print(json.dumps(report, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
