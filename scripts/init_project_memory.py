#!/usr/bin/env python3
"""Initialize lightweight project-memory anchors for virtual-intelligent-dev-team."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent


def copy_template(source: Path, target: Path, overwrite: bool) -> str:
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() and not overwrite:
        return "skipped"
    existed = target.exists()
    shutil.copyfile(source, target)
    return "updated" if existed else "created"


def init_project_memory(root: Path, mode: str = "all", overwrite: bool = False) -> dict[str, object]:
    actions: list[dict[str, str]] = []

    if mode in {"all", "planning"}:
        planning_source = SKILL_DIR / "assets" / "pre-development-progress-master-template.md"
        planning_target = root / "docs" / "progress" / "MASTER.md"
        result = copy_template(planning_source, planning_target, overwrite)
        actions.append(
            {
                "kind": "planning-anchor",
                "target": str(planning_target.relative_to(root)),
                "status": result,
            }
        )

    if mode in {"all", "iteration"}:
        iteration_specs = [
            (
                SKILL_DIR / "assets" / "round-memory-template.md",
                root / ".skill-iterations" / "current-round-memory.md",
                "iteration-anchor",
            ),
            (
                SKILL_DIR / "assets" / "distilled-patterns-template.md",
                root / ".skill-iterations" / "distilled-patterns.md",
                "pattern-anchor",
            ),
        ]
        for source, target, kind in iteration_specs:
            result = copy_template(source, target, overwrite)
            actions.append(
                {
                    "kind": kind,
                    "target": str(target.relative_to(root)),
                    "status": result,
                }
            )

    return {
        "ok": True,
        "root": str(root),
        "mode": mode,
        "overwrite": overwrite,
        "actions": actions,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Initialize project-memory-lite anchors.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument(
        "--mode",
        choices=["all", "planning", "iteration"],
        default="all",
        help="Which anchor set to initialize.",
    )
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing anchors.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = init_project_memory(
        root=Path(args.root).resolve(),
        mode=args.mode,
        overwrite=args.overwrite,
    )
    if args.pretty:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
