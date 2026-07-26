#!/usr/bin/env python3
"""Generate the exhaustive production-art inventory from requirements and game data."""
from __future__ import annotations

import argparse
import csv
import io
import json
import subprocess
from collections import Counter
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
DOC_DIR = ROOT / "docs" / "art-reference"
REQ_PATH = DOC_DIR / "asset-requirements.yml"
CSV_PATH = DOC_DIR / "art-inventory.csv"
MD_PATH = DOC_DIR / "ART-INVENTORY.md"
STATUSES = {"complete", "partial", "template-only", "missing", "deferred"}
FIELDS = ["asset_id", "category", "family", "piece", "scope", "priority", "status", "art_missing", "current_art", "implemented_in", "requirement_id", "notes"]

CHAR_FILES = {
    "char-officer": "officer.svg",
    "char-medic": "medicalSupport.svg",
    "char-recon": "recon.svg",
    "char-engineer": "combatEngineer.svg",
    "char-heavy-gunner": "heavyGunOperator.svg",
}
ENTITY_FILES = {
    "intruder-drone": "drone.svg",
    "intruder-adult": "adult.svg",
    "intruder-queen": "queen.svg",
}
ACTION_ICONS = {
    "move": "move", "cautiousMove": "cautious", "shoot": "shoot",
    "burst": "burst", "melee": "melee", "useItem": "item",
    "useTacticalGear": "gear", "useRoom": "room", "search": "search",
    "trade": "trade", "activateRobot": "robot", "pass": "pass",
    "sprint": "sprint", "rest": "rest", "reinforce": "reinforce",
    "drill": "drill", "command": "command", "special": "gear",
}
CARD_FRAMES = {
    "red": "../../assets/generated/cards/red-item.svg",
    "yellow": "../../assets/generated/cards/yellow-item.svg",
    "green": "../../assets/generated/cards/green-item.svg",
}


def load_game_data() -> dict:
    script = (
        "const fs=require('fs'),vm=require('vm');const c={};"
        "vm.runInNewContext(fs.readFileSync('js/data.js','utf8')+';this.out=GAME_DATA',c);"
        "process.stdout.write(JSON.stringify(c.out));"
    )
    return json.loads(subprocess.check_output(["node", "-e", script], cwd=ROOT, text=True))


def missing_value(status: str) -> str:
    return {"complete": "no", "partial": "partial", "template-only": "yes", "missing": "yes", "deferred": "deferred"}[status]


def add(rows: list[dict], *, asset_id: str, category: str, family: str, piece: str,
        scope: str, priority: str, status: str, current_art: str = "",
        implemented_in: str = "", requirement_id: str = "", notes: str = "") -> None:
    if status not in STATUSES:
        raise ValueError(f"Unknown status {status}")
    rows.append({
        "asset_id": asset_id, "category": category, "family": family,
        "piece": piece, "scope": scope, "priority": priority,
        "status": status, "art_missing": missing_value(status),
        "current_art": current_art, "implemented_in": implemented_in,
        "requirement_id": requirement_id, "notes": notes,
    })


