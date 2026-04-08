#!/usr/bin/env python3
"""Initialize product-delivery workspace anchors for virtual-intelligent-dev-team."""

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


def init_product_delivery(root: Path, overwrite: bool = False) -> dict[str, object]:
    specs = [
        (
            SKILL_DIR / "assets" / "product-delivery-brief-template.md",
            root / ".skill-product" / "current-slice.md",
            "product-slice",
        ),
        (
            SKILL_DIR / "assets" / "product-delivery-brief-template.md",
            root / ".skill-product" / "acceptance-criteria.md",
            "acceptance-criteria",
        ),
        (
            SKILL_DIR / "assets" / "product-contract-questions-template.md",
            root / ".skill-product" / "contract-questions.md",
            "contract-questions",
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
        "resume_anchor": ".skill-product/current-slice.md",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Initialize product-delivery workspace anchors.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing anchors.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = init_product_delivery(Path(args.root).resolve(), overwrite=args.overwrite)
    if args.pretty:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
