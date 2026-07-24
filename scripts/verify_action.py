#!/usr/bin/env python3
"""Pre-action verification for virtual-intelligent-dev-team process decisions."""

from __future__ import annotations

import argparse
from contextlib import redirect_stdout
from datetime import datetime
import importlib.util
from io import StringIO
import json
import re
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
ROUTE_SCRIPT = SCRIPT_DIR / "route_request.py"
RESPONSE_PACK_SCRIPT = SCRIPT_DIR / "generate_response_pack.py"
RESPONSE_CONTRACT_SCRIPT = SCRIPT_DIR / "response_contract.py"
EVALUATE_MICRO_PRACTICES_SCRIPT = SCRIPT_DIR / "evaluate_micro_practices.py"
VERIFY_COMPLETION_EVIDENCE_SCRIPT = SCRIPT_DIR / "verify_completion_evidence.py"
CIRCUIT_BREAKER_SCRIPT = SCRIPT_DIR / "circuit_breaker.py"
EMIT_TELEMETRY_SCRIPT = SCRIPT_DIR / "emit_telemetry.py"
INSPECT_DECISION_LOG_SCRIPT = SCRIPT_DIR / "inspect_decision_log.py"
DEFAULT_CONFIG_PATH = SKILL_DIR / "references" / "routing-rules.json"
DEFAULT_BREAKER_CONFIG_PATH = SKILL_DIR / "references" / "circuit-breaker-config.json"
DEFAULT_BREAKER_STATE_FILE = Path(".vidt/harness") / "breaker-state.json"
DEFAULT_BREAKER_ESCALATION_SINK = Path(".vidt/harness") / "escalation-queue.jsonl"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


route_request = load_module("virtual_team_verify_action_route_request", ROUTE_SCRIPT)
response_pack = load_module("virtual_team_verify_action_response_pack", RESPONSE_PACK_SCRIPT)
response_contract = load_module("virtual_team_verify_action_response_contract", RESPONSE_CONTRACT_SCRIPT)
micro_practice_evaluator = load_module(
    "virtual_team_verify_action_evaluate_micro_practices",
    EVALUATE_MICRO_PRACTICES_SCRIPT,
)
completion_evidence_verifier = load_module(
    "virtual_team_verify_action_verify_completion_evidence",
    VERIFY_COMPLETION_EVIDENCE_SCRIPT,
)
circuit_breaker_module = load_module(
    "virtual_team_verify_action_circuit_breaker",
    CIRCUIT_BREAKER_SCRIPT,
)
emit_telemetry_module = load_module(
    "virtual_team_verify_action_emit_telemetry",
    EMIT_TELEMETRY_SCRIPT,
)
inspect_decision_log_module = load_module(
    "virtual_team_verify_action_inspect_decision_log",
    INSPECT_DECISION_LOG_SCRIPT,
)


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


