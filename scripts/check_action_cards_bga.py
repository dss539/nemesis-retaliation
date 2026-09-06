#!/usr/bin/env python3
import json
import subprocess

node_script = """
const fs = require('fs');
const vm = require('vm');
const src = fs.readFileSync('docs/rules/source-extraction/secondary/bga-staticData-260622-1220.js', 'utf8');
const transformed = src.replace(/^const\\s+([A-Za-z_$][\\w$]*)\\s*=/gm, 'globalThis.$1 =');
const ctx = {};
vm.createContext(ctx);
vm.runInContext(transformed, ctx);

console.log(JSON.stringify(ctx.ACTION_CARDS_DATA, null, 2));
"""

res = subprocess.run(["node", "-e", node_script], capture_output=True, text=True, check=True)
cards = json.loads(res.stdout)
print(f"Loaded {len(cards)} action cards")
for k in list(cards.keys())[:5]:
    print(k, cards[k]["name"], "character:", cards[k]["character"], "noIntruders:", cards[k].get("noIntruders"))
