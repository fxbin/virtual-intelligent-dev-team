#!/usr/bin/env python3
"""Run one bounded-iteration state-machine cycle and write local artifacts."""

from __future__ import annotations

import argparse
from datetime import datetime
import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
BENCHMARK_SCRIPT = SCRIPT_DIR / "run_benchmarks.py"
REGISTER_SCRIPT = SCRIPT_DIR / "register_benchmark_baseline.py"
INIT_SCRIPT = SCRIPT_DIR / "init_iteration_round.py"
COMPARE_SCRIPT = SCRIPT_DIR / "compare_benchmark_results.py"
PROMOTE_SCRIPT = SCRIPT_DIR / "promote_iteration_baseline.py"
SYNC_SCRIPT = SCRIPT_DIR / "sync_distilled_patterns.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


baseline_registry = load_module("virtual_team_baseline_registry", REGISTER_SCRIPT)
iteration_init = load_module("virtual_team_iteration_init", INIT_SCRIPT)
benchmark_compare = load_module("virtual_team_benchmark_compare", COMPARE_SCRIPT)
baseline_promotion = load_module("virtual_team_baseline_promotion", PROMOTE_SCRIPT)
pattern_sync = load_module("virtual_team_pattern_sync", SYNC_SCRIPT)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def round_sort_key(path: Path) -> tuple[int, str]:
    suffix = path.name.removeprefix("round-")
    try:
        return (int(suffix), path.name)
    except ValueError:
        return (10**9, path.name)


def load_registry(workspace: Path) -> dict[str, object]:
    registry_path = workspace / "baselines" / "registry.json"
    if not registry_path.exists():
        raise RuntimeError("baseline registry not found; run register_benchmark_baseline.py first")
    return baseline_registry.load_json(registry_path)


def resolve_baseline_report(workspace: Path, label: str) -> Path:
    registry = load_registry(workspace)
    items = registry.get("baselines", [])
    if not isinstance(items, list):
        raise RuntimeError("baseline registry is malformed")
    for item in items:
        if not isinstance(item, dict):
            continue
        if item.get("label") != label:
            continue
        stored_report = item.get("stored_report")
        if not isinstance(stored_report, str) or stored_report.strip() == "":
            raise RuntimeError(f"baseline {label} has no stored report")
        return Path(stored_report).resolve()
    raise RuntimeError(f"baseline label not found: {label}")


def resolve_candidate_repo(candidate_repo: Path | None) -> Path:
    return candidate_repo.resolve() if candidate_repo is not None else SKILL_DIR


def resolve_benchmark_script(candidate_repo: Path | None) -> Path:
    benchmark_root = resolve_candidate_repo(candidate_repo)
    benchmark_script = benchmark_root / "scripts" / "run_benchmarks.py"
    if not benchmark_script.exists():
        raise RuntimeError(f"benchmark script not found in candidate repo: {benchmark_script}")
    return benchmark_script


def normalize_command(command: str, output_dir: Path) -> str:
    normalized = command.replace("{output_dir}", str(output_dir))
    stripped = normalized.lstrip()
    if stripped.startswith("python "):
        prefix_len = len(normalized) - len(stripped)
        normalized = normalized[:prefix_len] + sys.executable + stripped[len("python") :]
    return normalized


def is_git_repo(path: Path) -> bool:
    if (path / ".git").exists():
        return True
    probe = run_process(["git", "rev-parse", "--show-toplevel"], cwd=path)
    if not bool(probe["passed"]):
        return False
    try:
        return Path(str(probe["stdout"]).strip()).resolve() == path.resolve()
    except (OSError, RuntimeError):
        return False


def run_process(command: list[str], cwd: Path) -> dict[str, object]:
    proc = subprocess.run(
        command,
        cwd=str(cwd),
        text=True,
        capture_output=True,
        encoding="utf-8",
        check=False,
    )
    return {
        "command": command,
        "cwd": str(cwd),
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "passed": proc.returncode == 0,
    }


def run_checked_process(command: list[str], cwd: Path) -> dict[str, object]:
    result = run_process(command, cwd)
    if not result["passed"]:
        raise RuntimeError(str(result["stdout"]) + str(result["stderr"]))
    return result


def resolve_command_shell() -> tuple[str, str]:
    """Return an available POSIX shell and the flag used to execute one command.

    zsh remains preferred where it exists for backwards compatibility, but
    production/CI hosts are not required to install it. Bash is the normal
    fallback and POSIX sh is the final portable fallback.
    """
    for name in ("zsh", "bash"):
        path = shutil.which(name)
        if path:
            return path, "-lc"
    path = shutil.which("sh")
    if path:
        return path, "-c"
    raise RuntimeError("no supported command shell found (expected zsh, bash, or sh)")


def run_command(command: str, cwd: Path) -> dict[str, object]:
    normalized_command = command
    stripped = normalized_command.lstrip()
    if stripped.startswith("python "):
        prefix_len = len(normalized_command) - len(stripped)
        normalized_command = normalized_command[:prefix_len] + sys.executable + stripped[len("python") :]
    shell_path, shell_flag = resolve_command_shell()
    proc = subprocess.run(
        [shell_path, shell_flag, normalized_command],
        cwd=str(cwd),
        text=True,
        capture_output=True,
        encoding="utf-8",
        check=False,
    )
    result = {
        "command": normalized_command,
        "shell": shell_path,
        "cwd": str(cwd),
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "passed": proc.returncode == 0,
    }
    if proc.returncode != 0:
        raise RuntimeError(proc.stdout + proc.stderr)
    return result


def write_if_present(path: Path, content: str) -> str | None:
    if content == "":
        return None
    write_text(path, content)
    return str(path)


def capture_candidate_snapshot(round_dir: Path, candidate_root: Path, stage: str) -> dict[str, object]:
    snapshot_dir = round_dir / "workspace-snapshots" / stage
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    payload: dict[str, object] = {
        "stage": stage,
        "captured_at": datetime.now().isoformat(timespec="seconds"),
        "candidate_root": str(candidate_root),
        "snapshot_dir": str(snapshot_dir),
    }
