#!/usr/bin/env python3
"""Initialize lightweight pre-development planning artifacts."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Callable, Iterable


SKILL_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = SKILL_DIR / "assets"
SAFE_SLUG = re.compile(r"[^a-z0-9]+")
DEFAULT_PHASE_BLUEPRINTS = [
    {
        "name": "Foundation",
        "goal_template": "Confirm the current-state architecture, constraints, and migration risks for {task_name}.",
        "prerequisite_template": "Transformation scope and constraints are confirmed.",
        "task_title_template": "Confirm current-state architecture and migration constraints for {task_name}",
        "acceptance_template": "Architecture, constraints, and major risks are written down.",
        "effort": "M",
    },
    {
        "name": "Architecture",
        "goal_template": "Define the target architecture, system boundaries, and dependency strategy for {task_name}.",
        "prerequisite_template": "Phase 1 findings are accepted and the main risks are visible.",
        "task_title_template": "Define target architecture slices and dependency boundaries for {task_name}",
        "acceptance_template": "Target architecture, boundaries, and migration sequencing are documented.",
        "effort": "L",
    },
    {
        "name": "Execution",
        "goal_template": "Break {task_name} into implementation slices with acceptance criteria and owner handoffs.",
        "prerequisite_template": "Target architecture and dependency strategy are approved.",
        "task_title_template": "Split the transformation into executable implementation slices for {task_name}",
        "acceptance_template": "Execution slices, dependencies, and acceptance criteria are ready for implementation.",
        "effort": "L",
    },
    {
        "name": "Cutover",
        "goal_template": "Prepare rollout, validation, and rollback readiness for {task_name}.",
        "prerequisite_template": "Execution slices are planned and critical dependencies are mapped.",
        "task_title_template": "Define rollout validation and rollback checkpoints for {task_name}",
        "acceptance_template": "Cutover checks, rollback points, and release-readiness criteria are documented.",
        "effort": "M",
    },
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str, *, force: bool) -> bool:
    if path.exists() and not force:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True


def replace_line(content: str, prefix: str, value: str) -> str:
    lines = content.splitlines()
    updated: list[str] = []
    for line in lines:
        if line.startswith(prefix):
            updated.append(f"{prefix} {value}".rstrip())
        else:
            updated.append(line)
    return "\n".join(updated) + "\n"


def slugify(value: str, *, default: str) -> str:
    lowered = value.lower().strip()
    normalized = SAFE_SLUG.sub("-", lowered).strip("-")
    return normalized or default


def normalize_phase_display_name(value: str, *, default: str) -> str:
    normalized = value.strip()
    if normalized == "":
        return default
    if normalized == normalized.lower():
        return " ".join(part.capitalize() for part in re.split(r"[\s_-]+", normalized) if part)
    return normalized


def replace_first_matching_line(content: str, predicate: Callable[[str], bool], value: str) -> str:
    lines = content.splitlines()
    for index, line in enumerate(lines):
        if predicate(line):
            lines[index] = value
            break
    return "\n".join(lines) + "\n"


def replace_exact_line(content: str, original: str, value: str) -> str:
    return replace_first_matching_line(content, lambda line: line == original, value)


def replace_table_row(content: str, prefix: str, value: str) -> str:
    return replace_first_matching_line(content, lambda line: line.startswith(prefix), value)


def fill_blank_line_after_header(content: str, header: str, value: str) -> str:
    lines = content.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == header and index + 1 < len(lines) and lines[index + 1].strip() == "":
            lines[index + 1] = value
            break
    return "\n".join(lines) + "\n"


def insert_value_after_label(content: str, label: str, value: str) -> str:
    lines = content.splitlines()
    for index, line in enumerate(lines):
        if line.strip() != label:
            continue
        if index + 1 >= len(lines):
            lines.append(value)
            break
        next_line = lines[index + 1]
        if next_line.strip() == "" or next_line.endswith(":"):
            lines.insert(index + 1, value)
        else:
            lines[index + 1] = value
        break
    return "\n".join(lines) + "\n"


def phase_blueprints(first_phase_name: str) -> list[dict[str, str]]:
    blueprints = [dict(item) for item in DEFAULT_PHASE_BLUEPRINTS]
    blueprints[0]["name"] = normalize_phase_display_name(first_phase_name, default="Foundation")
    return blueprints


def prepare_project_overview(task_name: str, task_description: str) -> str:
    content = read_text(ASSETS_DIR / "pre-development-project-overview-template.md")
    content = replace_line(content, "- Scope:", task_name)
    content = replace_line(content, "- Target state:", task_description)
    content = replace_line(content, "- Primary priority:", "maintainability")
    content = replace_line(content, "- Resume hint:", "Read docs/progress/MASTER.md first.")
    return content


def prepare_task_breakdown(task_name: str, phase_name: str) -> str:
    phases = phase_blueprints(phase_name)
    phase_names = [str(phase["name"]).strip() or f"Phase {index}" for index, phase in enumerate(phases, start=1)]
    content = read_text(ASSETS_DIR / "pre-development-task-breakdown-template.md")
    content = replace_line(content, "- Total phases:", str(len(phases)))
    content = replace_line(
        content,
        "- Execution strategy:",
        "phase-gated transformation planning with dependency-aware checkpoints",
    )
    content = replace_line(
        content,
        "- Primary dependency chain:",
        " -> ".join(phase_names),
    )
    first_phase = phases[0]
    content = content.replace("Phase 1: Foundation", f"Phase 1: {first_phase['name']}")
    content = insert_value_after_label(content, "Goal:", first_phase["goal_template"].format(task_name=task_name))
    content = insert_value_after_label(
        content,
        "Prerequisite:",
        first_phase["prerequisite_template"].format(task_name=task_name),
    )
    content = replace_table_row(
        content,
        "| P1-T1",
        f"| P1-T1   | {first_phase['task_title_template'].format(task_name=task_name)} | P0       | {first_phase['effort']}      | --         | {first_phase['acceptance_template'].format(task_name=task_name)} |",
    )
    additional_sections: list[str] = []
    for index, phase in enumerate(phases[1:], start=2):
        section = "\n".join(
            [
                "",
                f"## Phase {index}: {phase['name']}",
                "Goal:",
                phase["goal_template"].format(task_name=task_name),
                "Prerequisite:",
                phase["prerequisite_template"].format(task_name=task_name),
                "",
                "| Task ID | Task | Priority | Effort | Depends On | Acceptance Criteria |",
                "|:--------|:-----|:---------|:-------|:-----------|:--------------------|",
                (
                    f"| P{index}-T1   | {phase['task_title_template'].format(task_name=task_name)} "
                    f"| P1       | {phase['effort']}      | P{index - 1}-T1    | "
                    f"{phase['acceptance_template'].format(task_name=task_name)} |"
                ),
            ]
        )
        additional_sections.append(section)
    content = content.replace("## Milestones\n", "".join(additional_sections) + "\n\n## Milestones\n", 1)
    content = replace_table_row(
        content,
        "|           |       |          |",
        "| Planning pack approved | 1 | Scope, architecture snapshot, and major risks are aligned. |\n| Execution slices approved | 3 | Implementation slices and acceptance criteria are ready. |\n| Cutover plan approved | 4 | Rollout, rollback, and release-readiness checks are defined. |",
    )
    content = replace_line(content, "- Highest-risk phase:", "Phase 2")
    content = replace_line(content, "- First executable task:", first_phase["task_title_template"].format(task_name=task_name) + ".")
    return content


def build_phase_summary_rows(phases: Iterable[dict[str, str]]) -> str:
    rows = [
        f"| {phase['index']}     | {phase['name']} | 1     | 0    | {'in-progress' if phase['index'] == 1 else 'not-started'} |"
        for phase in phases
    ]
    return "\n".join(rows)


def prepare_master(task_name: str, task_description: str, phases: list[dict[str, str]]) -> str:
    today = datetime.now().date().isoformat()
    content = read_text(ASSETS_DIR / "pre-development-progress-master-template.md")
    content = replace_line(content, "- Name:", task_name)
    content = replace_line(content, "- Description:", task_description)
    content = replace_line(content, "- Started:", today)
    content = replace_line(content, "- Last updated:", today)
    content = replace_line(content, "- Active phase:", "Phase 1")
    content = replace_line(content, "- Active task:", phases[0]["task_title"])
    content = replace_line(content, "- Blockers:", "None")
    content = replace_table_row(
        content,
        "| 1     |",
        build_phase_summary_rows(phases),
    )
    content = replace_table_row(
        content,
        "|      |         |",
        f"| {today} | Initialized multi-phase planning pack with {len(phases)} phase trackers. |",
    )
    content = replace_line(content, "1.", phases[0]["task_title"])
    content = replace_line(content, "2.", "Confirm whether phase boundaries or naming need to change before implementation starts.")
    return content


def prepare_phase(
    phase_index: int,
    phase_name: str,
    goal: str,
    task_title: str,
    acceptance: str,
    effort: str,
    resume_point: str,
) -> str:
    content = read_text(ASSETS_DIR / "pre-development-phase-template.md")
    content = content.replace("# Phase N: Name", f"# Phase {phase_index}: {phase_name}")
    content = content.replace("- [ ] Task N.1", f"- [ ] Task {phase_index}.1: {task_title}", 1)
    content = replace_line(content, "  - Priority:", "P0")
    content = replace_line(content, "  - Effort:", effort)
    content = replace_line(content, "  - Acceptance:", acceptance)
    content = replace_line(content, "  - Notes:", "_none yet_")
    content = fill_blank_line_after_header(content, "## Goal", goal)
    status = "in-progress" if phase_index == 1 else "not-started"
    content = replace_exact_line(content, "- not-started | in-progress | complete", f"- {status}")
    content = replace_line(content, "- Resume point:", resume_point)
    return content


def initialize_pre_development_plan(
    root: Path,
    task_name: str,
    task_description: str,
    phase_name: str,
    *,
    force: bool = False,
) -> dict[str, object]:
    phase_specs: list[dict[str, str]] = []
    for index, blueprint in enumerate(phase_blueprints(phase_name), start=1):
        name = normalize_phase_display_name(str(blueprint["name"]), default=f"Phase {index}")
        phase_specs.append(
            {
                "index": index,
                "name": name,
                "slug": slugify(name, default=f"phase-{index}"),
                "goal": blueprint["goal_template"].format(task_name=task_name),
                "task_title": blueprint["task_title_template"].format(task_name=task_name),
                "acceptance": blueprint["acceptance_template"].format(task_name=task_name),
                "effort": str(blueprint["effort"]),
                "prerequisite": blueprint["prerequisite_template"].format(task_name=task_name),
            }
        )
    phase_slug = phase_specs[0]["slug"]
    analysis_dir = root / "docs" / "analysis"
    plan_dir = root / "docs" / "plan"
    progress_dir = root / "docs" / "progress"

    project_overview_path = analysis_dir / "project-overview.md"
    task_breakdown_path = plan_dir / "task-breakdown.md"
    master_path = progress_dir / "MASTER.md"
    phase_path = progress_dir / f"phase-1-{phase_slug}.md"

    created: list[str] = []
    refreshed: list[str] = []
    skipped: list[str] = []

    files = [
        (project_overview_path, prepare_project_overview(task_name, task_description)),
        (task_breakdown_path, prepare_task_breakdown(task_name, phase_name)),
        (master_path, prepare_master(task_name, task_description, phase_specs)),
    ]
    phase_paths: list[str] = []
    for phase in phase_specs:
        current_phase_path = progress_dir / f"phase-{phase['index']}-{phase['slug']}.md"
        phase_paths.append(str(current_phase_path))
        files.append(
            (
                current_phase_path,
                prepare_phase(
                    phase_index=int(phase["index"]),
                    phase_name=str(phase["name"]),
                    goal=str(phase["goal"]),
                    task_title=str(phase["task_title"]),
                    acceptance=str(phase["acceptance"]),
                    effort=str(phase["effort"]),
                    resume_point=f"Start with Task {phase['index']}.1: {phase['task_title']}",
                ),
            )
        )

    for path, content in files:
        existed = path.exists()
        changed = write_text(path, content, force=force)
        if changed and existed:
            refreshed.append(str(path))
        elif changed:
            created.append(str(path))
        else:
            skipped.append(str(path))

    return {
        "root": str(root),
        "task_name": task_name,
        "task_description": task_description,
        "phase_name": phase_name,
        "phase_slug": phase_slug,
        "phase_count": len(phase_specs),
        "created": created,
        "refreshed": refreshed,
        "skipped": skipped,
        "resume_anchor": str(master_path),
        "artifacts": {
            "project_overview": str(project_overview_path),
            "task_breakdown": str(task_breakdown_path),
            "master": str(master_path),
            "phase": str(phase_path),
            "phase_files": phase_paths,
        },
        "phases": [
            {
                "index": phase["index"],
                "name": phase["name"],
                "slug": phase["slug"],
                "path": phase_paths[phase["index"] - 1],
                "goal": phase["goal"],
                "task_title": phase["task_title"],
            }
            for phase in phase_specs
        ],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Initialize pre-development planning artifacts.")
    parser.add_argument("--root", default=".", help="Project root for docs output")
    parser.add_argument("--task-name", default="<task-name>", help="Transformation task name")
    parser.add_argument("--task-description", default="<task-description>", help="Transformation summary")
    parser.add_argument("--phase-name", default="Foundation", help="Phase 1 display name")
    parser.add_argument("--force", action="store_true", help="Overwrite existing artifacts")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = initialize_pre_development_plan(
        root=Path(args.root).resolve(),
        task_name=args.task_name,
        task_description=args.task_description,
        phase_name=args.phase_name,
        force=bool(args.force),
    )
    if args.pretty:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(payload, ensure_ascii=False))


if __name__ == "__main__":
    main()
