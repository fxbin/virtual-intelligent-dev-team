#!/usr/bin/env python3
"""Resume automation from the latest state via a guarded dry-run or explicit execution."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import shlex
import shutil
import subprocess


SCRIPT_DIR = Path(__file__).resolve().parent
INSPECT_AUTOMATION_STATE_SCRIPT = SCRIPT_DIR / "inspect_automation_state.py"
ALLOWED_SCRIPT_PATHS = {
    "scripts/run_auto_workflow.py",
    "scripts/run_release_gate.py",
    "scripts/evaluate_post_release_feedback.py",
    "scripts/init_technical_governance.py",
    "scripts/init_product_delivery.py",
    "scripts/init_iteration_round.py",
    "scripts/run_iteration_loop.py",
}


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


automation_state_inspector = load_module(
    "virtual_team_resume_from_automation_state_inspector",
    INSPECT_AUTOMATION_STATE_SCRIPT,
)


def parse_command(command: str) -> list[str]:
    try:
        return shlex.split(command)
    except ValueError as exc:
        raise RuntimeError(f"unable to parse recommended command: {exc}") from exc


def allowed_command_prefixes() -> list[str]:
    return sorted(f"python {path}" for path in ALLOWED_SCRIPT_PATHS)


def evaluate_command_guard(command: str) -> tuple[bool, str | None]:
    tokens = parse_command(command)
    if len(tokens) < 2:
        return False, None
    if tokens[0] not in {"python", "python3"}:
        return False, None
    script_path = Path(tokens[1]).as_posix()
    return script_path in ALLOWED_SCRIPT_PATHS, script_path


def normalize_command_tokens(tokens: list[str]) -> list[str]:
    normalized = list(tokens)
    if normalized and normalized[0] == "python" and shutil.which("python") is None and shutil.which("python3"):
        normalized[0] = "python3"
    return normalized


def build_resume_payload(
    *,
    repo_root: Path,
    workflow: str | None = None,
    run_id: str | None = None,
    state_path: Path | None = None,
    execute: bool = False,
) -> dict[str, object]:
    inspection = automation_state_inspector.inspect_automation_state(
        repo_root=repo_root,
        workflow=workflow,
        run_id=run_id,
        state_path=state_path,
    )
    decision_card = inspection.get("decision_card", {})
    if not isinstance(decision_card, dict):
        decision_card = {}
    recommended_command = str(
        decision_card.get("recommended_command") or inspection.get("recommended_resume_command") or ""
    ).strip()
    command_allowed, allowed_script = evaluate_command_guard(recommended_command) if recommended_command else (False, None)
    payload: dict[str, object] = {
        "ok": True,
        "repo_root": str(repo_root),
        "execute_requested": execute,
        "dry_run": not execute,
        "selected_state_path": inspection.get("selected_state_path"),
        "selection_mode": inspection.get("selection_mode"),
        "decision_card": decision_card,
        "recommended_command": recommended_command,
        "command_allowed": command_allowed,
        "allowed_script": allowed_script,
        "allowed_command_prefixes": allowed_command_prefixes(),
        "execution": {
            "executed": False,
            "returncode": None,
            "stdout": "",
            "stderr": "",
        },
    }
    if recommended_command == "":
        payload["ok"] = False
        payload["error"] = "no recommended command is available for the selected automation state"
        return payload
    if not command_allowed:
        payload["ok"] = False
        payload["error"] = "recommended command is outside the guarded automation resume allowlist"
        return payload
    if not execute:
        payload["next_action"] = "pass --execute to run the recommended command"
        return payload

    tokens = normalize_command_tokens(parse_command(recommended_command))
    proc = subprocess.run(
        tokens,
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    payload["ok"] = proc.returncode == 0
    payload["execution"] = {
        "executed": True,
        "command": tokens,
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }
    if proc.returncode != 0:
        payload["error"] = "resume command exited with a non-zero status"
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Resume automation state through a guarded dry-run or explicit execution."
    )
    parser.add_argument("--repo", default=".", help="Repository root.")
    parser.add_argument("--workflow", help="Filter by source workflow.")
    parser.add_argument("--run-id", help="Select an explicit run id.")
    parser.add_argument("--state", help="Read a specific automation state path.")
    parser.add_argument("--execute", action="store_true", help="Run the recommended command after guard checks pass.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    repo_root = Path(args.repo).resolve()
    try:
        result = build_resume_payload(
            repo_root=repo_root,
            workflow=args.workflow,
            run_id=args.run_id,
            state_path=Path(args.state).resolve() if args.state else None,
            execute=args.execute,
        )
        exit_code = 0 if bool(result.get("ok")) else 2
    except Exception as exc:
        result = {"ok": False, "error": str(exc)}
        exit_code = 2

    if args.pretty:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(result, ensure_ascii=False))
    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