def generic_coverage(req: dict, variant: str) -> tuple[str, str, str, str]:
    rid = req["id"]
    priority = req["priority"]
    render = "../../js/render.js"
    ui = "../../js/ui.js"
    css = "../../css/style.css"
    symbols = "../../assets/generated/ui-symbols.svg"

    if priority == "future":
        return "deferred", "", "", "Not in current base-game scope."

    if rid in CHAR_FILES:
        char_art = f"../../assets/generated/characters/{CHAR_FILES[rid]}"
        if variant in {"portrait", "tactical-token"}:
            return "complete", char_art, f"{render};{ui}", "Original class-coded vector asset."
        if variant == "dashboard":
            return "partial", char_art, f"{ui};{css}", "Functional dashboard uses the portrait; unique dashboard scene is not authored."
        if variant == "action-card-frame":
            return "template-only", "../../assets/generated/cards/action.svg", ui, "Shared functional frame; unique class treatment is missing."
        return "missing", "", "", "Unique authored character art is required."
    if rid == "char-bioexpert":
        return "missing", "", "", "Not represented in current game data or generated roster."
    if rid == "char-state":
        if variant in {"selected", "active"}:
            return "complete", render, render, "Rendered with selection/active rings."
        if variant in {"injured", "heavily-injured", "dead", "escaped", "disconnected"}:
            return "partial", f"{render};{ui}", f"{render};{ui}", "State is text/color-redundant; dedicated variant art is missing."
        return "missing", "", "", "Dedicated state treatment is missing."
    if rid == "player-color":
        return "complete", symbols, f"../../js/assets.js;{css}", "Semantic color mapping with text/icon redundancy."

    if rid in ENTITY_FILES:
        art = f"../../assets/generated/intruders/{ENTITY_FILES[rid]}"
        if variant in {"top-down-token", "silhouette"}:
            return "complete", art, render, "Original tactical silhouette."
        if variant == "boss-health" and rid == "intruder-queen":
            return "partial", art, render, "Queen token and hit count exist; dedicated boss board is missing."
        return "missing", "", "", "Unique entity art is required."
    if rid == "intruder-eggs" and variant == "nest-room":
        return "complete", "../../assets/generated/rooms/nest.svg", render, "Original Nest room plate."
    if rid == "robot" and variant in {"portrait", "active"}:
        return "partial", f"{symbols}#i-robot", f"{render};{ui}", "Semantic robot symbol exists; dedicated entity art is missing."

    if rid.startswith("room-tiles-"):
        if variant in {"unexplored", "explored", "selected", "legal-target"}:
            return "complete", render, render, "Shared tactical room-state rendering."
        return "partial", render, render, "Disabled state relies on subdued rendering rather than unique art."
    if rid == "landing-zone":
        if variant == "room-art":
            return "complete", "../../assets/generated/rooms/landingZone.svg", render, "Original room plate."
        if variant == "deployment-zones":
            return "partial", "../../assets/generated/rooms/landingZone.svg", render, "Player placement works; dedicated deployment-zone art is missing."
    if rid == "corridor-tiles":
        if variant in {"straight", "explored", "lit", "noisy", "occupied"}:
            return "complete", render, render, "Procedural tactical corridor rendering."
        if variant in {"corner", "junction", "dark", "blocked"}:
            return "partial", render, render, "Functional geometry/state exists only in generalized form."
        return "missing", "", "", "Dedicated corridor treatment is missing."
    if rid in {"room-floor-kit", "corridor-floor-kit"}:
        if variant in {"metal-panels", "grating", "hazard-stripes", "conduits", "vents", "rails", "decals"}:
            return "complete", "../../assets/generated/board/facility-playmat.svg", render, "Original geometric material vocabulary."
        return "missing", "", "", "Dedicated material variant is missing."
    if rid == "room-walls":
        if variant in {"wall", "doorway", "open-passage"}:
            return "complete", render, render, "Procedural octagonal boundaries and passages."
        return "missing", "", "", "Dedicated door-state art is missing."
    if rid == "tactical-grid":
        if variant != "path-preview":
            return "complete", render, render, "Procedural geometry shared by display and hit testing."
        return "missing", "", "", "Path-preview art is not implemented."

    board_ui_complete = {
        "board-sectors": {"A", "B", "C", "inactive"},
        "item-search-area": {"red", "yellow", "green", "depleted"},
        "computer-room": {"available", "broken"},
        "room-security": {"secure", "security-count", "cannot-secure"},
        "room-destruction": {"normal", "malfunction", "cannot-break"},
        "life-support": {"active", "inactive", "oxygen-track", "suffocation"},
        "reactor": {"normal", "overheating", "autodestruction-active", "countdown"},
        "time-track": {"round-marker", "event-phase", "end-state"},
        "objective-track": {"choice-position", "progress", "locked", "resolved"},
    }
    if rid in board_ui_complete and variant in board_ui_complete[rid]:
        return "partial" if rid in {"life-support", "reactor", "objective-track"} else "complete", render, f"{render};{ui}", "Functional board/HUD treatment; bespoke illustration may still be needed."
    if req["category"] == "board-ui":
        return "missing", "", "", "Dedicated board-information treatment is missing."

    if rid == "card-action":
        if variant == "card-back":
            return "complete", "../../assets/generated/cards/action.svg", ui, "Original generic action treatment."
        return "template-only", "../../assets/generated/cards/action.svg", ui, "Functional shared treatment; unique class/card art is missing."
    if rid in {"card-item-red", "card-item-yellow", "card-item-green", "card-starting-item"}:
        color = {"card-item-red": "red", "card-item-yellow": "yellow", "card-item-green": "green"}.get(rid)
        art = CARD_FRAMES[color] if color else "../../assets/generated/cards/yellow-item.svg"
        return "template-only", art, ui, "Functional category frame; unique item illustration is missing."
    if rid in {"card-objective-mission", "card-objective-private"}:
        return "template-only", "../../assets/generated/cards/objective.svg", ui, "Functional objective treatment; unique card illustration is missing."
    if rid == "card-contamination":
        return "partial", "../../assets/generated/cards/contamination.svg", ui, "Functional treatment exists; scan/code face variants are not authored."
    if req["category"] == "card":
        return "missing", "", "", "No game-facing card artwork exists for this family."

    if rid in {"dashboard-character", "dashboard-team"}:
        return "partial", f"{ui};{css}", f"{ui};{css}", "Functional responsive dashboard; unique illustrated surface variants remain."

    icon_complete = {
        "icon-actions": {"move", "cautious-move", "shoot", "melee", "search", "room-action", "pass"},
        "icon-health": {"health", "serious-wound", "death"},
        "icon-resources": {"ammo", "oxygen", "search", "computer", "backpack"},
        "icon-hazards": {"fire", "malfunction", "contamination", "infected", "noise"},
        "icon-entities": {"character", "drone", "adult", "queen", "robot"},
        "icon-objectives": {"mission", "private", "task", "success", "failure", "escape", "survival"},
    }
    if rid in icon_complete and variant in icon_complete[rid]:
        return "complete", symbols, f"../../js/assets.js;{render};{ui}", "Semantic vector symbol and visible text label."
    if req["category"] == "icon":
        return "missing", "", "", "Dedicated semantic icon is missing."

    if rid in {"token-noise", "token-fire", "token-malfunction", "token-secure"}:
        return "complete", symbols, render, "Procedural marker uses the shared vector symbol."
    if rid in {"token-health", "token-round", "token-objective"}:
        return "partial", f"{symbols};{ui}", f"{render};{ui}", "Functional HUD/label exists; dedicated physical-style token is missing."
    if req["category"] == "token":
        return "missing", "", "", "Dedicated token art is missing."
    if req["category"] == "dice":
        return "missing", "", "", "Dedicated die-face and animation art is missing."

    if rid == "ui-panels":
        if variant in {"marine-terminal", "cards", "players", "log", "modal", "phase-banner"}:
            return "complete", css, f"{css};{ui}", "Original responsive HUD surface."
        return "missing", "", "", "Dedicated tooltip surface is missing."
    if rid == "ui-legibility":
        if variant in {"text-labels", "high-contrast", "colorblind-redundancy", "focus", "disabled"}:
            return "complete", css, f"{css};{ui};{render}", "Text/icon redundancy and interactive states are implemented."
    if req["category"] in {"fx", "presentation"}:
        return "missing", "", "", "Unique authored presentation/effect art is required."

    return "missing", "", "", "No current production art is linked."


