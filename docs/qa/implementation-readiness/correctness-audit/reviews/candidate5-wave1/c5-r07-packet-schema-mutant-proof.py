#!/usr/bin/env python3
import json
import sys
from pathlib import Path
repo = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(repo / "scripts"))
import test_correctness_audit_mutations as tests
h = tests.Harness()
try:
    h.packet["unexpectedPacketField"] = "schema-mutant-survivor"
    h.resign_packet_chain()
    report = h.validate(enforce_seals=False)
    print(json.dumps({"passed": report["passed"], "failureCount": report["failureCount"], "failures": report["failures"]}, indent=2))
    raise SystemExit(0 if report["passed"] else 1)
finally:
    h.close()
