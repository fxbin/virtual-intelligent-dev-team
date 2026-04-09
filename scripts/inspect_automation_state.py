#!/usr/bin/env python3
"""Inspect automation state snapshots and derive the next resume/playbook decision."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import shlex


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
    ".skill-post-release/decisions",
]
PLAYBOOK_PATHS = {
    "auto-run": "references/auto-run-playbook.md",
    "root-cause": "references/root-cause-escalation-playbook.md",
    "iteration": "references/iteration-protocol.md",
    "release-gate": "references/release-gate-playbook.md",
    "post-release": "references/post-release-feedback-playbook.md",
    "technical-governance": "references/technical-governance-playbook.md",
    "decision-matrix": "references/automation-resume-decision-matrix.md",
}


def load_state(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"{path} must contain a JSON object")
    automation_state.response_contract.validate_automation_state(payload)
    return payload


def load_optional_json(path: Path) -> dict[str, object] | None:
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    if not isinstance(payload, dict):
        return None
    return payload


def discover_state_files(repo_root: Path) -> list[Path]:
    candidates: list[Path] = []
    state_dir = repo_root / ".skill-auto" / "state"
    if state_dir.exists():
        candidates.extend(sorted(state_dir.glob("*.json")))
    release_gate_state = repo_root / "evals" / "release-gate" / "automation-state.json"
    if release_gate_state.exists():
        candidates.append(release_gate_state)
    post_release_dir = repo_root / ".skill-post-release" / "decisions"
    if post_release_dir.exists():
        candidates.extend(sorted(post_release_dir.rglob("automation-state.json")))
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


def resolve_related_paths(repo_root: Path, payload: dict[str, object]) -> list[Path]:
    state_paths = payload.get("state_paths", {})
    if not isinstance(state_paths, dict):
        return []
    raw_related = state_paths.get("related", [])
    if not isinstance(raw_related, list):
        return []
    paths: list[Path] = []
    for item in raw_related:
        text = str(item).strip()
        if text == "":
            continue
        paths.append(automation_state.resolve_path(repo_root, text))
    return paths


def load_companion_payload(repo_root: Path, payload: dict[str, object]) -> tuple[str | None, dict[str, object] | None]:
    for candidate in resolve_related_paths(repo_root, payload):
        if candidate.suffix != ".json":
            continue
        loaded = load_optional_json(candidate)
        if loaded is not None:
            return automation_state.relative_path(candidate, repo_root), loaded
    state_kind = str(payload.get("state_kind", "")).strip()
    fallback_files = {
        "release-gate-result": "evals/release-gate/release-gate-results.json",
        "post-release-feedback-result": ".skill-post-release/decisions/post-release-feedback-result.json",
        "auto-run-setup": ".skill-auto/auto-run-plan.json",
        "auto-run-go": ".skill-auto/last-run.json",
    }
    fallback = fallback_files.get(state_kind)
    if fallback is None:
        return None, None
    target = automation_state.resolve_path(repo_root, fallback)
    loaded = load_optional_json(target)
    if loaded is None:
        return None, None
    return automation_state.relative_path(target, repo_root), loaded


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


def build_playbook_list(keys: list[str]) -> list[str]:
    values: list[str] = []
    for key in keys:
        path = PLAYBOOK_PATHS.get(key)
        if path is not None:
            values.append(path)
    return values


def first_command(commands: object) -> str:
    if not isinstance(commands, list):
        return ""
    for item in commands:
        text = str(item).strip()
        if text:
            return text
    return ""


def command_targets_script(command: str, script_path: str) -> bool:
    try:
        tokens = shlex.split(command)
    except ValueError:
        return False
    if len(tokens) < 2:
        return False
    return Path(tokens[1]).as_posix() == script_path


def preferred_command(commands: object, preferred_scripts: list[str]) -> str:
    if not isinstance(commands, list):
        return ""
    for script_path in preferred_scripts:
        for item in commands:
            text = str(item).strip()
            if text and command_targets_script(text, script_path):
                return text
    return first_command(commands)


def companion_follow_up(companion_payload: dict[str, object] | None) -> dict[str, object]:
    if not isinstance(companion_payload, dict):
        return {}
    follow_up = companion_payload.get("follow_up", {})
    return follow_up if isinstance(follow_up, dict) else {}


def build_resume_decision(
    *,
    repo_root: Path,
    payload: dict[str, object],
    companion_path: str | None,
    companion_payload: dict[str, object] | None,
) -> dict[str, object]:
    state_kind = str(payload.get("state_kind", "")).strip()
    source_workflow = str(payload.get("source_workflow", "")).strip()
    decision = str(payload.get("decision", "")).strip()
    resume_anchor = str(payload.get("resume_anchor", "")).strip()
    recommended_command = recommend_resume_command(payload)
    blocking_conditions: list[str] = []
    playbooks = ["decision-matrix"]
    decision_id = "manual-review"
    decision_label = "Review the current automation state manually"
    decision_reason = str(payload.get("recommended_next_step", "")).strip() or "No specialized resume path was inferred from this state."
    resume_strategy = "manual-review"
    follow_up_artifacts = [automation_state.relative_path(path, repo_root) for path in resolve_related_paths(repo_root, payload)]
    follow_up = companion_follow_up(companion_payload)

    if state_kind == "auto-run-setup":
        decision_id = "resume-explicit-go"
        decision_label = "Continue from explicit auto setup into go"
        decision_reason = "The setup phase is already materialized, so the next bounded step is the explicit go command."
        resume_strategy = "command-resume"
        blocking_conditions = [
            "The saved auto-run plan must still match the intended request before go executes.",
            "Destructive git actions still remain outside the automatic boundary.",
        ]
        if source_workflow == "root-cause-remediate":
            playbooks += ["auto-run", "root-cause", "iteration"]
        elif source_workflow == "ship-hold-remediate":
            playbooks += ["auto-run", "release-gate"]
        elif source_workflow == "post-release-close-loop":
            playbooks += ["auto-run", "post-release"]
        else:
            playbooks += ["auto-run"]
    elif state_kind == "release-gate-result":
        if decision == "ship":
            bootstrap = follow_up.get("post_release_bootstrap", {})
            if not isinstance(bootstrap, dict):
                bootstrap = {}
            decision_id = "release-ship-continue-post-release"
            decision_label = "Continue from ship into post-release feedback"
            decision_reason = "The release gate closed successfully, so the next durable loop should move into post-release telemetry and feedback."
            resume_strategy = "playbook-follow-through"
            recommended_command = str(bootstrap.get("recommended_command", "")).strip() or recommended_command
            resume_anchor = str(bootstrap.get("resume_anchor", "")).strip() or resume_anchor
            playbooks += ["release-gate", "post-release"]
            blocking_conditions = [
                "Do not reopen remediation unless post-release signals justify it.",
            ]
            artifacts = bootstrap.get("artifacts", [])
            if isinstance(artifacts, list):
                follow_up_artifacts.extend(str(item) for item in artifacts if str(item).strip())
        else:
            brief_json = str(follow_up.get("brief_json", "")).strip()
            brief_payload = (
                load_optional_json(automation_state.resolve_path(repo_root, brief_json))
                if brief_json
                else None
            )
            brief_commands = (brief_payload or {}).get("recommended_commands")
            decision_id = "release-hold-reopen-iteration"
            decision_label = "Release hold requires bounded remediation"
            decision_reason = "The release gate is still blocked, so resume should continue through the hold brief and bounded iteration path."
            resume_strategy = "playbook-follow-through"
            recommended_command = preferred_command(
                brief_commands,
                [
                    "scripts/init_iteration_round.py",
                    "scripts/run_iteration_loop.py",
                    "scripts/run_release_gate.py",
                ],
            ) or recommended_command
            playbooks += ["release-gate", "iteration"]
            blocking_conditions = [
                "Release blockers remain unresolved until the hold brief evidence is satisfied.",
            ]
            if brief_json:
                follow_up_artifacts.append(brief_json)
    elif state_kind == "post-release-feedback-result":
        follow_up_commands = follow_up.get("recommended_commands")
        if decision == "monitor":
            decision_id = "post-release-monitor-continue"
            decision_label = "Stay in the post-release observation loop"
            decision_reason = "Signals remain inside watch thresholds, so the next step is another scheduled post-release checkpoint."
            resume_strategy = "playbook-follow-through"
            recommended_command = preferred_command(
                follow_up_commands,
                ["scripts/evaluate_post_release_feedback.py"],
            ) or recommended_command
            playbooks += ["post-release"]
            blocking_conditions = [
                "Do not reopen bounded iteration without new shipped evidence.",
            ]
        elif decision == "iterate":
            decision_id = "post-release-reopen-iteration"
            decision_label = "Reopen bounded iteration from shipped evidence"
            decision_reason = "Post-release evidence now justifies a corrective slice and a new bounded remediation loop."
            resume_strategy = "playbook-follow-through"
            recommended_command = preferred_command(
                follow_up_commands,
                [
                    "scripts/init_product_delivery.py",
                    "scripts/run_release_gate.py",
                ],
            ) or recommended_command
            playbooks += ["post-release", "iteration"]
            blocking_conditions = [
                "Carry the shipped evidence and feedback ledger into the corrective slice before rerunning acceptance.",
            ]
        elif decision == "escalate":
            decision_id = "post-release-escalate-governance"
            decision_label = "Escalate shipped feedback into governance"
            decision_reason = "The shipped version reveals production-level control gaps, so the next path should include governance escalation."
            resume_strategy = "handoff"
            recommended_command = preferred_command(
                follow_up_commands,
                [
                    "scripts/init_technical_governance.py",
                    "scripts/run_release_gate.py",
                ],
            ) or recommended_command
            playbooks += ["post-release", "technical-governance"]
            blocking_conditions = [
                "Do not continue normal rollout while governance escalation is unresolved.",
            ]
        else:
            recommended_command = first_command(follow_up_commands) or recommended_command
            playbooks += ["post-release"]

    return {
        "decision_id": decision_id,
        "decision_label": decision_label,
        "decision_reason": decision_reason,
        "resume_strategy": resume_strategy,
        "recommended_command": recommended_command,
        "resume_anchor": resume_anchor,
        "playbooks": build_playbook_list(playbooks),
        "blocking_conditions": blocking_conditions,
        "handoff_target": str(payload.get("handoff_target", "")),
        "follow_up_artifacts": sorted({item for item in follow_up_artifacts if str(item).strip()}),
        "companion_payload_path": companion_path,
    }


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
    companion_path, companion_payload = load_companion_payload(repo_root, selected_payload)
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
        "decision_card": build_resume_decision(
            repo_root=repo_root,
            payload=selected_payload,
            companion_path=companion_path,
            companion_payload=companion_payload,
        ),
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
