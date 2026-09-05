#!/usr/bin/env python3
"""Isolated Ollama Cloud critic over the concise-corpus repair diff.

Read-only: reads the diff and the rulebook page text; writes one report file.
Usage: python3 scripts/ollama_repair_critic.py <model> <out.md>
"""
import json
import os
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = "f01fe25"

SYSTEM = (
    "You are an isolated, adversarial rules critic for a board-game rules corpus (Nemesis: Retaliation). "
    "You are given (A) a unified diff of additions to a concise rules corpus, and (B) the verbatim text of the "
    "official rulebook pages the additions cite. Your only job: find places where an ADDED line (a) misstates or "
    "over-reaches its cited rulebook source, (b) contradicts another line in the corpus or in the same diff, or "
    "(c) silently resolves something the source leaves open. Ignore formatting, style, table layout, and TTS "
    "source-variant rows that are explicitly labeled as source-bound variants. Do not propose new rules. "
    "Output: a numbered list; each item = the exact added line (quoted, trimmed to 200 chars), the cited page, "
    "the specific defect in one sentence, and the rulebook sentence that supports your finding (quoted). "
    "If you find nothing material in a chunk, output exactly: NO MATERIAL FINDINGS. Be terse."
)


def rulebook_pages():
    d = ROOT / "docs/rules/source-extraction/rulebook-pages"
    return {p.stem: p.read_text(encoding="utf-8") for p in sorted(d.glob("page-*.txt"))}


def chunks(diff: str, n: int = 4):
    files = diff.split("diff --git ")
    files = [f for f in files if f.strip()]
    per = max(1, (len(files) + n - 1) // n)
    return ["diff --git " + "diff --git ".join(files[i : i + per]) for i in range(0, len(files), per)]


def call(model, prompt):
    key = os.environ.get("OLLAMA_API_KEY")
    if not key:
        env = (Path.home() / ".hermes/.env").read_text().splitlines()
        key = next(l.split("=", 1)[1].strip().strip('"') for l in env if l.startswith("OLLAMA_API_KEY="))
    body = {
        "model": model,
        "stream": False,
        "think": True,
        "options": {"temperature": 0.2, "num_ctx": 131072},
        "messages": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": prompt}],
    }
    req = urllib.request.Request(
        "https://ollama.com/api/chat",
        data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=1500) as r:
        return json.load(r)["message"]["content"]


def main():
    model, out = sys.argv[1], Path(sys.argv[2])
    diff = subprocess.check_output(
        ["git", "diff", f"{BASE}..HEAD", "--", "docs/rules/00-foundations.md", "docs/rules/01-round-and-turns.md",
         "docs/rules/02-character-actions.md", "docs/rules/03-intruders-and-survival.md",
         "docs/rules/04-items-and-equipment.md", "docs/rules/icon-glossary.md"],
        cwd=ROOT, text=True,
    )
    pages = rulebook_pages()
    reports = []
    for i, ch in enumerate(chunks(diff), 1):
        import re
        cited = sorted({f"page-{str(int(x)).zfill(2)}" for tup in re.findall(r"RB-P(\d\d)|Rulebook p\. (\d+)", ch) for x in tup if x})
        src = "\n\n".join(f"===== {p} =====\n{pages[p]}" for p in cited if p in pages)
        prompt = f"(A) DIFF CHUNK {i}\n\n{ch}\n\n(B) CITED RULEBOOK PAGES\n\n{src}"
        print(f"chunk {i}: {len(ch)} diff chars, {len(cited)} pages", flush=True)
        reports.append(f"## Chunk {i} (pages {', '.join(cited)})\n\n{call(model, prompt)}\n")
    out.write_text(f"# Repair-diff critic — {model}\n\nBase `{BASE}`..HEAD, read-only, max reasoning.\n\n" + "\n".join(reports), encoding="utf-8")
    print("wrote", out)


if __name__ == "__main__":
    main()
