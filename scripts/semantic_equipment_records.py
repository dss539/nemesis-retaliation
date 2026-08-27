from __future__ import annotations

import json
import re
from pathlib import Path

from semantic_equipment_sources import (
    BGA_EQUIPMENT_SOURCE_ID,
    EQUIPMENT_REUSABLE_RULE_IDS,
)


EQUIPMENT_QUESTION_IDS = [f"SEM-Q-{number:03d}" for number in range(79, 97)]
EQUIPMENT_CONFLICT_IDS = [f"SC-{number:03d}" for number in range(70, 81)]
OFFICIAL_EQUIPMENT_RULE_IDS = [
    "SEM-CHARACTER-ITEM-OFFICIAL-AUTOMATIC-SHOTGUN-001",
    "SEM-CHARACTER-ITEM-OFFICIAL-SONIC-GUN-001",
    "SEM-HEAVY-OFFICIAL-MILITARY-TASER-001",
    "SEM-SUPPORT-OFFICIAL-GRENADE-LAUNCHER-001",
    "SEM-SUPPORT-OFFICIAL-HEAVY-ARMOR-001",
    "SEM-SUPPORT-OFFICIAL-TACTICAL-HATCHET-001",
]


_EFFECT_QUESTION_REFS = {
    "gatling-second-burst": ["SEM-Q-088", "SEM-Q-089"],
    "assault-shotgun-prevent": ["SEM-Q-083", "SEM-Q-088", "SEM-Q-091"],
    "entrenching-tool": ["SEM-Q-093"],
    "security-system-control": ["SEM-Q-088", "SEM-Q-093"],
    "submachine-gun": ["SEM-Q-088", "SEM-Q-091"],
    "plasma-gun": ["SEM-Q-088", "SEM-Q-089"],
    "rpg-launcher": ["SEM-Q-091", "SEM-Q-094", "SEM-Q-096"],
    "supporting-robot-controller": ["SEM-Q-012", "SEM-Q-013", "SEM-Q-092"],
    "portable-device": ["SEM-Q-018", "SEM-Q-092"],
    "hand-cannon": ["SEM-Q-088"],
    "tactical-hatchet": ["SEM-Q-088", "SEM-Q-089", "SEM-Q-091"],
    "combat-motion-tracker": ["SEM-Q-095"],
    "engineering-equipment": ["SEM-Q-093", "SEM-Q-096"],
    "sonic-gun": ["SEM-Q-088", "SEM-Q-089"],
    "autoloader-belt": ["SEM-Q-083", "SEM-Q-086"],
    "flamethrower": ["SEM-Q-088"],
    "grenade-launcher": ["SEM-Q-083", "SEM-Q-090"],
    "utility-vest": ["SEM-Q-083"],
    "bayonet": ["SEM-Q-081", "SEM-Q-089"],
    "tactical-armor": ["SEM-Q-082", "SEM-Q-086"],
    "heavy-armor": ["SEM-Q-082", "SEM-Q-086"],
    "drum-mag-rifle": ["SEM-Q-083"],
    "motion-tracker": ["SEM-Q-095"],
    "biohazard-armor": ["SEM-Q-082", "SEM-Q-086"],
    "excluded-heavy-medkit": ["SEM-Q-039", "SEM-Q-043", "SEM-Q-096"],
    "excluded-heavy-oxygen": ["SEM-Q-039", "SEM-Q-091", "SEM-Q-096"],
    "excluded-heavy-remote-detonator": ["SEM-Q-091", "SEM-Q-094", "SEM-Q-096"],
    "carbine": ["SEM-Q-079", "SEM-Q-083", "SEM-Q-088"],
    "handgun": ["SEM-Q-079", "SEM-Q-083", "SEM-Q-088"],
    "bulletproof-vest": ["SEM-Q-079", "SEM-Q-082", "SEM-Q-086"],
    "sawed-off-shotgun": ["SEM-Q-079", "SEM-Q-083", "SEM-Q-088", "SEM-Q-091"],
    "assault-rifle": ["SEM-Q-079", "SEM-Q-083", "SEM-Q-088"],
    "official-automatic-shotgun": ["SEM-Q-088"],
    "official-sonic-gun": ["SEM-Q-088", "SEM-Q-089"],
    "official-tactical-hatchet": ["SEM-Q-088", "SEM-Q-089", "SEM-Q-091"],
    "official-military-taser": ["SEM-Q-094", "SEM-Q-096"],
    "official-heavy-armor": ["SEM-Q-082", "SEM-Q-086"],
    "official-grenade-launcher": ["SEM-Q-090"],
}


def _target(target_id: str, eligible: list[str], *, selector: str = "P-OWNER", mode: str = "player-choice", minimum: int = 1, maximum=1, visibility: str = "public") -> dict:
    return {"targetId": target_id, "selectorRef": selector, "eligibleTaxonIds": eligible, "cardinality": {"min": minimum, "max": maximum}, "selectionMode": mode, "visibility": visibility}


def _face_terms_and_taxa(face: dict) -> tuple[list[str], list[str]]:
    terms = ["term.item"]
    taxa = ["tax.entity.component.card.item"]
    item_source = face.get("itemSourceClass")
    physical = face.get("physicalClass")
    if item_source == "support-equipment":
        terms.append("term.support-equipment")
        taxa.append("tax.entity.component.card.item.support")
    elif item_source == "character-item":
        terms.append("term.character-item")
        taxa.append("tax.entity.component.card.item.character")
    if physical == "armor-item":
        terms.append("term.armor-item")
        taxa.append("tax.entity.component.card.item.armor")
    else:
        terms.append("term.heavy-item")
        taxa.append("tax.entity.component.card.item.heavy")
    if physical in {"ranged-weapon", "melee-weapon"}:
        terms.append("term.weapon")
        taxa.append("tax.entity.component.card.item.weapon")
    if physical == "ranged-weapon":
        terms.append("term.ranged-weapon")
        taxa.append("tax.entity.component.card.item.weapon.ranged")
    if physical == "melee-weapon":
        terms.append("term.melee-weapon")
        taxa.append("tax.entity.component.card.item.weapon.melee")
    for icon in face.get("iconOccurrences") or []:
        if icon.get("semanticReferenceId"):
            terms.append(icon["semanticReferenceId"])
    return terms, taxa


def _effect_questions(face: dict) -> list[str]:
    return list(dict.fromkeys(_EFFECT_QUESTION_REFS.get(face.get("effectKind"), [])))


def equipment_rule_ids(source_index: dict) -> dict[str, list[str]]:
    support = [row["semanticRuleId"] for row in source_index["supportEquipmentFaces"]]
    character = [row["semanticRuleId"] for row in source_index["characterItemTtsFaces"] if row.get("semanticRuleId")]
    color_heavy = [row["semanticRuleId"] for row in source_index["colorRootHeavyFaces"]]
    official = [row["semanticRuleId"] for row in source_index["officialVisibleOccurrences"]]
    return {
        "support": support,
        "character": character,
        "colorHeavy": color_heavy,
        "official": official,
        "physical": [*support, *character, *color_heavy],
        "allFaces": [*support, *character, *color_heavy, *official],
        "reusable": list(EQUIPMENT_REUSABLE_RULE_IDS),
        "all": [*EQUIPMENT_REUSABLE_RULE_IDS, *support, *character, *color_heavy, *official],
    }


def equipment_question_blocks(source_index: dict) -> dict[str, list[str]]:
    blocks = {qid: [] for qid in EQUIPMENT_QUESTION_IDS}
    faces = [
        *source_index["supportEquipmentFaces"],
        *[row for row in source_index["characterItemTtsFaces"] if row.get("semanticRuleId")],
        *source_index["colorRootHeavyFaces"],
    ]
    for face in faces:
        for qid in _effect_questions(face):
            if qid in blocks:
                blocks[qid].append(face["semanticRuleId"])
    official_kinds = {
        "SEM-CHARACTER-ITEM-OFFICIAL-AUTOMATIC-SHOTGUN-001": "official-automatic-shotgun",
        "SEM-CHARACTER-ITEM-OFFICIAL-SONIC-GUN-001": "official-sonic-gun",
        "SEM-SUPPORT-OFFICIAL-TACTICAL-HATCHET-001": "official-tactical-hatchet",
        "SEM-HEAVY-OFFICIAL-MILITARY-TASER-001": "official-military-taser",
        "SEM-SUPPORT-OFFICIAL-HEAVY-ARMOR-001": "official-heavy-armor",
        "SEM-SUPPORT-OFFICIAL-GRENADE-LAUNCHER-001": "official-grenade-launcher",
    }
    for rule_id, kind in official_kinds.items():
        for qid in _EFFECT_QUESTION_REFS[kind]:
            if qid in blocks:
                blocks[qid].append(rule_id)
    reusable = {
        "SEM-Q-079": ["SEM-CHARACTER-ITEM-SETUP-001", "SEM-EQUIPMENT-VARIANT-BOUNDARIES-001"],
        "SEM-Q-080": ["SEM-SUPPORT-EQUIPMENT-DRAFT-001"],
        "SEM-Q-081": ["SEM-HEAVY-ITEM-HAND-CAPACITY-001", "SEM-ITEM-TRADE-GAIN-001"],
        "SEM-Q-082": ["SEM-ARMOR-ITEM-LIFECYCLE-001", "SEM-ITEM-LOSS-ATTACHED-GEAR-001"],
        "SEM-Q-083": ["SEM-EQUIPMENT-FULLY-LOADED-001", "SEM-EQUIPMENT-VARIANT-BOUNDARIES-001"],
        "SEM-Q-084": ["SEM-EQUIPMENT-FULLY-LOADED-001", "SEM-SUPPORT-EQUIPMENT-DRAFT-001"],
        "SEM-Q-085": ["SEM-ITEM-TRADE-GAIN-001", "SEM-HEAVY-ITEM-HAND-CAPACITY-001", "SEM-ARMOR-ITEM-LIFECYCLE-001"],
        "SEM-Q-086": ["SEM-ITEM-PASSIVE-EFFECT-001"],
        "SEM-Q-087": ["SEM-ITEM-LOSS-ATTACHED-GEAR-001", "SEM-CHARACTER-ITEM-SETUP-001"],
        "SEM-Q-088": ["SEM-WEAPON-DIE-RESULT-ADDITION-001", "SEM-WEAPON-MALFUNCTION-LIFECYCLE-001"],
        "SEM-Q-089": ["SEM-WEAPON-MALFUNCTION-LIFECYCLE-001", "SEM-ITEM-LOSS-ATTACHED-GEAR-001"],
        "SEM-Q-090": ["SEM-GRENADE-LAUNCHER-MALFUNCTION-001"],
        "SEM-Q-091": ["SEM-EQUIPMENT-VARIANT-BOUNDARIES-001"],
        "SEM-Q-092": ["SEM-EQUIPMENT-OCCURRENCE-DISPATCH-001"],
        "SEM-Q-093": ["SEM-EQUIPMENT-OCCURRENCE-DISPATCH-001"],
        "SEM-Q-094": ["SEM-EQUIPMENT-OCCURRENCE-DISPATCH-001"],
        "SEM-Q-095": ["SEM-EQUIPMENT-OCCURRENCE-DISPATCH-001"],
        "SEM-Q-096": ["SEM-HEAVY-ITEM-USE-001", "SEM-HEAVY-ITEM-ONE-USE-001"],
    }
    for qid, rule_ids in reusable.items():
        blocks[qid] = [*rule_ids, *blocks[qid]]
    return {qid: list(dict.fromkeys(rule_ids)) for qid, rule_ids in blocks.items()}


