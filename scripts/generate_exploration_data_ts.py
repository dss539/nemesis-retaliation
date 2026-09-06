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

console.log(JSON.stringify({
  explorationCards: ctx.EXPLORATION_CARDS_DATA,
  corridors: ctx.CORRIDORS_DATA,
}));
"""

res = subprocess.run(["node", "-e", node_script], capture_output=True, text=True, check=True)
data = json.loads(res.stdout)
exp_cards = data["explorationCards"]
corridors = data["corridors"]

dir_map = {
    0: "NE",
    1: "E",
    2: "SE",
    3: "SW",
    4: "W",
    5: "NW",
}

# 1. Generate src/data/exploration-cards.ts
ts_lines = [
    "/**",
    " * Official Exploration Cards for Nemesis: Retaliation (12 cards).",
    " * Source: docs/rules/source-extraction/secondary/bga-staticData-260622-1220.js and official rules.",
    " */",
    "",
    'import { Direction, RoomBackType } from "../engine/types/primitives.js";',
    "",
    "export interface ExplorationCardDefinition {",
    "  readonly id: string;",
    "  readonly number: number;",
    "  readonly roomType: RoomBackType | 'ABC';",
    "  readonly corridorDirections: readonly Direction[];",
    "  readonly noiseDirections: readonly Direction[];",
    "  readonly tokens: readonly string[];",
    "  readonly description: string;",
    "  readonly closeDoor: boolean;",
    "  readonly noiseRoll: boolean;",
    "  readonly hazard: boolean;",
    "  readonly intrudersToAdd: number;",
    "  readonly removeFromGame: boolean;",
    "}",
    "",
    "export const EXPLORATION_CARDS: readonly ExplorationCardDefinition[] = [",
]

for key, card in exp_cards.items():
    num = card.get("number")
    c_dirs = [dir_map[d] for d in card.get("corridors", [])]
    n_dirs = [dir_map[d] for d in card.get("corridorsWithNoise", [])]
    tokens = card.get("otherTokens", [])
    effects = "\n".join(card.get("effectDesc", []))
    room_type = card.get("type")

    ts_lines.append("  {")
    ts_lines.append(f'    id: "exploration-card-{num}",')
    ts_lines.append(f'    number: {num},')
    ts_lines.append(f'    roomType: {json.dumps(room_type)},')
    ts_lines.append(f'    corridorDirections: {json.dumps(c_dirs)},')
    ts_lines.append(f'    noiseDirections: {json.dumps(n_dirs)},')
    ts_lines.append(f'    tokens: {json.dumps(tokens)},')
    ts_lines.append(f'    description: {json.dumps(effects)},')
    ts_lines.append(f'    closeDoor: {json.dumps(bool(card.get("closeDoor")))},')
    ts_lines.append(f'    noiseRoll: {json.dumps(bool(card.get("noiseRoll")))},')
    ts_lines.append(f'    hazard: {json.dumps(bool(card.get("hazard")))},')
    ts_lines.append(f'    intrudersToAdd: {card.get("intrudersToAdd", 0)},')
    ts_lines.append(f'    removeFromGame: {json.dumps(bool(card.get("removeFromGame")))},')
    ts_lines.append("  },")

ts_lines.append("] as const;")
ts_lines.append("")

out_exp = REPO / "src/data/exploration-cards.ts"
out_exp.write_text("\n".join(ts_lines), encoding="utf-8")
print(f"Generated {out_exp} with {len(exp_cards)} exploration cards")

# 2. Generate src/data/corridors.ts
c_lines = [
    "/**",
    " * Official Corridor tile pool for Nemesis: Retaliation (40 corridor tiles).",
    " * 10 each of values 1, 2, 3, 4.",
    " */",
    "",
    "export interface CorridorTileDefinition {",
    "  readonly id: string;",
    "  readonly number: number;",
    "  readonly noiseValue: number;",
    "  readonly deadlyNoiseValue?: number;",
    "  readonly hasDoor: boolean;",
    "}",
    "",
    "export const CORRIDOR_TILES: readonly CorridorTileDefinition[] = [",
]

for key, corr in corridors.items():
    num = corr.get("number")
    nv = corr.get("noiseValue")
    dnv = corr.get("deadlyNoiseValue")
    hd = bool(corr.get("hasDoor"))

    c_lines.append("  {")
    c_lines.append(f'    id: "corridor-tile-{num}",')
    c_lines.append(f'    number: {num},')
    c_lines.append(f'    noiseValue: {nv},')
    if dnv is not None:
        c_lines.append(f'    deadlyNoiseValue: {dnv},')
    c_lines.append(f'    hasDoor: {json.dumps(hd)},')
    c_lines.append("  },")

c_lines.append("] as const;")
c_lines.append("")

out_corr = REPO / "src/data/corridors.ts"
out_corr.write_text("\n".join(c_lines), encoding="utf-8")
print(f"Generated {out_corr} with {len(corridors)} corridor tiles")
