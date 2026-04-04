#!/usr/bin/env python3
"""Initialize lightweight pre-development planning artifacts."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = SKILL_DIR / "assets"
SAFE_SLUG = re.compile(r"[^a-z0-9]+")


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


def prepare_project_overview(task_name: str, task_description: str) -> str:
    content = read_text(ASSETS_DIR / "pre-development-project-overview-template.md")
    content = replace_line(content, "- Scope:", task_name)
    content = replace_line(content, "- Target state:", task_description)
    content = replace_line(content, "- Primary priority:", "maintainability")
    content = replace_line(content, "- Resume hint:", "Read docs/progress/MASTER.md first.")
    return content


def prepare_task_breakdown(task_name: str, phase_name: str) -> str:
    content = read_text(ASSETS_DIR / "pre-development-task-breakdown-template.md")
    content = content.replace("Phase 1: Foundation", f"Phase 1: {phase_name}")
    content = content.replace("Goal:\n", f"Goal:\nDeliver the first executable planning phase for {task_name}.\n", 1)
    content = content.replace("Prerequisite:\n", "Prerequisite:\nConfirmed transformation scope and constraints.\n", 1)
    content = content.replace("| P1-T1   |      | P0       | M      | --         |                     |", f"| P1-T1   | Confirm current-state architecture and migration constraints for {task_name} | P0       | M      | --         | Architecture, constraints, and risks are written down. |")
    content = replace_line(content, "- First executable task:", "Confirm current-state architecture and migration constraints.")
    return content


def prepare_master(task_name: str, task_description: str) -> str:
    today = datetime.now().date().isoformat()
    content = read_text(ASSETS_DIR / "pre-development-progress-master-template.md")
    content = replace_line(content, "- Name:", task_name)
    content = replace_line(content, "- Description:", task_description)
    content = replace_line(content, "- Started:", today)
    content = replace_line(content, "- Last updated:", today)
    content = replace_line(content, "- Active phase:", "Phase 1")
    content = replace_line(content, "- Active task:", "Confirm current-state architecture and migration constraints.")
    content = replace_line(content, "- Blockers:", "None")
    return content


def prepare_phase(phase_name: str) -> str:
    content = read_text(ASSETS_DIR / "pre-development-phase-template.md")
    content = content.replace("# Phase N: Name", f"# Phase 1: {phase_name}")
    content = content.replace("- [ ] Task N.1", "- [ ] Task 1.1: Confirm current-state architecture and migration constraints", 1)
    content = replace_line(content, "  - Priority:", "P0")
    content = replace_line(content, "  - Effort:", "M")
    content = replace_line(content, "  - Acceptance:", "Architecture, constraints, and major risks are written down.")
    content = replace_line(content, "  - Notes:", "_none yet_")
    return content


def initialize_pre_development_plan(
    root: Path,
    task_name: str,
    task_description: str,
    phase_name: str,
    *,
    force: bool = False,
) -> dict[str, object]:
    phase_slug = slugify(phase_name, default="foundation")
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
        (master_path, prepare_master(task_name, task_description)),
        (phase_path, prepare_phase(phase_name)),
    ]

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
        "created": created,
        "refreshed": refreshed,
        "skipped": skipped,
        "resume_anchor": str(master_path),
        "artifacts": {
            "project_overview": str(project_overview_path),
            "task_breakdown": str(task_breakdown_path),
            "master": str(master_path),
            "phase": str(phase_path),
        },
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
