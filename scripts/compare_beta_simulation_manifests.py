#!/usr/bin/env python3
"""Compare two beta simulation fixture manifests and emit a structured diff."""

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


response_contract = load_module("virtual_team_compare_beta_simulation_manifests_contract", RESPONSE_CONTRACT_SCRIPT)


def load_json(path: Path) -> dict[str, object]:
    with path.open("r", encoding="utf-8") as file:
        payload = json.load(file)
    if not isinstance(payload, dict):
        raise RuntimeError(f"{path} must contain a JSON object")
    return payload


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def repo_root_from_manifest(manifest_path: Path) -> Path:
    if (
        manifest_path.parent.parent.name == "fixture-previews"
        and manifest_path.parent.parent.parent.name == ".skill-beta"
    ):
        return manifest_path.parent.parent.parent.parent
    return manifest_path.parent


def session_signature(session: dict[str, object]) -> tuple[str, str, str]:
    return (
        str(session.get("persona_id", "")).strip(),
        str(session.get("scenario_id", "")).strip(),
        str(session.get("trace_id", "")).strip(),
    )


def build_index(
    sessions: list[dict[str, object]],
    *,
    id_key: str,
    label_key: str,
) -> dict[str, dict[str, object]]:
    indexed: dict[str, dict[str, object]] = {}
    for item in sessions:
        entity_id = str(item.get(id_key, "")).strip()
        if entity_id == "":
            continue
        session_ids = indexed.setdefault(
            entity_id,
            {
                id_key: entity_id,
                label_key: str(item.get(label_key, "")).strip(),
                "session_ids": [],
            },
        )["session_ids"]
        if isinstance(session_ids, list):
            session_ids.append(str(item.get("session_id", "")).strip())

    normalized: dict[str, dict[str, object]] = {}
    for entity_id, item in indexed.items():
        session_ids = sorted({value for value in item["session_ids"] if value})
        normalized[entity_id] = {
            id_key: entity_id,
            label_key: str(item.get(label_key, "")).strip(),
            "session_count": len(session_ids),
            "session_ids": session_ids,
        }
    return normalized


