#!/usr/bin/env python3
"""Spec 自更新脚本:将 Verifier 发现的新 edge case 抽取为 spec 规则。

触发时机:Verifier 发现 spec_violation 但规范未覆盖,或路由误判,或重复踩坑。
安全网:Git 版本化 + check 守护 + 增量更新 + 可追溯。
"""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
DEFAULT_SPEC_FILE = SKILL_DIR / "references" / "routing-rules.json"
SPEC_UPDATE_LOG = SKILL_DIR / "references" / "spec-update-log.jsonl"
SUPPORTED_RULE_TYPES = [
    "priority_routing_rules",
    "assistant_routing_rules",
    "agent_rules",
    "process_skill_rules",
]


def load_spec(spec_path: Path) -> dict:
    """读取 spec 文件"""
    with open(spec_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_spec(spec_path: Path, spec: dict) -> None:
    """写入 spec 文件"""
    with open(spec_path, "w", encoding="utf-8") as f:
        json.dump(spec, f, ensure_ascii=False, indent=2)
        f.write("\n")


def append_update_log(
    log_path: Path,
    trigger_case: str,
    spec_file: str,
    rule_type: str,
    rule: dict,
    reason: str,
    commit_hash: str,
) -> None:
    """追加更新日志(JSONL 格式)"""
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "trigger_case": trigger_case,
        "spec_file": spec_file,
        "rule_type": rule_type,
        "rule": rule,
        "reason": reason,
        "commit_hash": commit_hash,
    }
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def get_git_hash() -> str:
    """获取当前 git commit hash"""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            cwd=SCRIPT_DIR,
        )
        return result.stdout.strip()[:12] if result.returncode == 0 else "unknown"
    except Exception:
        return "unknown"


def update_spec(
    spec_path: Path,
    rule_type: str,
    rule: dict,
    trigger_case: str,
    reason: str,
    dry_run: bool,
) -> dict:
    """执行 spec 更新"""
    spec = load_spec(spec_path)
    existing = spec.get(rule_type, [])
    if not isinstance(existing, list):
        return {"ok": False, "error": f"rule_type '{rule_type}' is not a list in spec"}

    before_len = len(existing)
    existing.append(rule)
    after_len = len(existing)

    diff = {
        "spec_file": str(spec_path.relative_to(SKILL_DIR)),
        "rule_type": rule_type,
        "rule_added": rule,
        "before_count": before_len,
        "after_count": after_len,
        "trigger_case": trigger_case,
        "reason": reason,
    }

    if dry_run:
        return {"ok": True, "dry_run": True, "diff": diff}

    save_spec(spec_path, spec)
    commit_hash = get_git_hash()
    append_update_log(
        SPEC_UPDATE_LOG,
        trigger_case,
        str(spec_path.relative_to(SKILL_DIR)),
        rule_type,
        rule,
        reason,
        commit_hash,
    )
    return {"ok": True, "dry_run": False, "diff": diff, "commit_hash": commit_hash}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Update spec with new rule.")
    parser.add_argument("--trigger-case", required=True, help="描述触发场景")
    parser.add_argument(
        "--spec-file",
        default=str(DEFAULT_SPEC_FILE),
        help="目标 spec 文件路径",
    )
    parser.add_argument(
        "--rule-type",
        required=True,
        choices=SUPPORTED_RULE_TYPES,
        help="规则类型",
    )
    parser.add_argument("--rule", required=True, help="JSON 格式的规则内容")
    parser.add_argument("--reason", required=True, help="更新理由")
    parser.add_argument("--dry-run", action="store_true", help="只输出 diff,不实际写入")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        rule = json.loads(args.rule)
    except json.JSONDecodeError as exc:
        print(json.dumps({"ok": False, "error": f"Invalid JSON in --rule: {exc}"}, ensure_ascii=False))
        raise SystemExit(2)

    result = update_spec(
        spec_path=Path(args.spec_file).resolve(),
        rule_type=args.rule_type,
        rule=rule,
        trigger_case=args.trigger_case,
        reason=args.reason,
        dry_run=args.dry_run,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result.get("ok") else 2)


if __name__ == "__main__":
    main()
