#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
from typing import Any

from PIL import Image

REPO = Path(__file__).resolve().parents[5]
ROOT = Path(__file__).resolve().parent
WORKER_ID = "sol-max-persistent-worker-23-20260820T185027Z-p240642-4513b3"
EXPECTED_HEAD = "48854fdd86478c1f74b614e9daa8faaa6d0beee1"
EXPECTED_BRANCH = "work/card-corpus-extraction"
START_INDEX = 113
EXPECTED_FIRST = (
    "assets/tts-mod/extract/v2-dl/tree/cards/game/missionTaskDeck-116.jpg",
    "c1adf21143fb353e2253fa99feb8f50b93fb246d8d0bd91701690a4033c658e6",
)
QUEUE_PATH = REPO / "assets/tts-mod/extract/low-confidence-review.json"
REGISTRY_PATH = REPO / "assets/tts-mod/extract/selected-card-text-evidence.json"
PROGRESS_PATH = REPO / "assets/tts-mod/extract/vision-progress.json"
CORPUS_PATH = REPO / "assets/tts-mod/extract/card-text-corpus.json"
SHARED_PATHS = {
    "progress": PROGRESS_PATH,
    "queue": QUEUE_PATH,
    "registry": REGISTRY_PATH,
    "corpus": CORPUS_PATH,
}
QA_PATHS = {
    "coverage": REPO / "docs/qa/card-extraction-coverage.json",
    "symbols": REPO / "docs/qa/card-symbol-resolution-backlog.json",
    "corpusValidation": REPO / "assets/tts-mod/extract/card-text-corpus-validation.json",
    "visionValidation": REPO / "assets/tts-mod/extract/vision-validation.json",
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def load(path: Path) -> Any:
    return json.loads(path.read_text())


def sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode()


def create_immutable(path: Path, value: Any) -> None:
    content = canonical_bytes(value)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o400)
    try:
        os.write(fd, content)
        os.fsync(fd)
    finally:
        os.close(fd)
    os.chmod(path, 0o400)


def image_probe(path: Path) -> dict[str, Any]:
    content = path.read_bytes()
    with Image.open(path) as image:
        width, height = image.size
        image_format = image.format
        mode = image.mode
        frames = int(getattr(image, "n_frames", 1))
        image.verify()
    with Image.open(path) as image:
        image.load()
    return {
        "width": width,
        "height": height,
        "format": image_format,
        "mode": mode,
        "frames": frames,
        "bytes": len(content),
        "decode": True,
    }


def tuple_digest(assets: list[dict[str, Any]]) -> str:
    rows = [(row["assetId"], row["sourcePath"], row["sourceSha256"]) for row in assets]
    return sha_bytes(json.dumps(rows, separators=(",", ":")).encode())


def process_ancestry() -> set[int]:
    ancestry: set[int] = set()
    pid = os.getpid()
    while pid > 1 and pid not in ancestry:
        ancestry.add(pid)
        try:
            status = (Path("/proc") / str(pid) / "status").read_text().splitlines()
            pid = int(next(line.split()[1] for line in status if line.startswith("PPid:")))
        except Exception:
            break
    return ancestry


def live_overlap_probe() -> list[dict[str, Any]]:
    ancestry = process_ancestry()
    matches: list[dict[str, Any]] = []
    for proc in Path("/proc").iterdir():
        if not proc.name.isdigit() or int(proc.name) in ancestry:
            continue
        try:
            raw = (proc / "cmdline").read_bytes()
            cmd = raw.replace(b"\0", b" ").decode(errors="replace")
            cwd = os.readlink(proc / "cwd")
        except Exception:
            continue
        lower = cmd.lower()
        overlap = (
            "direct_isolated_runner.py" in lower
            or "hermes chat --image" in lower
            or ("vision-workers/sol-max" in lower and "worker-23" in lower)
            or ("nemesis-card-corpus" in cwd and "hermes chat" in lower)
        )
        if overlap:
            argv0 = raw.split(b"\0", 1)[0].decode(errors="replace") if raw else ""
            matches.append({"pid": int(proc.name), "executable": argv0, "cwd": cwd})
    return sorted(matches, key=lambda row: row["pid"])


