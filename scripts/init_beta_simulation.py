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
PERSONA_LIBRARY_PATH = SKILL_DIR / "references" / "simulation-persona-library.json"
COHORT_FIXTURES_PATH = SKILL_DIR / "references" / "simulation-cohort-fixtures.json"
SCENARIO_PACKS_PATH = SKILL_DIR / "references" / "simulation-scenario-packs.json"
TRACE_CATALOG_PATH = SKILL_DIR / "references" / "simulation-trace-catalog.json"
RESPONSE_CONTRACT_SCRIPT = SCRIPT_DIR / "response_contract.py"
PREVIEW_BETA_SIMULATION_FIXTURE_SCRIPT = SCRIPT_DIR / "preview_beta_simulation_fixture.py"


def load_module(name: str, path: Path):
    import importlib.util

    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


response_contract = load_module("virtual_team_init_beta_simulation_response_contract", RESPONSE_CONTRACT_SCRIPT)
fixture_preview = load_module(
    "virtual_team_init_beta_simulation_fixture_preview",
    PREVIEW_BETA_SIMULATION_FIXTURE_SCRIPT,
)


def load_json(path: Path) -> dict[str, object]:
    with path.open("r", encoding="utf-8") as file:
        payload = json.load(file)
    if not isinstance(payload, dict):
        raise RuntimeError(f"{path} must contain a JSON object")
    return payload


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_persona_library() -> tuple[list[dict[str, object]], dict[str, list[str]]]:
    payload = load_json(PERSONA_LIBRARY_PATH)
    response_contract.validate_simulation_persona_library(payload)
    personas = payload.get("personas", [])
    if not isinstance(personas, list) or not personas:
        raise RuntimeError("simulation-persona-library.json must define a non-empty personas array")
    round_sets = payload.get("round_persona_sets", {})
    if not isinstance(round_sets, dict):
        round_sets = {}
    normalized_round_sets: dict[str, list[str]] = {}
    for key, value in round_sets.items():
        if not isinstance(value, list):
            continue
        normalized_round_sets[str(key)] = [str(item) for item in value if str(item).strip() != ""]
    return [dict(item) for item in personas if isinstance(item, dict)], normalized_round_sets


def select_profiles_for_round(round_id: str) -> list[dict[str, object]]:
    personas, round_sets = load_persona_library()
    allowed_ids = round_sets.get(round_id) or round_sets.get("default") or []
    if not allowed_ids:
        return personas
    allowed_lookup = {item for item in allowed_ids}
    selected = [item for item in personas if str(item.get("profile_id", "")) in allowed_lookup]
    return selected or personas


def load_scenario_registry() -> tuple[dict[str, dict[str, str]], list[dict[str, object]]]:
    payload = load_json(SCENARIO_PACKS_PATH)
    response_contract.validate_simulation_scenario_packs(payload)
    scenarios = payload.get("scenarios", [])
    packs = payload.get("packs", [])
    if not isinstance(scenarios, list) or not scenarios:
        raise RuntimeError("simulation-scenario-packs.json must define a non-empty scenarios array")
    if not isinstance(packs, list) or not packs:
        raise RuntimeError("simulation-scenario-packs.json must define a non-empty packs array")
    scenario_map: dict[str, dict[str, str]] = {}
    for item in scenarios:
        if not isinstance(item, dict):
            continue
        scenario_id = str(item.get("scenario_id", "")).strip()
        if scenario_id == "":
            continue
        scenario_map[scenario_id] = {
            "scenario_id": scenario_id,
            "title": str(item.get("title", "")).strip(),
            "primary_task": str(item.get("primary_task", "")).strip(),
            "success_definition": str(item.get("success_definition", "")).strip(),
            "risk_focus": str(item.get("risk_focus", "")).strip(),
        }
    if not scenario_map:
        raise RuntimeError("simulation-scenario-packs.json did not contain any valid scenarios")
    return scenario_map, [dict(item) for item in packs if isinstance(item, dict)]


def select_scenarios(round_id: str, objective: str) -> list[dict[str, str]]:
    scenario_map, packs = load_scenario_registry()
    objective_lower = objective.lower()

    def pack_matches(item: dict[str, object]) -> bool:
        keywords = item.get("objective_keywords", [])
        if isinstance(keywords, list) and any(str(keyword).lower() in objective_lower for keyword in keywords):
            return True
        round_ids = item.get("round_ids", [])
        return isinstance(round_ids, list) and round_id in {str(value) for value in round_ids}

    selected_pack = next((item for item in packs if pack_matches(item)), None)
    if selected_pack is None:
        selected_pack = next((item for item in packs if str(item.get("pack_id", "")) == "default-beta"), None)
    scenario_ids = selected_pack.get("scenario_ids", []) if isinstance(selected_pack, dict) else []
    if not isinstance(scenario_ids, list) or not scenario_ids:
        return list(scenario_map.values())
    selected = [scenario_map[str(item)] for item in scenario_ids if str(item) in scenario_map]
    return selected or list(scenario_map.values())


def load_cohort_fixtures() -> list[dict[str, object]]:
    payload = load_json(COHORT_FIXTURES_PATH)
    response_contract.validate_simulation_cohort_fixtures(payload)
    fixtures = payload.get("fixtures", [])
    if not isinstance(fixtures, list) or not fixtures:
        raise RuntimeError("simulation-cohort-fixtures.json must define a non-empty fixtures array")
    return [dict(item) for item in fixtures if isinstance(item, dict)]


