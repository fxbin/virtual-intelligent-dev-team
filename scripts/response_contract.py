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
    if not isinstance(resume_artifacts, list):
        resume_artifacts = []
    return {
        "workflow_bundle": team_dispatch.get("workflow_bundle"),
        "workflow_bundle_source": team_dispatch.get("workflow_bundle_source"),
        "workflow_source_explanation": evidence.get("workflow_source_explanation"),
        "route_evidence": evidence.get("route_evidence"),
        "next_action": next_action.get("smallest_executable_action"),
        "current_owner": next_action.get("current_owner"),
        "progress_anchor": resume.get("progress_anchor"),
        "resume_artifacts": [str(item) for item in resume_artifacts],
    }


def build_release_gate_explanation_card(
    *,
    decision: str,
    reason: str,
    summary: dict[str, object],
    follow_up: dict[str, object],
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

    progress_anchor = (
        str(follow_up.get("brief_markdown", "")).strip()
        or str(follow_up.get("closure_markdown", "")).strip()
        or "not required"
    )
    route_evidence = (
        f"Release gate decision is `{decision}` because {reason}. "
        f"tests={'PASS' if summary.get('tests_passed') else 'FAIL'}, "
        f"validator={'PASS' if summary.get('validator_passed') else 'FAIL'}, "
        f"evals={'PASS' if summary.get('evals_passed') else 'FAIL'}, "
        f"offline-drill={'PASS' if summary.get('offline_drill_passed') else 'FAIL'}."
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