def concrete_rows(rows: list[dict], data: dict) -> None:
    # Current game characters, including Contractor (not represented by the source taxonomy's Bioexpert slot).
    for char_id, char in data["CHARACTERS"].items():
        art = f"../../assets/generated/characters/{char_id}.svg"
        for piece in ("portrait", "tactical-token"):
            add(rows, asset_id=f"game-char-{char_id}-{piece}", category="character",
                family=char["name"], piece=piece, scope="base-game", priority="critical",
                status="complete", current_art=art, implemented_in="../../js/render.js;../../js/ui.js",
                requirement_id="game-data-character", notes="Concrete current-roster asset.")

    for room_id, room in data["ROOMS"].items():
        add(rows, asset_id=f"game-room-{room_id}", category="map", family="Room plates",
            piece=room["name"], scope="base-game", priority="critical", status="complete",
            current_art=f"../../assets/generated/rooms/{room_id}.svg", implemented_in="../../js/render.js",
            requirement_id=f"room-tiles-{str(room.get('type', 'random')).replace('?', 'random').lower()}",
            notes="Concrete room plate from current game data.")

    # The engine creates ten deterministic action-card slots for each character.
    actions = ["move", "move", "move", "shoot", "search", "move", "cautiousMove", "shoot", "useRoom", "special"]
    for char_id, char in data["CHARACTERS"].items():
        for index, action in enumerate(actions):
            icon = ACTION_ICONS[action]
            add(rows, asset_id=f"card-action-{char_id}-{index + 1:02d}", category="card",
                family="Character action cards", piece=f"{char['name']} #{index + 1}: {action}",
                scope="base-game", priority="critical", status="template-only",
                current_art=f"../../assets/generated/cards/action.svg;../../assets/generated/ui-symbols.svg#i-{icon}",
                implemented_in="../../js/ui.js", requirement_id="card-action",
                notes="Functional frame and icon exist; unique card illustration is missing.")

    starter_ids = sorted({item for char in data["CHARACTERS"].values() for item in char.get("startItems", [])})
    for item_id in starter_ids:
        item = data["ITEMS"].get(item_id, {"name": item_id, "type": "yellow"})
        add(rows, asset_id=f"card-starting-{item_id}", category="card", family="Starting item cards",
            piece=item["name"], scope="base-game", priority="critical", status="template-only",
            current_art=CARD_FRAMES.get(item.get("type"), CARD_FRAMES["yellow"]), implemented_in="../../js/ui.js",
            requirement_id="card-starting-item", notes="Category frame exists; unique item illustration is missing.")

    for item_id, item in data["ITEMS"].items():
        add(rows, asset_id=f"card-item-{item_id}", category="card", family=f"{item['type'].title()} item cards",
            piece=item["name"], scope="base-game", priority="critical", status="template-only",
            current_art=CARD_FRAMES[item["type"]], implemented_in="../../js/ui.js",
            requirement_id=f"card-item-{item['type']}", notes="Category frame exists; unique item illustration is missing.")

    concrete_cards = [
        ("EVENTS", "card-event", "Event cards", "missing", ""),
        ("EXPLORATION_CARDS", "card-exploration", "Exploration cards", "missing", ""),
        ("INTRUDER_ATTACKS", "card-intruder-attack", "Intruder attack cards", "missing", ""),
        ("SERIOUS_WOUNDS", "card-wound", "Serious wound cards", "missing", ""),
        ("MISSION_OBJECTIVES", "card-objective-mission", "Mission objective cards", "template-only", "../../assets/generated/cards/objective.svg"),
        ("PRIVATE_OBJECTIVES", "card-objective-private", "Private objective cards", "template-only", "../../assets/generated/cards/objective.svg"),
        ("MISSION_TASKS", "card-objective-mission", "Mission task cards", "template-only", "../../assets/generated/cards/objective.svg"),
    ]
    for data_key, req_id, family, status, art in concrete_cards:
        for entry in data.get(data_key, []):
            entry_id = entry.get("id", entry.get("name", "unnamed")).replace(" ", "-").lower()
            name = entry.get("name") or f"Exploration {entry_id}"
            add(rows, asset_id=f"{req_id}-{entry_id}", category="card", family=family,
                piece=name, scope="base-game", priority="critical" if req_id in {"card-event", "card-exploration", "card-intruder-attack"} else "high",
                status=status, current_art=art, implemented_in="../../js/ui.js" if art else "",
                requirement_id=req_id,
                notes="Unique card illustration is missing." if status != "complete" else "")

    # Larva exists in current data but is absent from the grouped Primeblood requirements.
    for piece in ("top-down-token", "silhouette"):
        add(rows, asset_id=f"game-intruder-larva-{piece}", category="entity", family="Larva",
            piece=piece, scope="base-game", priority="critical", status="complete",
            current_art="../../assets/generated/intruders/larva.svg", implemented_in="../../js/render.js",
            requirement_id="game-data-intruder", notes="Concrete current-roster asset.")


