#!/usr/bin/env python3
"""Mechanical contract checks for virtual-intelligent-dev-team."""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import tempfile
from pathlib import Path
from unittest import mock


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
ROUTE_SCRIPT = SCRIPT_DIR / "route_request.py"
RESPONSE_PACK_SCRIPT = SCRIPT_DIR / "generate_response_pack.py"
RESPONSE_CONTRACT_SCRIPT = SCRIPT_DIR / "response_contract.py"
VERIFY_ACTION_SCRIPT = SCRIPT_DIR / "verify_action.py"
RELEASE_GATE_SCRIPT = SCRIPT_DIR / "run_release_gate.py"
CONFIG_PATH = SKILL_DIR / "references" / "routing-rules.json"
VERSION_PATH = SKILL_DIR / "VERSION"
BENCHMARK_EVALS_PATH = SKILL_DIR / "evals" / "evals.json"
SIDECAR_SCHEMA_PATH = SKILL_DIR / "references" / "response-pack-sidecar-schema.md"
SIDECAR_SCHEMA_JSON_PATH = SKILL_DIR / "references" / "response-pack-sidecar.schema.json"
VERIFY_ACTION_SCHEMA_JSON_PATH = SKILL_DIR / "references" / "verify-action-result.schema.json"
RELEASE_GATE_SCHEMA_JSON_PATH = SKILL_DIR / "references" / "release-gate-result.schema.json"
BETA_ROUND_REPORT_SCHEMA_JSON_PATH = SKILL_DIR / "references" / "beta-round-report.schema.json"
BETA_ROUND_GATE_RESULT_SCHEMA_JSON_PATH = SKILL_DIR / "references" / "beta-round-gate-result.schema.json"
BETA_SIMULATION_DIFF_SCHEMA_JSON_PATH = SKILL_DIR / "references" / "beta-simulation-diff.schema.json"
BETA_RAMP_PLAN_SCHEMA_JSON_PATH = SKILL_DIR / "references" / "beta-ramp-plan.schema.json"
SIMULATED_USER_PROFILE_SCHEMA_JSON_PATH = SKILL_DIR / "references" / "simulated-user-profile.schema.json"
BETA_SIMULATION_CONFIG_SCHEMA_JSON_PATH = SKILL_DIR / "references" / "beta-simulation-config.schema.json"
BETA_SIMULATION_EVENT_SCHEMA_JSON_PATH = SKILL_DIR / "references" / "beta-simulation-event.schema.json"
BETA_SIMULATION_RUN_SCHEMA_JSON_PATH = SKILL_DIR / "references" / "beta-simulation-run.schema.json"
BENCHMARK_EVALS_SCHEMA_JSON_PATH = SKILL_DIR / "references" / "benchmark-evals.schema.json"
BENCHMARK_RUN_RESULT_SCHEMA_JSON_PATH = SKILL_DIR / "references" / "benchmark-run-result.schema.json"
MARKDOWN_PATH_RE = re.compile(r"(?<![\w./-])((?:assets|references|scripts)/[A-Za-z0-9_./-]+\.(?:md|json|py))(?![\w./-])")
BARE_REFERENCE_RE = re.compile(r"^\s*-\s+`([A-Za-z0-9_.-]+\.(?:md|json))`\s*$")
SCRIPT_COMMAND_RE = re.compile(r"python\s+(scripts/[A-Za-z0-9_.-]+\.py)\b")
SCHEMA_VERSION_RE = re.compile(r"版本：`([^`]+)`")


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_json(path: Path) -> dict[str, object]:
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, dict):
        raise RuntimeError(f"{path} must contain a JSON object")
    return data


def _check(condition: bool, errors: list[str], message: str) -> None:
    if not condition:
        errors.append(message)


def _resolve_markdown_path(raw_path: str, source_path: Path, skill_dir: Path) -> Path:
    if raw_path.startswith(("assets/", "references/", "scripts/")):
        return (skill_dir / raw_path).resolve()
    return (source_path.parent / raw_path).resolve()


def _collect_markdown_references(source_path: Path) -> list[str]:
    text = source_path.read_text(encoding="utf-8")
    refs = set(MARKDOWN_PATH_RE.findall(text))
    if source_path.name == "runtime-routing-index.md":
        for line in text.splitlines():
            match = BARE_REFERENCE_RE.match(line)
            if match:
                refs.add(match.group(1))
    return sorted(refs)


