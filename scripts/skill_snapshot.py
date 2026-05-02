#!/usr/bin/env python3
"""Copy filtered virtual-intelligent-dev-team snapshots for tests and workflows."""

from __future__ import annotations

import shutil
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent

IGNORED_DIR_NAMES = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".tmp-offline-loop-drill",
    ".skill-iterations",
}
IGNORED_FILE_SUFFIXES = {".pyc"}
IGNORED_FILE_NAMES = {".DS_Store"}


def _should_ignore(relative_path: Path) -> bool:
    parts = relative_path.parts
    if any(part in IGNORED_DIR_NAMES for part in parts):
        return True
    if any(part.startswith(".tmp-") for part in parts):
        return True
    if parts[:2] == ("evals", "benchmark-results"):
        return True
    if parts[:2] == ("evals", "release-gate"):
        return True
    if relative_path.name in IGNORED_FILE_NAMES:
        return True
    if relative_path.suffix in IGNORED_FILE_SUFFIXES:
        return True
    return False


def build_snapshot_ignore(source_root: Path):
    source_root = source_root.resolve()

    def ignore(directory: str, names: list[str]) -> set[str]:
        current_dir = Path(directory).resolve()
        ignored: set[str] = set()
        for name in names:
            candidate = current_dir / name
            relative_path = candidate.relative_to(source_root)
            if _should_ignore(relative_path):
                ignored.add(name)
        return ignored

    return ignore


def copy_skill_snapshot(target_dir: Path, source_root: Path | None = None) -> Path:
    source = source_root.resolve() if source_root is not None else SKILL_DIR
    if target_dir.exists():
        shutil.rmtree(target_dir)
    shutil.copytree(source, target_dir, ignore=build_snapshot_ignore(source))
    return target_dir

