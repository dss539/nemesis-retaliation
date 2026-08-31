#!/usr/bin/env python3
from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import io
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable

REPO = Path("/home/smithers/projects/nemesis-c5-r06/repos/nemesis-retaliation")
SOURCE_ROOT = Path("/home/smithers/nemesis-retaliation")
EXPECTED_HEAD = "d78e91e9f0d29eab7e9d838d4fc043ba73518cec"
STAGE_PATH = REPO / "scripts/stage_correctness_audit_sources.py"
PROMPT_PATH = REPO / "scripts/build_correctness_audit_prompt.py"
TREES = (Path("docs/rulebooks"), Path("assets/tts-mod/extract"))


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


stage = load("candidate5_stage_path_probe", STAGE_PATH)
prompt = load("candidate5_prompt_path_probe", PROMPT_PATH)


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            value.update(chunk)
    return value.hexdigest()


def make_source(root: Path) -> Path:
    source = root / "source"
    (source / "docs/rulebooks").mkdir(parents=True)
    (source / "assets/tts-mod/extract").mkdir(parents=True)
    (source / "docs/rulebooks/probe.pdf").write_bytes(b"bounded pdf source\n")
    (source / "assets/tts-mod/extract/probe.bin").write_bytes(b"bounded asset source\n")
    return source


