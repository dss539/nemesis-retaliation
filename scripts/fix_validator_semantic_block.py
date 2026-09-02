#!/usr/bin/env python3
"""Remove the obsolete semantic fragment block from validate_project_status.py.

Deletes lines 210-272 (the duplicated closing bracket at 210, every
semantic_validation/semantic_contradictions expected_fragment line, and the
original closing bracket at 272), leaving one closing bracket. Also drops the
two semantic report fields. Verifies the result compiles and contains no
semantic references.
"""
from pathlib import Path

p = Path("/home/smithers/nemesis-retaliation/scripts/validate_project_status.py")
lines = p.read_text(encoding="utf-8").splitlines(keepends=True)

# sanity-check anchors before cutting
assert lines[209].strip() == "]", "line 210 not the stray bracket"
assert lines[271].strip() == "]", "line 272 not the closing bracket"
assert "semantic_validation" in lines[210], "expected semantic block"

new = lines[:209] + lines[272:]
text = "".join(new)

# drop the two semantic report fields
for field in (
    '            "semanticPilotRecords": semantic_validation["checks"]["records"],\n',
    '            "semanticOpenQuestions": semantic_validation["checks"]["openQuestions"],\n',
):
    assert field in text, f"missing report field: {field!r}"
    text = text.replace(field, "")

p.write_text(text, encoding="utf-8")
compile(text, str(p), "exec")
assert "semantic" not in text.lower(), "semantic references remain"
print("ok: block removed, file compiles, no semantic refs")