def diff_entities(
    previous_sessions: list[dict[str, object]],
    current_sessions: list[dict[str, object]],
    *,
    id_key: str,
    label_key: str,
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    previous_index = build_index(previous_sessions, id_key=id_key, label_key=label_key)
    current_index = build_index(current_sessions, id_key=id_key, label_key=label_key)

    added = [
        dict(current_index[key])
        for key in sorted(current_index)
        if key not in previous_index
    ]
    removed = [
        dict(previous_index[key])
        for key in sorted(previous_index)
        if key not in current_index
    ]
    return added, removed


def coverage_mode(
    *,
    session_count_delta: int,
    added_count: int,
    removed_count: int,
) -> str:
    if session_count_delta == 0 and added_count == 0 and removed_count == 0:
        return "unchanged"
    if session_count_delta >= 0 and added_count > 0 and removed_count == 0:
        return "expanded"
    if session_count_delta <= 0 and removed_count > 0 and added_count == 0:
        return "contracted"
    return "mixed"


def build_risk_notes(
    *,
    session_count_delta: int,
    added_personas: list[dict[str, object]],
    removed_personas: list[dict[str, object]],
    added_scenarios: list[dict[str, object]],
    removed_scenarios: list[dict[str, object]],
    added_traces: list[dict[str, object]],
    removed_traces: list[dict[str, object]],
    new_session_matrix: list[dict[str, object]],
    expansion_mode: str,
) -> list[str]:
    notes: list[str] = []
    if expansion_mode == "unchanged":
        notes.append("Fixture shape is unchanged from the previous round.")
    if session_count_delta > 0:
        notes.append(f"Session count expands by {session_count_delta}; review new coverage before execution.")
    if session_count_delta < 0:
        notes.append(f"Session count contracts by {abs(session_count_delta)}; confirm whether the rollback in coverage is intentional.")
    if removed_personas:
        notes.append("Persona coverage shrank; do not drop a persona cohort without an explicit acceptance decision.")
    if removed_scenarios:
        notes.append("Scenario coverage shrank; ensure the removed task path is not hiding unresolved workflow risk.")
    if removed_traces:
        notes.append("Trace coverage shrank; confirm that removed failure paths are already retired or otherwise covered.")
    if new_session_matrix:
        notes.append(
            f"New persona/scenario/trace combinations were introduced ({len(new_session_matrix)} sessions); spot-check them before the run."
        )
    if not notes and (added_personas or added_scenarios or added_traces):
        notes.append("Coverage expanded while preserving the previous baseline.")
    return notes


def compare_beta_simulation_manifests(
    *,
    previous_manifest_path: Path,
    current_manifest_path: Path,
    output_dir: Path | None = None,
) -> dict[str, object]:
    previous = load_json(previous_manifest_path)
    current = load_json(current_manifest_path)
    response_contract.validate_beta_simulation_manifest(previous)
    response_contract.validate_beta_simulation_manifest(current)

    previous_sessions = previous.get("sessions", [])
    current_sessions = current.get("sessions", [])
    if not isinstance(previous_sessions, list) or not isinstance(current_sessions, list):
        raise RuntimeError("beta simulation manifests must provide sessions arrays")
    previous_session_rows = [dict(item) for item in previous_sessions if isinstance(item, dict)]
    current_session_rows = [dict(item) for item in current_sessions if isinstance(item, dict)]

    added_personas, removed_personas = diff_entities(
        previous_session_rows,
        current_session_rows,
        id_key="persona_id",
        label_key="persona_name",
    )
    added_scenarios, removed_scenarios = diff_entities(
        previous_session_rows,
        current_session_rows,
        id_key="scenario_id",
        label_key="scenario_title",
    )
    added_traces, removed_traces = diff_entities(
        previous_session_rows,
        current_session_rows,
        id_key="trace_id",
        label_key="trace_label",
    )

    previous_signature_counts = Counter(session_signature(item) for item in previous_session_rows)
    new_session_matrix: list[dict[str, object]] = []
    for item in current_session_rows:
        signature = session_signature(item)
        if previous_signature_counts[signature] > 0:
            previous_signature_counts[signature] -= 1
            continue
        new_session_matrix.append(
            {
                "session_id": str(item.get("session_id", "")).strip(),
                "persona_id": str(item.get("persona_id", "")).strip(),
                "persona_name": str(item.get("persona_name", "")).strip(),
                "scenario_id": str(item.get("scenario_id", "")).strip(),
                "scenario_title": str(item.get("scenario_title", "")).strip(),
                "trace_id": str(item.get("trace_id", "")).strip(),
                "trace_label": str(item.get("trace_label", "")).strip(),
            }
        )

    previous_session_count = len(previous_session_rows)
    current_session_count = len(current_session_rows)
    session_count_delta = current_session_count - previous_session_count
    added_count = len(added_personas) + len(added_scenarios) + len(added_traces) + len(new_session_matrix)
    removed_count = len(removed_personas) + len(removed_scenarios) + len(removed_traces)
    expansion_mode = coverage_mode(
        session_count_delta=session_count_delta,
        added_count=added_count,
        removed_count=removed_count,
    )
    risk_notes = build_risk_notes(
        session_count_delta=session_count_delta,
        added_personas=added_personas,
        removed_personas=removed_personas,
        added_scenarios=added_scenarios,
        removed_scenarios=removed_scenarios,
        added_traces=added_traces,
        removed_traces=removed_traces,
        new_session_matrix=new_session_matrix,
        expansion_mode=expansion_mode,
    )
    expansion_ok = session_count_delta >= 0 and removed_count == 0
    review_required = session_count_delta < 0 or removed_count > 0

    repo_root = repo_root_from_manifest(current_manifest_path.resolve())
    resolved_output_dir = (
        output_dir.resolve()
        if output_dir is not None
        else repo_root
        / ".skill-beta"
        / "fixture-diffs"
        / f"{previous.get('round_id', 'previous')}-to-{current.get('round_id', 'current')}"
    )
    resolved_output_dir.mkdir(parents=True, exist_ok=True)
    json_report = resolved_output_dir / "beta-simulation-diff.json"
    markdown_report = resolved_output_dir / "beta-simulation-diff.md"

    payload = {
        "schema_version": "beta-simulation-diff/v1",
        "generated_at": now_iso(),
        "skill_name": "virtual-intelligent-dev-team",
        "previous_round_id": str(previous.get("round_id", "")).strip(),
        "current_round_id": str(current.get("round_id", "")).strip(),
        "previous_manifest_path": str(previous_manifest_path),
        "current_manifest_path": str(current_manifest_path),
        "previous_session_count": previous_session_count,
        "current_session_count": current_session_count,
        "session_count_delta": session_count_delta,
        "added_personas": added_personas,
        "removed_personas": removed_personas,
        "added_scenarios": added_scenarios,
        "removed_scenarios": removed_scenarios,
        "added_traces": added_traces,
        "removed_traces": removed_traces,
        "new_session_matrix": new_session_matrix,
        "coverage_shift_summary": {
            "previous_persona_count": len({str(item.get("persona_id", "")).strip() for item in previous_session_rows}),
            "current_persona_count": len({str(item.get("persona_id", "")).strip() for item in current_session_rows}),
            "previous_scenario_count": len({str(item.get("scenario_id", "")).strip() for item in previous_session_rows}),
            "current_scenario_count": len({str(item.get("scenario_id", "")).strip() for item in current_session_rows}),
            "previous_trace_count": len({str(item.get("trace_id", "")).strip() for item in previous_session_rows}),
            "current_trace_count": len({str(item.get("trace_id", "")).strip() for item in current_session_rows}),
            "new_session_matrix_count": len(new_session_matrix),
            "expansion_mode": expansion_mode,
        },
        "risk_notes": risk_notes,
        "expansion_ok": expansion_ok,
        "review_required": review_required,
        "json_report": str(json_report),
        "markdown_report": str(markdown_report),
    }
    response_contract.validate_beta_simulation_diff(payload)
    write_json(json_report, payload)

    def render_entity_changes(title: str, items: list[dict[str, object]], id_key: str, label_key: str) -> list[str]:
        lines = [f"## {title}", ""]
        if not items:
            lines.append("- none")
            lines.append("")
            return lines
        for item in items:
            lines.append(
                f"- {item[id_key]} | {item[label_key]} | sessions {item['session_count']} | {', '.join(item['session_ids'])}"
            )
        lines.append("")
        return lines

    markdown_lines = [
        f"# Beta Simulation Diff: {payload['previous_round_id']} -> {payload['current_round_id']}",
        "",
        f"- Previous manifest: `{payload['previous_manifest_path']}`",
        f"- Current manifest: `{payload['current_manifest_path']}`",
        f"- Expansion ok: {'yes' if payload['expansion_ok'] else 'no'}",
        f"- Review required: {'yes' if payload['review_required'] else 'no'}",
        "",
        "## Coverage Shift Summary",
        "",
        f"- Sessions: {payload['previous_session_count']} -> {payload['current_session_count']} ({payload['session_count_delta']:+d})",
        f"- Personas: {payload['coverage_shift_summary']['previous_persona_count']} -> {payload['coverage_shift_summary']['current_persona_count']}",
        f"- Scenarios: {payload['coverage_shift_summary']['previous_scenario_count']} -> {payload['coverage_shift_summary']['current_scenario_count']}",
        f"- Traces: {payload['coverage_shift_summary']['previous_trace_count']} -> {payload['coverage_shift_summary']['current_trace_count']}",
        f"- New session matrix count: {payload['coverage_shift_summary']['new_session_matrix_count']}",
        f"- Expansion mode: {payload['coverage_shift_summary']['expansion_mode']}",
        "",
    ]
    markdown_lines.extend(render_entity_changes("Added Personas", added_personas, "persona_id", "persona_name"))
    markdown_lines.extend(render_entity_changes("Removed Personas", removed_personas, "persona_id", "persona_name"))
    markdown_lines.extend(render_entity_changes("Added Scenarios", added_scenarios, "scenario_id", "scenario_title"))
    markdown_lines.extend(render_entity_changes("Removed Scenarios", removed_scenarios, "scenario_id", "scenario_title"))
    markdown_lines.extend(render_entity_changes("Added Traces", added_traces, "trace_id", "trace_label"))
    markdown_lines.extend(render_entity_changes("Removed Traces", removed_traces, "trace_id", "trace_label"))
    markdown_lines.extend(["## New Session Matrix", ""])
    if not new_session_matrix:
        markdown_lines.extend(["- none", ""])
    else:
        for item in new_session_matrix:
            markdown_lines.append(
                f"- {item['session_id']} | {item['persona_name']} | {item['scenario_title']} | {item['trace_id']} | {item['trace_label']}"
            )
        markdown_lines.append("")
    markdown_lines.extend(["## Risk Notes", ""])
    if not risk_notes:
        markdown_lines.append("- none")
    else:
        markdown_lines.extend(f"- {note}" for note in risk_notes)
    markdown_report.write_text("\n".join(markdown_lines) + "\n", encoding="utf-8")
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare two beta simulation manifests.")
    parser.add_argument("--previous", required=True, help="Path to the previous beta simulation manifest JSON.")
    parser.add_argument("--current", required=True, help="Path to the current beta simulation manifest JSON.")
    parser.add_argument("--output-dir", help="Optional output directory for diff artifacts.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = compare_beta_simulation_manifests(
        previous_manifest_path=Path(args.previous).resolve(),
        current_manifest_path=Path(args.current).resolve(),
        output_dir=Path(args.output_dir).resolve() if args.output_dir else None,
    )
    if args.pretty:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
