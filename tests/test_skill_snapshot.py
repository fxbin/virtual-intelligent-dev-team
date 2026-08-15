from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "skill_snapshot.py"


def load_snapshot_module():
    spec = importlib.util.spec_from_file_location("skill_snapshot_test_module", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_release_gate_output_directories_are_ignored():
    snapshot = load_snapshot_module()
    assert snapshot._should_ignore(Path("evals/release-gate")) is True
    assert snapshot._should_ignore(Path("evals/release-gate-v61")) is True
    assert snapshot._should_ignore(Path("evals/release-gate-custom/offline-loop-drill")) is True


def test_unrelated_evals_directory_is_not_ignored():
    snapshot = load_snapshot_module()
    assert snapshot._should_ignore(Path("evals/manual-analysis")) is False
