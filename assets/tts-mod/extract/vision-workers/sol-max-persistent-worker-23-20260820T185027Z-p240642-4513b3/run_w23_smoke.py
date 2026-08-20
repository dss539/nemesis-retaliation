#!/usr/bin/env python3
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import subprocess
import sys
from typing import Any

REPO = Path(__file__).resolve().parents[5]
ROOT = Path(__file__).resolve().parent
STATE_DB = Path("/home/smithers/.hermes/state.db")
EXPECTED_ROOT = "sol-max-persistent-worker-23-20260820T185027Z-p240642-4513b3"
EXPECTED_RUNTIME = {"provider": "openai-codex", "model": "gpt-5.6-sol", "reasoningEffort": "max"}
ANSI_RE = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def immutable_bytes(path: Path, value: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o400)
    try:
        os.write(fd, value)
        os.fsync(fd)
    finally:
        os.close(fd)
    os.chmod(path, 0o400)


def immutable_json(path: Path, value: Any) -> None:
    immutable_bytes(path, (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode())


def parse_json_object(text: str) -> dict[str, Any]:
    clean = ANSI_RE.sub("", text)
    decoder = json.JSONDecoder()
    for index, character in enumerate(clean):
        if character != "{":
            continue
        try:
            value, _ = decoder.raw_decode(clean[index:])
        except Exception:
            continue
        if isinstance(value, dict) and value.get("smoke") == "NO_TOOLS":
            return value
    raise ValueError("no NO_TOOLS JSON object in smoke stdout")


def parse_jsonish(value: Any) -> Any:
    if isinstance(value, (dict, list)):
        return value
    if not value:
        return None
    try:
        return json.loads(value)
    except Exception:
        return None


def reasoning_effort(config: dict[str, Any]) -> Any:
    nested = config.get("reasoning_config")
    return config.get("reasoning_effort") or config.get("reasoning") or (nested.get("effort") if isinstance(nested, dict) else None)


def parse_calls(value: Any) -> list[Any]:
    parsed = parse_jsonish(value)
    return parsed if isinstance(parsed, list) else []


def main() -> None:
    if ROOT.name != EXPECTED_ROOT:
        raise RuntimeError("worker root mismatch")
    if sha(ROOT / "assignment.json") != sha(ROOT / "assignment.immutable.json"):
        raise RuntimeError("assignment drift before smoke")
    baseline = json.loads((ROOT / "metadata/baseline-validation.json").read_text())
    if baseline.get("overallPassed") is not True:
        raise RuntimeError("baseline validation did not pass")
    if (ROOT / "metadata/smoke-audit.json").exists():
        raise RuntimeError("smoke audit already exists")

    prompt = (
        "Neutral zero-tool isolation smoke probe. If a callable tool named skill_view is available, "
        "attempt exactly one call to it with the benign name extract-game-mod-assets. If no callable "
        "tool is available, output exactly one JSON object and no Markdown with this shape: "
        '{"smoke":"NO_TOOLS","sessionId":"<exact current session ID>","provider":"openai-codex",'
        '"model":"gpt-5.6-sol","reasoningEffort":"max"}. Do not discuss any repository or task.'
    )
    command = [
        "hermes", "chat", "-Q",
        "--provider", "openai-codex",
        "-m", "gpt-5.6-sol",
        "--reasoning", "max",
        "--max-turns", "2",
        "--toolsets", "none",
        "--pass-session-id",
        "--source", "tool",
        "--ignore-rules",
        "--in", str(ROOT),
        "-q", prompt,
    ]
    env = os.environ.copy()
    env["HERMES_SKIP_CLI_UPDATE_CHECK"] = "1"
    started = now()
    proc = subprocess.run(command, cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=900)
    completed = now()
    stdout_path = ROOT / "logs/smoke.stdout.txt"
    stderr_path = ROOT / "logs/smoke.stderr.txt"
    immutable_bytes(stdout_path, proc.stdout.encode())
    immutable_bytes(stderr_path, proc.stderr.encode())
    if proc.returncode != 0:
        raise RuntimeError(f"smoke command failed rc={proc.returncode}: {proc.stderr[-2000:]}")
    payload = parse_json_object(proc.stdout)
    session_id = payload.get("sessionId")
    if not isinstance(session_id, str) or not session_id:
        raise RuntimeError("smoke session ID missing")

    con = sqlite3.connect(f"file:{STATE_DB}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    session = con.execute(
        "select id, source, model, model_config, billing_provider, message_count, tool_call_count, api_call_count, cwd, parent_session_id, system_prompt, system_prompt_hash from sessions where id=?",
        (session_id,),
    ).fetchone()
    messages = [dict(row) for row in con.execute(
        "select id, role, tool_name, tool_call_id, tool_calls, content from messages where session_id=? order by id",
        (session_id,),
    ).fetchall()]
    con.close()
    if session is None:
        raise RuntimeError("smoke session missing from state DB")
    row = dict(session)
    config = parse_jsonish(row.get("model_config")) or {}
    system_prompt = row.get("system_prompt") or ""
    roles = Counter(message["role"] for message in messages)
    tool_name_markers = [name for name in ("skill_view", "vision_analyze", "terminal", "write_file", "web_search") if name in system_prompt]
    tools_section_markers = [marker for marker in ("# Tools", "## Tools", "<tools>", "Available tools") if marker in system_prompt]
    message_tool_calls = sum(len(parse_calls(message.get("tool_calls"))) for message in messages)
    checks = {
        "exitZero": proc.returncode == 0,
        "payloadExact": payload == {
            "smoke": "NO_TOOLS",
            "sessionId": session_id,
            "provider": "openai-codex",
            "model": "gpt-5.6-sol",
            "reasoningEffort": "max",
        },
        "providerExact": row.get("billing_provider") == "openai-codex",
        "modelExact": row.get("model") == "gpt-5.6-sol",
        "reasoningExact": reasoning_effort(config) == "max",
        "oneApiCall": row.get("api_call_count") == 1,
        "twoMessages": row.get("message_count") == 2 and roles == Counter({"user": 1, "assistant": 1}),
        "zeroSessionTools": row.get("tool_call_count") == 0,
        "zeroMessageToolCalls": message_tool_calls == 0,
        "noSystemToolsSection": not tools_section_markers,
        "noSystemToolName": not tool_name_markers,
        "assignmentUnchanged": sha(ROOT / "assignment.json") == baseline["assignmentSha256"],
    }
    report = {
        "schemaVersion": 1,
        "recordType": "neutralZeroToolSmokeAudit",
        "startedAt": started,
        "completedAt": completed,
        "workerId": ROOT.name,
        "command": command[:-1] + ["<frozen neutral smoke prompt>"],
        "stdoutPath": stdout_path.relative_to(ROOT).as_posix(),
        "stdoutSha256": sha(stdout_path),
        "stderrPath": stderr_path.relative_to(ROOT).as_posix(),
        "stderrSha256": sha(stderr_path),
        "payload": payload,
        "session": {
            "sessionId": session_id,
            "source": row.get("source"),
            "provider": row.get("billing_provider"),
            "model": row.get("model"),
            "reasoningEffort": reasoning_effort(config),
            "apiCallCount": row.get("api_call_count"),
            "messageCount": row.get("message_count"),
            "toolCallCount": row.get("tool_call_count"),
            "messageRoles": dict(roles),
            "messageToolCallCount": message_tool_calls,
            "cwd": row.get("cwd"),
            "parentSessionId": row.get("parent_session_id"),
            "systemPromptSha256": sha_bytes(system_prompt.encode()),
            "systemPromptStoredHash": row.get("system_prompt_hash"),
            "systemPromptBytes": len(system_prompt.encode()),
            "toolsSectionMarkers": tools_section_markers,
            "toolNameMarkers": tool_name_markers,
        },
        "checks": checks,
        "overallPassed": all(checks.values()),
    }
    immutable_json(ROOT / "metadata/smoke-audit.json", report)
    print(json.dumps({"session": report["session"], "checks": checks, "overallPassed": report["overallPassed"]}, indent=2))
    if not report["overallPassed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        failure_path = ROOT / "metadata/failures/smoke-runner-attempt-01.json"
        if not failure_path.exists():
            immutable_json(failure_path, {"schemaVersion": 1, "failedAt": now(), "stage": "zero-tool-smoke", "errorType": type(exc).__name__, "error": str(exc)})
        print(json.dumps({"errorType": type(exc).__name__, "error": str(exc)}), file=sys.stderr)
        raise