def _effect_atoms(face: dict, assertion_id: str, operation, decision, condition) -> tuple[list[dict], list[dict], list[dict], list[dict]]:
    kind = {
        "official-sonic-gun": "sonic-gun",
        "official-tactical-hatchet": "tactical-hatchet",
        "official-heavy-armor": "heavy-armor",
        "official-grenade-launcher": "grenade-launcher",
    }.get(face["effectKind"], face["effectKind"])
    code = face["semanticRuleId"].removeprefix("SEM-").removesuffix("-001")
    sentences = face.get("sentences") or []
    decisions: list[dict] = []
    targets: list[dict] = []
    preconditions: list[dict] = []
    operations: list[dict] = []

    def add(op_type: str, modality: str, subject: str, obj: str, *, sentence=1, conditions=None, decision_ref=None, target_ref=None, transition=None, value_change=None, invoke=None, repeat=None, notes=None):
        row = operation(f"S{len(operations)+1:02d}", len(operations)+1, op_type, modality, subject, obj, [assertion_id], conditions=conditions, decision_ref=decision_ref, target_ref=target_ref, transition=transition, value_change=value_change, invoke=invoke, repeat=repeat, notes=notes)
        if sentences:
            source_sentence = sentences[min(max(sentence - 1, 0), len(sentences) - 1)]
            row["sourceSentenceId"] = source_sentence["sentenceId"]
            row["sourcePanelId"] = source_sentence["panelId"]
        operations.append(row)
        return row

    def branch(options: list[str]) -> str:
        did = f"D-{code}-BRANCH"
        decisions.append(decision(did, "P-OWNER", "player-choice", 1, 1, False, "public-on-declaration", options))
        add("choose", "must", "P-OWNER", "one exact printed OR branch", decision_ref=did)
        return did

    def target(suffix: str, eligible: list[str], label: str, *, owner="P-OWNER", mode="player-choice", minimum=1, maximum=1, unresolved=False) -> str:
        did = f"D-{code}-{suffix}"
        selection = "unresolved" if unresolved else mode
        decisions.append(decision(did, owner if not unresolved else "P-RULES", selection, minimum, maximum, minimum == 0, "public-on-declaration", [label]))
        tid = f"T-{code}-{suffix}"
        targets.append(_target(tid, eligible, selector=owner if not unresolved else "P-RULES", mode=mode if not unresolved else "unresolved-order", minimum=minimum, maximum=maximum))
        add("select-target", "must", owner if not unresolved else "P-RULES", label, decision_ref=did, target_ref=tid)
        return tid

    if kind in {"gatling-second-burst"}:
        add("evaluate-condition", "must", "P-RULES", "trigger immediately after this Weapon completes one Burst")
        did = f"D-{code}-SECOND-BURST"
        decisions.append(decision(did, "P-OWNER", "player-choice", 0, 1, True, "public-on-declaration", ["decline", "Burst a second time at the same Corridor without spending Ammo"]))
        add("choose", "may", "P-OWNER", "whether to Burst a second time", decision_ref=did)
        add("invoke-process", "may", "P-CHARACTER", "one second Burst at the same Corridor with this effect's Ammo spend waived", conditions=["owner chooses second Burst"], decision_ref=did, invoke="SEM-ACT-BURST-001")
        add("invoke-process", "must", "P-RULES", "Weapon die-result additional-effect procedure for the printed special result", invoke="SEM-WEAPON-DIE-RESULT-ADDITION-001")
        add("place-component", "must", "P-RULES", "one Malfunction marker on this Weapon when its printed special result occurs", invoke="SEM-WEAPON-MALFUNCTION-LIFECYCLE-001")
    elif kind == "assault-shotgun-prevent":
        add("evaluate-condition", "must", "P-RULES", "this Character would be Attacked by one Intruder")
        did = f"D-{code}-PREVENT"
        decisions.append(decision(did, "P-OWNER", "player-choice", 0, 1, True, "public-on-declaration", ["decline", "spend all source-local resource occurrences from this Weapon"]))
        add("resolve-open-alternative", "must", "P-RULES", "SEM-Q-091 exact source-local resource glyph and spend eligibility")
        add("pay-cost", "may", "P-OWNER", "all source-established matching resources from this Weapon", conditions=["owner elects prevention", "SEM-Q-091 establishes the resource"], decision_ref=did)
        add("change-value", "must", "P-RULES", "attacking Intruder receives 1 Hit", conditions=["cost paid"], value_change={"amount": 1, "value": "Hits"})
        add("end-process", "must", "P-RULES", "pending Intruder Attack is Prevented", conditions=["cost paid"])
    elif kind == "entrenching-tool":
        did = branch(["Destroy 1 accessible Door.", "Place 2 Secure tokens."])
        door = target("DOOR", ["tax.entity.spatial.door"], "one accessible Door")
        add("set-state", "must", "P-RULES", "selected Door becomes Destroyed", conditions=["Door branch selected"], decision_ref=did, target_ref=door)
        add("resolve-open-alternative", "must", "P-RULES", "SEM-Q-093 target/placement owner and exact-two finite Secure allocation", conditions=["Secure branch selected"], decision_ref=did)
        add("place-component", "if-able", "P-RULES", "exactly 2 Secure tokens in source-legal locations", conditions=["Secure branch selected", "SEM-Q-093 resolved"], repeat={"quantity": 2, "finiteSupply": True})
    elif kind == "security-system-control":
        add("resolve-open-alternative", "must", "P-RULES", "SEM-Q-093 owner and eligibility for the Secure-bearing Room and adjacent Corridor")
        room = target("ROOM", ["tax.entity.spatial.room"], "one source-legal Room in the same Section with a Secure token", unresolved=True)
        add("remove-component", "must", "P-RULES", "1 Secure token from selected Room", target_ref=room)
        corridor = target("CORRIDOR", ["tax.entity.spatial.corridor"], "one Corridor adjacent to selected Room", unresolved=True)
        add("draw-random", "must", "P-CHARACTER", "one Burst die result for this Item effect", target_ref=corridor)
        add("change-value", "must", "P-OWNER", "allocate Hits equal to the numeric result among eligible Intruders in the selected Corridor", target_ref=corridor, value_change={"amount": "Burst-die numeric result", "value": "Hits"})
        add("invoke-process", "must", "P-RULES", "printed special-result Malfunction in addition to the standard die result", conditions=["printed special result"], invoke="SEM-WEAPON-DIE-RESULT-ADDITION-001")
    elif kind == "submachine-gun":
        add("invoke-process", "must", "P-RULES", "standard Shoot-die Ammo-loss result remains in force", invoke="SEM-WEAPON-DIE-RESULT-ADDITION-001")
        add("resolve-open-alternative", "must", "P-RULES", "SEM-Q-091 isolated source-local result glyph after Deal")
        add("evaluate-condition", "if-able", "P-RULES", "apply the source-established additional result only after SEM-Q-091 resolves its exact denotation", conditions=["SEM-Q-091 resolved"])
    elif kind == "plasma-gun":
        add("invoke-process", "must", "P-RULES", "standard die result plus this Weapon effect", invoke="SEM-WEAPON-DIE-RESULT-ADDITION-001")
        add("change-value", "must", "P-CHARACTER", "lose 2 Character Health for each Universal marker currently on this Weapon", value_change={"amount": "-2 per current Universal marker", "value": "Character Health"})
        add("place-component", "must", "P-RULES", "1 Universal marker on this Weapon after the complete Health-loss calculation", repeat={"quantity": 1})
    elif kind == "rpg-launcher":
        room = target("ROOM", ["tax.entity.spatial.room"], "one neighboring Room")
        add("set-state", "must", "P-RULES", "all Doors in the selected Room and all Corridors adjacent to it become Destroyed", target_ref=room, repeat={"scope": "all named Doors"})
        add("resolve-open-alternative", "must", "P-RULES", "SEM-Q-091 exact isolated result glyph and SEM-Q-094 allocation/continuation")
        add("change-value", "if-able", "P-RULES", "all Intruders in the selected Room and adjacent Corridors receive the source-established result", conditions=["SEM-Q-091 resolved"], target_ref=room, repeat={"scope": "all matching Intruders"})
        add("change-value", "must", "P-RULES", "each Character in the selected Room and adjacent Corridors loses 3 Character Health", target_ref=room, value_change={"amount": -3, "value": "Character Health"}, repeat={"scope": "each Character"})
    elif kind == "supporting-robot-controller":
        did = branch(["Activate the Robot anywhere in the Facility.", "Place the Robot in your Room; reveal its card if the Hibernatorium is not Discovered."])
        add("invoke-process", "must", "P-CHARACTER", "Activate the Robot under existing reveal/movement/availability gates", conditions=["Activation branch selected"], decision_ref=did, invoke="SEM-ACT-ROBOT-001")
        add("resolve-open-alternative", "must", "P-RULES", "SEM-Q-012/092 pre-reveal external targeting, actor, and effect availability", conditions=["placement branch selected"], decision_ref=did)
        add("move-entity", "if-able", "P-RULES", "Robot to this Character's Room", conditions=["placement branch selected", "SEM-Q-012/092 permits resolution"])
        add("reveal", "must", "P-RULES", "selected Robot card", conditions=["placement branch selected", "Hibernatorium is not Discovered", "placement remains source-legal"])
    elif kind == "portable-device":
        preconditions.append(condition(f"C-{code}-ROOM", "any", [{"predicate": "Character is in a Computer Room"}, {"predicate": "Character is in a Life Support Control Room"}], [assertion_id]))
        add("resolve-open-alternative", "must", "P-RULES", "SEM-Q-018/092 actor, local context, and nested Use-the-Room costs")
        add("invoke-selected-process", "if-able", "P-CHARACTER", "exact occupied Room effect with its Malfunction restriction bypassed only", conditions=["SEM-Q-018/092 source context resolved"])
    elif kind == "hand-cannon":
        add("change-value", "must", "P-RULES", "each numeric Burst result from this Weapon is reduced by 1", value_change={"amount": -1, "value": "Burst result"})
        add("change-value", "must", "P-RULES", "each numeric Shoot result from this Weapon is reduced by 1", value_change={"amount": -1, "value": "Shoot result"})
    elif kind == "tactical-hatchet":
        add("resolve-open-alternative", "must", "P-RULES", "SEM-Q-091 exact isolated result glyph used instead of the Melee Shoot-die roll")
        add("evaluate-condition", "if-able", "P-RULES", "apply the source-established result instead of rolling", conditions=["SEM-Q-091 resolved"])
        add("place-component", "must", "P-RULES", "1 Malfunction marker on this Weapon", invoke="SEM-WEAPON-MALFUNCTION-LIFECYCLE-001")
    elif kind == "combat-motion-tracker":
        add("set-state", "must", "P-RULES", "while this exact Item is owned, its Character ignores Hazard results from all sources whenever discovering a new Room")
        add("resolve-open-alternative", "must", "P-RULES", "SEM-Q-095 trigger window and interaction with Exploration/Noise/Hazard source order")
    elif kind == "engineering-equipment":
        did = branch(["Remove a Malfunction or a Fire.", "Remove this Item and Reinforce an empty Corridor."])
        marker = target("MARKER", ["tax.entity.component.marker.malfunction", "tax.entity.component.marker.fire"], "one source-legal local Malfunction or Fire marker", unresolved=True)
        add("remove-component", "must", "P-RULES", "selected marker", conditions=["marker branch selected", "SEM-Q-093 target resolved"], decision_ref=did, target_ref=marker)
        add("transition-zone", "must", "P-RULES", "this exact Item is removed from the game", conditions=["Reinforce branch selected"], decision_ref=did, transition={"from": "owned Hand slot", "to": "tax.scaffold.zone.removed-from-game"})
        add("resolve-open-alternative", "must", "P-RULES", "SEM-Q-093 target and SEM-Q-096 Item-removal/Reinforce order", conditions=["Reinforce branch selected"], decision_ref=did)
        add("invoke-process", "if-able", "P-RULES", "Reinforce one source-legal empty Corridor", conditions=["Reinforce branch selected", "SEM-Q-093/096 resolved"], invoke="SEM-REINFORCE-CORRIDOR-001")
    elif kind == "sonic-gun":
        add("change-value", "must", "P-RULES", "Burst result 3 or 4 from this Weapon is treated as Burst result 2", value_change={"from": [3, 4], "to": 2, "value": "Burst result"})
        add("invoke-process", "must", "P-RULES", "standard special die result plus this source effect", invoke="SEM-WEAPON-DIE-RESULT-ADDITION-001")
        add("place-component", "must", "P-RULES", "1 Malfunction marker in this Character's Room on either printed special result", invoke="SEM-ROOM-MALFUNCTION-PLACEMENT-001")
    elif kind == "autoloader-belt":
        add("resolve-open-alternative", "must", "P-RULES", "SEM-Q-083 exact source-local slot identities/count and attached Ammo availability")
        add("permit", "if-able", "P-CHARACTER", "treat each source-established Ammo token on this Armor as if loaded in any owned Weapon", conditions=["SEM-Q-083 establishes the attached Ammo slots/tokens"])
    elif kind == "flamethrower":
        add("evaluate-condition", "must", "P-RULES", "whether the Character is in a Section with Inactive Life Support")
        add("pay-cost", "must", "P-CHARACTER", "1 Oxygen before this Weapon's Shoot or Burst when Life Support is Inactive", conditions=["Life Support is Inactive"])
        add("invoke-process", "must", "P-RULES", "standard die result plus this Weapon effect", invoke="SEM-WEAPON-DIE-RESULT-ADDITION-001")
        add("place-component", "must", "P-RULES", "1 Fire marker in this Character's Room on either printed special result")
    elif kind == "grenade-launcher":
        add("resolve-open-alternative", "must", "P-RULES", "SEM-Q-083 exact source slot/token identity and SEM-Q-090 count/timing before-or-instead choice")
        did = f"D-{code}-GRENADES"
        decisions.append(decision(did, "P-OWNER", "player-choice-sequential", 0, None, True, "public-on-use", ["stop", "use one next source-established Grenade token from this Weapon"]))
        add("choose", "may", "P-OWNER", "any source-legal number of Grenade tokens from this Weapon one at a time", decision_ref=did)
        add("invoke-process", "may", "P-CHARACTER", "Grenade token effect for each selected token", decision_ref=did, invoke="SEM-GRENADE-TOKEN-EFFECT-001", repeat={"scope": "each selected token", "selectionTiming": "SEM-Q-090 unresolved"})
        add("invoke-process", "must", "P-RULES", "FQ-P03-U03 malfunctioning-Grenade-Launcher Tactical Gear carveout", invoke="SEM-GRENADE-LAUNCHER-MALFUNCTION-001")
    elif kind in {"utility-vest", "drum-mag-rifle"}:
        add("evaluate-condition", "must", "P-RULES", "this exact face prints no special effect beyond its class and source-resolved slot/ordinary lifecycle evidence")
        add("resolve-open-alternative", "must", "P-RULES", "SEM-Q-083 exact TTS slot identities/count; GMNotes and licensed fields remain corroboration/variants only")
    elif kind == "bayonet":
        add("permit", "may", "P-OWNER", "hold this Item in the same Hand slot as one Ranged Weapon", invoke="SEM-HEAVY-ITEM-HAND-CAPACITY-001")
        add("evaluate-condition", "must", "P-RULES", "this Character would be Attacked by one Intruder")
        did = f"D-{code}-PREVENT"
        decisions.append(decision(did, "P-OWNER", "player-choice", 0, 1, True, "public-on-declaration", ["decline", "place a Malfunction on this Bayonet to Prevent the Attack"]))
        add("place-component", "may", "P-OWNER", "1 Malfunction marker on this Bayonet", decision_ref=did, invoke="SEM-WEAPON-MALFUNCTION-LIFECYCLE-001")
        add("end-process", "must", "P-RULES", "pending Intruder Attack is Prevented", conditions=["Malfunction was legally placed"], decision_ref=did)
    elif kind == "tactical-armor":
        add("evaluate-condition", "must", "P-RULES", "Character loses Health as a result of an Intruder Attack")
        add("change-value", "must", "P-RULES", "reduce that source Health loss by 1, not below zero", value_change={"amount": 1, "value": "prevented Character Health loss"})
    elif kind == "heavy-armor":
        add("evaluate-condition", "must", "P-RULES", "Character would gain one Serious Wound")
        did = f"D-{code}-REPLACE"
        decisions.append(decision(did, "P-OWNER", "player-choice", 0, 1, True, "public-on-declaration", ["gain the Serious Wound normally", "lose 2 Character Health instead"]))
        add("replace-target", "may", "P-OWNER", "replace this one Serious Wound gain with losing 2 Character Health", decision_ref=did)
        add("change-value", "if-able", "P-CHARACTER", "lose 2 Character Health", conditions=["owner selects replacement"], decision_ref=did, value_change={"amount": -2, "value": "Character Health"})
    elif kind == "motion-tracker":
        corridor = target("CORRIDOR", ["tax.entity.spatial.corridor"], "one Corridor anywhere in the Facility", unresolved=True)
        add("remove-component", "must", "P-RULES", "1 Noise marker from selected Corridor", target_ref=corridor)
        add("draw-random", "must", "P-CHARACTER", "one Noise-die result", target_ref=corridor)
        add("resolve-open-alternative", "must", "P-RULES", "SEM-Q-095 exact Corridor number comparison, Hazard handling, and Encounter timing", target_ref=corridor)
        add("invoke-process", "if-able", "P-RULES", "Encounter in selected Corridor when the result equals its printed number", conditions=["SEM-Q-095 equality/Encounter conditions met"], target_ref=corridor, invoke="SEM-NOISE-001")
    elif kind == "biohazard-armor":
        add("evaluate-condition", "must", "P-RULES", "Character would gain one Contamination")
        add("replace-target", "must", "P-RULES", "replace that Contamination gain with losing 1 Character Health")
        add("change-value", "must", "P-CHARACTER", "lose 1 Character Health instead", value_change={"amount": -1, "value": "Character Health"})
    elif kind == "excluded-heavy-medkit":
        did = f"D-{code}-ANDOR"
        decisions.append(decision(did, "P-OWNER", "player-choice", 1, 2, False, "public-on-declaration", ["discard 1 Serious Wound", "restore up to 3 Character Health", "both, in source-unspecified order"]))
        add("choose", "must", "P-OWNER", "one or both printed and/or clauses", decision_ref=did)
        add("invoke-process", "if-able", "P-CHARACTER", "discard one owner-selected Serious Wound", conditions=["discard clause selected"], decision_ref=did, invoke="SEM-SERIOUS-WOUND-DISCARD-001")
        add("invoke-process", "if-able", "P-CHARACTER", "restore up to 3 Character Health under SEM-Q-043", conditions=["restore clause selected"], decision_ref=did, invoke="SEM-RESTORE-HEALTH-001", repeat={"sourceMaximum": 3})
        add("resolve-open-alternative", "must", "P-RULES", "SEM-Q-096 order when both and/or clauses and One Use lifecycle interact", conditions=["both clauses selected"])
    elif kind == "excluded-heavy-oxygen":
        add("resolve-open-alternative", "must", "P-RULES", "SEM-Q-091 exact source-local upper-right restriction denotation")
        add("change-value", "must", "P-CHARACTER", "gain 7 Oxygen without exceeding 7", conditions=["any source-local restriction under SEM-Q-091 is satisfied"], value_change={"amount": 7, "cap": 7, "value": "Oxygen"})
    elif kind == "excluded-heavy-remote-detonator":
        room = target("ROOM", ["tax.entity.spatial.room"], "one source-legal Room in the same Section with a Secure token", unresolved=True)
        add("remove-component", "must", "P-RULES", "1 Secure token from selected Room", target_ref=room)
        add("resolve-open-alternative", "must", "P-RULES", "SEM-Q-091 isolated result-glyph scope and SEM-Q-094 target/allocation/continuation", target_ref=room)
        add("change-value", "if-able", "P-RULES", "all Intruders in selected Room receive the source-established result", conditions=["SEM-Q-091 resolved"], target_ref=room, repeat={"scope": "all Intruders"})
        add("change-value", "must", "P-RULES", "each Character there loses 3 Character Health", target_ref=room, value_change={"amount": -3, "value": "Character Health"}, repeat={"scope": "each Character there"})
    elif kind == "carbine":
        add("evaluate-condition", "must", "P-RULES", "a Shoot with this Weapon has completed and did not kill its target Intruder")
        add("change-value", "must", "P-RULES", "that Intruder receives 1 additional Hit", value_change={"amount": 1, "value": "Hits"})
    elif kind == "handgun":
        add("change-value", "must", "P-RULES", "each numeric Burst result from this Weapon is reduced by 1", value_change={"amount": -1, "value": "Burst result"})
    elif kind == "bulletproof-vest":
        add("evaluate-condition", "must", "P-RULES", "Character would gain one Serious Wound")
        did = f"D-{code}-DISCARD"
        decisions.append(decision(did, "P-OWNER", "player-choice", 0, 1, True, "public-on-declaration", ["gain Wound normally", "discard this Item instead"]))
        add("transition-zone", "may", "P-RULES", "this exact Armor Item to the Item discard pile instead of gaining the Wound", conditions=["owner chooses replacement"], decision_ref=did, transition={"from": "Armor position", "to": "tax.scaffold.zone.discard-pile"})
    elif kind == "sawed-off-shotgun":
        add("resolve-open-alternative", "must", "P-RULES", "SEM-Q-091 exact source-local spend glyph and SEM-Q-088 replacement timing")
        adult = target("ADULT", ["tax.entity.agent.intruder"], "one Adult in the Room")
        add("pay-cost", "may", "P-OWNER", "one source-established resource from this Weapon instead of a normal Shoot", conditions=["SEM-Q-091 resolves resource"], target_ref=adult)
        add("invoke-process", "must", "P-RULES", "Repel selected Adult", conditions=["replacement cost paid"], target_ref=adult, invoke="SEM-INTRUDER-REPEL-001")
    elif kind == "assault-rifle":
        add("evaluate-condition", "must", "P-RULES", "one Shoot with this Weapon has completed")
        did = f"D-{code}-SECOND-SHOOT"
        decisions.append(decision(did, "P-OWNER", "player-choice", 0, 1, True, "public-on-declaration", ["decline", "spend 1 Ammo to Shoot a second time at the same Intruder"]))
        add("pay-cost", "may", "P-OWNER", "1 Ammo from this Weapon", decision_ref=did)
        add("invoke-process", "must", "P-CHARACTER", "one second Shoot at the same Intruder", conditions=["Ammo paid"], decision_ref=did, invoke="SEM-ACT-SHOOT-001")
    elif kind == "official-automatic-shotgun":
        add("change-value", "must", "P-RULES", "deal 1 Hit before the enclosing Shoot")
        add("invoke-process", "must", "P-RULES", "standard Shoot-die Critical result plus spend Ammo if able", invoke="SEM-WEAPON-DIE-RESULT-ADDITION-001")
    elif kind == "official-tactical-hatchet":
        add("resolve-open-alternative", "must", "P-RULES", "SEM-Q-091 exact official isolated result glyph")
        add("evaluate-condition", "if-able", "P-RULES", "apply source-established result instead of the Melee Shoot-die roll", conditions=["SEM-Q-091 resolved"])
        add("place-component", "must", "P-RULES", "1 Malfunction marker on this Weapon", invoke="SEM-WEAPON-MALFUNCTION-LIFECYCLE-001")
    elif kind == "official-military-taser":
        did = branch(["Repel 1 Intruder from the Room.", "A Character of your choice discards all Action cards."])
        add("resolve-open-alternative", "must", "P-RULES", "SEM-Q-094 target owner, target scope, and branch continuation", decision_ref=did)
        add("invoke-process", "if-able", "P-RULES", "Repel one source-legal Intruder", conditions=["Repel branch", "SEM-Q-094 resolved"], decision_ref=did, invoke="SEM-INTRUDER-REPEL-001")
        add("transition-zone", "if-able", "P-RULES", "all Action cards of one source-legal chosen Character", conditions=["discard branch", "SEM-Q-094 resolved"], decision_ref=did, transition={"from": "tax.scaffold.zone.hand", "to": "tax.scaffold.zone.discard-pile"})
    else:
        raise AssertionError(f"unhandled Equipment effect kind: {kind}")
    return preconditions, decisions, targets, operations


