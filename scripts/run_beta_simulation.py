#!/usr/bin/env python3
"""Run a deterministic beta simulation from config and emit trace artifacts."""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
RESPONSE_CONTRACT_SCRIPT = SCRIPT_DIR / "response_contract.py"


def load_module(name: str, path: Path):
    import importlib.util

    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


response_contract = load_module("virtual_team_run_beta_simulation_response_contract", RESPONSE_CONTRACT_SCRIPT)


def load_json(path: Path) -> dict[str, object]:
    with path.open("r", encoding="utf-8") as file:
        payload = json.load(file)
    if not isinstance(payload, dict):
        raise RuntimeError(f"{path} must contain a JSON object")
    return payload


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def repo_root_from_config(config_path: Path) -> Path:
    if config_path.parent.name == "simulation-configs" and config_path.parent.parent.name == ".skill-beta":
        return config_path.parent.parent.parent
    return config_path.parent


def resolve_repo_path(repo_root: Path, raw_path: str) -> Path:
    path = Path(raw_path)
    if path.is_absolute():
        return path
    repo_candidate = (repo_root / path).resolve()
    if repo_candidate.exists():
        return repo_candidate
    skill_candidate = (SKILL_DIR / path).resolve()
    if skill_candidate.exists():
        return skill_candidate
    return repo_candidate


def validate_event(payload: dict[str, object]) -> dict[str, object]:
    response_contract.validate_beta_simulation_event(payload)
    return payload


def load_trace_catalog(path: Path) -> dict[str, dict[str, object]]:
    payload = load_json(path)
    response_contract.validate_simulation_trace_catalog(payload)
    traces = payload.get("traces", [])
    if not isinstance(traces, list) or not traces:
        raise RuntimeError(f"{path} must define a non-empty traces array")
    catalog: dict[str, dict[str, object]] = {}
    for item in traces:
        if not isinstance(item, dict):
            continue
        trace_id = str(item.get("trace_id", "")).strip()
        if trace_id == "":
            continue
        catalog[trace_id] = dict(item)
    if not catalog:
        raise RuntimeError(f"{path} did not contain any valid traces")
    return catalog


def make_event(
    step_index: int,
    *,
    event_type: str,
    actor_id: str,
    scenario_id: str,
    action: str,
    outcome: str,
    severity: str,
    observation: str,
) -> dict[str, object]:
    return validate_event(
        {
            "step_index": step_index,
            "event_type": event_type,
            "actor_id": actor_id,
            "scenario_id": scenario_id,
            "action": action,
            "outcome": outcome,
            "severity": severity,
            "observation": observation,
        }
    )


def infer_session_result(profile: dict[str, object], scenario: dict[str, object]) -> dict[str, object]:
    persona_id = str(profile["profile_id"])
    archetype = str(profile.get("archetype", "")).lower()
    tool_literacy = str(profile.get("tool_literacy", "medium"))
    domain_familiarity = str(profile.get("domain_familiarity", "medium"))
    workflow_preference = str(profile.get("workflow_preference", "")).lower()
    risk_focus = str(scenario.get("risk_focus", "")).lower()

    task_completed = True
    blocker_detected = False
    critical_detected = False
    high_detected = False
    themes: list[str] = []
    events: list[dict[str, object]] = [
        make_event(
            1,
            event_type="entry",
            actor_id=persona_id,
            scenario_id=str(scenario["scenario_id"]),
            action="start scenario",
            outcome="neutral",
            severity="info",
            observation=f"{profile['display_name']} starts `{scenario['title']}`.",
        )
    ]

    step = 2
    if tool_literacy == "low" or "clarity" in risk_focus:
        themes.append("onboarding clarity")
        events.append(
            make_event(
                step,
                event_type="hesitation",
                actor_id=persona_id,
                scenario_id=str(scenario["scenario_id"]),
                action="interpret primary CTA",
                outcome="warning",
                severity="medium",
                observation="The user pauses to infer what the next safe action should be.",
            )
        )
        step += 1

    if "power user" in archetype or "shortcut" in workflow_preference or "fast" in workflow_preference:
        themes.append("efficiency friction")
        high_detected = True
        events.append(
            make_event(
                step,
                event_type="action",
                actor_id=persona_id,
                scenario_id=str(scenario["scenario_id"]),
                action="optimize the happy path",
                outcome="warning",
                severity="high",
                observation="The user finishes the task but reports too much friction on the fast path.",
            )
        )
        step += 1

    if "skeptical" in archetype:
        themes.append("trust and differentiation")
        events.append(
            make_event(
                step,
                event_type="feedback",
                actor_id=persona_id,
                scenario_id=str(scenario["scenario_id"]),
                action="question credibility",
                outcome="warning",
                severity="medium",
                observation="The user wants clearer proof of why this workflow is worth trusting.",
            )
        )
        step += 1

    if "edge-case" in archetype or ("error recovery" in risk_focus and domain_familiarity == "high"):
        themes.append("edge-case handling")
        blocker_detected = True
        high_detected = True
        task_completed = False
        events.append(
            make_event(
                step,
                event_type="error",
                actor_id=persona_id,
                scenario_id=str(scenario["scenario_id"]),
                action="push invalid or unusual state",
                outcome="failure",
                severity="high",
                observation="The user finds a fragile edge path that breaks recovery or leaves the state unclear.",
            )
        )
        step += 1
        events.append(
            make_event(
                step,
                event_type="workaround",
                actor_id=persona_id,
                scenario_id=str(scenario["scenario_id"]),
                action="attempt workaround",
                outcome="warning",
                severity="medium",
                observation="A workaround exists, but it is not obvious enough to count as safe recovery.",
            )
        )
        step += 1

    if task_completed:
        events.append(
            make_event(
                step,
                event_type="success",
                actor_id=persona_id,
                scenario_id=str(scenario["scenario_id"]),
                action="finish the task",
                outcome="success",
                severity="info",
                observation="The user reaches the intended outcome.",
            )
        )
        step += 1

    feedback_summary = (
        "Task succeeded, but onboarding clarity and trust cues need improvement."
        if "skeptical" in archetype and tool_literacy == "low"
        else "Task succeeded, but the fast path still has unnecessary friction."
        if "power user" in archetype
        else "A blocker emerged on an edge path and should be fixed before expansion."
        if blocker_detected
        else "Task completed with moderate friction that should be simplified before scaling."
    )
    events.append(
        make_event(
            step,
            event_type="feedback",
            actor_id=persona_id,
            scenario_id=str(scenario["scenario_id"]),
            action="summarize experience",
            outcome="warning" if high_detected or blocker_detected else "neutral",
            severity="high" if blocker_detected else "medium" if high_detected else "low",
            observation=feedback_summary,
        )
    )

    return {
        "trace_id": "heuristic-fallback",
        "trace_label": "Heuristic fallback",
        "task_completed": task_completed,
        "blocker_detected": blocker_detected,
        "critical_issue_detected": critical_detected,
        "high_severity_issue_detected": high_detected,
        "top_feedback_themes": sorted(set(themes)) or ["workflow confidence"],
        "feedback_summary": feedback_summary,
        "events": events,
    }


