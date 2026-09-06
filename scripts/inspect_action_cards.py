#!/usr/bin/env python3
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

with open(REPO / "assets/tts-mod/extract/card-text-corpus.json", encoding="utf-8") as f:
    corpus = json.load(f)

action_cards = []
for record in corpus["records"]:
    family = record.get("componentFamily", "")
    if family.startswith("character/"):
        action_cards.append({
            "family": family,
            "title": record.get("identity", {}).get("canonicalSlug", ""),
            "body": record.get("printedData", {}).get("body", ""),
            "upperRight": record.get("printedData", {}).get("upperRight", ""),
            "sidecar": record.get("identity", {}).get("sidecarPath", ""),
        })

print(f"Total character corpus records: {len(action_cards)}")
by_family = {}
for c in action_cards:
    fam = c["family"]
    by_family.setdefault(fam, []).append(c)

for fam, cards in sorted(by_family.items()):
    print(f"  {fam}: {len(cards)} cards")
