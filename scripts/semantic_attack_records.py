from __future__ import annotations

import ast
from collections import Counter
import hashlib
import json
import re
import struct
from pathlib import Path

from PIL import Image


BASE_ATTACK_DECK_GUID = "34c73e"
ATTACK_SHEET_SOURCE_ID = "SRC-ATTACK-SHEET"
ATTACK_SHEET_PATH = "assets/tts-mod/extract/v2-dl/tree/cards/game/attack-151.jpg"
ATTACK_BACK_SOURCE_ID = "SRC-ATTACK-BACK"
ATTACK_BACK_PATH = "assets/tts-mod/extract/v2-dl/tree/cards/game/attack-020.png"
BGA_ATTACK_SOURCE_ID = "SRC-BGA-INTRUDER-ATTACKS"
BGA_ATTACK_PATH = "docs/rules/source-extraction/secondary/bga-staticData-260622-1220.js"
RAW_SAVE_PATH = "assets/tts-mod/extract/nemesis_script_mod.bin"


def _sentence(sentence_id: str, panel_id: str, exact_text: str) -> dict:
    return {"sentenceId": sentence_id, "panelId": panel_id, "exactText": exact_text}


def _definition(
    card_id: int,
    *,
    title: str,
    bga_key: str,
    panels: list[str],
    sentences: list[tuple[str, str, str]],
    badges: list[tuple[str, str]],
    family: str,
    named_identity: str | None,
    questions: list[str] | None = None,
    official_refs: list[str] | None = None,
    generated_cell: int | None = None,
    tts_guid: str,
    deck_sequence: int,
    variant_difference: str,
) -> dict:
    return {
        "sourceId": f"SRC-ATTACK-{card_id}",
        "ruleId": f"SEM-ATTACK-{card_id}-001",
        "title": title,
        "bgaKey": bga_key,
        "panelTexts": panels,
        "sentences": [_sentence(*row) for row in sentences],
        "badgePanels": [{"panelId": panel_id, "intruderType": intruder_type} for panel_id, intruder_type in badges],
        "family": family,
        "namedIdentityRefs": [named_identity] if named_identity else [],
        "questions": questions or [],
        "officialCounterpartRefs": official_refs or [],
        "generatedCellIndex": generated_cell,
        "ttsGuid": tts_guid,
        "deckSequence": deck_sequence,
        "variantDifference": variant_difference,
    }


ATTACK_DEFINITIONS: dict[int, dict] = {}

_bite_panel = "If you are Heavily Injured,\nyou die.\n\nOtherwise, you get\n1 Serious Wound and\n1 Contamination card."
_bite_sentences = [
    ("ATK-BITE-S01", "P3", "If you are Heavily Injured,\nyou die."),
    ("ATK-BITE-S02", "P3", "Otherwise, you get\n1 Serious Wound and\n1 Contamination card."),
]
_bite_meta = [
    (394900, 0, "5afea3", 2),
    (394901, 1, "f59fca", 4),
    (394902, 2, "ca7eaf", 5),
    (394903, 3, "d4547c", 3),
    (394904, 4, "5e9926", 1),
    (394905, 5, "d98fc8", 6),
]
for card_id, cell, guid, sequence in _bite_meta:
    ATTACK_DEFINITIONS[card_id] = _definition(
        card_id,
        title="BITE",
        bga_key="IntruderAttack_Bite",
        panels=[_bite_panel],
        sentences=[(f"ATK-{card_id}-S{index:02d}", panel_id, text) for index, (_, panel_id, text) in enumerate(_bite_sentences, 1)],
        badges=[("P3", "Adult"), ("P3", "Queen"), ("P3", "Drone")],
        family="bite",
        named_identity="NI-0029",
        questions=["SEM-Q-021"],
        official_refs=["RB-P03-V01-ATTACK-BITE"],
        generated_cell=cell,
        tts_guid=guid,
        deck_sequence=sequence,
        variant_difference="The scan says “get” and “Contamination card”; the official-visible and licensed occurrences say “gain” and omit “card”. Applicability is the same, but every physical scan copy remains a distinct occurrence.",
    )

ATTACK_DEFINITIONS[394906] = _definition(
    394906,
    title="DEADLY CLAWS",
    bga_key="IntruderAttack_DeadlyClaws1",
    panels=[
        "Lose 1 [LOCAL_ICON:INLINE-1].",
        "If you are Heavily Injured, you die.\nOtherwise, get a Serious Wound\non each empty Serious Wound\nslot to the right\nof your Health marker.\nThen, get 1 Serious Wound more.",
    ],
    sentences=[
        ("ATK-394906-P3-S01", "P3", "Lose 1 [LOCAL_ICON:INLINE-1]."),
        ("ATK-394906-P4-S01", "P4", "If you are Heavily Injured, you die."),
        ("ATK-394906-P4-S02", "P4", "Otherwise, get a Serious Wound\non each empty Serious Wound\nslot to the right\nof your Health marker."),
        ("ATK-394906-P4-S03", "P4", "Then, get 1 Serious Wound more."),
    ],
    badges=[("P3", "Adult"), ("P3", "Drone"), ("P4", "Queen")],
    family="deadly-claws",
    named_identity="NI-0123",
    questions=["SEM-Q-021", "SEM-Q-023"],
    generated_cell=6,
    tts_guid="aa3f4a",
    deck_sequence=8,
    variant_difference="The scan assigns Adult+Drone to Lose 1 and Queen to its multi-Wound branch. The licensed record assigns Adult+Queen to Lose 1 and Drone to the current injured-state branch. No title-only merge is made.",
)
ATTACK_DEFINITIONS[394907] = _definition(
    394907,
    title="DEADLY CLAWS",
    bga_key="IntruderAttack_DeadlyClaws2",
    panels=[
        "Lose 2 [characterHealth].\nGet 1 Contamination.",
        "If you are Heavily Injured, you die.\n\nOtherwise, get a Serious Wound\non each empty Serious Wound\nslot to the right\nof your Health marker.\n\nThen, get 1 Serious Wound more.",
    ],
    sentences=[
        ("ATK-394907-P3-S01", "P3", "Lose 2 [characterHealth]."),
        ("ATK-394907-P3-S02", "P3", "Get 1 Contamination."),
        ("ATK-394907-P4-S01", "P4", "If you are Heavily Injured, you die."),
        ("ATK-394907-P4-S02", "P4", "Otherwise, get a Serious Wound\non each empty Serious Wound\nslot to the right\nof your Health marker."),
        ("ATK-394907-P4-S03", "P4", "Then, get 1 Serious Wound more."),
    ],
    badges=[("P3", "Adult"), ("P3", "Drone"), ("P4", "Queen")],
    family="deadly-claws",
    named_identity="NI-0123",
    questions=["SEM-Q-021", "SEM-Q-023"],
    official_refs=["RB-P03-V01-ATTACK-DEADLY-CLAWS"],
    generated_cell=7,
    tts_guid="58a1fa",
    deck_sequence=9,
    variant_difference="The scan assigns Adult+Drone to Lose 2 plus Contamination and Queen to a multi-Wound branch. The official-visible/licensed current occurrence assigns Adult+Queen to the first panel and Drone to a different injured-state branch.",
)
ATTACK_DEFINITIONS[394908] = _definition(
    394908,
    title="DEADLY CLAWS",
    bga_key="IntruderAttack_DeadlyClaws3",
    panels=[
        "Lose 3 [characterHealth].",
        "If you are Heavily Injured, you die.\n\nOtherwise, get a Serious Wound\non each empty Serious Wound\nslot to the right\nof your Health marker.\n\nThen, get 1 Serious Wound more.",
    ],
    sentences=[
        ("ATK-394908-P3-S01", "P3", "Lose 3 [characterHealth]."),
        ("ATK-394908-P4-S01", "P4", "If you are Heavily Injured, you die."),
        ("ATK-394908-P4-S02", "P4", "Otherwise, get a Serious Wound\non each empty Serious Wound\nslot to the right\nof your Health marker."),
        ("ATK-394908-P4-S03", "P4", "Then, get 1 Serious Wound more."),
    ],
    badges=[("P3", "Adult"), ("P3", "Drone"), ("P4", "Queen")],
    family="deadly-claws",
    named_identity="NI-0123",
    questions=["SEM-Q-021", "SEM-Q-023"],
    generated_cell=8,
    tts_guid="2bc4ac",
    deck_sequence=10,
    variant_difference="The scan assigns Adult+Drone to Lose 3 and Queen to its multi-Wound branch. The licensed current record assigns Adult+Queen to Lose 3 and Drone to a different injured-state branch.",
)

for card_id, cell, guid, sequence, amount, bga_key in (
    (394909, 9, "a58129", 11, 1, "IntruderAttack_Fury1"),
    (394910, 10, "d78969", 12, 2, "IntruderAttack_Fury2"),
):
    ATTACK_DEFINITIONS[card_id] = _definition(
        card_id,
        title="FURY",
        bga_key=bga_key,
        panels=[
            f"Lose {amount} [characterHealth].\nGet 1 Contamination.",
            "All Heavily Injured\nCharacters die.\n\nAll Characters who survived,\nget 1 Serious Wound and\n1 Contamination card.",
        ],
        sentences=[
            (f"ATK-{card_id}-P3-S01", "P3", f"Lose {amount} [characterHealth]."),
            (f"ATK-{card_id}-P3-S02", "P3", "Get 1 Contamination."),
            (f"ATK-{card_id}-P4-S01", "P4", "All Heavily Injured\nCharacters die."),
            (f"ATK-{card_id}-P4-S02", "P4", "All Characters who survived,\nget 1 Serious Wound and\n1 Contamination card."),
        ],
        badges=[("P3", "Adult"), ("P4", "Queen"), ("P4", "Drone")],
        family="fury",
        named_identity="NI-0218",
        questions=["SEM-Q-020", "SEM-Q-021"],
        generated_cell=cell,
        tts_guid=guid,
        deck_sequence=sequence,
        variant_difference="The scan says all Heavily Injured Characters and all survivors without a Room qualifier. The licensed occurrence limits both cohorts to the attacking Character's Room and says each other Character; this lower-authority scope is retained as an unresolved lead.",
    )

ATTACK_DEFINITIONS[394911] = _definition(
    394911,
    title="INFECTING",
    bga_key="IntruderAttack_Infecting",
    panels=[
        "Lose 2 [characterHealth].",
        "Get 1 Contamination card.\n\nIf you don’t have a Larva\non your Character board,\nplace one there.",
    ],
    sentences=[
        ("ATK-394911-P3-S01", "P3", "Lose 2 [characterHealth]."),
        ("ATK-394911-P4-S01", "P4", "Get 1 Contamination card."),
        ("ATK-394911-P4-S02", "P4", "If you don’t have a Larva\non your Character board,\nplace one there."),
    ],
    badges=[("P3", "Adult"), ("P3", "Queen"), ("P4", "Drone")],
    family="infecting",
    named_identity="NI-0254",
    official_refs=["RB-P32-V01-ATTACK-INFECTING"],
    generated_cell=11,
    tts_guid="f8df5b",
    deck_sequence=13,
    variant_difference="The scan assigns Adult+Queen to Lose 2 and Drone to Contamination/Larva placement. The official page-32 anatomy and licensed occurrence assign Adult+Drone to Lose 2 and Queen to the infection panel; wording also differs between don’t have and not Infected.",
)