def make_target(root: Path) -> Path:
    target = root / "target"
    target.mkdir()
    subprocess.run(
        ["git", "init", "-q"],
        cwd=target,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return target


def code_from_system_exit(value: Any) -> int:
    if value is None:
        return 0
    if isinstance(value, int):
        return value
    return 1


def run_stage_main(
    target: Path,
    source_argument: Path | str,
    configure: Callable[[dict[str, Any]], None] | None = None,
) -> dict[str, Any]:
    original_root = stage.ROOT
    original_argv = sys.argv[:]
    original_copy2 = stage.shutil.copy2
    original_sha256 = stage.sha256
    state: dict[str, Any] = {
        "target": target,
        "sourceArgument": Path(source_argument),
        "originalCopy2": original_copy2,
        "originalSha256": original_sha256,
        "copyCalls": [],
    }
    if configure:
        configure(state)
    stage.ROOT = target
    sys.argv = [os.fspath(STAGE_PATH), "--source-root", os.fspath(source_argument)]
    output = io.StringIO()
    errors = io.StringIO()
    code = 0
    message = ""
    try:
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
            returned = stage.main()
        code = int(returned)
    except SystemExit as exc:
        code = code_from_system_exit(exc.code)
        message = "" if exc.code is None else str(exc.code)
    finally:
        stage.ROOT = original_root
        stage.shutil.copy2 = original_copy2
        stage.sha256 = original_sha256
        sys.argv = original_argv
    parsed = None
    if output.getvalue().strip():
        parsed = json.loads(output.getvalue())
    return {
        "exitCode": code,
        "message": message,
        "stdout": parsed,
        "stderr": errors.getvalue(),
        "copyCalls": state["copyCalls"],
        "state": {key: value for key, value in state.items() if key.startswith("observed")},
    }


def observe_copy_calls(state: dict[str, Any]) -> None:
    original = state["originalCopy2"]

    def wrapper(src, dst, *args, **kwargs):
        state["copyCalls"].append(
            {"source": os.fspath(src), "target": os.fspath(dst)}
        )
        return original(src, dst, *args, **kwargs)

    stage.shutil.copy2 = wrapper


def static_stage_controls() -> dict[str, Any]:
    results: dict[str, Any] = {}

    with tempfile.TemporaryDirectory(prefix="candidate5-source-root-link-") as directory:
        root = Path(directory)
        source = make_source(root)
        alias = root / "source-link"
        alias.symlink_to(source, target_is_directory=True)
        target = make_target(root)
        observed = run_stage_main(target, alias, observe_copy_calls)
        assert observed["exitCode"] != 0 and not observed["copyCalls"], observed
        assert "--source-root contains a symlink component" in observed["message"], observed
        results["sourceRootSymlink"] = observed

    with tempfile.TemporaryDirectory(prefix="candidate5-source-intermediate-") as directory:
        root = Path(directory)
        source = root / "source"
        source.mkdir()
        outside = root / "outside-source"
        (outside / "rulebooks").mkdir(parents=True)
        (outside / "rulebooks/probe.pdf").write_bytes(b"outside source\n")
        (source / "docs").symlink_to(outside, target_is_directory=True)
        (source / "assets/tts-mod/extract").mkdir(parents=True)
        (source / "assets/tts-mod/extract/probe.bin").write_bytes(b"asset\n")
        target = make_target(root)
        observed = run_stage_main(target, source, observe_copy_calls)
        assert observed["exitCode"] != 0 and not observed["copyCalls"], observed
        assert "source tree contains a symlink component" in observed["message"], observed
        assert not (target / "docs/rulebooks/probe.pdf").exists(), observed
        results["sourceIntermediateSymlink"] = observed

    with tempfile.TemporaryDirectory(prefix="candidate5-target-intermediate-") as directory:
        root = Path(directory)
        source = make_source(root)
        target = make_target(root)
        outside = root / "outside-target"
        outside.mkdir()
        (target / "docs").symlink_to(outside, target_is_directory=True)
        observed = run_stage_main(target, source, observe_copy_calls)
        assert observed["exitCode"] != 0 and not observed["copyCalls"], observed
        assert "target path contains a symlink" in observed["message"], observed
        assert not (outside / "rulebooks/probe.pdf").exists(), observed
        results["targetIntermediateSymlink"] = observed

    with tempfile.TemporaryDirectory(prefix="candidate5-target-dangling-") as directory:
        root = Path(directory)
        source = make_source(root)
        target = make_target(root)
        external = root / "outside/missing.pdf"
        link = target / "docs/rulebooks/probe.pdf"
        link.parent.mkdir(parents=True)
        link.symlink_to(external)
        link_text = os.readlink(link)
        observed = run_stage_main(target, source, observe_copy_calls)
        assert observed["exitCode"] != 0 and not observed["copyCalls"], observed
        assert "target path contains a symlink" in observed["message"], observed
        assert link.is_symlink() and os.readlink(link) == link_text, observed
        assert not external.exists(), observed
        results["danglingFinalTargetSymlink"] = {
            **observed,
            "symlinkPreserved": True,
            "externalReferentAbsent": True,
        }

    return results


def rejected(call: Callable[[], Any]) -> str:
    try:
        call()
    except (ValueError, SystemExit) as exc:
        return str(exc)
    raise AssertionError("alias unexpectedly accepted")


def alias_and_prompt_static_controls() -> dict[str, Any]:
    stage_aliases = {
        "backslash": rejected(
            lambda: stage.target_path(Path("docs/rulebooks\\bad.pdf"))
        ),
        "dotdot": rejected(
            lambda: stage.target_path(Path("docs/rulebooks/../bad.pdf"))
        ),
        "absolute": rejected(
            lambda: stage.target_path(Path("/docs/rulebooks/bad.pdf"))
        ),
    }
    with tempfile.TemporaryDirectory(prefix="candidate5-prompt-static-") as directory:
        root = Path(directory)
        original_root = prompt.ROOT
        original_audit = prompt.AUDIT_DIR
        prompt.ROOT = root
        prompt.AUDIT_DIR = root / "docs/qa/implementation-readiness/correctness-audit"
        prompt_root = prompt.AUDIT_DIR / "packets/prompts"
        prompt_root.mkdir(parents=True)
        (prompt_root / "real").mkdir()
        (prompt_root / "alias").symlink_to("real", target_is_directory=True)
        dangling = prompt_root / "dangling.txt"
        dangling.symlink_to(root / "outside/missing.txt")
        prefix = "docs/qa/implementation-readiness/correctness-audit/packets/prompts"
        try:
            prompt_aliases = {
                "empty": rejected(lambda: prompt.canonical_output_path("")),
                "backslash": rejected(
                    lambda: prompt.canonical_output_path(f"{prefix}/bad\\name.txt")
                ),
                "dot": rejected(
                    lambda: prompt.canonical_output_path(f"{prefix}/./bad.txt")
                ),
                "dotdot": rejected(
                    lambda: prompt.canonical_output_path(f"{prefix}/sub/../bad.txt")
                ),
                "duplicateSeparator": rejected(
                    lambda: prompt.canonical_output_path(f"{prefix}//bad.txt")
                ),
                "trailingSeparator": rejected(
                    lambda: prompt.canonical_output_path(f"{prefix}/bad.txt/")
                ),
                "absolute": rejected(
                    lambda: prompt.canonical_output_path(f"/{prefix}/bad.txt")
                ),
                "siblingPrefix": rejected(
                    lambda: prompt.canonical_output_path(f"{prefix}-other/bad.txt")
                ),
                "intermediateSymlink": rejected(
                    lambda: prompt.canonical_output_path(f"{prefix}/alias/out.txt")
                ),
                "danglingFinalSymlink": rejected(
                    lambda: prompt.canonical_output_path(f"{prefix}/dangling.txt")
                ),
            }
        finally:
            prompt.ROOT = original_root
            prompt.AUDIT_DIR = original_audit
    return {
        "sourceRelativeTargetAliases": stage_aliases,
        "promptOutputAliasesAndSymlinks": prompt_aliases,
    }


def stage_final_target_race() -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="candidate5-stage-final-race-") as directory:
        root = Path(directory)
        source = make_source(root)
        target = make_target(root)
        external = root / "outside/final-race.pdf"
        external.parent.mkdir()
        expected = (source / "docs/rulebooks/probe.pdf").read_bytes()

        def configure(state: dict[str, Any]) -> None:
            original = state["originalCopy2"]
            raced = False

            def wrapper(src, dst, *args, **kwargs):
                nonlocal raced
                state["copyCalls"].append(
                    {"source": os.fspath(src), "target": os.fspath(dst)}
                )
                destination = Path(dst)
                if not raced and destination.as_posix().endswith("docs/rulebooks/probe.pdf"):
                    assert not destination.exists() and not destination.is_symlink()
                    destination.symlink_to(external)
                    raced = True
                    state["observedSwapAfterPrewriteCheck"] = True
                return original(src, dst, *args, **kwargs)

            stage.shutil.copy2 = wrapper

        observed = run_stage_main(target, source, configure)
        link = target / "docs/rulebooks/probe.pdf"
        result = {
            **observed,
            "targetIsSymlink": link.is_symlink(),
            "externalReferentExists": external.exists(),
            "externalBytesMatchSource": external.exists() and external.read_bytes() == expected,
        }
        assert result["exitCode"] == 0, result
        assert result["state"].get("observedSwapAfterPrewriteCheck"), result
        assert result["targetIsSymlink"] and result["externalBytesMatchSource"], result
        return result


