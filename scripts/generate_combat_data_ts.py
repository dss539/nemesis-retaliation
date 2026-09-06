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

const out = {
  attacks: ctx.INTRUDER_ATTACKS_DATA || {},
  events: ctx.EVENT_CARDS_DATA || {},
  seriousWounds: ctx.SERIOUS_WOUNDS_DATA || {},
  queenCards: ctx.QUEEN_CARDS_DATA || {}
};

process.stdout.write(JSON.stringify(out));
"""

proc = subprocess.run(["node", "-e", node_script], capture_output=True, text=True, check=True)
data = json.loads(proc.stdout)

def flatten_str(x):
    if isinstance(x, list):
        return " ".join(flatten_str(i) for i in x if i)
    return str(x) if x is not None else ""

# 1. Attacks
attacks_lines = [
    "/**",
    " * Intruder Attack cards for Nemesis: Retaliation.",
    " */",
    "",
    "export interface IntruderAttackCard {",
    "  id: string;",
    "  title: string;",
    "  rulesText: string;",
    "}",
    "",
    "export const INTRUDER_ATTACK_CARDS: readonly IntruderAttackCard[] = [",
]
for k, v in data["attacks"].items():
    desc = flatten_str(v.get("effectDesc", ""))
    attacks_lines.append("  {")
    attacks_lines.append(f"    id: {json.dumps(k)},")
    attacks_lines.append(f"    title: {json.dumps(v.get('name', k))},")
    attacks_lines.append(f"    rulesText: {json.dumps(desc.strip())},")
    attacks_lines.append("  },")
attacks_lines.append("];\n")
(REPO / "src/data/attacks.ts").write_text("\n".join(attacks_lines), encoding="utf-8")

# 2. Events
events_lines = [
    "/**",
    " * Event cards for Nemesis: Retaliation.",
    " */",
    "",
    "export interface EventCardDefinition {",
    "  id: string;",
    "  title: string;",
    "  intruderMovementDesc: string;",
    "  primaryEffectDesc: string;",
    "  secondaryEffectDesc: string;",
    "}",
    "",
    "export const EVENT_CARDS: readonly EventCardDefinition[] = [",
]
for k, v in data["events"].items():
    mv = flatten_str(v.get("intrudersEffectDesc", ""))
    p = flatten_str(v.get("primaryEffectDesc", ""))
    s = flatten_str(v.get("secondaryEffectDesc", ""))
    events_lines.append("  {")
    events_lines.append(f"    id: {json.dumps(k)},")
    events_lines.append(f"    title: {json.dumps(v.get('name', k))},")
    events_lines.append(f"    intruderMovementDesc: {json.dumps(mv.strip())},")
    events_lines.append(f"    primaryEffectDesc: {json.dumps(p.strip())},")
    events_lines.append(f"    secondaryEffectDesc: {json.dumps(s.strip())},")
    events_lines.append("  },")
events_lines.append("];\n")
(REPO / "src/data/events.ts").write_text("\n".join(events_lines), encoding="utf-8")

# 3. Serious Wounds
sw_lines = [
    "/**",
    " * Serious Wound cards for Nemesis: Retaliation.",
    " */",
    "",
    "export interface SeriousWoundDefinition {",
    "  id: string;",
    "  title: string;",
    "  bodyText: string;",
    "}",
    "",
    "export const SERIOUS_WOUND_CARDS: readonly SeriousWoundDefinition[] = [",
]
for k, v in data["seriousWounds"].items():
    desc = flatten_str(v.get("effectDesc", ""))
    sw_lines.append("  {")
    sw_lines.append(f"    id: {json.dumps(k)},")
    sw_lines.append(f"    title: {json.dumps(v.get('name', k))},")
    sw_lines.append(f"    bodyText: {json.dumps(desc.strip())},")
    sw_lines.append("  },")
sw_lines.append("];\n")
(REPO / "src/data/serious-wounds.ts").write_text("\n".join(sw_lines), encoding="utf-8")

# 4. Queen Cards
qc_lines = [
    "/**",
    " * Queen Health cards for Nemesis: Retaliation.",
    " */",
    "",
    "export interface QueenCardDefinition {",
    "  id: string;",
    "  title: string;",
    "  healthModifier: number;",
    "  effectDesc: string;",
    "}",
    "",
    "export const QUEEN_HEALTH_CARDS: readonly QueenCardDefinition[] = [",
]
for k, v in data["queenCards"].items():
    desc = flatten_str(v.get("effectDesc", ""))
    qc_lines.append("  {")
    qc_lines.append(f"    id: {json.dumps(k)},")
    qc_lines.append(f"    title: {json.dumps(v.get('name', k))},")
    qc_lines.append(f"    healthModifier: {v.get('hp', 0)},")
    qc_lines.append(f"    effectDesc: {json.dumps(desc.strip())},")
    qc_lines.append("  },")
qc_lines.append("];\n")
(REPO / "src/data/queen-cards.ts").write_text("\n".join(qc_lines), encoding="utf-8")

print("Generated attacks.ts, events.ts, serious-wounds.ts, and queen-cards.ts successfully!")
