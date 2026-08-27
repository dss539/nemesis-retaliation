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
VOCAB_VALIDATION = REPO / "docs/rules/vocabulary/validation.json"
ONTOLOGY_VALIDATION = REPO / "docs/rules/ontology/validation.json"
SEMANTIC_VALIDATION = REPO / "docs/rules/semantics/validation.json"
SEMANTIC_CONTRADICTIONS = REPO / "docs/rules/semantics/contradictions.json"


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
    vocab_validation = json.loads(VOCAB_VALIDATION.read_text(encoding="utf-8"))
    ontology_validation = json.loads(ONTOLOGY_VALIDATION.read_text(encoding="utf-8"))
    semantic_validation = json.loads(SEMANTIC_VALIDATION.read_text(encoding="utf-8"))
    semantic_contradictions = json.loads(SEMANTIC_CONTRADICTIONS.read_text(encoding="utf-8"))

    require("PROJECT_STATUS.md" in agents, "AGENTS.md must point to PROJECT_STATUS.md", failures)
    require("Current implementation work is out of scope" in agents, "AGENTS.md must freeze legacy implementation work", failures)
    require("PROJECT_STATUS.md" in supplement, "AGENTS-SUPPLEMENT.md must name PROJECT_STATUS.md as current status home", failures)
    require("PROJECT_STATUS.md" in readme, "readme.md must link to PROJECT_STATUS.md", failures)
    require("legacy implementation is frozen" in readme.lower(), "readme.md must state the legacy implementation boundary", failures)
    require(source_validation.get("passed") is True and source_validation.get("failureCount") == 0,
            "source-extraction validation must pass", failures)
    if vocab_validation["checks"]["openReviewGates"] == 0:
        require("Semantic coverage expansion (pilot gate passed)" in status,
                "PROJECT_STATUS.md must advance to semantic coverage after pilot approval", failures)
    else:
        require("Canonical vocabulary and source-scoped aliases (extraction gate passed)" in status,
                "PROJECT_STATUS.md must remain in vocabulary phase while review gates are open", failures)
    require(vocab_validation.get("passed") is True and vocab_validation.get("failureCount") == 0,
            "vocabulary proposal validation must pass", failures)
    require(ontology_validation.get("passed") is True and ontology_validation.get("failureCount") == 0,
            "taxonomy/ontology validation must pass", failures)
    require(semantic_validation.get("passed") is True and semantic_validation.get("failureCount") == 0,
            "semantic pilot validation must pass", failures)

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
        f"- Room Help Sheet: **{source_validation['checks']['roomHelpEffectsExtracted']}/{source_validation['checks']['roomHelpEffectsExtracted']} entries extracted source-bound and independently locked**",
        f"  - {source_validation['checks']['roomHelpExactSourceProjectionsVerified']} exact source projections verified",
        f"  - {source_validation['checks']['roomHelpAuditedCropCoverageBoxesVerified']} complete audited evidence crops verified",
        f"  - {source_validation['checks']['roomHelpFunctionalIconOccurrences']} literal functional-icon occurrences",
        f"  - {source_validation['checks']['roomHelpEffectAndNoteIconReferences']} effect/note icon references",
        f"  - {source_validation['checks']['roomHelpMaterialUnreadableSpans']} unreadable operative spans",
        "  - corruption negative controls reject verbatim, icon, crop, provenance, unreadability, and coordinated-layout drift",
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
        "- Secondary evidence closure:",
        f"  - {source_validation['checks']['bgaCopies']} BGA copies verified byte-identical; 1 immutable build `260622-1220` snapshot retained",
        f"  - {source_validation['checks']['bgaTopLevelTables']} BGA tables and {source_validation['checks']['bgaStructuredRecords']} scoped structured records indexed",
        f"  - {source_validation['checks']['ttsStructuredFiles']} TTS structured files indexed",
        f"  - {source_validation['checks']['ttsLuaRoleRecords']} Lua role records",
        f"  - {source_validation['checks']['ttsGmnotesTagRows']} GMNotes tag rows / {source_validation['checks']['ttsGmnotesTaggedOccurrences']:,} tagged occurrences",
        f"  - {source_validation['checks']['secondarySelectedEvidenceEntries']} selected-evidence entries/runs",
        f"  - {source_validation['checks']['corpusRecordsWithBgaConflictBoundary']} corpus records explicitly preserve a BGA conflict/secondary boundary",
        "- Extraction closure gate: **PASS**",
        f"  - {source_validation['checks']['closureExtractedOrIndexedChannels']}/{source_validation['checks']['closureChannels']} source channels extracted or indexed",
        f"  - {source_validation['checks']['closurePassedGateCriteria']}/{source_validation['checks']['closureGateCriteria']} gate criteria passed",
        f"  - {source_validation['checks']['closureRemainingGraphicalSourceUnits']} remaining graphical source units",
        f"  - {source_validation['checks']['closureExplicitBlockers']} explicit exact-source operative blocker retained",
        "  - next phase authorized: canonical vocabulary and source-scoped aliases",
        f"- {vocab_validation['checks']['sourceTermOccurrences']:,} observed source-term occurrences / {vocab_validation['checks']['uniqueNormalizedSourceKeys']:,} normalized exact-string keys",
        f"- {vocab_validation['checks']['namedIdentityOccurrences']} named-identity source occurrences / {vocab_validation['checks']['namedIdentityExactStringGroups']} exact-string groups",
        f"- {vocab_validation['checks']['canonicalVocabularyEntries']} controlled vocabulary entries",
        f"  - {vocab_validation['checks']['acceptedExistingIconTerms']} accepted existing icon-glossary terms",
        f"  - {vocab_validation['checks']['proposedAuthorityDerivedTerms']} authority-derived canonical-label proposals",
        f"- {vocab_validation['checks']['aliasEntries']} alias entries",
        f"  - {vocab_validation['checks']['acceptedAliases']} accepted explicit/source-scoped aliases",
        f"  - {vocab_validation['checks']['proposedReviewAliases']} proposed alias" + ("" if vocab_validation['checks']['proposedReviewAliases'] == 1 else "es") + " awaiting owner review",
        f"- {vocab_validation['checks']['openReviewGates']} open review gate" + ("" if vocab_validation['checks']['openReviewGates'] == 1 else "s") + ("; taxonomy/ontology is authorized" if vocab_validation['checks']['openReviewGates'] == 0 else "; taxonomy/ontology has not started"),
        f"- {ontology_validation['checks']['taxa']} source-traceable taxa / {ontology_validation['checks']['rootTaxa']} roots",
        f"- all {ontology_validation['checks']['controlledTerms']} controlled terms mapped exactly once",
        f"- all {ontology_validation['checks']['namedIdentities']} named identity observations mapped as source identities",
        f"- {ontology_validation['checks']['symbolDenotations']} printed-symbol denotations",
        f"- {ontology_validation['checks']['relations']} static relationship shapes / {ontology_validation['checks']['inversePairs']} inverse pairs",
        f"- {ontology_validation['checks']['staticAssertions']} source-backed structural assertions and constraints",
        f"- {ontology_validation['checks']['semanticScaffoldTaxa']} semantic-scaffolding taxa for later zones, timing, decisions, visibility, lifecycle, and finite supply",
        f"- {ontology_validation['checks']['openReviewGates']} ontology owner gates after four-workstream independent review",
        f"- {semantic_validation['checks']['sources']} exact source registry tuples",
        f"- {semantic_validation['checks']['semanticNodes']} semantic-only state/zone/position/visibility nodes",
        f"- {semantic_validation['checks']['records']} pilot records across {semantic_validation['checks']['systems']} systems",
        f"- {semantic_validation['checks']['sourceBacked']} source-backed",
        f"- {semantic_validation['checks']['withOpenQuestion']} source-backed with open questions",
        f"- {semantic_validation['checks']['sourceAssertions']} source assertions / {semantic_validation['checks']['conditions']} structured conditions and guards",
        f"- {semantic_validation['checks']['operations']} ordered operations",
        f"- {semantic_validation['checks']['decisions']} actor-owned decisions / {semantic_validation['checks']['informationPolicies']} information policies",
        f"- {semantic_validation['checks']['costs']} explicit costs / {semantic_validation['checks']['targets']} target specifications",
        f"- {semantic_validation['checks']['variantReferences']} preserved source-variant references",
        f"- {semantic_validation['checks']['openQuestions']} open semantic questions with explicit alternatives and defaults prohibited",
        f"- {semantic_validation['checks']['conflicts']} registered conflicts: {semantic_contradictions['counts']['resolvedByAuthority']} authority-resolved, {semantic_validation['checks']['unresolvedConflicts']} unresolved, {semantic_contradictions['counts']['preservedBoundary']} preserved boundaries",
        f"- base Event family: **{semantic_validation['checks']['eventIdentities']}/{semantic_validation['checks']['eventIdentities']} identities represented**",
        f"  - {semantic_validation['checks']['eventScanOccurrences']} exact Event scan occurrences",
        f"  - {semantic_validation['checks']['eventLicensedOccurrences']} licensed-digital Event occurrences retained as variants",
        f"  - {semantic_validation['checks']['eventOfficialOccurrences']} official visible component occurrences",
        f"  - {semantic_validation['checks']['eventRecords']} Event semantic records / {semantic_validation['checks']['eventBacklogTuples']} exact Event backlog tuples",
        f"- base Exploration family: **{semantic_validation['checks']['explorationIdentities']}/{semantic_validation['checks']['explorationIdentities']} untitled identities represented**",
        f"  - {semantic_validation['checks']['explorationScanOccurrences']} exact TTS CardID/GUID/FaceURL scan occurrences and 1 shared BackURL occurrence",
        f"  - {semantic_validation['checks']['explorationLicensedOccurrences']} licensed-digital Exploration occurrences retained as variants",
        f"  - {semantic_validation['checks']['explorationOfficialOccurrences']} official visible occurrences across 2 component identities",
        f"  - {semantic_validation['checks']['explorationPrintedSentences']} exact printed sentences / 12 source-local diagrams / {semantic_validation['checks']['explorationIconOccurrences']} functional icon occurrences",
        f"  - {semantic_validation['checks']['explorationRecords']} Exploration semantic records / {semantic_validation['checks']['explorationBacklogTuples']} exact Exploration backlog tuples",
        "  - 0 generated sprite-sheet cells and 0 selector gaps in the mechanically derived base family",
        f"- base Robot family: **{semantic_validation['checks']['robotIdentities']}/{semantic_validation['checks']['robotIdentities']} identities represented**",
        f"  - {semantic_validation['checks']['robotScanOccurrences']} exact TTS full-CardID/GUID/FaceURL scan occurrences and {semantic_validation['checks']['robotSharedBackOccurrences']} shared non-operative BackURL occurrence",
        f"  - {semantic_validation['checks']['robotLicensedOccurrences']} licensed-digital Robot occurrences retained as variants",
        f"  - {semantic_validation['checks']['robotOfficialOccurrences']} official visible face occurrences across 2 component identities",
        f"  - {semantic_validation['checks']['robotPhysicalPanels']} physical panels / {semantic_validation['checks']['robotOperativePanels']} operative rules panels / {semantic_validation['checks']['robotActionOptions']} printed options",
        f"  - {semantic_validation['checks']['robotPrintedSentences']} exact printed sentences / {semantic_validation['checks']['robotIconOccurrences']} functional icon occurrences",
        f"  - {semantic_validation['checks']['robotRecords']} Robot-face semantic records / {semantic_validation['checks']['robotBacklogTuples']} exact Robot backlog tuples",
        f"- base Intruder Attack family: **{semantic_validation['checks']['attackIdentities']}/{semantic_validation['checks']['attackIdentities']} mechanically selected physical occurrences represented**",
        f"  - {semantic_validation['checks']['attackGeneratedOccurrences']} exact generated-cell full-CardID/GUID/CustomDeck/FaceURL occurrences plus {semantic_validation['checks']['attackDirectOccurrences']} direct Blood Sense occurrence",
        "  - 8 printed titles with multiplicities preserved, including 6 distinct Bite copies; no title/cell/folder/modulo join",
        f"  - {semantic_validation['checks']['attackSharedBackOccurrences']} shared non-operative BackURL, {semantic_validation['checks']['attackSourceSheets']} parent 5×4 source sheet, and {semantic_validation['checks']['attackSelectorGaps']} unused selector-gap `SUMMONING` cell explicitly excluded from rules-face counts",
        f"  - {semantic_validation['checks']['attackPhysicalPanels']} physical panels / {semantic_validation['checks']['attackOperativePanels']} operative effect panels / {semantic_validation['checks']['attackPrintedSentences']} exact printed sentences",
        f"  - {semantic_validation['checks']['attackBadgeOccurrences']} literal applicability badges projected source-scoped from page-32 Adult/Drone/Queen templates, plus {semantic_validation['checks']['attackInlineIconOccurrences']} independently resolved inline icons; all {semantic_validation['checks']['attackSelectedNoMatches']} selected no-match rows remain intact",
        f"  - {semantic_validation['checks']['attackLicensedVariants']} licensed structured variants linked across {semantic_validation['checks']['attackLicensedFaceLinks']} physical occurrences, {semantic_validation['checks']['attackOfficialFaceCounterparts']} official-visible face counterparts, and {semantic_validation['checks']['attackOfficialBackCounterparts']} official-visible back counterpart retained independently",
        f"  - {semantic_validation['checks']['attackRecords']} Attack-face semantic records plus reusable finite Contamination gain and exact dispatch from `SEM-INT-004`; five new no-default questions preserve Fury scope, dead-target continuation, Blood Sense timing, Deadly Claws Wound order, and MISS applicability",
        "- core Combat/Attacks/Noise/Hazard/entry batch closed at its source-clear boundary",
        f"  - {semantic_validation['checks']['combatAttackClasses']} attack classes and {semantic_validation['checks']['combatMovementClasses']} movement classes retained without flattening; immediate entry/Secure/prevention timing is explicit",
        f"  - {semantic_validation['checks']['combatVisualObligations']} rendered visual obligations closed: `RB-P24-V02`, `RB-P25-V01/V02`, `RB-P30-V01/V02`, `RB-P33-V01/V02`, `RB-P34-V01`, and `RB-P40-V01`",
        f"  - {semantic_validation['checks']['combatNewQuestions']} new no-default questions retain Corridor/Intruder order, bag/Attack-deck exhaustion, Blank-row scope, death interruption, Larva continuation, Burst resolution, and mixed Adult/Drone allocation",
        f"  - {semantic_validation['checks']['combatNewConflicts']} new conflicts preserve the official current Noise set versus stale unbound TTS Silence/Danger branches and the side-level Blank-panel scope boundary",
        f"- complete base Action family: **{semantic_validation['checks']['actionPhysicalOccurrences']}/{semantic_validation['checks']['actionPhysicalOccurrences']} mechanically derived physical occurrences represented (10 per Character)**",
        "  - 55 exact Character-kit selectors plus 5 exact Shared Contractor selectors compose six ten-card decks; all copies retain full CardID/GUID/CustomDeck/FaceURL/BackURL/container provenance",
        f"  - {semantic_validation['checks']['actionDirectOccurrences']} direct faces plus {semantic_validation['checks']['actionGeneratedOccurrences']} selected generated cells across two 9×5 sheets; {semantic_validation['checks']['actionSelectorGaps']} source-clear base selector-gap cells and 40 expansion cells remain explicit exclusions",
        f"  - 60 selected face assets / {semantic_validation['checks']['actionUniqueTitles']} printed titles / one shared non-operative back with {semantic_validation['checks']['actionSharedBackReferences']} global references; repeated and cross-Character titles never collapse physical or semantic occurrences",
        f"  - {semantic_validation['checks']['actionPhysicalPanels']} physical panels / {semantic_validation['checks']['actionOperativePanels']} operative panels / {semantic_validation['checks']['actionPrintedSentences']} exact printed sentences / {semantic_validation['checks']['actionFunctionalIconOccurrences']} physical functional-icon occurrences ({semantic_validation['checks']['actionMatchedIconOccurrences']} source-resolved + {semantic_validation['checks']['actionUnresolvedLocalGlyphOccurrences']} literal local no-matches)",
        f"  - {semantic_validation['checks']['actionResolvedNotInCombatOccurrences']} source-resolved Not In Combat occurrences, {semantic_validation['checks']['actionUnresolvedUpperRightOccurrences']} unresolved upper-right local morphologies, and 24 absent upper-right regions remain source-scoped; no licensed-flag default is imported",
        f"  - {semantic_validation['checks']['actionLicensedOccurrences']} independent licensed rows retain {semantic_validation['checks']['actionLicensedReactionOccurrences']} Reactions, {semantic_validation['checks']['actionLicensedCommandOccurrences']} `command=true`, and {semantic_validation['checks']['actionLicensedNotInCombatOccurrences']} `noIntruders=true` occurrences with zero asserted TTS-copy identity links; {semantic_validation['checks']['actionOfficialFaceOccurrences']} official visible faces, {semantic_validation['checks']['actionOfficialBackOccurrences']} visible backs, and {semantic_validation['checks']['actionFaqOccurrences']} FAQ obligations remain independent",
        f"  - {semantic_validation['checks']['actionRecords']} physical main-effect records plus exact Action setup/play/payment/draw/reshuffle/Reaction/Command dispatch and {semantic_validation['checks']['actionReactionRecords']} Reaction-panel records; 18 new no-default questions retain glyph, payment, owner, consent, target, ordering, interruption, shortage, and lifecycle boundaries",
        f"- base competitive Objective/Mission family: **{semantic_validation['checks']['objectivePhysicalOccurrences']}/{semantic_validation['checks']['objectivePhysicalOccurrences']} mechanically derived physical copies represented at their source boundary ({semantic_validation['checks']['objectiveSourceClearPhysicalOccurrences']} source-clear + {semantic_validation['checks']['objectiveSourceBlockedPhysicalOccurrences']} exact-source blocker)**",
        f"  - {semantic_validation['checks']['objectiveGeneratedPhysicalOccurrences']} generated physical copies plus {semantic_validation['checks']['objectiveDirectPhysicalOccurrences']} direct physical copies; {semantic_validation['checks']['objectiveSourceFaceAssets']} exact face assets, 13 base-selected cells, {semantic_validation['checks']['objectiveSelectorGapAssets']} base selector-gap cells, two parent sheets, and two shared backs with 33 Objective plus 11 Mission Task global references remain role-distinct",
        f"  - {semantic_validation['checks']['objectivePhysicalPanels']} physical panels / {semantic_validation['checks']['objectivePrintedSentences']} exact printed sentence occurrences / {semantic_validation['checks']['objectiveFunctionalIconOccurrences']} physical functional-icon occurrences ({semantic_validation['checks']['objectiveMatchedIconOccurrences']} source-resolved + {semantic_validation['checks']['objectiveLiteralNoMatchIconOccurrences']} literal local no-matches) / {semantic_validation['checks']['objectiveCheckboxPhysicalOccurrences']} persistent checkbox occurrence; exact Number-of-Characters metadata, AND/OR grouping, punctuation, sheet cells, source selectors, and visibility remain locked",
        f"  - all {semantic_validation['checks']['objectiveOfficialHelpUnits']} official Objective Help units are linked independently: {semantic_validation['checks']['objectiveOfficialVisibleUnits']} fully visible and {semantic_validation['checks']['objectiveOfficialOccludedUnits']} physically occluded, with {semantic_validation['checks']['objectiveOfficialVisibleFaceRecords']} visible card records, 50 fully visible icons, 5 partial icons, and zero promotion of hidden PDF text-layer, TTS, or BGA wording into occluded official faces",
        f"  - {semantic_validation['checks']['objectiveLicensedRows']} licensed rows remain independent: {semantic_validation['checks']['objectiveLicensedCompetitiveRows']} competitive (18 Objectives + 8 Mission Tasks) and {semantic_validation['checks']['objectiveLicensedSoloCoopRowsExcluded']} Solo/Coop exclusions, with zero asserted physical-to-licensed or physical-to-official identity links",
        "  - 29 exact TTS physical-face, 20 official-visible-face, and 26 licensed competitive occurrence records plus reusable setup, secrecy/discussion/inspection, Objective Choice, fulfillment, Survivor/Escape, Facility destruction, Mission Task/check, and exact occurrence dispatch procedures; SEM-Q-075–078 retain OR-branch, continuous-unfulfilled, late-choice/reward, and reveal-order alternatives without defaults",
        f"- {semantic_validation['checks']['backlogUnits']} source-obligation backlog units",
        f"  - {semantic_validation['checks']['backlogPilotCovered']} pilot-covered",
        f"  - {semantic_validation['checks']['backlogUnits'] - semantic_validation['checks']['backlogPilotCovered'] - semantic_validation['checks']['backlogSourceBlocked']} pending",
        f"  - {semantic_validation['checks']['backlogSourceBlocked']} inherited exact-source blocker",
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
            "vocabularyEntries": vocab_validation["checks"]["canonicalVocabularyEntries"],
            "vocabularyOpenReviewGates": vocab_validation["checks"]["openReviewGates"],
            "ontologyTaxa": ontology_validation["checks"]["taxa"],
            "ontologyOpenReviewGates": ontology_validation["checks"]["openReviewGates"],
            "semanticPilotRecords": semantic_validation["checks"]["records"],
            "semanticOpenQuestions": semantic_validation["checks"]["openQuestions"],
        },
        "failureCount": len(failures),
        "failures": failures,
    }
    print(json.dumps(report, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
