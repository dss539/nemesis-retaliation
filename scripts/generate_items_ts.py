#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

node_script = """
const fs = require('fs');
const vm = require('vm');
const src = fs.readFileSync('docs/rules/source-extraction/secondary/bga-staticData-260622-1220.js', 'utf8');
const transformed = src.replace(/^const\\s+([A-Za-z_$][\\w$]*)\\s*=/gm, 'globalThis.$1 =');
const ctx = {};
vm.createContext(ctx);
vm.runInContext(transformed, ctx);

console.log(JSON.stringify(ctx.ITEMS_DATA));
"""

res = subprocess.run(["node", "-e", node_script], capture_output=True, text=True, check=True)
bga_items = json.loads(res.stdout)

ts_lines = [
    "/**",
    " * Official Item definitions for Nemesis: Retaliation.",
    " * Source: docs/rules/source-extraction/secondary/bga-staticData-260622-1220.js and official components.",
    " */",
    "",
    'import { ItemCategory, ItemDeckColor } from "../engine/types/items.js";',
    'import { WeaponType } from "../engine/types/items.js";',
    "",
    "export interface ItemDefinition {",
    "  readonly id: string;",
    "  readonly key: string;",
    "  readonly title: string;",
    "  readonly deck: string;",
    "  readonly category: ItemCategory;",
    "  readonly color?: ItemDeckColor;",
    "  readonly isHeavy: boolean;",
    "  readonly isArmor: boolean;",
    "  readonly isOneUse: boolean;",
    "  readonly isWeapon: boolean;",
    "  readonly weaponType?: WeaponType;",
    "  readonly requiresNoAmmo: boolean;",
    "  readonly ammoCapacity: number;",
    "  readonly countInDeck: number;",
    "  readonly rulesText: string;",
    "  readonly traits?: string;",
    "}",
    "",
    "export const ALL_ITEMS: readonly ItemDefinition[] = [",
]

for key, item in bga_items.items():
    name = item.get("name", "")
    deck = item.get("deck", "")
    heavy = bool(item.get("heavy", False))
    armor = bool(item.get("armor", False))
    one_use = bool(item.get("oneUse", False))
    ranged = bool(item.get("rangedWeapon", False))
    melee = bool(item.get("meleeWeapon", False))
    no_ammo = bool(item.get("noAmmoWeapon", False))
    nbr = item.get("nbr", 1)
    traits = item.get("traits", "")
    slots = item.get("slots", [])
    ammo_capacity = len([s for s in slots if s == "ammo"])

    is_weapon = ranged or melee or no_ammo
    weapon_type = "ranged" if ranged else ("melee" if melee else None)

    category = "support" if deck == "item-support" else (
        "starting" if deck.startswith("item-") else (
            "quest" if deck == "eggs-reserve" else deck.replace("deck-", "")
        )
    )
    color = deck.replace("deck-", "") if deck in ("deck-red", "deck-yellow", "deck-green") else None

    effects = item.get("effectDesc", [])
    if isinstance(effects, list):
        effect_text = "\n\n".join(effects)
    else:
        effect_text = str(effects)

    item_id = f"item-{key.lower()}"

    ts_lines.append("  {")
    ts_lines.append(f"    id: {json.dumps(item_id)},")
    ts_lines.append(f"    key: {json.dumps(key)},")
    ts_lines.append(f"    title: {json.dumps(name)},")
    ts_lines.append(f"    deck: {json.dumps(deck)},")
    ts_lines.append(f"    category: {json.dumps(category)},")
    if color:
        ts_lines.append(f"    color: {json.dumps(color)},")
    ts_lines.append(f"    isHeavy: {json.dumps(heavy)},")
    ts_lines.append(f"    isArmor: {json.dumps(armor)},")
    ts_lines.append(f"    isOneUse: {json.dumps(one_use)},")
    ts_lines.append(f"    isWeapon: {json.dumps(is_weapon)},")
    if weapon_type:
        ts_lines.append(f"    weaponType: {json.dumps(weapon_type)},")
    ts_lines.append(f"    requiresNoAmmo: {json.dumps(no_ammo)},")
    ts_lines.append(f"    ammoCapacity: {ammo_capacity},")
    ts_lines.append(f"    countInDeck: {nbr},")
    ts_lines.append(f"    rulesText: {json.dumps(effect_text)},")
    if traits:
        ts_lines.append(f"    traits: {json.dumps(traits)},")
    ts_lines.append("  },")

ts_lines.append("] as const;")
ts_lines.append("")
ts_lines.append("export const ALL_ITEMS_BY_KEY: Readonly<Record<string, ItemDefinition>> =")
ts_lines.append("  Object.fromEntries(ALL_ITEMS.map(i => [i.key, i]));")
ts_lines.append("")
ts_lines.append("export const ALL_ITEMS_BY_ID: Readonly<Record<string, ItemDefinition>> =")
ts_lines.append("  Object.fromEntries(ALL_ITEMS.map(i => [i.id, i]));")
ts_lines.append("")

out_file = REPO / "src/data/items.ts"
out_file.write_text("\n".join(ts_lines), encoding="utf-8")
print(f"Successfully generated {out_file} with {len(bga_items)} items")