def stage_intermediate_target_race() -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="candidate5-stage-intermediate-race-") as directory:
        root = Path(directory)
        source = make_source(root)
        target = make_target(root)
        (target / "docs").mkdir()
        external = root / "outside-intermediate"
        external.mkdir()
        parked = root / "parked-docs"
        expected = (source / "docs/rulebooks/probe.pdf").read_bytes()

        def configure(state: dict[str, Any]) -> None:
            original_sha = state["originalSha256"]
            original_copy = state["originalCopy2"]
            raced = False

            def sha_wrapper(path):
                nonlocal raced
                value = Path(path)
                if not raced and value == source / "docs/rulebooks/probe.pdf":
                    (target / "docs").rename(parked)
                    (target / "docs").symlink_to(external, target_is_directory=True)
                    raced = True
                    state["observedIntermediateSwapAfterTargetPathCheck"] = True
                return original_sha(path)

            def copy_wrapper(src, dst, *args, **kwargs):
                state["copyCalls"].append(
                    {"source": os.fspath(src), "target": os.fspath(dst)}
                )
                return original_copy(src, dst, *args, **kwargs)

            stage.sha256 = sha_wrapper
            stage.shutil.copy2 = copy_wrapper

        observed = run_stage_main(target, source, configure)
        escaped = external / "rulebooks/probe.pdf"
        result = {
            **observed,
            "intermediateTargetIsSymlink": (target / "docs").is_symlink(),
            "externalCopyExists": escaped.exists(),
            "externalBytesMatchSource": escaped.exists() and escaped.read_bytes() == expected,
        }
        assert result["exitCode"] == 0, result
        assert result["state"].get("observedIntermediateSwapAfterTargetPathCheck"), result
        assert result["intermediateTargetIsSymlink"] and result["externalBytesMatchSource"], result
        return result