def lint_contract(skill_dir: Path | None = None) -> dict[str, object]:
    resolved_skill_dir = skill_dir.resolve() if skill_dir is not None else SKILL_DIR
    config_path = resolved_skill_dir / "references" / "routing-rules.json"
    version_path = resolved_skill_dir / "VERSION"
    response_pack_script = resolved_skill_dir / "scripts" / "generate_response_pack.py"
    response_contract_script = resolved_skill_dir / "scripts" / "response_contract.py"
    verify_action_script = resolved_skill_dir / "scripts" / "verify_action.py"
    release_gate_script = resolved_skill_dir / "scripts" / "run_release_gate.py"
    benchmark_evals_path = resolved_skill_dir / "evals" / "evals.json"
    sidecar_schema_path = resolved_skill_dir / "references" / "response-pack-sidecar-schema.md"
    sidecar_schema_json_path = resolved_skill_dir / "references" / "response-pack-sidecar.schema.json"
    verify_action_schema_json_path = resolved_skill_dir / "references" / "verify-action-result.schema.json"
    release_gate_schema_json_path = resolved_skill_dir / "references" / "release-gate-result.schema.json"
    beta_round_report_schema_json_path = resolved_skill_dir / "references" / "beta-round-report.schema.json"
    beta_round_gate_result_schema_json_path = resolved_skill_dir / "references" / "beta-round-gate-result.schema.json"
    beta_simulation_diff_schema_json_path = resolved_skill_dir / "references" / "beta-simulation-diff.schema.json"
    beta_ramp_plan_schema_json_path = resolved_skill_dir / "references" / "beta-ramp-plan.schema.json"
    simulated_user_profile_schema_json_path = resolved_skill_dir / "references" / "simulated-user-profile.schema.json"
    beta_simulation_config_schema_json_path = resolved_skill_dir / "references" / "beta-simulation-config.schema.json"
    beta_simulation_event_schema_json_path = resolved_skill_dir / "references" / "beta-simulation-event.schema.json"
    beta_simulation_run_schema_json_path = resolved_skill_dir / "references" / "beta-simulation-run.schema.json"
    benchmark_evals_schema_json_path = resolved_skill_dir / "references" / "benchmark-evals.schema.json"
    benchmark_run_result_schema_json_path = resolved_skill_dir / "references" / "benchmark-run-result.schema.json"
    route_script = resolved_skill_dir / "scripts" / "route_request.py"
    index_paths = [
        resolved_skill_dir / "references" / "tooling-command-index.md",
        resolved_skill_dir / "references" / "runtime-routing-index.md",
    ]
    local_route_request = load_module(
        f"virtual_team_contract_lint_route_request_{resolved_skill_dir.name}",
        route_script,
    )
    local_response_pack = (
        load_module(
            f"virtual_team_contract_lint_response_pack_{resolved_skill_dir.name}",
            response_pack_script,
        )
        if response_pack_script.exists()
        else None
    )
    local_response_contract = (
        load_module(
            f"virtual_team_contract_lint_response_contract_{resolved_skill_dir.name}",
            response_contract_script,
        )
        if response_contract_script.exists()
        else None
    )
    local_verify_action = (
        load_module(
            f"virtual_team_contract_lint_verify_action_{resolved_skill_dir.name}",
            verify_action_script,
        )
        if verify_action_script.exists()
        else None
    )
    local_release_gate = (
        load_module(
            f"virtual_team_contract_lint_release_gate_{resolved_skill_dir.name}",
            release_gate_script,
        )
        if release_gate_script.exists()
        else None
    )
    config = load_json(config_path)
    errors: list[str] = []
    checks: list[dict[str, object]] = []

    version = version_path.read_text(encoding="utf-8").strip()
    config_version = str(config.get("meta", {}).get("version", "")).strip()
    _check(
        version == config_version,
        errors,
        f"VERSION mismatch: `{version}` != routing-rules meta.version `{config_version}`. Fix both files together before release.",
    )
    checks.append({"name": "version-sync", "passed": version == config_version})

    _check(
        response_pack_script.exists(),
        errors,
        "Missing scripts/generate_response_pack.py. Restore the response-pack generator before release.",
    )
    _check(
        response_contract_script.exists(),
        errors,
        "Missing scripts/response_contract.py. Restore the shared response contract helper before release.",
    )
    _check(
        sidecar_schema_path.exists(),
        errors,
        "Missing references/response-pack-sidecar-schema.md. Restore the sidecar schema document before release.",
    )
    _check(
        sidecar_schema_json_path.exists(),
        errors,
        "Missing references/response-pack-sidecar.schema.json. Restore the executable sidecar schema before release.",
    )
    _check(
        verify_action_schema_json_path.exists(),
        errors,
        "Missing references/verify-action-result.schema.json. Restore the verify_action executable schema before release.",
    )
    _check(
        release_gate_schema_json_path.exists(),
        errors,
        "Missing references/release-gate-result.schema.json. Restore the release_gate executable schema before release.",
    )
    _check(
        beta_round_report_schema_json_path.exists(),
        errors,
        "Missing references/beta-round-report.schema.json. Restore the beta round report schema before release.",
    )
    _check(
        beta_round_gate_result_schema_json_path.exists(),
        errors,
        "Missing references/beta-round-gate-result.schema.json. Restore the beta round gate result schema before release.",
    )
    _check(
        beta_simulation_diff_schema_json_path.exists(),
        errors,
        "Missing references/beta-simulation-diff.schema.json. Restore the beta simulation diff schema before release.",
    )
    _check(
        beta_ramp_plan_schema_json_path.exists(),
        errors,
        "Missing references/beta-ramp-plan.schema.json. Restore the beta ramp plan schema before release.",
    )
    _check(
        simulated_user_profile_schema_json_path.exists(),
        errors,
        "Missing references/simulated-user-profile.schema.json. Restore the simulated user profile schema before release.",
    )
    _check(
        beta_simulation_config_schema_json_path.exists(),
        errors,
        "Missing references/beta-simulation-config.schema.json. Restore the beta simulation config schema before release.",
    )
    _check(
        beta_simulation_event_schema_json_path.exists(),
        errors,
        "Missing references/beta-simulation-event.schema.json. Restore the beta simulation event schema before release.",
    )
    _check(
        beta_simulation_run_schema_json_path.exists(),
        errors,
        "Missing references/beta-simulation-run.schema.json. Restore the beta simulation run schema before release.",
    )
    _check(
        benchmark_evals_path.exists(),
        errors,
        "Missing evals/evals.json. Restore the benchmark eval catalog before release.",
    )
    _check(
        benchmark_evals_schema_json_path.exists(),
        errors,
        "Missing references/benchmark-evals.schema.json. Restore the benchmark eval executable schema before release.",
    )
    _check(
        benchmark_run_result_schema_json_path.exists(),
        errors,
        "Missing references/benchmark-run-result.schema.json. Restore the benchmark result executable schema before release.",
    )
    checks.append(
        {
            "name": "response-contract-schema-files",
            "passed": (
                response_pack_script.exists()
                and response_contract_script.exists()
                and verify_action_script.exists()
                and release_gate_script.exists()
                and sidecar_schema_path.exists()
                and sidecar_schema_json_path.exists()
                and verify_action_schema_json_path.exists()
                and release_gate_schema_json_path.exists()
                and beta_round_report_schema_json_path.exists()
                and beta_round_gate_result_schema_json_path.exists()
                and beta_simulation_diff_schema_json_path.exists()
                and beta_ramp_plan_schema_json_path.exists()
                and simulated_user_profile_schema_json_path.exists()
                and beta_simulation_config_schema_json_path.exists()
                and beta_simulation_event_schema_json_path.exists()
                and beta_simulation_run_schema_json_path.exists()
                and benchmark_evals_path.exists()
                and benchmark_evals_schema_json_path.exists()
                and benchmark_run_result_schema_json_path.exists()
            ),
        }
    )

    schema_constant = getattr(local_response_contract, "SIDECAR_SCHEMA_VERSION", "")
    _check(
        isinstance(schema_constant, str) and schema_constant.strip() != "",
        errors,
        "response_contract.py must expose a non-empty SIDECAR_SCHEMA_VERSION constant.",
    )

    schema_doc_version = ""
    if sidecar_schema_path.exists():
        schema_doc_text = sidecar_schema_path.read_text(encoding="utf-8")
        match = SCHEMA_VERSION_RE.search(schema_doc_text)
        schema_doc_version = match.group(1).strip() if match else ""
        _check(
            schema_doc_version != "",
            errors,
            "response-pack-sidecar-schema.md must declare its schema version in the `版本：` header.",
        )
        if isinstance(schema_constant, str) and schema_constant.strip():
            _check(
                schema_doc_version == schema_constant,
                errors,
                f"Sidecar schema version mismatch: schema doc `{schema_doc_version}` != response_contract `{schema_constant}`.",
            )

    build_payload = getattr(local_response_pack, "build_response_pack_payload", None)
    _check(
        callable(build_payload),
        errors,
        "generate_response_pack.py must expose build_response_pack_payload for machine-readable response packs.",
    )
    payload: dict[str, object] = {}
    if callable(build_payload):
        payload = build_payload({})
        _check(
            payload.get("schema_version") == schema_constant,
            errors,
            "build_response_pack_payload must expose schema_version that matches response_contract.SIDECAR_SCHEMA_VERSION.",
        )
        required_sections = {
            "team_dispatch",
            "execution_result",
            "evidence",
            "next_action",
            "resume",
            "git_workflow",
            "governance",
        }
        missing_sections = sorted(section for section in required_sections if section not in payload)
        _check(
            len(missing_sections) == 0,
            errors,
            f"build_response_pack_payload is missing required top-level sections: {missing_sections}.",
        )
        if hasattr(local_response_contract, "validate_response_pack_payload"):
            sample_payloads = {
                "default": payload,
                "planning": build_payload({"needs_pre_development_planning": True}),
                "release": build_payload({"needs_release_gate": True}),
                "iteration": build_payload(
                    {
                        "needs_iteration": True,
                        "iteration_profile": {
                            "round_cap_online": 3,
                            "round_cap_offline": 120,
                            "allowed_decisions": ["keep", "retry", "rollback", "stop"],
                        },
                        "progress_anchor_recommended": ".skill-iterations/current-round-memory.md",
                    }
                ),
                "beta": build_payload(
                    {
                        "workflow_bundle": "beta-feedback-ramp",
                        "request_language": "zh",
                        "lead_agent": "World-Class Product Architect",
                        "beta_validation_plan": {
                            "enabled": True,
                            "simulation_allowed": True,
                            "feedback_anchor": ".skill-beta/feedback-ledger.md",
                            "cohort_artifact": ".skill-beta/cohort-matrix.md",
                            "ramp_plan_template": "assets/beta-ramp-plan-template.json",
                            "ramp_plan_schema": "references/beta-ramp-plan.schema.json",
                            "ramp_plan_path": ".skill-beta/ramp-plan.json",
                            "simulation_profile_template": "assets/simulated-user-profile-template.json",
                            "simulation_profile_dir": ".skill-beta/personas",
                            "simulation_persona_library": "references/simulation-persona-library.json",
                            "simulation_cohort_fixtures": "references/simulation-cohort-fixtures.json",
                            "simulation_config_template": "assets/beta-simulation-config-template.json",
                            "simulation_config_dir": ".skill-beta/simulation-configs",
                            "simulation_scenario_packs": "references/simulation-scenario-packs.json",
                            "simulation_trace_catalog": "references/simulation-trace-catalog.json",
                            "simulation_preview_dir": ".skill-beta/fixture-previews",
                            "simulation_diff_dir": ".skill-beta/fixture-diffs",
                            "simulation_run_dir": ".skill-beta/simulation-runs",
                            "simulation_init_command_template": "python scripts/init_beta_simulation.py --root . --round-id <round-id> --phase \"<phase>\" --objective \"<objective>\" --pretty",
                            "simulation_preview_command_template": "python scripts/preview_beta_simulation_fixture.py --config .skill-beta/simulation-configs/<round-id>.json --pretty",
                            "simulation_diff_command_template": "python scripts/compare_beta_simulation_manifests.py --previous .skill-beta/fixture-previews/<previous-round-id>/beta-simulation-manifest.json --current .skill-beta/fixture-previews/<round-id>/beta-simulation-manifest.json --pretty",
                            "simulation_run_command_template": "python scripts/run_beta_simulation.py --config .skill-beta/simulation-configs/<round-id>.json --pretty",
                            "simulation_summary_command_template": "python scripts/summarize_beta_simulation.py --run .skill-beta/simulation-runs/<round-id>/beta-simulation-run.json --feedback-ledger-out .skill-beta/feedback-ledger.md --round-report-out .skill-beta/reports/<round-id>.json --pretty",
                            "report_template": "assets/beta-round-report-template.json",
                            "report_dir": ".skill-beta/reports",
                            "decision_dir": ".skill-beta/round-decisions",
                            "gate_command_template": "python scripts/evaluate_beta_round.py --report .skill-beta/reports/<round-id>.json --pretty",
                            "rounds": [
                                {
                                    "round_id": "round-0",
                                    "phase": "pre-build concept smoke",
                                    "sample_size": 5,
                                    "participant_mode": "simulated target users",
                                    "archetypes": ["first-time novice"],
                                    "goal": "validate the promise",
                                    "exit_criteria": "coherent flow"
                                }
                            ],
                        },
                    }
                ),
            }
            schema_validation_failures: list[str] = []
            for sample_name, sample_payload in sample_payloads.items():
                try:
                    local_response_contract.validate_response_pack_payload(sample_payload)
                except Exception as exc:
                    schema_validation_failures.append(f"{sample_name}: {exc}")
            _check(
                len(schema_validation_failures) == 0,
                errors,
                "response-pack sidecar schema validation failed for sample payloads: "
                + "; ".join(schema_validation_failures),
            )
        else:
            schema_validation_failures = ["response_contract.validate_response_pack_payload missing"]
        checks.append(
            {
                "name": "response-pack-sidecar-contract",
                "passed": (
                    len(missing_sections) == 0
                    and payload.get("schema_version") == schema_constant
                    and len(schema_validation_failures) == 0
                ),
                "details": {
                    "schema_version": payload.get("schema_version"),
                    "required_sections": sorted(required_sections),
                    "schema_json": str(sidecar_schema_json_path),
                },
            }
        )
    else:
        checks.append({"name": "response-pack-sidecar-contract", "passed": False})

    verify_action_failures: list[str] = []
    if (
        local_verify_action is not None
        and local_response_contract is not None
        and hasattr(local_response_contract, "validate_verify_action_result")
    ):
        verify_config = local_verify_action.load_config(config_path)
        verify_samples = [
            {
                "check": "process-skill",
                "text": "Rewrite this project in Rust, but plan before coding and keep a progress tracker for later sessions.",
                "kwargs": {"process_skill": "pre-development-planning"},
            },
            {
                "check": "git-workflow",
                "text": "Refactor this Flask service and then commit and push the branch.",
                "kwargs": {},
            },
            {
                "check": "worktree",
                "text": "Use FastAPI for a backend service, then commit, push, and isolate the work in a worktree.",
                "kwargs": {},
            },
            {
                "check": "lead-assignment",
                "text": "Review this Django API for security issues.",
                "kwargs": {"lead_agent": "Technical Trinity", "assistant_agents": []},
            },
            {
                "check": "release-gate",
                "text": "Is this version ready to ship? Do not answer from benchmark alone. Run the formal release gate.",
                "kwargs": {},
            },
            {
                "check": "iteration",
                "text": "Run another iteration, benchmark it against the baseline, and stop if the result regresses.",
                "kwargs": {},
            },
            {
                "check": "workflow-bundle",
                "text": "Rewrite this project in Rust, but plan before coding and keep a progress tracker for later sessions.",
                "kwargs": {},
            },
            {
                "check": "bundle-bootstrap",
                "text": "Define the onboarding user flow, acceptance criteria, and backend contract for this signup revamp.",
                "kwargs": {},
            },
            {
                "check": "assistant-delta-contract",
                "text": "Define the onboarding user flow, acceptance criteria, and backend contract for this signup revamp.",
                "kwargs": {},
            },
        ]
        for sample in verify_samples:
            try:
                local_verify_action.verify_action(
                    text=sample["text"],
                    config=verify_config,
                    repo_path=resolved_skill_dir.parent,
                    check=sample["check"],
                    **sample["kwargs"],
                )
            except Exception as exc:
                verify_action_failures.append(f"{sample['check']}: {exc}")
    else:
        verify_action_failures.append("verify_action schema validator missing")
    _check(
        len(verify_action_failures) == 0,
        errors,
        "verify_action schema validation failed for sample results: "
        + "; ".join(verify_action_failures),
    )
    checks.append(
        {
            "name": "verify-action-contract",
            "passed": len(verify_action_failures) == 0,
            "details": {"schema_json": str(verify_action_schema_json_path)},
        }
    )

    release_gate_failures: list[str] = []
    if (
        local_release_gate is not None
        and local_response_contract is not None
        and hasattr(local_response_contract, "validate_release_gate_result")
    ):
        release_gate_samples = [
            (
                "hold",
                {
                    "tests_passed": True,
                    "validator_passed": True,
                    "evals_passed": True,
                    "offline_drill_enabled": True,
                    "offline_drill_passed": False,
                    "overall_passed": False,
                },
            ),
            (
                "ship",
                {
                    "tests_passed": True,
                    "validator_passed": True,
                    "evals_passed": True,
                    "offline_drill_enabled": True,
                    "offline_drill_passed": True,
                    "overall_passed": True,
                },
            ),
        ]
        for sample_name, summary in release_gate_samples:
            try:
                with tempfile.TemporaryDirectory() as tmp:
                    output_dir = Path(tmp) / sample_name
                    benchmark_output = output_dir / "benchmark-results.json"
                    benchmark_report = output_dir / "benchmark-report.md"
                    with mock.patch.object(
                        local_release_gate.benchmark_runner,
                        "run_benchmark_suite",
                        return_value={
                            "summary": summary,
                            "json_report": str(benchmark_output),
                            "markdown_report": str(benchmark_report),
                            "offline_drill_run": {
                                "markdown_report": str(output_dir / "offline-loop-drill-report.md"),
                            },
                        },
                    ):
                        local_release_gate.run_release_gate(output_dir=output_dir)
            except Exception as exc:
                release_gate_failures.append(f"{sample_name}: {exc}")
    else:
        release_gate_failures.append("release_gate schema validator missing")
    _check(
        len(release_gate_failures) == 0,
        errors,
        "release_gate schema validation failed for sample results: "
        + "; ".join(release_gate_failures),
    )
    checks.append(
        {
            "name": "release-gate-contract",
            "passed": len(release_gate_failures) == 0,
            "details": {"schema_json": str(release_gate_schema_json_path)},
        }
    )

    beta_round_contract_failures: list[str] = []
    if local_response_contract is not None:
        sample_report = {
            "schema_version": "beta-round-report/v1",
            "round_id": "round-1",
            "phase": "closed beta",
            "goal": "validate the implemented slice",
            "participant_mode": "seed users",
            "planned_sample_size": 12,
            "completed_sessions": 10,
            "task_success_count": 9,
            "blocker_issue_count": 0,
            "critical_issue_count": 0,
            "high_severity_issue_count": 1,
            "top_feedback_themes": ["copy clarity"],
            "exit_criteria": "no blocker-level failures remain",
            "gate_thresholds": {
                "min_completed_sessions": 8,
                "min_success_rate": 0.8,
                "max_blocker_issue_count": 0,
                "max_critical_issue_count": 0,
            },
            "evidence_artifacts": {
                "simulation_run_json": ".skill-beta/simulation-runs/round-1/beta-simulation-run.json",
                "simulation_run_markdown": ".skill-beta/simulation-runs/round-1/beta-simulation-run.md",
                "simulation_summary_json": ".skill-beta/simulation-runs/round-1/beta-simulation-summary.json",
                "feedback_ledger_markdown": ".skill-beta/feedback-ledger.md",
                "fixture_manifest_json": ".skill-beta/fixture-previews/round-1/beta-simulation-manifest.json",
                "fixture_manifest_markdown": ".skill-beta/fixture-previews/round-1/beta-simulation-manifest.md",
                "fixture_diff_json": ".skill-beta/fixture-diffs/round-0-to-round-1/beta-simulation-diff.json",
                "fixture_diff_markdown": ".skill-beta/fixture-diffs/round-0-to-round-1/beta-simulation-diff.md",
                "ramp_plan_json": ".skill-beta/ramp-plan.json",
            },
            "notes": "",
        }
        sample_gate = {
            "generated_at": "2026-04-08T12:00:00Z",
            "skill_name": "virtual-intelligent-dev-team",
            "ok": True,
            "decision": "advance",
            "reason": "sample report clears thresholds",
            "round_id": "round-1",
            "report_path": ".skill-beta/reports/round-1.json",
            "observed": {
                "planned_sample_size": 12,
                "completed_sessions": 10,
                "success_rate": 0.9,
                "blocker_issue_count": 0,
                "critical_issue_count": 0,
                "high_severity_issue_count": 1,
                "top_feedback_themes": ["copy clarity"],
            },
            "thresholds": {
                "min_completed_sessions": 8,
                "min_success_rate": 0.8,
                "max_blocker_issue_count": 0,
                "max_critical_issue_count": 0,
            },
            "follow_up": {
                "next_action": "promote learnings",
                "continue_beta": True,
                "release_governance_recommended": False,
                "next_round_recommended": "round-2",
            },
            "ramp_gate": {
                "status": "passed",
                "required_for_round": True,
                "reason": "Ramp plan matches the current round report.",
                "ramp_plan_json": ".skill-beta/ramp-plan.json",
                "expected_sample_size": 12,
                "observed_planned_sample_size": 12,
                "expected_participant_mode": "seed users",
                "observed_participant_mode": "seed users",
                "expected_phase": "closed beta",
                "observed_phase": "closed beta",
                "expected_archetypes": ["first-time novice", "daily operator"],
                "observed_persona_ids": ["daily-operator", "edge-case-breaker"],
            },
            "diff_gate": {
                "status": "passed",
                "required_for_round": True,
                "review_required": False,
                "expansion_ok": True,
                "reason": "Fixture diff cleared expansion review.",
                "fixture_diff_json": ".skill-beta/fixture-diffs/round-0-to-round-1/beta-simulation-diff.json",
                "fixture_diff_markdown": ".skill-beta/fixture-diffs/round-0-to-round-1/beta-simulation-diff.md",
                "coverage_shift_summary": {
                    "previous_persona_count": 1,
                    "current_persona_count": 2,
                    "previous_scenario_count": 1,
                    "current_scenario_count": 1,
                    "previous_trace_count": 1,
                    "current_trace_count": 1,
                    "new_session_matrix_count": 1,
                    "expansion_mode": "expanded",
                },
                "risk_notes": ["Coverage expanded while preserving the previous baseline."],
            },
            "json_report": ".skill-beta/round-decisions/round-1/beta-round-gate-result.json",
            "markdown_report": ".skill-beta/round-decisions/round-1/beta-round-gate-report.md",
        }
        try:
            local_response_contract.validate_beta_round_report(sample_report)
        except Exception as exc:
            beta_round_contract_failures.append(f"report: {exc}")
        try:
            local_response_contract.validate_beta_round_gate_result(sample_gate)
        except Exception as exc:
            beta_round_contract_failures.append(f"gate: {exc}")
        sample_profile = {
            "schema_version": "simulated-user-profile/v1",
            "profile_id": "first-time-novice",
            "display_name": "First-Time Novice",
            "archetype": "first-time novice",
            "primary_goal": "Understand the core promise quickly.",
            "tool_literacy": "low",
            "domain_familiarity": "low",
            "risk_tolerance": "low",
            "workflow_preference": "step-by-step clarity",
            "failure_sensitivity": "high",
            "feedback_style": "balanced",
            "preferred_tasks": ["first-run journey"],
            "notes": "surface ambiguity early",
        }
        sample_event = {
            "step_index": 1,
            "event_type": "entry",
            "actor_id": "first-time-novice",
            "scenario_id": "scenario-1",
            "action": "start scenario",
            "outcome": "neutral",
            "severity": "info",
            "observation": "The simulated user starts the scenario.",
        }
        sample_simulation_config = {
            "schema_version": "beta-simulation-config/v1",
            "skill_name": "virtual-intelligent-dev-team",
            "round_id": "round-0",
            "phase": "pre-build concept smoke",
            "objective": "validate the promise",
            "persona_dir": ".skill-beta/personas",
            "run_output_dir": ".skill-beta/simulation-runs/round-0",
            "feedback_ledger_out": ".skill-beta/feedback-ledger.md",
            "round_report_out": ".skill-beta/reports/round-0.json",
            "summary_command_template": "python scripts/summarize_beta_simulation.py --run .skill-beta/simulation-runs/<round-id>/beta-simulation-run.json --feedback-ledger-out .skill-beta/feedback-ledger.md --round-report-out .skill-beta/reports/<round-id>.json --pretty",
            "cohort_fixture_source": "references/simulation-cohort-fixtures.json",
            "trace_catalog_source": "references/simulation-trace-catalog.json",
            "scenarios": [
                {
                    "scenario_id": "scenario-1",
                    "title": "first meaningful task",
                    "primary_task": "finish the primary happy-path task",
                    "success_definition": "the user completes the task and understands the value",
                    "risk_focus": "onboarding clarity",
                }
            ],
            "session_plan": [
                {
                    "session_id": "session-01",
                    "persona_id": "first-time-novice",
                    "scenario_id": "scenario-1",
                    "trace_id": "novice-cta-hesitation",
                }
            ],
        }
        sample_simulation_run = {
            "schema_version": "beta-simulation-run/v1",
            "generated_at": "2026-04-08T12:00:00Z",
            "skill_name": "virtual-intelligent-dev-team",
            "round_id": "round-0",
            "phase": "pre-build concept smoke",
            "objective": "validate the promise",
            "config_path": ".skill-beta/simulation-configs/round-0.json",
            "cohort_fixture_source": "references/simulation-cohort-fixtures.json",
            "trace_catalog_source": "references/simulation-trace-catalog.json",
            "personas": [
                {
                    "profile_id": "first-time-novice",
                    "display_name": "First-Time Novice",
                    "archetype": "first-time novice",
                }
            ],
            "scenarios": sample_simulation_config["scenarios"],
            "sessions": [
                {
                    "session_id": "session-01",
                    "persona_id": "first-time-novice",
                    "persona_name": "First-Time Novice",
                    "scenario_id": "scenario-1",
                    "scenario_title": "first meaningful task",
                    "trace_id": "novice-cta-hesitation",
                    "trace_label": "Novice CTA hesitation",
                    "status": "completed",
                    "task_completed": True,
                    "blocker_detected": False,
                    "critical_issue_detected": False,
                    "high_severity_issue_detected": False,
                    "top_feedback_themes": ["onboarding clarity"],
                    "feedback_summary": "Task completed with minor friction.",
                    "events": [sample_event],
                }
            ],
            "summary": {
                "planned_sessions": 1,
                "completed_sessions": 1,
                "task_success_count": 1,
                "blocker_issue_count": 0,
                "critical_issue_count": 0,
                "high_severity_issue_count": 0,
                "top_feedback_themes": ["onboarding clarity"],
            },
            "json_report": ".skill-beta/simulation-runs/round-0/beta-simulation-run.json",
            "markdown_report": ".skill-beta/simulation-runs/round-0/beta-simulation-run.md",
        }
        sample_simulation_manifest = {
            "schema_version": "beta-simulation-manifest/v1",
            "generated_at": "2026-04-08T12:00:00Z",
            "skill_name": "virtual-intelligent-dev-team",
            "round_id": "round-0",
            "phase": "pre-build concept smoke",
            "objective": "validate the promise",
            "config_path": ".skill-beta/simulation-configs/round-0.json",
            "cohort_fixture_source": "references/simulation-cohort-fixtures.json",
            "trace_catalog_source": "references/simulation-trace-catalog.json",
            "sessions": [
                {
                    "session_id": "session-01",
                    "persona_id": "first-time-novice",
                    "persona_name": "First-Time Novice",
                    "scenario_id": "scenario-1",
                    "scenario_title": "first meaningful task",
                    "trace_id": "novice-cta-hesitation",
                    "trace_label": "Novice CTA hesitation",
                }
            ],
            "json_report": ".skill-beta/fixture-previews/round-0/beta-simulation-manifest.json",
            "markdown_report": ".skill-beta/fixture-previews/round-0/beta-simulation-manifest.md",
        }
        sample_simulation_diff = {
            "schema_version": "beta-simulation-diff/v1",
            "generated_at": "2026-04-08T12:00:00Z",
            "skill_name": "virtual-intelligent-dev-team",
            "previous_round_id": "round-0",
            "current_round_id": "round-1",
            "previous_manifest_path": ".skill-beta/fixture-previews/round-0/beta-simulation-manifest.json",
            "current_manifest_path": ".skill-beta/fixture-previews/round-1/beta-simulation-manifest.json",
            "previous_session_count": 1,
            "current_session_count": 2,
            "session_count_delta": 1,
            "added_personas": [
                {
                    "persona_id": "edge-case-breaker",
                    "persona_name": "Edge-Case Breaker",
                    "session_count": 1,
                    "session_ids": ["session-02"],
                }
            ],
            "removed_personas": [],
            "added_scenarios": [],
            "removed_scenarios": [],
            "added_traces": [],
            "removed_traces": [],
            "new_session_matrix": [
                {
                    "session_id": "session-02",
                    "persona_id": "edge-case-breaker",
                    "persona_name": "Edge-Case Breaker",
                    "scenario_id": "scenario-1",
                    "scenario_title": "first meaningful task",
                    "trace_id": "novice-cta-hesitation",
                    "trace_label": "Novice CTA hesitation",
                }
            ],
            "coverage_shift_summary": {
                "previous_persona_count": 1,
                "current_persona_count": 2,
                "previous_scenario_count": 1,
                "current_scenario_count": 1,
                "previous_trace_count": 1,
                "current_trace_count": 1,
                "new_session_matrix_count": 1,
                "expansion_mode": "expanded",
            },
            "risk_notes": [
                "Session count expands by 1; review new coverage before execution.",
                "New persona/scenario/trace combinations were introduced (1 sessions); spot-check them before the run.",
            ],
            "expansion_ok": True,
            "review_required": False,
            "json_report": ".skill-beta/fixture-diffs/round-0-to-round-1/beta-simulation-diff.json",
            "markdown_report": ".skill-beta/fixture-diffs/round-0-to-round-1/beta-simulation-diff.md",
        }
        sample_ramp_plan = {
            "schema_version": "beta-ramp-plan/v1",
            "skill_name": "virtual-intelligent-dev-team",
            "rounds": [
                {
                    "round_id": "round-0",
                    "phase": "pre-build concept smoke",
                    "sample_size": 5,
                    "participant_mode": "simulated target users",
                    "archetypes": ["first-time novice"],
                    "goal": "validate the promise",
                    "exit_criteria": "coherent flow",
                },
                {
                    "round_id": "round-1",
                    "phase": "closed beta",
                    "sample_size": 12,
                    "participant_mode": "seed users",
                    "archetypes": ["daily operator"],
                    "goal": "validate the implemented slice",
                    "exit_criteria": "no blocker-level failures remain",
                }
            ],
        }
        try:
            local_response_contract.validate_simulated_user_profile(sample_profile)
        except Exception as exc:
            beta_round_contract_failures.append(f"profile: {exc}")
        try:
            local_response_contract.validate_beta_simulation_manifest(sample_simulation_manifest)
        except Exception as exc:
            beta_round_contract_failures.append(f"simulation-manifest: {exc}")
        try:
            local_response_contract.validate_beta_simulation_diff(sample_simulation_diff)
        except Exception as exc:
            beta_round_contract_failures.append(f"simulation-diff: {exc}")
        try:
            local_response_contract.validate_beta_ramp_plan(sample_ramp_plan)
        except Exception as exc:
            beta_round_contract_failures.append(f"ramp-plan: {exc}")
        sample_persona_library = {
            "schema_version": "simulation-persona-library/v1",
            "skill_name": "virtual-intelligent-dev-team",
            "round_persona_sets": {
                "round-0": ["first-time-novice"],
                "default": ["first-time-novice"],
            },
            "personas": [
                {
                    "profile_id": "first-time-novice",
                    "display_name": "First-Time Novice",
                    "archetype": "first-time novice",
                    "primary_goal": "Understand the core promise quickly.",
                    "tool_literacy": "low",
                    "domain_familiarity": "low",
                    "risk_tolerance": "low",
                    "workflow_preference": "step-by-step clarity",
                    "failure_sensitivity": "high",
                    "feedback_style": "balanced",
                    "preferred_tasks": ["first-run journey"],
                    "notes": "surface ambiguity early",
                }
            ],
        }
        sample_scenario_packs = {
            "schema_version": "simulation-scenario-packs/v1",
            "skill_name": "virtual-intelligent-dev-team",
            "scenarios": [
                {
                    "scenario_id": "scenario-1",
                    "title": "first meaningful task",
                    "primary_task": "finish the primary happy-path task",
                    "success_definition": "the user completes the task and understands the value",
                    "risk_focus": "onboarding clarity",
                }
            ],
            "packs": [
                {
                    "pack_id": "concept-smoke",
                    "round_ids": ["round-0"],
                    "objective_keywords": [],
                    "scenario_ids": ["scenario-1"],
                }
            ],
        }
        sample_cohort_fixtures = {
            "schema_version": "simulation-cohort-fixtures/v1",
            "skill_name": "virtual-intelligent-dev-team",
            "fixtures": [
                {
                    "fixture_id": "round-0-default",
                    "round_id": "round-0",
                    "description": "sample fixture",
                    "sessions": [
                        {
                            "session_id": "session-01",
                            "persona_id": "first-time-novice",
                            "scenario_id": "scenario-1",
                            "trace_id": "novice-cta-hesitation",
                        }
                    ],
                }
            ],
        }
        sample_trace_catalog = {
            "schema_version": "simulation-trace-catalog/v1",
            "skill_name": "virtual-intelligent-dev-team",
            "traces": [
                {
                    "trace_id": "novice-cta-hesitation",
                    "label": "Novice CTA hesitation",
                    "task_completed": True,
                    "blocker_detected": False,
                    "critical_issue_detected": False,
                    "high_severity_issue_detected": False,
                    "top_feedback_themes": ["onboarding clarity"],
                    "feedback_summary": "Task completed, but the next safe action was not obvious enough.",
                    "events": [
                        {
                            "event_type": "entry",
                            "action": "start scenario",
                            "outcome": "neutral",
                            "severity": "info",
                            "observation": "{persona_name} starts `{scenario_title}`.",
                        }
                    ],
                }
            ],
        }
        try:
            local_response_contract.validate_simulation_persona_library(sample_persona_library)
        except Exception as exc:
            beta_round_contract_failures.append(f"simulation-persona-library: {exc}")
        try:
            local_response_contract.validate_simulation_cohort_fixtures(sample_cohort_fixtures)
        except Exception as exc:
            beta_round_contract_failures.append(f"simulation-cohort-fixtures: {exc}")
        try:
            local_response_contract.validate_beta_simulation_event(sample_event)
        except Exception as exc:
            beta_round_contract_failures.append(f"simulation-event: {exc}")
        try:
            local_response_contract.validate_simulation_scenario_packs(sample_scenario_packs)
        except Exception as exc:
            beta_round_contract_failures.append(f"simulation-scenario-packs: {exc}")
        try:
            local_response_contract.validate_simulation_trace_catalog(sample_trace_catalog)
        except Exception as exc:
            beta_round_contract_failures.append(f"simulation-trace-catalog: {exc}")
        try:
            local_response_contract.validate_beta_simulation_config(sample_simulation_config)
        except Exception as exc:
            beta_round_contract_failures.append(f"simulation-config: {exc}")
        try:
            local_response_contract.validate_beta_simulation_run(sample_simulation_run)
        except Exception as exc:
            beta_round_contract_failures.append(f"simulation-run: {exc}")
    else:
        beta_round_contract_failures.append("beta round schema validator missing")
    _check(
        len(beta_round_contract_failures) == 0,
        errors,
        "beta round contract validation failed: " + "; ".join(beta_round_contract_failures),
    )
    checks.append(
        {
            "name": "beta-round-contract",
            "passed": len(beta_round_contract_failures) == 0,
            "details": {
                "report_schema_json": str(beta_round_report_schema_json_path),
                "gate_schema_json": str(beta_round_gate_result_schema_json_path),
                "simulation_manifest_schema_json": str(SKILL_DIR / "references" / "beta-simulation-manifest.schema.json"),
                "simulation_diff_schema_json": str(beta_simulation_diff_schema_json_path),
                "ramp_plan_schema_json": str(beta_ramp_plan_schema_json_path),
                "simulation_profile_schema_json": str(simulated_user_profile_schema_json_path),
                "simulation_persona_library_schema_json": str(SKILL_DIR / "references" / "simulation-persona-library.schema.json"),
                "simulation_cohort_fixtures_schema_json": str(SKILL_DIR / "references" / "simulation-cohort-fixtures.schema.json"),
                "simulation_config_schema_json": str(beta_simulation_config_schema_json_path),
                "simulation_event_schema_json": str(beta_simulation_event_schema_json_path),
                "simulation_run_schema_json": str(beta_simulation_run_schema_json_path),
                "simulation_scenario_packs_schema_json": str(SKILL_DIR / "references" / "simulation-scenario-packs.schema.json"),
                "simulation_trace_catalog_schema_json": str(SKILL_DIR / "references" / "simulation-trace-catalog.schema.json"),
            },
        }
    )

    benchmark_evals_failures: list[str] = []
    if (
        benchmark_evals_path.exists()
        and local_response_contract is not None
        and hasattr(local_response_contract, "validate_benchmark_evals_payload")
    ):
        try:
            local_response_contract.validate_benchmark_evals_payload(load_json(benchmark_evals_path))
        except Exception as exc:
            benchmark_evals_failures.append(str(exc))
    else:
        benchmark_evals_failures.append("benchmark evals schema validator missing")
    _check(
        len(benchmark_evals_failures) == 0,
        errors,
        "benchmark evals contract validation failed: " + "; ".join(benchmark_evals_failures),
    )
    checks.append(
        {
            "name": "benchmark-evals-contract",
            "passed": len(benchmark_evals_failures) == 0,
            "details": {
                "schema_json": str(benchmark_evals_schema_json_path),
                "evals_json": str(benchmark_evals_path),
            },
        }
    )

    benchmark_run_result_failures: list[str] = []
    if local_response_contract is not None and hasattr(local_response_contract, "validate_benchmark_run_result"):
        benchmark_run_samples = [
            (
                "minimal",
                {
                    "summary": {"overall_passed": True},
                    "eval_run": {"passed": 1, "total": 1},
                },
            ),
            (
                "full",
                {
                    "generated_at": "2026-04-08T12:00:00",
                    "skill_name": "virtual-intelligent-dev-team",
                    "test_run": {
                        "command": ["python", "tests.py"],
                        "cwd": str(resolved_skill_dir),
                        "returncode": 0,
                        "stdout": "",
                        "stderr": "",
                        "passed": True,
                    },
                    "validator_run": {
                        "command": ["python", "validate.py"],
                        "cwd": str(resolved_skill_dir),
                        "returncode": 0,
                        "stdout": "",
                        "stderr": "",
                        "passed": True,
                    },
                    "eval_run": {
                        "passed": 1,
                        "total": 1,
                        "cases": [
                            {
                                "id": 1,
                                "prompt": "fixture",
                                "tags": ["contract-output"],
                                "runner": "route",
                                "lead_agent": "Technical Trinity",
                                "assistant_agents": [],
                                "response_pack_preview": "",
                                "passed": True,
                                "failures": [],
                            }
                        ],
                        "category_breakdown": [
                            {"category": "contract-output", "passed": 1, "total": 1, "pass_rate": 1.0}
                        ],
                    },
                    "summary": {
                        "tests_passed": True,
                        "validator_passed": True,
                        "evals_passed": True,
                        "offline_drill_enabled": False,
                        "offline_drill_passed": None,
                        "overall_passed": True,
                        "lead_distribution": {"Technical Trinity": 1},
                        "assistant_distribution": {},
                        "eval_failures": [],
                    },
                },
            ),
        ]
        for sample_name, sample_payload in benchmark_run_samples:
            try:
                local_response_contract.validate_benchmark_run_result(sample_payload)
            except Exception as exc:
                benchmark_run_result_failures.append(f"{sample_name}: {exc}")
    else:
        benchmark_run_result_failures.append("benchmark run result schema validator missing")
    _check(
        len(benchmark_run_result_failures) == 0,
        errors,
        "benchmark run result contract validation failed: " + "; ".join(benchmark_run_result_failures),
    )
    checks.append(
        {
            "name": "benchmark-run-result-contract",
            "passed": len(benchmark_run_result_failures) == 0,
            "details": {"schema_json": str(benchmark_run_result_schema_json_path)},
        }
    )

    lead_agents = config.get("process_skill_lead_agents", {})
    process_rules = config.get("process_skill_rules", {})
    if not isinstance(lead_agents, dict):
        raise RuntimeError("routing-rules.json process_skill_lead_agents must be an object")
    if not isinstance(process_rules, dict):
        raise RuntimeError("routing-rules.json process_skill_rules must be an object")

    lead_keys = {key for key in lead_agents if isinstance(key, str)}
    rule_keys = {key for key in process_rules if isinstance(key, str)}
    missing_in_rules = sorted(lead_keys - rule_keys)
    missing_in_leads = sorted(rule_keys - lead_keys)
    _check(
        len(missing_in_rules) == 0,
        errors,
        f"process_skill_lead_agents has no matching process_skill_rules for: {missing_in_rules}. Add trigger rules before exposing that process skill.",
    )
    _check(
        len(missing_in_leads) == 0,
        errors,
        f"process_skill_rules has no lead mapping for: {missing_in_leads}. Add process_skill_lead_agents entries so routing stays executable.",
    )
    checks.append(
        {
            "name": "process-skill-key-sync",
            "passed": len(missing_in_rules) == 0 and len(missing_in_leads) == 0,
            "details": {
                "lead_agent_keys": sorted(lead_keys),
                "rule_keys": sorted(rule_keys),
            },
        }
    )

    repo_strategy = {"strategy": "trunk-main", "base_branch": "main"}
    skill_flags = {
        "pre-development-planning": {"needs_pre_development_planning": True},
        "bounded-iteration": {"needs_iteration": True},
        "using-git-worktrees": {"needs_worktree": True},
        "release-gate": {"needs_release_gate": True},
        "git-workflow": {"needs_git_workflow": True},
    }
    for skill_name, flags in skill_flags.items():
        plan = local_route_request.build_process_plan(repo_strategy=repo_strategy, **flags)
        matching = [item for item in plan if isinstance(item, dict) and item.get("skill") == skill_name]
        _check(
            len(matching) == 1,
            errors,
            f"build_process_plan does not emit exactly one `{skill_name}` entry. Update route_request.py so the process plan stays contract-complete.",
        )
        if len(matching) != 1:
            checks.append({"name": f"process-plan-{skill_name}", "passed": False})
            continue
        entry = matching[0]
        reference = entry.get("reference")
        _check(
            isinstance(reference, str) and reference != "",
            errors,
            f"Process skill `{skill_name}` is missing its `reference` field in build_process_plan. Point it to the owning playbook.",
        )
        if isinstance(reference, str) and reference:
            reference_path = (resolved_skill_dir / reference).resolve()
            _check(
                reference_path.exists(),
                errors,
                f"Process skill `{skill_name}` points to missing reference `{reference}`. Restore the file or update the process plan reference.",
            )
        commands = entry.get("commands", [])
        _check(
            isinstance(commands, list) and len(commands) > 0,
            errors,
            f"Process skill `{skill_name}` has no command examples. Add at least one runnable command so the operator path is discoverable.",
        )
        if isinstance(commands, list):
            for command in commands:
                if not isinstance(command, str):
                    continue
                for script_path in SCRIPT_COMMAND_RE.findall(command):
                    resolved_script = (resolved_skill_dir / script_path).resolve()
                    _check(
                        resolved_script.exists(),
                        errors,
                        f"Process skill `{skill_name}` references missing script `{script_path}` in command `{command}`. Fix the command or add the script.",
                    )
        checks.append({"name": f"process-plan-{skill_name}", "passed": True})

    for index_path in index_paths:
        refs = _collect_markdown_references(index_path)
        missing_refs = []
        for raw_ref in refs:
            resolved = _resolve_markdown_path(raw_ref, index_path, resolved_skill_dir)
            if not resolved.exists():
                missing_refs.append(raw_ref)
        _check(
            len(missing_refs) == 0,
            errors,
            f"{index_path.name} references missing files: {missing_refs}. Update the index so it only points to real assets.",
        )
        text = index_path.read_text(encoding="utf-8")
        missing_scripts = []
        for script_path in SCRIPT_COMMAND_RE.findall(text):
            resolved = (resolved_skill_dir / script_path).resolve()
            if not resolved.exists():
                missing_scripts.append(script_path)
        _check(
            len(missing_scripts) == 0,
            errors,
            f"{index_path.name} contains commands for missing scripts: {missing_scripts}. Repair the command index before release.",
        )
        checks.append(
            {
                "name": f"index-{index_path.name}",
                "passed": len(missing_refs) == 0 and len(missing_scripts) == 0,
                "details": {"references_checked": refs},
            }
        )

    return {
        "ok": len(errors) == 0,
        "skill_dir": str(resolved_skill_dir),
        "version": version,
        "checks": checks,
        "errors": errors,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Lint virtual-intelligent-dev-team mechanical contract.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        result = lint_contract()
        exit_code = 0 if result["ok"] else 2
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
