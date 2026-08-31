#!/usr/bin/env python3
from __future__ import annotations

import io
import json
import sys
import unittest
from pathlib import Path
from unittest import mock

repo = Path("/home/smithers/projects/nemesis-c5-r08/repos/nemesis-retaliation")
sys.path.insert(0, str(repo / "scripts"))
import test_correctness_audit_mutations as suite  # noqa: E402

original_paths, original_ids = suite.prompt_target.source_only_forbidden_inventory()
test_name = "test_source_only_inventory_covers_frozen_paths_and_post_reveal_ids"


def run_mutant(name: str, paths: set[str], identifiers: set[str]) -> dict[str, object]:
    stream = io.StringIO()
    case = suite.AuditMutationTests(test_name)
    with mock.patch.object(
        suite.prompt_target,
        "source_only_forbidden_inventory",
        return_value=(set(paths), set(identifiers)),
    ):
        result = unittest.TextTestRunner(stream=stream, verbosity=2).run(
            unittest.TestSuite([case])
        )
    return {
        "name": name,
        "testsRun": result.testsRun,
        "passed": result.wasSuccessful(),
        "failures": len(result.failures),
        "errors": len(result.errors),
        "runnerOutput": stream.getvalue(),
    }

omitted_path = "docs/rules/ontology/mappings.json"
omitted_identifier = "sourceFinding"
minimal_ids = {
    "rootCauseId",
    "authorityOverride",
    "classification",
    "hiddenDefault",
    "verificationEvidenceRefs",
    "reviewedDiscrepancyIds",
}
mutants = [
    run_mutant(
        "omit-one-derived-path",
        original_paths - {omitted_path},
        original_ids,
    ),
    run_mutant(
        "omit-one-derived-identifier",
        original_paths,
        original_ids - {omitted_identifier},
    ),
    run_mutant(
        "collapse-to-only-explicitly-asserted-inventory",
        {"scripts/build_semantic_pilots.py"},
        minimal_ids,
    ),
]
print(
    json.dumps(
        {
            "candidateHead": "d78e91e9f0d29eab7e9d838d4fc043ba73518cec",
            "focusedTest": f"AuditMutationTests.{test_name}",
            "originalPathCount": len(original_paths),
            "originalIdentifierCount": len(original_ids),
            "omittedPath": omitted_path,
            "omittedIdentifier": omitted_identifier,
            "mutants": mutants,
            "survivingMutantCount": sum(row["passed"] for row in mutants),
        },
        indent=2,
        sort_keys=True,
    )
)
