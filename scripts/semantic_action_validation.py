from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path


PINNED_ACTION_SOURCE_INDEX_HASH = "640aef7685e24a67cb399151a3fdad3c0b349c658860a16edd1add86d6587752"
EXPECTED_COUNTS_DIGEST = "324623d34a17023e3f74661aac10fd8e6b6ef4fc526829e491c616e93f76caad"
EXPECTED_FACE_PROJECTION_DIGEST = "8e4f4a03c90104120a0fe7299d2d978b43e5bb9e8f4277e978d6b1729f0ec7d6"
EXPECTED_ASSET_PROJECTION_DIGEST = "4bc3cc8c76e6f6f1a4bf5f94ac9119ac096799eae2a8be7a25c6296d6be494d8"
EXPECTED_GAP_PROJECTION_DIGEST = "5bdd8aa17debbe6a6d3ce41896b9479c1c8ddc1bd049d1ec90d1f0c02d20309a"
EXPECTED_ROOT_PROJECTION_DIGEST = "6d0a1e775d3f29f65210780cde01beb561448ad152a0009bade77b629d5be321"
EXPECTED_DECK_PROJECTION_DIGEST = "58ac8cd043c4632868e76c31f02679ba7231439f75e4c041e5811eb140d9c937"
EXPECTED_SHEET_PROJECTION_DIGEST = "6379cdb7ab00bbc685ffc2105a0b141d2f78d27d966166de0cd17b2b46d71f1b"
EXPECTED_BACK_PROJECTION_DIGEST = "262aee533bea7b5170c4290e778f3ada2ca13392dafd8d65e4db9b759e656b67"
EXPECTED_LICENSED_PROJECTION_DIGEST = "83e78aa89738f7aa76fbad4063522ffcad906fc3fe20227755f5d3c477163772"
EXPECTED_OFFICIAL_PROJECTION_DIGEST = "033871678f9869dede9b86587b2324de561fbab4905055f636011bd26d12c2ad"
EXPECTED_FAQ_PROJECTION_DIGEST = "1406f37475cef9cf843cea7bfb7b35e3df477da4f7f237103a810ca66f9f8c9c"
EXPECTED_RECORD_PROJECTION_DIGEST = "bf274259dd596a8046e34301ec7becc094bf68ea887458bcfae5db8dcedf05ce"
EXPECTED_RECORD_ID_DIGEST = "a8de8dd8fa6c3bed398252232d1cbe370f31107f1644b54424eedce32ca80278"
EXPECTED_LINKED_BACKLOG_ID_DIGEST = "0ff7c2fcca6d3dac5ea3389a70af1db265dbfd9ed169d6885ffe3a50c9e8403e"

EXPECTED_REUSABLE_IDS = [
    "SEM-ACTION-DECK-SETUP-001",
    "SEM-ACTION-CARD-PLAY-001",
    "SEM-ACTION-CARD-PAYMENT-001",
    "SEM-ACTION-CARD-REACTION-001",
    "SEM-ACTION-CARD-COMMAND-001",
    "SEM-ACTION-CARD-VARIANT-BOUNDARIES-001",
    "SEM-ACTION-CARD-DRAW-001",
    "SEM-ACT-SEARCH-001",
    "SEM-ACT-REST-001",
    "SEM-REACTION-DUCK-001",
    "SEM-RT-012",
]


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()


def _face_projection(row: dict) -> dict:
    return {key: row.get(key) for key in [
        "character", "characterCode", "characterDeckId", "copyId", "deckGuid", "deckSegment", "rootSequence",
        "ttsCardId", "ttsCardGuid", "customDeckId", "sourceSelector", "sourceId", "sourcePath", "sourceSha256",
        "printedTitle", "printedBody", "printedFooter", "upperRight", "notInCombat", "reactionText", "effectKind",
        "printedCostClauses", "panels", "sentences", "iconOccurrences", "semanticRuleId", "reactionRuleId",
        "backlogUnitId", "identityJoinEvidence", "representationBoundary",
    ]}


def _asset_projection(row: dict) -> dict:
    return {key: row.get(key) for key in [
        "assetId", "sourceId", "sourcePath", "sourceSha256", "sourceRole", "sourceSheetId", "sourceSheetPath",
        "sourceSheetGrid", "customDeckId", "selectorGap", "backlogUnitId", "printedTitle", "printedBody",
        "printedFooter", "upperRight", "reactionText", "notInCombat", "panels", "sentences", "iconOccurrences",
        "representationBoundary",
    ]}