def build_rows() -> list[dict]:
    requirements = yaml.safe_load(REQ_PATH.read_text(encoding="utf-8"))["requirements"]
    rows: list[dict] = []
    for req in requirements:
        variants = req.get("variants") or ["unspecified"]
        for variant in variants:
            status, art, implementation, notes = generic_coverage(req, str(variant))
            add(rows, asset_id=f"req-{req['id']}-{str(variant).lower().replace(' ', '-').replace('/', '-')}",
                category=req["category"], family=req["name"], piece=str(variant),
                scope="future" if req["priority"] == "future" else "base-game",
                priority=req["priority"], status=status, current_art=art,
                implemented_in=implementation, requirement_id=req["id"], notes=notes)
    concrete_rows(rows, load_game_data())
    rows.sort(key=lambda row: (row["category"], row["family"], row["piece"], row["asset_id"]))
    return rows


def validate(rows: list[dict]) -> None:
    ids = [row["asset_id"] for row in rows]
    if len(ids) != len(set(ids)):
        duplicates = [item for item, count in Counter(ids).items() if count > 1]
        raise ValueError(f"Duplicate inventory IDs: {duplicates}")
    requirement_ids = {req["id"] for req in yaml.safe_load(REQ_PATH.read_text(encoding="utf-8"))["requirements"]}
    covered = {row["requirement_id"] for row in rows}
    missing_requirements = requirement_ids - covered
    if missing_requirements:
        raise ValueError(f"Requirements absent from inventory: {sorted(missing_requirements)}")

    data = load_game_data()
    concrete_counts = {
        "game-char-": len(data["CHARACTERS"]) * 2,
        "game-room-": len(data["ROOMS"]),
        "card-action-": sum(int(char["actionDeckSize"]) for char in data["CHARACTERS"].values()),
        "card-item-": len(data["ITEMS"]),
        "card-event-": len(data["EVENTS"]),
        "card-exploration-": len(data["EXPLORATION_CARDS"]),
        "card-intruder-attack-": len(data["INTRUDER_ATTACKS"]),
        "card-wound-": len(data["SERIOUS_WOUNDS"]),
        "card-objective-private-": len(data["PRIVATE_OBJECTIVES"]),
        "card-objective-mission-": len(data["MISSION_OBJECTIVES"]) + len(data["MISSION_TASKS"]),
    }
    for prefix, expected in concrete_counts.items():
        actual = sum(row["asset_id"].startswith(prefix) for row in rows)
        if actual != expected:
            raise ValueError(f"Concrete inventory count for {prefix}: expected {expected}, found {actual}")

    for row in rows:
        if row["status"] not in STATUSES:
            raise ValueError(f"Invalid status in {row['asset_id']}")
        for link in filter(None, row["current_art"].split(";")):
            target = link.split("#", 1)[0]
            if target.startswith("../../") and not (DOC_DIR / target).resolve().exists():
                raise FileNotFoundError(f"Broken current-art link in {row['asset_id']}: {link}")


