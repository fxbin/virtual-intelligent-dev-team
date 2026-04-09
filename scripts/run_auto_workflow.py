#!/usr/bin/env python3
"""Run explicit /auto setup and go flows for supported virtual-team workflows."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
ROUTE_SCRIPT = SCRIPT_DIR / "route_request.py"
ITERATION_LOOP_SCRIPT = SCRIPT_DIR / "run_iteration_loop.py"
RELEASE_GATE_SCRIPT = SCRIPT_DIR / "run_release_gate.py"
INIT_PROJECT_MEMORY_SCRIPT = SCRIPT_DIR / "init_project_memory.py"
INIT_POST_RELEASE_FEEDBACK_SCRIPT = SCRIPT_DIR / "init_post_release_feedback.py"
EVALUATE_POST_RELEASE_FEEDBACK_SCRIPT = SCRIPT_DIR / "evaluate_post_release_feedback.py"
DEFAULT_CONFIG_PATH = SKILL_DIR / "references" / "routing-rules.json"
AUTO_PLAN_TEMPLATE_PATH = SKILL_DIR / "assets" / "auto-run-plan-template.json"
ITERATION_PLAN_TEMPLATE_PATH = SKILL_DIR / "assets" / "iteration-plan-template.json"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


route_request = load_module("virtual_team_auto_route_request", ROUTE_SCRIPT)
iteration_loop = load_module("virtual_team_auto_iteration_loop", ITERATION_LOOP_SCRIPT)
release_gate = load_module("virtual_team_auto_release_gate", RELEASE_GATE_SCRIPT)
project_memory_init = load_module("virtual_team_auto_project_memory", INIT_PROJECT_MEMORY_SCRIPT)
post_release_init = load_module(
    "virtual_team_auto_post_release_init",
    INIT_POST_RELEASE_FEEDBACK_SCRIPT,
)
post_release_feedback = load_module(
    "virtual_team_auto_post_release_feedback",
    EVALUATE_POST_RELEASE_FEEDBACK_SCRIPT,
)


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_config(config_path: Path) -> dict[str, object]:
    config = route_request.load_config(config_path)
    governance = config.setdefault("governance", {})
    if isinstance(governance, dict):
        fast_track = governance.setdefault("fast_track_control", {})
        if isinstance(fast_track, dict):
            fast_track["write_event_log"] = False
    return config


def load_json(path: Path) -> dict[str, object]:
    with path.open("r", encoding="utf-8") as file:
        payload = json.load(file)
    if not isinstance(payload, dict):
        raise RuntimeError(f"{path} must contain a JSON object")
    return payload


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def relative_path(path: Path, root: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except ValueError:
        return str(path.resolve())


def build_setup_markdown(plan: dict[str, object]) -> str:
    return "\n".join(
        [
            "# Auto Run Plan",
            "",
            f"- Generated: `{plan['generated_at']}`",
            f"- Trigger: `{plan['trigger']}`",
            f"- Requested phase: `{plan['requested_phase']}`",
            f"- Workflow bundle: `{plan['workflow_bundle']}`",
            f"- Lead agent: `{plan['route_snapshot']['lead_agent']}`",
            f"- Workflow supported: `{plan['workflow_supported']}`",
            f"- Resume anchor: `{plan['resume_anchor']}`",
            "",
            "## Request",
            "",
            plan["request_text"],
            "",
            "## Setup Actions",
            "",
        ]
        + [f"- `{item}`" for item in plan["workflow_execution"]["setup_actions"]]
        + [
            "",
            "## Go Actions",
            "",
        ]
        + [f"- `{item}`" for item in plan["workflow_execution"]["go_actions"]]
        + [
            "",
            "## Safety Guards",
            "",
        ]
        + [f"- {item}" for item in plan["safety_guards"]]
        + [
            "",
            "## Go Command",
            "",
            f"`{plan['go_command']}`",
            "",
        ]
    )


def build_go_markdown(summary: dict[str, object]) -> str:
    return "\n".join(
        [
            "# Auto Run Result",
            "",
            f"- Generated: `{summary['generated_at']}`",
            f"- Mode: `{summary['mode']}`",
            f"- Workflow bundle: `{summary['workflow_bundle']}`",
            f"- Status: `{summary['status']}`",
            f"- Decision: `{summary['decision']}`",
            f"- Resume anchor: `{summary['resume_anchor']}`",
            "",
            "## Resume Artifacts",
            "",
        ]
        + [f"- `{item}`" for item in summary["resume_artifacts"]]
        + [
            "",
            "## Recommended Next Step",
            "",
            summary["recommended_next_step"],
            "",
        ]
    )


def workflow_setup_actions(bundle: str) -> list[str]:
    if bundle == "root-cause-remediate":
        return [
            "initialize .skill-iterations anchors if missing",
            "materialize .skill-iterations/iteration-plan.auto.json from the template",
            "persist .skill-auto/auto-run-plan.json before go",
        ]
    if bundle == "ship-hold-remediate":
        return [
            "persist the explicit auto-run plan",
            "prepare evals/release-gate as the release workspace",
            "keep hold remediation bounded via --auto-run-next-iteration-on-hold",
        ]
    if bundle == "post-release-close-loop":
        return [
            "persist the explicit auto-run plan",
            "initialize .skill-post-release/ if the workspace is missing",
            "evaluate .skill-post-release/current-signals.json during go",
        ]
    return []


def workflow_go_actions(bundle: str) -> list[str]:
    if bundle == "root-cause-remediate":
        return [
            "python scripts/run_iteration_loop.py --workspace .skill-iterations --plan .skill-iterations/iteration-plan.auto.json --pretty",
        ]
    if bundle == "ship-hold-remediate":
        return [
            "python scripts/run_release_gate.py --output-dir evals/release-gate --iteration-workspace .skill-iterations --auto-run-next-iteration-on-hold --hold-loop-max-rounds 3 --pretty",
        ]
    if bundle == "post-release-close-loop":
        return [
            "python scripts/init_post_release_feedback.py --root . --pretty",
            "python scripts/evaluate_post_release_feedback.py --report .skill-post-release/current-signals.json --pretty",
        ]
    return []


def create_root_cause_iteration_plan(repo_root: Path, plan: dict[str, object]) -> Path:
    project_memory_init.init_project_memory(root=repo_root, mode="iteration", overwrite=False)
    iteration_plan = load_json(ITERATION_PLAN_TEMPLATE_PATH)
    loop_policy = dict(iteration_plan.get("loop_policy", {}))
    stop_caps = plan.get("stop_caps", {})
    route_snapshot = plan.get("route_snapshot", {})
    iteration_profile = route_snapshot.get("iteration_profile", {})
    if not isinstance(iteration_profile, dict):
        iteration_profile = {}
    loop_policy["max_rounds"] = max(int(stop_caps.get("iteration_online_round_cap", 3)), 1)
    loop_policy["max_same_hypothesis_retries"] = max(
        int(iteration_profile.get("max_same_hypothesis_retries", 2)),
        1,
    )
    loop_policy["auto_pivot_on_stagnation"] = True
    iteration_plan["loop_policy"] = loop_policy
    iteration_plan["owner"] = str(route_snapshot.get("lead_agent", "Technical Trinity"))
    iteration_plan["objective"] = str(plan.get("request_text", "")).strip() or "auto-remediate the current issue without regressions"
    iteration_plan["baseline_label"] = "stable"
    iteration_plan["autonomous_candidate_generation"] = True
    iteration_plan["candidates"] = []
    iteration_plan_path = repo_root / ".skill-iterations" / "iteration-plan.auto.json"
    write_json(iteration_plan_path, iteration_plan)
    return iteration_plan_path


def build_setup_plan(
    *,
    text: str,
    repo_root: Path,
    config: dict[str, object],
) -> dict[str, object]:
    route_result = route_request.route_request(text=text, config=config, repo_path=repo_root)
    auto_profile = route_result.get("auto_run_profile", {})
    if not isinstance(auto_profile, dict) or not bool(auto_profile.get("enabled")):
        raise RuntimeError("auto mode is not enabled for this request; use /auto explicitly")
    if not bool(auto_profile.get("workflow_supported")):
        raise RuntimeError(
            f"workflow `{route_result.get('workflow_bundle')}` is not supported by /auto yet"
        )

    state_root = repo_root / str(auto_profile.get("state_root", ".skill-auto"))
    state_root.mkdir(parents=True, exist_ok=True)
    plan_json_path = repo_root / str(auto_profile.get("plan_json", ".skill-auto/auto-run-plan.json"))
    plan_markdown_path = repo_root / str(auto_profile.get("plan_markdown", ".skill-auto/auto-run-plan.md"))

    payload = load_json(AUTO_PLAN_TEMPLATE_PATH)
    payload.update(
        {
            "ok": True,
            "mode": "setup",
            "generated_at": now_iso(),
            "trigger": str(auto_profile.get("trigger", "/auto")),
            "requested_phase": "setup",
            "requires_explicit_go": bool(auto_profile.get("requires_explicit_go", True)),
            "workflow_bundle": str(route_result.get("workflow_bundle", "")),
            "workflow_supported": bool(auto_profile.get("workflow_supported")),
            "request_text": str(auto_profile.get("text_without_trigger", text)).strip() or text.strip(),
            "root": str(repo_root),
            "state_root": relative_path(state_root, repo_root),
            "plan_json": relative_path(plan_json_path, repo_root),
            "plan_markdown": relative_path(plan_markdown_path, repo_root),
            "resume_anchor": str(auto_profile.get("resume_anchor", relative_path(plan_markdown_path, repo_root))),
            "eligible_workflows": [
                str(item) for item in auto_profile.get("eligible_workflows", []) if str(item).strip()
            ],
            "stop_caps": dict(auto_profile.get("stop_caps", {})),
            "safety_guards": [
                str(item) for item in auto_profile.get("safety_guards", []) if str(item).strip()
            ],
            "setup_command": str(auto_profile.get("setup_command", "")),
            "go_command": str(auto_profile.get("go_command", "")),
            "route_snapshot": {
                "lead_agent": route_result.get("lead_agent"),
                "assistant_agents": route_result.get("assistant_agents", []),
                "workflow_bundle": route_result.get("workflow_bundle"),
                "workflow_bundle_source": route_result.get("workflow_bundle_source"),
                "progress_anchor_recommended": route_result.get("progress_anchor_recommended"),
                "resume_artifacts": route_result.get("resume_artifacts", []),
                "iteration_profile": route_result.get("iteration_profile", {}),
            },
            "workflow_execution": {
                "setup_actions": workflow_setup_actions(str(route_result.get("workflow_bundle", ""))),
                "go_actions": workflow_go_actions(str(route_result.get("workflow_bundle", ""))),
                "artifacts": [
                    relative_path(plan_json_path, repo_root),
                    relative_path(plan_markdown_path, repo_root),
                ],
            },
        }
    )
    write_json(plan_json_path, payload)
    write_text(plan_markdown_path, build_setup_markdown(payload) + "\n")
    return payload


def run_root_cause_go(repo_root: Path, plan: dict[str, object]) -> dict[str, object]:
    iteration_plan_path = create_root_cause_iteration_plan(repo_root, plan)
    workspace = repo_root / ".skill-iterations"
    result = iteration_loop.run_loop(workspace=workspace, plan_path=iteration_plan_path, resume=False)
    resume_anchor = str(result.get("summary", relative_path(workspace / "current-round-memory.md", repo_root)))
    resume_artifacts = [
        str(item)
        for item in result.get("rounds_run", [])
        if isinstance(item, dict) and item.get("state")
    ]
    if not resume_artifacts:
        resume_artifacts = [
            relative_path(workspace / "current-round-memory.md", repo_root),
            relative_path(workspace / "distilled-patterns.md", repo_root),
            relative_path(iteration_plan_path, repo_root),
        ]
    return {
        "ok": True,
        "status": str(result.get("status", "completed")),
        "decision": str(result.get("halt_reason", "completed")),
        "resume_anchor": resume_anchor,
        "resume_artifacts": resume_artifacts,
        "recommended_next_step": "Inspect the latest iteration summary and either keep the accepted baseline or refine the next hypothesis.",
        "result": result,
    }


def run_release_go(repo_root: Path, plan: dict[str, object]) -> dict[str, object]:
    output_dir = repo_root / "evals" / "release-gate"
    iteration_workspace = repo_root / ".skill-iterations"
    result = release_gate.run_release_gate(
        output_dir=output_dir,
        iteration_workspace=iteration_workspace,
        auto_run_next_iteration_on_hold=True,
        hold_loop_max_rounds=max(int(plan.get("stop_caps", {}).get("release_hold_loop_max_rounds", 3)), 1),
    )
    follow_up = result.get("follow_up", {})
    if not isinstance(follow_up, dict):
        follow_up = {}
    return {
        "ok": bool(result.get("ok")),
        "status": "completed",
        "decision": str(result.get("decision", "hold")),
        "resume_anchor": str(
            follow_up.get(
                "resume_anchor",
                relative_path(output_dir / "release-gate-report.md", repo_root),
            )
        ),
        "resume_artifacts": [
            str(item)
            for item in follow_up.get("resume_artifacts", [])
            if str(item).strip()
        ]
        or [
            relative_path(output_dir / "release-gate-report.md", repo_root),
            relative_path(output_dir / "release-gate-results.json", repo_root),
        ],
        "recommended_next_step": str(
            follow_up.get(
                "next_action",
                "Read the release gate follow-up and continue from ship closure or hold remediation.",
            )
        ),
        "result": result,
    }


def run_post_release_go(repo_root: Path, plan: dict[str, object]) -> dict[str, object]:
    init_result = post_release_init.init_post_release_feedback(root=repo_root, overwrite=False)
    report_path = repo_root / ".skill-post-release" / "current-signals.json"
    result = post_release_feedback.evaluate_post_release_feedback(report_path=report_path)
    follow_up = result.get("follow_up", {})
    if not isinstance(follow_up, dict):
        follow_up = {}
    artifacts = [
        str(item)
        for item in follow_up.get("resume_artifacts", [])
        if str(item).strip()
    ]
    if not artifacts:
        artifacts = [str(item) for item in init_result.get("artifacts", []) if str(item).strip()]
    return {
        "ok": bool(result.get("ok")),
        "status": "completed",
        "decision": str(result.get("decision", "monitor")),
        "resume_anchor": str(repo_root / ".skill-post-release" / "triage-summary.md"),
        "resume_artifacts": artifacts,
        "recommended_next_step": str(
            follow_up.get(
                "next_action",
                "Use the post-release decision to decide whether to monitor, iterate, or escalate.",
            )
        ),
        "result": result,
    }


def run_go(plan_path: Path, repo_root: Path) -> dict[str, object]:
    plan = load_json(plan_path)
    workflow_bundle = str(plan.get("workflow_bundle", "")).strip()
    if workflow_bundle == "root-cause-remediate":
        execution = run_root_cause_go(repo_root, plan)
    elif workflow_bundle == "ship-hold-remediate":
        execution = run_release_go(repo_root, plan)
    elif workflow_bundle == "post-release-close-loop":
        execution = run_post_release_go(repo_root, plan)
    else:
        raise RuntimeError(f"unsupported auto workflow bundle: {workflow_bundle}")

    state_root = repo_root / str(plan.get("state_root", ".skill-auto"))
    last_run_json = state_root / "last-run.json"
    last_run_markdown = state_root / "last-run.md"
    summary = {
        "ok": bool(execution.get("ok", True)),
        "generated_at": now_iso(),
        "mode": "go",
        "workflow_bundle": workflow_bundle,
        "status": str(execution.get("status", "completed")),
        "decision": str(execution.get("decision", "completed")),
        "resume_anchor": str(execution.get("resume_anchor", plan.get("resume_anchor", ""))),
        "resume_artifacts": [
            str(item) for item in execution.get("resume_artifacts", []) if str(item).strip()
        ],
        "recommended_next_step": str(execution.get("recommended_next_step", "")),
        "plan_json": relative_path(plan_path, repo_root),
        "last_run_json": relative_path(last_run_json, repo_root),
        "last_run_markdown": relative_path(last_run_markdown, repo_root),
        "result": execution.get("result", {}),
    }
    write_json(last_run_json, summary)
    write_text(last_run_markdown, build_go_markdown(summary) + "\n")
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run explicit /auto setup or go workflows.")
    parser.add_argument("--text", help="Original request text. Required for --mode setup.")
    parser.add_argument("--mode", choices=["setup", "go"], required=True, help="Auto workflow phase to run.")
    parser.add_argument(
        "--plan",
        default=".skill-auto/auto-run-plan.json",
        help="Path to the saved auto plan for --mode go.",
    )
    parser.add_argument(
        "--config",
        default=str(DEFAULT_CONFIG_PATH),
        help="Path to routing config JSON.",
    )
    parser.add_argument("--repo", default=".", help="Repository root.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    repo_root = Path(args.repo).resolve()
    config = load_config(Path(args.config).resolve())
    try:
        if args.mode == "setup":
            if not args.text:
                raise RuntimeError("--text is required for --mode setup")
            result = build_setup_plan(text=args.text, repo_root=repo_root, config=config)
            exit_code = 0
        else:
            plan_path = Path(args.plan)
            if not plan_path.is_absolute():
                plan_path = repo_root / plan_path
            result = run_go(plan_path.resolve(), repo_root)
            exit_code = 0 if bool(result.get("result", {}).get("ok", True)) else 2
    except Exception as exc:
        result = {"ok": False, "error": str(exc), "mode": args.mode}
        exit_code = 2

    if args.pretty:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(result, ensure_ascii=False))
    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