def _verify_iteration(
    result: dict[str, object],
    repo_path: Path,
    iteration_workspace: Path | None = None,
) -> dict[str, object]:
    iteration_enabled = bool(result.get("needs_iteration"))
    profile = result.get("iteration_profile", {})
    if not isinstance(profile, dict):
        profile = {}
    workspace = (
        iteration_workspace.resolve()
        if iteration_workspace is not None
        else (repo_path / ".vidt/iterations").resolve()
    )
    registry_path = workspace / "baselines" / "registry.json"
    registry_exists = registry_path.is_file()
    registry_error = ""
    baseline_entries: list[dict[str, object]] = []
    if registry_exists:
        try:
            registry_payload = json.loads(registry_path.read_text(encoding="utf-8"))
            raw_entries = registry_payload.get("baselines", []) if isinstance(registry_payload, dict) else []
            if not isinstance(raw_entries, list):
                raise ValueError("baselines must be an array")
            baseline_entries = [entry for entry in raw_entries if isinstance(entry, dict)]
        except (json.JSONDecodeError, OSError, ValueError) as exc:
            registry_error = f"{type(exc).__name__}: {exc}"

    missing_baselines: list[str] = []
    valid_baselines: list[str] = []
    for entry in baseline_entries:
        label = str(entry.get("label", "<unlabeled>"))
        stored_value = str(entry.get("stored_report", "")).strip()
        if not stored_value:
            missing_baselines.append(f"{label}: stored_report missing")
            continue
        stored_path = Path(stored_value)
        if not stored_path.is_absolute():
            stored_path = (repo_path / stored_path).resolve()
        if stored_path.is_file():
            valid_baselines.append(label)
        else:
            missing_baselines.append(f"{label}: {stored_path}")

    baseline_ready = (
        registry_exists
        and not registry_error
        and len(baseline_entries) > 0
        and len(valid_baselines) == len(baseline_entries)
    )
    allowed = iteration_enabled and baseline_ready
    if allowed:
        summary = f"Bounded iteration is enabled with {len(valid_baselines)} valid baseline(s)."
        next_step = "Use the registered baseline and iteration profile to keep the loop evidence-driven and bounded."
    elif iteration_enabled:
        summary = "Bounded iteration is requested but its baseline registry is missing, invalid, or points to deleted reports."
        next_step = (
            "Register or repair a baseline with python scripts/register_benchmark_baseline.py "
            "before running the next iteration cycle."
        )
    else:
        summary = "Bounded iteration is not required for this request."
        next_step = "Stay on the direct execution path unless the user explicitly asks for benchmarking, retries, or another round."
    return {
        "allowed": allowed,
        "summary": summary,
        "details": {
            "needs_iteration": bool(result.get("needs_iteration")),
            "iteration_workspace": str(workspace),
            "registry_path": str(registry_path),
            "registry_exists": registry_exists,
            "registry_error": registry_error,
            "baseline_count": len(baseline_entries),
            "valid_baseline_count": len(valid_baselines),
            "valid_baselines": valid_baselines,
            "missing_baselines": missing_baselines,
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
    bundle_confidence = result.get("bundle_confidence")
    bundle_source = result.get("workflow_bundle_source")
    progress_anchor = result.get("progress_anchor_recommended")
    resume_artifacts = result.get("resume_artifacts", [])
    workflow_steps = result.get("workflow_steps", [])
    numeric_confidence = float(bundle_confidence) if isinstance(bundle_confidence, (int, float)) else 0.0
    source_text = str(bundle_source) if isinstance(bundle_source, str) else ""
    bundle_bootstrap = result.get("workflow_bundle_bootstrap", {})
    if not isinstance(bundle_bootstrap, dict):
        bundle_bootstrap = {}
    source_explanations = {
        "keyword": "The workflow bundle is activated directly by matching request keywords, so the workflow is tied to the task shape even without an explicit process skill.",
        "process-skill": "The workflow bundle is activated by an explicit process skill, so it should be treated as the primary execution journey.",
        "keyword+lead": "The workflow bundle is activated by the combination of task keywords and a high-risk lead, so it is evidence-backed but not purely process-driven.",
        "lead+keyword": "The workflow bundle is activated by both the selected lead and matching request keywords, so the journey is strongly anchored in task semantics.",
        "lead-default": "The workflow bundle is activated mainly by the selected lead's default journey, so keep the route but avoid overstating it as a hard process lane.",
        "fallback": "The workflow bundle is only a lightweight fallback and should not be treated as a strong process commitment.",
    }
    known_source = source_text in source_explanations
    allowed = (
        isinstance(bundle, str)
        and bundle not in {"", "direct-execution"}
        and numeric_confidence >= 0.6
        and known_source
    )
    if allowed:
        summary = f"Workflow bundle `{bundle}` is active for this request (source: {source_text})."
        next_step = "Follow the workflow bundle first, use the source explanation to justify the journey, then use the recommended progress anchor to resume safely."
    else:
        summary = "No special workflow bundle is required for this request."
        next_step = "Keep execution lightweight and follow the lead plus active process skills only."
    return {
        "allowed": allowed,
        "summary": summary,
        "details": {
            "workflow_bundle": bundle,
            "bundle_confidence": numeric_confidence,
            "workflow_bundle_source": source_text,
            "workflow_bundle_source_explanation": source_explanations.get(
                source_text,
                "Unknown workflow bundle source. Re-check the router contract before treating the bundle as authoritative.",
            ),
            "progress_anchor_recommended": progress_anchor,
            "resume_artifacts": resume_artifacts,
            "workflow_steps": workflow_steps,
            "bundle_bootstrap": bundle_bootstrap,
        },
        "recommended_next_step": next_step,
    }


def _verify_bundle_bootstrap(result: dict[str, object], repo_path: Path) -> dict[str, object]:
    bundle = str(result.get("workflow_bundle", ""))
    bundle_source = str(result.get("workflow_bundle_source", ""))
    progress_anchor = result.get("progress_anchor_recommended")
    resume_artifacts = result.get("resume_artifacts", [])
    if not isinstance(resume_artifacts, list):
        resume_artifacts = []
    workflow_steps = result.get("workflow_steps", [])
    if not isinstance(workflow_steps, list):
        workflow_steps = []

    bootstrap = result.get("workflow_bundle_bootstrap", {})
    if not isinstance(bootstrap, dict):
        bootstrap = {}
    bootstrap_required = bool(bootstrap.get("required"))
    reference = bootstrap.get("reference")
    if not isinstance(reference, str):
        reference = None
    commands = bootstrap.get("commands", [])
    if not isinstance(commands, list):
        commands = []
    artifacts = bootstrap.get("artifacts", [])
    if not isinstance(artifacts, list):
        artifacts = []
    resume_anchor = bootstrap.get("resume_anchor")
    if not isinstance(resume_anchor, str):
        resume_anchor = None

    missing_contract_fields: list[str] = []
    if bootstrap_required:
        if reference is None:
            missing_contract_fields.append("reference")
        if len(commands) == 0:
            missing_contract_fields.append("commands")
        if len(artifacts) == 0:
            missing_contract_fields.append("artifacts")
        if resume_anchor is None:
            missing_contract_fields.append("resume_anchor")

    progress_anchor_matches_resume_anchor = (
        resume_anchor is not None and progress_anchor == resume_anchor
    )
    resume_anchor_in_artifacts = resume_anchor in artifacts if resume_anchor else False
    resume_anchor_in_resume_artifacts = (
        resume_anchor in resume_artifacts if resume_anchor else False
    )
    existing_artifacts = [
        artifact for artifact in artifacts if (repo_path / artifact).exists()
    ]
    missing_artifacts_on_disk = [
        artifact for artifact in artifacts if artifact not in existing_artifacts
    ]
    resume_anchor_exists = (repo_path / resume_anchor).exists() if resume_anchor else False
    workspace_ready = bootstrap_required and len(missing_artifacts_on_disk) == 0 and resume_anchor_exists
    if not bootstrap_required:
        workspace_state = "not-required"
    elif workspace_ready:
        workspace_state = "ready"
    elif len(existing_artifacts) == 0:
        workspace_state = "missing"
    else:
        workspace_state = "partial"
    bootstrap_command_required_now = bootstrap_required and not workspace_ready
    allowed = (
        bootstrap_required
        and len(missing_contract_fields) == 0
        and progress_anchor_matches_resume_anchor
        and resume_anchor_in_artifacts
        and resume_anchor_in_resume_artifacts
    )

    if allowed:
        summary = f"Workflow bundle bootstrap is required and contract-complete for `{bundle}`."
        if workspace_ready:
            next_step = "Bootstrap artifacts already exist. Resume directly from the bootstrap resume anchor."
        else:
            next_step = "Run the bootstrap command first, create the listed artifacts, then resume from the bootstrap resume anchor."
    elif bootstrap_required:
        summary = f"Workflow bundle bootstrap is required for `{bundle}` but the bootstrap contract is incomplete."
        next_step = "Repair the bootstrap contract so reference, commands, artifacts, and resume anchor all stay executable."
    else:
        summary = "Workflow bundle bootstrap is not required for this request."
        next_step = "Skip bootstrap and follow the active workflow bundle or direct execution path."

    return {
        "allowed": allowed,
        "summary": summary,
        "details": {
            "workflow_bundle": bundle,
            "workflow_bundle_source": bundle_source,
            "bootstrap_required": bootstrap_required,
            "progress_anchor_recommended": progress_anchor,
            "progress_anchor_matches_resume_anchor": progress_anchor_matches_resume_anchor,
            "resume_artifacts": resume_artifacts,
            "workflow_steps": workflow_steps,
            "bootstrap": {
                "required": bootstrap_required,
                "reference": reference,
                "commands": commands,
                "artifacts": artifacts,
                "resume_anchor": resume_anchor,
            },
            "missing_contract_fields": missing_contract_fields,
            "resume_anchor_in_artifacts": resume_anchor_in_artifacts,
            "resume_anchor_in_resume_artifacts": resume_anchor_in_resume_artifacts,
            "workspace_state": workspace_state,
            "workspace_ready": workspace_ready,
            "existing_artifacts": existing_artifacts,
            "missing_artifacts_on_disk": missing_artifacts_on_disk,
            "resume_anchor_exists": resume_anchor_exists,
            "bootstrap_command_required_now": bootstrap_command_required_now,
        },
        "recommended_next_step": next_step,
    }


def _verify_assistant_delta_contract(result: dict[str, object]) -> dict[str, object]:
    contract = result.get("assistant_delta_contract", {})
    if not isinstance(contract, dict):
        contract = {}
    assistants = result.get("assistant_agents", [])
    if not isinstance(assistants, list):
        assistants = []
    by_agent = contract.get("by_agent", {})
    if not isinstance(by_agent, dict):
        by_agent = {}
    strict_mode = bool(contract.get("strict_mode"))

    enabled = bool(contract.get("enabled"))
    required_fields = contract.get("required_fields", [])
    if not isinstance(required_fields, list):
        required_fields = []
    special_field_failures: list[str] = []
    required_field_failures: list[str] = []

    for agent in assistants:
        fields = by_agent.get(agent, [])
        if not isinstance(fields, list):
            fields = []
        missing_required = [field for field in required_fields if field not in fields]
        if missing_required:
            required_field_failures.append(f"{agent}: missing required fields {', '.join(missing_required)}")
        extra_fields = [field for field in fields if field not in required_fields]
        if strict_mode and len(extra_fields) == 0:
            special_field_failures.append(f"{agent}: missing agent-specific delta field")

    allowed = (
        len(assistants) > 0
        and enabled
        and all(field in required_fields for field in ["claim", "evidence", "decision"])
        and all(agent in by_agent for agent in assistants)
        and len(required_field_failures) == 0
        and len(special_field_failures) == 0
    )
    if allowed:
        summary = "Assistant delta contract is active and structurally valid for this request."
        next_step = "Keep assistant responses compact and require only claim/evidence/decision plus agent-specific delta fields."
    else:
        summary = "Assistant delta contract is not active for this request."
        next_step = "If assistants are introduced, re-run verification so the lead merges structured delta instead of loose role fragments."
    return {
        "allowed": allowed,
        "summary": summary,
        "details": {
            "assistant_delta_contract": contract,
            "assistant_count": len(assistants),
            "assistants": assistants,
            "required_field_failures": required_field_failures,
            "special_field_failures": special_field_failures,
        },
        "recommended_next_step": next_step,
    }


def _verify_auto_mode(result: dict[str, object], repo_path: Path) -> dict[str, object]:
    profile = result.get("auto_run_profile", {})
    if not isinstance(profile, dict):
        profile = {}
    enabled = bool(profile.get("enabled"))
    workflow_supported = bool(profile.get("workflow_supported"))
    requested_phase = str(profile.get("requested_phase", "manual")).strip() or "manual"
    plan_json = str(profile.get("plan_json", "")).strip()
    plan_path = (repo_path / plan_json).resolve() if plan_json else None
    plan_exists = plan_path.exists() if plan_path is not None else False
    requires_explicit_go = bool(profile.get("requires_explicit_go", True))
    explicit_go_requested = requested_phase == "go"
    allowed = enabled and workflow_supported and (
        not explicit_go_requested or (requires_explicit_go and plan_exists)
    )
    if allowed:
        if explicit_go_requested:
            summary = "Auto mode is enabled, workflow-supported, and ready for the explicit go phase."
            next_step = str(profile.get("go_command", "")).strip() or "Run the auto go command from the saved plan."
        else:
            summary = "Auto mode is enabled for this request and is ready to generate a setup plan."
            next_step = str(profile.get("setup_command", "")).strip() or "Run the auto setup command first."
    elif enabled and not workflow_supported:
        summary = "Auto mode is explicitly requested, but this workflow is outside the current auto-run whitelist."
        next_step = "Stay in manual mode for this workflow, or reroute into root-cause, release, or post-release close-loop."
    elif enabled and explicit_go_requested and not plan_exists:
        summary = "Auto go was requested, but the saved auto-run plan does not exist yet."
        next_step = "Run auto setup first so .vidt/auto/auto-run-plan.json exists before go."
    else:
        summary = "Auto mode is not enabled for this request."
        next_step = "Stay in manual mode unless the user explicitly asks for /auto."
    return {
        "allowed": allowed,
        "summary": summary,
        "details": {
            "auto_mode_enabled": enabled,
            "trigger": str(profile.get("trigger", "none")),
            "requested_phase": requested_phase,
            "execution_mode": str(profile.get("execution_mode", "manual")),
            "run_style": str(profile.get("run_style", "foreground")),
            "safety_level": str(profile.get("safety_level", "standard")),
            "resume_requested": bool(profile.get("resume_requested")),
            "detached_ready": bool(profile.get("detached_ready")),
            "workflow_bundle": str(profile.get("workflow_bundle", result.get("workflow_bundle", ""))),
            "workflow_supported": workflow_supported,
            "eligible_workflows": profile.get("eligible_workflows", []),
            "requires_explicit_go": requires_explicit_go,
            "setup_command": str(profile.get("setup_command", "")),
            "go_command": str(profile.get("go_command", "")),
            "plan_json": plan_json,
            "plan_exists": plan_exists,
            "resume_anchor": str(profile.get("resume_anchor", "")),
            "state_dir": str(profile.get("state_dir", "")),
            "automation_state_schema": str(profile.get("automation_state_schema", "")),
            "safety_guards": profile.get("safety_guards", []),
            "eligibility_reason": str(profile.get("eligibility_reason", "")),
        },
        "recommended_next_step": next_step,
    }


def _micro_practice_names(result: dict[str, object]) -> list[str]:
    names = result.get("micro_practice_names", [])
    if isinstance(names, list):
        compact_names = [str(item).strip() for item in names if str(item).strip()]
        if compact_names:
            return compact_names

    practices = result.get("micro_practices", [])
    if not isinstance(practices, list):
        return []
    compact_names = []
    for item in practices:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name", "")).strip()
        if name:
            compact_names.append(name)
    return compact_names


def _micro_practice_ledger_contract(result: dict[str, object]) -> dict[str, object]:
    bootstrap = result.get("workflow_bundle_bootstrap", {})
    if not isinstance(bootstrap, dict):
        bootstrap = {}
    ledger = bootstrap.get("micro_practice_ledger", {})
    return ledger if isinstance(ledger, dict) else {}


def _verify_micro_practice_ledger(result: dict[str, object], repo_path: Path) -> dict[str, object]:
    names = _micro_practice_names(result)
    ledger_contract = _micro_practice_ledger_contract(result)
    ledger_required = bool(ledger_contract.get("required")) or len(names) > 0
    ledger_rel = str(ledger_contract.get("resume_anchor", "")).strip() or ".vidt/practices/micro-practice-ledger.json"
    ledger_path = (repo_path / ledger_rel).resolve()
    ledger_exists = ledger_path.exists()
    init_command = str(ledger_contract.get("command", "")).strip() or (
        'python scripts/init_micro_practices.py --root . --text "<user request>" --pretty'
    )
    evaluation_command = str(ledger_contract.get("evaluation_command", "")).strip() or (
        f"python scripts/evaluate_micro_practices.py --ledger {ledger_rel} --pretty"
    )

    evaluation: dict[str, object] | None = None
    evaluation_error = ""
    decision = "not-required"
    status_counts = {"total": 0, "active": 0, "satisfied": 0, "blocked": 0}
    completion_allowed = not ledger_required
    recommended_commands: list[str] = []
    missing_required_practices: list[str] = []

    if ledger_required and not ledger_exists:
        decision = "missing"
        recommended_commands = [init_command, evaluation_command]
        summary = "Micro-practice ledger is required for this request but is missing."
        next_step = "Initialize the micro-practice ledger, capture practice evidence, then re-run this check before claiming completion."
    elif ledger_required:
        try:
            evaluation = micro_practice_evaluator.evaluate_micro_practices(
                ledger_path,
                write_reports=False,
            )
            decision = str(evaluation.get("decision", "")).strip()
            raw_counts = evaluation.get("status_counts", {})
            if isinstance(raw_counts, dict):
                status_counts = {
                    "total": int(raw_counts.get("total", 0)),
                    "active": int(raw_counts.get("active", 0)),
                    "satisfied": int(raw_counts.get("satisfied", 0)),
                    "blocked": int(raw_counts.get("blocked", 0)),
                }
            follow_up = evaluation.get("follow_up", {})
            if isinstance(follow_up, dict):
                completion_allowed = bool(follow_up.get("completion_allowed"))
                raw_commands = follow_up.get("recommended_commands", [])
                if isinstance(raw_commands, list):
                    recommended_commands = [
                        str(command).strip()
                        for command in raw_commands
                        if str(command).strip()
                    ]
            practices = evaluation.get("practices", [])
            evaluated_names = {
                str(item.get("name", "")).strip()
                for item in practices
                if isinstance(item, dict) and str(item.get("name", "")).strip()
            } if isinstance(practices, list) else set()
            missing_required_practices = [
                name for name in names if name not in evaluated_names
            ]
            if missing_required_practices:
                decision = "mismatch"
                completion_allowed = False
                recommended_commands = [f"{init_command} --overwrite", evaluation_command]
            if completion_allowed:
                summary = "Micro-practice ledger is complete; completion can use it as evidence."
                next_step = "Use the ledger evaluation as completion evidence and keep the ledger path in the handoff or commit evidence."
            elif missing_required_practices:
                summary = "Micro-practice ledger exists but does not cover the practices required by this route."
                next_step = "Reinitialize the ledger for the current request, then update and evaluate the required practices before completion."
            elif decision == "blocked":
                summary = "Micro-practice ledger has blocked practices; completion is not allowed yet."
                next_step = "Resolve or reclassify blocked practices, update the ledger with evidence, then re-run the ledger evaluation."
            else:
                summary = "Micro-practice ledger still has active practices; completion is not allowed yet."
                next_step = "Capture concrete evidence for active practices, update the ledger, then re-run the ledger evaluation."
        except Exception as exc:
            decision = "invalid"
            evaluation_error = str(exc)
            completion_allowed = False
            recommended_commands = [evaluation_command]
            summary = "Micro-practice ledger exists but could not be evaluated."
            next_step = "Repair the ledger so it matches references/micro-practice-ledger.schema.json, then re-run evaluation."
    else:
        summary = "No micro-practice ledger is required for this request."
        next_step = "Keep the completion path lightweight; do not force a ledger when the router did not activate micro-practices."

    return {
        "allowed": completion_allowed,
        "summary": summary,
        "details": {
            "micro_practice_required": ledger_required,
            "active_practices": names,
            "ledger_path": ledger_rel,
            "ledger_exists": ledger_exists,
            "decision": decision,
            "completion_allowed": completion_allowed,
            "status_counts": status_counts,
            "evaluation": evaluation,
            "evaluation_error": evaluation_error,
            "missing_required_practices": missing_required_practices,
            "init_command": init_command,
            "evaluation_command": evaluation_command,
            "recommended_commands": recommended_commands,
        },
        "recommended_next_step": next_step,
    }


def _repo_relative(path: Path, repo_path: Path) -> str:
    try:
        return str(path.resolve().relative_to(repo_path.resolve()))
    except ValueError:
        return str(path.resolve())


def _verify_completion_evidence(
    result: dict[str, object],
    repo_path: Path,
    completion_evidence: Path | None = None,
) -> dict[str, object]:
    default_evidence_rel = ".vidt/evidence/completion-evidence.json"
    requested_path = completion_evidence or Path(default_evidence_rel)
    evidence_path = (
        requested_path.resolve()
        if requested_path.is_absolute()
        else (repo_path / requested_path).resolve()
    )
    evidence_rel = _repo_relative(evidence_path, repo_path)
    evidence_exists = evidence_path.exists()
    template = "assets/completion-evidence-template.json"
    schema = "references/completion-evidence.schema.json"
    parent_rel = str(Path(evidence_rel).parent)
    init_command = (
        f"mkdir -p {parent_rel} && cp assets/completion-evidence-template.json {evidence_rel}"
        if parent_rel not in {"", "."}
        else f"cp assets/completion-evidence-template.json {evidence_rel}"
    )
    verify_command = (
        f"python scripts/verify_completion_evidence.py --evidence {evidence_rel} --pretty"
    )

    verification: dict[str, object] | None = None
    verification_error = ""
    if not evidence_exists:
        allowed = False
        decision = "missing"
        summary = "Completion evidence is required before a done/ready/handoff claim but is missing."
        next_step = "Create completion evidence from the template, fill direct evidence, then re-run this check."
        recommended_commands = [init_command, verify_command]
    else:
        try:
            verification = completion_evidence_verifier.evaluate_completion_evidence(evidence_path)
            allowed = bool(verification.get("completion_allowed"))
            decision = str(verification.get("decision", "")).strip()
            follow_up = verification.get("follow_up", {})
            if isinstance(follow_up, dict):
                raw_commands = follow_up.get("recommended_commands", [])
                recommended_commands = [
                    str(command).strip()
                    for command in raw_commands
                    if str(command).strip()
                ] if isinstance(raw_commands, list) else [verify_command]
            else:
                recommended_commands = [verify_command]
            if allowed:
                summary = "Completion evidence is present and supports the completion claim."
                next_step = "Use the completion evidence slots in the final done/ready/handoff claim."
            elif decision == "blocked":
                summary = "Completion evidence is present but structurally blocks completion."
                next_step = "Repair failed or incomplete evidence before claiming completion."
            else:
                summary = "Completion evidence is present but still indicates uncovered scope or residual risk."
                next_step = "Close uncovered scope or residual risk, then re-run completion evidence verification."
        except Exception as exc:
            allowed = False
            decision = "invalid"
            verification_error = str(exc)
            summary = "Completion evidence exists but could not be evaluated."
            next_step = "Repair the evidence JSON so it matches references/completion-evidence.schema.json."
            recommended_commands = [verify_command]

    return {
        "allowed": allowed,
        "summary": summary,
        "details": {
            "completion_evidence_required": True,
            "evidence_path": evidence_rel,
            "evidence_exists": evidence_exists,
            "decision": decision,
            "completion_allowed": allowed,
            "template": template,
            "schema": schema,
            "verification": verification,
            "verification_error": verification_error,
            "init_command": init_command,
            "verify_command": verify_command,
            "recommended_commands": recommended_commands,
        },
        "recommended_next_step": next_step,
    }


ALLOWED_HANDOFF_TYPES = {
    "WorkOrder",
    "ImplementationOutput",
    "VerificationReport",
    "DeliveryCycleReport",
    "RemediationPatch",
}

ALLOWED_HANDOFF_DIRECTIONS = {
    ("Lead", "Worker"),
    ("Worker", "Verifier"),
    ("Verifier", "Lead"),
    ("Verifier", "Worker"),
}

HANDOFF_CONTRACT = {
    "WorkOrder": ("Lead", "Worker"),
    "ImplementationOutput": ("Worker", "Verifier"),
    "VerificationReport": ("Verifier", "Lead"),
    "DeliveryCycleReport": ("Verifier", "Lead"),
    "RemediationPatch": ("Verifier", "Worker"),
}


def _valid_handoff_timestamp(value: str) -> bool:
    if not value.strip():
        return False
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None


def _verify_file_handoff(
    result: dict[str, object],
    repo_path: Path,
    handoff_dir: Path | None = None,
    handoff_type: str | None = None,
) -> dict[str, object]:
    """校验角色间交接物是否落文件,禁止 prompt 粘贴"""
    default_dir = ".vidt/handoff"
    dir_rel = str(handoff_dir) if handoff_dir else default_dir
    dir_rel = dir_rel.rstrip("/")
    handoff_path = (repo_path / dir_rel).resolve()
    dir_exists = handoff_path.is_dir()

    files_checked: list[dict[str, object]] = []
    missing_handoff_meta: list[str] = []
    invalid_directions: list[str] = []
    invalid_types: list[str] = []
    invalid_contracts: list[str] = []
    invalid_paths: list[str] = []
    invalid_timestamps: list[str] = []
    total_files = 0
    matching_files = 0

    if dir_exists:
        for entry in sorted(handoff_path.iterdir()):
            if not entry.is_file() or entry.suffix != ".json":
                continue
            total_files += 1
            rel = _repo_relative(entry, repo_path)
            try:
                with open(entry, "r", encoding="utf-8") as f:
                    data = json.load(f)
                meta = data.get("handoff")
                if not isinstance(meta, dict):
                    missing_handoff_meta.append(rel)
                    continue
                required_fields = (
                    "from_role",
                    "to_role",
                    "artifact_type",
                    "artifact_path",
                    "timestamp",
                )
                missing_fields = [field for field in required_fields if not str(meta.get(field, "")).strip()]
                if missing_fields:
                    missing_handoff_meta.append(f"{rel}: missing {', '.join(missing_fields)}")
                from_role = str(meta.get("from_role", ""))
                to_role = str(meta.get("to_role", ""))
                artifact_type = str(meta.get("artifact_type", ""))
                artifact_path = str(meta.get("artifact_path", ""))
                timestamp = str(meta.get("timestamp", ""))
                if (from_role, to_role) not in ALLOWED_HANDOFF_DIRECTIONS:
                    invalid_directions.append(f"{rel}: {from_role}->{to_role}")
                if artifact_type not in ALLOWED_HANDOFF_TYPES:
                    invalid_types.append(f"{rel}: {artifact_type}")
                expected_direction = HANDOFF_CONTRACT.get(artifact_type)
                if expected_direction is not None and (from_role, to_role) != expected_direction:
                    invalid_contracts.append(
                        f"{rel}: {artifact_type} requires {expected_direction[0]}->{expected_direction[1]}, "
                        f"got {from_role}->{to_role}"
                    )
                path_valid = False
                if artifact_path and not Path(artifact_path).is_absolute():
                    declared_path = (repo_path / artifact_path).resolve()
                    try:
                        declared_path.relative_to(repo_path.resolve())
                        path_valid = declared_path == entry.resolve()
                    except ValueError:
                        path_valid = False
                if not path_valid:
                    invalid_paths.append(f"{rel}: artifact_path={artifact_path!r}")
                timestamp_valid = _valid_handoff_timestamp(timestamp)
                if not timestamp_valid:
                    invalid_timestamps.append(f"{rel}: timestamp={timestamp!r}")
                if handoff_type and artifact_type != handoff_type:
                    matches_filter = False
                else:
                    matches_filter = True
                    matching_files += 1
                contract_valid = (
                    not missing_fields
                    and (from_role, to_role) in ALLOWED_HANDOFF_DIRECTIONS
                    and artifact_type in ALLOWED_HANDOFF_TYPES
                    and expected_direction == (from_role, to_role)
                    and path_valid
                    and timestamp_valid
                )
                files_checked.append({
                    "file": rel,
                    "from_role": from_role,
                    "to_role": to_role,
                    "artifact_type": artifact_type,
                    "artifact_path": artifact_path,
                    "timestamp": timestamp,
                    "matches_filter": matches_filter,
                    "valid": contract_valid,
                })
            except (json.JSONDecodeError, OSError):
                missing_handoff_meta.append(rel)

    has_failures = bool(
        missing_handoff_meta
        or invalid_directions
        or invalid_types
        or invalid_contracts
        or invalid_paths
        or invalid_timestamps
    )
    required_file_count = matching_files if handoff_type else total_files
    allowed = dir_exists and required_file_count > 0 and not has_failures

    if not dir_exists:
        summary = f"Handoff directory '{dir_rel}' does not exist. No file handoffs found."
        next_step = f"Create '{dir_rel}/' and write handoff artifacts before invoking Verifier."
    elif total_files == 0:
        summary = f"Handoff directory '{dir_rel}' exists but contains no JSON artifacts."
        next_step = "Write WorkOrder/ImplementationOutput/VerificationReport to the handoff directory."
    elif handoff_type and matching_files == 0:
        summary = f"No handoff artifact matches required type '{handoff_type}'."
        next_step = f"Write a valid {handoff_type} artifact before invoking the next role."
    elif has_failures:
        summary = "Handoff artifacts exist but some have invalid metadata, role contract, timestamp, or path identity."
        next_step = "Fix all five handoff metadata fields and make artifact_path identify the file being verified."
    else:
        summary = f"All {required_file_count} required handoff artifact(s) passed schema, identity, and direction checks."
        next_step = "Proceed to Verifier; file handoff contract is satisfied."

    return {
        "allowed": allowed,
        "summary": summary,
        "details": {
            "handoff_dir": dir_rel,
            "dir_exists": dir_exists,
            "total_files": total_files,
            "matching_files": matching_files,
            "files_checked": files_checked,
            "missing_handoff_meta": missing_handoff_meta,
            "invalid_directions": invalid_directions,
            "invalid_types": invalid_types,
            "invalid_contracts": invalid_contracts,
            "invalid_paths": invalid_paths,
            "invalid_timestamps": invalid_timestamps,
            "filter_type": handoff_type,
        },
        "recommended_next_step": next_step,
    }


def _verify_spec_violation(
    result: dict[str, object],
    repo_path: Path,
    worker_output: Path | None = None,
    config: dict[str, object] | None = None,
) -> dict[str, object]:
    """检查 Worker 产出是否违反 routing-rules.json 中的 agent constraints"""
    lead_agent = str(result.get("lead_agent", ""))
    agent_rules = {}
    if config and isinstance(config, dict):
        raw_rules = config.get("agent_rules", {})
        if isinstance(raw_rules, dict):
            agent_rules = raw_rules

    constraints: list[str] = []
    if lead_agent and lead_agent in agent_rules:
        agent_entry = agent_rules[lead_agent]
        if isinstance(agent_entry, dict):
            raw_constraints = agent_entry.get("constraints", [])
            if isinstance(raw_constraints, list):
                constraints = [str(c) for c in raw_constraints]

    output_text = ""
    output_rel = ""
    output_exists = False
    if worker_output:
        output_path = worker_output.resolve() if worker_output.is_absolute() else (repo_path / worker_output).resolve()
        output_exists = output_path.exists()
        output_rel = _repo_relative(output_path, repo_path) if output_exists else str(worker_output)
        if output_exists:
            try:
                output_text = output_path.read_text(encoding="utf-8")
            except OSError:
                output_text = ""

    state_ownership_constraint = (
        "State fields must be written only by the owner layers declared in references/state-schema-spec.md"
    )
    constraints.append(state_ownership_constraint)
    violations: list[dict[str, str]] = []
    if constraints and output_text:
        output_text_lower = output_text.lower()
        for constraint in constraints:
            constraint_lower = constraint.lower()
            if "java.util.date" in constraint_lower and "java.util.date" in output_text_lower:
                violations.append({"constraint": constraint, "evidence": "java.util.date found in output"})
            if "stream.parallel" in constraint_lower and "stream.parallel" in output_text_lower:
                violations.append({"constraint": constraint, "evidence": "Stream.parallel() found in output"})
            if "force push" in constraint_lower or "force-push" in constraint_lower:
                if "force push" in output_text_lower or "force-push" in output_text_lower:
                    violations.append({"constraint": constraint, "evidence": "force push mentioned in output"})

        mutation_detected = bool(
            re.search(r"\b(modif(?:y|ied)|writ(?:e|es|ten)|updat(?:e|ed)|overwrit(?:e|ten)|mutat(?:e|ed))\b", output_text_lower)
        )
        state_owners = {
            "plan": {"layer1", "layer 1", "planning"},
            "route": {"layer2", "layer 2", "routing"},
            "delivery": {"layer3", "layer 3", "delivery", "layer7", "layer 7", "layer7_subgraph"},
            "iteration": {"layer4", "layer 4", "iteration"},
            "release": {"layer5", "layer 5", "release"},
        }
        all_layer_markers = set().union(*state_owners.values())
        if mutation_detected:
            for field, allowed_writers in state_owners.items():
                if not re.search(rf"\b{re.escape(field)}(?:\.|\b)", output_text_lower):
                    continue
                observed_writers = {
                    marker for marker in all_layer_markers if marker in output_text_lower
                }
                unauthorized = sorted(observed_writers - allowed_writers)
                if unauthorized:
                    violations.append(
                        {
                            "constraint": state_ownership_constraint,
                            "evidence": (
                                f"mutation of state field '{field}' mentions unauthorized writer(s): "
                                f"{', '.join(unauthorized)}"
                            ),
                        }
                    )

    has_violations = len(violations) > 0
    if not worker_output:
        allowed = True
        verdict = "pass"
        summary = "No worker output provided for spec violation check; skipping."
        next_step = "Provide --worker-output to check spec compliance."
    elif not output_exists:
        allowed = False
        verdict = "hold"
        summary = f"Worker output '{output_rel}' does not exist; cannot check spec compliance."
        next_step = "Ensure Worker writes output to the specified path before verification."
    elif has_violations:
        allowed = False
        verdict = "spec_violation"
        summary = f"Worker output violates {len(violations)} spec constraint(s) for '{lead_agent}'."
        next_step = "Fix violations; see details for specific constraints and evidence."
    else:
        allowed = True
        verdict = "pass"
        summary = f"Worker output complies with all {len(constraints)} spec constraint(s) for '{lead_agent}'."
        next_step = "Proceed to WorkOrder completion check."

    return {
        "allowed": allowed,
        "summary": summary,
        "details": {
            "lead_agent": lead_agent,
            "constraints_checked": len(constraints),
            "constraints": constraints,
            "worker_output": output_rel,
            "output_exists": output_exists,
            "verdict": verdict,
            "violations": violations,
            "spec_file": "references/routing-rules.json; references/state-schema-spec.md",
        },
        "recommended_next_step": next_step,
    }


PREJUDGMENT_PATTERNS = [
    "应该没问题",
    "肯定能过",
    "可以 ship",
    "可以ship",
    "肯定没问题",
    "应该能过",
    "肯定通过",
    "应该通过",
    "肯定行",
    "should be fine",
    "will pass",
    "can ship",
    "definitely pass",
    "should pass",
    "no problem",
]

ASSUMPTION_MARKERS = ["假设", "assuming", "assume"]


def _is_assumption_context(text: str, pos: int, window: int = 15) -> bool:
    """检查关键词所在位置前 window 个字符内是否有假设标记"""
    start = max(0, pos - window)
    prefix = text[start:pos].lower()
    return any(marker in prefix for marker in ASSUMPTION_MARKERS)


def _verify_lead_prejudgment(
    result: dict[str, object],
    dispatch_text: str | None = None,
) -> dict[str, object]:
    """检测 Lead 在 Verifier 出 verdict 前的预判性语言"""
    text = dispatch_text or ""
    hits: list[dict[str, str]] = []
    text_lower = text.lower()
    for pattern in PREJUDGMENT_PATTERNS:
        pattern_lower = pattern.lower()
        search_from = 0
        while True:
            idx = text_lower.find(pattern_lower, search_from)
            if idx == -1:
                break
            if not _is_assumption_context(text_lower, idx):
                context_start = max(0, idx - 10)
                context_end = min(len(text), idx + len(pattern) + 10)
                hits.append({
                    "pattern": pattern,
                    "context": text[context_start:context_end].strip(),
                })
            search_from = idx + len(pattern)

    has_hits = len(hits) > 0
    if has_hits:
        summary = f"Lead dispatch contains {len(hits)} prejudgment pattern(s) before Verifier verdict."
        next_step = "Remove final judgment statements from Lead dispatch; restate as assumptions if needed."
    else:
        summary = "No prejudgment patterns detected in Lead dispatch."
        next_step = "Proceed with normal Lead-to-Worker dispatch."

    return {
        "allowed": not has_hits,
        "summary": summary,
        "details": {
            "dispatch_length": len(text),
            "patterns_checked": len(PREJUDGMENT_PATTERNS),
            "hits": hits,
        },
        "recommended_next_step": next_step,
    }


YAGNI_PATTERNS = [
    {"pattern": r"interface\s+\w+", "label": "new interface"},
    {"pattern": r"class\s+\w+Factory", "label": "new factory class"},
    {"pattern": r"abstract\s+class\s+\w+", "label": "new abstract class"},
    {"pattern": r"middleware", "label": "new middleware"},
    {"pattern": r"class\s+\w+Adapter", "label": "new adapter"},
    {"pattern": r"class\s+\w+Proxy", "label": "new proxy"},
    {"pattern": r"class\s+\w+Wrapper", "label": "new wrapper"},
]

YAGNI_RED_LINE_KEYWORDS = [
    "security",
    "auth",
    "encrypt",
    "decrypt",
    "a11y",
    "accessibility",
    "transaction",
    "backup",
    "idempotent",
    "sanitize",
    "validate",
    "escape",
]


def _verify_yagni(
    result: dict[str, object],
    diff_file: Path | None = None,
) -> dict[str, object]:
    """检测 Worker 产出中未被请求的抽象(YAGNI 门禁)"""
    import re

    if not diff_file:
        return {
            "allowed": True,
            "summary": "No diff file provided; YAGNI check skipped.",
            "details": {
                "diff_file": "",
                "diff_exists": False,
                "added_lines_scanned": 0,
                "hits": [],
                "red_line_keywords_found": [],
            },
            "recommended_next_step": "Provide --diff-file to enable YAGNI abstraction scan.",
        }

    diff_path = diff_file.resolve() if diff_file.is_absolute() else Path.cwd() / diff_file
    diff_exists = diff_path.exists()
    hits: list[dict[str, str]] = []
    red_line_found: list[str] = []

    if diff_exists:
        content = diff_path.read_text(encoding="utf-8", errors="replace")
        added_lines = [
            line[1:] for line in content.splitlines()
            if line.startswith("+") and not line.startswith("+++")
        ]
        content_lower = content.lower()
        for kw in YAGNI_RED_LINE_KEYWORDS:
            if kw in content_lower:
                red_line_found.append(kw)

        for item in YAGNI_PATTERNS:
            regex = re.compile(item["pattern"], re.IGNORECASE)
            for line in added_lines:
                match = regex.search(line)
                if match:
                    hits.append({
                        "label": item["label"],
                        "match": match.group(),
                        "context": line.strip()[:120],
                    })

    has_hits = len(hits) > 0
    if has_hits:
        summary = f"YAGNI check found {len(hits)} suspicious abstraction pattern(s)."
        next_step = "Review hits; remove unrequested abstractions or justify with WorkOrder requirements."
    else:
        summary = "No YAGNI violations detected." if diff_exists else "Diff file not found; YAGNI check skipped."
        next_step = "Proceed with normal verification." if diff_exists else "Provide a valid diff file path."

    return {
        "allowed": not has_hits,
        "summary": summary,
        "details": {
            "diff_file": str(diff_file),
            "diff_exists": diff_exists,
            "added_lines_scanned": len(added_lines) if diff_exists else 0,
            "hits": hits,
            "red_line_keywords_found": red_line_found,
        },
        "recommended_next_step": next_step,
    }


def _verify_breaker_status(
    result: dict[str, object],
    breaker_layer: str,
    breaker_config: Path | None = None,
    breaker_state_file: Path | None = None,
    breaker_escalation_sink: Path | None = None,
) -> dict[str, object]:
    """检查指定层的 circuit breaker 状态(advisory,不 hard exit)"""
    config_path = breaker_config or DEFAULT_BREAKER_CONFIG_PATH
    state_file = breaker_state_file or DEFAULT_BREAKER_STATE_FILE
    escalation_sink = breaker_escalation_sink or DEFAULT_BREAKER_ESCALATION_SINK
    breaker = circuit_breaker_module.CircuitBreaker(
        config_path=config_path,
        state_file=state_file,
        escalation_sink=escalation_sink,
    )
    check_result = breaker.check(breaker_layer)
    state = str(check_result.get("state", "closed"))
    allowed = bool(check_result.get("allowed", True))
    consecutive_failures = int(check_result.get("consecutive_failures", 0))
    if allowed:
        summary = f"Circuit breaker for layer '{breaker_layer}' is {state}. Action allowed."
        next_step = "Proceed with the action. Breaker is not blocking."
    else:
        summary = f"Circuit breaker for layer '{breaker_layer}' is {state}. Action blocked."
        next_step = "Do not proceed. Escalate or wait for cooldown. See .vidt/harness/escalation-queue.jsonl."
    return {
        "allowed": allowed,
        "summary": summary,
        "details": {
            "layer": breaker_layer,
            "breaker_state": state,
            "consecutive_failures": consecutive_failures,
            "reason": str(check_result.get("reason", "")),
            "fail_closed": bool(check_result.get("fail_closed", False)),
            "state_file": str(state_file),
            "escalation_sink": str(escalation_sink),
        },
        "recommended_next_step": next_step,
    }


def _verify_contract_lock(
    result: dict[str, object],
    contract_spec: Path | None = None,
) -> dict[str, object]:
    """检查前后端协作的 contract-spec 是否存在且双方签署(P1-5)

    参数:
        result: 路由结果
        contract_spec: contract-spec 文件路径,为 None 时跳过检查
    """
    if not contract_spec:
        return {
            "allowed": True,
            "summary": "No contract-spec path provided; contract lock check skipped.",
            "details": {
                "contract_spec": "",
                "spec_exists": False,
                "signatures_complete": False,
                "both_accepted": False,
                "missing_parties": [],
                "content_consistent": False,
                "content_mismatches": [],
                "parse_error": "",
            },
            "recommended_next_step": "Provide --contract-spec to enable contract lock verification.",
        }

    spec_path = contract_spec.resolve() if contract_spec.is_absolute() else Path.cwd() / contract_spec
    spec_exists = spec_path.exists()
    signatures_complete = False
    both_accepted = False
    missing_parties: list[str] = []
    content_consistent = False
    content_mismatches: list[str] = []
    parse_error = ""

    if spec_exists:
        try:
            spec_data = json.loads(spec_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            spec_data = {}
            parse_error = f"{type(exc).__name__}: {exc}"
        signatures = spec_data.get("signatures", {}) if isinstance(spec_data, dict) else {}
        frontend = signatures.get("frontend_lead", {}) if isinstance(signatures, dict) else {}
        backend = signatures.get("backend_lead", {}) if isinstance(signatures, dict) else {}
        if not frontend:
            missing_parties.append("frontend_lead")
        if not backend:
            missing_parties.append("backend_lead")
        signatures_complete = len(missing_parties) == 0
        if signatures_complete:
            both_accepted = bool(frontend.get("accepted", False)) and bool(backend.get("accepted", False))
        fields = spec_data.get("fields") if isinstance(spec_data, dict) else None
        if isinstance(fields, dict) and ("frontend" in fields or "backend" in fields):
            frontend_fields = fields.get("frontend", {})
            backend_fields = fields.get("backend", {})
            if not isinstance(frontend_fields, dict) or not isinstance(backend_fields, dict):
                content_mismatches.append("fields.frontend and fields.backend must both be objects")
            else:
                frontend_keys = set(str(key) for key in frontend_fields)
                backend_keys = set(str(key) for key in backend_fields)
                if frontend_keys != backend_keys:
                    content_mismatches.append(
                        "field names differ: "
                        f"frontend={sorted(frontend_keys)}, backend={sorted(backend_keys)}"
                    )
                for field_name in sorted(frontend_keys & backend_keys):
                    if frontend_fields.get(field_name) != backend_fields.get(field_name):
                        content_mismatches.append(
                            f"field '{field_name}' type differs: "
                            f"frontend={frontend_fields.get(field_name)!r}, "
                            f"backend={backend_fields.get(field_name)!r}"
                        )
            content_consistent = len(content_mismatches) == 0
        else:
            # Canonical contract-spec/v1 has one shared request/response schema.
            content_consistent = bool(
                isinstance(spec_data, dict)
                and isinstance(spec_data.get("request_schema"), dict)
                and isinstance(spec_data.get("response_schema"), dict)
            )
            if not content_consistent and not parse_error:
                content_mismatches.append(
                    "contract must provide canonical request_schema/response_schema or comparable frontend/backend fields"
                )

    if not spec_exists:
        summary = "Contract-spec file not found; contract lock failed."
        next_step = "Create and co-sign contract-spec before Worker starts implementation."
    elif not signatures_complete:
        summary = f"Contract-spec signatures incomplete; missing: {', '.join(missing_parties)}."
        next_step = "Require both frontend_lead and backend_lead to sign the contract-spec."
    elif not both_accepted:
        summary = "Contract-spec signatures exist but not both accepted; contract lock failed."
        next_step = "Re-negotiate contract terms; both parties must set accepted=true."
    elif not content_consistent:
        summary = "Contract-spec signatures are accepted but the contract content is invalid or inconsistent."
        next_step = "Align frontend/backend field names and types, or provide the canonical shared request/response schema, then re-sign."
    else:
        summary = "Contract lock passed: contract-spec content is consistent and both parties signed."
        next_step = "Proceed with normal verification."

    return {
        "allowed": spec_exists and signatures_complete and both_accepted and content_consistent,
        "summary": summary,
        "details": {
            "contract_spec": str(contract_spec),
            "spec_exists": spec_exists,
            "signatures_complete": signatures_complete,
            "both_accepted": both_accepted,
            "missing_parties": missing_parties,
            "content_consistent": content_consistent,
            "content_mismatches": content_mismatches,
            "parse_error": parse_error,
        },
        "recommended_next_step": next_step,
    }


def _verify_observability_schema(
    result: dict[str, object],
    repo_path: Path,
) -> dict[str, object]:
    """校验可观测性三件套 schema（observability-protocol.md，P2-16）

    参数:
        result: 路由结果（本 check 不依赖路由结果，但保持接口一致）
        repo_path: 仓库根路径

    返回:
        outcome dict，含 allowed / summary / details / recommended_next_step
    """
    details: dict[str, object] = {}
    issues: list[str] = []

    try:
        self_test_output = StringIO()
        with redirect_stdout(self_test_output):
            emit_exit = emit_telemetry_module.self_test()
        details["emit_self_test_exit"] = emit_exit
        if emit_exit != 0:
            issues.append("emit_telemetry.py self-test failed")
    except Exception as exc:
        details["emit_self_test_exit"] = -1
        issues.append(f"emit_telemetry.py self-test raised: {exc!r}")

    try:
        build_health_report = inspect_decision_log_module.build_health_report
        health_schema_version = inspect_decision_log_module.HEALTH_REPORT_SCHEMA_VERSION
        report = build_health_report(
            repo_path,
            window_id="30d",
            markdown_output=None,
            html_output=None,
        )
        schema = str(report.get("schema_version", ""))
        details["health_schema_version"] = schema
        layers = report.get("layers", [])
        details["health_layer_count"] = len(layers) if isinstance(layers, list) else 0
        if schema != health_schema_version:
            issues.append(f"health report schema_version mismatch: {schema}")
    except Exception as exc:
        details["health_schema_version"] = ""
        details["health_layer_count"] = 0
        issues.append(f"health report raised: {exc!r}")

    skill_md = repo_path / "SKILL.md"
    protocol_file = repo_path / "references" / "observability-protocol.md"
    details["protocol_exists"] = protocol_file.exists()
    referenced = False
    if skill_md.exists() and protocol_file.exists():
        content = skill_md.read_text(encoding="utf-8")
        referenced = "observability-protocol" in content
    details["skill_md_references_protocol"] = referenced
    if not protocol_file.exists():
        issues.append("observability-protocol.md not found")
    if not referenced:
        issues.append("SKILL.md does not reference observability-protocol.md")

    allowed = len(issues) == 0
    if allowed:
        summary = "Observability schema valid: telemetry self-test passed, health report schema correct, protocol referenced."
        next_step = "All observability checks passed."
    else:
        summary = f"Observability schema issues: {'; '.join(issues)}"
        next_step = "Fix observability schema issues before release."

    return {
        "allowed": allowed,
        "summary": summary,
        "details": details,
        "recommended_next_step": next_step,
    }


def _build_explanation_card(result: dict[str, object]) -> dict[str, object]:
    payload = response_pack.build_response_pack_payload(result)
    return response_contract.build_explanation_card_from_payload(payload)


def verify_action(
    *,
    text: str,
    config: dict[str, object],
    repo_path: Path,
    check: str,
    process_skill: str | None = None,
    lead_agent: str | None = None,
    assistant_agents: list[str] | None = None,
    completion_evidence: Path | None = None,
    handoff_dir: Path | None = None,
    handoff_type: str | None = None,
    worker_output: Path | None = None,
    dispatch_text: str | None = None,
    diff_file: Path | None = None,
    breaker_layer: str | None = None,
    breaker_config: Path | None = None,
    breaker_state_file: Path | None = None,
    breaker_escalation_sink: Path | None = None,
    contract_spec: Path | None = None,
    iteration_workspace: Path | None = None,
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
        outcome = _verify_iteration(result, repo_path, iteration_workspace)
    elif check == "workflow-bundle":
        outcome = _verify_workflow_bundle(result)
    elif check == "bundle-bootstrap":
        outcome = _verify_bundle_bootstrap(result, repo_path)
    elif check == "assistant-delta-contract":
        outcome = _verify_assistant_delta_contract(result)
    elif check == "auto-mode":
        outcome = _verify_auto_mode(result, repo_path)
    elif check == "micro-practice-ledger":
        outcome = _verify_micro_practice_ledger(result, repo_path)
    elif check == "completion-evidence":
        outcome = _verify_completion_evidence(result, repo_path, completion_evidence)
    elif check == "file-handoff":
        outcome = _verify_file_handoff(result, repo_path, handoff_dir, handoff_type)
    elif check == "spec-violation":
        outcome = _verify_spec_violation(result, repo_path, worker_output, config)
    elif check == "lead-prejudgment":
        outcome = _verify_lead_prejudgment(result, dispatch_text)
    elif check == "yagni":
        outcome = _verify_yagni(result, diff_file)
    elif check == "breaker-status":
        if not breaker_layer:
            raise ValueError("--breaker-layer is required for check=breaker-status")
        outcome = _verify_breaker_status(
            result,
            breaker_layer,
            breaker_config,
            breaker_state_file,
            breaker_escalation_sink,
        )
    elif check == "contract-lock":
        outcome = _verify_contract_lock(result, contract_spec)
    elif check == "observability-schema":
        outcome = _verify_observability_schema(result, repo_path)
    else:
        raise ValueError(f"Unsupported check: {check}")

    output = {
        "ok": True,
        "check": check,
        "allowed": outcome["allowed"],
        "summary": outcome["summary"],
        "details": outcome["details"],
        "explanation_card": _build_explanation_card(result),
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
            "bundle_confidence": result.get("bundle_confidence"),
            "workflow_bundle_source": result.get("workflow_bundle_source"),
            "progress_anchor_recommended": result.get("progress_anchor_recommended"),
            "resume_artifacts": result.get("resume_artifacts"),
            "workflow_bundle_bootstrap": result.get("workflow_bundle_bootstrap"),
            "micro_practice_names": result.get("micro_practice_names"),
            "auto_run_profile": {
                "auto_mode_enabled": bool((result.get("auto_run_profile") or {}).get("enabled")),
                "trigger": str((result.get("auto_run_profile") or {}).get("trigger", "none")),
                "requested_phase": str((result.get("auto_run_profile") or {}).get("requested_phase", "manual")),
                "execution_mode": str((result.get("auto_run_profile") or {}).get("execution_mode", "manual")),
                "run_style": str((result.get("auto_run_profile") or {}).get("run_style", "foreground")),
                "safety_level": str((result.get("auto_run_profile") or {}).get("safety_level", "standard")),
                "resume_requested": bool((result.get("auto_run_profile") or {}).get("resume_requested")),
                "detached_ready": bool((result.get("auto_run_profile") or {}).get("detached_ready")),
                "workflow_bundle": str((result.get("auto_run_profile") or {}).get("workflow_bundle", result.get("workflow_bundle", ""))),
                "workflow_supported": bool((result.get("auto_run_profile") or {}).get("workflow_supported")),
                "eligible_workflows": (result.get("auto_run_profile") or {}).get("eligible_workflows", []),
                "requires_explicit_go": bool((result.get("auto_run_profile") or {}).get("requires_explicit_go", False)),
                "setup_command": str((result.get("auto_run_profile") or {}).get("setup_command", "")),
                "go_command": str((result.get("auto_run_profile") or {}).get("go_command", "")),
                "plan_json": str((result.get("auto_run_profile") or {}).get("plan_json", "")),
                "plan_exists": False,
                "resume_anchor": str((result.get("auto_run_profile") or {}).get("resume_anchor", "")),
                "state_dir": str((result.get("auto_run_profile") or {}).get("state_dir", "")),
                "automation_state_schema": str((result.get("auto_run_profile") or {}).get("automation_state_schema", "")),
                "safety_guards": (result.get("auto_run_profile") or {}).get("safety_guards", []),
                "eligibility_reason": str((result.get("auto_run_profile") or {}).get("eligibility_reason", "")),
            },
        },
    }
    response_contract.validate_verify_action_result(output)
    return output


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify whether a planned virtual team action matches the router contract.")
    parser.add_argument("--self-test", action="store_true", help="Run self-test for all v5.9.0 checks.")
    parser.add_argument("--text", help="User request text.")
    parser.add_argument(
        "--check",
        choices=[
            "process-skill",
            "git-workflow",
            "worktree",
            "lead-assignment",
            "release-gate",
            "iteration",
            "workflow-bundle",
            "bundle-bootstrap",
            "assistant-delta-contract",
            "auto-mode",
            "micro-practice-ledger",
            "completion-evidence",
            "file-handoff",
            "spec-violation",
            "lead-prejudgment",
            "yagni",
            "breaker-status",
            "contract-lock",
            "observability-schema",
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
    parser.add_argument(
        "--completion-evidence",
        help="Path to completion evidence JSON for check=completion-evidence.",
    )
    parser.add_argument(
        "--handoff-dir",
        help="Handoff directory for check=file-handoff. Defaults to .vidt/handoff.",
    )
    parser.add_argument(
        "--handoff-type",
        help="Filter handoff artifacts by type for check=file-handoff.",
    )
    parser.add_argument(
        "--worker-output",
        help="Worker output file path for check=spec-violation.",
    )
    parser.add_argument(
        "--dispatch-text",
        help="Lead dispatch text for check=lead-prejudgment.",
    )
    parser.add_argument(
        "--diff-file",
        help="Diff file path for check=yagni.",
    )
    parser.add_argument(
        "--breaker-layer",
        help="Circuit breaker layer name for check=breaker-status (e.g. routing, verifier, delivery).",
    )
    parser.add_argument("--breaker-config", help="Circuit breaker config path for check=breaker-status.")
    parser.add_argument("--breaker-state-file", help="Circuit breaker state path for check=breaker-status.")
    parser.add_argument("--breaker-escalation-sink", help="Circuit breaker escalation sink for check=breaker-status.")
    parser.add_argument(
        "--contract-spec",
        help="Contract-spec file path for check=contract-lock.",
    )
    parser.add_argument(
        "--iteration-workspace",
        help="Iteration workspace for check=iteration. Defaults to <repo>/.vidt/iterations.",
    )
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    return parser.parse_args()


def self_test() -> int:
    """自测:验证 v5.9.0 新增 check 能正常执行并返回预期结构"""
    config = load_config(DEFAULT_CONFIG_PATH)
    repo_path = Path(".").resolve()
    test_text = "self-test probe"
    failures: list[str] = []

    checks: list[tuple[str, str, bool, str]] = [
        ("file-handoff", "目录不存在时 allowed 应为 false", False, "allowed"),
        ("completion-evidence", "evidence 不存在时 allowed 应为 false", False, "allowed"),
        ("lead-prejudgment", "空 dispatch 时 allowed 应为 true", True, "allowed"),
        ("yagni", "无 diff 时 allowed 应为 true", True, "allowed"),
        ("spec-violation", "无 worker output 时 allowed 应为 true", True, "allowed"),
        ("contract-lock", "无 contract-spec 时 allowed 应为 true(跳过)", True, "allowed"),
    ]

    for check_name, description, expected_allowed, field_name in checks:
        try:
            result = verify_action(
                text=test_text,
                config=config,
                repo_path=repo_path,
                check=check_name,
            )
            actual_allowed = bool(result.get("allowed"))
            if actual_allowed != expected_allowed:
                failures.append(
                    f"FAIL: {check_name} — {description}, expected {field_name}={expected_allowed}, got {actual_allowed}"
                )
        except Exception as exc:
            failures.append(f"FAIL: {check_name} — raised exception: {exc}")

    try:
        result = verify_action(
            text=test_text,
            config=config,
            repo_path=repo_path,
            check="breaker-status",
            breaker_layer="verifier",
        )
        breaker_state = str(result.get("details", {}).get("breaker_state", ""))
        if breaker_state != "closed":
            failures.append(f"FAIL: breaker-status — expected breaker_state=closed, got {breaker_state}")
    except Exception as exc:
        failures.append(f"FAIL: breaker-status — raised exception: {exc}")

    try:
        result = verify_action(
            text=test_text,
            config=config,
            repo_path=repo_path,
            check="contract-lock",
            contract_spec=Path("/nonexistent/contract-spec.json"),
        )
        actual_allowed = bool(result.get("allowed"))
        if actual_allowed:
            failures.append("FAIL: contract-lock — 文件不存在时 allowed 应为 false")
    except Exception as exc:
        failures.append(f"FAIL: contract-lock — raised exception: {exc}")

    try:
        result = verify_action(
            text=test_text,
            config=config,
            repo_path=SKILL_DIR,
            check="observability-schema",
        )
        actual_allowed = bool(result.get("allowed"))
        if not actual_allowed:
            failures.append(
                f"FAIL: observability-schema — expected allowed=true, got false: "
                f"{result.get('summary', '')}"
            )
    except Exception as exc:
        failures.append(f"FAIL: observability-schema — raised exception: {exc}")

    if failures:
        for f in failures:
            print(f"  {f}")
        print(f"\nSelf-test FAILED ({len(failures)} assertion(s))")
        return 1

    print("Self-test PASSED: all checks return expected structure")
    print("  - file-handoff: rejects when handoff dir missing")
    print("  - completion-evidence: rejects when evidence file missing")
    print("  - lead-prejudgment: allows empty dispatch")
    print("  - yagni: allows empty diff")
    print("  - spec-violation: allows empty worker output")
    print("  - breaker-status: returns closed state for verifier layer")
    print("  - contract-lock: allows when no spec provided, rejects when spec missing")
    print("  - observability-schema: validates telemetry + health report + protocol reference")
    return 0


def main() -> None:
    args = parse_args()

    if args.self_test:
        raise SystemExit(self_test())

    if not args.text or not args.check:
        raise SystemExit("--text and --check are required (use --self-test for self-test)")

    try:
        result = verify_action(
            text=args.text,
            config=load_config(Path(args.config).resolve()),
            repo_path=Path(args.repo).resolve(),
            check=args.check,
            process_skill=args.process_skill,
            lead_agent=args.lead_agent,
            assistant_agents=list(args.assistant_agent),
            completion_evidence=Path(args.completion_evidence) if args.completion_evidence else None,
            handoff_dir=Path(args.handoff_dir) if args.handoff_dir else None,
            handoff_type=args.handoff_type,
            worker_output=Path(args.worker_output) if args.worker_output else None,
            dispatch_text=args.dispatch_text,
            diff_file=Path(args.diff_file) if args.diff_file else None,
            breaker_layer=args.breaker_layer,
            breaker_config=Path(args.breaker_config) if args.breaker_config else None,
            breaker_state_file=Path(args.breaker_state_file) if args.breaker_state_file else None,
            breaker_escalation_sink=Path(args.breaker_escalation_sink) if args.breaker_escalation_sink else None,
            contract_spec=Path(args.contract_spec) if args.contract_spec else None,
            iteration_workspace=Path(args.iteration_workspace) if args.iteration_workspace else None,
        )
        exit_code = 0 if bool(result.get("ok")) and bool(result.get("allowed")) else 1
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
