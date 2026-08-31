#!/usr/bin/env python3
"""Real-CLI source-only prewrite matrix for the Stage 1 audit."""

from __future__ import annotations

import copy
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

import build_correctness_audit_prompt as prompt
import test_correctness_audit_mutations as mutations


class SourceOnlyCliMatrixTests(unittest.TestCase):
    def setUp(self) -> None:
        self.harness = mutations.Harness()
        prompts = prompt.AUDIT_DIR / "packets" / "prompts"
        prompts.mkdir(parents=True, exist_ok=True)
        self.output_root = Path(tempfile.mkdtemp(prefix=".source-only-cli-", dir=prompts))
        self.output = self.output_root / "prompt.txt"
        self.original_argv = sys.argv[:]
        self.rejected = 0

    def tearDown(self) -> None:
        sys.argv = self.original_argv
        shutil.rmtree(self.output_root, ignore_errors=True)
        self.harness.close()

    def invoke(
        self,
        *,
        mode: str,
        location: str,
        representation: str,
        token_kind: str,
        token: str,
        initial: str,
    ) -> None:
        packet = copy.deepcopy(self.harness.packet)
        review = copy.deepcopy(self.harness.review)
        target = packet if location == "packet" else review
        if representation == "value":
            field = "packetId" if location == "packet" else "reviewId"
            target[field] = f"fixture {token} fixture"
        elif token_kind == "identifier":
            target[f"wrapper:{token}:wrapper"] = "fixture"
        else:
            target[token] = "fixture"
        mutations.dump(self.harness.packet_path, packet)
        mutations.dump(self.harness.review_path, review)

        self.output.unlink(missing_ok=True)
        sentinel = b"SOURCE-ONLY-CLI-SENTINEL\x00\xff\n"
        if initial == "sentinel":
            self.output.write_bytes(sentinel)
        before_exists = self.output.exists()
        before = self.output.read_bytes() if before_exists else None
        argv = [
            "build_correctness_audit_prompt.py",
            "--mode",
            mode,
            "--packet",
            str(self.harness.packet_path),
        ]
        if mode == "blind":
            argv.extend(["--completeness", str(self.harness.review_path)])
        argv.extend(["--output", self.output.relative_to(prompt.ROOT).as_posix()])
        sys.argv = argv
        with self.assertRaises((ValueError, SystemExit), msg=(mode, location, representation, token, initial)):
            prompt.main()
        after_exists = self.output.exists()
        after = self.output.read_bytes() if after_exists else None
        self.assertEqual(before_exists, after_exists, (mode, location, representation, token, initial))
        self.assertEqual(before, after, (mode, location, representation, token, initial))
        self.rejected += 1

    def test_complete_derived_inventory_rejects_before_write(self) -> None:
        forbidden_paths, forbidden_ids = prompt.source_only_forbidden_inventory()
        self.assertEqual((len(forbidden_paths), len(forbidden_ids)), (57, 33))
        inventories = (
            ("path", sorted(forbidden_paths)),
            ("identifier", sorted(forbidden_ids)),
        )
        for token_kind, tokens in inventories:
            for token in tokens:
                for representation in ("key", "value"):
                    for initial in ("absent", "sentinel"):
                        self.invoke(
                            mode="completeness",
                            location="packet",
                            representation=representation,
                            token_kind=token_kind,
                            token=token,
                            initial=initial,
                        )
                        for location in ("packet", "completeness"):
                            self.invoke(
                                mode="blind",
                                location=location,
                                representation=representation,
                                token_kind=token_kind,
                                token=token,
                                initial=initial,
                            )
        self.assertEqual(self.rejected, 1080)

    def test_benign_payloads_reach_atomic_write(self) -> None:
        mutations.dump(self.harness.packet_path, self.harness.packet)
        mutations.dump(self.harness.review_path, self.harness.review)
        for mode in ("completeness", "blind"):
            self.output.write_bytes(b"old sentinel\n")
            argv = [
                "build_correctness_audit_prompt.py",
                "--mode",
                mode,
                "--packet",
                str(self.harness.packet_path),
            ]
            if mode == "blind":
                argv.extend(["--completeness", str(self.harness.review_path)])
            argv.extend(["--output", self.output.relative_to(prompt.ROOT).as_posix()])
            sys.argv = argv
            self.assertEqual(prompt.main(), 0)
            self.assertNotEqual(self.output.read_bytes(), b"old sentinel\n")


if __name__ == "__main__":
    unittest.main(verbosity=2)