ATTACK_DEFINITIONS[394912] = _definition(
    394912,
    title="MISS",
    bga_key="IntruderAttack_Miss",
    panels=["Nothing happens.\nReshuffle the Intruder Attack deck."],
    sentences=[
        ("ATK-394912-P3-S01", "P3", "Nothing happens."),
        ("ATK-394912-P3-S02", "P3", "Reshuffle the Intruder Attack deck."),
    ],
    badges=[],
    family="miss",
    named_identity=None,
    questions=["SEM-Q-024"],
    generated_cell=12,
    tts_guid="0959a7",
    deck_sequence=18,
    variant_difference="The licensed record explicitly applies the effect to Adult, Drone, and Queen but misspells “Intuder.” The scan prints no applicability badges; FAQ v1.2 controls self-inclusive reshuffling only if the effect applies.",
)

_scratch_defs = [
    (394913, 13, "e8555f", 16, "IntruderAttack_Scratch1", ["Get 1 Contamination."], []),
    (394914, 14, "09613e", 14, "IntruderAttack_Scratch2", ["Lose 1 [characterHealth].", "Get 1 Contamination."], ["SEM-Q-021"]),
    (394915, 15, "e7be5a", 15, "IntruderAttack_Scratch3", ["Lose 1 [characterHealth]."], []),
    (394916, 16, "b9afbe", 17, "IntruderAttack_Scratch4", ["Lose 2 [characterHealth]."], []),
]
for card_id, cell, guid, sequence, bga_key, sentence_texts, questions in _scratch_defs:
    panel = "\n".join(sentence_texts)
    ATTACK_DEFINITIONS[card_id] = _definition(
        card_id,
        title="SCRATCH",
        bga_key=bga_key,
        panels=[panel],
        sentences=[(f"ATK-{card_id}-P3-S{index:02d}", "P3", text) for index, text in enumerate(sentence_texts, 1)],
        badges=[("P3", "Adult"), ("P3", "Queen"), ("P3", "Drone")],
        family="scratch",
        named_identity="NI-0425",
        questions=questions,
        generated_cell=cell,
        tts_guid=guid,
        deck_sequence=sequence,
        variant_difference="The scan and licensed occurrence preserve the same effect variant; capitalization, HP placeholder syntax, punctuation, and the physical source occurrence remain independent.",
    )

ATTACK_DEFINITIONS[394918] = _definition(
    394918,
    title="TAIL ATTACK",
    bga_key="IntruderAttack_TailAttack1",
    panels=[
        "Get 1 Contamination",
        "If you are Injured or Heavily\nInjured, you die.\nOtherwise, you get\n1 Serious Wound and\n1 Contamination card.",
    ],
    sentences=[
        ("ATK-394918-P3-S01", "P3", "Get 1 Contamination"),
        ("ATK-394918-P4-S01", "P4", "If you are Injured or Heavily\nInjured, you die."),
        ("ATK-394918-P4-S02", "P4", "Otherwise, you get\n1 Serious Wound and\n1 Contamination card."),
    ],
    badges=[("P3", "Adult"), ("P3", "Queen"), ("P4", "Drone")],
    family="tail-attack",
    named_identity="NI-0475",
    questions=["SEM-Q-021"],
    generated_cell=18,
    tts_guid="f08b5b",
    deck_sequence=20,
    variant_difference="The scan assigns Adult+Queen to Contamination and Drone to the lethal branch. The licensed record assigns Adult+Drone to Contamination and Queen to the lethal branch; the scan also omits terminal punctuation on its first panel.",
)
ATTACK_DEFINITIONS[394919] = _definition(
    394919,
    title="TAIL ATTACK",
    bga_key="IntruderAttack_TailAttack2",
    panels=[
        "Lose 1 [characterHealth].\nGet 1 Contamination.",
        "If you are Injured or Heavily\nInjured, you die.\nOtherwise, you get\n1 Serious Wound and\n1 Contamination card.",
    ],
    sentences=[
        ("ATK-394919-P3-S01", "P3", "Lose 1 [characterHealth]."),
        ("ATK-394919-P3-S02", "P3", "Get 1 Contamination."),
        ("ATK-394919-P4-S01", "P4", "If you are Injured or Heavily\nInjured, you die."),
        ("ATK-394919-P4-S02", "P4", "Otherwise, you get\n1 Serious Wound and\n1 Contamination card."),
    ],
    badges=[("P3", "Adult"), ("P3", "Queen"), ("P4", "Drone")],
    family="tail-attack",
    named_identity="NI-0475",
    questions=["SEM-Q-021"],
    generated_cell=19,
    tts_guid="6caa45",
    deck_sequence=19,
    variant_difference="The scan assigns Adult+Queen to Health loss/Contamination and Drone to the lethal branch. The licensed record assigns Adult+Drone to the first panel and Queen to the lethal branch.",
)

ATTACK_DEFINITIONS[399100] = _definition(
    399100,
    title="BLOOD SENSE",
    bga_key="IntruderAttack_BloodSense",
    panels=[
        "Lose 2 [characterHealth].",
        "Lose 2 [characterHealth].\nIf you are Moving, place the\nAttacking [intruder] in the Room where\nyour Movement ends.\n(It does not Attack again)",
    ],
    sentences=[
        ("ATK-399100-P3-S01", "P3", "Lose 2 [characterHealth]."),
        ("ATK-399100-P4-S01", "P4", "Lose 2 [characterHealth]."),
        ("ATK-399100-P4-S02", "P4", "If you are Moving, place the\nAttacking [intruder] in the Room where\nyour Movement ends."),
        ("ATK-399100-P4-S03", "P4", "(It does not Attack again)"),
    ],
    badges=[("P3", "Adult"), ("P4", "Drone"), ("P4", "Queen")],
    family="blood-sense",
    named_identity="NI-0031",
    questions=["SEM-Q-022"],
    generated_cell=None,
    tts_guid="50e156",
    deck_sequence=7,
    variant_difference="The selected source-bound reread corrects the earlier corpus snapshot's “you Movement ends” to visibly printed “your Movement ends.” The licensed occurrence normalizes line grouping and lowercase attack wording; all snapshots remain traceable.",
)

ATTACK_RULE_IDS = [ATTACK_DEFINITIONS[card_id]["ruleId"] for card_id in sorted(ATTACK_DEFINITIONS)]
ATTACK_QUESTION_BLOCKS = {
    question_id: [
        ATTACK_DEFINITIONS[card_id]["ruleId"]
        for card_id in sorted(ATTACK_DEFINITIONS)
        if question_id in ATTACK_DEFINITIONS[card_id]["questions"]
    ]
    for question_id in ("SEM-Q-020", "SEM-Q-021", "SEM-Q-022", "SEM-Q-023", "SEM-Q-024")
}


BADGE_COMPONENT_BBOXES = {
    394900: [[133, 773, 64, 59], [123, 865, 70, 55], [118, 942, 80, 70]],
    394901: [[133, 773, 64, 59], [123, 865, 70, 56], [118, 942, 80, 70]],
    394902: [[133, 773, 64, 59], [123, 865, 70, 55], [119, 942, 79, 70]],
    394903: [[133, 773, 64, 59], [123, 865, 71, 55], [118, 942, 80, 70]],
    394904: [[133, 773, 64, 59], [123, 865, 70, 55], [118, 942, 80, 70]],
    394905: [[133, 773, 65, 59], [123, 865, 71, 55], [118, 942, 80, 69]],
    394906: [[133, 553, 65, 59], [118, 638, 80, 71], [123, 878, 71, 55]],
    394907: [[133, 553, 65, 59], [118, 639, 80, 70], [123, 878, 70, 55]],
    394908: [[133, 553, 65, 59], [119, 638, 79, 71], [123, 878, 71, 55]],
    394909: [[133, 713, 64, 59], [122, 857, 71, 57], [119, 938, 79, 69]],
    394910: [[133, 713, 64, 59], [123, 857, 71, 57], [118, 938, 80, 69]],
    394911: [[133, 612, 64, 59], [123, 706, 71, 57], [118, 894, 80, 68]],
    394913: [[133, 781, 64, 59], [123, 872, 70, 57], [119, 950, 79, 70]],
    394914: [[133, 781, 64, 59], [123, 872, 70, 57], [118, 950, 80, 70]],
    394915: [[133, 781, 64, 59], [123, 872, 71, 57], [118, 950, 80, 70]],
    394916: [[133, 781, 64, 59], [123, 872, 71, 57], [119, 950, 79, 70]],
    394918: [[133, 612, 65, 59], [123, 706, 70, 56], [119, 894, 79, 69]],
    394919: [[133, 612, 65, 59], [123, 706, 71, 56], [118, 894, 80, 69]],
    399100: [[166, 720, 80, 74], [148, 1102, 99, 85], [153, 1221, 88, 70]],
}

BADGE_TYPE_METADATA = {
    "Adult": {"controlledTermId": "term.adult", "taxonId": "tax.entity.agent.intruder.adult", "templateOccurrenceId": "ATK-394906-B01"},
    "Drone": {"controlledTermId": "term.drone", "taxonId": "tax.entity.agent.intruder.drone", "templateOccurrenceId": "ATK-394906-B02"},
    "Queen": {"controlledTermId": "term.queen", "taxonId": "tax.entity.agent.intruder.queen", "templateOccurrenceId": "ATK-394906-B03"},
}

OFFICIAL_VISIBLE_COUNTERPARTS = [
    {
        "sourceOccurrenceId": "RB-P03-V01-ATTACK-BACK",
        "parentOccurrenceId": "RB-P03-V01",
        "kind": "shared-back",
        "locator": "unprinted PDF page 3 / Intruder Attack inventory row / rulebook_text lines 420–457 and 580–610",
        "visibleTitle": "ATTACK / PRIMEBLOOD",
        "visibleText": "ATTACK\nPRIMEBLOOD",
        "linkedCardIds": [],
        "variantDifference": "Official inventory visibly supplies the family back and a printed count of 20; it is not a rules face.",
    },
    {
        "sourceOccurrenceId": "RB-P03-V01-ATTACK-BITE",
        "parentOccurrenceId": "RB-P03-V01",
        "kind": "face-counterpart",
        "locator": "unprinted PDF page 3 / Intruder Attack inventory row / rulebook_text lines 449–457",
        "visibleTitle": "Bite",
        "visibleText": "If you are Heavily Injured, you die.\nOtherwise, gain 1 Serious Wound and 1 Contamination.",
        "linkedCardIds": [394900, 394901, 394902, 394903, 394904, 394905],
        "variantDifference": "One official-visible face is a counterpart for six separately selected TTS physical occurrences; it does not collapse their GUID/CardID identities.",
    },
    {
        "sourceOccurrenceId": "RB-P03-V01-ATTACK-DEADLY-CLAWS",
        "parentOccurrenceId": "RB-P03-V01",
        "kind": "face-counterpart",
        "locator": "unprinted PDF page 3 / Intruder Attack inventory row / rulebook_text lines 405–453",
        "visibleTitle": "Deadly Claws",
        "visibleText": "Adult and Queen: Lose 2 [Character Health]. Gain 1 Contamination.\nDrone: If you are Heavily Injured, you die. If you are Injured, gain 1 Serious Wound. Otherwise, gain 2 Serious Wounds.",
        "linkedCardIds": [394907],
        "variantDifference": "The official-visible current face matches the Lose-2 occurrence by exact title, amount, Contamination sentence, and panel role, but differs materially in badge applicability and branch body from the TTS scan.",
    },
    {
        "sourceOccurrenceId": "RB-P32-V01-ATTACK-INFECTING",
        "parentOccurrenceId": "RB-P32-V01",
        "kind": "face-anatomy-counterpart",
        "locator": "printed page 32 / RB-P32-V01 / rulebook_text lines 5368–5392",
        "visibleTitle": "INFECTING",
        "visibleText": "Adult and Drone: Lose 2 [Character Health].\nQueen: Gain 1 Contamination. If you are not infected with a Larva, place 1 Larva on your Character board.",
        "linkedCardIds": [394911],
        "variantDifference": "Official-primary row alignment assigns Adult+Drone to Lose 2 and Queen to the infection panel; the TTS scan's source-scoped badges assign Adult+Queen and Drone respectively.",
    },
]