def _licensed_projection(row: dict) -> dict:
    return {key: row.get(key) for key in [
        "key", "character", "name", "effectDesc", "reactionDesc", "noIntruders", "command", "sourceBlockText",
        "assertedTtsPhysicalIdentityLinks",
    ]}


def validate_action_family(
    repo: Path,
    source_path: Path,
    source: dict,
    source_by_id: dict[str, dict],
    backlog_by_id: dict[str, dict],
    record_by_id: dict[str, dict],
    question_by_id: dict[str, dict],
    conflict_rows: list[dict],
    coverage: dict,
    failures: list[dict],
) -> dict:
    faces = source.get("faces") or []
    assets = source.get("sourceFaceAssets") or []
    gaps = [row for row in assets if row.get("selectorGap")]
    roots = source.get("rootDeckEvidence") or []
    decks = source.get("characterDecks") or []
    sheets = source.get("sourceSheets") or []
    back = source.get("sharedBack") or {}
    licensed = source.get("licensedDigitalOccurrences") or []

    if _sha(source_path) != PINNED_ACTION_SOURCE_INDEX_HASH:
        failures.append({"check": "pinned Action source index"})
    if _digest(source.get("counts")) != EXPECTED_COUNTS_DIGEST:
        failures.append({"check": "Action exact family counts"})
    expected_headline = {
        "officialActionCardTotal": 60,
        "officialCharacters": 6,
        "officialCardsPerCharacter": 10,
        "physicalFaceOccurrences": 60,
        "sourceFaceAssets": 89,
        "baseSelectorGapCells": 29,
        "excludedExpansionSheetCells": 40,
        "licensedDigitalOccurrences": 60,
        "backlogTuples": 89,
        "semanticPhysicalFaceRecords": 60,
    }
    if any((source.get("counts") or {}).get(key) != value for key, value in expected_headline.items()):
        failures.append({"check": "Action official/physical/source/licensed reconciliation"})

    face_ids = [row.get("occurrenceId") for row in faces]
    copy_ids = [row.get("copyId") for row in faces]
    rule_ids = [row.get("semanticRuleId") for row in faces]
    if len(faces) != 60 or len(set(face_ids)) != 60 or len(set(copy_ids)) != 60 or len(set(rule_ids)) != 60:
        failures.append({"check": "Action dropped/duplicated physical copy closure"})
    if Counter(row.get("character") for row in faces) != Counter({
        "Combat Engineer": 10, "Heavy Gun Operator": 10, "Medical Support": 10,
        "Contractor": 10, "Officer": 10, "Recon": 10,
    }):
        failures.append({"check": "Action exact 10x6 Character partition"})
    if _digest([_face_projection(row) for row in faces]) != EXPECTED_FACE_PROJECTION_DIGEST:
        failures.append({"check": "Action exact occurrence tuple/anatomy/text/cost/icon projection"})
    if _digest([_asset_projection(row) for row in assets]) != EXPECTED_ASSET_PROJECTION_DIGEST:
        failures.append({"check": "Action exact source-face asset/selector closure"})
    if _digest([_asset_projection(row) for row in gaps]) != EXPECTED_GAP_PROJECTION_DIGEST:
        failures.append({"check": "Action exact selector-gap variant closure"})
    if _digest(roots) != EXPECTED_ROOT_PROJECTION_DIGEST:
        failures.append({"check": "Action exact root/member tuple projection"})
    if _digest(decks) != EXPECTED_DECK_PROJECTION_DIGEST:
        failures.append({"check": "Action Character deck/member swap closure"})
    if _digest(sheets) != EXPECTED_SHEET_PROJECTION_DIGEST:
        failures.append({"check": "Action sheet/grid/cell/expansion boundary closure"})
    if _digest(back) != EXPECTED_BACK_PROJECTION_DIGEST:
        failures.append({"check": "Action shared-back role/reference closure"})

    # Re-read every exact source tuple rather than trusting the generated hash.
    for face in faces:
        path = repo / str(face.get("sourcePath") or "")
        registry = source_by_id.get(face.get("sourceId")) or {}
        if not path.is_file() or _sha(path) != face.get("sourceSha256"):
            failures.append({"check": "Action live physical source hash", "occurrenceId": face.get("occurrenceId")})
        if (registry.get("path"), registry.get("sha256"), registry.get("occurrenceId"), registry.get("authority")) != (
            face.get("sourcePath"), face.get("sourceSha256"), face.get("occurrenceId"), "source-bound-component-scan",
        ):
            failures.append({"check": "Action exact source-registry physical tuple", "occurrenceId": face.get("occurrenceId")})
        selector = face.get("sourceSelector") or {}
        forbidden = face.get("identityJoinEvidence") or {}
        if (
            selector.get("fullCardId") != face.get("ttsCardId")
            or selector.get("guid") != face.get("ttsCardGuid")
            or selector.get("parentDeckGuid") != face.get("deckGuid")
            or selector.get("backUrl") != "https://steamusercontent-a.akamaihd.net/ugc/10207952820401286363/045849F3D9E78090494EBF29460723DFD3BF642F/"
            or selector.get("cardIdModuloJoinUsed") is not False
            or any(forbidden.get(key) is not False for key in (
                "characterNameOnlyJoin", "titleOnlyJoin", "bodySimilarityJoin", "folderOnlyJoin", "sourceSheetOnlyJoin",
                "generatedCellOnlyJoin", "cardIdModuloJoin", "licensedKeyJoin",
            ))
        ):
            failures.append({"check": "Action prohibited title/Character/folder/sheet/cell/modulo join", "occurrenceId": face.get("occurrenceId")})
        if selector.get("url") == selector.get("backUrl") or selector.get("sideRole") != "operative-base-Action-face":
            failures.append({"check": "Action selector/back inversion", "occurrenceId": face.get("occurrenceId")})
        panel_ids = [panel.get("panelId") for panel in face.get("panels") or []]
        sentence_panels = [sentence.get("panelId") for sentence in face.get("sentences") or []]
        if (
            [panel.get("readingOrder") for panel in face.get("panels") or []] != list(range(1, len(panel_ids) + 1))
            or len(panel_ids) != len(set(panel_ids))
            or any(panel_id not in panel_ids for panel_id in sentence_panels)
            or [sentence.get("sequence") for sentence in face.get("sentences") or []] != list(range(1, len(sentence_panels) + 1))
        ):
            failures.append({"check": "Action panel/sentence order closure", "occurrenceId": face.get("occurrenceId")})

    if len(assets) != 89 or len(gaps) != 29 or sum(row.get("selectedByPhysicalRoot") is True for row in assets) != 60:
        failures.append({"check": "Action selected/gap source-asset partition"})
    if len(sheets) != 2 or sorted(len(row.get("selectedCells") or []) for row in sheets) != [5, 16] or sum(len(row.get("expansionCellsExcluded") or []) for row in sheets) != 40:
        failures.append({"check": "Action exact generated selector/expansion-cell partition"})
    if back.get("globalReferenceCount") != 273 or back.get("physicalSelectorReferences") != 60 or back.get("rulesFaceCounted") is not False:
        failures.append({"check": "Action back non-operative/273-reference lock"})

    if len(licensed) != 60 or _digest([_licensed_projection(row) for row in licensed]) != EXPECTED_LICENSED_PROJECTION_DIGEST:
        failures.append({"check": "Action exact independent licensed row/variant closure"})
    if any(row.get("assertedTtsPhysicalIdentityLinks") for row in licensed) or (source.get("counts") or {}).get("assertedPhysicalToLicensedIdentityLinks") != 0:
        failures.append({"check": "Action no physical-to-licensed title/Character join"})
    if (
        sum(bool(row.get("reactionDesc")) for row in licensed) != 6
        or sum(row.get("command") is True for row in licensed) != 7
        or sum(row.get("noIntruders") is True for row in licensed) != 35
    ):
        failures.append({"check": "Action licensed Reaction/Command/Not-in-Combat field closure"})
    if _digest(source.get("officialVisibleOccurrences")) != EXPECTED_OFFICIAL_PROJECTION_DIGEST:
        failures.append({"check": "Action current-official visible occurrence boundary"})
    if _digest(source.get("faqOccurrences")) != EXPECTED_FAQ_PROJECTION_DIGEST:
        failures.append({"check": "Action exact FAQ obligation linkage"})

    expected_backlog_rules = {}
    for asset in assets:
        unit_id = asset.get("backlogUnitId")
        matching = [row.get("semanticRuleId") for row in faces if row.get("sourcePath") == asset.get("sourcePath")]
        expected_backlog_rules[unit_id] = matching or ["SEM-ACTION-CARD-VARIANT-BOUNDARIES-001"]
    for unit_id, expected_rules in expected_backlog_rules.items():
        row = backlog_by_id.get(unit_id) or {}
        if row.get("pilotRuleIds") != expected_rules or row.get("status") != "pilot-covered":
            failures.append({"check": "Action exact backlog tuple projection", "semanticUnitId": unit_id})
    linked_ids = (source.get("familyCountEvidence") or {}).get("backlog", {}).get("linkedUnitIds") or []
    if _digest(linked_ids) != EXPECTED_LINKED_BACKLOG_ID_DIGEST or len(linked_ids) != 115:
        failures.append({"check": "Action exact overlapping backlog-obligation closure"})
    for unit_id in linked_ids:
        if (backlog_by_id.get(unit_id) or {}).get("status") != "pilot-covered":
            failures.append({"check": "Action linked backlog obligation status", "semanticUnitId": unit_id})

    new_reaction_ids = sorted({
        row.get("reactionRuleId") for row in faces
        if row.get("reactionRuleId") and row.get("reactionRuleId") != "SEM-REACTION-DUCK-001"
    })
    expected_record_ids = sorted(set([*EXPECTED_REUSABLE_IDS, *rule_ids, *new_reaction_ids]))
    if _digest(expected_record_ids) != EXPECTED_RECORD_ID_DIGEST or len(expected_record_ids) != 76:
        failures.append({"check": "Action independently locked semantic rule-ID set"})
    if any(rule_id not in record_by_id for rule_id in expected_record_ids):
        failures.append({"check": "Action semantic record closure"})
    if _digest([record_by_id.get(rule_id) for rule_id in expected_record_ids]) != EXPECTED_RECORD_PROJECTION_DIGEST:
        failures.append({"check": "Action independently locked ordered semantic atoms"})

    for face in faces:
        record = record_by_id.get(face.get("semanticRuleId")) or {}
        scan = next((row for row in record.get("sourceAssertions") or [] if row.get("sourceId") == face.get("sourceId")), {})
        expected_text = face.get("printedBody") + (("\n\nREACTION\n" + face.get("reactionText")) if face.get("reactionText") else "")
        if scan.get("sourceText") != expected_text or scan.get("textKind") != "verbatim" or scan.get("sourceSha256") != face.get("sourceSha256"):
            failures.append({"check": "Action exact face/body/punctuation semantic assertion", "ruleId": face.get("semanticRuleId")})
        valid_panels = {panel.get("panelId") for panel in face.get("panels") or [] if panel.get("operative")}
        operation_panels = [panel_id for op in record.get("operations") or [] for panel_id in op.get("sourcePanelIds") or []]
        if not operation_panels or any(panel_id not in valid_panels for panel_id in operation_panels):
            failures.append({"check": "Action semantic operation/panel support closure", "ruleId": face.get("semanticRuleId")})
        nic_status = (face.get("notInCombat") or {}).get("status")
        terms = set(record.get("termRefs") or [])
        if nic_status == "source-resolved" and "icon.notInCombat" not in terms:
            failures.append({"check": "Action source-resolved Not-in-Combat projection", "ruleId": face.get("semanticRuleId")})
        if nic_status == "literal-unresolved" and ("icon.notInCombat" in terms or "SEM-Q-057" not in (record.get("unresolvedQuestionRefs") or [])):
            failures.append({"check": "Action unresolved upper-right no-default lock", "ruleId": face.get("semanticRuleId")})
        if any(variant.get("sourceId") == "SRC-BGA-ACTION-CARDS" for variant in record.get("sourceVariants") or []):
            failures.append({"check": "Action no per-face licensed identity assertion", "ruleId": face.get("semanticRuleId")})

    play = record_by_id.get("SEM-ACTION-CARD-PLAY-001") or {}
    play_dispatch = next((op.get("dispatchRuleIds") for op in play.get("operations") or [] if op.get("dispatchRuleIds")), None)
    if play_dispatch != rule_ids or [op.get("operationType") for op in play.get("operations") or []] != ["play-card", "invoke-selected-process", "resolve-open-alternative", "transition-zone"]:
        failures.append({"check": "Action exact physical occurrence play/discard dispatcher"})
    if not any("owner-private" in row.get("audience", "") and "common backs" in row.get("secrecy", "") for row in play.get("informationPolicy") or []):
        failures.append({"check": "Action private-hand visibility/no-leakage lock"})
    if any((op.get("transition") or {}).get("to") == "tax.scaffold.zone.discard-pile" and "played" in op.get("objectRef", "").lower() for rule_id in rule_ids for op in (record_by_id.get(rule_id) or {}).get("operations") or []):
        failures.append({"check": "Action generic discard ownership/no-double-discard lock"})

    reaction = record_by_id.get("SEM-ACTION-CARD-REACTION-001") or {}
    reaction_dispatch = next((op.get("dispatchRuleIds") for op in reaction.get("operations") or [] if op.get("dispatchRuleIds")), None)
    expected_reaction_dispatch = ["SEM-REACTION-DUCK-001", *new_reaction_ids]
    if reaction_dispatch != expected_reaction_dispatch or len(expected_reaction_dispatch) != 6:
        failures.append({"check": "Action exact Reaction panel dispatcher/no-flattening lock"})
    command = record_by_id.get("SEM-ACTION-CARD-COMMAND-001") or {}
    if "SEM-Q-059" not in (command.get("unresolvedQuestionRefs") or []) or not any(op.get("operationType") == "resolve-open-alternative" for op in command.get("operations") or []):
        failures.append({"check": "Action Command cost/owner/no-default lock"})
    if sum(sum(panel.get("heading") == "COMMAND" for panel in face.get("panels") or []) for face in faces) != 8 or sum(sum(panel.get("heading") == "REACTION" for panel in face.get("panels") or []) for face in faces) != 6:
        failures.append({"check": "Action Command/Reaction printed heading closure"})

    setup = record_by_id.get("SEM-ACTION-DECK-SETUP-001") or {}
    setup_text = json.dumps(setup, ensure_ascii=False)
    if not all(fragment in setup_text for fragment in ("BASE-ACTION-DECK-CE", "BASE-ACTION-DECK-CON", "include" if False else "noTitleOrCharacterNameOnlyJoin")):
        failures.append({"check": "Action exact setup/deck membership lifecycle lock"})
    draw = record_by_id.get("SEM-ACTION-CARD-DRAW-001") or {}
    if [op.get("operationType") for op in draw.get("operations") or []] != ["evaluate-condition", "shuffle", "draw-random", "resolve-open-alternative"] or "SEM-Q-072" not in (draw.get("unresolvedQuestionRefs") or []):
        failures.append({"check": "Action draw/reshuffle/shortage lifecycle lock"})
    search = record_by_id.get("SEM-ACT-SEARCH-001") or {}
    rest = record_by_id.get("SEM-ACT-REST-001") or {}
    duck = record_by_id.get("SEM-REACTION-DUCK-001") or {}
    if any("played Search" in op.get("objectRef", "") for op in search.get("operations") or []) or any("played Rest" in op.get("objectRef", "") for op in rest.get("operations") or []) or any(op.get("operationType") in {"play-card", "transition-zone"} for op in duck.get("operations") or []):
        failures.append({"check": "Action reusable effect versus generic card-lifecycle separation"})

    action_question_ids = [f"SEM-Q-{number:03d}" for number in range(57, 75)]
    semantic_records = {rule_id: record_by_id.get(rule_id) or {} for rule_id in expected_record_ids}
    for question_id in action_question_ids:
        question = question_by_id.get(question_id) or {}
        actual_blocked = sorted(rule_id for rule_id, record in semantic_records.items() if question_id in (record.get("unresolvedQuestionRefs") or []))
        if question.get("defaultProhibited") is not True or sorted(question.get("blocksRuleIds") or []) != actual_blocked or not actual_blocked:
            failures.append({"check": "Action ambiguity owner/target/consent/default linkage", "questionId": question_id})
    action_conflicts = [row for row in conflict_rows if row.get("conflictId") in {f"SC-{number:03d}" for number in range(49, 59)}]
    if [row.get("conflictId") for row in action_conflicts] != [f"SC-{number:03d}" for number in range(49, 59)] or Counter(row.get("status") for row in action_conflicts) != Counter({"preserved-boundary": 7, "unresolved": 3}):
        failures.append({"check": "Action exact conflict/variant/authority register closure"})

    action_system = next((row for row in coverage.get("systems") or [] if row.get("system") == "complete base Action card/component family"), {})
    expected_system_ids = [
        "SEM-ACTION-DECK-SETUP-001", "SEM-ACTION-CARD-PLAY-001", "SEM-ACTION-CARD-PAYMENT-001",
        "SEM-ACTION-CARD-REACTION-001", "SEM-ACTION-CARD-COMMAND-001", "SEM-ACTION-CARD-VARIANT-BOUNDARIES-001",
        *rule_ids, *new_reaction_ids,
    ]
    not_yet_text = " ".join(coverage.get("notYetCovered") or [])
    if action_system.get("ruleIds") != expected_system_ids or "all remaining Heavy/Equipment/Starting, Action" in not_yet_text or "all Action" in not_yet_text:
        failures.append({"check": "Action family coverage/no-full-coverage boundary"})

    return {
        "faces": faces,
        "assets": assets,
        "gaps": gaps,
        "roots": roots,
        "decks": decks,
        "sheets": sheets,
        "back": back,
        "licensed": licensed,
        "official": source.get("officialVisibleOccurrences") or {},
        "faq": source.get("faqOccurrences") or [],
        "actualRuleIds": rule_ids,
        "reactionRuleIds": new_reaction_ids,
        "expectedBacklogRules": expected_backlog_rules,
        "expectedRecordIds": expected_record_ids,
    }
