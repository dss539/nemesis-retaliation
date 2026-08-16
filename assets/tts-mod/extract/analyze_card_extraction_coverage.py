#!/usr/bin/env python3
"""Summarize useful card-text coverage independently of canonical promotion."""
from __future__ import annotations

import argparse
import collections
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
EXTRACT = REPO / "assets/tts-mod/extract"
PROGRESS = EXTRACT / "vision-progress.json"
QUEUE = EXTRACT / "low-confidence-review.json"
TOKEN_RE = re.compile(r"\[([^\]]+)\]")
TEXT_KEYS = ("title", "typeLine", "body", "footer", "upperRight", "lowerCenter", "visibleText")


def load(path: Path):
    return json.loads(path.read_text())


def family(path: str) -> str:
    marker = "/tree/cards/"
    if marker not in path:
        return "non-card"
    tail = path.split(marker, 1)[1].split("/")
    if not tail:
        return "cards/unknown"
    if tail[0] == "character":
        return "/".join(tail[:2]) if len(tail) > 1 else "character/unknown"
    if tail[0] == "game":
        return "/".join(tail[:2]) if len(tail) > 1 else "game/unknown"
    return tail[0]


def visible_dict(entry: dict) -> dict:
    value = entry.get("visibleText")
    if isinstance(value, dict):
        return value
    semantic = entry.get("semanticRead")
    if isinstance(semantic, dict):
        return semantic
    if isinstance(value, list):
        return {"visibleFragments": value}
    return {}


def flatten_text(value) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        result = []
        for item in value:
            if isinstance(item, dict):
                result.extend(flatten_text(item.get("text")))
            else:
                result.extend(flatten_text(item))
        return result
    if isinstance(value, dict):
        result = []
        for key in TEXT_KEYS + ("printedLines", "sections", "visibleFragments"):
            if key in value:
                result.extend(flatten_text(value[key]))
        return result
    return []


def reason_tags(reason: str, uncertainties: list) -> list[str]:
    text = " ".join([reason, *[str(v) for v in uncertainties]]).lower()
    tests = {
        "provenance": ("provenance", "guid", "faceurl", "backurl", "paired side", "cell-to", "cell-specific"),
        "unknown-icon": ("unknown icon", "unknown glyph", "icon identity", "glyph identity", "glossary match", "glyph has not", "icon has not"),
        "clipped-or-illegible": ("clipped", "illegible", "unreadable"),
        "source-conflict": ("conflict", "prototype", "official-versus", "official vs", "supersession"),
        "classification": ("classification", "category", "ownership", "component identity", "component function"),
        "orientation": ("orientation", "rotation"),
        "schema-or-destination": ("schema", "destination", "existing canonical", "overwrite"),
        "needs-official-source": ("official source", "official component", "rulebook", "faq", "errata"),
    }
    return [tag for tag, needles in tests.items() if any(n in text for n in needles)] or ["other"]


def extraction_state(entry: dict) -> tuple[str, dict]:
    visible = visible_dict(entry)
    fragments = flatten_text(visible)
    text = "\n".join(x for x in fragments if x).strip()
    body = visible.get("body") if isinstance(visible.get("body"), str) else ""
    structured_rules = [
        visible.get(key) for key in ("firstEffect", "secondEffect", "commandPanel", "reactionPanel")
        if isinstance(visible.get(key), str) and visible.get(key).strip()
    ]
    has_rules_text = bool(body.strip() or structured_rules)
    tokens = sorted(set(TOKEN_RE.findall(text)))
    unknown = sorted(t for t in tokens if t.upper().startswith("ICON:") or t.lower() in {"illegible", "clipped"})
    markers = re.findall(r"\[(?:illegible|clipped)(?:[^\]]*)\]", text, re.I)
    if has_rules_text and not markers:
        state = "draft-full"
    elif has_rules_text:
        state = "draft-partial"
    elif text:
        state = "non-rules-or-reference"
    else:
        state = "no-transcription"
    return state, {
        "title": visible.get("title"),
        "typeLine": visible.get("typeLine"),
        "body": visible.get("body"),
        "footer": visible.get("footer"),
        "recognizedTokens": sorted(t for t in tokens if t not in unknown),
        "unknownTokens": unknown,
        "unreadableMarkers": markers,
    }


