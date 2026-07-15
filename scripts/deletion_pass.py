#!/usr/bin/env python3
"""deletion_pass.py — 审查 v5.9.0 新增文件的引用关系，辅助删除/合并决策。

本脚本是阶段3（v6.0.0）批次0 的工具，遵循 ponytail「先删后建」原则：
在新增任何文件前，先审查 v5.9.0 已有文件是否冗余、可合并或可删除。

工作方式：
1. 扫描 v5.9.0 新增的 11 个文件
2. 对每个文件，以文件名 stem 为关键词，在 skill 目录内搜索引用
3. 输出每个文件的 referenced_by 列表
4. 标记零引用文件为 deletion_candidate
5. 产出 JSON 和 markdown 报告

author: fxbin
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent

V590_NEW_FILES = [
    "references/complexity-ladder.md",
    "references/contract-lock-protocol.md",
    "references/failure-runbook.md",
    "references/hook-injection-protocol.md",
    "references/layer-reinforcement-protocol.md",
    "references/state-schema-spec.md",
    "references/verifier-extraction-guide.md",
    "references/workspace-journal-protocol.md",
    "assets/contract-spec-template.json",
    "assets/debt-ledger-template.json",
    "scripts/track_debt.py",
]

SEARCH_GLOBS = [
    "SKILL.md",
    "VERSION",
    "references/**/*",
    "scripts/*.py",
    "evals/*.json",
    "assets/**/*",
    "agents/*.yaml",
    "agents/*.yml",
]

DEFAULT_REPORT_PATH = SKILL_DIR / "deletion-pass-report.md"


def collect_search_files() -> list[Path]:
    """收集 skill 目录下所有需要搜索引用的文件"""
    files: list[Path] = []
    for pattern in SEARCH_GLOBS:
        for p in SKILL_DIR.glob(pattern):
            if p.is_file():
                files.append(p)
    return files


def find_references(target: Path, search_files: list[Path]) -> list[str]:
    """查找 target 文件被哪些其他文件引用

    以文件名 stem（不含扩展名）作为关键词做子串匹配。
    例如 complexity-ladder.md 的 stem 是 complexity-ladder，
    任何包含该子串的文件都算引用方。
    """
    stem = target.stem
    refs: list[str] = []
    for sf in search_files:
        if sf.resolve() == target.resolve():
            continue
        try:
            content = sf.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        if stem in content:
            refs.append(str(sf.relative_to(SKILL_DIR)))
    return sorted(refs)


def analyze_file(rel_path: str, search_files: list[Path]) -> dict[str, object]:
    """分析单个 v5.9.0 新增文件的引用关系"""
    target = SKILL_DIR / rel_path
    if not target.exists():
        return {
            "file": rel_path,
            "exists": False,
            "referenced_by": [],
            "reference_count": 0,
            "deletion_candidate": False,
            "note": "文件不存在",
        }
    refs = find_references(target, search_files)
    return {
        "file": rel_path,
        "exists": True,
        "stem": target.stem,
        "referenced_by": refs,
        "reference_count": len(refs),
        "deletion_candidate": len(refs) == 0,
    }


def render_markdown(results: list[dict[str, object]]) -> str:
    """渲染 markdown 报告"""
    total = len(results)
    candidates = sum(1 for r in results if r.get("deletion_candidate"))
    referenced = sum(1 for r in results if not r.get("deletion_candidate") and r.get("exists"))
    missing = sum(1 for r in results if not r.get("exists"))

    lines = [
        "# Deletion Pass 报告 — v5.9.0 新增文件引用分析",
        "",
        f"- 生成时间: {datetime.now().isoformat(timespec='seconds')}",
        f"- 审查文件数: {total}",
        f"- 可删除候选（零外部引用）: {candidates}",
        f"- 有引用文件: {referenced}",
        f"- 不存在文件: {missing}",
        "",
        "## 判读规则",
        "",
        "- `deletion_candidate: true` 表示该文件在 skill 内无任何外部引用，是删除/合并的首选对象",
        "- `reference_count` 为 0 或 1（仅被 SKILL.md 引用）的文件需重点审查是否冗余",
        "- 引用关系仅基于文件名 stem 子串匹配，最终删除决策需结合内容审查",
        "",
        "## 逐文件分析",
        "",
    ]

    for r in results:
        rel = r["file"]
        if not r.get("exists"):
            lines.append(f"### {rel}")
            lines.append(f"- 状态: {r.get('note', '不存在')}")
            lines.append("")
            continue

        count = r["reference_count"]
        is_candidate = r["deletion_candidate"]

        if is_candidate:
            status = "**可删除候选**（零外部引用）"
        elif count <= 1:
            status = f"低引用（{count} 处），需审查是否冗余"
        else:
            status = f"被 {count} 处引用"

        lines.append(f"### {rel}")
        lines.append(f"- 文件名关键词: `{r['stem']}`")
        lines.append(f"- 引用状态: {status}")
        if r["referenced_by"]:
            lines.append("- 被以下文件引用:")
            for ref in r["referenced_by"]:
                lines.append(f"  - `{ref}`")
        else:
            lines.append("- 被引用方: 无")
        lines.append("")

    lines.append("## 下一步")
    lines.append("")
    lines.append("1. 对 `deletion_candidate: true` 的文件，结合内容审查决定删除或合并")
    lines.append("2. 对低引用文件，检查是否与其他协议文件描述同一件事")
    lines.append("3. 删除/合并后运行 `quick_validate` 确认无 trace 断裂")
    lines.append("")

    return "\n".join(lines)


def main() -> None:
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description="审查 v5.9.0 新增文件引用关系，辅助删除/合并决策",
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="产出 markdown 报告到默认路径",
    )
    parser.add_argument(
        "--json-output",
        help="JSON 输出路径（默认输出到 stdout）",
    )
    parser.add_argument(
        "--md-output",
        help="markdown 输出路径（默认与 --report 配合使用）",
    )
    args = parser.parse_args()

    search_files = collect_search_files()
    results = [analyze_file(f, search_files) for f in V590_NEW_FILES]

    output = {
        "version": "deletion-pass/v1",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "files": results,
    }

    if args.json_output:
        Path(args.json_output).write_text(
            json.dumps(output, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    else:
        print(json.dumps(output, ensure_ascii=False, indent=2))

    if args.report or args.md_output:
        md = render_markdown(results)
        md_path = Path(args.md_output) if args.md_output else DEFAULT_REPORT_PATH
        md_path.write_text(md, encoding="utf-8")
        print(f"\n报告已写入: {md_path}")


if __name__ == "__main__":
    main()
