#!/usr/bin/env python3
"""Group unresolved card glyph descriptions for evidence-driven triage.

Cluster names are morphological triage labels, never canonical semantics.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import re
from typing import Any

REPO = Path(__file__).resolve().parents[3]
CORPUS = REPO / "assets/tts-mod/extract/card-text-corpus.json"

CLUSTERS = [
    ("circular-creature-morphology", r"creature|alien|insect|many[- ]limbed|tentacl|spined|spiky|crouched|winged|dragon|humanoid.*medallion"),
    ("octagonal-or-chamfered-polygon", r"octagon|eight[- ]sided|8[- ]sided|chamfered"),
    ("red-prohibition-overlay", r"red (?:x|cross)|crossed[- ]out|diagonal (?:slash|bar)|prohibition"),
    ("gear-or-cog-morphology", r"cog|gear|cogwheel"),
    ("skull-burst-or-explosion-morphology", r"skull|burst|explosion|splash"),
    ("exclamation-marker", r"exclamation"),
    ("biohazard-morphology", r"biohazard"),
    ("triangle-morphology", r"triangle|triangular"),
    ("square-or-checkbox-morphology", r"square|checkbox|rounded rectangle|rounded-rectangle"),
    ("die-or-face-morphology", r"\bdie\b|dice|pips?"),
]

STRATEGY = {
    "circular-creature-morphology": "Build a focused contact sheet across attack-card rows, then establish printed type names from applicable official Attack Card/rulebook evidence.",
    "octagonal-or-chamfered-polygon": "Compare representative cards against authoritative room/search/item references; preserve literal shape until a printed name is proven.",
    "red-prohibition-overlay": "Inspect glyph location and occluded base silhouette; compare with authoritative restriction/action icons rather than inferring from rules semantics.",
    "gear-or-cog-morphology": "Compare directly with the page-40 malfunction crop and card-local gear markers; do not collapse lookalikes without visible discriminators.",
    "skull-burst-or-explosion-morphology": "Compare with authoritative die-face crops and any card-local damage marker references; require a visible internal-mark match.",
    "exclamation-marker": "Check source edition/prototype provenance first; several examples may be prototype-only UI markers rather than final-game rules icons.",
    "biohazard-morphology": "Separate decorative art/watermarks from inline operative symbols by location and sentence grammar before assigning meaning.",
    "triangle-morphology": "Build a local comparison set; retain descriptive token if no exhaustive official vocabulary exists.",
    "square-or-checkbox-morphology": "Distinguish mission checkbox/control decoration from operative inline icons using layout and official component references.",
    "die-or-face-morphology": "Compare with the complete authoritative die-face crop set and require exact internal marks.",
    "other-local-morphology": "Review highest-frequency rules-bearing examples first, then split into narrower morphology clusters without semantic guessing.",
}


def classify(token: str) -> str:
    low = token.lower()
    for name, pattern in CLUSTERS:
        if re.search(pattern, low):
            return name
    return "other-local-morphology"


def rules_excerpt(row: dict[str, Any]) -> str:
    printed = row.get("printedData")
    if not isinstance(printed, dict):
        return ""
    chunks = []
    for key in ("body", "firstEffect", "secondEffect", "commandPanel", "reactionPanel"):
        value = printed.get(key)
        if isinstance(value, str) and value.strip():
            chunks.append(value.strip())
    return " | ".join(chunks)[:500]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default="docs/qa/card-symbol-resolution-backlog.json")
    args = ap.parse_args()

    corpus = json.loads(CORPUS.read_text())
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    token_counts = Counter()
    for row in corpus["records"]:
        for token in row["symbols"]["unresolvedOrLocalTokens"]:
            cluster = classify(token)
            token_counts[token] += 1
            grouped[cluster].append({
                "sourcePath": row["sourcePath"],
                "sourceSha256": row["sourceSha256"],
                "componentFamily": row["componentFamily"],
                "printedTitle": row.get("identity", {}).get("printedTitle"),
                "token": token,
                "rulesTextPresent": row["rulesTextPresent"],
                "rulesExcerpt": rules_excerpt(row),
                "ledgerStatus": row["ledgerStatus"],
            })

    clusters = []
    for name, occurrences in grouped.items():
        unique_assets = sorted({x["sourcePath"] for x in occurrences})
        rules_assets = sorted({x["sourcePath"] for x in occurrences if x["rulesTextPresent"]})
        unique_tokens = sorted({x["token"] for x in occurrences})
        priority = len(rules_assets) * 100 + len(unique_assets) * 10 + len(occurrences)
        if name in {"biohazard-morphology", "exclamation-marker"}:
            priority -= 300
        clusters.append({
            "cluster": name,
            "status": "morphology-only-unresolved",
            "priorityScore": priority,
            "occurrences": len(occurrences),
            "assetCount": len(unique_assets),
            "rulesBearingAssetCount": len(rules_assets),
            "distinctLiteralDescriptions": len(unique_tokens),
            "resolutionStrategy": STRATEGY[name],
            "topRepeatedLiterals": [
                {"token": token, "count": token_counts[token]}
                for token in sorted(unique_tokens, key=lambda t: (-token_counts[t], t))[:20]
            ],
            "evidence": sorted(occurrences, key=lambda x: (x["sourcePath"], x["token"])),
        })
    clusters.sort(key=lambda x: (-x["priorityScore"], x["cluster"]))

    out = {
        "schemaVersion": 1,
        "sourceCorpus": "assets/tts-mod/extract/card-text-corpus.json",
        "sourceProgressUpdatedAt": corpus["generatedFrom"]["visionProgressUpdatedAt"],
        "warning": "Cluster labels describe visible morphology only. They are not canonical icon names or semantic claims.",
        "summary": {
            "unresolvedTokenOccurrences": sum(len(v) for v in grouped.values()),
            "distinctLiteralDescriptions": len(token_counts),
            "affectedAssets": len({x["sourcePath"] for rows in grouped.values() for x in rows}),
            "clusters": len(clusters),
        },
        "clusters": clusters,
    }
    output = REPO / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({"output": str(output.relative_to(REPO)), "summary": out["summary"], "ranking": [{k: c[k] for k in ("cluster", "priorityScore", "assetCount", "rulesBearingAssetCount", "occurrences")} for c in clusters]}, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
