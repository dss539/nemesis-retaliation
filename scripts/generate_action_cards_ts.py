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

console.log(JSON.stringify(ctx.ACTION_CARDS_DATA));
"""

res = subprocess.run(["node", "-e", node_script], capture_output=True, text=True, check=True)
bga_cards = json.loads(res.stdout)

char_map = {
    1: "recon",
    2: "heavy-gun-operator",
    3: "combat-engineer",
    4: "officer",
    5: "medical-support",
    6: "contractor",
}

ts_lines = [
    "/**",
    " * Official Action Card definitions for Nemesis: Retaliation (60 cards, 10 per character).",
    " * Source: docs/rules/source-extraction/secondary/bga-staticData-260622-1220.js and official cards.",
    " */",
    "",
    'import { CharacterId } from "../engine/types/primitives.js";',
    'import { ActionCard } from "../engine/types/cards.js";',
    "",
    "export interface ActionCardDefinition extends ActionCard {",
    "  readonly key: string;",
    "  readonly isCommand?: boolean;",
    "  readonly reactionText?: string;",
    "}",
    "",
    "export const ACTION_CARDS: readonly ActionCardDefinition[] = [",
]

for key, card in bga_cards.items():
    char_num = card.get("character")
    char_id = char_map[char_num]
    name = card.get("name", "")
    no_intruders = bool(card.get("noIntruders", False))
    reaction = card.get("reactionDesc", "")
    is_reaction = bool(reaction)
    is_command = bool(card.get("command", False))
    
    effects = card.get("effectDesc", [])
    if isinstance(effects, list):
        effect_text = "\n\n".join(effects)
    else:
        effect_text = str(effects)

    card_id = f"action-{key.lower().replace('_', '-')}"

    ts_lines.append("  {")
    ts_lines.append(f"    id: {json.dumps(card_id)},")
    ts_lines.append(f"    key: {json.dumps(key)},")
    ts_lines.append(f"    title: {json.dumps(name)},")
    ts_lines.append(f"    characterId: {json.dumps(char_id)},")
    ts_lines.append(f"    combatRestricted: {json.dumps(no_intruders)},")
    ts_lines.append(f"    isReaction: {json.dumps(is_reaction)},")
    ts_lines.append(f"    rulesText: {json.dumps(effect_text)},")
    if is_command:
        ts_lines.append(f"    isCommand: true,")
    if reaction:
        ts_lines.append(f"    reactionText: {json.dumps(reaction)},")
    ts_lines.append("  },")

ts_lines.append("] as const;")
ts_lines.append("")
ts_lines.append("export const ACTION_CARDS_BY_ID: Readonly<Record<string, ActionCardDefinition>> =")
ts_lines.append("  Object.fromEntries(ACTION_CARDS.map(c => [c.id, c]));")
ts_lines.append("")
ts_lines.append("export const ACTION_CARDS_BY_CHARACTER: Readonly<Record<CharacterId, readonly ActionCardDefinition[]>> =")
ts_lines.append("  ACTION_CARDS.reduce((acc, card) => {")
ts_lines.append("    const list = acc[card.characterId as CharacterId] ?? [];")
ts_lines.append("    return { ...acc, [card.characterId]: [...list, card] };")
ts_lines.append("  }, {} as Record<CharacterId, readonly ActionCardDefinition[]>);")
ts_lines.append("")

out_file = REPO / "src/data/action-cards.ts"
out_file.write_text("\n".join(ts_lines), encoding="utf-8")
print(f"Successfully generated {out_file} with {len(bga_cards)} action cards")
