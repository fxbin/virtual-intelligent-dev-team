#!/usr/bin/env python3
"""Shared response contract helpers for virtual-intelligent-dev-team."""

from __future__ import annotations


SIDECAR_SCHEMA_VERSION = "response-pack-sidecar/v1"


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
