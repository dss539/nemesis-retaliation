#!/usr/bin/env python3
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

with open(REPO / "docs/rules/source-extraction/room-help-sheet.json", encoding="utf-8") as f:
    rooms_data = json.load(f)

with open(REPO / "archive/obsolete/semantics/data/room-icon-denotations.json", encoding="utf-8") as f:
    denotations_data = json.load(f)

room_icons = {}
for entry in denotations_data["denotations"]:
    occ = entry["occurrenceId"]
    r_id = occ.split("-")[0]
    if r_id not in room_icons:
        room_icons[r_id] = {"items": [], "hasComputer": False}
    sem = entry["semanticReferenceId"]
    if sem == "icon.computer":
        room_icons[r_id]["hasComputer"] = True
    elif "Item" in sem:
        item_color = sem.replace("icon.", "").replace("Item", "").lower()
        if item_color not in room_icons[r_id]["items"]:
            room_icons[r_id]["items"].append(item_color)

ts_lines = [
    "/**",
    " * Official Room definitions for Nemesis: Retaliation (25 rooms).",
    " * Source: docs/rules/source-extraction/room-help-sheet.json and official Room Help sheet.",
    " */",
    "",
    'import { ItemColor, RoomBackType } from "../engine/types/primitives.js";',
    "",
    "export interface RoomDefinition {",
    "  readonly id: string;",
    "  readonly roomNumber: string;",
    "  readonly name: string;",
    "  readonly sectionMarker: RoomBackType;",
    "  readonly items: readonly ItemColor[];",
    "  readonly hasComputer: boolean;",
    "  readonly actionEffect: string;",
    "  readonly notes: readonly string[];",
    "}",
    "",
    "export const OFFICIAL_ROOMS: readonly RoomDefinition[] = [",
]

for entry in rooms_data["entries"]:
    p_num = entry["printedNumber"]
    p_sec = entry["printedSectionMarker"]
    p_title = entry["printedTitle"]
    p_eff = entry["printedEffect"].replace("\n", " ").strip()
    notes = [n.replace("\n", " ").strip() for n in entry.get("associatedNotes", [])]

    r_key = f"R{p_num}"
    icons = room_icons.get(r_key, {"items": [], "hasComputer": False})

    slug = p_title.lower().replace('"', "").replace(" ", "-")
    room_id = f"room-{p_num}-{slug}"

    items_json = json.dumps(icons["items"])
    comp_json = json.dumps(icons["hasComputer"])

    ts_lines.append("  {")
    ts_lines.append(f'    id: {json.dumps(room_id)},')
    ts_lines.append(f'    roomNumber: {json.dumps(p_num)},')
    ts_lines.append(f'    name: {json.dumps(p_title)},')
    ts_lines.append(f'    sectionMarker: {json.dumps(p_sec)},')
    ts_lines.append(f'    items: {items_json},')
    ts_lines.append(f'    hasComputer: {comp_json},')
    ts_lines.append(f'    actionEffect: {json.dumps(p_eff)},')
    ts_lines.append(f'    notes: {json.dumps(notes)},')
    ts_lines.append("  },")

ts_lines.append("] as const;")
ts_lines.append("")
ts_lines.append("export const OFFICIAL_ROOMS_BY_NUMBER: Readonly<Record<string, RoomDefinition>> =")
ts_lines.append("  Object.fromEntries(OFFICIAL_ROOMS.map(r => [r.roomNumber, r]));")
ts_lines.append("")
ts_lines.append("export const OFFICIAL_ROOMS_BY_ID: Readonly<Record<string, RoomDefinition>> =")
ts_lines.append("  Object.fromEntries(OFFICIAL_ROOMS.map(r => [r.id, r]));")
ts_lines.append("")

out_path = REPO / "src/data/rooms.ts"
out_path.parent.mkdir(parents=True, exist_ok=True)
out_path.write_text("\n".join(ts_lines), encoding="utf-8")
print(f"Successfully generated {out_path} with {len(rooms_data['entries'])} rooms")