OFFICIAL_RULEBOOK_TEXT_OCCURRENCES = [
    {"occurrenceId": "RB-ATTACK-FAMILY-COUNT", "section": "inventory", "locator": "unprinted PDF page 3 / RB-P03-V01 / rulebook_text line 539", "sourceText": "20 Intruder Attack cards."},
    {"occurrenceId": "RB-ATTACK-STANDARD-DRAW", "section": "standard-attack", "locator": "printed page 32 / lines 5398–5401", "sourceText": "Whenever a non-Larva Intruder Attacks a Character, draw a random Intruder Attack card."},
    {"occurrenceId": "RB-ATTACK-STANDARD-MATCH", "section": "applicability", "locator": "printed page 32 / lines 5402–5404 and RB-P32-V01", "sourceText": "Find the icon matching the attacking Intruder type and resolve its associated effect."},
    {"occurrenceId": "RB-ATTACK-STANDARD-DISCARD", "section": "lifecycle", "locator": "printed page 32 / lines 5402–5404", "sourceText": "After the associated effect resolves, discard the card."},
    {"occurrenceId": "RB-ATTACK-RESHUFFLE", "section": "lifecycle", "locator": "printed page 32 / lines 5405–5406", "sourceText": "The Intruder Attack deck is only reshuffled when instructed by the game."},
    {"occurrenceId": "RB-ATTACK-PREVENT", "section": "prevention", "locator": "printed page 32 / lines 5418–5423", "sourceText": "A prevented Attack is ignored entirely and no Intruder Attack card is drawn."},
    {"occurrenceId": "RB-ATTACK-TARGET", "section": "targeting", "locator": "printed page 32 / lines 5424–5430", "sourceText": "Entry Attacks target the source Character when possible after a player effect, otherwise the Character first in Turn order."},
    {"occurrenceId": "RB-ATTACK-HEALTH-WOUNDS", "section": "health-and-wounds", "locator": "printed page 18 / lines 3744–3823", "sourceText": "Health loss, random Serious Wound placement, Health-track displacement, Armor loss, and death follow the Character Health and Wound procedure."},
    {"occurrenceId": "RB-ATTACK-COMPONENT-LIMITS", "section": "finite-supply", "locator": "printed pages 3 and 17 / component inventory and lines 3538–3548", "sourceText": "The physical game has 27 Contamination and 27 Serious Wound cards; unavailable finite components do nothing unless a specific fallback is stated."},
]


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _parse_key(data: bytes, offset: int) -> tuple[str, int]:
    end = data.find(b"\x00", offset)
    if end < 0:
        raise AssertionError("unterminated TTS save key")
    return data[offset:end].decode("latin-1", "replace"), end + 1


def _parse_value(data: bytes, offset: int, content_end: int | None = None):
    if content_end is not None and offset >= content_end:
        return None, offset
    marker = data[offset]
    if marker == 0:
        offset += 1
        while content_end is not None and offset < content_end and data[offset] == 0:
            offset += 1
        if content_end is not None and offset >= content_end:
            return None, offset
        marker = data[offset]
        offset += 1
    else:
        offset += 1
    key, offset = _parse_key(data, offset)
    if marker == 0x02:
        length = struct.unpack_from("<I", data, offset)[0]
        offset += 4
        value = data[offset:offset + length].rstrip(b"\x00").decode("latin-1", "replace")
        offset += length
    elif marker == 0x01:
        value = struct.unpack_from("<d", data, offset)[0]
        offset += 8
    elif marker == 0x08:
        value = bool(data[offset])
        offset += 1
    elif marker == 0x07:
        value = data[offset]
        offset += 1
    elif marker == 0x10:
        value = struct.unpack_from("<i", data, offset)[0]
        offset += 4
    elif marker == 0x12:
        value = struct.unpack_from("<Q", data, offset)[0]
        offset += 8
    elif marker in (0x03, 0x04):
        length = struct.unpack_from("<I", data, offset)[0]
        offset += 4
        end = offset + length - 4
        fields: dict = {}
        while offset < end:
            parsed, offset = _parse_value(data, offset, end)
            if parsed is None:
                break
            child_key, child_value = parsed
            if child_key in fields:
                if not isinstance(fields[child_key], list):
                    fields[child_key] = [fields[child_key]]
                fields[child_key].append(child_value)
            else:
                fields[child_key] = child_value
        value = fields
    else:
        raise AssertionError(f"unknown TTS save marker {marker:#x}")
    return (key, value), offset


def _find_guid(node, guid: str):
    if isinstance(node, dict):
        if node.get("GUID") == guid:
            return node
        for value in node.values():
            found = _find_guid(value, guid)
            if found is not None:
                return found
    elif isinstance(node, list):
        for value in node:
            found = _find_guid(value, guid)
            if found is not None:
                return found
    return None


def _raw_attack_deck(repo: Path) -> tuple[dict, str]:
    path = repo / RAW_SAVE_PATH
    data = path.read_bytes()
    root: dict = {}
    offset = 4
    while offset < len(data):
        parsed, offset = _parse_value(data, offset, len(data))
        if parsed is not None:
            root[parsed[0]] = parsed[1]
    deck = _find_guid(root.get("ObjectStates"), BASE_ATTACK_DECK_GUID)
    if not isinstance(deck, dict):
        raise AssertionError("base Attack root DeckCustom missing from raw TTS save")
    return deck, _sha(path)


def _parse_js_literal(body: str, field: str):
    match = re.search(rf"^    {field}: ", body, re.M)
    if not match:
        raise AssertionError(f"missing Attack BGA field {field}")
    start = match.end()
    opening = body[start]
    if opening == "'":
        escaped = False
        for index in range(start + 1, len(body)):
            char = body[index]
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == "'":
                return ast.literal_eval(body[start:index + 1])
    elif opening == "[":
        depth = 0
        in_string = False
        escaped = False
        for index in range(start, len(body)):
            char = body[index]
            if in_string:
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == "'":
                    in_string = False
                continue
            if char == "'":
                in_string = True
            elif char == "[":
                depth += 1
            elif char == "]":
                depth -= 1
                if depth == 0:
                    return ast.literal_eval(body[start:index + 1])
    raise AssertionError(f"unterminated Attack BGA field {field}")


def _parse_bga_attacks(path: Path) -> dict[str, dict]:
    text = path.read_text(encoding="utf-8")
    match = re.search(r"const INTRUDER_ATTACKS_DATA = \{\n(.*?)\n\};", text, re.S)
    if not match:
        raise AssertionError("INTRUDER_ATTACKS_DATA block not found")
    records = {}
    for row in re.finditer(r"^  (IntruderAttack_[A-Za-z0-9]+): \{\n(.*?)^  \},$", match.group(1), re.M | re.S):
        key, body = row.groups()
        records[key] = {
            "name": _parse_js_literal(body, "name"),
            "effectDesc": _parse_js_literal(body, "effectDesc"),
            "asset": _parse_js_literal(body, "asset"),
            "sourceBlockText": row.group(0),
        }
    expected = {definition["bgaKey"] for definition in ATTACK_DEFINITIONS.values()}
    if set(records) != expected or len(records) != 15:
        raise AssertionError("licensed Attack table identity set changed")
    return records


def _selected_run(entry: dict | None) -> dict:
    runs = (entry or {}).get("runs") or []
    return runs[-1] if runs else {}


def _title_and_body(repo: Path, definition: dict, corpus_row: dict, selected_entry: dict | None) -> tuple[str, str, str]:
    expected_body = "\n\n".join(definition["panelTexts"])
    if definition["title"] == "MISS":
        result_path = (corpus_row.get("evidence") or {}).get("resultPath")
        if not isinstance(result_path, str) or not result_path:
            raise AssertionError("MISS title/body evidence path missing")
        evidence = json.loads((repo / result_path).read_text(encoding="utf-8"))
        title = (evidence.get("parsed") or {}).get("title")
        body = (evidence.get("parsed") or {}).get("body")
        title_evidence = result_path
    else:
        run = _selected_run(selected_entry)
        visible = run.get("visibleText") or {}
        title = visible.get("title")
        if definition["ttsGuid"] == "aa3f4a":
            body = "\n\n".join([visible.get("upperPanel", {}).get("instruction", ""), visible.get("lowerPanel", {}).get("instruction", "")])
        else:
            body = visible.get("body")
        title_evidence = "assets/tts-mod/extract/selected-card-text-evidence.json"
    if title != definition["title"] or body != expected_body:
        raise AssertionError(f"Attack selected title/body drift: {definition['ruleId']}")
    if not isinstance(title, str) or not isinstance(body, str) or not isinstance(title_evidence, str):
        raise AssertionError(f"Attack title/body evidence types invalid: {definition['ruleId']}")
    return title, body, title_evidence


def _panels(title: str, body: str, panel_texts: list[str]) -> list[dict]:
    rows = [
        {"panelId": "P1", "readingOrder": 1, "role": "title", "operative": False, "exactText": title, "bodyStart": None, "bodyEnd": None},
        {"panelId": "P2", "readingOrder": 2, "role": "artwork", "operative": False, "exactText": "", "bodyStart": None, "bodyEnd": None},
    ]
    cursor = 0
    for index, text in enumerate(panel_texts, 3):
        start = body.find(text, cursor)
        if start < 0:
            raise AssertionError(f"Attack panel span missing: {title} P{index}")
        end = start + len(text)
        rows.append({"panelId": f"P{index}", "readingOrder": index, "role": "applicability-and-effect-panel", "operative": True, "exactText": text, "bodyStart": start, "bodyEnd": end})
        cursor = end
    return rows


