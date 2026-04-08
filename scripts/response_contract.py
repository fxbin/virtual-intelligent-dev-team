#!/usr/bin/env python3
"""Shared response contract helpers for virtual-intelligent-dev-team."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from jsonschema import Draft202012Validator


SIDECAR_SCHEMA_VERSION = "response-pack-sidecar/v1"
SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
SIDECAR_SCHEMA_JSON_PATH = SKILL_DIR / "references" / "response-pack-sidecar.schema.json"
VERIFY_ACTION_SCHEMA_JSON_PATH = SKILL_DIR / "references" / "verify-action-result.schema.json"
RELEASE_GATE_SCHEMA_JSON_PATH = SKILL_DIR / "references" / "release-gate-result.schema.json"
BETA_ROUND_REPORT_SCHEMA_JSON_PATH = SKILL_DIR / "references" / "beta-round-report.schema.json"
BETA_ROUND_GATE_RESULT_SCHEMA_JSON_PATH = SKILL_DIR / "references" / "beta-round-gate-result.schema.json"
SIMULATED_USER_PROFILE_SCHEMA_JSON_PATH = SKILL_DIR / "references" / "simulated-user-profile.schema.json"
BETA_SIMULATION_PERSONA_LIBRARY_SCHEMA_JSON_PATH = SKILL_DIR / "references" / "simulation-persona-library.schema.json"
BETA_SIMULATION_CONFIG_SCHEMA_JSON_PATH = SKILL_DIR / "references" / "beta-simulation-config.schema.json"
BETA_SIMULATION_EVENT_SCHEMA_JSON_PATH = SKILL_DIR / "references" / "beta-simulation-event.schema.json"
BETA_SIMULATION_RUN_SCHEMA_JSON_PATH = SKILL_DIR / "references" / "beta-simulation-run.schema.json"
BETA_SIMULATION_SCENARIO_PACKS_SCHEMA_JSON_PATH = SKILL_DIR / "references" / "simulation-scenario-packs.schema.json"
BENCHMARK_EVALS_SCHEMA_JSON_PATH = SKILL_DIR / "references" / "benchmark-evals.schema.json"
BENCHMARK_RUN_RESULT_SCHEMA_JSON_PATH = SKILL_DIR / "references" / "benchmark-run-result.schema.json"


@lru_cache(maxsize=None)
def load_json_schema(schema_path: str) -> dict[str, object]:
    resolved_path = Path(schema_path)
    with resolved_path.open("r", encoding="utf-8") as file:
        payload = json.load(file)
    if not isinstance(payload, dict):
        raise ValueError(f"{resolved_path} must contain a JSON object")
    Draft202012Validator.check_schema(payload)
    return payload


def load_sidecar_schema() -> dict[str, object]:
    return load_json_schema(str(SIDECAR_SCHEMA_JSON_PATH))


def validate_payload_against_schema(
    payload: dict[str, object],
    *,
    schema_path: Path,
    label: str,
) -> None:
    validator = Draft202012Validator(load_json_schema(str(schema_path)))
    errors = sorted(validator.iter_errors(payload), key=lambda item: list(item.path))
    if not errors:
        return
    first = errors[0]
    path = ".".join(str(part) for part in first.path) or "<root>"
    raise ValueError(f"{label} schema validation failed at {path}: {first.message}")


def validate_response_pack_payload(payload: dict[str, object]) -> None:
    validate_payload_against_schema(
        payload,
        schema_path=SIDECAR_SCHEMA_JSON_PATH,
        label="response-pack sidecar",
    )


def validate_verify_action_result(payload: dict[str, object]) -> None:
    validate_payload_against_schema(
        payload,
        schema_path=VERIFY_ACTION_SCHEMA_JSON_PATH,
        label="verify_action result",
    )


def validate_release_gate_result(payload: dict[str, object]) -> None:
    validate_payload_against_schema(
        payload,
        schema_path=RELEASE_GATE_SCHEMA_JSON_PATH,
        label="release_gate result",
    )


def validate_beta_round_report(payload: dict[str, object]) -> None:
    validate_payload_against_schema(
        payload,
        schema_path=BETA_ROUND_REPORT_SCHEMA_JSON_PATH,
        label="beta round report",
    )


def validate_beta_round_gate_result(payload: dict[str, object]) -> None:
    validate_payload_against_schema(
        payload,
        schema_path=BETA_ROUND_GATE_RESULT_SCHEMA_JSON_PATH,
        label="beta round gate result",
    )


def validate_simulated_user_profile(payload: dict[str, object]) -> None:
    validate_payload_against_schema(
        payload,
        schema_path=SIMULATED_USER_PROFILE_SCHEMA_JSON_PATH,
        label="simulated user profile",
    )


def validate_simulation_persona_library(payload: dict[str, object]) -> None:
    validate_payload_against_schema(
        payload,
        schema_path=BETA_SIMULATION_PERSONA_LIBRARY_SCHEMA_JSON_PATH,
        label="simulation persona library",
    )
    personas = payload.get("personas", [])
    round_sets = payload.get("round_persona_sets", {})
    if not isinstance(personas, list):
        raise ValueError("simulation persona library schema validation failed at personas: expected an array")
    if not isinstance(round_sets, dict):
        raise ValueError("simulation persona library schema validation failed at round_persona_sets: expected an object")

    persona_ids = {str(item.get("profile_id", "")).strip() for item in personas if isinstance(item, dict)}
    for round_id, raw_ids in round_sets.items():
        if not isinstance(raw_ids, list):
            continue
        missing = sorted(str(item) for item in raw_ids if str(item) not in persona_ids)
        if missing:
            raise ValueError(
                "simulation persona library schema validation failed at round_persona_sets."
                f"{round_id}: unknown persona ids {', '.join(missing)}"
            )


def validate_beta_simulation_config(payload: dict[str, object]) -> None:
    validate_payload_against_schema(
        payload,
        schema_path=BETA_SIMULATION_CONFIG_SCHEMA_JSON_PATH,
        label="beta simulation config",
    )


def validate_beta_simulation_event(payload: dict[str, object]) -> None:
    validate_payload_against_schema(
        payload,
        schema_path=BETA_SIMULATION_EVENT_SCHEMA_JSON_PATH,
        label="beta simulation event",
    )


def validate_beta_simulation_run(payload: dict[str, object]) -> None:
    validate_payload_against_schema(
        payload,
        schema_path=BETA_SIMULATION_RUN_SCHEMA_JSON_PATH,
        label="beta simulation run",
    )


def validate_simulation_scenario_packs(payload: dict[str, object]) -> None:
    validate_payload_against_schema(
        payload,
        schema_path=BETA_SIMULATION_SCENARIO_PACKS_SCHEMA_JSON_PATH,
        label="simulation scenario packs",
    )
    scenarios = payload.get("scenarios", [])
    packs = payload.get("packs", [])
    if not isinstance(scenarios, list):
        raise ValueError("simulation scenario packs schema validation failed at scenarios: expected an array")
    if not isinstance(packs, list):
        raise ValueError("simulation scenario packs schema validation failed at packs: expected an array")

    scenario_ids = {str(item.get("scenario_id", "")).strip() for item in scenarios if isinstance(item, dict)}
    for index, pack in enumerate(packs):
        if not isinstance(pack, dict):
            continue
        referenced = pack.get("scenario_ids", [])
        if not isinstance(referenced, list):
            continue
        missing = sorted(str(item) for item in referenced if str(item) not in scenario_ids)
        if missing:
            raise ValueError(
                "simulation scenario packs schema validation failed at packs."
                f"{index}.scenario_ids: unknown scenario ids {', '.join(missing)}"
            )


def validate_benchmark_evals_payload(payload: dict[str, object]) -> None:
    validate_payload_against_schema(
        payload,
        schema_path=BENCHMARK_EVALS_SCHEMA_JSON_PATH,
        label="benchmark evals",
    )
    evals = payload.get("evals", [])
    if not isinstance(evals, list):
        raise ValueError("benchmark evals schema validation failed at evals: expected an array of eval cases")

    seen_ids: set[int] = set()
    duplicate_ids: list[int] = []
    for item in evals:
        if not isinstance(item, dict):
            continue
        eval_id = item.get("id")
        if not isinstance(eval_id, int):
            continue
        if eval_id in seen_ids and eval_id not in duplicate_ids:
            duplicate_ids.append(eval_id)
            continue
        seen_ids.add(eval_id)

    if duplicate_ids:
        raise ValueError(
            "benchmark evals schema validation failed at evals: duplicate eval ids "
            + ", ".join(str(item) for item in duplicate_ids)
        )


def validate_benchmark_run_result(payload: dict[str, object]) -> None:
    validate_payload_against_schema(
        payload,
        schema_path=BENCHMARK_RUN_RESULT_SCHEMA_JSON_PATH,
        label="benchmark run result",
    )


def build_explanation_card_from_payload(payload: dict[str, object]) -> dict[str, object]:
    evidence = payload.get("evidence", {})
    next_action = payload.get("next_action", {})
    resume = payload.get("resume", {})
    team_dispatch = payload.get("team_dispatch", {})
    if not isinstance(evidence, dict):
        evidence = {}
    if not isinstance(next_action, dict):
        next_action = {}
    if not isinstance(resume, dict):
        resume = {}
    if not isinstance(team_dispatch, dict):
        team_dispatch = {}
    resume_artifacts = resume.get("resume_artifacts", [])
    bundle_bootstrap = payload.get("bundle_bootstrap", {})
    if not isinstance(resume_artifacts, list):
        resume_artifacts = []
    if not isinstance(bundle_bootstrap, dict):
        bundle_bootstrap = {}
    bootstrap_commands = bundle_bootstrap.get("commands", [])
    if not isinstance(bootstrap_commands, list):
        bootstrap_commands = []
    return {
        "workflow_bundle": team_dispatch.get("workflow_bundle"),
        "workflow_bundle_source": team_dispatch.get("workflow_bundle_source"),
        "workflow_source_explanation": evidence.get("workflow_source_explanation"),
        "route_evidence": evidence.get("route_evidence"),
        "next_action": next_action.get("smallest_executable_action"),
        "current_owner": next_action.get("current_owner"),
        "progress_anchor": resume.get("progress_anchor"),
        "resume_artifacts": [str(item) for item in resume_artifacts],
        "bundle_bootstrap_commands": [str(item) for item in bootstrap_commands],
    }


def build_release_gate_explanation_card(
    *,
    decision: str,
    reason: str,
    summary: dict[str, object],
    follow_up: dict[str, object],
    beta_gate: dict[str, object] | None = None,
) -> dict[str, object]:
    resume_artifacts: list[str] = []
    for key in ("brief_json", "brief_markdown", "closure_json", "closure_markdown"):
        value = str(follow_up.get(key, "")).strip()
        if value:
            resume_artifacts.append(value)
    bootstrap = follow_up.get("bootstrap", {})
    if isinstance(bootstrap, dict):
        for key in ("plan_json", "workspace"):
            value = str(bootstrap.get(key, "")).strip()
            if value:
                resume_artifacts.append(value)
    if isinstance(beta_gate, dict):
        for key in ("json_report", "markdown_report"):
            value = str(beta_gate.get(key, "")).strip()
            if value:
                resume_artifacts.append(value)

    progress_anchor = (
        str(follow_up.get("brief_markdown", "")).strip()
        or str(follow_up.get("closure_markdown", "")).strip()
        or "not required"
    )
    beta_summary = "beta=SKIP"
    if isinstance(beta_gate, dict):
        beta_summary = (
            f"beta={'PASS' if beta_gate.get('ok') else 'FAIL'}"
            f" ({beta_gate.get('decision')} / {beta_gate.get('round_id')})"
        )
    route_evidence = (
        f"Release gate decision is `{decision}` because {reason}. "
        f"tests={'PASS' if summary.get('tests_passed') else 'FAIL'}, "
        f"validator={'PASS' if summary.get('validator_passed') else 'FAIL'}, "
        f"evals={'PASS' if summary.get('evals_passed') else 'FAIL'}, "
        f"offline-drill={'PASS' if summary.get('offline_drill_passed') else 'FAIL'}, "
        f"{beta_summary}."
    )
    next_action = str(follow_up.get("next_action", "")).strip()
    if next_action == "":
        next_action = "archive the release-ready baseline" if decision == "ship" else "bootstrap the next bounded iteration"
    return {
        "workflow_bundle": "ship-hold-remediate",
        "workflow_bundle_source": "process-skill",
        "workflow_source_explanation": "Release gate is the active acceptance lane because the current decision must be justified by benchmark and drill evidence.",
        "route_evidence": route_evidence,
        "next_action": next_action,
        "current_owner": "Technical Trinity",
        "progress_anchor": progress_anchor,
        "resume_artifacts": resume_artifacts,
    }