def render_trace_observation(template: str, *, persona_name: str, scenario_title: str) -> str:
    return template.format(
        persona_name=persona_name,
        scenario_title=scenario_title,
    )


def simulate_session_from_trace(
    *,
    trace: dict[str, object],
    persona_id: str,
    persona_name: str,
    scenario_id: str,
    scenario_title: str,
) -> dict[str, object]:
    raw_events = trace.get("events", [])
    if not isinstance(raw_events, list) or not raw_events:
        raise RuntimeError(f"trace `{trace.get('trace_id', '')}` must define at least one event")

    events: list[dict[str, object]] = []
    for step_index, item in enumerate(raw_events, start=1):
        if not isinstance(item, dict):
            continue
        events.append(
            make_event(
                step_index,
                event_type=str(item.get("event_type", "")).strip(),
                actor_id=persona_id,
                scenario_id=scenario_id,
                action=str(item.get("action", "")).strip(),
                outcome=str(item.get("outcome", "")).strip(),
                severity=str(item.get("severity", "")).strip(),
                observation=render_trace_observation(
                    str(item.get("observation", "")).strip(),
                    persona_name=persona_name,
                    scenario_title=scenario_title,
                ),
            )
        )

    themes = trace.get("top_feedback_themes", [])
    return {
        "trace_id": str(trace.get("trace_id", "")).strip(),
        "trace_label": str(trace.get("label", "")).strip(),
        "task_completed": bool(trace.get("task_completed")),
        "blocker_detected": bool(trace.get("blocker_detected")),
        "critical_issue_detected": bool(trace.get("critical_issue_detected")),
        "high_severity_issue_detected": bool(trace.get("high_severity_issue_detected")),
        "top_feedback_themes": [str(item) for item in themes if str(item).strip() != ""]
        if isinstance(themes, list)
        else ["workflow confidence"],
        "feedback_summary": str(trace.get("feedback_summary", "")).strip() or "simulation feedback captured",
        "events": events,
    }