def priority(entry: dict, state: str, facts: dict, tags: list[str]) -> int:
    path = entry["sourcePath"]
    if "/tree/cards/" not in path or "/cards/reference/" in path:
        return -1000
    score = {"no-transcription": 1000, "draft-partial": 650, "draft-full": 100, "non-rules-or-reference": -500}[state]
    score += 350 if facts["unreadableMarkers"] else 0
    score += 250 if facts["unknownTokens"] else 0
    score += 100 if "unknown-icon" in tags else 0
    score += 80 if any(x in path for x in ("/attack", "/event", "/exploration", "/action", "/item", "/queenhealth", "/seriouswound")) else 0
    score -= 100 if tags == ["provenance"] else 0
    return score


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--top", type=int, default=50)
    args = parser.parse_args()
    progress = load(PROGRESS)
    queue = load(QUEUE)
    records = progress["records"]
    deferred = {e["sourcePath"]: e for e in queue["entries"]}
    rows = []
    state_counts = collections.Counter()
    family_counts = collections.Counter()
    tag_counts = collections.Counter()
    card_state_counts = collections.Counter()
    for entry in queue["entries"]:
        state, facts = extraction_state(entry)
        tags = reason_tags(entry.get("reasonSkipped", ""), entry.get("uncertainties") or [])
        fam = family(entry["sourcePath"])
        is_card = fam != "non-card"
        is_rules_bearing = is_card and fam != "reference"
        score = priority(entry, state, facts, tags)
        state_counts[state] += 1
        family_counts[fam] += 1
        for tag in tags:
            tag_counts[tag] += 1
        if is_card:
            card_state_counts[state] += 1
        rows.append({
            "sourcePath": entry["sourcePath"],
            "sourceSha256": entry.get("sourceSha256"),
            "family": fam,
            "isCard": is_card,
            "isRulesBearingCandidate": is_rules_bearing,
            "extractionState": state,
            "priorityScore": score,
            **facts,
            "reasonTags": tags,
            "reasonSkipped": entry.get("reasonSkipped"),
            "uncertainties": entry.get("uncertainties") or [],
            "vision": {k: (entry.get("vision") or {}).get(k) for k in ("provider", "model", "reasoningEffort", "workerId", "sessionId", "resultPath", "rawResultPath")},
        })
    card_records = [r for r in records if "/tree/cards/" in r["sourcePath"]]
    complete_cards = [r for r in card_records if r["status"] == "complete"]
    deferred_cards = [r for r in card_records if r["status"] == "deferred"]
    top = sorted((r for r in rows if r["isRulesBearingCandidate"]), key=lambda r: (-r["priorityScore"], r["sourcePath"]))[:args.top]
    payload = {
        "schemaVersion": 1,
        "sourceProgressUpdatedAt": progress.get("updatedAt"),
        "sourceQueueUpdatedAt": queue.get("updatedAt"),
        "totals": {
            "inScope": len(records),
            "complete": sum(r["status"] == "complete" for r in records),
            "deferred": len(deferred),
            "cardImages": len(card_records),
            "completeCardImages": len(complete_cards),
            "deferredCardImages": len(deferred_cards),
            "deferredNonCardImages": len(deferred) - len(deferred_cards),
            "canonicalSidecars": len(list((REPO / "cards").rglob("*.json"))),
        },
        "deferredExtractionStates": dict(sorted(state_counts.items())),
        "deferredCardExtractionStates": dict(sorted(card_state_counts.items())),
        "deferredFamilies": dict(sorted(family_counts.items())),
        "reasonTags": dict(sorted(tag_counts.items())),
        "topRulesInformationPriorities": top,
    }
    text = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        output = args.output if args.output.is_absolute() else REPO / args.output
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text)
    print(text, end="")


if __name__ == "__main__":
    main()
