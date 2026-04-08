#!/usr/bin/env python3
"""Initialize simulation personas and config for one beta round."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
PROFILE_TEMPLATE_PATH = SKILL_DIR / "assets" / "simulated-user-profile-template.json"
CONFIG_TEMPLATE_PATH = SKILL_DIR / "assets" / "beta-simulation-config-template.json"
RESPONSE_CONTRACT_SCRIPT = SCRIPT_DIR / "response_contract.py"


def load_module(name: str, path: Path):
    import importlib.util

    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


response_contract = load_module("virtual_team_init_beta_simulation_response_contract", RESPONSE_CONTRACT_SCRIPT)


def load_json(path: Path) -> dict[str, object]:
    with path.open("r", encoding="utf-8") as file:
        payload = json.load(file)
    if not isinstance(payload, dict):
        raise RuntimeError(f"{path} must contain a JSON object")
    return payload


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def default_profiles_for_round(round_id: str) -> list[dict[str, object]]:
    profiles = [
        {
            "profile_id": "first-time-novice",
            "display_name": "First-Time Novice",
            "archetype": "first-time novice",
            "primary_goal": "Understand the promise quickly and finish the first meaningful task without guidance.",
            "tool_literacy": "low",
            "domain_familiarity": "low",
            "risk_tolerance": "low",
            "workflow_preference": "step-by-step clarity with visible next actions",
            "failure_sensitivity": "high",
            "feedback_style": "balanced",
            "preferred_tasks": ["first-run journey", "guided onboarding"],
            "notes": "Treat confusion as a blocker candidate.",
        },
        {
            "profile_id": "daily-operator",
            "display_name": "Daily Operator",
            "archetype": "daily operator",
            "primary_goal": "Finish the core repeated task with minimal friction.",
            "tool_literacy": "medium",
            "domain_familiarity": "high",
            "risk_tolerance": "medium",
            "workflow_preference": "repeatable routine with low cognitive load",
            "failure_sensitivity": "medium",
            "feedback_style": "brief",
            "preferred_tasks": ["core repeated task", "resume interrupted work"],
            "notes": "Surface repetitive friction and state drift.",
        },
        {
            "profile_id": "goal-driven-power-user",
            "display_name": "Goal-Driven Power User",
            "archetype": "goal-driven power user",
            "primary_goal": "Reach the target outcome through the fastest path available.",
            "tool_literacy": "high",
            "domain_familiarity": "medium",
            "risk_tolerance": "high",
            "workflow_preference": "shortcuts, batching, and fast-path actions",
            "failure_sensitivity": "medium",
            "feedback_style": "brief",
            "preferred_tasks": ["fastest happy path", "advanced settings"],
            "notes": "Surface efficiency friction, missing shortcuts, and slow defaults.",
        },
        {
            "profile_id": "skeptical-evaluator",
            "display_name": "Skeptical Evaluator",
            "archetype": "skeptical evaluator",
            "primary_goal": "Decide whether the product is trustworthy and differentiated enough to keep evaluating.",
            "tool_literacy": "medium",
            "domain_familiarity": "low",
            "risk_tolerance": "low",
            "workflow_preference": "strong explanations before committing effort",
            "failure_sensitivity": "high",
            "feedback_style": "verbose",
            "preferred_tasks": ["value proposition review", "permission review"],
            "notes": "Surface trust, messaging, and credibility issues.",
        },
        {
            "profile_id": "edge-case-breaker",
            "display_name": "Edge-Case Breaker",
            "archetype": "edge-case breaker",
            "primary_goal": "Intentionally hit unusual states to discover hidden blockers.",
            "tool_literacy": "high",
            "domain_familiarity": "high",
            "risk_tolerance": "high",
            "workflow_preference": "boundary pushing and invalid-state exploration",
            "failure_sensitivity": "low",
            "feedback_style": "balanced",
            "preferred_tasks": ["invalid input", "state transitions", "error recovery"],
            "notes": "Surface hidden blockers before wider rollout.",
        },
    ]
    if round_id == "round-0":
        allowed = {"first-time-novice", "goal-driven-power-user", "skeptical-evaluator"}
        return [item for item in profiles if item["profile_id"] in allowed]
    if round_id == "round-1":
        allowed = {"first-time-novice", "daily-operator", "goal-driven-power-user", "edge-case-breaker"}
        return [item for item in profiles if item["profile_id"] in allowed]
    return profiles


def default_scenarios(round_id: str, objective: str) -> list[dict[str, str]]:
    scenarios = [
        {
            "scenario_id": "scenario-1",
            "title": "first meaningful task",
            "primary_task": "finish the primary happy-path task",
            "success_definition": "the user completes the task and can restate the product value",
            "risk_focus": "onboarding clarity",
        },
        {
            "scenario_id": "scenario-2",
            "title": "repeat core workflow",
            "primary_task": "repeat the core task after the first-run context disappears",
            "success_definition": "the user can re-enter the flow without rebuilding context from scratch",
            "risk_focus": "workflow friction",
        },
        {
            "scenario_id": "scenario-3",
            "title": "recover from a rough edge",
            "primary_task": "handle a confusing or unusual state and still reach a recoverable outcome",
            "success_definition": "the user can recover without silent failure or dead-end confusion",
            "risk_focus": "error recovery and edge-case handling",
        },
    ]
    if round_id == "round-0":
        return scenarios[:2]
    if "operational" in objective.lower() or "stability" in objective.lower():
        return scenarios
    return scenarios


def build_session_plan(personas: list[dict[str, object]], scenarios: list[dict[str, str]]) -> list[dict[str, str]]:
    plan: list[dict[str, str]] = []
    for index, persona in enumerate(personas, start=1):
        primary_scenario = scenarios[min(index - 1, len(scenarios) - 1)]
        persona_id = str(persona["profile_id"])
        plan.append(
            {
                "session_id": f"session-{index:02d}",
                "persona_id": persona_id,
                "scenario_id": str(primary_scenario["scenario_id"]),
            }
        )
        if persona_id in {"edge-case-breaker", "goal-driven-power-user"} and len(scenarios) > 1:
            plan.append(
                {
                    "session_id": f"session-{len(plan)+1:02d}",
                    "persona_id": persona_id,
                    "scenario_id": str(scenarios[-1]["scenario_id"]),
                }
            )
    return plan


def init_beta_simulation(
    *,
    root: Path,
    round_id: str,
    phase: str,
    objective: str,
    overwrite: bool = False,
) -> dict[str, object]:
    _ = load_json(PROFILE_TEMPLATE_PATH)
    config_template = load_json(CONFIG_TEMPLATE_PATH)
    personas = default_profiles_for_round(round_id)
    scenarios = default_scenarios(round_id, objective)
    session_plan = build_session_plan(personas, scenarios)

    persona_dir = root / ".skill-beta" / "personas"
    config_dir = root / ".skill-beta" / "simulation-configs"
    config_path = config_dir / f"{round_id}.json"
    run_output_dir = root / ".skill-beta" / "simulation-runs" / round_id
    round_report_out = root / ".skill-beta" / "reports" / f"{round_id}.json"

    created_profiles: list[str] = []
    for payload in personas:
        profile_payload = dict(payload)
        profile_payload["schema_version"] = "simulated-user-profile/v1"
        response_contract.validate_simulated_user_profile(profile_payload)
        path = persona_dir / f"{profile_payload['profile_id']}.json"
        if overwrite or not path.exists():
            write_json(path, profile_payload)
            created_profiles.append(str(path.relative_to(root)))

    config_payload = dict(config_template)
    config_payload.update(
        {
            "round_id": round_id,
            "phase": phase,
            "objective": objective,
            "persona_dir": str(persona_dir.relative_to(root)),
            "run_output_dir": str(run_output_dir.relative_to(root)),
            "feedback_ledger_out": ".skill-beta/feedback-ledger.md",
            "round_report_out": str(round_report_out.relative_to(root)),
            "summary_command_template": (
                "python scripts/summarize_beta_simulation.py "
                f"--run .skill-beta/simulation-runs/{round_id}/beta-simulation-run.json "
                "--feedback-ledger-out .skill-beta/feedback-ledger.md "
                f"--round-report-out .skill-beta/reports/{round_id}.json --pretty"
            ),
            "scenarios": scenarios,
            "session_plan": session_plan,
        }
    )
    response_contract.validate_beta_simulation_config(config_payload)

    status = "skipped"
    if overwrite or not config_path.exists():
        write_json(config_path, config_payload)
        status = "updated" if overwrite and config_path.exists() else "created"

    return {
        "ok": True,
        "status": status,
        "round_id": round_id,
        "config_path": str(config_path.relative_to(root)),
        "persona_dir": str(persona_dir.relative_to(root)),
        "run_output_dir": str(run_output_dir.relative_to(root)),
        "feedback_ledger_out": ".skill-beta/feedback-ledger.md",
        "round_report_out": str(round_report_out.relative_to(root)),
        "created_profiles": created_profiles,
        "scenario_count": len(scenarios),
        "session_count": len(session_plan),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Initialize simulated-user profiles and a beta simulation config.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--round-id", required=True, help="Round id, for example round-0.")
    parser.add_argument("--phase", required=True, help="Round phase label.")
    parser.add_argument("--objective", required=True, help="Simulation objective.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing config and profiles.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = init_beta_simulation(
        root=Path(args.root).resolve(),
        round_id=args.round_id,
        phase=args.phase,
        objective=args.objective,
        overwrite=args.overwrite,
    )
    if args.pretty:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