def _sentences(body: str, definitions: list[dict]) -> list[dict]:
    rows = []
    cursor = 0
    for sequence, sentence in enumerate(definitions, 1):
        start = body.find(sentence["exactText"], cursor)
        if start < 0:
            raise AssertionError(f"Attack sentence span missing: {sentence['sentenceId']}")
        end = start + len(sentence["exactText"])
        rows.append({**sentence, "sequence": sequence, "start": start, "end": end})
        cursor = end
    return rows


def _literal_badges(corpus_row: dict) -> list[str]:
    printed = corpus_row.get("printedData") or {}
    literal_body = printed.get("body") or ""
    rows = [match.group(0) for match in re.finditer(r"\[ICON: [^\]]+\]", literal_body)]
    if not rows:
        rows = [match.group(0) for match in re.finditer(r"\[ICON: [^\]]+\]", printed.get("visibleText") or "")]
    return rows


def _inline_icons(card_id: int, body: str) -> list[dict]:
    rows = []
    token_pattern = re.compile(r"\[(characterHealth|intruder|LOCAL_ICON:INLINE-1)\]")
    health_scores = {394906: 0.955931, 394919: 0.811163}
    for sequence, match in enumerate(token_pattern.finditer(body), 1):
        source_token = match.group(1)
        semantic_reference = "icon.characterHealth" if source_token in {"characterHealth", "LOCAL_ICON:INLINE-1"} else "icon.intruder"
        row = {
            "occurrenceId": f"ATK-{card_id}-I{sequence:02d}",
            "sequence": sequence,
            "sourceToken": source_token,
            "semanticReferenceId": semantic_reference,
            "start": match.start(),
            "end": match.end(),
            "location": body[max(0, match.start() - 24):min(len(body), match.end() + 24)].replace("\n", " "),
            "mappingScope": f"exact Attack source occurrence TTS-ATTACK-{card_id}-FACE only",
        }
        if source_token == "LOCAL_ICON:INLINE-1":
            row["literalResolutionBoundary"] = "Selected W08 evidence retained this occurrence as unlabeled local morphology. A separate exact-scale template match to the independently page-40-matched card-11 Character Health occurrence scored 0.955931; the literal no-match row remains unchanged."
            row["templateMatchScore"] = health_scores[card_id]
        elif card_id == 394919 and source_token == "characterHealth":
            row["literalResolutionBoundary"] = "Selected evidence contains both a Character Health match and a contradictory no-match/location row. The body glyph remains independently matched to the page-40-backed card-11 template; neither selected row is deleted."
            row["templateMatchScore"] = health_scores[card_id]
        else:
            row["literalResolutionBoundary"] = "Use only the selected occurrence-specific authoritative comparison; no color/position-wide alias is inferred."
        rows.append(row)
    return rows