def csv_text(rows: list[dict]) -> str:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue()


def md_escape(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def links(value: str) -> str:
    if not value:
        return "—"
    return " · ".join(f"[art{index if index > 1 else ''}]({path})" for index, path in enumerate(value.split(";"), 1))


def markdown_text(rows: list[dict]) -> str:
    statuses = Counter(row["status"] for row in rows)
    categories = Counter(row["category"] for row in rows)
    missing = sum(row["art_missing"] in {"yes", "partial"} for row in rows)
    lines = [
        "# Master art inventory", "",
        "This is the repository overview for every currently known production-art requirement. It expands the grouped taxonomy in `asset-requirements.yml`, adds every concrete room and game-data card, links the current game-facing art where one exists, and explicitly marks missing unique art.", "",
        "Regenerate and validate it with `python3 scripts/generate_art_inventory.py --check`.", "",
        "## Status definitions", "",
        "- `complete` — current art fulfills this functional production slot.",
        "- `partial` — a functional treatment exists, but a dedicated variant or illustration is still needed.",
        "- `template-only` — a reusable frame/icon exists; the unique illustration is missing.",
        "- `missing` — no current game-facing art exists.",
        "- `deferred` — known expansion/future requirement; no current art is expected yet.", "",
        "Reusable overlays, symbols, and material treatments are tracked once. Cards and named rooms are tracked individually because they need unique faces or plates.", "",
        "## Summary", "",
        f"Total atomic inventory rows: {len(rows)}", "",
        f"Rows with missing or partially missing authored art: {missing}", "",
        "| Status | Count |", "| --- | ---: |",
    ]
    lines.extend(f"| {status} | {statuses.get(status, 0)} |" for status in ["complete", "partial", "template-only", "missing", "deferred"])
    lines.extend(["", "| Category | Count |", "| --- | ---: |"])
    lines.extend(f"| {category} | {count} |" for category, count in sorted(categories.items()))
    lines.extend(["", "Machine-readable version: [art-inventory.csv](art-inventory.csv)", ""])
    for category in sorted(categories):
        lines.extend([f"## {category.replace('-', ' ').title()}", "", "| ID | Family | Piece | Scope | Priority | Status | Missing art? | Current art | Notes |", "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"])
        for row in (item for item in rows if item["category"] == category):
            lines.append("| " + " | ".join([
                md_escape(row["asset_id"]), md_escape(row["family"]), md_escape(row["piece"]),
                row["scope"], row["priority"], row["status"], row["art_missing"],
                links(row["current_art"]), md_escape(row["notes"]),
            ]) + " |")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Fail if committed inventory output is stale")
    args = parser.parse_args()
    rows = build_rows()
    validate(rows)
    outputs = {CSV_PATH: csv_text(rows), MD_PATH: markdown_text(rows)}
    if args.check:
        stale = [str(path.relative_to(ROOT)) for path, content in outputs.items() if not path.exists() or path.read_text(encoding="utf-8") != content]
        if stale:
            raise SystemExit("Stale inventory output: " + ", ".join(stale))
        print(f"Inventory valid: {len(rows)} atomic rows; all current-art links resolve")
        return
    for path, content in outputs.items():
        path.write_text(content, encoding="utf-8", newline="")
    print(f"Generated {len(rows)} atomic rows in {CSV_PATH.relative_to(ROOT)} and {MD_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