def stage_source_file_race() -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="candidate5-stage-source-race-") as directory:
        root = Path(directory)
        source = make_source(root)
        target = make_target(root)
        source_file = source / "docs/rulebooks/probe.pdf"
        external = root / "outside-source.pdf"
        external.write_bytes(b"raced external source bytes\n")
        original_source = root / "original-source.pdf"

        def configure(state: dict[str, Any]) -> None:
            original_sha = state["originalSha256"]
            original_copy = state["originalCopy2"]
            raced = False

            def sha_wrapper(path):
                nonlocal raced
                value = Path(path)
                if not raced and value == source_file:
                    source_file.rename(original_source)
                    source_file.symlink_to(external)
                    raced = True
                    state["observedSourceSwapAfterTreeScan"] = True
                return original_sha(path)

            def copy_wrapper(src, dst, *args, **kwargs):
                state["copyCalls"].append(
                    {"source": os.fspath(src), "target": os.fspath(dst)}
                )
                return original_copy(src, dst, *args, **kwargs)

            stage.sha256 = sha_wrapper
            stage.shutil.copy2 = copy_wrapper

        observed = run_stage_main(target, source, configure)
        staged = target / "docs/rulebooks/probe.pdf"
        result = {
            **observed,
            "sourceBecameSymlink": source_file.is_symlink(),
            "stagedExternalBytes": staged.exists() and staged.read_bytes() == external.read_bytes(),
        }
        assert result["exitCode"] == 0, result
        assert result["state"].get("observedSourceSwapAfterTreeScan"), result
        assert result["sourceBecameSymlink"] and result["stagedExternalBytes"], result
        return result


def configure_prompt_fixture(root: Path) -> tuple[Path, Path, str]:
    audit = root / "docs/qa/implementation-readiness/correctness-audit"
    prompts = audit / "prompts"
    packets = audit / "packets"
    output_root = packets / "prompts"
    prompts.mkdir(parents=True)
    output_root.mkdir(parents=True)
    instruction = prompts / "packet-completeness-instructions.txt"
    instruction.write_text("fixed instructions\n", encoding="utf-8")
    packet = packets / "unit.json"
    packet.write_text('{"schemaVersion":1,"recordType":"source-packet","auditUnitId":"U1"}\n', encoding="utf-8")
    output_value = "docs/qa/implementation-readiness/correctness-audit/packets/prompts/out.txt"
    return instruction, packet, output_value


def prompt_output_race() -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="candidate5-prompt-output-race-") as directory:
        root = Path(directory)
        instruction, packet, output_value = configure_prompt_fixture(root)
        output = root / output_value
        external = root / "outside/output.txt"
        external.parent.mkdir()
        external.write_bytes(b"sentinel\n")
        original_root = prompt.ROOT
        original_audit = prompt.AUDIT_DIR
        original_instructions = prompt.INSTRUCTION_PATHS
        original_builder = prompt.canonical_prompt_bytes
        original_argv = sys.argv[:]
        state: dict[str, Any] = {}

        prompt.ROOT = root
        prompt.AUDIT_DIR = root / "docs/qa/implementation-readiness/correctness-audit"
        prompt.INSTRUCTION_PATHS = {"completeness": instruction, "blind": instruction}

        def builder(*args, **kwargs):
            expected = original_builder(*args, **kwargs)
            assert not output.exists() and not output.is_symlink()
            output.symlink_to(external)
            state["expectedSha256"] = hashlib.sha256(expected).hexdigest()
            state["swapAfterCanonicalOutputCheck"] = True
            return expected

        prompt.canonical_prompt_bytes = builder
        sys.argv = [
            os.fspath(PROMPT_PATH),
            "--mode",
            "completeness",
            "--packet",
            os.fspath(packet),
            "--output",
            output_value,
        ]
        stdout = io.StringIO()
        code = 0
        message = ""
        try:
            with contextlib.redirect_stdout(stdout):
                returned = prompt.main()
            code = int(returned)
        except SystemExit as exc:
            code = code_from_system_exit(exc.code)
            message = "" if exc.code is None else str(exc.code)
        finally:
            prompt.ROOT = original_root
            prompt.AUDIT_DIR = original_audit
            prompt.INSTRUCTION_PATHS = original_instructions
            prompt.canonical_prompt_bytes = original_builder
            sys.argv = original_argv
        parsed = json.loads(stdout.getvalue()) if stdout.getvalue().strip() else None
        result = {
            "exitCode": code,
            "message": message,
            "stdout": parsed,
            **state,
            "outputIsSymlink": output.is_symlink(),
            "externalSentinelOverwritten": external.read_bytes() != b"sentinel\n",
            "externalSha256": digest(external),
        }
        assert result["exitCode"] == 0, result
        assert result["swapAfterCanonicalOutputCheck"], result
        assert result["outputIsSymlink"] and result["externalSentinelOverwritten"], result
        assert result["externalSha256"] == result["expectedSha256"], result
        return result


