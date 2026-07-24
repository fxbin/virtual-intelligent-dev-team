#!/usr/bin/env python3
"""Initialize quick-slice delivery anchors for virtual-intelligent-dev-team."""

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


def init_quick_slice(root: Path, overwrite: bool = False) -> dict[str, object]:
    specs = [
        (
            SKILL_DIR / "assets" / "quick-slice-brief-template.md",
            root / ".vidt/delivery" / "current-slice.md",
            "quick-slice-brief",
        ),
        (
            SKILL_DIR / "assets" / "delivery-status-template.yaml",
            root / ".vidt/delivery" / "status.yaml",
            "delivery-status",
        ),
    ]
    actions: list[dict[str, str]] = []
    for source, target, kind in specs:
        actions.append(
            {
                "kind": kind,
                "target": str(target.relative_to(root)),
                "status": copy_template(source, target, overwrite),
            }
        )
    return {
        "ok": True,
        "root": str(root),
        "overwrite": overwrite,
        "actions": actions,
        "resume_anchor": ".vidt/delivery/current-slice.md",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Initialize quick-slice delivery anchors.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing anchors.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = init_quick_slice(Path(args.root).resolve(), overwrite=args.overwrite)
    if args.pretty:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