def lock_probe() -> dict[str, Any]:
    lock_path = Path(os.environ.get("WORKSPACE_LOCK_PATH", ""))
    lock_fd_text = os.environ.get("WORKSPACE_LOCK_FD", "")
    if lock_path != Path("/home/smithers/projects/nemesis-card-corpus/.workspace.lock"):
        raise RuntimeError(f"unexpected workspace lock path: {lock_path}")
    if not lock_fd_text.isdigit():
        raise RuntimeError("WORKSPACE_LOCK_FD is not exposed")
    lock_fd = int(lock_fd_text)
    path_stat = lock_path.stat()
    child_fd_visible = True
    try:
        fd_stat = os.fstat(lock_fd)
    except OSError:
        child_fd_visible = False
        fd_stat = None
    if fd_stat is not None and (path_stat.st_dev, path_stat.st_ino) != (fd_stat.st_dev, fd_stat.st_ino):
        raise RuntimeError("visible child lock fd does not match canonical lock inode")
    if not stat.S_ISREG(path_stat.st_mode) or stat.S_IMODE(path_stat.st_mode) != 0o600:
        raise RuntimeError("workspace lock is not regular mode 0600")
    lock_rows = json.loads(
        subprocess.run(
            ["lslocks", "--json", "--output", "COMMAND,PID,TYPE,MODE,PATH"],
            check=True,
            stdout=subprocess.PIPE,
            text=True,
        ).stdout
    )["locks"]
    exact = [row for row in lock_rows if row.get("path") == str(lock_path)]
    if len(exact) != 1 or exact[0].get("type") != "FLOCK" or exact[0].get("mode") != "WRITE":
        raise RuntimeError(f"exclusive workspace lock row not exact: {exact}")
    holder_pid = int(exact[0]["pid"])
    if holder_pid not in process_ancestry():
        raise RuntimeError(f"workspace lock holder is outside supervisor ancestry: {exact}")
    holder_fd_path = Path(f"/proc/{holder_pid}/fd/{lock_fd}")
    holder_fd_stat = holder_fd_path.stat()
    if (path_stat.st_dev, path_stat.st_ino) != (holder_fd_stat.st_dev, holder_fd_stat.st_ino):
        raise RuntimeError("outer supervisor lock fd does not match canonical lock inode")
    return {
        "lockPath": str(lock_path),
        "lockFd": lock_fd,
        "childFdVisible": child_fd_visible,
        "outerHolderFdTarget": os.readlink(holder_fd_path),
        "device": path_stat.st_dev,
        "inode": path_stat.st_ino,
        "mode": "0600",
        "holder": exact[0],
        "contention": "busy-as-expected-from-inherited-exclusive-owner",
        "verificationMethod": "read-only lslocks plus outer-holder fd device/inode; no lock reacquisition",
    }


def canonical_pairs() -> dict[str, Any]:
    sidecars = sorted((REPO / "cards").rglob("*.json"))
    pairs: list[dict[str, str]] = []
    for sidecar in sidecars:
        images = [candidate for suffix in (".png", ".jpg", ".jpeg", ".webp") if (candidate := sidecar.with_suffix(suffix)).is_file()]
        if len(images) != 1:
            raise RuntimeError(f"canonical sidecar does not have exactly one image: {sidecar}")
        pairs.append({
            "sidecar": sidecar.relative_to(REPO).as_posix(),
            "sidecarSha256": sha(sidecar),
            "image": images[0].relative_to(REPO).as_posix(),
            "imageSha256": sha(images[0]),
        })
    return {
        "count": len(pairs),
        "digest": sha_bytes(json.dumps(pairs, separators=(",", ":")).encode()),
        "pairs": pairs,
    }