def load_trace_catalog() -> dict[str, dict[str, object]]:
    payload = load_json(TRACE_CATALOG_PATH)
    response_contract.validate_simulation_trace_catalog(payload)
    traces = payload.get("traces", [])
    if not isinstance(traces, list) or not traces:
        raise RuntimeError("simulation-trace-catalog.json must define a non-empty traces array")
    catalog: dict[str, dict[str, object]] = {}
    for item in traces:
        if not isinstance(item, dict):
            continue
        trace_id = str(item.get("trace_id", "")).strip()
        if trace_id == "":
            continue
        catalog[trace_id] = dict(item)
    if not catalog:
        raise RuntimeError("simulation-trace-catalog.json did not contain any valid traces")
    return catalog


def default_trace_id_for_persona(persona_id: str) -> str:
    mapping = {
        "first-time-novice": "novice-cta-hesitation",
        "daily-operator": "operator-reentry-friction",
        "goal-driven-power-user": "power-user-fast-path-friction",
        "skeptical-evaluator": "skeptic-trust-check",
        "edge-case-breaker": "edge-recovery-break",
    }
    return mapping.get(persona_id, "novice-cta-hesitation")


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
                "trace_id": default_trace_id_for_persona(persona_id),
            }
        )
        if persona_id in {"edge-case-breaker", "goal-driven-power-user"} and len(scenarios) > 1:
            plan.append(
                {
                    "session_id": f"session-{len(plan)+1:02d}",
                    "persona_id": persona_id,
                    "scenario_id": str(scenarios[-1]["scenario_id"]),
                    "trace_id": default_trace_id_for_persona(persona_id),
                }
            )
    return plan


def select_session_plan(
    round_id: str,
    *,
    personas: list[dict[str, object]],
    scenarios: list[dict[str, str]],
) -> tuple[str | None, list[dict[str, str]]]:
    fixtures = load_cohort_fixtures()
    trace_catalog = load_trace_catalog()
    persona_ids = {str(item.get("profile_id", "")) for item in personas if isinstance(item, dict)}
    scenario_ids = {str(item.get("scenario_id", "")) for item in scenarios if isinstance(item, dict)}

    selected_fixture = next((item for item in fixtures if str(item.get("round_id", "")).strip() == round_id), None)
    if selected_fixture is None:
        return None, build_session_plan(personas, scenarios)

    sessions = selected_fixture.get("sessions", [])
    if not isinstance(sessions, list) or not sessions:
        return str(selected_fixture.get("fixture_id", "")).strip() or None, build_session_plan(personas, scenarios)

    plan: list[dict[str, str]] = []
    for item in sessions:
        if not isinstance(item, dict):
            continue
        persona_id = str(item.get("persona_id", "")).strip()
        scenario_id = str(item.get("scenario_id", "")).strip()
        trace_id = str(item.get("trace_id", "")).strip()
        if persona_id not in persona_ids:
            raise RuntimeError(f"simulation cohort fixture references unknown persona_id: {persona_id}")
        if scenario_id not in scenario_ids:
            raise RuntimeError(f"simulation cohort fixture references unknown scenario_id: {scenario_id}")
        if trace_id not in trace_catalog:
            raise RuntimeError(f"simulation cohort fixture references unknown trace_id: {trace_id}")
        plan.append(
            {
                "session_id": str(item.get("session_id", "")).strip() or f"session-{len(plan)+1:02d}",
                "persona_id": persona_id,
                "scenario_id": scenario_id,
                "trace_id": trace_id,
            }
        )
    return str(selected_fixture.get("fixture_id", "")).strip() or None, plan


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
    personas = select_profiles_for_round(round_id)
    scenarios = select_scenarios(round_id, objective)
    fixture_id, session_plan = select_session_plan(
        round_id,
        personas=personas,
        scenarios=scenarios,
    )

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
            "cohort_fixture_source": "references/simulation-cohort-fixtures.json",
            "trace_catalog_source": "references/simulation-trace-catalog.json",
            "scenarios": scenarios,
            "session_plan": session_plan,
        }
    )
    response_contract.validate_beta_simulation_config(config_payload)

    config_existed = config_path.exists()
    status = "skipped"
    if overwrite or not config_existed:
        write_json(config_path, config_payload)
        status = "updated" if overwrite and config_existed else "created"

    preview_payload = fixture_preview.preview_beta_simulation_fixture(config_path=config_path.resolve())

    return {
        "ok": True,
        "status": status,
        "round_id": round_id,
        "config_path": str(config_path.relative_to(root)),
        "persona_dir": str(persona_dir.relative_to(root)),
        "run_output_dir": str(run_output_dir.relative_to(root)),
        "feedback_ledger_out": ".skill-beta/feedback-ledger.md",
        "round_report_out": str(round_report_out.relative_to(root)),
        "cohort_fixture_source": "references/simulation-cohort-fixtures.json",
        "trace_catalog_source": "references/simulation-trace-catalog.json",
        "cohort_fixture_id": fixture_id,
        "fixture_manifest_json": str(Path(str(preview_payload["json_report"])).relative_to(root)),
        "fixture_manifest_markdown": str(Path(str(preview_payload["markdown_report"])).relative_to(root)),
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