def build_attack_source_index(repo: Path) -> dict:
    corpus = json.loads((repo / "assets/tts-mod/extract/card-text-corpus.json").read_text(encoding="utf-8"))
    corpus_by_path = {row["sourcePath"]: row for row in corpus["records"]}
    selected = json.loads((repo / "assets/tts-mod/extract/selected-card-text-evidence.json").read_text(encoding="utf-8"))
    selected_by_path = {row["sourcePath"]: row for row in selected["entries"]}
    progress = json.loads((repo / "assets/tts-mod/extract/vision-progress.json").read_text(encoding="utf-8"))
    progress_by_path = {row["sourcePath"]: row for row in progress["records"]}
    provenance = json.loads((repo / "assets/tts-mod/extract/card-provenance-inventory.json").read_text(encoding="utf-8"))
    objects = json.loads((repo / "assets/tts-mod/extract/v2/objects.json").read_text(encoding="utf-8"))
    roles = json.loads((repo / "assets/tts-mod/extract/v2/lua_roles.json").read_text(encoding="utf-8"))
    secondary = json.loads((repo / "docs/rules/source-extraction/secondary-evidence-index.json").read_text(encoding="utf-8"))
    visuals = json.loads((repo / "docs/rules/source-extraction/rulebook-visual-obligations.json").read_text(encoding="utf-8"))
    faq = json.loads((repo / "docs/rules/source-extraction/faq-v1.2-source-extraction.json").read_text(encoding="utf-8"))
    backlog = json.loads((repo / "docs/rules/semantics/backlog.json").read_text(encoding="utf-8"))
    backlog_by_id = {row["semanticUnitId"]: row for row in backlog["units"]}
    bga = _parse_bga_attacks(repo / BGA_ATTACK_PATH)

    role = next(row for row in roles if row.get("role") == "attacksDeck" and row.get("guid") == BASE_ATTACK_DECK_GUID)
    if role.get("type") != "DeckCustom" or role.get("n_urls") != 3 or role.get("deck_nums") != ["3949", "3991"]:
        raise AssertionError("base Attack root Lua role changed")
    excluded_roles = [row for row in roles if row.get("role") == "attacksDeck" and row.get("guid") != BASE_ATTACK_DECK_GUID]
    if {(row["guid"], tuple(row["deck_nums"])) for row in excluded_roles} != {
        ("61a87c", ("4582", "4583", "4584", "4585", "4587", "4658", "4663", "4665", "4667", "4668", "4669", "5043", "5044", "5045", "5046", "5047", "5048", "5049")),
        ("3a25fc", ("5480", "5481", "5482", "5484", "5485", "5486", "5487", "5492", "5493", "5494", "5495", "5496", "5497", "5498", "5499", "5574", "5575", "5576", "5577", "5578")),
        ("9aefbc", ("5686", "5687", "5688", "5689", "5690", "5691", "5692", "5693")),
    }:
        raise AssertionError("Attack expansion-role boundary changed")

    raw_deck, raw_save_sha = _raw_attack_deck(repo)
    custom_deck = raw_deck.get("CustomDeck") or {}
    expected_custom = {
        "3949": {"FaceURL": "https://steamusercontent-a.akamaihd.net/ugc/2468613527880234536/A0DC2BC12F4C9ECFE5AF1398ED52FD8746072DD8/", "BackURL": "https://steamusercontent-a.akamaihd.net/ugc/11924678148411699/14FCBEEBC01824DE1591E0218355C01ECC48C923/", "NumWidth": 5, "NumHeight": 4, "BackIsHidden": True, "UniqueBack": False, "Type": 0},
        "3991": {"FaceURL": "https://steamusercontent-a.akamaihd.net/ugc/11925215517129770/8DF8175468EFA277EC2BD907070B7070D7810F54/", "BackURL": "https://steamusercontent-a.akamaihd.net/ugc/11924678148411699/14FCBEEBC01824DE1591E0218355C01ECC48C923/", "NumWidth": 1, "NumHeight": 1, "BackIsHidden": True, "UniqueBack": False, "Type": 0},
    }
    deck_ids = [int(value) for value in (raw_deck.get("DeckIDs") or {}).values()]
    expected_deck_ids = [394904, 394900, 394903, 394901, 394902, 394905, 399100, 394906, 394907, 394908, 394909, 394910, 394911, 394914, 394915, 394913, 394916, 394912, 394919, 394918]
    if custom_deck != expected_custom or deck_ids != expected_deck_ids:
        raise AssertionError("base Attack raw CustomDeck/DeckIDs changed")
    contained = list((raw_deck.get("ContainedObjects") or {}).values())
    raw_child_by_card = {int(row["CardID"]): row for row in contained}
    if set(raw_child_by_card) != set(ATTACK_DEFINITIONS) or len(contained) != 20:
        raise AssertionError("base Attack raw child occurrence count changed")

    sheet_path = repo / ATTACK_SHEET_PATH
    sheet_sha = _sha(sheet_path)
    with Image.open(sheet_path) as image:
        sheet_dimensions = list(image.size)
    if sheet_dimensions != [4135, 4444]:
        raise AssertionError("Attack generated source-sheet dimensions changed")

    provenance_by_file = {row["file"]: row for row in provenance}
    sheet_provenance = provenance_by_file["cards/game/attack-151.jpg"]
    back_provenance = provenance_by_file["cards/game/attack-020.png"]
    direct_provenance = provenance_by_file["cards/game/attack-022.png"]
    if sheet_provenance.get("refs") != 20 or back_provenance.get("refs") != 21 or direct_provenance.get("refs") != 2:
        raise AssertionError("Attack FaceURL/BackURL reference counts changed")

    table = next(row for row in secondary["licensedDigital"]["structuredIndex"]["tables"] if row["name"] == "INTRUDER_ATTACKS_DATA")
    if table.get("count") != 15 or set(table.get("keys") or []) != set(bga):
        raise AssertionError("licensed Attack evidence-index closure changed")

    visual_by_id = {unit["occurrenceId"]: unit for page in visuals["pages"] for unit in page.get("visualUnits", [])}
    if any(occurrence_id not in visual_by_id for occurrence_id in ("RB-P03-V01", "RB-P32-V01")):
        raise AssertionError("Attack official visual occurrence missing")
    faq_by_id = {unit["sourceUnitId"]: unit for page in faq["pages"] for unit in page.get("units", [])}
    faq_ids = ["FQ-P02-U11", "FQ-P02-U16", "FQ-P02-U19"]
    if any(faq_by_id[qid]["applicability"] != "base-game" for qid in faq_ids):
        raise AssertionError("Attack FAQ applicability boundary changed")

    counterpart_by_id = {row["sourceOccurrenceId"]: row for row in OFFICIAL_VISIBLE_COUNTERPARTS}
    rows = []
    for card_id in sorted(ATTACK_DEFINITIONS):
        definition = ATTACK_DEFINITIONS[card_id]
        raw_child = raw_child_by_card[card_id]
        if raw_child.get("GUID") != definition["ttsGuid"]:
            raise AssertionError(f"Attack full CardID/GUID crosswalk drift: {card_id}")
        cell = definition["generatedCellIndex"]
        if cell is None:
            source_path = "assets/tts-mod/extract/v2-dl/tree/cards/game/attack-022.png"
            source_role = "direct-face"
            custom_deck_id = "3991"
            source_url = expected_custom[custom_deck_id]["FaceURL"]
            selector_status = "exact-direct-FaceURL-card-reference"
            generated = None
        else:
            source_path = f"assets/tts-mod/extract/v2-dl/tree/cards/game/attack-151_cards/card-{cell:02d}.png"
            source_role = "generated-cell-face"
            custom_deck_id = "3949"
            source_url = expected_custom[custom_deck_id]["FaceURL"]
            selector_status = "exact-full-CardID/GUID-to-reviewed-generated-cell-crosswalk"
            progress_row = progress_by_path.get(source_path) or {}
            generated_from = progress_row.get("generatedFrom") or {}
            if generated_from != {"sourceSheetPath": ATTACK_SHEET_PATH, "cellIndex": cell}:
                raise AssertionError(f"Attack generated-cell provenance drift: {card_id}")
            generated = {
                "sourceSheetId": ATTACK_SHEET_SOURCE_ID,
                "sourceSheetPath": ATTACK_SHEET_PATH,
                "sourceSheetSha256": sheet_sha,
                "grid": {"columns": 5, "rows": 4, "cellWidth": 827, "cellHeight": 1111},
                "cellIndex": cell,
                "row": cell // 5,
                "column": cell % 5,
                "cellPath": source_path,
            }
        source_sha = _sha(repo / source_path)
        corpus_row = corpus_by_path.get(source_path) or {}
        if source_sha != corpus_row.get("sourceSha256") or not corpus_row.get("rulesTextPresent") or corpus_row.get("extractionState") not in {"verified-canonical", "draft-full"}:
            raise AssertionError(f"Attack corpus/hash readiness drift: {card_id}")
        selected_entry = selected_by_path.get(source_path)
        title, body, title_evidence = _title_and_body(repo, definition, corpus_row, selected_entry)
        panels = _panels(title, body, definition["panelTexts"])
        sentences = _sentences(body, definition["sentences"])
        literal_badges = _literal_badges(corpus_row)
        if len(literal_badges) != len(definition["badgePanels"]):
            raise AssertionError(f"Attack literal badge count drift: {card_id}")
        badge_rows = []
        for index, (badge, bbox, literal) in enumerate(zip(definition["badgePanels"], BADGE_COMPONENT_BBOXES.get(card_id, []), literal_badges), 1):
            type_meta = BADGE_TYPE_METADATA[badge["intruderType"]]
            badge_rows.append({
                "occurrenceId": f"ATK-{card_id}-B{index:02d}",
                "sequence": index,
                "panelId": badge["panelId"],
                "literalSourceToken": literal,
                "literalCyanComponentBbox": bbox,
                "sourceScopedResolution": {
                    "intruderType": badge["intruderType"],
                    **type_meta,
                    "authorityEvidence": "official rulebook printed page 32 / RB-P32-V01 labels the three reference morphologies Adult, Drone, and Queen",
                    "method": "source-scoped cyan-mask normalized-IoU projection from the three independently labeled card-394906 templates",
                    "familyMinimumWinningIou": 0.8241,
                    "familyMinimumWinningMargin": 0.3549,
                    "page40GlossaryAliasCreated": False,
                },
                "mappingScope": f"exact Attack source occurrence TTS-ATTACK-{card_id}-FACE only",
            })
        inline_icons = _inline_icons(card_id, body)
        backlog_id = "CARD:" + source_sha[:16]
        backlog_row = backlog_by_id.get(backlog_id)
        if not backlog_row or backlog_row.get("sourcePath") != source_path or backlog_row.get("sourceLocator") != source_sha:
            raise AssertionError(f"Attack backlog source tuple drift: {card_id}")
        bga_row = bga[definition["bgaKey"]]
        selected_run = _selected_run(selected_entry)
        selector = {
            "key": "FaceURL",
            "objectType": raw_child.get("Name"),
            "fullCardId": card_id,
            "guid": definition["ttsGuid"],
            "parentDeckGuid": BASE_ATTACK_DECK_GUID,
            "customDeckId": custom_deck_id,
            "url": source_url,
            "backUrl": expected_custom[custom_deck_id]["BackURL"],
            "sideRole": "operative-face",
            "sourceRole": source_role,
            "selectorStatus": selector_status,
            "generatedCell": generated,
            "selectorGap": None,
            "cardIdModuloJoinUsed": False,
        }
        rows.append({
            "attackOccurrenceId": f"TTS-ATTACK-{card_id}-FACE",
            "ttsRole": "attacksDeck",
            "ttsDeckGuid": BASE_ATTACK_DECK_GUID,
            "ttsDeckType": "DeckCustom",
            "ttsDeckSequence": definition["deckSequence"],
            "ttsCardGuid": definition["ttsGuid"],
            "ttsCardId": card_id,
            "sourceSelector": selector,
            "sourceId": definition["sourceId"],
            "sourcePath": source_path,
            "sourceSha256": source_sha,
            "sourceAuthority": "source-bound-component-scan",
            "sourceVersion": f"TTS base Intruder Attack occurrence / root deck {BASE_ATTACK_DECK_GUID} / full CardID {card_id}",
            "corpusEvidencePath": "assets/tts-mod/extract/card-text-corpus.json",
            "selectedEvidencePath": title_evidence,
            "provenanceEvidencePath": "assets/tts-mod/extract/card-provenance-inventory.json",
            "literalCorpusBody": (corpus_row.get("printedData") or {}).get("body") or "",
            "printedTitle": title,
            "printedBody": body,
            "extractionState": corpus_row["extractionState"],
            "rulesInformationReadiness": corpus_row["rulesInformationReadiness"],
            "panels": panels,
            "sentences": sentences,
            "applicabilityBadgeOccurrences": badge_rows,
            "inlineIconOccurrences": inline_icons,
            "selectedEvidenceComparisons": {
                "selectedRunIdentity": (selected_entry or {}).get("selectedRunIdentity"),
                "verifiedIconOccurrences": selected_run.get("verifiedIconOccurrences") or [],
                "unresolvedIconOccurrences": selected_run.get("unresolvedIconOccurrences") or [],
                "allMaterialIconsAuthoritativelyMatched": selected_run.get("allMaterialIconsAuthoritativelyMatched"),
                "boundary": "Literal selected no-match/match rows are retained verbatim; source-scoped semantic projections do not rewrite them.",
            },
            "semanticRuleId": definition["ruleId"],
            "backlogUnitId": backlog_id,
            "bgaOccurrence": {
                "sourceId": BGA_ATTACK_SOURCE_ID,
                "sourcePath": BGA_ATTACK_PATH,
                "sourceSha256": _sha(repo / BGA_ATTACK_PATH),
                "sourceVersion": "licensed BGA immutable build 260622-1220 / INTRUDER_ATTACKS_DATA",
                "table": "INTRUDER_ATTACKS_DATA",
                "key": definition["bgaKey"],
                **bga_row,
                "variantDifference": definition["variantDifference"],
            },
            "officialCounterpartRefs": definition["officialCounterpartRefs"],
            "joinEvidence": {
                "identityJoin": "explicit full occurrence crosswalk",
                "titleOnlyJoin": False,
                "sourceCellOnlyJoin": False,
                "folderOnlyJoin": False,
                "cardIdModuloJoin": False,
                "basis": [
                    "root base attacksDeck Lua role and exact DeckCustom GUID",
                    "raw CustomDeck ID, full CardID, child GUID, FaceURL, BackURL, and parent deck tuple",
                    "reviewed generated source sheet/hash/grid/cell or exact direct-face selector",
                    "closed-corpus cell bytes and live SHA-256",
                    "ordered panels, sentences, source-scoped applicability badges, and inline icon occurrences",
                    "explicit licensed INTRUDER_ATTACKS_DATA key plus exact nested effectDesc fields",
                ],
            },
        })

    unused_cell_path = "assets/tts-mod/extract/v2-dl/tree/cards/game/attack-151_cards/card-17.png"
    unused_corpus = corpus_by_path[unused_cell_path]
    if _sha(repo / unused_cell_path) != unused_corpus["sourceSha256"] or any(definition["generatedCellIndex"] == 17 for definition in ATTACK_DEFINITIONS.values()) or 394917 in raw_child_by_card:
        raise AssertionError("Attack unused generated-cell selector gap changed")

    back_sha = _sha(repo / ATTACK_BACK_PATH)
    back_corpus = corpus_by_path[ATTACK_BACK_PATH]
    if back_sha != back_corpus.get("sourceSha256") or back_corpus.get("rulesTextPresent") or (back_corpus.get("printedData") or {}).get("title") != "ATTACK\nPRIMEBLOOD":
        raise AssertionError("Attack shared-back corpus boundary changed")

    official_projection = []
    for counterpart in OFFICIAL_VISIBLE_COUNTERPARTS:
        parent = visual_by_id[counterpart["parentOccurrenceId"]]
        official_projection.append({
            **counterpart,
            "sourceId": "SRC-RULEBOOK",
            "sourcePath": "docs/rulebooks/Nemesis_RT_Rulebook_official.pdf",
            "sourceSha256": _sha(repo / "docs/rulebooks/Nemesis_RT_Rulebook_official.pdf"),
            "parentVisualType": parent["type"],
            "parentBbox160Dpi": parent["bbox"],
        })

    face_unit_ids = [row["backlogUnitId"] for row in rows]
    linked_backlog_ids = [
        *face_unit_ids,
        "RULE:INT-004",
        "RULE:INT-006",
        "RULE:INT-008",
        "FAQ:FQ-P02-U11",
        "FAQ:FQ-P02-U16",
        "FAQ:FQ-P02-U19",
        "VIS:RB-P03-V01",
        "VIS:RB-P32-V01",
    ]
    if any(unit_id not in backlog_by_id for unit_id in linked_backlog_ids):
        raise AssertionError("Attack source-obligation backlog closure failed")

    title_counts = Counter(row["printedTitle"] for row in rows)
    bga_link_counts = Counter(row["bgaOccurrence"]["key"] for row in rows)
    selected_no_match = sum(len((row["selectedEvidenceComparisons"] or {}).get("unresolvedIconOccurrences") or []) for row in rows)
    selected_match = sum(len((row["selectedEvidenceComparisons"] or {}).get("verifiedIconOccurrences") or []) for row in rows)
    official_face_counterparts = [row for row in official_projection if row["kind"] != "shared-back"]
    return {
        "schemaVersion": 1,
        "recordType": "semantic-attack-source-index",
        "scope": "entire mechanically selected base Intruder Attack family; physical occurrences, repeated titles, source variants, and exclusions remain independent",
        "derivationPolicy": "Derive the base family only from the first/base attacksDeck Lua role and raw root DeckCustom GUID, exact full CardID/GUID/CustomDeck/FaceURL/BackURL/DeckIDs tuples, then close generated cells against source sheet/hash/grid/cell, direct faces, corpus bytes, panels, sentences, badges, official counterparts, licensed records, and backlog. Never join by title, cell alone, folder, or CardID modulo.",
        "counts": {
            "attackOccurrences": len(rows),
            "uniquePrintedTitles": len(title_counts),
            "generatedFaceOccurrences": sum(row["sourceSelector"]["sourceRole"] == "generated-cell-face" for row in rows),
            "directFaceOccurrences": sum(row["sourceSelector"]["sourceRole"] == "direct-face" for row in rows),
            "generatedSourceSheetCells": 20,
            "selectedGeneratedCells": 19,
            "excludedSelectorGaps": 1,
            "sharedBackOccurrences": 1,
            "sharedBackSelectorReferences": back_provenance["refs"],
            "sourceSheets": 1,
            "canonicalCorpusFaces": sum(row["extractionState"] == "verified-canonical" for row in rows),
            "sourceBoundDraftFaces": sum(row["extractionState"] == "draft-full" for row in rows),
            "physicalPanels": sum(len(row["panels"]) for row in rows),
            "operativePanels": sum(sum(panel["operative"] for panel in row["panels"]) for row in rows),
            "printedSentences": sum(len(row["sentences"]) for row in rows),
            "applicabilityBadgeOccurrences": sum(len(row["applicabilityBadgeOccurrences"]) for row in rows),
            "inlineIconOccurrences": sum(len(row["inlineIconOccurrences"]) for row in rows),
            "functionalSymbolOccurrences": sum(len(row["applicabilityBadgeOccurrences"]) + len(row["inlineIconOccurrences"]) for row in rows),
            "selectedEvidenceNoMatchOccurrences": selected_no_match,
            "selectedEvidenceMatchedOccurrences": selected_match,
            "licensedStructuredVariants": len(bga),
            "licensedFaceLinks": sum(bga_link_counts.values()),
            "officialVisibleFaceCounterparts": len(official_face_counterparts),
            "officialVisibleBackCounterparts": 1,
            "officialFaceLinks": sum(len(row["linkedCardIds"]) for row in official_face_counterparts),
            "officialRulebookTextOccurrences": len(OFFICIAL_RULEBOOK_TEXT_OCCURRENCES),
            "officialRulebookVisualObligations": 2,
            "faqOccurrences": len(faq_ids),
            "excludedExpansionAttackDecks": len(excluded_roles),
            "excludedUnusedGeneratedFaces": 1,
            "backlogTuples": len(rows),
            "backlogObligationsLinked": len(linked_backlog_ids),
        },
        "titleMultiplicity": dict(sorted(title_counts.items())),
        "familyCountEvidence": {
            "officialRulebook": {"sourcePath": "docs/rulebooks/Nemesis_RT_Rulebook_official.pdf", "locator": "unprinted PDF page 3 / RB-P03-V01 / rulebook_text line 539", "printedPhysicalCount": 20},
            "rawTtsDeck": {"sourcePath": RAW_SAVE_PATH, "sourceSha256": raw_save_sha, "rolePath": "assets/tts-mod/extract/v2/lua_roles.json", "role": "attacksDeck", "deckGuid": BASE_ATTACK_DECK_GUID, "customDeck": expected_custom, "deckIdsInSavedOrder": deck_ids, "faceCount": len(rows)},
            "closedCorpus": {"sourcePath": "assets/tts-mod/extract/card-text-corpus.json", "faceCount": len(rows), "sourcePaths": [row["sourcePath"] for row in rows]},
            "licensedDigital": {"sourcePath": BGA_ATTACK_PATH, "indexPath": "docs/rules/source-extraction/secondary-evidence-index.json", "table": "INTRUDER_ATTACKS_DATA", "structuredVariantCount": len(bga), "keys": sorted(bga), "physicalLinkMultiplicity": dict(sorted(bga_link_counts.items())), "linkedPhysicalCount": sum(bga_link_counts.values())},
            "backlog": {"sourcePath": "docs/rules/semantics/backlog.json", "faceTupleCount": len(rows), "faceUnitIds": face_unit_ids, "linkedUnitIds": linked_backlog_ids},
        },
        "sourceSheet": {
            "sourceId": ATTACK_SHEET_SOURCE_ID,
            "occurrenceId": "TTS-ATTACK-GENERATED-SHEET",
            "sourcePath": ATTACK_SHEET_PATH,
            "sourceSha256": sheet_sha,
            "sourceAuthority": "source-bound-component-scan",
            "sourceVersion": f"TTS base Attack generated 5x4 source sheet / CustomDeck 3949 / root deck {BASE_ATTACK_DECK_GUID}",
            "dimensions": sheet_dimensions,
            "grid": {"columns": 5, "rows": 4, "cellWidth": 827, "cellHeight": 1111},
            "sourceSelector": {"key": "FaceURL", "objectType": "DeckCustom", "guid": BASE_ATTACK_DECK_GUID, "customDeckId": "3949", "url": expected_custom["3949"]["FaceURL"], "referenceCount": sheet_provenance["refs"], "parentSheetNotRulesFace": True},
            "generatedCellPaths": [f"assets/tts-mod/extract/v2-dl/tree/cards/game/attack-151_cards/card-{index:02d}.png" for index in range(20)],
        },
        "sharedBack": {
            "sourceId": ATTACK_BACK_SOURCE_ID,
            "occurrenceId": "TTS-ATTACK-SHARED-BACK",
            "sourcePath": ATTACK_BACK_PATH,
            "sourceSha256": back_sha,
            "sourceAuthority": "source-bound-component-scan",
            "sourceVersion": f"TTS shared base Attack back / root deck {BASE_ATTACK_DECK_GUID}",
            "sourceSelector": {"key": "BackURL", "objectType": "DeckCustom", "guid": BASE_ATTACK_DECK_GUID, "url": expected_custom["3949"]["BackURL"], "sideRole": "shared-non-operative-back", "rootDeckSelectorCount": 1, "baseCardSelectorCount": 20, "referenceCount": back_provenance["refs"]},
            "printedTitle": "ATTACK\nPRIMEBLOOD",
            "rulesTextPresent": False,
            "separateRulesFace": False,
        },
        "badgeResolutionMethod": {
            "mappingScope": "only the 57 exact badge occurrences enumerated below",
            "authorityReference": "official rulebook printed page 32 / RB-P32-V01",
            "referenceTemplateOccurrenceIds": ["ATK-394906-B01", "ATK-394906-B02", "ATK-394906-B03"],
            "algorithm": "cyan HSV mask, connected source component, aspect-preserving normalization, best shifted intersection-over-union",
            "familyMinimumWinningIou": 0.8241,
            "familyMinimumWinningMargin": 0.3549,
            "literalNoMatchPreservation": "All selected-evidence no-match rows remain embedded per face; semantic projection creates no page-40 or color/position-wide alias.",
        },
        "officialRulebookTextOccurrences": OFFICIAL_RULEBOOK_TEXT_OCCURRENCES,
        "officialVisibleCounterparts": official_projection,
        "faqOccurrences": [{"sourceUnitId": qid, "section": faq_by_id[qid]["section"], "applicability": faq_by_id[qid]["applicability"], "printedText": faq_by_id[qid]["printedText"]} for qid in faq_ids],
        "excludedContent": {
            "unusedGeneratedCell": {
                "sourcePath": unused_cell_path,
                "sourceSha256": unused_corpus["sourceSha256"],
                "cellIndex": 17,
                "printedTitle": (unused_corpus.get("printedData") or {}).get("title"),
                "selectorGap": "No root DeckID, contained child CardID, or GUID selects source-sheet cell 17; official physical count remains 20 and BGA has no Summoning key.",
                "classification": "unused/prototype-era source-sheet face; not a base Attack deck occurrence",
                "backlogStatus": (backlog_by_id.get("CARD:" + unused_corpus["sourceSha256"][:16]) or {}).get("status"),
            },
            "expansionAttackDecks": [{"role": row["role"], "guid": row["guid"], "type": row["type"], "deckNums": row["deck_nums"], "scope": "expansion; excluded from base conclusions"} for row in excluded_roles],
            "parentSheetBoundary": "The 5x4 parent sheet is provenance, not a twentieth-plus rules face; only 19 explicitly selected generated cells enter the base deck.",
            "sharedBackBoundary": "The shared BackURL is one non-operative side referenced by the root and all 20 selected cards; reference count does not create extra faces.",
            "duplicateReferenceBoundary": "Root-deck, child-card, corpus, selected-evidence, official-counterpart, and licensed references are evidence links, not additional physical Attack occurrences.",
        },
        "faces": rows,
    }


