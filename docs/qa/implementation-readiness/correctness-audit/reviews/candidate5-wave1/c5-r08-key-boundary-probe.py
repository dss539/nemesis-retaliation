#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

repo = Path("/home/smithers/projects/nemesis-c5-r08/repos/nemesis-retaliation")
module_path = repo / "scripts/build_correctness_audit_prompt.py"
spec = importlib.util.spec_from_file_location("candidate_prompt", module_path)
assert spec and spec.loader
prompt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prompt)

paths, identifiers = prompt.source_only_forbidden_inventory()
rows = []
for identifier in sorted(identifiers):
    exact_key = prompt.source_only_payload_failures({identifier: "fixture"})
    decorated_key_text = f"fixture {identifier} fixture"
    decorated_key = prompt.source_only_payload_failures({decorated_key_text: "fixture"})
    decorated_value = prompt.source_only_payload_failures(
        {"value": decorated_key_text}
    )
    punctuation_key_text = f"meta:{identifier}!"
    punctuation_key = prompt.source_only_payload_failures(
        {punctuation_key_text: "fixture"}
    )
    rows.append(
        {
            "identifier": identifier,
            "exactKeyRejected": bool(exact_key),
            "decoratedKey": decorated_key_text,
            "decoratedKeyRejected": bool(decorated_key),
            "sameTextAsValueRejected": bool(decorated_value),
            "punctuationKey": punctuation_key_text,
            "punctuationKeyRejected": bool(punctuation_key),
            "decoratedKeyFailures": decorated_key,
            "punctuationKeyFailures": punctuation_key,
        }
    )
result = {
    "candidateHead": "d78e91e9f0d29eab7e9d838d4fc043ba73518cec",
    "identifierCount": len(identifiers),
    "exactKeyRejectedCount": sum(row["exactKeyRejected"] for row in rows),
    "decoratedKeyRejectedCount": sum(row["decoratedKeyRejected"] for row in rows),
    "sameTextAsValueRejectedCount": sum(row["sameTextAsValueRejected"] for row in rows),
    "punctuationKeyRejectedCount": sum(row["punctuationKeyRejected"] for row in rows),
    "allIdentifiersBypassAsDecoratedKeys": all(
        not row["decoratedKeyRejected"] and not row["punctuationKeyRejected"]
        for row in rows
    ),
    "rows": rows,
}
print(json.dumps(result, indent=2, sort_keys=True))