def _build_physical_face_record(face: dict, record, assertion, timing, participant, condition, decision, operation) -> dict:
    rule_id = face["semanticRuleId"]
    source_id = face["sourceId"]
    occurrence_id = face.get("supportEquipmentOccurrenceId") or face.get("characterItemOccurrenceId") or face.get("equipmentOccurrenceId")
    assertion_id = "SA-" + rule_id.removeprefix("SEM-") + "-FACE"
    exact = assertion(assertion_id, source_id, f"{occurrence_id} / exact full selector, title, trait, panels, punctuation, text, icons, slots/tracks evidence", ["timing", "preconditions", "decisions", "informationPolicy", "costs", "targets", "operations", "partialResolution", "duration", "stacking", "unresolvedQuestionRefs", "sourceVariants"], face.get("printedBody") or face.get("typeLine") or face.get("printedTitle"), f"docs/rules/semantics/equipment-source-index.json:{occurrence_id}")
    exact["textKind"] = "verbatim"
    general_id = "SA-" + rule_id.removeprefix("SEM-") + "-GENERAL"
    general = assertion(general_id, "SRC-RULEBOOK", "printed pages 11–18, 28–29, and 33–34 / setup, Items, Heavy, Armor, Tactical Gear, Combat, Malfunction", ["timing", "preconditions", "informationPolicy", "costs", "targets", "operations", "partialResolution", "duration", "stacking"], "Resolve only the exact physical occurrence through its class-appropriate setup, storage, use/passive/Weapon trigger, finite component, Malfunction, loss, and visibility lifecycle.", "docs/rulebooks/rulebook_text.txt:lines 2692–2736,3469–3548,3657–3673,4882–5103,5576–5667")
    terms, taxa = _face_terms_and_taxa(face)
    preconditions, decisions, targets, operations = _effect_atoms(face, assertion_id, operation, decision, condition)
    preconditions.insert(0, condition(f"C-{rule_id.removeprefix('SEM-')}-OCCURRENCE", "predicate", [{"predicate": f"exact selected physical occurrence is {occurrence_id}"}], [assertion_id, general_id]))
    costs = []
    for op in operations:
        if op.get("operationType") != "pay-cost":
            if op.get("operationType") == "change-value" and not isinstance(op.get("valueChange"), dict):
                op["valueChange"] = {"amount": "source-stated", "value": "source-stated value"}
            continue
        object_text = str(op.get("objectRef") or "")
        resource = "icon.actionCard" if "Action" in object_text else "icon.ammoToken" if "Ammo" in object_text else "icon.oxygen" if "Oxygen" in object_text else "term.item"
        cost_id = f"COST-{rule_id.removeprefix('SEM-')}-{op['sequence']:02d}"
        costs.append({"costId": cost_id, "payerRef": op.get("subjectRef"), "resourceTermId": resource, "quantity": 1, "selectionDecisionRef": op.get("decisionRef"), "transition": None})
        op["objectRef"] = cost_id
    questions = _effect_questions(face)
    physical_class = face["physicalClass"]
    kind = face["effectKind"]
    passive = kind in {"combat-motion-tracker", "autoloader-belt", "tactical-armor", "heavy-armor", "biohazard-armor", "bulletproof-vest"}
    weapon = physical_class in {"ranged-weapon", "melee-weapon"}
    one_use = "ONE USE ONLY" in (face.get("typeLine") or "") or kind in {"rpg-launcher", "excluded-heavy-medkit", "excluded-heavy-oxygen", "excluded-heavy-remote-detonator"}
    if passive:
        duration_kind = "persistent-while-this-exact-physical-Item-is-equipped; triggered clauses recur only at printed timing"
        reveal_trigger = "setup/gain/equip; persistent public equipped state"
    elif weapon:
        duration_kind = "per-source-defined-Weapon-trigger within one Shoot, Burst, Melee, or pending Attack"
        reveal_trigger = "public equipped Weapon and source trigger"
    else:
        duration_kind = "instantaneous exact Item effect through class-appropriate Use/source window"
        reveal_trigger = "public equipped Item and use declaration"
    return record(
        rule_id,
        f"Exact {face.get('itemSourceClass', 'Heavy Item')} occurrence {occurrence_id}",
        "source-backed-with-open-question" if questions else "source-backed",
        "component-effect",
        "official-primary",
        "open-alternatives" if questions else "source-composed",
        [exact, general],
        terms,
        taxa,
        [],
        timing(f"TW-{rule_id.removeprefix('SEM-')}", taxa[-1], "when-triggered", "once-per-exact-source-trigger"),
        [participant("P-OWNER", "decision-owner", "tax.entity.agent.player"), participant("P-CHARACTER", "actor", "tax.entity.agent.character"), participant("P-RULES", "rules-system")],
        "mixed" if decisions or questions else "must",
        preconditions,
        decisions,
        [{"informationId": f"I-{rule_id.removeprefix('SEM-')}", "subjectRef": "exact physical face, class, owner, equipped location, source trigger, decisions, attached components, and result", "audience": "public once equipped/gained; no unrelated hidden color-deck, Backpack, hand, Objective, or source-sheet faces exposed", "revealTrigger": reveal_trigger, "secrecy": "source identity is not inferred from title, back, color, folder, GMNotes, slot art, licensed row, or aggregate count"}],
        costs,
        targets,
        operations,
        {"policy": "source-conditional-steps", "unit": "one exact physical face occurrence and one complete source trigger/selected branch", "onImpossible": "do not invent a target, owner, slot, glyph, payment, order, replacement, partial effect, or default; reusable class/lifecycle records remain separate"},
        {"kind": duration_kind},
        {"policy": "each exact physical copy remains independent; repeated title/body does not collapse identity; passive duplication/stacking remains SEM-Q-086 where source-unspecified"},
        [],
        questions,
        [],
    )


def _official_face_as_physical(row: dict) -> dict:
    effect_map = {
        "SEM-CHARACTER-ITEM-OFFICIAL-AUTOMATIC-SHOTGUN-001": "official-automatic-shotgun",
        "SEM-CHARACTER-ITEM-OFFICIAL-SONIC-GUN-001": "official-sonic-gun",
        "SEM-SUPPORT-OFFICIAL-TACTICAL-HATCHET-001": "official-tactical-hatchet",
        "SEM-HEAVY-OFFICIAL-MILITARY-TASER-001": "official-military-taser",
        "SEM-SUPPORT-OFFICIAL-HEAVY-ARMOR-001": "official-heavy-armor",
        "SEM-SUPPORT-OFFICIAL-GRENADE-LAUNCHER-001": "official-grenade-launcher",
    }
    item_source = row["itemSourceClass"]
    if item_source == "color-item-heavy-current-occurrence":
        item_source = "heavy-item-current-official"
    icons = []
    for sequence, token in enumerate(re.findall(r"\[([^\]]+)\]", row["printedBody"]), 1):
        icons.append({"occurrenceId": f"{row['officialOccurrenceId']}-I{sequence:02d}", "sequence": sequence, "sourceToken": token, "semanticReferenceId": None if token.startswith("LOCAL_ICON:") else f"icon.{token}", "mappingStatus": "official-visible-source-scoped" if not token.startswith("LOCAL_ICON:") else "literal-source-local-no-match"})
    sentences = []
    body = row["printedBody"]
    start = 0
    for sequence, text in enumerate([part for part in re.split(r"\nOR\n|(?<=[.!?])\n", body) if part], 1):
        offset = body.find(text, start)
        sentences.append({"sentenceId": f"{row['officialOccurrenceId']}-S{sequence:02d}", "sequence": sequence, "panelId": f"{row['officialOccurrenceId']}-P1", "exactText": text, "start": offset, "end": offset + len(text)})
        start = offset + len(text)
    return {
        **row,
        "sourceAuthority": "official-primary",
        "sourceVersion": f"current official rulebook visible occurrence {row['officialOccurrenceId']}",
        "sourcePath": "docs/rulebooks/Nemesis_RT_Rulebook_official.pdf",
        "sourceSha256": None,
        "itemSourceClass": item_source,
        "effectKind": effect_map[row["semanticRuleId"]],
        "upperRight": "",
        "lowerCenter": "",
        "iconOccurrences": icons,
        "sentences": sentences,
        "panels": [{"panelId": f"{row['officialOccurrenceId']}-P1", "readingOrder": 1, "role": "official-visible-component-face", "operative": True, "exactText": "\n".join([row["printedTitle"], row["typeLine"], row["printedBody"]])}],
    }