def attack_source_registry_rows(attack_source_index: dict) -> list[dict]:
    rows = []
    for face in attack_source_index["faces"]:
        rows.append({"sourceId": face["sourceId"], "authority": face["sourceAuthority"], "version": face["sourceVersion"], "path": face["sourcePath"], "sha256": face["sourceSha256"], "occurrenceId": face["attackOccurrenceId"], "evidenceIndexPath": face["corpusEvidencePath"], "evidenceRecord": face["sourceSha256"], "provenanceIndexPath": face["provenanceEvidencePath"]})
    sheet = attack_source_index["sourceSheet"]
    rows.append({"sourceId": sheet["sourceId"], "authority": sheet["sourceAuthority"], "version": sheet["sourceVersion"], "path": sheet["sourcePath"], "sha256": sheet["sourceSha256"], "occurrenceId": sheet["occurrenceId"], "evidenceIndexPath": "assets/tts-mod/extract/vision-progress.json", "evidenceRecord": sheet["sourceSha256"], "provenanceIndexPath": "assets/tts-mod/extract/card-provenance-inventory.json"})
    back = attack_source_index["sharedBack"]
    rows.append({"sourceId": back["sourceId"], "authority": back["sourceAuthority"], "version": back["sourceVersion"], "path": back["sourcePath"], "sha256": back["sourceSha256"], "occurrenceId": back["occurrenceId"], "evidenceIndexPath": "assets/tts-mod/extract/card-text-corpus.json", "evidenceRecord": back["sourceSha256"], "provenanceIndexPath": "assets/tts-mod/extract/card-provenance-inventory.json"})
    rows.append({"sourceId": BGA_ATTACK_SOURCE_ID, "authority": "licensed-digital-secondary", "version": "licensed BGA immutable build 260622-1220 / INTRUDER_ATTACKS_DATA", "path": BGA_ATTACK_PATH, "sha256": attack_source_index["faces"][0]["bgaOccurrence"]["sourceSha256"], "occurrenceId": "INTRUDER_ATTACKS_DATA", "evidenceIndexPath": "docs/rules/source-extraction/secondary-evidence-index.json", "evidenceRecord": "INTRUDER_ATTACKS_DATA"})
    return rows


def _target(target_id: str, eligible_taxa: list[str], *, selector: str = "rules-system", mode: str = "deterministic-state-filter", minimum: int = 0, maximum=None) -> dict:
    return {"targetId": target_id, "selectorRef": selector, "eligibleTaxonIds": eligible_taxa, "cardinality": {"min": minimum, "max": maximum}, "selectionMode": mode, "visibility": "public"}


