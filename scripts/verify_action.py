#!/usr/bin/env python3
"""Pre-action verification for virtual-intelligent-dev-team process decisions."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
ROUTE_SCRIPT = SCRIPT_DIR / "route_request.py"
DEFAULT_CONFIG_PATH = SKILL_DIR / "references" / "routing-rules.json"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


route_request = load_module("virtual_team_verify_action_route_request", ROUTE_SCRIPT)


def load_config(config_path: Path) -> dict[str, object]:
    config = route_request.load_config(config_path)
    governance = config.setdefault("governance", {})
    if isinstance(governance, dict):
        fast_track = governance.setdefault("fast_track_control", {})
        if isinstance(fast_track, dict):
            fast_track["write_event_log"] = False
    return config


def _details_for_process_skill(result: dict[str, object], process_skill: str) -> dict[str, object]:
    process_skills = result.get("process_skills", [])
    reason = result.get("reason", {})
    process_hits = reason.get("process_skill_hits", {})
    commands: list[str] = []
    references: list[str] = []
    for item in result.get("process_plan", []):
        if isinstance(item, dict) and item.get("skill") == process_skill:
            commands = item.get("commands", []) if isinstance(item.get("commands"), list) else []
            reference = item.get("reference")
            if isinstance(reference, str) and reference:
                references = [reference]
            break
    return {
        "requested_process_skill": process_skill,
        "recommended_process_skills": process_skills,
        "matching_reason_hits": process_hits.get(process_skill, []),
        "commands": commands,
        "references": references,
    }


def _get_process_plan_entry(result: dict[str, object], skill_name: str) -> dict[str, object]:
    for item in result.get("process_plan", []):
        if isinstance(item, dict) and item.get("skill") == skill_name:
            return item
    return {}


def _verify_process_skill(result: dict[str, object], process_skill: str) -> dict[str, object]:
    allowed = process_skill in result.get("process_skills", [])
    details = _details_for_process_skill(result, process_skill)
    if allowed:
        summary = f"Process skill `{process_skill}` is allowed for this request."
        next_step = f"Use the `{process_skill}` plan entry from process_plan before execution."
    else:
        summary = f"Process skill `{process_skill}` is not recommended for this request."
        next_step = "Follow the recommended process_skills from the router, or reroute with a more explicit request."
    return {
        "allowed": allowed,
        "summary": summary,
        "details": details,
        "recommended_next_step": next_step,
    }


def _verify_git_workflow(result: dict[str, object]) -> dict[str, object]:
    allowed = bool(result.get("needs_git_workflow"))
    plan_entry = _get_process_plan_entry(result, "git-workflow")
    git_profile = result.get("git_workflow_profile", {})
    repo_strategy = (
        git_profile.get("repo_strategy", {})
        if isinstance(git_profile, dict)
        else {}
    )
    commands = plan_entry.get("commands", []) if isinstance(plan_entry.get("commands"), list) else []
    templates = git_profile.get("templates", {}) if isinstance(git_profile, dict) else {}
    if allowed:
        summary = "Git workflow guardrail flow is required for this request."
        next_step = "Start from the git-workflow plan entry, run the guardrail checks in order, and do not skip G0-G4."
    else:
        summary = "Git workflow guardrail flow is not required for this request."
        next_step = "Do not force commit / push / PR handling unless the request explicitly includes delivery workflow actions."
    return {
        "allowed": allowed,
        "summary": summary,
        "details": {
            "needs_git_workflow": bool(result.get("needs_git_workflow")),
            "recommended_process_skills": result.get("process_skills", []),
            "commands": commands,
            "repo_strategy": repo_strategy,
            "templates": templates,
        },
        "recommended_next_step": next_step,
    }


def _verify_worktree(result: dict[str, object]) -> dict[str, object]:
    allowed = bool(result.get("needs_worktree"))
    plan_entry = _get_process_plan_entry(result, "using-git-worktrees")
    commands = plan_entry.get("commands", []) if isinstance(plan_entry.get("commands"), list) else []
    git_profile = result.get("git_workflow_profile", {})
    repo_strategy = (
        git_profile.get("repo_strategy", {})
        if isinstance(git_profile, dict)
        else {}
    )
    if allowed:
        summary = "Git worktree isolation is required for this request."
        next_step = "Use the worktree plan entry first so execution stays isolated from the main working tree."
    else:
        summary = "Git worktree isolation is not required for this request."
        next_step = "Stay in the current working tree unless the request explicitly asks for isolation or parallel task branches."
    return {
        "allowed": allowed,
        "summary": summary,
        "details": {
            "needs_worktree": bool(result.get("needs_worktree")),
            "recommended_process_skills": result.get("process_skills", []),
            "commands": commands,
            "repo_strategy": repo_strategy,
            "base_branch": str(repo_strategy.get("base_branch", "main")),
        },
        "recommended_next_step": next_step,
    }


def _verify_lead_assignment(
    result: dict[str, object], lead_agent: str, assistant_agents: list[str]
) -> dict[str, object]:
    expected_lead = str(result.get("lead_agent"))
    expected_assistants = result.get("assistant_agents", [])
    if not isinstance(expected_assistants, list):
        expected_assistants = []
    provided_assistants = [agent for agent in assistant_agents if agent]
    unexpected_assistants = [agent for agent in provided_assistants if agent not in expected_assistants]
    missing_assistants = [agent for agent in expected_assistants if agent not in provided_assistants]
    allowed = lead_agent == expected_lead and len(unexpected_assistants) == 0
    if allowed:
        summary = "Lead assignment matches the router recommendation."
        next_step = "Keep the semantic lead, then add only the recommended assistants that are actually needed."
    else:
        summary = "Lead assignment conflicts with the router recommendation."
        next_step = f"Switch lead to `{expected_lead}` and recheck assistants against the recommended set."
    return {
        "allowed": allowed,
        "summary": summary,
        "details": {
            "requested_lead_agent": lead_agent,
            "requested_assistant_agents": provided_assistants,
            "expected_lead_agent": expected_lead,
            "expected_assistant_agents": expected_assistants,
            "unexpected_assistant_agents": unexpected_assistants,
            "missing_recommended_assistants": missing_assistants,
        },
        "recommended_next_step": next_step,
    }


def _verify_release_gate(result: dict[str, object]) -> dict[str, object]:
    allowed = bool(result.get("needs_release_gate"))
    entry = _get_process_plan_entry(result, "release-gate")
    commands = entry.get("commands", []) if isinstance(entry.get("commands"), list) else []
    decisions = entry.get("decisions", []) if isinstance(entry.get("decisions"), list) else []
    artifacts = entry.get("artifacts", []) if isinstance(entry.get("artifacts"), list) else []
    if allowed:
        summary = "Formal release gate is required for this request."
        next_step = "Run `python scripts/run_release_gate.py --output-dir evals/release-gate --pretty` before answering ship or hold."
    else:
        summary = "Formal release gate is not required for this request."
        next_step = "Do not force release-gate flow unless the user is explicitly asking for ship/hold or formal acceptance."
    return {
        "allowed": allowed,
        "summary": summary,
        "details": {
            "needs_release_gate": bool(result.get("needs_release_gate")),
            "recommended_process_skills": result.get("process_skills", []),
            "commands": commands,
            "decisions": decisions,
            "artifacts": artifacts,
        },
        "recommended_next_step": next_step,
    }


def _verify_iteration(result: dict[str, object]) -> dict[str, object]:
    allowed = bool(result.get("needs_iteration"))
    profile = result.get("iteration_profile", {})
    if not isinstance(profile, dict):
        profile = {}
    if allowed:
        summary = "Bounded iteration is enabled for this request."
        next_step = "Use the iteration profile and process_plan to keep the loop evidence-driven and bounded."
    else:
        summary = "Bounded iteration is not required for this request."
        next_step = "Stay on the direct execution path unless the user explicitly asks for benchmarking, retries, or another round."
    return {
        "allowed": allowed,
        "summary": summary,
        "details": {
            "needs_iteration": bool(result.get("needs_iteration")),
            "workflow_bundle": result.get("workflow_bundle"),
            "progress_anchor_recommended": result.get("progress_anchor_recommended"),
            "resume_artifacts": result.get("resume_artifacts", []),
            "round_caps": {
                "online": int(profile.get("round_cap_online", 0)),
                "offline": int(profile.get("round_cap_offline", 0)),
            },
            "max_same_hypothesis_retries": int(profile.get("max_same_hypothesis_retries", 0)),
            "require_objective_signal": bool(profile.get("require_objective_signal", False)),
            "allowed_decisions": profile.get("allowed_decisions", []),
            "required_artifacts": profile.get("required_artifacts", []),
        },
        "recommended_next_step": next_step,
    }


def _verify_workflow_bundle(result: dict[str, object]) -> dict[str, object]:
    bundle = result.get("workflow_bundle")
    progress_anchor = result.get("progress_anchor_recommended")
    resume_artifacts = result.get("resume_artifacts", [])
    workflow_steps = result.get("workflow_steps", [])
    allowed = isinstance(bundle, str) and bundle not in {"", "direct-execution"}
    if allowed:
        summary = f"Workflow bundle `{bundle}` is active for this request."
        next_step = "Follow the workflow bundle first, then use the recommended progress anchor to resume safely."
    else:
        summary = "No special workflow bundle is required for this request."
        next_step = "Keep execution lightweight and follow the lead plus active process skills only."
    return {
        "allowed": allowed,
        "summary": summary,
        "details": {
            "workflow_bundle": bundle,
            "progress_anchor_recommended": progress_anchor,
            "resume_artifacts": resume_artifacts,
            "workflow_steps": workflow_steps,
        },
        "recommended_next_step": next_step,
    }


def verify_action(
    *,
    text: str,
    config: dict[str, object],
    repo_path: Path,
    check: str,
    process_skill: str | None = None,
    lead_agent: str | None = None,
    assistant_agents: list[str] | None = None,
) -> dict[str, object]:
    if assistant_agents is None:
        assistant_agents = []
    result = route_request.route_request(text=text, config=config, repo_path=repo_path)

    if check == "process-skill":
        if not process_skill:
            raise ValueError("--process-skill is required for check=process-skill")
        outcome = _verify_process_skill(result, process_skill)
    elif check == "git-workflow":
        outcome = _verify_git_workflow(result)
    elif check == "worktree":
        outcome = _verify_worktree(result)
    elif check == "lead-assignment":
        if not lead_agent:
            raise ValueError("--lead-agent is required for check=lead-assignment")
        outcome = _verify_lead_assignment(result, lead_agent, assistant_agents)
    elif check == "release-gate":
        outcome = _verify_release_gate(result)
    elif check == "iteration":
        outcome = _verify_iteration(result)
    elif check == "workflow-bundle":
        outcome = _verify_workflow_bundle(result)
    else:
        raise ValueError(f"Unsupported check: {check}")

    return {
        "ok": True,
        "check": check,
        "allowed": outcome["allowed"],
        "summary": outcome["summary"],
        "details": outcome["details"],
        "recommended_next_step": outcome["recommended_next_step"],
        "router_snapshot": {
            "lead_agent": result.get("lead_agent"),
            "assistant_agents": result.get("assistant_agents"),
            "process_skills": result.get("process_skills"),
            "needs_git_workflow": result.get("needs_git_workflow"),
            "needs_worktree": result.get("needs_worktree"),
            "needs_release_gate": result.get("needs_release_gate"),
            "needs_iteration": result.get("needs_iteration"),
            "workflow_bundle": result.get("workflow_bundle"),
            "progress_anchor_recommended": result.get("progress_anchor_recommended"),
            "resume_artifacts": result.get("resume_artifacts"),
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify whether a planned virtual team action matches the router contract.")
    parser.add_argument("--text", required=True, help="User request text.")
    parser.add_argument(
        "--check",
        required=True,
        choices=[
            "process-skill",
            "git-workflow",
            "worktree",
            "lead-assignment",
            "release-gate",
            "iteration",
            "workflow-bundle",
        ],
        help="What to verify before taking action.",
    )
    parser.add_argument("--process-skill", help="Process skill name for check=process-skill.")
    parser.add_argument("--lead-agent", help="Candidate lead agent for check=lead-assignment.")
    parser.add_argument(
        "--assistant-agent",
        action="append",
        default=[],
        help="Candidate assistant agent for check=lead-assignment. Repeatable.",
    )
    parser.add_argument(
        "--config",
        default=str(DEFAULT_CONFIG_PATH),
        help="Path to routing config JSON.",
    )
    parser.add_argument("--repo", default=".", help="Repository path for strategy detection.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        result = verify_action(
            text=args.text,
            config=load_config(Path(args.config).resolve()),
            repo_path=Path(args.repo).resolve(),
            check=args.check,
            process_skill=args.process_skill,
            lead_agent=args.lead_agent,
            assistant_agents=list(args.assistant_agent),
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