def prompt_packet_race() -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="candidate5-prompt-packet-race-") as directory:
        root = Path(directory)
        instruction, packet, output_value = configure_prompt_fixture(root)
        output = root / output_value
        external = root / "outside/packet.json"
        external.parent.mkdir()
        forbidden_token = "downstreamPath"
        external.write_text(
            json.dumps(
                {
                    "schemaVersion": 1,
                    "recordType": "source-packet",
                    "auditUnitId": "U1",
                    "payload": f"raced {forbidden_token}",
                }
            )
            + "\n",
            encoding="utf-8",
        )
        parked = root / "parked-packet.json"
        original_root = prompt.ROOT
        original_audit = prompt.AUDIT_DIR
        original_instructions = prompt.INSTRUCTION_PATHS
        original_validator = prompt.validate_source_only_json
        original_argv = sys.argv[:]
        state: dict[str, Any] = {}
        prompt.ROOT = root
        prompt.AUDIT_DIR = root / "docs/qa/implementation-readiness/correctness-audit"
        prompt.INSTRUCTION_PATHS = {"completeness": instruction, "blind": instruction}

        def validator(path: Path) -> None:
            original_validator(path)
            packet.rename(parked)
            packet.symlink_to(external)
            state["swapAfterCanonicalAndSourceOnlyChecks"] = True

        prompt.validate_source_only_json = validator
        sys.argv = [
            os.fspath(PROMPT_PATH),
            "--mode",
            "completeness",
            "--packet",
            os.fspath(packet),
            "--output",
            output_value,
        ]
        stdout = io.StringIO()
        code = 0
        message = ""
        try:
            with contextlib.redirect_stdout(stdout):
                returned = prompt.main()
            code = int(returned)
        except SystemExit as exc:
            code = code_from_system_exit(exc.code)
            message = "" if exc.code is None else str(exc.code)
        finally:
            prompt.ROOT = original_root
            prompt.AUDIT_DIR = original_audit
            prompt.INSTRUCTION_PATHS = original_instructions
            prompt.validate_source_only_json = original_validator
            sys.argv = original_argv
        rendered = output.read_text(encoding="utf-8") if output.exists() else ""
        result = {
            "exitCode": code,
            "message": message,
            "stdout": json.loads(stdout.getvalue()) if stdout.getvalue().strip() else None,
            **state,
            "packetBecameSymlink": packet.is_symlink(),
            "outsideForbiddenPayloadInPrompt": forbidden_token in rendered,
        }
        assert result["exitCode"] == 0, result
        assert result["swapAfterCanonicalAndSourceOnlyChecks"], result
        assert result["packetBecameSymlink"] and result["outsideForbiddenPayloadInPrompt"], result
        return result


