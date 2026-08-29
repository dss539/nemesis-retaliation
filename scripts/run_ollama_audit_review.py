#!/usr/bin/env python3
"""Call an isolated Ollama Cloud audit reviewer without retaining thinking."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import urllib.request
from pathlib import Path


def strict_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key in reviewer response: {key}")
        result[key] = value
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--prompt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--num-ctx", type=int, default=65536)
    args = parser.parse_args()

    key = os.environ.get("OLLAMA_API_KEY")
    if not key:
        raise SystemExit("OLLAMA_API_KEY is not set")
    prompt_bytes = args.prompt.read_bytes()
    prompt = prompt_bytes.decode("utf-8")
    request_body = {
        "model": args.model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "format": "json",
        "options": {"temperature": 0.0, "num_ctx": args.num_ctx},
        "think": "max",
    }
    request = urllib.request.Request(
        "https://ollama.com/api/chat",
        data=json.dumps(request_body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=1200) as response:
        raw = json.load(response, object_pairs_hook=strict_pairs)
    message = raw.get("message", {})
    content = message.get("content")
    if not isinstance(content, str) or not content.strip():
        failure = {
            "schemaVersion": 1,
            "recordType": "ollama-cloud-audit-review-failed-attempt",
            "provider": "ollama-cloud",
            "requestedModel": args.model,
            "responseModel": raw.get("model"),
            "requestedReasoning": "max",
            "promptPath": str(args.prompt),
            "promptSha256": hashlib.sha256(prompt_bytes).hexdigest(),
            "responseCreatedAt": raw.get("created_at"),
            "done": raw.get("done"),
            "doneReason": raw.get("done_reason"),
            "error": "empty message.content",
            "thinkingRetained": False,
        }
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(failure, indent=2) + "\n", encoding="utf-8")
        raise SystemExit("reviewer returned empty message.content")
    review = json.loads(content, object_pairs_hook=strict_pairs)
    envelope = {
        "schemaVersion": 1,
        "recordType": "ollama-cloud-audit-review",
        "provider": "ollama-cloud",
        "requestedModel": args.model,
        "responseModel": raw.get("model"),
        "requestedReasoning": "max",
        "stream": False,
        "format": "json",
        "promptPath": str(args.prompt),
        "promptSha256": hashlib.sha256(prompt_bytes).hexdigest(),
        "responseCreatedAt": raw.get("created_at"),
        "done": raw.get("done"),
        "doneReason": raw.get("done_reason"),
        "review": review,
        "thinkingRetained": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(envelope, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "output": str(args.output),
                "requestedModel": args.model,
                "responseModel": raw.get("model"),
                "promptSha256": envelope["promptSha256"],
                "verdict": review.get("verdict"),
                "findingCount": len(review.get("findings", [])),
                "thinkingRetained": False,
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