def build_attack_records(repo: Path, attack_source_index: dict, record, assertion, timing, participant, condition, operation) -> list[dict]:
    del repo
    records = []
    face_by_card = {row["ttsCardId"]: row for row in attack_source_index["faces"]}

    records.append(record(
        "SEM-CONTAMINATION-GAIN-001", "Gain one Contamination card", "source-backed", "procedure", "official-primary", "verbatim-structure",
        [assertion("SA-CONTAMINATION-GAIN-RB", "SRC-RULEBOOK", "printed pages 3, 17, 32, and 36 / Contamination gain and Component Limits", ["timing", "targets", "operations", "partialResolution", "duration", "stacking"], "When a Character gains Contamination, draw one of the 27 finite Contamination cards and place it in that Character's discard pile; an unavailable finite component does nothing unless a specific source says otherwise.", "docs/rulebooks/rulebook_text.txt:lines 5408–5411, 5825–5833" )],
        ["term.contamination-card"], ["tax.entity.component.card.contamination", "tax.entity.agent.character", "tax.scaffold.supply-pool"], [],
        timing("TW-CONTAMINATION-GAIN", "tax.entity.component.card.contamination", "when-triggered", "per-source-instruction-to-gain-one-card"), [participant("P-CHARACTER", "affected", "tax.entity.agent.character"), participant("P-RULES", "rules-system")], "must", [], [],
        [{"informationId": "I-CONTAMINATION-GAIN", "subjectRef": "drawn Contamination card identity and destination", "audience": "public-component-identity; hidden INFECTED text", "revealTrigger": "draw/placement", "secrecy": "the card type/count and discard placement are public; hidden INFECTED text is not scanned or revealed"}], [],
        [_target("T-CONTAMINATION-CHARACTER", ["tax.entity.agent.character"], minimum=1, maximum=1)],
        [operation("S01", 1, "draw-random", "if-able", "P-RULES", "1 Contamination card from the finite Contamination deck", ["SA-CONTAMINATION-GAIN-RB"], target_ref="T-CONTAMINATION-CHARACTER", repeat={"physicalSupply": 27}), operation("S02", 2, "transition-zone", "if-able", "P-RULES", "drawn Contamination card", ["SA-CONTAMINATION-GAIN-RB"], conditions=["a Contamination card was available and drawn"], target_ref="T-CONTAMINATION-CHARACTER", transition={"from": "tax.scaffold.zone.deck", "to": "tax.scaffold.zone.discard-pile", "positionRef": "sem.position.deck-top"})],
        {"policy": "source-limited-components", "unit": "one requested Contamination card", "onImpossible": "if no physical Contamination card is available, this requested component does nothing; the caller controls whether later printed operations continue"}, {"kind": "instantaneous-card-gain"}, {"policy": "one physical card moves from the finite deck to one Character discard pile per successful invocation"}, [], [], []))

    def build_face(card_id: int) -> dict:
        definition = ATTACK_DEFINITIONS[card_id]
        source = face_by_card[card_id]
        code = str(card_id)
        scan_id = f"SA-ATK-{code}-SCAN"
        general_id = f"SA-ATK-{code}-GENERAL"
        health_id = f"SA-ATK-{code}-HEALTH"
        limits_id = f"SA-ATK-{code}-LIMITS"
        bga_id = f"SA-ATK-{code}-BGA"
        assertions = [
            assertion(scan_id, definition["sourceId"], f"{source['attackOccurrenceId']} / exact panels, punctuation, badge occurrences, and sentences", ["timing", "preconditions", "informationPolicy", "targets", "operations", "partialResolution", "sourceVariants", "unresolvedQuestionRefs"], source["printedBody"], f"docs/rules/semantics/attack-source-index.json:{source['attackOccurrenceId']}"),
            assertion(general_id, "SRC-RULEBOOK", "printed page 32 / Standard Attacks and type-specific effect lookup", ["timing", "preconditions", "informationPolicy", "targets", "operations", "partialResolution", "sourceVariants", "unresolvedQuestionRefs"], "The generic Intruder Attack procedure draws one random card, uses the source-scoped badge matching the attacking Adult/Drone/Queen, resolves that associated panel in printed order, and discards the card if it remains in resolution.", "docs/rulebooks/rulebook_text.txt:lines 5398–5406"),
            assertion(health_id, "SRC-RULEBOOK", "printed page 18 / Character Health, Serious Wounds, and death", ["targets", "operations", "partialResolution", "duration", "stacking", "unresolvedQuestionRefs"], "Health loss, random Serious Wound gain/placement, Health displacement, Armor loss, and Character death use the existing Character Health/Wound procedure.", "docs/rules/03-intruders-and-survival.md:INT-006"),
            assertion(limits_id, "SRC-RULEBOOK", "printed pages 3 and 17 / finite Contamination and Serious Wound supplies", ["targets", "operations", "partialResolution", "unresolvedQuestionRefs"], "The physical game has 27 Contamination and 27 Serious Wound cards; unavailable finite components do nothing where no special fallback is stated.", "docs/rulebooks/rulebook_text.txt:lines 520–540, 3538–3548"),
            assertion(bga_id, BGA_ATTACK_SOURCE_ID, f"INTRUDER_ATTACKS_DATA.{definition['bgaKey']}", ["sourceVariants"], source["bgaOccurrence"]["sourceBlockText"], f"docs/rules/semantics/attack-source-index.json:{source['attackOccurrenceId']}.bgaOccurrence"),
        ]
        assertions[0]["textKind"] = "verbatim"
        assertions[4]["textKind"] = "verbatim"
        official_assertion_ids = []
        counterpart_by_id = {row["sourceOccurrenceId"]: row for row in attack_source_index["officialVisibleCounterparts"]}
        for index, counterpart_ref in enumerate(definition["officialCounterpartRefs"], 1):
            counterpart = counterpart_by_id[counterpart_ref]
            assertion_id = f"SA-ATK-{code}-OFFICIAL-{index:02d}"
            item = assertion(assertion_id, "SRC-RULEBOOK", counterpart["locator"], ["preconditions", "targets", "operations", "sourceVariants"], counterpart["visibleText"], f"docs/rules/semantics/attack-source-index.json:{counterpart_ref}")
            item["textKind"] = "verbatim"
            assertions.append(item)
            official_assertion_ids.append(assertion_id)
        faq_id = None
        if definition["family"] == "miss":
            faq_id = f"SA-ATK-{code}-FAQ"
            item = assertion(faq_id, "SRC-FAQ", "General rules / FQ-P02-U11", ["operations", "partialResolution", "sourceVariants"], "Q: When a card tells me to reshuffle the deck, does it include the card itself?\nA: Yes.", "docs/rules/source-extraction/faq-v1.2-source-extraction.json:FQ-P02-U11")
            item["textKind"] = "verbatim"
            assertions.append(item)

        target_id = f"T-ATK-{code}-TARGET"
        targets = [_target(target_id, ["tax.entity.agent.character"], minimum=1, maximum=1)]
        participants = [participant("P-INTRUDER", "actor", "tax.entity.agent.intruder"), participant("P-TARGET", "affected", "tax.entity.agent.character"), participant("P-RULES", "rules-system")]
        information = [{"informationId": f"I-ATK-{code}", "subjectRef": "exact revealed Attack occurrence, attacking Intruder type, applicable printed panel, target, random cards, and outcome", "audience": "public", "revealTrigger": "Attack-card draw/resolution", "secrecy": "remaining Attack-deck order remains unrevealed; hidden Contamination INFECTED text is not scanned"}]
        terms = ["term.intruder-attack-card", "term.attack", "term.adult", "term.drone", "term.queen"]
        taxa = ["tax.entity.component.card.intruder-attack", "tax.process.attack", "tax.entity.agent.intruder", "tax.entity.agent.intruder.adult", "tax.entity.agent.intruder.drone", "tax.entity.agent.intruder.queen", "tax.entity.agent.character"]
        unresolved = list(definition["questions"])
        sentence_by_id = {row["sentenceId"]: row for row in source["sentences"]}
        ops = []

        def add(sentence_id: str, op_type: str, modality: str, subject: str, obj: str, *, source_ids=None, conditions=None, target_ref=target_id, transition=None, invoke=None, repeat=None, notes=None):
            sentence = sentence_by_id[sentence_id]
            step = len(ops) + 1
            op = operation(f"S{step:02d}", step, op_type, modality, subject, obj, source_ids or [scan_id, general_id], conditions=conditions, target_ref=target_ref, transition=transition, invoke=invoke, repeat=repeat, notes=notes)
            op["sourceSentenceId"] = sentence_id
            op["sourcePanelId"] = sentence["panelId"]
            op["sourceApplicabilityBadgeIds"] = [row["occurrenceId"] for row in source["applicabilityBadgeOccurrences"] if row["panelId"] == sentence["panelId"]]
            ops.append(op)
            return op

        def health(sentence_id: str, amount: int, *, conditions=None):
            terms.extend(["icon.characterHealth", "term.character-health"])
            taxa.extend(["tax.state.health", "tax.state.health.point"])
            return add(sentence_id, "invoke-process", "must", "P-TARGET", f"lose {amount} Character Health through SEM-INT-006", source_ids=[scan_id, health_id], conditions=conditions, invoke="SEM-INT-006")

        def contamination(sentence_id: str, *, conditions=None):
            terms.append("term.contamination-card")
            taxa.append("tax.entity.component.card.contamination")
            return add(sentence_id, "invoke-process", "if-able", "P-TARGET", "gain 1 Contamination card into the target discard pile", source_ids=[scan_id, limits_id], conditions=conditions, invoke="SEM-CONTAMINATION-GAIN-001")

        def wound(sentence_id: str, *, conditions=None, repeat=None, notes=None):
            terms.append("term.serious-wound-card")
            taxa.append("tax.entity.component.card.serious-wound")
            return add(sentence_id, "invoke-process", "if-able", "P-TARGET", "gain a random Serious Wound through SEM-INT-006", source_ids=[scan_id, health_id, limits_id], conditions=conditions, invoke="SEM-INT-006", repeat=repeat, notes=notes)

        def death(sentence_id: str, condition_text: str):
            terms.extend(["term.heavily-injured", "term.injured"])
            taxa.extend(["tax.state.health.heavily-injured", "tax.state.health.injured"])
            return add(sentence_id, "invoke-process", "must", "P-TARGET", "Character death through SEM-INT-006", source_ids=[scan_id, health_id], conditions=[condition_text], invoke="SEM-INT-006")

        family = definition["family"]
        sids = [row["sentenceId"] for row in source["sentences"]]
        if family == "bite":
            add(sids[0], "branch", "must", "P-RULES", "target is Heavily Injured or not", conditions=["attacking type matches any printed badge on P3"])
            death(sids[0], "target is Heavily Injured when the condition is evaluated")
            wound(sids[1], conditions=["target is not Heavily Injured"])
            add(sids[1], "resolve-open-alternative", "must", "P-RULES", "SEM-Q-021 continuation if the Serious Wound kills the target", source_ids=[scan_id, health_id], conditions=["target was not Heavily Injured before the Wound"])
            contamination(sids[1], conditions=["target is not Heavily Injured and continuation remains legal under SEM-Q-021"])
        elif family == "blood-sense":
            health(sids[0], 2, conditions=["attacking type is Adult"])
            health(sids[1], 2, conditions=["attacking type is Drone or Queen"])
            add(sids[2], "resolve-open-alternative", "must", "P-RULES", "SEM-Q-022 Moving-condition timing and relocation after target death/interruption", source_ids=[scan_id, general_id, health_id], conditions=["attacking type is Drone or Queen"])
            add(sids[2], "move-entity", "if-able", "P-INTRUDER", "the already attacking Intruder to the Room where the target's current Movement ends", conditions=["attacking type is Drone or Queen", "target is Moving under the unresolved SEM-Q-022 reading"], notes="No destination choice is created here; the Movement destination was selected by the enclosing Movement Sequence.")
            add(sids[3], "set-state", "must", "P-RULES", "this relocation does not trigger another entry Attack", conditions=["the Blood Sense relocation occurred"], notes="Suppression lasts only for the relocation caused by this parenthetical; it does not grant a persistent immunity.")
            terms.extend(["term.movement-sequence", "icon.intruder", "term.room"]); taxa.extend(["tax.process.sequence.movement", "tax.entity.spatial.room"])
        elif family == "deadly-claws":
            first_amount = {394906: 1, 394907: 2, 394908: 3}[card_id]
            health(sids[0], first_amount, conditions=["attacking type is Adult or Drone"])
            index = 1
            if card_id == 394907:
                add(sids[1], "resolve-open-alternative", "must", "P-RULES", "SEM-Q-021 continuation after potentially lethal Health loss", source_ids=[scan_id, health_id], conditions=["attacking type is Adult or Drone"])
                contamination(sids[1], conditions=["attacking type is Adult or Drone and continuation remains legal under SEM-Q-021"])
                index = 2
            condition_sid, otherwise_sid, then_sid = sids[index:index + 3]
            add(condition_sid, "branch", "must", "P-RULES", "Queen target is Heavily Injured or not", conditions=["attacking type is Queen"])
            death(condition_sid, "attacking type is Queen and target is Heavily Injured")
            add(otherwise_sid, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-023 random Wound-to-slot order and finite-deck exhaustion", source_ids=[scan_id, health_id, limits_id], conditions=["attacking type is Queen", "target is not Heavily Injured"])
            wound(otherwise_sid, conditions=["attacking type is Queen", "target is not Heavily Injured"], repeat={"scope": "each empty Serious Wound slot to the right of the Health marker", "slotOrder": "SEM-Q-023 unresolved", "physicalWoundSupply": 27}, notes="The card overrides ordinary slot eligibility but does not state random-card assignment order among multiple slots.")
            add(then_sid, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-021 whether the final additional Wound resolves after an earlier Wound causes death", source_ids=[scan_id, health_id], conditions=["attacking type is Queen", "target began the branch not Heavily Injured"])
            wound(then_sid, conditions=["attacking type is Queen", "target began the branch not Heavily Injured", "continuation remains legal under SEM-Q-021"], notes="Resolve only after the per-empty-slot instruction; exact continuation on death is prohibited from defaulting.")
        elif family == "fury":
            amount = 1 if card_id == 394909 else 2
            health(sids[0], amount, conditions=["attacking type is Adult"])
            add(sids[1], "resolve-open-alternative", "must", "P-RULES", "SEM-Q-021 continuation after potentially lethal Health loss", source_ids=[scan_id, health_id], conditions=["attacking type is Adult"])
            contamination(sids[1], conditions=["attacking type is Adult and continuation remains legal under SEM-Q-021"])
            participants.append(participant("P-AFFECTED-CHARACTERS", "collection", "tax.entity.agent.character"))
            targets.extend([_target(f"T-ATK-{code}-HEAVY", ["tax.entity.agent.character"], mode="deterministic-turn-order"), _target(f"T-ATK-{code}-SURVIVORS", ["tax.entity.agent.character"], mode="deterministic-turn-order")])
            add(sids[2], "resolve-open-alternative", "must", "P-RULES", "SEM-Q-020 global versus attacking-Room Character scope", source_ids=[scan_id, general_id], conditions=["attacking type is Drone or Queen"], target_ref=f"T-ATK-{code}-HEAVY")
            add(sids[2], "invoke-process", "must", "each Heavily Injured Character in the unresolved scope, in Turn order", "Character death through SEM-INT-006", source_ids=[scan_id, health_id], conditions=["attacking type is Drone or Queen"], target_ref=f"T-ATK-{code}-HEAVY", invoke="SEM-INT-006", repeat={"order": "Turn order"})
            add(sids[3], "select-target", "must", "P-RULES", "all Characters who survived the preceding sentence in the same unresolved scope", conditions=["attacking type is Drone or Queen"], target_ref=f"T-ATK-{code}-SURVIVORS")
            add(sids[3], "invoke-process", "if-able", "each surviving Character in Turn order", "gain 1 random Serious Wound through SEM-INT-006", source_ids=[scan_id, health_id, limits_id], conditions=["attacking type is Drone or Queen"], target_ref=f"T-ATK-{code}-SURVIVORS", invoke="SEM-INT-006", repeat={"order": "Turn order", "physicalWoundSupply": 27})
            add(sids[3], "resolve-open-alternative", "must", "P-RULES", "SEM-Q-021 continuation to Contamination if the new Wound kills a survivor", source_ids=[scan_id, health_id], conditions=["attacking type is Drone or Queen"], target_ref=f"T-ATK-{code}-SURVIVORS")
            add(sids[3], "invoke-process", "if-able", "each still-eligible surviving Character in Turn order", "gain 1 Contamination card", source_ids=[scan_id, limits_id], conditions=["attacking type is Drone or Queen", "continuation remains legal under SEM-Q-021"], target_ref=f"T-ATK-{code}-SURVIVORS", invoke="SEM-CONTAMINATION-GAIN-001", repeat={"order": "Turn order"})
            terms.extend(["term.heavily-injured", "term.serious-wound-card", "term.contamination-card"]); taxa.extend(["tax.state.health.heavily-injured", "tax.entity.component.card.serious-wound", "tax.entity.component.card.contamination"])
        elif family == "infecting":
            health(sids[0], 2, conditions=["attacking type is Adult or Queen in this exact scan occurrence"])
            contamination(sids[1], conditions=["attacking type is Drone in this exact scan occurrence"])
            add(sids[2], "place-component", "if-able", "P-RULES", "1 Larva from the finite pool on the target Character board", source_ids=[scan_id, limits_id], conditions=["attacking type is Drone in this exact scan occurrence", "target Character board has no Larva"], repeat={"requested": 1, "finiteModelSupply": True})
            terms.append("term.larva"); taxa.append("tax.entity.agent.intruder.larva")
        elif family == "miss":
            add(sids[0], "resolve-open-alternative", "must", "P-RULES", "SEM-Q-024 meaning of a text panel with no applicability badges", source_ids=[scan_id, general_id])
            add(sids[0], "evaluate-condition", "must", "P-RULES", "nothing happens before the reshuffle instruction", conditions=["the no-badge panel applies under the unresolved SEM-Q-024 reading"])
            source_ids = [scan_id, general_id, faq_id]
            add(sids[1], "transition-zone", "must", "P-RULES", "this MISS Attack card", source_ids=source_ids, conditions=["the no-badge panel applies under the unresolved SEM-Q-024 reading"], transition={"from": "sem.zone.card-in-resolution", "to": "tax.scaffold.zone.deck"})
            add(sids[1], "shuffle", "must", "P-RULES", "Intruder Attack deck including this MISS card", source_ids=source_ids, conditions=["this MISS card was returned to the deck"], notes="FAQ v1.2 makes the resolving card self-inclusive; generic SEM-INT-004 discard applies only if a card remains in resolution.")
            taxa.append("tax.scaffold.zone.deck")
        elif family == "scratch":
            if card_id == 394913:
                contamination(sids[0])
            elif card_id == 394914:
                health(sids[0], 1)
                add(sids[1], "resolve-open-alternative", "must", "P-RULES", "SEM-Q-021 continuation after potentially lethal Health loss", source_ids=[scan_id, health_id])
                contamination(sids[1], conditions=["continuation remains legal under SEM-Q-021"])
            elif card_id == 394915:
                health(sids[0], 1)
            elif card_id == 394916:
                health(sids[0], 2)
        elif family == "tail-attack":
            if card_id == 394918:
                contamination(sids[0], conditions=["attacking type is Adult or Queen in this exact scan occurrence"])
                condition_index = 1
            else:
                health(sids[0], 1, conditions=["attacking type is Adult or Queen in this exact scan occurrence"])
                add(sids[1], "resolve-open-alternative", "must", "P-RULES", "SEM-Q-021 continuation after potentially lethal Health loss", source_ids=[scan_id, health_id], conditions=["attacking type is Adult or Queen"])
                contamination(sids[1], conditions=["attacking type is Adult or Queen", "continuation remains legal under SEM-Q-021"])
                condition_index = 2
            condition_sid, otherwise_sid = sids[condition_index:condition_index + 2]
            add(condition_sid, "branch", "must", "P-RULES", "Drone target is Injured/Heavily Injured or neither", conditions=["attacking type is Drone in this exact scan occurrence"])
            death(condition_sid, "attacking type is Drone and target is Injured or Heavily Injured")
            wound(otherwise_sid, conditions=["attacking type is Drone", "target is neither Injured nor Heavily Injured"])
            add(otherwise_sid, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-021 continuation to Contamination if the Wound kills the target", source_ids=[scan_id, health_id], conditions=["attacking type is Drone", "target began the branch neither Injured nor Heavily Injured"])
            contamination(otherwise_sid, conditions=["attacking type is Drone", "target began the branch neither Injured nor Heavily Injured", "continuation remains legal under SEM-Q-021"])
        else:
            raise AssertionError(family)

        variants = [{"variantId": f"SV-ATK-{code}-BGA", "sourceId": BGA_ATTACK_SOURCE_ID, "sourceAssertionId": bga_id, "difference": source["bgaOccurrence"]["variantDifference"], "resolution": "Retain the licensed structured record as a lower-authority source variant; never rewrite the exact TTS occurrence or use title alone to merge repeated cards."}]
        for index, (counterpart_ref, assertion_id) in enumerate(zip(definition["officialCounterpartRefs"], official_assertion_ids), 1):
            counterpart = counterpart_by_id[counterpart_ref]
            variants.append({"variantId": f"SV-ATK-{code}-OFFICIAL-{index:02d}", "sourceId": "SRC-RULEBOOK", "sourceAssertionId": assertion_id, "difference": counterpart["variantDifference"], "resolution": "Retain the official-visible occurrence independently; official-primary wording/applicability controls the matching current counterpart without erasing the TTS scan variant or sibling repeated-title occurrences."})

        applicability_text = ", ".join(f"{row['sourceScopedResolution']['intruderType']} via {row['occurrenceId']} on {row['panelId']}" for row in source["applicabilityBadgeOccurrences"]) or "no printed applicability badges; SEM-Q-024"
        preconditions = [condition(f"C-ATK-{code}-FACE", "all", [{"predicate": f"drawn source occurrence is {source['attackOccurrenceId']}"}, {"predicate": f"applicable panel is selected only by exact source-scoped badge projection: {applicability_text}"}], [scan_id, general_id])]
        status = "source-backed-with-open-question" if unresolved else "source-backed"
        highest = "official-errata" if faq_id else "official-primary"
        result = record(
            definition["ruleId"], f"{definition['title'].title()} Intruder Attack occurrence {card_id}", status, "component-effect", highest, "open-alternatives" if unresolved else "source-composed", assertions, terms, taxa, definition["namedIdentityRefs"],
            timing(f"TW-ATK-{code}", "tax.process.attack", "during", "when-this-exact-Attack-occurrence-is-drawn-by-SEM-INT-004"), participants, "must", preconditions, [], information, [], targets, ops,
            {"policy": "source-conditional-steps", "unit": "one exact source panel selected by one attacking-Intruder badge occurrence", "onImpossible": "use finite-component rules per requested card/model; preserve printed operation order and every no-default continuation/scope/selector question; generic draw and discard remain owned by SEM-INT-004"}, {"kind": "instantaneous-selected-Attack-panel"}, {"policy": "one applicable panel per drawn physical occurrence; repeated titles/copies never stack or merge identity"}, [], unresolved, variants)
        return result

    records.extend(build_face(card_id) for card_id in sorted(ATTACK_DEFINITIONS))
    return records