def real_inventory() -> dict[str, Any]:
    source_rows: dict[str, str] = {}
    target_rows: dict[str, str] = {}
    exclusions: list[str] = []
    symlinks: list[str] = []
    tree_counts: dict[str, int] = {}
    for relative_tree in TREES:
        tree = SOURCE_ROOT / relative_tree
        count = 0
        for path in sorted(tree.rglob("*")):
            rel_tree = path.relative_to(tree)
            rel_source = path.relative_to(SOURCE_ROOT).as_posix()
            if path.is_symlink():
                symlinks.append(rel_source)
                continue
            if "__pycache__" in rel_tree.parts or path.suffix in {".pyc", ".pyo"}:
                if path.is_file():
                    exclusions.append(rel_source)
                continue
            if path.is_file():
                source_rows[rel_source] = digest(path)
                count += 1
        tree_counts[relative_tree.as_posix()] = count
    for relative, expected_hash in source_rows.items():
        target = REPO / relative
        assert target.is_file() and not target.is_symlink(), relative
        target_rows[relative] = digest(target)
        assert target_rows[relative] == expected_hash, relative
    assert len(source_rows) == 1098, len(source_rows)
    assert not symlinks, symlinks
    return {
        "sourceRoot": os.fspath(SOURCE_ROOT),
        "targetRoot": os.fspath(REPO),
        "sourceFileCount": len(source_rows),
        "targetMatchedFileCount": len(target_rows),
        "treeCounts": tree_counts,
        "excludedCacheArtifactCount": len(exclusions),
        "excludedCacheArtifacts": exclusions,
        "symlinkCount": len(symlinks),
        "allHashesMatch": source_rows == target_rows,
    }


def worktree_evidence() -> dict[str, Any]:
    def git(*args: str) -> str:
        return subprocess.run(
            ["git", "-C", os.fspath(REPO), *args],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()

    show_toplevel = git("rev-parse", "--show-toplevel")
    git_dir_raw = git("rev-parse", "--git-dir")
    common_dir_raw = git("rev-parse", "--git-common-dir")
    git_dir = (REPO / git_dir_raw).resolve() if not Path(git_dir_raw).is_absolute() else Path(git_dir_raw).resolve()
    common_dir = (REPO / common_dir_raw).resolve() if not Path(common_dir_raw).is_absolute() else Path(common_dir_raw).resolve()
    return {
        "head": git("rev-parse", "HEAD"),
        "branch": git("branch", "--show-current"),
        "showToplevel": show_toplevel,
        "gitDir": os.fspath(git_dir),
        "gitCommonDir": os.fspath(common_dir),
        "stageModuleRoot": os.fspath(stage.ROOT),
        "promptModuleRoot": os.fspath(prompt.ROOT),
        "moduleRootsEqualWorktree": stage.ROOT == REPO and prompt.ROOT == REPO and show_toplevel == os.fspath(REPO),
        "moduleRootsDifferFromCommonDir": stage.ROOT.resolve() != common_dir and prompt.ROOT.resolve() != common_dir,
        "trackedAndUntrackedStatus": git("status", "--porcelain=v1", "--untracked-files=all"),
    }


def main() -> int:
    evidence = {
        "candidateHead": subprocess.run(
            ["git", "-C", os.fspath(REPO), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip(),
        "staticStageControls": static_stage_controls(),
        "aliasAndPromptStaticControls": alias_and_prompt_static_controls(),
        "raceProbes": {
            "stageFinalTargetSwap": stage_final_target_race(),
            "stageIntermediateTargetSwap": stage_intermediate_target_race(),
            "stageSourceFileSwap": stage_source_file_race(),
            "promptOutputFinalSwap": prompt_output_race(),
            "promptPacketFinalSwap": prompt_packet_race(),
        },
        "realSourceInventory": real_inventory(),
        "worktree": worktree_evidence(),
    }
    assert evidence["candidateHead"] == EXPECTED_HEAD, evidence["candidateHead"]
    assert evidence["worktree"]["moduleRootsEqualWorktree"], evidence["worktree"]
    assert evidence["worktree"]["moduleRootsDifferFromCommonDir"], evidence["worktree"]
    assert evidence["worktree"]["trackedAndUntrackedStatus"] == "", evidence["worktree"]
    print(json.dumps(evidence, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
