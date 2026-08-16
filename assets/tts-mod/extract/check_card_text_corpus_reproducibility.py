#!/usr/bin/env python3
"""Verify deterministic card-corpus reconstruction without touching tracked output."""
from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

import build_card_text_corpus as corpus_builder

REPO = Path(__file__).resolve().parents[3]
CORPUS = REPO / "assets/tts-mod/extract/card-text-corpus.json"
FORBIDDEN_GENERATION_KEYS = {"generatedAt", "mergedAt", "selectedEvidenceLastMerged"}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def find_forbidden_keys(value, location: str = "$" + "") -> list[str]:
    found = []
    if isinstance(value, dict):
        for key, item in value.items():
            child = f"{location}.{key}"
            if key in FORBIDDEN_GENERATION_KEYS:
                found.append(child)
            found.extend(find_forbidden_keys(item, child))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            found.extend(find_forbidden_keys(item, f"{location}[{index}]"))
    return found


def main() -> int:
    subprocess.run(
        ["git", "ls-files", "--error-unmatch", CORPUS.relative_to(REPO).as_posix()],
        cwd=REPO,
        check=True,
        stdout=subprocess.DEVNULL,
    )
    original_bytes = CORPUS.read_bytes()
    original_hash = hashlib.sha256(original_bytes).hexdigest()
    original_stat = CORPUS.stat()
    with tempfile.TemporaryDirectory(prefix=".card-text-corpus-repro-", dir=CORPUS.parent) as temp_dir:
        first = Path(temp_dir) / "first.json"
        second = Path(temp_dir) / "second.json"
        corpus_builder.write_corpus(first)
        corpus_builder.write_corpus(second)
        first_hash = sha256(first)
        second_hash = sha256(second)
        if first_hash != second_hash or first.read_bytes() != second.read_bytes():
            raise SystemExit("two fresh corpus builds differ")
        if first.read_bytes() != original_bytes:
            raise SystemExit("tracked corpus differs from freshly generated content")
        forbidden = find_forbidden_keys(json.loads(first.read_text()))
        if forbidden:
            raise SystemExit(f"generated corpus contains wall-clock generation metadata: {forbidden}")
    final_stat = CORPUS.stat()
    if CORPUS.read_bytes() != original_bytes:
        raise SystemExit("reproducibility check modified tracked corpus content")
    if (final_stat.st_mtime_ns, final_stat.st_size) != (original_stat.st_mtime_ns, original_stat.st_size):
        raise SystemExit("reproducibility check rewrote tracked corpus")
    print(json.dumps({
        "passed": True,
        "trackedCorpus": CORPUS.relative_to(REPO).as_posix(),
        "trackedCorpusSha256": original_hash,
        "firstBuildSha256": first_hash,
        "secondBuildSha256": second_hash,
        "trackedOutputUnchanged": True,
        "forbiddenGenerationMetadata": [],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
