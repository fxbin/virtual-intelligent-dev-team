#!/usr/bin/env python3
"""Inspect machine-readable automation state snapshots and surface the next resume action."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
AUTOMATION_STATE_SCRIPT = SCRIPT_DIR / "automation_state.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


automation_state = load_module(
    "virtual_team_inspect_automation_state_module",
    AUTOMATION_STATE_SCRIPT,
)


DEFAULT_STATE_FILES = [
    ".skill-auto/state",
    "evals/release-gate/automation-state.json",
    ".skill-post-release/decisions/automation-state.json",
]


def load_state(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"{path} must contain a JSON object")
    automation_state.response_contract.validate_automation_state(payload)
    return payload


def discover_state_files(repo_root: Path) -> list[Path]:
    candidates: list[Path] = []
    state_dir = repo_root / ".skill-auto" / "state"
    if state_dir.exists():
        candidates.extend(sorted(state_dir.glob("*.json")))
    for rel in DEFAULT_STATE_FILES[1:]:
        target = repo_root / rel
        if target.exists():
            candidates.append(target)
    deduped: list[Path] = []
    seen: set[str] = set()
    for item in candidates:
        resolved = str(item.resolve())
        if resolved in seen:
            continue
        seen.add(resolved)
        deduped.append(item.resolve())
    return deduped


def state_sort_key(item: tuple[Path, dict[str, object]]) -> tuple[str, str, str]:
    path, payload = item
    return (
        str(payload.get("generated_at", "")),
        str(payload.get("run_id", "")),
        str(path),
    )


def summarize_state(path: Path, payload: dict[str, object], repo_root: Path) -> dict[str, object]:
    return {
        "path": automation_state.relative_path(path, repo_root),
        "generated_at": str(payload.get("generated_at", "")),
        "run_id": str(payload.get("run_id", "")),
        "source_workflow": str(payload.get("source_workflow", "")),
        "state_kind": str(payload.get("state_kind", "")),
        "phase": str(payload.get("phase", "")),
        "status": str(payload.get("status", "")),
        "decision": str(payload.get("decision", "")),
        "resume_anchor": str(payload.get("resume_anchor", "")),
    }


def recommend_resume_command(payload: dict[str, object]) -> str:
    state_kind = str(payload.get("state_kind", "")).strip()
    source_workflow = str(payload.get("source_workflow", "")).strip()
    if state_kind == "auto-run-setup":
        return "python scripts/run_auto_workflow.py --mode go --plan .skill-auto/auto-run-plan.json --pretty"
    if state_kind == "release-gate-result":
        return (
            "python scripts/run_release_gate.py --output-dir evals/release-gate "
            "--iteration-workspace .skill-iterations --pretty"
        )
    if state_kind == "post-release-feedback-result":
        return (
            "python scripts/evaluate_post_release_feedback.py "
            "--report .skill-post-release/current-signals.json --pretty"
        )
    if source_workflow in {
        "root-cause-remediate",
        "ship-hold-remediate",
        "post-release-close-loop",
    }:
        return "python scripts/run_auto_workflow.py --mode go --plan .skill-auto/auto-run-plan.json --pretty"
    return ""


def inspect_automation_state(
    *,
    repo_root: Path,
    workflow: str | None = None,
    run_id: str | None = None,
    state_path: Path | None = None,
) -> dict[str, object]:
    states: list[tuple[Path, dict[str, object]]] = []
    for candidate in discover_state_files(repo_root):
        payload = load_state(candidate)
        states.append((candidate, payload))

    if state_path is not None:
        resolved = state_path.resolve()
        selected = (resolved, load_state(resolved))
        selection_mode = "path"
    else:
        filtered = states
        if workflow:
            filtered = [
                item for item in filtered if str(item[1].get("source_workflow", "")).strip() == workflow
            ]
        if run_id:
            filtered = [item for item in filtered if str(item[1].get("run_id", "")).strip() == run_id]
        if not filtered:
            raise RuntimeError("no automation state matched the requested filters")
        selected = max(filtered, key=state_sort_key)
        selection_mode = "run-id" if run_id else ("workflow" if workflow else "latest")

    selected_path, selected_payload = selected
    command = recommend_resume_command(selected_payload)
    return {
        "ok": True,
        "selection_mode": selection_mode,
        "selected_state_path": automation_state.relative_path(selected_path, repo_root),
        "selected_state": selected_payload,
        "available_state_count": len(states),
        "resume_ready": command != "",
        "recommended_resume_command": command,
        "recommended_next_step": str(selected_payload.get("recommended_next_step", "")),
        "resume_anchor": str(selected_payload.get("resume_anchor", "")),
        "available_states": [
            summarize_state(path, payload, repo_root) for path, payload in sorted(states, key=state_sort_key)
        ],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inspect automation state snapshots and suggest the next resume action.")
    parser.add_argument("--repo", default=".", help="Repository root.")
    parser.add_argument("--workflow", help="Filter by source workflow.")
    parser.add_argument("--run-id", help="Select an explicit run id.")
    parser.add_argument("--state", help="Read a specific automation state path.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    repo_root = Path(args.repo).resolve()
    try:
        result = inspect_automation_state(
            repo_root=repo_root,
            workflow=args.workflow,
            run_id=args.run_id,
            state_path=Path(args.state).resolve() if args.state else None,
        )
        exit_code = 0
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
