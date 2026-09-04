#!/usr/bin/env python3
from __future__ import annotations

import fcntl
import json
import subprocess
import sys
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HELPER = Path(__file__).with_name("audit_work_steal.py")


class WorkStealTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.audit = Path(self.tmp.name) / "audit"
        self.audit.mkdir()
        for name in ("pass", "fail", "unsure", "repair", "irrelevant"):
            (self.audit / name).mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def seed(self, count=1):
        rows = []
        for i in range(count):
            fragment_id = f"T-{i:03d}"
            filename = f"{fragment_id}.fact.txt"
            (self.audit / filename).write_text(f"fragment {i}\n", encoding="utf-8")
            rows.append({"id": fragment_id, "file": filename, "chars": 11})
        (self.audit / "manifest.json").write_text(json.dumps({"total": count, "fragments": rows}), encoding="utf-8")

    def run_helper(self, *args):
        proc = subprocess.run(
            [sys.executable, str(HELPER), "--audit-root", str(self.audit), *args],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertTrue(proc.stdout.strip(), proc.stderr)
        return proc, json.loads(proc.stdout)

    def test_lock_contention_then_same_call_claim(self):
        self.seed()
        source = self.audit / "T-000.fact.txt"
        with source.open("rb") as held:
            fcntl.flock(held.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            proc, payload = self.run_helper("claim", "--worker", "W1", "--rounds", "1")
            self.assertEqual(proc.returncode, 0)
            self.assertEqual(payload["status"], "busy")
            self.assertTrue(source.exists())
        proc, payload = self.run_helper("claim", "--worker", "W1")
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(payload["status"], "claimed")
        self.assertFalse(source.exists())
        self.assertTrue((self.audit / "claimed" / "W1" / source.name).is_file())

    def test_missing_source_is_never_created(self):
        self.seed(0)
        proc, payload = self.run_helper("claim", "--worker", "W2")
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(payload["status"], "empty")
        self.assertEqual(list(self.audit.glob("*.txt")), [])

    def test_parallel_claims_are_unique(self):
        self.seed(12)
        def claim(i):
            return self.run_helper("claim", "--worker", f"P{i:02d}")[1]
        with ThreadPoolExecutor(max_workers=12) as pool:
            results = list(pool.map(claim, range(12)))
        claimed = [item["id"] for item in results if item["status"] == "claimed"]
        self.assertEqual(len(claimed), 12)
        self.assertEqual(len(set(claimed)), 12)
        self.assertEqual(list(self.audit.glob("*.txt")), [])

    def test_finalize_records_runtime_metadata(self):
        self.seed()
        _, claim = self.run_helper("claim", "--worker", "L001")
        proc, payload = self.run_helper(
            "finalize", "--worker", "L001", "--id", claim["id"], "--verdict", "pass",
            "--model", "gpt-5.6-luna", "--provider", "openai-codex",
            "--evidence", "docs/rules/00-foundations.md FND-001",
        )
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(payload["status"], "finalized")
        sidecar = self.audit / "pass" / "T-000.fact.pass.md"
        text = sidecar.read_text(encoding="utf-8")
        self.assertIn("Model: `gpt-5.6-luna`", text)
        self.assertIn("Provider: `openai-codex`", text)
        self.assertTrue((self.audit / "pass" / "T-000.fact.txt").is_file())

    def test_abandoned_claim_requeues(self):
        self.seed()
        self.run_helper("claim", "--worker", "G001")
        proc, payload = self.run_helper("recover", "--worker", "G001")
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(payload["actions"][0]["action"], "requeued")
        self.assertTrue((self.audit / "T-000.fact.txt").is_file())


if __name__ == "__main__":
    unittest.main(verbosity=2)