def build_equipment_records(repo: Path, source_index: dict, record, assertion, timing, participant, condition, decision, operation) -> list[dict]:
    del repo
    ids = equipment_rule_ids(source_index)
    records: list[dict] = []

    records.append(record(
        "SEM-CHARACTER-ITEM-SETUP-001", "Place each current Character Item during setup", "source-backed-with-open-question", "procedure", "official-primary", "open-alternatives",
        [assertion("SA-CI-SETUP-RB", "SRC-RULEBOOK", "printed pages 3 and 11 / RB-P03-V01 / lines 523,2692–2699", ["timing", "preconditions", "decisions", "informationPolicy", "targets", "operations", "partialResolution", "duration", "stacking", "unresolvedQuestionRefs"], "There are 7 Character Item cards. Each Character places their Character Item in a Hand if Heavy or on the Heavily Injured Health section if Armor; fill each Ammo slot with one Full Ammo token. Contractor starts with two Character Items.", "docs/rulebooks/rulebook_text.txt:lines 523,2692–2699"), assertion("SA-CI-SETUP-INDEX", "SRC-EQUIPMENT-SUPPORT-ROOT", "equipment source index / seven exact TTS kit occurrences and official-visible roster boundary", ["informationPolicy", "targets", "operations", "partialResolution", "duration", "stacking", "sourceVariants", "unresolvedQuestionRefs"], "TTS contains seven exact kit occurrences but current official page 3 overrides Automatic Shotgun ownership and rejects BF Gun; the complete current seven-card identity/owner crosswalk is not visible.", "docs/rules/semantics/equipment-source-index.json:characterItemTtsFaces/officialVisibleOccurrences")],
        ["term.character-item", "term.heavy-item", "term.armor-item", "term.hand-slot", "icon.ammoToken"], ["tax.entity.component.card.item.character", "tax.entity.component.card.item.heavy", "tax.entity.component.card.item.armor", "tax.entity.component.slot.hand", "tax.entity.component.token.tactical-gear.ammo"], [],
        timing("TW-CI-SETUP", "tax.entity.component.card.item.character", "when-triggered", "once-per-participating-Character-at-setup"), [participant("P-OWNER", "decision-owner", "tax.entity.agent.player"), participant("P-CHARACTER", "actor", "tax.entity.agent.character"), participant("P-RULES", "rules-system")], "must", [], [],
        [{"informationId": "I-CI-SETUP", "subjectRef": "current Character Item identity, source owner, physical class, equipped location, slots/tokens, and prototype/variant boundary", "audience": "public equipped state; unresolved/current source variants remain audit evidence rather than secret game state", "revealTrigger": "setup", "secrecy": "do not substitute TTS back/kit label or licensed deck label for current official ownership"}], [],
        [_target("T-CI-ITEM", ["tax.entity.component.card.item.character"], selector="P-RULES", mode="deterministic-state-filter", minimum=1, maximum=2)],
        [operation("S01", 1, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-079 complete current Character Item roster/owner/copy identity", ["SA-CI-SETUP-RB", "SA-CI-SETUP-INDEX"]), operation("S02", 2, "transition-zone", "must", "P-RULES", "each source-resolved current Heavy Character Item to one empty Hand slot", ["SA-CI-SETUP-RB"], conditions=["source-resolved current item is Heavy"], target_ref="T-CI-ITEM", transition={"from": "character kit/supply", "to": "equipped Hand slot"}), operation("S03", 3, "transition-zone", "must", "P-RULES", "each source-resolved current Armor Character Item to the Heavily Injured Health section", ["SA-CI-SETUP-RB"], conditions=["source-resolved current item is Armor"], target_ref="T-CI-ITEM", transition={"from": "character kit/supply", "to": "Armor position on Health track"}), operation("S04", 4, "place-component", "if-able", "P-RULES", "1 Full Ammo token on each source-resolved Ammo slot", ["SA-CI-SETUP-RB"], target_ref="T-CI-ITEM", repeat={"scope": "each exact source-resolved Ammo slot", "finiteSupply": True}), operation("S05", 5, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-087 loss/replacement/recovery of Character Items after setup", ["SA-CI-SETUP-RB", "SA-CI-SETUP-INDEX"], conditions=["later Character Item loss/replacement occurs"])],
        {"policy": "source-conditional-steps", "unit": "one Character and each source-resolved current Character Item", "onImpossible": "SEM-Q-079 prohibits substituting the exact TTS/BGA kit roster for unavailable current official identities; finite slot/token shortage remains explicit"}, {"kind": "setup-to-persistent-equipped-state"}, {"policy": "one source-defined Character Item per non-Contractor and two for Contractor; exact identities/copies remain source scoped"}, [], ["SEM-Q-079", "SEM-Q-087"], []))

    records.append(record(
        "SEM-SUPPORT-EQUIPMENT-DRAFT-001", "Support Equipment setup draft and remaining deck", "source-backed-with-open-question", "procedure", "official-primary", "open-alternatives",
        [assertion("SA-SE-DRAFT-RB", "SRC-RULEBOOK", "printed page 11 / lines 2702–2736", ["timing", "preconditions", "decisions", "informationPolicy", "targets", "operations", "partialResolution", "duration", "stacking", "unresolvedQuestionRefs"], "Non-Contractors shuffle the 24-card Support Equipment deck, reveal 7, choose one each from highest player number in descending order, equip by class, fill empty slots, remove unchosen revealed cards from the game, leave the deck close to the Item decks, then choose 4 Tactical Gear tokens for each Belt; simultaneous choice is allowed, otherwise descending player order.", "docs/rulebooks/rulebook_text.txt:lines 2702–2736"), assertion("SA-SE-DRAFT-TTS", "SRC-EQUIPMENT-SUPPORT-ROOT", "raw startItemDeck GUID f71196 / exact 24 full CardID/GUID members", ["informationPolicy", "targets", "operations", "partialResolution", "duration", "stacking", "sourceVariants"], "The exact TTS Support root contains 24 distinct physical occurrences and one shared non-operative back; saved order is provenance and setup shuffles.", "docs/rules/semantics/equipment-source-index.json:supportRootEvidence")],
        ["term.support-equipment", "term.heavy-item", "term.armor-item", "term.tactical-gear-token", "term.tactical-belt"], ["tax.entity.component.card.item.support", "tax.entity.component.card.item.heavy", "tax.entity.component.card.item.armor", "tax.entity.component.token.tactical-gear", "tax.entity.component.storage.tactical-belt"], [],
        timing("TW-SE-DRAFT", "tax.entity.component.card.item.support", "when-triggered", "once-during-setup-plus-source-unspecified-later-access"), [participant("P-PLAYERS", "collection", "tax.entity.agent.player"), participant("P-CHARACTERS", "collection", "tax.entity.agent.character"), participant("P-RULES", "rules-system")], "mixed", [],
        [decision("D-SE-CHOICE", "P-PLAYERS", "player-choice-sequential", 1, 1, False, "public-on-selection", ["one remaining revealed Support Equipment in exact descending player-number order"]), decision("D-SE-BELT", "P-PLAYERS", "player-choice", 4, 4, False, "public-on-placement", ["four finite Tactical Gear tokens in any combination, subject to availability/slot legality"])],
        [{"informationId": "I-SE-DRAFT", "subjectRef": "shuffled Support deck order/fronts, seven-card public draft pool, player order, selected/removed cards, equipped classes, slots, and token choices", "audience": "deck fronts/order hidden; seven drawn cards and every choice/equipped result public", "revealTrigger": "seven-card setup draw", "secrecy": "do not reveal undrawn fronts/order or infer future deck access"}], [],
        [_target("T-SE-CARD", ["tax.entity.component.card.item.support"], selector="P-PLAYERS", mode="player-choice", minimum=1, maximum=1), _target("T-SE-TOKENS", ["tax.entity.component.token.tactical-gear"], selector="P-PLAYERS", mode="player-choice", minimum=4, maximum=4)],
        [operation("S01", 1, "shuffle", "must", "P-RULES", "all 24 exact Support Equipment physical copies", ["SA-SE-DRAFT-RB", "SA-SE-DRAFT-TTS"], repeat={"physicalCardCount": 24}), operation("S02", 2, "draw-random", "must", "P-RULES", "7 Support Equipment cards face up into the public draft pool", ["SA-SE-DRAFT-RB"], repeat={"quantity": 7}), operation("S03", 3, "select-target", "must", "P-PLAYERS", "one remaining revealed card per participating non-Contractor, highest player number then descending", ["SA-SE-DRAFT-RB"], decision_ref="D-SE-CHOICE", target_ref="T-SE-CARD", repeat={"order": "descending player number", "ContractorExcluded": True}), operation("S04", 4, "transition-zone", "must", "P-RULES", "each selected Heavy card to an empty Hand or Armor card to the Heavily Injured Health section", ["SA-SE-DRAFT-RB"], target_ref="T-SE-CARD", transition={"from": "public draft pool", "to": "class-appropriate equipped position"}), operation("S05", 5, "invoke-process", "must", "P-RULES", "fill each selected Equipment's source-resolved empty Tactical Gear slots", ["SA-SE-DRAFT-RB"], invoke="SEM-EQUIPMENT-FULLY-LOADED-001"), operation("S06", 6, "transition-zone", "must", "P-RULES", "all unchosen revealed Support Equipment", ["SA-SE-DRAFT-RB"], transition={"from": "public draft pool", "to": "tax.scaffold.zone.removed-from-game"}), operation("S07", 7, "set-state", "must", "P-RULES", "remaining Support Equipment deck stays near the Item decks for source-authorized later use", ["SA-SE-DRAFT-RB"]), operation("S08", 8, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-080 later deck-access/exhaustion procedure and SEM-Q-084 finite setup token shortage/choice order", ["SA-SE-DRAFT-RB"]), operation("S09", 9, "place-component", "if-able", "P-PLAYERS", "four chosen finite Tactical Gear tokens per Character's Tactical Belt", ["SA-SE-DRAFT-RB"], decision_ref="D-SE-BELT", target_ref="T-SE-TOKENS", repeat={"quantityPerCharacter": 4, "simultaneousAllowed": True, "fallbackOrder": "descending player number"})],
        {"policy": "source-limited-components", "unit": "one setup draft choice/equipment/token placement", "onImpossible": "no support-deck replenishment, later draw mechanism, scarce Any-slot assignment, or token substitution is invented under SEM-Q-080/084"}, {"kind": "setup-draft-then-persistent-finite-deck/equipped-state"}, {"policy": "one Equipment per non-Contractor from the seven-card pool; removed and remaining cards stay distinct"}, [], ["SEM-Q-080", "SEM-Q-084"], []))

    records.append(record(
        "SEM-HEAVY-ITEM-HAND-CAPACITY-001", "Heavy Item Hand placement and capacity", "source-backed-with-open-question", "constraint", "official-primary", "open-alternatives",
        [assertion("SA-HEAVY-HAND-RB", "SRC-RULEBOOK", "printed pages 17 and 29 / lines 3657–3662,5024–5034", ["timing", "decisions", "informationPolicy", "targets", "operations", "partialResolution", "duration", "stacking", "unresolvedQuestionRefs"], "Each Character has 2 Hand slots. Every horizontal Item is Heavy; normally only 1 Heavy Item occupies one Hand. On gaining a Heavy Item with both Hands occupied, the owner may first discard one held Item. Weapons and Eggs are Heavy.", "docs/rulebooks/rulebook_text.txt:lines 3657–3662,5024–5034")],
        ["term.heavy-item", "term.hand-slot", "term.weapon"], ["tax.entity.component.card.item.heavy", "tax.entity.component.slot.hand", "tax.entity.component.card.item.weapon"], [],
        timing("TW-HEAVY-HAND", "tax.entity.component.card.item.heavy", "when-triggered", "per-Heavy-Item-gain/equip/transfer/loss"), [participant("P-OWNER", "decision-owner", "tax.entity.agent.player"), participant("P-CHARACTER", "actor", "tax.entity.agent.character"), participant("P-RULES", "rules-system")], "mixed", [],
        [decision("D-HEAVY-DISCARD", "P-OWNER", "player-choice", 0, 1, True, "public-on-discard", ["decline gain if no slot can be made", "discard one exact held Item before gaining the new Heavy Item"])],
        [{"informationId": "I-HEAVY-HAND", "subjectRef": "two Hand slots, exact occupying Items, Duct Tape/paired occupancy, proposed gain, optional discard, and resulting capacity", "audience": "public equipped state", "revealTrigger": "gain/equip/transfer", "secrecy": "does not reveal Backpack/hand-card identities"}], [],
        [_target("T-HEAVY-ITEM", ["tax.entity.component.card.item.heavy"], minimum=1, maximum=1), _target("T-HEAVY-DISCARD", ["tax.entity.component.card.item"], selector="P-OWNER", mode="player-choice", minimum=0, maximum=1)],
        [operation("S01", 1, "evaluate-condition", "must", "P-RULES", "whether one legal Hand position exists for the gained exact Heavy Item", ["SA-HEAVY-HAND-RB"], target_ref="T-HEAVY-ITEM"), operation("S02", 2, "choose", "may", "P-OWNER", "discard one exact held Item first when both ordinary Hand slots are occupied", ["SA-HEAVY-HAND-RB"], conditions=["no ordinary empty Hand slot"], decision_ref="D-HEAVY-DISCARD", target_ref="T-HEAVY-DISCARD"), operation("S03", 3, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-081 Duct Tape/Bayonet/attachment occupancy, gain legality, and discard order; SEM-Q-085 transfer capacity/consent", ["SA-HEAVY-HAND-RB"]), operation("S04", 4, "transition-zone", "if-able", "P-RULES", "gained exact Heavy Item to one source-legal Hand position", ["SA-HEAVY-HAND-RB"], conditions=["a legal position exists after source-legal optional discard and SEM-Q-081/085"], target_ref="T-HEAVY-ITEM", transition={"from": "gain/transfer source", "to": "equipped Hand position"})],
        {"policy": "all-or-nothing-selection", "unit": "one exact gained/transferred Heavy Item", "onImpossible": "do not auto-discard, stack, reroute, refuse consent, or exceed capacity; attachment exceptions remain source-specific"}, {"kind": "persistent-equipped-Hand-capacity"}, {"policy": "ordinary maximum one Heavy Item per Hand; exact source exceptions remain independent"}, [], ["SEM-Q-081", "SEM-Q-085"], []))

    records.append(record(
        "SEM-ARMOR-ITEM-LIFECYCLE-001", "Armor equip, replacement, break, and damage lifecycle", "source-backed-with-open-question", "procedure", "official-primary", "open-alternatives",
        [assertion("SA-ARMOR-RB", "SRC-RULEBOOK", "printed pages 18 and 29 / RB-P29-V02 / lines 3750–3756,5045–5057", ["timing", "decisions", "informationPolicy", "targets", "operations", "partialResolution", "duration", "stacking", "unresolvedQuestionRefs"], "Armor is placed on the Heavily Injured Health section. Only one may be worn. Before gaining replacement Armor, the owner may discard the current Armor. If already Heavily Injured, new Armor cannot be gained and is discarded. When Health would enter Armor's section, discard Armor and continue moving Health; Armor prevents no Health unless its own effect says so.", "docs/rulebooks/rulebook_text.txt:lines 3750–3756,5045–5057")],
        ["term.armor-item", "term.character-health"], ["tax.entity.component.card.item.armor", "tax.state.health", "tax.state.health.point"], [],
        timing("TW-ARMOR", "tax.entity.component.card.item.armor", "when-triggered", "per-Armor-gain/replacement/Health-entry/loss"), [participant("P-OWNER", "decision-owner", "tax.entity.agent.player"), participant("P-CHARACTER", "actor", "tax.entity.agent.character"), participant("P-RULES", "rules-system")], "mixed", [],
        [decision("D-ARMOR-REPLACE", "P-OWNER", "player-choice", 0, 1, True, "public-on-discard", ["keep current Armor and discard the gained Armor", "discard current Armor first and gain the new Armor"])],
        [{"informationId": "I-ARMOR", "subjectRef": "current/gained exact Armor, Health marker, three-space Heavily Injured section, attached Tactical Gear, optional replacement, break/discard, and remaining damage", "audience": "public", "revealTrigger": "gain/equip/damage", "secrecy": "none"}], [],
        [_target("T-ARMOR", ["tax.entity.component.card.item.armor"], selector="P-OWNER", mode="player-choice", minimum=1, maximum=1), _target("T-HEALTH", ["tax.state.health"], selector="P-RULES", mode="deterministic-state-filter", minimum=1, maximum=1)],
        [operation("S01", 1, "evaluate-condition", "must", "P-RULES", "current Armor occupancy and whether Health marker is already in Heavily Injured", ["SA-ARMOR-RB"]), operation("S02", 2, "choose", "may", "P-OWNER", "discard current Armor before gaining replacement", ["SA-ARMOR-RB"], conditions=["one Armor already worn", "Health not already Heavily Injured"], decision_ref="D-ARMOR-REPLACE", target_ref="T-ARMOR"), operation("S03", 3, "transition-zone", "if-able", "P-RULES", "new Armor to Heavily Injured Health section", ["SA-ARMOR-RB"], conditions=["no Armor remains there", "Health marker is not already Heavily Injured"], target_ref="T-ARMOR", transition={"from": "gain source", "to": "Armor position on Health track"}), operation("S04", 4, "transition-zone", "must", "P-RULES", "ungainable Armor to Item discard pile", ["SA-ARMOR-RB"], conditions=["Health marker already Heavily Injured or replacement declined"], target_ref="T-ARMOR", transition={"from": "gain source", "to": "tax.scaffold.zone.discard-pile"}), operation("S05", 5, "transition-zone", "must", "P-RULES", "worn Armor breaks and is discarded immediately before Health enters its section", ["SA-ARMOR-RB"], conditions=["Health marker would enter occupied Heavily Injured section"], target_ref="T-ARMOR", transition={"from": "Armor position on Health track", "to": "tax.scaffold.zone.discard-pile"}), operation("S06", 6, "invoke-process", "must", "P-RULES", "attached Tactical Gear loss for discarded Armor", ["SA-ARMOR-RB"], conditions=["Armor is lost/discarded as a result"], invoke="SEM-ITEM-LOSS-ATTACHED-GEAR-001"), operation("S07", 7, "change-value", "must", "P-RULES", "continue all remaining source damage after Armor breaks", ["SA-ARMOR-RB"], target_ref="T-HEALTH", value_change={"amount": "remaining source Health loss", "value": "Character Health"}), operation("S08", 8, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-082 exact simultaneous damage/break/token-loss/death order and SEM-Q-085 transfer/replacement capacity", ["SA-ARMOR-RB"], conditions=["nested/simultaneous replacement, attached tokens, or terminal Health consequence matters"])],
        {"policy": "source-conditional-steps", "unit": "one exact Armor gain/replacement or one Health-entry break", "onImpossible": "new Armor is discarded when the source forbids gain; no second Armor, hidden buffer, durability counter, or damage prevention is invented"}, {"kind": "persistent-equipped-Armor-until-discard/break/loss"}, {"policy": "at most one worn Armor; distinct source passives do not coexist unless a future source says so"}, [], ["SEM-Q-082", "SEM-Q-085"], []))

    records.append(record(
        "SEM-EQUIPMENT-FULLY-LOADED-001", "Fill source-resolved Item Tactical Gear slots", "source-backed-with-open-question", "procedure", "official-primary", "open-alternatives",
        [assertion("SA-FULLY-LOADED-RB", "SRC-RULEBOOK", "printed pages 11,16,28–29 / RB-P29-V03/RB-P29-V04 / lines 2692–2724,3485–3490,4899–4901,5058–5078", ["timing", "decisions", "informationPolicy", "targets", "operations", "partialResolution", "duration", "stacking", "unresolvedQuestionRefs"], "Items found during the game are Fully Loaded. Setup fills chosen Support Equipment slots with appropriate tokens and Character Item Ammo slots with Full Ammo. Slot type controls token compatibility; Gray is Any. Components are finite.", "docs/rulebooks/rulebook_text.txt:lines 2692–2724,3485–3490,4899–4901,5058–5078")],
        ["term.tactical-gear-slot", "term.tactical-gear-token", "term.item"], ["tax.entity.component.slot.tactical-gear", "tax.entity.component.token.tactical-gear", "tax.entity.component.card.item"], [],
        timing("TW-FULLY-LOADED", "tax.entity.component.card.item", "immediately-after-gain", "per-source-resolved Item gain/setup placement"), [participant("P-OWNER", "possible-decision-owner", "tax.entity.agent.player"), participant("P-RULES", "rules-system")], "mixed", [],
        [decision("D-ANY-SLOT-TOKEN", "P-RULES", "unresolved", 1, 1, False, "public-on-placement", ["owner chooses compatible token", "deterministic/source-defined token", "another source-defined assignment"])],
        [{"informationId": "I-FULLY-LOADED", "subjectRef": "exact printed slot occurrences/types, current token pool, compatible choices, placement order, token side, shortages, and lower-authority GMNotes/licensed evidence", "audience": "public once Item/slots/tokens are equipped; deck fronts remain hidden", "revealTrigger": "gain/setup", "secrecy": "no slot type/count inferred from color, title, art, orientation, GMNotes, BGA, or expected weapon behavior"}], [],
        [_target("T-FULLY-SLOTS", ["tax.entity.component.slot.tactical-gear"], selector="P-RULES", mode="deterministic-state-filter", minimum=0, maximum=None), _target("T-FULLY-TOKENS", ["tax.entity.component.token.tactical-gear"], selector="P-RULES", mode="unresolved-order", minimum=0, maximum=None)],
        [operation("S01", 1, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-083 exact TTS printed slot type/count where tracked pixels lack an authoritative source-scoped match", ["SA-FULLY-LOADED-RB"]), operation("S02", 2, "evaluate-condition", "must", "P-RULES", "each exact source-resolved empty compatible slot and finite matching token supply", ["SA-FULLY-LOADED-RB"], target_ref="T-FULLY-SLOTS"), operation("S03", 3, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-084 owner/order for Any slots and finite shortage across multiple Items/slots", ["SA-FULLY-LOADED-RB"], decision_ref="D-ANY-SLOT-TOKEN"), operation("S04", 4, "place-component", "if-able", "P-RULES", "one source-compatible finite Tactical Gear token in each source-resolved slot", ["SA-FULLY-LOADED-RB"], target_ref="T-FULLY-TOKENS", repeat={"scope": "each source-resolved empty slot", "finiteSupply": True, "assignmentOrder": "SEM-Q-084 unresolved"}), operation("S05", 5, "set-state", "must", "P-RULES", "Ammo placed during Character/setup loading is Full-side up", ["SA-FULLY-LOADED-RB"], conditions=["placed token is Ammo during source-specified setup loading"])],
        {"policy": "source-limited-components", "unit": "one source-resolved slot/token placement", "onImpossible": "unavailable generic components do nothing, but SEM-Q-084 retains multi-slot assignment/order and no unverified slot is created"}, {"kind": "instantaneous-gain/setup loading plus persistent attached-token state"}, {"policy": "one physical token per slot; each source-resolved slot remains distinct"}, [], ["SEM-Q-083", "SEM-Q-084"], []))

    active_rule_ids = [face["semanticRuleId"] for face in [*source_index["supportEquipmentFaces"], *source_index["colorRootHeavyFaces"]] if face["effectKind"] in {"entrenching-tool", "security-system-control", "rpg-launcher", "supporting-robot-controller", "portable-device", "engineering-equipment", "motion-tracker", "excluded-heavy-medkit", "excluded-heavy-oxygen", "excluded-heavy-remote-detonator"}]
    records.append(record(
        "SEM-HEAVY-ITEM-USE-001", "Use one active Heavy Item", "source-backed-with-open-question", "action", "official-primary", "open-alternatives",
        [assertion("SA-HEAVY-USE-RB", "SRC-RULEBOOK", "printed pages 12 and 28–29 / lines 2889,4915–4951,5024–5034", ["timing", "preconditions", "decisions", "informationPolicy", "costs", "targets", "operations", "partialResolution", "duration", "stacking", "unresolvedQuestionRefs"], "Use an Item costs 1 Action card. Most Items apply their effects only when Used, while passive Items cannot be Used this way. Heavy Items are public equipped cards in Hands; One Use Only Items are discarded when Used.", "docs/rulebooks/rulebook_text.txt:lines 2889,4915–4951,5024–5034")],
        ["term.item", "term.heavy-item", "icon.actionCard"], ["tax.entity.component.card.item", "tax.entity.component.card.item.heavy", "tax.entity.component.card.action"], [],
        timing("TW-HEAVY-USE", "tax.entity.component.card.item.heavy", "during", "per-selected-Use-an-Item-Action-or-exact-source window"), [participant("P-OWNER", "decision-owner", "tax.entity.agent.player"), participant("P-CHARACTER", "actor", "tax.entity.agent.character"), participant("P-RULES", "rules-system")], "mixed", [],
        [decision("D-HEAVY-USE-ITEM", "P-OWNER", "player-choice", 1, 1, False, "public-on-declaration", ["one exact owned active Heavy Item with a fully resolvable source effect"]), decision("D-HEAVY-USE-PAY", "P-OWNER", "player-choice", 1, 1, False, "owner-private-until-discard", ["one Action card unless an exact source waives/replaces the cost"])],
        [{"informationId": "I-HEAVY-USE", "subjectRef": "selected exact Heavy Item, public face/class, payment, targets/branches, attached components, effect, and disposition", "audience": "public selected/equipped Item and effect; unselected hand Action cards remain private", "revealTrigger": "use declaration/payment", "secrecy": "no hidden sibling/color-deck/source-sheet fronts exposed"}],
        [{"costId": "COST-HEAVY-USE", "payerRef": "P-OWNER", "resourceTermId": "icon.actionCard", "quantity": 1, "selectionDecisionRef": "D-HEAVY-USE-PAY", "transition": {"from": "tax.scaffold.zone.hand", "to": "tax.scaffold.zone.discard-pile"}}],
        [_target("T-HEAVY-USE-ITEM", ["tax.entity.component.card.item.heavy"], selector="P-OWNER", mode="player-choice", minimum=1, maximum=1)],
        [operation("S01", 1, "select-target", "must", "P-OWNER", "one exact active Heavy Item; exclude passive-only Armor/Items and Weapon trigger text", ["SA-HEAVY-USE-RB"], decision_ref="D-HEAVY-USE-ITEM", target_ref="T-HEAVY-USE-ITEM"), operation("S02", 2, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-039/096 declaration, payment, effect, Item discard/remove, and attached-token order", ["SA-HEAVY-USE-RB"], target_ref="T-HEAVY-USE-ITEM"), operation("S03", 3, "pay-cost", "must", "P-OWNER", "COST-HEAVY-USE", ["SA-HEAVY-USE-RB"], conditions=["ordinary Use an Item Action and payment point reached under SEM-Q-039/096"], decision_ref="D-HEAVY-USE-PAY"), operation("S04", 4, "invoke-selected-process", "must", "P-CHARACTER", "exact occurrence-specific active Heavy Item effect", ["SA-HEAVY-USE-RB"], conditions=["source conditions/costs complete under SEM-Q-039/096"], target_ref="T-HEAVY-USE-ITEM", notes="Dispatch uses exact full root/kit/official occurrence identity, never title, class label, back, color, folder, GMNotes, cell, modulo, BGA, or aggregate multiplicity."), operation("S05", 5, "invoke-process", "if-able", "P-RULES", "One Use Only Heavy Item lifecycle", ["SA-HEAVY-USE-RB"], conditions=["selected exact face is One Use Only"], invoke="SEM-HEAVY-ITEM-ONE-USE-001")],
        {"policy": "all-or-nothing-selection", "unit": "one exact active Heavy Item and one complete branch", "onImpossible": "passive-only Items cannot be Used; no partial target/cost/effect/disposition default under SEM-Q-039/096"}, {"kind": "instantaneous-basic-action-or-exact-source window"}, {"policy": "one selected physical copy per invocation"}, [], ["SEM-Q-039", "SEM-Q-096"], []))
    records[-1]["operations"][3]["dispatchRuleIds"] = active_rule_ids

    records.append(record(
        "SEM-HEAVY-ITEM-ONE-USE-001", "One Use Only Heavy Item disposition", "source-backed-with-open-question", "procedure", "official-primary", "open-alternatives",
        [assertion("SA-HEAVY-ONE-USE-RB", "SRC-RULEBOOK", "printed page 29 / lines 4933–4948", ["timing", "informationPolicy", "operations", "partialResolution", "duration", "stacking", "unresolvedQuestionRefs"], "One Use Only Items are discarded when Used.", "docs/rulebooks/rulebook_text.txt:lines 4933–4948")],
        ["term.item", "term.heavy-item"], ["tax.entity.component.card.item", "tax.entity.component.card.item.heavy"], [],
        timing("TW-HEAVY-ONE-USE", "tax.entity.component.card.item.heavy", "when-triggered", "once-when-this-exact-physical-Item-is-Used"), [participant("P-OWNER", "controller", "tax.entity.agent.player"), participant("P-RULES", "rules-system")], "must", [], [],
        [{"informationId": "I-HEAVY-ONE-USE", "subjectRef": "used exact physical Item, attached tokens, effect, discard/remove destination, and same-title copies", "audience": "public", "revealTrigger": "use/disposition", "secrecy": "same-title siblings/source variants remain distinct"}], [],
        [_target("T-HEAVY-ONE-USE", ["tax.entity.component.card.item.heavy"], minimum=1, maximum=1)],
        [operation("S01", 1, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-039/096 exact payment/effect/discard order and explicit remove-from-game text precedence", ["SA-HEAVY-ONE-USE-RB"], target_ref="T-HEAVY-ONE-USE"), operation("S02", 2, "invoke-process", "must", "P-RULES", "attached Tactical Gear loss before/with Item disposition at source-defined point", ["SA-HEAVY-ONE-USE-RB"], target_ref="T-HEAVY-ONE-USE", invoke="SEM-ITEM-LOSS-ATTACHED-GEAR-001"), operation("S03", 3, "transition-zone", "must", "P-RULES", "used exact One Use Only Heavy Item", ["SA-HEAVY-ONE-USE-RB"], conditions=["source-defined disposition point reached", "face does not explicitly say remove this Item from the game"], target_ref="T-HEAVY-ONE-USE", transition={"from": "equipped Hand/card-in-resolution", "to": "tax.scaffold.zone.discard-pile"}), operation("S04", 4, "transition-zone", "must", "P-RULES", "exact Item with explicit remove-this-Item text", ["SA-HEAVY-ONE-USE-RB"], conditions=["exact face explicitly requires remove from game"], target_ref="T-HEAVY-ONE-USE", transition={"from": "equipped Hand/card-in-resolution", "to": "tax.scaffold.zone.removed-from-game"})],
        {"policy": "source-conditional-steps", "unit": "one exact used physical One Use Only Item", "onImpossible": "never discard/remove another copy or substitute a same-title variant; timing remains SEM-Q-039/096"}, {"kind": "instantaneous-disposition-ending-that-copy's-availability"}, {"policy": "one physical copy per completed use"}, [], ["SEM-Q-039", "SEM-Q-096"], []))

    records.append(record(
        "SEM-ITEM-PASSIVE-EFFECT-001", "Public equipped Item passive effects", "source-backed-with-open-question", "constraint", "official-primary", "open-alternatives",
        [assertion("SA-PASSIVE-RB", "SRC-RULEBOOK", "printed page 28 / lines 4915–4923", ["timing", "informationPolicy", "operations", "duration", "stacking", "unresolvedQuestionRefs"], "Items with passive effects apply when the timing on the card calls for it and may never be used by performing the Use an Item Basic Action.", "docs/rulebooks/rulebook_text.txt:lines 4915–4923")],
        ["term.item"], ["tax.entity.component.card.item"], [],
        timing("TW-ITEM-PASSIVE", "tax.entity.component.card.item", "when-triggered", "each exact printed passive timing while equipped/owned"), [participant("P-OWNER", "controller", "tax.entity.agent.player"), participant("P-CHARACTER", "affected", "tax.entity.agent.character"), participant("P-RULES", "rules-system")], "must", [], [],
        [{"informationId": "I-ITEM-PASSIVE", "subjectRef": "equipped public Item identity, exact passive text/timing, owner, affected event, duplicates, activation/suppression, and result", "audience": "public equipped state", "revealTrigger": "setup/gain/equip and each trigger", "secrecy": "does not reveal unrelated private cards"}], [], [],
        [operation("S01", 1, "prohibit", "must", "P-RULES", "selecting a passive-only Item for the Use an Item Basic Action", ["SA-PASSIVE-RB"]), operation("S02", 2, "evaluate-condition", "must", "P-RULES", "each equipped exact Item's printed passive trigger", ["SA-PASSIVE-RB"]), operation("S03", 3, "invoke-selected-process", "must", "P-RULES", "exact occurrence-specific passive effect when its trigger is met", ["SA-PASSIVE-RB"]), operation("S04", 4, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-086 visibility before trigger, duplicate/passive stacking, simultaneous trigger order, Malfunction suppression, and duration", ["SA-PASSIVE-RB"], conditions=["more than one passive/trigger or source visibility/suppression is material"])],
        {"policy": "per-effect-check", "unit": "one exact passive trigger occurrence", "onImpossible": "do not Use, conceal equipped public state, stack/cancel duplicates, or choose trigger order without source support"}, {"kind": "persistent-while-exact-Item-remains-source-legally-equipped/owned"}, {"policy": "same-title/source duplicates remain distinct; interaction remains SEM-Q-086"}, [], ["SEM-Q-086"], []))

    records.append(record(
        "SEM-ITEM-LOSS-ATTACHED-GEAR-001", "Item loss and attached Tactical Gear", "source-backed-with-open-question", "procedure", "official-primary", "open-alternatives",
        [assertion("SA-ITEM-LOSS-RB", "SRC-RULEBOOK", "printed pages 17–18 and 29 / lines 3665–3673,3760–3763,5074–5078", ["timing", "decisions", "informationPolicy", "targets", "operations", "partialResolution", "duration", "stacking", "unresolvedQuestionRefs"], "Losing an Item also loses all Tactical Gear tokens from it. Voluntarily discarded Items go to the Item discard pile and tokens return to the pool. On death, all carried Items are lost, but their exact destination and starting-item replacement/recovery are not stated.", "docs/rulebooks/rulebook_text.txt:lines 3665–3673,3760–3763,5074–5078")],
        ["term.item", "term.tactical-gear-token"], ["tax.entity.component.card.item", "tax.entity.component.token.tactical-gear"], [],
        timing("TW-ITEM-LOSS", "tax.entity.component.card.item", "when-triggered", "per-exact-Item discard/loss/destruction/death"), [participant("P-OWNER", "controller", "tax.entity.agent.player"), participant("P-CHARACTER", "affected", "tax.entity.agent.character"), participant("P-RULES", "rules-system")], "must", [], [],
        [{"informationId": "I-ITEM-LOSS", "subjectRef": "lost/discarded exact Item, cause, attached tokens, source/destination, owner participation/death/escape state, and starting-item identity", "audience": "public equipped Item/loss result; unrelated private cards remain hidden", "revealTrigger": "loss/discard/death", "secrecy": "no hidden replacement/return is inferred"}], [],
        [_target("T-LOST-ITEM", ["tax.entity.component.card.item"], minimum=1, maximum=1), _target("T-ATTACHED-GEAR", ["tax.entity.component.token.tactical-gear"], selector="P-RULES", mode="deterministic-state-filter", minimum=0, maximum=None)],
        [operation("S01", 1, "remove-component", "must", "P-RULES", "all Tactical Gear tokens physically attached to the exact lost Item", ["SA-ITEM-LOSS-RB"], target_ref="T-ATTACHED-GEAR", repeat={"scope": "all attached tokens"}), operation("S02", 2, "transition-zone", "must", "P-RULES", "discarded attached tokens to finite component pool", ["SA-ITEM-LOSS-RB"], conditions=["tokens are discarded/lost under ordinary token discard rules"], target_ref="T-ATTACHED-GEAR", transition={"from": "Item slots", "to": "finite component pool"}), operation("S03", 3, "transition-zone", "must", "P-RULES", "voluntarily/One-Use/broken exact Item to Item discard pile unless source says remove", ["SA-ITEM-LOSS-RB"], conditions=["ordinary Item discard"], target_ref="T-LOST-ITEM", transition={"from": "class-appropriate equipped storage", "to": "tax.scaffold.zone.discard-pile"}), operation("S04", 4, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-082 attached-token versus Armor break/damage order, SEM-Q-087 death/escape/lost destination and Starting Item replacement/recovery, and SEM-Q-089 Weapon destruction/repair token order", ["SA-ITEM-LOSS-RB"], conditions=["cause is death, destruction, Armor break, escape, or Starting Item loss"]), operation("S05", 5, "evaluate-condition", "must", "P-RULES", "a dead Character loses every carried Item and no longer participates; no checked source says Escaping/Hibernating loses equipped Items", ["SA-ITEM-LOSS-RB"])],
        {"policy": "per-selected-component", "unit": "one exact lost Item and each attached token", "onImpossible": "do not preserve, duplicate, transfer, replace, return, or expose other Items without a source rule"}, {"kind": "instantaneous-loss/disposition ending exact Item/passive availability"}, {"policy": "each physical Item/token transitions independently"}, [], ["SEM-Q-082", "SEM-Q-087", "SEM-Q-089"], []))

    records.append(record(
        "SEM-WEAPON-MALFUNCTION-LIFECYCLE-001", "Weapon Malfunction, Ammo eligibility, and destruction", "source-backed-with-open-question", "procedure", "official-errata", "open-alternatives",
        [assertion("SA-WEAPON-MAL-RB", "SRC-RULEBOOK", "printed pages 17,33–34 / lines 3537–3548,5576–5587,5606–5611,5661–5667", ["timing", "preconditions", "decisions", "informationPolicy", "targets", "operations", "partialResolution", "duration", "stacking", "unresolvedQuestionRefs"], "Shoot requires a working loaded Ranged Weapon without Malfunction. During Melee response, a Character may place Malfunction on any Weapon to Prevent; placing one on a Weapon already malfunctioning destroys it. Full Ammo flips Half-full; Half-full is discarded.", "docs/rulebooks/rulebook_text.txt:lines 5576–5611,5661–5667"), assertion("SA-WEAPON-MAL-FAQ-NOAMMO", "SRC-FAQ", "Items and Tactical Gear / FQ-P03-U01", ["preconditions", "operations"], "A Requires no Ammo Weapon may spend Ammo for an effect.", "docs/rules/source-extraction/faq-v1.2-source-extraction.json:FQ-P03-U01"), assertion("SA-WEAPON-MAL-FAQ", "SRC-FAQ", "Items and Tactical Gear / FQ-P03-U02", ["preconditions", "operations", "unresolvedQuestionRefs"], "Ammo cannot be spent from a malfunctioning Weapon for other effects.", "docs/rules/source-extraction/faq-v1.2-source-extraction.json:FQ-P03-U02")],
        ["term.weapon", "icon.malfunction", "icon.ammoToken"], ["tax.entity.component.card.item.weapon", "tax.entity.component.marker.malfunction", "tax.entity.component.token.tactical-gear.ammo"], [],
        timing("TW-WEAPON-MAL", "tax.entity.component.card.item.weapon", "when-triggered", "per-Weapon selection/Malfunction placement/Ammo spend/destruction/repair"), [participant("P-OWNER", "decision-owner", "tax.entity.agent.player"), participant("P-CHARACTER", "actor", "tax.entity.agent.character"), participant("P-RULES", "rules-system")], "mixed", [],
        [decision("D-WEAPON-MELEE-PREVENT", "P-OWNER", "player-choice", 0, 1, True, "public-on-placement", ["resolve Intruder Attack", "place a Malfunction on one owned Weapon to Prevent"])],
        [{"informationId": "I-WEAPON-MAL", "subjectRef": "exact Weapon, class, Malfunction state/count, loaded Ammo/Requires-no-Ammo state, selected effect, pending Attack, attached tokens, destruction/repair/loss result", "audience": "public", "revealTrigger": "equip/use/placement/spend/destruction", "secrecy": "none"}], [],
        [_target("T-WEAPON", ["tax.entity.component.card.item.weapon"], selector="P-OWNER", mode="player-choice", minimum=1, maximum=1)],
        [operation("S01", 1, "evaluate-condition", "must", "P-RULES", "Shoot selection requires Ranged Weapon, no Malfunction, and at least one loaded Ammo token unless Requires no Ammo", ["SA-WEAPON-MAL-RB", "SA-WEAPON-MAL-FAQ-NOAMMO"], target_ref="T-WEAPON"), operation("S02", 2, "prohibit", "must", "P-RULES", "spending Ammo from a malfunctioning Weapon for other effects", ["SA-WEAPON-MAL-FAQ"], target_ref="T-WEAPON"), operation("S03", 3, "permit", "must", "P-RULES", "source-instructed Ammo spend from Requires no Ammo Weapon subject to all other legality", ["SA-WEAPON-MAL-FAQ-NOAMMO"], target_ref="T-WEAPON"), operation("S04", 4, "choose", "may", "P-OWNER", "place a Malfunction on one owned Weapon to Prevent an Intruder response after failed Melee", ["SA-WEAPON-MAL-RB"], decision_ref="D-WEAPON-MELEE-PREVENT", target_ref="T-WEAPON"), operation("S05", 5, "place-component", "if-able", "P-RULES", "first Malfunction marker on selected Weapon", ["SA-WEAPON-MAL-RB"], conditions=["selected Weapon has no Malfunction"], target_ref="T-WEAPON"), operation("S06", 6, "invoke-process", "must", "P-RULES", "destroy/loss lifecycle instead of retaining a second Malfunction", ["SA-WEAPON-MAL-RB"], conditions=["Malfunction would be placed on a Weapon already having one"], target_ref="T-WEAPON", invoke="SEM-ITEM-LOSS-ATTACHED-GEAR-001"), operation("S07", 7, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-088 exact Weapon-trigger order and SEM-Q-089 destruction destination, repair scope, attached-token return, pending-effect continuation, and simultaneous second placement", ["SA-WEAPON-MAL-RB", "SA-WEAPON-MAL-FAQ"])],
        {"policy": "source-conditional-steps", "unit": "one exact Weapon selection/spend/Malfunction placement", "onImpossible": "do not use/spend from malfunctioning Weapon except exact FAQ Grenade-token carveout; no repair/destruction/token order default"}, {"kind": "persistent-public Malfunction/loaded-token state until repaired/destroyed/lost"}, {"policy": "one Malfunction disables; a second placement destroys rather than stacks"}, [], ["SEM-Q-088", "SEM-Q-089"], []))

    records.append(record(
        "SEM-WEAPON-DIE-RESULT-ADDITION-001", "FAQ Weapon die-result effects are additional unless they say instead", "source-backed-with-open-question", "procedure", "official-errata", "open-alternatives",
        [assertion("SA-WEAPON-DIE-FAQ", "SRC-FAQ", "Items and Tactical Gear / FQ-P02-U21 / visual occurrences I01–I03", ["timing", "preconditions", "decisions", "informationPolicy", "targets", "operations", "partialResolution", "duration", "stacking", "unresolvedQuestionRefs"], "Unless a Weapon specifically says instead, its effect for a specific die result resolves in addition to the standard result. A Shoot Ammo-loss result still spends Ammo even if the Weapon adds an instruction resolving another printed result.", "docs/rules/source-extraction/faq-v1.2-source-extraction.json:FQ-P02-U21")],
        ["term.weapon", "icon.shootDieAmmoLoss", "icon.shootDieCritical"], ["tax.entity.component.card.item.weapon"], [],
        timing("TW-WEAPON-DIE", "tax.entity.component.card.item.weapon", "when-triggered", "per-specific-die-result Weapon effect"), [participant("P-OWNER", "controller", "tax.entity.agent.player"), participant("P-CHARACTER", "actor", "tax.entity.agent.character"), participant("P-RULES", "rules-system")], "must", [], [],
        [{"informationId": "I-WEAPON-DIE", "subjectRef": "exact die face, standard result, exact Weapon instruction, explicit instead word if any, Ammo state/spend, added result, and order", "audience": "public", "revealTrigger": "die roll", "secrecy": "none"}], [], [],
        [operation("S01", 1, "evaluate-condition", "must", "P-RULES", "whether the exact Weapon instruction explicitly says instead", ["SA-WEAPON-DIE-FAQ"]), operation("S02", 2, "invoke-process", "must", "P-RULES", "standard die result including Ammo spend when required", ["SA-WEAPON-DIE-FAQ"], conditions=["instruction does not specifically say instead"]), operation("S03", 3, "invoke-selected-process", "must", "P-RULES", "exact occurrence-specific Weapon result effect in addition", ["SA-WEAPON-DIE-FAQ"], conditions=["instruction does not specifically say instead"]), operation("S04", 4, "replace-target", "must", "P-RULES", "exact standard result with the source-stated replacement only", ["SA-WEAPON-DIE-FAQ"], conditions=["instruction specifically says instead"]), operation("S05", 5, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-088 exact relative timing/allocation when standard and added operations affect death, Ammo, Malfunction, targets, or continuation", ["SA-WEAPON-DIE-FAQ"], conditions=["relative order materially changes legality/outcome"])],
        {"policy": "source-conditional-steps", "unit": "one exact rolled die result and one exact Weapon instruction", "onImpossible": "FAQ settles additional-versus-replacement only; it does not identify unrelated local glyphs, owners, targets, or every nested operation order"}, {"kind": "one-die-result resolution"}, {"policy": "each applicable exact Weapon instruction resolves once for that result"}, [], ["SEM-Q-088"], []))

    records.append(record(
        "SEM-GRENADE-LAUNCHER-MALFUNCTION-001", "FAQ Grenade tokens remain usable from malfunctioning Grenade Launcher via Tactical Gear Action", "source-backed-with-open-question", "constraint", "official-errata", "open-alternatives",
        [assertion("SA-GL-FAQ", "SRC-FAQ", "Items and Tactical Gear / FQ-P03-U03", ["timing", "preconditions", "informationPolicy", "targets", "operations", "partialResolution", "duration", "stacking", "unresolvedQuestionRefs"], "Grenades can be thrown from a malfunctioning Grenade Launcher with the Use Any Tactical Gear Action because any tokens on any Items may be used by that Action.", "docs/rules/source-extraction/faq-v1.2-source-extraction.json:FQ-P03-U03"), assertion("SA-GL-FAQ-AMMO", "SRC-FAQ", "Items and Tactical Gear / FQ-P03-U02", ["preconditions", "operations", "unresolvedQuestionRefs"], "Ammo cannot be spent from a malfunctioning Weapon for other effects.", "docs/rules/source-extraction/faq-v1.2-source-extraction.json:FQ-P03-U02")],
        ["term.ranged-weapon", "icon.grenadeToken", "icon.malfunction"], ["tax.entity.component.card.item.weapon.ranged", "tax.entity.component.token.tactical-gear.grenade", "tax.entity.component.marker.malfunction"], [],
        timing("TW-GL-FAQ", "tax.entity.component.card.item.weapon.ranged", "when-triggered", "per-Grenade-token selection through Use Any Tactical Gear"), [participant("P-OWNER", "decision-owner", "tax.entity.agent.player"), participant("P-CHARACTER", "actor", "tax.entity.agent.character"), participant("P-RULES", "rules-system")], "may", [], [],
        [{"informationId": "I-GL-FAQ", "subjectRef": "exact malfunctioning Item, attached Grenade tokens, chosen token, Tactical Gear Action, token effect, Ammo/Weapon state, and result", "audience": "public", "revealTrigger": "token use", "secrecy": "none"}], [],
        [_target("T-GL-GRENADE", ["tax.entity.component.token.tactical-gear.grenade"], selector="P-OWNER", mode="player-choice", minimum=0, maximum=None)],
        [operation("S01", 1, "permit", "may", "P-OWNER", "select Grenade tokens physically on a malfunctioning Grenade Launcher through Use Any Tactical Gear", ["SA-GL-FAQ"], target_ref="T-GL-GRENADE"), operation("S02", 2, "invoke-process", "if-able", "P-CHARACTER", "each selected Grenade-token effect", ["SA-GL-FAQ"], target_ref="T-GL-GRENADE", invoke="SEM-GRENADE-TOKEN-EFFECT-001", repeat={"scope": "each selected token one by one"}), operation("S03", 3, "prohibit", "must", "P-RULES", "generalizing this carveout to Shoot/Burst with the malfunctioning Weapon, Ammo spend from it, repair, or other tokens/effects", ["SA-GL-FAQ", "SA-GL-FAQ-AMMO"]), operation("S04", 4, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-090 before/instead normal Burst timing, any-number selection, token order, attached-slot identity, and interaction with direct/official variants", ["SA-GL-FAQ"])],
        {"policy": "source-conditional-steps", "unit": "one exact attached Grenade token used through Tactical Gear Action", "onImpossible": "FAQ authorizes only this token-use proposition; no wider malfunction bypass or variant correspondence"}, {"kind": "exact FAQ exception while token/Item state persists"}, {"policy": "each token selected/resolved separately under existing finite lifecycle"}, [], ["SEM-Q-090"], []))

    records.append(record(
        "SEM-EQUIPMENT-OCCURRENCE-DISPATCH-001", "Exact Heavy/Equipment/Character Item occurrence dispatcher", "source-backed-with-open-question", "dispatcher", "official-primary", "open-alternatives",
        [assertion("SA-EQUIP-DISPATCH", "SRC-EQUIPMENT-SUPPORT-ROOT", "equipment source index / exact included root, kit-variant, color-Heavy, and official occurrence tuples", ["timing", "informationPolicy", "targets", "operations", "partialResolution", "duration", "stacking", "unresolvedQuestionRefs", "sourceVariants"], "Thirty-nine source-clear TTS physical occurrences and six current official-visible occurrences retain distinct occurrence identities. Twelve Red/Yellow class conflicts and two audited prototypes do not enter effect dispatch.", "docs/rules/semantics/equipment-source-index.json"), assertion("SA-EQUIP-DISPATCH-RB", "SRC-RULEBOOK", "printed pages 28–29 / Item class and effect rules", ["operations", "duration", "stacking"], "Most Items resolve only at their exact Use/passive/Weapon trigger; physical class determines storage, not effect identity.", "docs/rulebooks/rulebook_text.txt:lines 4915–4951,5024–5057")],
        ["term.item", "term.heavy-item", "term.armor-item", "term.character-item", "term.support-equipment"], ["tax.entity.component.card.item", "tax.entity.component.card.item.heavy", "tax.entity.component.card.item.armor", "tax.entity.component.card.item.character", "tax.entity.component.card.item.support"], [],
        timing("TW-EQUIP-DISPATCH", "tax.entity.component.card.item", "when-triggered", "per-exact-source-defined Item trigger"), [participant("P-RULES", "rules-system"), participant("P-OWNER", "controller", "tax.entity.agent.player"), participant("P-CHARACTER", "actor", "tax.entity.agent.character")], "must", [], [],
        [{"informationId": "I-EQUIP-DISPATCH", "subjectRef": "exact occurrence selector, source authority/version, physical class, trigger, face/back, owner, and dispatched rule", "audience": "public once source Item is equipped/used; hidden source deck/order remains protected", "revealTrigger": "source trigger", "secrecy": "no title/body/back/color/folder/GMNotes/cell/modulo/licensed/aggregate dispatch"}], [], [],
        [operation("S01", 1, "evaluate-condition", "must", "P-RULES", "exact source occurrence and authority/applicability tuple", ["SA-EQUIP-DISPATCH", "SA-EQUIP-DISPATCH-RB"]), operation("S02", 2, "prohibit", "must", "P-RULES", "dispatch for BF Gun, obsolete TTS Automatic Shotgun, six Red Military Taser conflicts, six Yellow class conflicts, parent sheet, backs, placeholders, or selector gaps", ["SA-EQUIP-DISPATCH"]), operation("S03", 3, "invoke-selected-process", "must", "P-RULES", "one exact occurrence-specific semantic rule", ["SA-EQUIP-DISPATCH", "SA-EQUIP-DISPATCH-RB"]), operation("S04", 4, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-092–095 exact Robot/Room/target/allocation/Hazard/area-effect boundaries where the selected face is affected", ["SA-EQUIP-DISPATCH"], conditions=["selected face references an unresolved procedure"])],
        {"policy": "per-effect-check", "unit": "one exact occurrence and source trigger", "onImpossible": "class/source-conflict and prototype occurrences remain non-dispatchable; no fallback variant"}, {"kind": "occurrence-dispatch-only; lifecycle remains in reusable records"}, {"policy": "one exact occurrence dispatches one exact rule; matching text never merges copies"}, [], ["SEM-Q-092", "SEM-Q-093", "SEM-Q-094", "SEM-Q-095"], []))
    records[-1]["operations"][2]["dispatchRuleIds"] = ids["allFaces"]

    # Source variants remain one audit record rather than being mistaken for
    # physical/effect dispatch. Every selected gap/prototype/class conflict/BGA
    # row/back is retained explicitly.
    variant_assertions = [
        assertion("SA-EQUIP-VARIANT-TTS", "SRC-EQUIPMENT-SUPPORT-ROOT", "equipment source index / root, sheet, kit, back, color-Heavy, and class-conflict projections", ["operations", "sourceVariants", "unresolvedQuestionRefs"], "All exact source occurrences, selector gaps, prototype/current conflicts, and non-operative backs remain independent.", "docs/rules/semantics/equipment-source-index.json"),
        assertion("SA-EQUIP-VARIANT-BGA", BGA_EQUIPMENT_SOURCE_ID, "ITEMS_DATA / 37 relevant rows in immutable source order", ["operations", "sourceVariants", "unresolvedQuestionRefs"], "\n".join(row["sourceBlockText"] for row in source_index["licensedDigitalOccurrences"]), "docs/rules/semantics/equipment-source-index.json:licensedDigitalOccurrences"),
        assertion("SA-EQUIP-VARIANT-RB", "SRC-RULEBOOK", "RB-P03-V01/RB-P29-V01–V04 and setup/item text", ["operations", "sourceVariants", "unresolvedQuestionRefs"], "Current official visible occurrences control only their exact publisher faces and general procedures; they identify no TTS GUID copy except by explicit documented source audit, and the current seven-card Character roster remains only partly visible.", "docs/rules/semantics/equipment-source-index.json:officialVisibleOccurrences"),
    ]
    for row in variant_assertions:
        row["textKind"] = "verbatim" if row["assertionId"] == "SA-EQUIP-VARIANT-BGA" else "normalized-paraphrase"
    variant_operations = []
    variants = []
    for asset in source_index["supportSourceFaceAssets"]:
        if not asset.get("selectorGap"):
            continue
        variant_id = f"SV-EQUIP-GAP-29-{asset['generatedCell']:02d}"
        variant_operations.append(operation(f"S{len(variant_operations)+1:02d}", len(variant_operations)+1, "preserve-identity", "must", "P-RULES", f"Support sheet cell {asset['generatedCell']} selector-gap source tuple {asset['sourcePath']}", ["SA-EQUIP-VARIANT-TTS"]))
        variants.append({"variantId": variant_id, "sourceId": asset["sourceId"], "sourceAssertionId": "SA-EQUIP-VARIANT-TTS", "difference": f"Cell {asset['generatedCell']} has no exact Support-root full CardID/GUID selector.", "resolution": "Preserve as source variant; never repair by title, body, cell, modulo, or licensed row."})
    for face in source_index["characterItemTtsFaces"]:
        if face.get("semanticRuleId"):
            continue
        variant_operations.append(operation(f"S{len(variant_operations)+1:02d}", len(variant_operations)+1, "prohibit", "must", "P-RULES", f"prototype/current-conflict Character Item dispatch: {face['characterItemOccurrenceId']}", ["SA-EQUIP-VARIANT-TTS"]))
        variants.append({"variantId": f"SV-EQUIP-PROTOTYPE-{face['ttsCardGuid'].upper()}", "sourceId": face["sourceId"], "sourceAssertionId": "SA-EQUIP-VARIANT-TTS", "difference": face["batchDisposition"], "resolution": "Retain exact TTS face/back/kit provenance; exclude from current effect dispatch."})
    for face in source_index["physicalClassConflictExclusions"]:
        variant_operations.append(operation(f"S{len(variant_operations)+1:02d}", len(variant_operations)+1, "prohibit", "must", "P-RULES", f"Heavy/Equipment semantic dispatch for unresolved class occurrence {face.get('redItemOccurrenceId') or face.get('yellowItemOccurrenceId')}", ["SA-EQUIP-VARIANT-TTS"]))
        variants.append({"variantId": f"SV-EQUIP-CLASS-CONFLICT-{len(variants)+1:02d}", "sourceId": face["sourceId"], "sourceAssertionId": "SA-EQUIP-VARIANT-TTS", "difference": face["physicalClass"], "resolution": f"Remain non-dispatchable under {face['questionId']}; no licensed/current class rewrite."})
    for row in source_index["licensedDigitalOccurrences"]:
        variant_operations.append(operation(f"S{len(variant_operations)+1:02d}", len(variant_operations)+1, "preserve-identity", "must", "P-RULES", f"licensed ITEMS_DATA.{row['key']} name={row['name']!r}, deck={row['deck']!r}, class={(row['heavy'], row['armor'], row['rangedWeapon'], row['meleeWeapon'])}, nbr={row['nbr']}, slots={row['slots']!r}, effect={row['effectDesc']!r}", ["SA-EQUIP-VARIANT-BGA"]))
        variants.append({"variantId": f"SV-EQUIP-BGA-{row['key'].upper()}", "sourceId": BGA_EQUIPMENT_SOURCE_ID, "sourceAssertionId": "SA-EQUIP-VARIANT-BGA", "difference": "Independent licensed title/deck/class/multiplicity/slots/effect tuple with no physical TTS or official identity selector.", "resolution": "Retain below official/source-bound authority; aggregate reconciliation is not a copy crosswalk."})
    for back in source_index["sharedBacks"]:
        variant_operations.append(operation(f"S{len(variant_operations)+1:02d}", len(variant_operations)+1, "preserve-identity", "must", "P-RULES", f"non-operative BackURL {back['sourcePath']} with {back.get('globalReferenceCount')} global references", ["SA-EQUIP-VARIANT-TTS"]))
        variants.append({"variantId": f"SV-EQUIP-BACK-{back['sourceId'].removeprefix('SRC-')}", "sourceId": back["sourceId"], "sourceAssertionId": "SA-EQUIP-VARIANT-TTS", "difference": back["sideRole"], "resolution": "Back is provenance/information side only; never a rules face or ownership/class selector."})
    variant_operations.append(operation(f"S{len(variant_operations)+1:02d}", len(variant_operations)+1, "prohibit", "must", "P-RULES", "title/body/color/orientation/GMNotes/folder/order/sheet/cell/CardID-modulo/licensed-key/multiplicity/current-title inference or variant flattening", [row["assertionId"] for row in variant_assertions]))
    records.append(record(
        "SEM-EQUIPMENT-VARIANT-BOUNDARIES-001", "Heavy/Equipment/Starting source, class, slot, face/back, and variant boundaries", "source-variant", "constraint", "official-primary", "open-alternatives",
        variant_assertions,
        ["term.item", "term.heavy-item", "term.armor-item", "term.character-item", "term.support-equipment", "term.tactical-gear-slot"], ["tax.entity.component.card.item", "tax.entity.component.card.item.heavy", "tax.entity.component.card.item.armor", "tax.entity.component.card.item.character", "tax.entity.component.card.item.support", "tax.entity.component.slot.tactical-gear"], [],
        timing("TW-EQUIP-VARIANTS", "tax.entity.component.card.item", "when-triggered", "per-source-comparison/canonicalization/dispatch attempt"), [participant("P-RULES", "rules-system")], "must", [], [],
        [{"informationId": "I-EQUIP-VARIANTS", "subjectRef": "24 Support physical faces, 40 Support source assets, 16 gaps, 7 TTS Character faces, 2 prototype exclusions, 10 color Heavy faces, 12 class conflicts, 6 official faces, 37 licensed rows, slots/tracks, parent sheet, and 6 backs", "audience": "public source evidence; live deck/order/privacy remains governed separately", "revealTrigger": "source audit", "secrecy": "no hidden source order/private card exposure"}], [], [], variant_operations,
        {"policy": "per-proposed-source-merge", "unit": "one proposed identity/class/effect/slot/back merge", "onImpossible": "without exact source-backed correspondence preserve each occurrence and defaultProhibited alternatives"}, {"kind": "persistent-source-audit-boundary"}, {"policy": "variants do not identify, replace, dispatch, stack, or inherit fields from one another"}, [], [], variants))

    physical_faces = [
        *source_index["supportEquipmentFaces"],
        *[row for row in source_index["characterItemTtsFaces"] if row.get("semanticRuleId")],
        *source_index["colorRootHeavyFaces"],
    ]
    records.extend(_build_physical_face_record(face, record, assertion, timing, participant, condition, decision, operation) for face in physical_faces)
    records.extend(_build_physical_face_record(_official_face_as_physical(row), record, assertion, timing, participant, condition, decision, operation) for row in source_index["officialVisibleOccurrences"])
    return records


def integrate_equipment_shared_records(records: list[dict], source_index: dict, assertion, operation) -> None:
    # Existing generic Item records remain byte-stable. Equipment-specific
    # records carry their own capacity, transfer, and attached-token links.
    del records, source_index, assertion, operation


def build_equipment_question_rows(source_index: dict) -> list[dict]:
    blocks = equipment_question_blocks(source_index)
    specs = {
        "SEM-Q-079": ("Complete current Character Item roster, owner, and source-copy crosswalk", "official-clarification-preferred", [
            ("A", "Current official owner/text is known only for visible Automatic Shotgun and Sonic Gun; leave all other current identities/owners unresolved.", "official page 3 directly resolves two occurrences only"),
            ("B", "Use the seven TTS kit occurrences as the current roster after applying only the explicit Automatic/BF corrections.", "exact kit count/ancestry exists, but remaining TTS version currency is not established"),
            ("C", "Use the seven licensed item-* rows as the current roster.", "licensed count is complete but BF/Automatic already conflicts with official current evidence"),
        ]),
        "SEM-Q-080": ("Remaining Support Equipment deck access, exhaustion, and later use", "official-clarification-preferred", [
            ("A", "The remaining deck is accessed only by explicit future effects; no generic draw/use procedure exists.", "setup says it may be used but names no access action"),
            ("B", "A general source-defined later Support Equipment draw/draft procedure exists.", "phrase “may be used during the game” suggests access but does not specify it"),
            ("C", "Apply another finite-deck exhaustion/removal/return procedure.", "no reshuffle or shortage rule is stated"),
        ]),
        "SEM-Q-081": ("Hand capacity with Duct Tape, Bayonet, gains, discard, and attachment topology", "official-clarification-preferred", [
            ("A", "Each explicit co-occupancy exception changes only the named Items; owner chooses any source-legal discard before a gain.", "narrow exception reading"),
            ("B", "Attachment groups occupy one Hand as a unit and transfer/discard/separate together.", "possible physical arrangement; lifecycle unstated"),
            ("C", "Use another source-defined occupancy, ordering, and separation rule without auto-discarding.", "generic Hand rules do not resolve attachments"),
        ]),
        "SEM-Q-082": ("Armor break, damage, attached-token loss, replacement, and terminal Health order", "official-clarification-preferred", [
            ("A", "Discard Armor, return attached tokens, then apply all remaining damage and death checks.", "prose says discard then continue moving Health"),
            ("B", "Apply damage/Health movement as one operation and resolve Armor/token loss during it.", "possible simultaneous physical handling"),
            ("C", "Use another source-defined order for replacement, Serious-Wound substitution, damage, token loss, and death.", "nested passives and simultaneous effects are not fully ordered"),
        ]),
        "SEM-Q-083": ("Exact TTS Tactical Gear slot type/count and non-card tracks", "source-ambiguity-owner-decision-after-source-search", [
            ("A", "Promote only tracked exact source-resolved slot tokens and exact official arrow/caption occurrences; leave other TTS slots literal.", "satisfies pixel/source requirement"),
            ("B", "Use TTS GMNotes letters or licensed slots to fill missing TTS slot types/counts.", "corroboration exists but is prohibited as sole authority"),
            ("C", "Obtain exact authoritative slot/track pixel matches before any additional semantic slot assignment.", "color/title/art/orientation cannot decide"),
        ]),
        "SEM-Q-084": ("Fully Loaded Any-slot choice, simultaneous allocation, and finite shortage", "official-clarification-preferred", [
            ("A", "Item owner chooses each compatible token/Any slot sequentially in setup/player order.", "player ownership plausible; source assigns no Any-slot chooser"),
            ("B", "Apply deterministic slot order and finite availability.", "source gives no order"),
            ("C", "Use another source-defined simultaneous allocation/shortage procedure.", "component limits do not assign scarce tokens among slots"),
        ]),
        "SEM-Q-085": ("Trade/transfer capacity, owner consent, attachments, and Character Item replacement", "official-clarification-preferred", [
            ("A", "Every transfer requires recipient capacity after source-legal optional discard; attachments transfer only when each component is consented.", "narrow consent/capacity composition"),
            ("B", "A transfer may temporarily exceed capacity and resolves attachments as a unit.", "possible physical handling; unstated"),
            ("C", "Use another source-defined failure/order/replacement procedure; never auto-transfer or auto-discard.", "generic Trade omits these edges"),
        ]),
        "SEM-Q-086": ("Passive Item visibility, duration, duplicate stacking, trigger order, and Malfunction suppression", "official-clarification-preferred", [
            ("A", "All equipped Heavy/Armor faces and passives are public and each distinct passive stacks unless identical-source rule says otherwise.", "physical equipped state; no general duplicate rule"),
            ("B", "Matching passives do not stack and owner orders simultaneous triggers.", "possible analogy to Wounds; no Item rule"),
            ("C", "Use another source-defined visibility/stacking/suppression/order policy.", "Malfunction effect availability is not globally defined for passive Items"),
        ]),
        "SEM-Q-087": ("Death, escape, Starting Item loss destination, replacement, and recovery", "official-clarification-preferred", [
            ("A", "Death sends carried Items to the Item discard pile and tokens to pool; escaped/hibernated Characters retain Items.", "ordinary discard destination plus no escape-loss text"),
            ("B", "Death removes Character/Starting Items from the game or returns unique Items to a source pool.", "“lost” is not “discarded” and destination unstated"),
            ("C", "Use another source-defined destination/replacement/recovery policy without creating replacement copies.", "no checked rule restores a lost Starting Item"),
        ]),
        "SEM-Q-088": ("Weapon trigger timing, added-result order, targeting, allocation, and continuation", "official-clarification-preferred", [
            ("A", "Resolve standard die result first, then exact additional Weapon effect; stop target-bound followups if target dies.", "FAQ establishes addition, not complete order"),
            ("B", "Resolve Weapon effect before/within standard result and finish all printed operations after death.", "some effects alter/prepend results"),
            ("C", "Use source-specific order for each Weapon trigger; preserve target/Hit allocation and continuation alternatives.", "one universal order is not stated"),
        ]),
        "SEM-Q-089": ("Weapon Malfunction repair, destruction destination, attached-token return, and pending-effect continuation", "official-clarification-preferred", [
            ("A", "Second Malfunction immediately destroys/discards Weapon and returns attached tokens before later Weapon operations stop.", "strong physical reading; continuation not explicit"),
            ("B", "Finish the triggering Weapon effect, then discard Weapon/tokens.", "possible complete-effect reading"),
            ("C", "Use another source-defined repair/destruction/loss order and destination.", "checked sources do not define all edges"),
        ]),
        "SEM-Q-090": ("Grenade Launcher token count, before/instead timing, variant scope, and malfunction exception", "official-clarification-preferred", [
            ("A", "Owner selects each attached Grenade sequentially before deciding whether to perform normal Burst; malfunction blocks Weapon Burst but not Tactical Gear token use.", "FAQ exact exception plus sequential token ruling"),
            ("B", "Commit token count and before-versus-instead branch up front.", "possible single-effect selection"),
            ("C", "Use another source-defined order; never generalize malfunction bypass to Ammo/Shoot/Burst or merge TTS/official variants.", "FAQ proposition is narrow"),
        ]),
        "SEM-Q-091": ("Source-local Heavy/Weapon glyph identities and restrictions", "source-ambiguity-owner-decision-after-source-search", [
            ("A", "Retain every unmatched isolated kill/resource/crossed glyph literally and dispatch only source-resolved operations.", "direct authoritative comparisons do not establish all semantics"),
            ("B", "Use licensed placeholders or surrounding tactics to assign likely meanings.", "secondary/semantic context only; prohibited default"),
            ("C", "Resolve each exact morphology against applicable current official component evidence before promotion.", "source-scoped evidence requirement"),
        ]),
        "SEM-Q-092": ("Supporting Robot Controller and Portable Device actor/reveal/remote context", "official-clarification-preferred", [
            ("A", "Item owner controls branch/Robot/Room choices; exact text bypasses only stated locality/Malfunction restrictions.", "natural owner reading; nested context unstated"),
            ("B", "Robot/Room is the local actor and external effects remain unavailable before normal reveal.", "possible object-centered context"),
            ("C", "Use another source-defined actor/cost/reveal/availability procedure while retaining SEM-Q-012/013/018.", "no implication resolves those wider questions"),
        ]),
        "SEM-Q-093": ("Security, Entrenching, and Engineering target/owner/scarce-component order", "official-clarification-preferred", [
            ("A", "Item owner chooses every legal Room/Corridor/Door/marker and finite placements resolve in printed order.", "effect-owner reading; some verbs omit choose"),
            ("B", "Apply ordinary local deterministic scope and whole-effect legality.", "general local rule; allocation still unstated"),
            ("C", "Use another source-defined target/owner/shortage order without importing similar card variants.", "source faces differ materially"),
        ]),
        "SEM-Q-094": ("RPG, Remote Detonator, and Military Taser area targets/allocation/continuation", "official-clarification-preferred", [
            ("A", "Owner chooses exact Room/Corridor/targets and all named entities resolve sequentially in printed order.", "explicit choice exists only on some faces"),
            ("B", "Use local/deterministic scope and treat grouped outcomes simultaneously.", "possible area-effect reading"),
            ("C", "Use another source-defined target, Hit/result allocation, Door, death, and continuation policy.", "checked text does not settle every nested edge"),
        ]),
        "SEM-Q-095": ("Motion Tracker target, Hazard suppression, Noise equality, and Encounter timing", "official-clarification-preferred", [
            ("A", "Owner chooses any eligible Corridor; compare the final die result to its printed number and immediately resolve Encounter.", "likely effect-owner reading"),
            ("B", "Use deterministic/local target or compare another Noise value/source state.", "text omits chooser in some variants"),
            ("C", "Use another source-defined Hazard/Exploration/Encounter order without joining Combat Motion Tracker, Motion Tracker, Noise Scanner, or Perimeter Device by title/function.", "variants differ"),
        ]),
        "SEM-Q-096": ("Active/One Use Heavy payment, effect, discard/remove, and partial-resolution order", "official-clarification-preferred", [
            ("A", "Declare target/branch, pay, resolve full effect, return attached tokens, then discard/remove exact Item.", "ordinary action/effect cleanup reading"),
            ("B", "Discard/remove Item and tokens when Used before resolving from card-in-resolution.", "One Use says discarded when Used"),
            ("C", "Use another source-defined order for and/or branches, explicit remove-this-Item text, impossibility, and death/target changes.", "complete relative order is absent"),
        ]),
    }
    rows = []
    for qid in EQUIPMENT_QUESTION_IDS:
        title, decision_class, alternatives = specs[qid]
        rows.append({
            "questionId": qid,
            "title": title,
            "decisionClass": decision_class,
            "blocksRuleIds": blocks[qid],
            "plannedRuleIds": [],
            "defaultProhibited": True,
            "sourceEvidenceRefs": ["docs/rules/semantics/equipment-source-index.json", "docs/rulebooks/rulebook_text.txt:lines 2692–2736,3469–3548,3657–3673,3750–3763,4882–5103,5576–5667", "docs/rules/source-extraction/faq-v1.2-source-extraction.json:FQ-P02-U21/FQ-P03-U01–U07"],
            "alternatives": [{"alternativeId": f"{qid}-{suffix}", "description": description, "support": support} for suffix, description, support in alternatives],
        })
    return rows


def finalize_equipment_question_blocks(records: list[dict], question_rows: list[dict]) -> None:
    by_id = {row["questionId"]: row for row in question_rows}
    for qid in EQUIPMENT_QUESTION_IDS:
        actual = [row["ruleId"] for row in records if qid in row.get("unresolvedQuestionRefs", [])]
        by_id[qid]["blocksRuleIds"] = actual


def build_equipment_conflicts(source_index: dict) -> list[dict]:
    ids = equipment_rule_ids(source_index)
    blocks = equipment_question_blocks(source_index)
    return [
        {"conflictId": "SC-070", "title": "Current official Automatic Shotgun versus TTS Automatic/BF Gun variants", "status": "resolved-by-authority", "questionId": None, "affectedRuleIds": ["SEM-CHARACTER-ITEM-OFFICIAL-AUTOMATIC-SHOTGUN-001", "SEM-EQUIPMENT-VARIANT-BOUNDARIES-001"], "evidenceRefs": ["SRC-RULEBOOK", "SRC-EQUIPMENT-CHARACTER-CE-431200-2059A7", "SRC-EQUIPMENT-CHARACTER-HGO-524700-427C1A", BGA_EQUIPMENT_SOURCE_ID], "difference": "Official page 3 assigns current Automatic Shotgun to Heavy Gun Operator with Heavy/Before/if-able wording; TTS misnests an obsolete Rifle/On Hit variant under Combat Engineer and carries obsolete BF Gun under HGO; licensed rows follow the obsolete owner split.", "resolution": "Official current occurrence controls. Exclude both audited TTS prototypes from current dispatch while retaining exact source faces/backs/kit ancestry."},
        {"conflictId": "SC-071", "title": "Seven Character Item count versus incomplete current identity/owner crosswalk", "status": "unresolved", "questionId": "SEM-Q-079", "affectedRuleIds": blocks["SEM-Q-079"], "evidenceRefs": ["SRC-RULEBOOK", "SRC-EQUIPMENT-SUPPORT-ROOT", BGA_EQUIPMENT_SOURCE_ID], "difference": "Official inventory/setup gives seven and Contractor two, but only two current Character Item owner/face occurrences are fully visible; TTS and licensed seven-row rosters contain known obsolete conflicts.", "resolution": "No default; preserve each source roster/occurrence independently."},
        {"conflictId": "SC-072", "title": "Exact 24-card Support root versus 24 independent licensed rows", "status": "preserved-boundary", "questionId": None, "affectedRuleIds": ["SEM-SUPPORT-EQUIPMENT-DRAFT-001", "SEM-EQUIPMENT-VARIANT-BOUNDARIES-001", *ids["support"]], "evidenceRefs": ["SRC-RULEBOOK", "SRC-EQUIPMENT-SUPPORT-ROOT", BGA_EQUIPMENT_SOURCE_ID], "difference": "Counts reconcile at 24, but direct/sheet TTS titles/text/classes/slots and licensed rows differ and no copy selector crosses sources.", "resolution": "Aggregate equality is not a one-to-one crosswalk; retain all physical and licensed occurrences."},
        {"conflictId": "SC-073", "title": "Support 6x3 parent-sheet selected cells versus sixteen selector gaps", "status": "preserved-boundary", "questionId": None, "affectedRuleIds": ["SEM-EQUIPMENT-VARIANT-BOUNDARIES-001"], "evidenceRefs": ["SRC-EQUIPMENT-SUPPORT-SHEET-29"], "difference": "Only exact full CardIDs 2910 and 2917 select cells 10 and 17; sixteen readable cells have no root full CardID/GUID selector and several share titles with direct faces.", "resolution": "Preserve all sheet/hash/grid/cell tuples; no title/body/cell/modulo repair."},
        {"conflictId": "SC-074", "title": "Printed Tactical Gear slot evidence versus GMNotes/licensed slots", "status": "unresolved", "questionId": "SEM-Q-083", "affectedRuleIds": blocks["SEM-Q-083"], "evidenceRefs": ["SRC-RULEBOOK", "SRC-EQUIPMENT-SUPPORT-ROOT", BGA_EQUIPMENT_SOURCE_ID], "difference": "Some tracked TTS faces lack source-scoped authoritative slot matches while GMNotes and licensed rows supply plausible counts/types; exact official Heavy Armor/Grenade Launcher slots are separately visible.", "resolution": "No color/title/art/orientation/GMNotes/BGA default; retain literal/corroborating evidence."},
        {"conflictId": "SC-075", "title": "Color-root Heavy occurrences versus stale all-regular downstream interpretation", "status": "resolved-by-authority", "questionId": None, "affectedRuleIds": [*ids["colorHeavy"], "SEM-EQUIPMENT-VARIANT-BOUNDARIES-001"], "evidenceRefs": ["SRC-RULEBOOK", "docs/rules/semantics/green-item-source-index.json", "docs/rules/semantics/red-item-source-index.json", "docs/rules/04-items-and-equipment.md:ITM-003/ITM-004"], "difference": "Exact Green root has seven Heavy and Red root three explicit Heavy faces, contradicting the old project statement that color roots contain only regular Backpack Items.", "resolution": "Correct the project interpretation; exact physical occurrences/class rules control, while color remains a source family rather than class."},
        {"conflictId": "SC-076", "title": "Red/Yellow Heavy candidates remain physical-class/source conflicts", "status": "unresolved", "questionId": "SEM-Q-052", "affectedRuleIds": ["SEM-EQUIPMENT-VARIANT-BOUNDARIES-001"], "evidenceRefs": ["docs/rules/semantics/red-item-source-index.json", "docs/rules/semantics/yellow-item-source-index.json", BGA_EQUIPMENT_SOURCE_ID], "difference": "Six portrait Red Military Taser and six portrait Yellow Fire Extinguisher/Robot Controller selectors conflict with current/licensed Heavy class occurrences without exact copy links.", "resolution": "Keep all twelve out of Heavy/Equipment effect dispatch under SEM-Q-047/052."},
        {"conflictId": "SC-077", "title": "Weapon die-result additional versus replacement scope", "status": "resolved-by-authority", "questionId": None, "affectedRuleIds": ["SEM-WEAPON-DIE-RESULT-ADDITION-001", *ids["allFaces"]], "evidenceRefs": ["SRC-FAQ"], "difference": "Earlier component/secondary readings could treat a Weapon-specific result as replacing the standard die result.", "resolution": "FQ-P02-U21 controls only this proposition: effects are additional unless the exact instruction specifically says instead; standard Ammo loss still occurs. Wider timing/targets remain SEM-Q-088."},
        {"conflictId": "SC-078", "title": "Grenade Launcher malfunction exception versus general malfunction prohibition", "status": "resolved-by-authority", "questionId": None, "affectedRuleIds": ["SEM-GRENADE-LAUNCHER-MALFUNCTION-001", "SEM-WEAPON-MALFUNCTION-LIFECYCLE-001", *[row["semanticRuleId"] for row in source_index["supportEquipmentFaces"] if row["effectKind"] == "grenade-launcher"], "SEM-SUPPORT-OFFICIAL-GRENADE-LAUNCHER-001"], "evidenceRefs": ["SRC-FAQ"], "difference": "General rules/FAQ block Weapon use and Ammo spending while malfunctioned; FQ-P03-U03 allows attached Grenade tokens through Use Any Tactical Gear.", "resolution": "Apply the exact token-use carveout only; do not enable Shoot/Burst, Ammo, repair, or other effects."},
        {"conflictId": "SC-079", "title": "Same-title direct, sheet, official, and licensed Equipment wording", "status": "preserved-boundary", "questionId": None, "affectedRuleIds": ["SEM-EQUIPMENT-VARIANT-BOUNDARIES-001", *ids["allFaces"]], "evidenceRefs": ["SRC-EQUIPMENT-SUPPORT-ROOT", "SRC-EQUIPMENT-SUPPORT-SHEET-29", "SRC-RULEBOOK", BGA_EQUIPMENT_SOURCE_ID], "difference": "Gatling, Plasma, Flamethrower, Tactical Hatchet, Sonic, Motion/Scanner, Engineering, Robot Controller, Grenade Launcher, and other variants differ in titles, traits, bodies, punctuation, slots, or local glyphs.", "resolution": "Exact occurrence authority applies; never flatten by title/body/function or multiplicity."},
        {"conflictId": "SC-080", "title": "Generic and Character-labeled BackURLs versus face ownership/class", "status": "preserved-boundary", "questionId": None, "affectedRuleIds": ["SEM-EQUIPMENT-VARIANT-BOUNDARIES-001"], "evidenceRefs": ["docs/rules/semantics/equipment-source-index.json:sharedBacks"], "difference": "One generic SUPPORT ITEM back is shared by 24 Support and two Character-kit faces; five other backs are Character/source variants, including obsolete labels. A back label can conflict with current face owner.", "resolution": "Backs remain non-operative source sides and never identify a current face, owner, class, or extra card."},
    ]