def run_beta_simulation(*, config_path: Path, output_dir: Path | None = None) -> dict[str, object]:
    config = load_json(config_path)
    response_contract.validate_beta_simulation_config(config)
    repo_root = repo_root_from_config(config_path.resolve())
    persona_dir = resolve_repo_path(repo_root, str(config["persona_dir"]))
    trace_catalog_path = resolve_repo_path(
        repo_root,
        str(config.get("trace_catalog_source", "references/simulation-trace-catalog.json")),
    )
    trace_catalog = load_trace_catalog(trace_catalog_path)
    scenarios = config.get("scenarios", [])
    session_plan = config.get("session_plan", [])
    if not isinstance(scenarios, list) or not isinstance(session_plan, list):
        raise RuntimeError("beta simulation config must provide list-shaped scenarios and session_plan")

    scenario_map = {
        str(item["scenario_id"]): item
        for item in scenarios
        if isinstance(item, dict)
    }
    persona_cache: dict[str, dict[str, object]] = {}
    sessions: list[dict[str, object]] = []
    for item in session_plan:
        if not isinstance(item, dict):
            continue
        persona_id = str(item["persona_id"])
        scenario_id = str(item["scenario_id"])
        if persona_id not in persona_cache:
            persona_path = persona_dir / f"{persona_id}.json"
            profile = load_json(persona_path)
            response_contract.validate_simulated_user_profile(profile)
            persona_cache[persona_id] = profile
        profile = persona_cache[persona_id]
        scenario = scenario_map[scenario_id]
        trace_id = str(item.get("trace_id", "")).strip()
        if trace_id:
            trace = trace_catalog.get(trace_id)
            if trace is None:
                raise RuntimeError(f"beta simulation config references unknown trace_id: {trace_id}")
            simulated = simulate_session_from_trace(
                trace=trace,
                persona_id=persona_id,
                persona_name=str(profile["display_name"]),
                scenario_id=scenario_id,
                scenario_title=str(scenario["title"]),
            )
        else:
            simulated = infer_session_result(profile, scenario)
        session_payload = {
            "session_id": str(item["session_id"]),
            "persona_id": persona_id,
            "persona_name": str(profile["display_name"]),
            "scenario_id": scenario_id,
            "scenario_title": str(scenario["title"]),
            "status": "completed",
            **simulated,
        }
        sessions.append(session_payload)

    theme_counter = Counter(
        theme
        for session in sessions
        for theme in session.get("top_feedback_themes", [])
        if isinstance(theme, str) and theme.strip() != ""
    )
    summary = {
        "planned_sessions": len(session_plan),
        "completed_sessions": len(sessions),
        "task_success_count": sum(1 for session in sessions if session["task_completed"]),
        "blocker_issue_count": sum(1 for session in sessions if session["blocker_detected"]),
        "critical_issue_count": sum(1 for session in sessions if session["critical_issue_detected"]),
        "high_severity_issue_count": sum(1 for session in sessions if session["high_severity_issue_detected"]),
        "top_feedback_themes": [theme for theme, _count in theme_counter.most_common(5)],
    }

    resolved_output_dir = (
        output_dir.resolve()
        if output_dir is not None
        else resolve_repo_path(repo_root, str(config["run_output_dir"]))
    )
    resolved_output_dir.mkdir(parents=True, exist_ok=True)
    json_report = resolved_output_dir / "beta-simulation-run.json"
    markdown_report = resolved_output_dir / "beta-simulation-run.md"

    payload = {
        "schema_version": "beta-simulation-run/v1",
        "generated_at": now_iso(),
        "skill_name": "virtual-intelligent-dev-team",
        "round_id": str(config["round_id"]),
        "phase": str(config["phase"]),
        "objective": str(config["objective"]),
        "config_path": str(config_path),
        "cohort_fixture_source": str(config.get("cohort_fixture_source", "")),
        "trace_catalog_source": str(config.get("trace_catalog_source", "")),
        "personas": [
            {
                "profile_id": str(profile["profile_id"]),
                "display_name": str(profile["display_name"]),
                "archetype": str(profile["archetype"]),
            }
            for profile in persona_cache.values()
        ],
        "scenarios": [
            {
                "scenario_id": str(item["scenario_id"]),
                "title": str(item["title"]),
                "primary_task": str(item["primary_task"]),
                "success_definition": str(item["success_definition"]),
                "risk_focus": str(item["risk_focus"]),
            }
            for item in scenario_map.values()
        ],
        "sessions": sessions,
        "summary": summary,
        "json_report": str(json_report),
        "markdown_report": str(markdown_report),
    }
    response_contract.validate_beta_simulation_run(payload)
    json_report.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        f"# Beta Simulation Run: {payload['round_id']}",
        "",
        f"- Phase: {payload['phase']}",
        f"- Objective: {payload['objective']}",
        f"- Completed sessions: {summary['completed_sessions']}/{summary['planned_sessions']}",
        f"- Task success count: {summary['task_success_count']}",
        f"- Blocker issue count: {summary['blocker_issue_count']}",
        f"- Critical issue count: {summary['critical_issue_count']}",
        f"- High severity issue count: {summary['high_severity_issue_count']}",
        f"- Top feedback themes: {', '.join(summary['top_feedback_themes']) if summary['top_feedback_themes'] else 'n/a'}",
        "",
        "## Sessions",
        "",
    ]
    for session in sessions:
        lines.extend(
            [
                f"- {session['session_id']} | {session['persona_name']} | {session['scenario_title']} | trace={session.get('trace_id', 'n/a')} | completed={session['task_completed']} | blocker={session['blocker_detected']} | themes={', '.join(session['top_feedback_themes'])}",
            ]
        )
    lines.append("")
    markdown_report.write_text("\n".join(lines), encoding="utf-8")
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a deterministic beta simulation.")
    parser.add_argument("--config", required=True, help="Path to beta simulation config JSON.")
    parser.add_argument("--output-dir", help="Optional output directory for run artifacts.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_beta_simulation(
        config_path=Path(args.config).resolve(),
        output_dir=Path(args.output_dir).resolve() if args.output_dir else None,
    )
    if args.pretty:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
