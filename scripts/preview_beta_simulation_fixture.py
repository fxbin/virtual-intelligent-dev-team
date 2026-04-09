#!/usr/bin/env python3
"""Preview the resolved beta simulation fixture for one config."""

from __future__ import annotations

import argparse
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


response_contract = load_module("virtual_team_preview_beta_simulation_fixture_response_contract", RESPONSE_CONTRACT_SCRIPT)


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


def load_trace_catalog(path: Path) -> dict[str, dict[str, object]]:
    payload = load_json(path)
    response_contract.validate_simulation_trace_catalog(payload)
    traces = payload.get("traces", [])
    if not isinstance(traces, list):
        raise RuntimeError(f"{path} must define a traces array")
    catalog: dict[str, dict[str, object]] = {}
    for item in traces:
        if not isinstance(item, dict):
            continue
        trace_id = str(item.get("trace_id", "")).strip()
        if trace_id == "":
            continue
        catalog[trace_id] = dict(item)
    return catalog


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def preview_beta_simulation_fixture(
    *,
    config_path: Path,
    output_dir: Path | None = None,
) -> dict[str, object]:
    config = load_json(config_path)
    response_contract.validate_beta_simulation_config(config)
    repo_root = repo_root_from_config(config_path.resolve())
    persona_dir = resolve_repo_path(repo_root, str(config["persona_dir"]))
    trace_catalog = load_trace_catalog(
        resolve_repo_path(repo_root, str(config.get("trace_catalog_source", "references/simulation-trace-catalog.json")))
    )

    scenarios = config.get("scenarios", [])
    session_plan = config.get("session_plan", [])
    if not isinstance(scenarios, list) or not isinstance(session_plan, list):
        raise RuntimeError("beta simulation config must provide list-shaped scenarios and session_plan")
    scenario_map = {
        str(item.get("scenario_id", "")): item
        for item in scenarios
        if isinstance(item, dict) and str(item.get("scenario_id", "")).strip() != ""
    }

    sessions: list[dict[str, object]] = []
    for item in session_plan:
        if not isinstance(item, dict):
            continue
        persona_id = str(item.get("persona_id", "")).strip()
        scenario_id = str(item.get("scenario_id", "")).strip()
        trace_id = str(item.get("trace_id", "")).strip()
        profile = load_json(persona_dir / f"{persona_id}.json")
        response_contract.validate_simulated_user_profile(profile)
        scenario = scenario_map.get(scenario_id)
        if scenario is None:
            raise RuntimeError(f"beta simulation config references unknown scenario_id: {scenario_id}")
        trace = trace_catalog.get(trace_id)
        if trace is None:
            raise RuntimeError(f"beta simulation config references unknown trace_id: {trace_id}")
        sessions.append(
            {
                "session_id": str(item.get("session_id", "")).strip(),
                "persona_id": persona_id,
                "persona_name": str(profile.get("display_name", "")).strip(),
                "scenario_id": scenario_id,
                "scenario_title": str(scenario.get("title", "")).strip(),
                "trace_id": trace_id,
                "trace_label": str(trace.get("label", "")).strip(),
            }
        )

    resolved_output_dir = (
        output_dir.resolve()
        if output_dir is not None
        else repo_root / ".skill-beta" / "fixture-previews" / str(config["round_id"])
    )
    resolved_output_dir.mkdir(parents=True, exist_ok=True)
    json_report = resolved_output_dir / "beta-simulation-manifest.json"
    markdown_report = resolved_output_dir / "beta-simulation-manifest.md"

    payload = {
        "schema_version": "beta-simulation-manifest/v1",
        "generated_at": now_iso(),
        "skill_name": "virtual-intelligent-dev-team",
        "round_id": str(config["round_id"]),
        "phase": str(config["phase"]),
        "objective": str(config["objective"]),
        "config_path": str(config_path),
        "cohort_fixture_source": str(config.get("cohort_fixture_source", "")),
        "trace_catalog_source": str(config.get("trace_catalog_source", "")),
        "sessions": sessions,
        "json_report": str(json_report),
        "markdown_report": str(markdown_report),
    }
    response_contract.validate_beta_simulation_manifest(payload)
    write_json(json_report, payload)

    lines = [
        f"# Beta Simulation Manifest: {payload['round_id']}",
        "",
        f"- Phase: {payload['phase']}",
        f"- Objective: {payload['objective']}",
        f"- Config: `{payload['config_path']}`",
        f"- Cohort fixture source: `{payload['cohort_fixture_source']}`",
        f"- Trace catalog source: `{payload['trace_catalog_source']}`",
        "",
        "## Sessions",
        "",
    ]
    for session in sessions:
        lines.append(
            f"- {session['session_id']} | {session['persona_name']} | {session['scenario_title']} | {session['trace_id']} | {session['trace_label']}"
        )
    markdown_report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Preview the resolved beta simulation fixture for one config.")
    parser.add_argument("--config", required=True, help="Path to beta simulation config JSON.")
    parser.add_argument("--output-dir", help="Optional output directory for manifest artifacts.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = preview_beta_simulation_fixture(
        config_path=Path(args.config).resolve(),
        output_dir=Path(args.output_dir).resolve() if args.output_dir else None,
    )
    if args.pretty:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