def git_output(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=REPO, check=True, stdout=subprocess.PIPE, text=True).stdout.strip()


def main() -> None:
    if ROOT.name != WORKER_ID:
        raise RuntimeError(f"worker root mismatch: {ROOT.name}")
    for relative in (
        "raw", "results", "sealed-clean-raw", "isolated-raw-output", "metadata",
        "metadata/failures", "logs", "logs/baseline", "logs/blind", "references",
        "reports", "validation", "checkpoints", "projections",
    ):
        (ROOT / relative).mkdir(parents=True, exist_ok=True)
    for relative in ("raw", "results", "sealed-clean-raw", "isolated-raw-output"):
        if any((ROOT / relative).iterdir()):
            raise RuntimeError(f"fresh staging directory is not empty: {relative}")
    for forbidden in ("assignment.json", "assignment.immutable.json"):
        if (ROOT / forbidden).exists():
            raise RuntimeError(f"fresh worker root already has {forbidden}")

    head = git_output("rev-parse", "HEAD")
    branch = git_output("symbolic-ref", "--short", "HEAD")
    status = git_output("status", "--porcelain=v1", "--untracked-files=all")
    if head != EXPECTED_HEAD or branch != EXPECTED_BRANCH or status:
        raise RuntimeError({"head": head, "branch": branch, "status": status})

    overlap = live_overlap_probe()
    if overlap:
        raise RuntimeError(f"live overlapping worker/process found: {overlap}")
    lock = lock_probe()

    queue = load(QUEUE_PATH)
    registry = load(REGISTRY_PATH)
    progress = load(PROGRESS_PATH)
    corpus = load(CORPUS_PATH)
    selected_entries = registry["entries"]
    selected_by_tuple: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for entry in selected_entries:
        selected_by_tuple.setdefault((entry["sourcePath"], entry["sourceSha256"]), []).append(entry)

    assets: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    for queue_index in range(START_INDEX, len(queue["entries"])):
        row = queue["entries"][queue_index]
        key = (row["sourcePath"], row["sourceSha256"])
        prior = selected_by_tuple.get(key, [])
        if prior:
            skipped.append({
                "queueIndex": queue_index,
                "sourcePath": key[0],
                "sourceSha256": key[1],
                "selectedRunIdentities": [run.get("runId") or run.get("workerId") for run in prior],
            })
            continue
        source = REPO / key[0]
        if not source.is_file():
            raise RuntimeError(f"missing source: {key[0]}")
        live_sha = sha(source)
        if live_sha != key[1]:
            raise RuntimeError(f"source hash drift: {key[0]} {key[1]} != {live_sha}")
        assets.append({
            "assetId": f"W23-{len(assets) + 1:03d}",
            "assignmentIndex": len(assets),
            "queueIndex": queue_index,
            "sourcePath": key[0],
            "sourceSha256": key[1],
            "sourceMetadata": image_probe(source),
        })
        if len(assets) == 8:
            break
    if len(assets) != 8:
        raise RuntimeError(f"only selected {len(assets)} eligible tuples")
    if (assets[0]["sourcePath"], assets[0]["sourceSha256"]) != EXPECTED_FIRST:
        raise RuntimeError(f"first tuple mismatch: {assets[0]}")

    counts = {
        "complete": sum(row["status"] == "complete" for row in progress["records"]),
        "deferred": sum(row["status"] == "deferred" for row in progress["records"]),
        "visionRead": sum(row["status"] == "visionRead" for row in progress["records"]),
        "visionFailed": sum(row["status"] == "visionFailed" for row in progress["records"]),
        "pending": sum(row["status"] == "pending" for row in progress["records"]),
        "unaccounted": sum(row["status"] not in {"complete", "deferred"} for row in progress["records"]),
        "progress": len(progress["records"]),
        "queue": len(queue["entries"]),
        "registry": len(registry["entries"]),
        "corpus": len(corpus["records"]),
    }
    canonical = canonical_pairs()
    counts["canonicalPairs"] = canonical["count"]
    expected_counts = {
        "complete": 148, "deferred": 384, "visionRead": 0, "visionFailed": 0,
        "pending": 0, "unaccounted": 0, "progress": 532, "queue": 384,
        "registry": 102, "corpus": 390, "canonicalPairs": 78,
    }
    if counts != expected_counts:
        raise RuntimeError(f"baseline count drift: {counts}")

    created = now()
    assignment = {
        "schemaVersion": 1,
        "workerId": WORKER_ID,
        "createdAt": created,
        "selectionBasis": {
            "queuePath": QUEUE_PATH.relative_to(REPO).as_posix(),
            "queueSha256": sha(QUEUE_PATH),
            "startCollection": "entries",
            "startIndex": START_INDEX,
            "registryPath": REGISTRY_PATH.relative_to(REPO).as_posix(),
            "registrySha256": sha(REGISTRY_PATH),
            "registryCollection": "entries",
            "registryEntryCount": len(registry["entries"]),
            "eligibility": "forward current queue; skip exact selected tuple; live hash/decode exact; no live overlap",
            "expectedFirstTuple": {
                "queueIndex": START_INDEX,
                "sourcePath": EXPECTED_FIRST[0],
                "sourceSha256": EXPECTED_FIRST[1],
            },
            "priorCheckpointHead": EXPECTED_HEAD,
            "skippedSelectedTuples": skipped,
            "toolDisableContract": {
                "argument": "none",
                "smokeSessionId": None,
                "smokeToolCallCount": None,
                "status": "pending-neutral-smoke-before-production",
            },
        },
        "model": {
            "provider": "openai-codex",
            "model": "gpt-5.6-sol",
            "reasoningEffort": "max",
        },
        "assets": assets,
        "completionContract": {
            "persistentSessionRequired": True,
            "focusedOneImageTurns": True,
            "rawWrapperMustBeCopiedByteForByteBeforeNextCall": True,
            "rawWrapperImmutableDirectory": "sealed-clean-raw",
            "semanticMetadataForbiddenUntilAllEightWrappersSealedAndReaderExited": True,
            "candidatePromotionDefault": "defer",
            "toolsetArgument": "none",
        },
    }
    create_immutable(ROOT / "assignment.json", assignment)
    create_immutable(ROOT / "assignment.immutable.json", assignment)
    assignment_sha = sha(ROOT / "assignment.json")
    if assignment_sha != sha(ROOT / "assignment.immutable.json"):
        raise RuntimeError("assignment copies differ")

    baseline = {
        "schemaVersion": 1,
        "recordedAt": created,
        "workerId": WORKER_ID,
        "git": {"head": head, "branch": branch, "clean": True},
        "lock": lock,
        "noLiveOverlap": True,
        "overlapProbe": overlap,
        "assignmentSha256": assignment_sha,
        "orderedTupleDigest": tuple_digest(assets),
        "counts": counts,
        "orderedTuples": [
            {key: row[key] for key in ("assetId", "queueIndex", "sourcePath", "sourceSha256")}
            for row in assets
        ],
        "skippedSelectedTuples": skipped,
        "sharedPreimageSha256": {name: sha(path) for name, path in SHARED_PATHS.items()},
        "qaPreimageSha256": {name: sha(path) for name, path in QA_PATHS.items()},
        "canonicalPairs": {"count": canonical["count"], "digest": canonical["digest"]},
        "freshWorkerRoot": True,
        "emptyRawResultStaging": True,
        "overallPassed": True,
    }
    create_immutable(ROOT / "metadata/baseline.json", baseline)
    print(json.dumps({
        "workerRoot": str(ROOT),
        "assignmentSha256": assignment_sha,
        "orderedTupleDigest": baseline["orderedTupleDigest"],
        "counts": counts,
        "skippedSelectedTuples": skipped,
        "assets": baseline["orderedTuples"],
        "lock": lock,
        "overallPassed": True,
    }, indent=2))


if __name__ == "__main__":
    main()
