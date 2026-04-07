#!/usr/bin/env python3
"""Generate a unified response pack from virtual-intelligent-dev-team routing output."""

from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
ROUTE_SCRIPT = SCRIPT_DIR / "route_request.py"
DEFAULT_CONFIG_PATH = SKILL_DIR / "references" / "routing-rules.json"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


route_request = load_module("virtual_team_generate_response_pack_route_request", ROUTE_SCRIPT)


def _bullet_list(items: list[str], empty_text: str) -> str:
    if not items:
        return f"- {empty_text}"
    return "\n".join(f"- {item}" for item in items)


def infer_template(result: dict[str, object]) -> str:
    if bool(result.get("needs_release_gate")):
        return "release"
    if bool(result.get("needs_pre_development_planning")):
        return "planning"
    if bool(result.get("needs_iteration")):
        return "iteration"
    if str(result.get("workflow_bundle")) == "audit-fix-deliver":
        return "review"
    return "default"


def infer_language(result: dict[str, object]) -> str:
    request_language = str(result.get("request_language", "")).lower()
    if request_language.startswith("zh"):
        return "zh"
    return "en"


def format_bool(value: object, language: str) -> str:
    truthy = bool(value)
    if language == "zh":
        return "是" if truthy else "否"
    return "yes" if truthy else "no"


def format_missing(value: object, language: str) -> str:
    text = str(value or "").strip()
    if text:
        return text
    return "无" if language == "zh" else "n/a"


def localize_workflow_reason(bundle: str, reason: str, language: str) -> str:
    if language != "zh":
        return reason
    translations = {
        "ship-hold-remediate": "当前请求明确以正式发布判断或验收为中心，应先走 release gate。",
        "plan-first-build": "当前请求属于重写、迁移或先规划后开发，应先产出 planning pack 和持久化进度锚点。",
        "root-cause-remediate": "当前请求需要基于证据做诊断或有边界迭代，应保留验证证据与回滚决策。",
        "audit-fix-deliver": "当前请求以审计或 review 为主，应先给出 findings，再决定修复与交付。",
        "direct-execution": "当前请求没有命中更强的流程旅程，保持轻量直执行即可。",
    }
    return translations.get(bundle, reason)


def localize_workflow_steps(bundle: str, steps: list[str], language: str) -> list[str]:
    if language != "zh":
        return steps
    translations = {
        "ship-hold-remediate": [
            "先运行正式 release gate",
            "基于明确证据回答 ship 或 hold",
            "如果是 hold，产出下一轮 remediation brief",
            "后续通过 release-gate 工件恢复，而不是从头重启",
        ],
        "plan-first-build": [
            "先锁定改造范围、目标和约束",
            "生成 planning pack",
            "创建或刷新进度锚点",
            "planning pack 建好后再回到正常交付路由",
        ],
        "root-cause-remediate": [
            "先冻结猜测并总结当前已知信息",
            "补齐缺失证据，或执行下一步验证性检查",
            "一次只验证一个 remediation 假设",
            "根据证据做 keep、retry、rollback 或 stop",
        ],
        "audit-fix-deliver": [
            "先给出 findings",
            "把 blocker 和后续优化项拆开",
            "定义最小且安全的修复动作",
            "只有在明确要求 commit、push 或 PR 时再进入 Git 交付",
        ],
        "direct-execution": [
            "保持路由轻量",
            "由当前主责执行最小下一步",
        ],
    }
    return translations.get(bundle, steps)


def explain_workflow_source(source: str, language: str) -> str:
    explanations = {
        "process-skill": {
            "en": "This bundle is activated by an explicit process skill, so it should be treated as the primary execution journey.",
            "zh": "这条 bundle 由显式 process skill 激活，应视为当前任务的主执行旅程。",
        },
        "keyword+lead": {
            "en": "This bundle is activated by the combination of task keywords and the selected lead, so it is evidence-backed but not purely process-driven.",
            "zh": "这条 bundle 由任务关键词和当前主责共同触发，有证据基础，但不是纯流程驱动。",
        },
        "lead+keyword": {
            "en": "This bundle is activated by both the selected lead and matching request keywords, so the journey is strongly anchored in task semantics.",
            "zh": "这条 bundle 同时由主责和请求关键词触发，因此和任务语义强绑定。",
        },
        "lead-default": {
            "en": "This bundle is activated mainly by the selected lead's default journey, so keep the route but do not overstate it as a hard process lane.",
            "zh": "这条 bundle 主要来自当前主责的默认旅程，可以沿用，但不要把它表述成强约束流程。",
        },
        "fallback": {
            "en": "This bundle is only a lightweight fallback and should not be treated as a strong process commitment.",
            "zh": "这条 bundle 只是轻量兜底，不应被表述成强流程承诺。",
        },
    }
    entry = explanations.get(source, {})
    if isinstance(entry, dict):
        return str(entry.get(language, entry.get("en", "")))
    return ""


def build_response_pack(
    result: dict[str, object],
    template: str = "auto",
    language: str = "auto",
) -> str:
    lead = str(result.get("lead_agent", "unknown"))
    assistants = result.get("assistant_agents", [])
    if not isinstance(assistants, list):
        assistants = []
    workflow_bundle = str(result.get("workflow_bundle", "direct-execution"))
    workflow_bundle_source = str(result.get("workflow_bundle_source", "unknown"))
    bundle_confidence = result.get("bundle_confidence", 0.0)
    workflow_reason = str(result.get("workflow_reason", ""))
    workflow_steps = result.get("workflow_steps", [])
    if not isinstance(workflow_steps, list):
        workflow_steps = []
    process_skills = result.get("process_skills", [])
    if not isinstance(process_skills, list):
        process_skills = []
    progress_anchor = result.get("progress_anchor_recommended")
    resume_artifacts = result.get("resume_artifacts", [])
    if not isinstance(resume_artifacts, list):
        resume_artifacts = []
    contract = result.get("assistant_delta_contract", {})
    if not isinstance(contract, dict):
        contract = {}
    governance = result.get("governance_plan", {})
    if not isinstance(governance, dict):
        governance = {}
    privy = governance.get("privy_council", {})
    if not isinstance(privy, dict):
        privy = {}
    git_profile = result.get("git_workflow_profile", {})
    if not isinstance(git_profile, dict):
        git_profile = {}
    templates = git_profile.get("templates", {})
    if not isinstance(templates, dict):
        templates = {}
    iteration_profile = result.get("iteration_profile", {})
    if not isinstance(iteration_profile, dict):
        iteration_profile = {}
    needs_planning = bool(result.get("needs_pre_development_planning"))
    needs_iteration = bool(result.get("needs_iteration"))
    selected_template = infer_template(result) if template == "auto" else template
    selected_language = infer_language(result) if language == "auto" else language
    localized_workflow_reason = localize_workflow_reason(
        workflow_bundle,
        workflow_reason,
        selected_language,
    )
    workflow_source_explanation = explain_workflow_source(
        workflow_bundle_source,
        selected_language,
    )
    localized_workflow_steps = localize_workflow_steps(
        workflow_bundle,
        [str(item) for item in workflow_steps],
        selected_language,
    )

    none_text = "无" if selected_language == "zh" else "none"
    not_required_text = "当前不需要" if selected_language == "zh" else "not required"
    direct_step_text = (
        "由当前主责执行最小下一步。"
        if selected_language == "zh"
        else "execute the next direct step under the lead."
    )
    assistant_contract_line = (
        f"- Assistant delta contract：必填字段 {', '.join(contract.get('required_fields', []))}。"
        if selected_language == "zh" and contract.get("enabled")
        else "- Assistant delta contract：当前不需要。"
        if selected_language == "zh"
        else f"- Assistant delta contract: required fields {', '.join(contract.get('required_fields', []))}."
        if contract.get("enabled")
        else "- Assistant delta contract: not required."
    )

    if selected_language == "zh":
        lines = [
            "## 团队派工",
            f"- 主责智能体：{lead}",
            f"- 协作智能体：{', '.join(assistants) if assistants else none_text}",
            f"- 工作流 bundle：{workflow_bundle}",
            f"- bundle 置信度：{bundle_confidence}（来源：{workflow_bundle_source}）",
            f"- 路由原因：{localized_workflow_reason or '详见路由结果。'}",
            f"- 工作流来源解释：{workflow_source_explanation or '当前没有额外来源解释。'}",
            "",
        ]
    else:
        lines = [
            "## Team Dispatch",
            f"- Lead agent: {lead}",
            f"- Assistant agents: {', '.join(assistants) if assistants else none_text}",
            f"- Workflow bundle: {workflow_bundle}",
            f"- Bundle confidence: {bundle_confidence} ({workflow_bundle_source})",
            f"- Why this route: {localized_workflow_reason or 'See router reasoning.'}",
            f"- Workflow source explanation: {workflow_source_explanation or 'No extra source explanation is available.'}",
            "",
        ]

    if selected_language == "zh":
        if selected_template == "review":
            lines.extend(
                [
                    "## 执行结论",
                    "- 关键结论：先出 review 结论，再进入修复与交付。",
                    f"- 关键决策：由 `{lead}` 持有最终审计判断。",
                    f"- 主要风险：{', '.join(process_skills) if process_skills else '行为回归与修复顺序失真'}。",
                ]
            )
        elif selected_template == "planning":
            lines.extend(
                [
                    "## 执行结论",
                    "- 关键结论：在 planning pack 建好之前，不进入实现阶段。",
                    f"- 关键决策：由 `{lead}` 负责范围收敛与规划闭环。",
                    f"- 主要风险：治理轨道 `{privy.get('selected_track', 'regular track')}`、缺少进度锚点、迁移范围收口不足。",
                ]
            )
        elif selected_template == "release":
            lines.extend(
                [
                    "## 执行结论",
                    "- 关键结论：先跑正式 release gate，再决定 ship 还是 hold。",
                    f"- 关键决策：由 `{lead}` 持有发版判断。",
                    f"- 主要风险：{', '.join(process_skills) if process_skills else '潜在 release blocker 还未被显式暴露'}。",
                ]
            )
        elif selected_template == "iteration":
            lines.extend(
                [
                    "## 执行结论",
                    "- 关键结论：保持在有边界的迭代环里，每轮只改一个变量。",
                    f"- 关键决策：由 `{lead}` 持有优化闭环的语义所有权。",
                    f"- 主要风险：证据不足、静默回归，以及超过 `{iteration_profile.get('round_cap_online', 0)}` 轮在线迭代后的 loop drift。",
                ]
            )
        else:
            lines.extend(
                [
                    "## 执行结论",
                    "- 关键结论：按当前主责与工作流 bundle 执行最小下一步。",
                    f"- 关键决策：保持 `{lead}` 为当前语义主责。",
                    f"- 主要风险：治理轨道 `{privy.get('selected_track', 'regular track')}`，流程技能 `{', '.join(process_skills) if process_skills else none_text}`。",
                ]
            )
    else:
        if selected_template == "review":
            lines.extend(
                [
                    "## Execution Result",
                    "- Key conclusion: review-first path with remediation after findings are clear.",
                    f"- Key decision: keep `{lead}` as owner of the review verdict.",
                    f"- Main risks: {', '.join(process_skills) if process_skills else 'behavioral regression and missing remediation sequencing'}.",
                ]
            )
        elif selected_template == "planning":
            lines.extend(
                [
                    "## Execution Result",
                    "- Key conclusion: do not jump into implementation before the planning pack exists.",
                    f"- Key decision: keep `{lead}` as owner of scope and planning closure.",
                    f"- Main risks: governance track `{privy.get('selected_track', 'regular track')}`, missing progress anchor, and under-scoped migration risks.",
                ]
            )
        elif selected_template == "release":
            lines.extend(
                [
                    "## Execution Result",
                    "- Key conclusion: run the formal release gate before making a ship decision.",
                    f"- Key decision: keep `{lead}` as release decision owner.",
                    f"- Main risks: {', '.join(process_skills) if process_skills else 'release blockers not yet surfaced'}.",
                ]
            )
        elif selected_template == "iteration":
            lines.extend(
                [
                    "## Execution Result",
                    "- Key conclusion: stay inside the bounded loop and change only one variable per round.",
                    f"- Key decision: keep `{lead}` as the semantic owner of the optimization loop.",
                    f"- Main risks: weak evidence, silent regression, and loop drift beyond `{iteration_profile.get('round_cap_online', 0)}` online rounds.",
                ]
            )
        else:
            lines.extend(
                [
                    "## Execution Result",
                    "- Key conclusion: Follow the selected workflow bundle under the current lead.",
                    f"- Key decision: Keep `{lead}` as semantic owner.",
                    f"- Main risks: governance track `{privy.get('selected_track', 'regular track')}`, process skills `{', '.join(process_skills) if process_skills else none_text}`.",
                ]
            )

    if selected_language == "zh":
        lines.extend(
            [
                "",
                "## 证据与约束",
                f"- 路由证据：{localized_workflow_reason or '详见路由结果。'}",
                f"- 工作流来源解释：{workflow_source_explanation or '当前没有额外来源解释。'}",
                f"- 流程技能：{', '.join(process_skills) if process_skills else none_text}",
                assistant_contract_line,
                "",
                "## 下一动作",
                f"- 最小可执行动作：{localized_workflow_steps[0] if localized_workflow_steps else direct_step_text}",
                f"- 当前主责：{lead}",
                "",
                "## 恢复信息",
                f"- 进度锚点：{progress_anchor or not_required_text}",
                "- 恢复工件：",
                _bullet_list([str(item) for item in resume_artifacts], none_text),
                "",
                "## Git 工作流",
                f"- using-git-worktrees：{format_bool(result.get('needs_worktree'), 'zh')}",
                f"- git-workflow：{format_bool(result.get('needs_git_workflow'), 'zh')}",
                f"- 建议分支：{format_missing(templates.get('branch_name', ''), 'zh')}",
                f"- 建议提交：{format_missing(templates.get('commit_message', ''), 'zh')}",
                f"- 建议 PR 标题：{format_missing(templates.get('pr_title', ''), 'zh')}",
                "",
                "## 治理信息",
                f"- 是否开启 roundtable：{format_bool(governance.get('roundtable_enabled'), 'zh')}",
                f"- 当前治理轨道：{privy.get('selected_track', 'regular track')}",
                f"- 风险等级：{governance.get('risk_level', 'unknown')}",
                f"- 是否需要双签：{format_bool(privy.get('dual_sign_required'), 'zh')}",
                "",
            ]
        )
    else:
        lines.extend(
            [
                "",
                "## Evidence",
                f"- Route evidence: {localized_workflow_reason or 'See router reasoning.'}",
                f"- Workflow source explanation: {workflow_source_explanation or 'No extra source explanation is available.'}",
                f"- Process skills: {', '.join(process_skills) if process_skills else none_text}",
                assistant_contract_line,
                "",
                "## Next Action",
                f"- Smallest executable action: {localized_workflow_steps[0] if localized_workflow_steps else direct_step_text}",
                f"- Current owner: {lead}",
                "",
                "## Resume",
                f"- Progress anchor: {progress_anchor or not_required_text}",
                "- Resume artifacts:",
                _bullet_list([str(item) for item in resume_artifacts], none_text),
                "",
                "## Git Workflow",
                f"- using-git-worktrees: {format_bool(result.get('needs_worktree'), 'en')}",
                f"- git-workflow: {format_bool(result.get('needs_git_workflow'), 'en')}",
                f"- Suggested branch: {format_missing(templates.get('branch_name', ''), 'en')}",
                f"- Suggested commit: {format_missing(templates.get('commit_message', ''), 'en')}",
                f"- Suggested PR title: {format_missing(templates.get('pr_title', ''), 'en')}",
                "",
                "## Governance",
                f"- Roundtable enabled: {format_bool(governance.get('roundtable_enabled'), 'en')}",
                f"- Selected governance track: {privy.get('selected_track', 'regular track')}",
                f"- Risk level: {governance.get('risk_level', 'unknown')}",
                f"- Dual-sign required: {format_bool(privy.get('dual_sign_required'), 'en')}",
                "",
            ]
        )

    if needs_planning:
        if selected_language == "zh":
            lines.extend(
                [
                    "## 规划包",
                    "- 已确认路径：先做轻量开发前规划，再进入实现。",
                    f"- 推荐锚点：{progress_anchor or 'docs/progress/MASTER.md'}",
                    "- 工作流步骤：",
                    _bullet_list(localized_workflow_steps, none_text),
                    "",
                ]
            )
        else:
            lines.extend(
                [
                    "## Planning Pack",
                    "- Confirmed path: lightweight pre-development planning before implementation.",
                    f"- Recommended anchor: {progress_anchor or 'docs/progress/MASTER.md'}",
                    "- Workflow steps:",
                    _bullet_list(localized_workflow_steps, none_text),
                    "",
                ]
            )

    if needs_iteration:
        if selected_language == "zh":
            lines.extend(
                [
                    "## 优化闭环",
                    f"- 当前模式：bounded iteration，在线上限 {iteration_profile.get('round_cap_online', 0)} 轮，离线上限 {iteration_profile.get('round_cap_offline', 0)} 轮。",
                    f"- 允许决策：{', '.join(iteration_profile.get('allowed_decisions', []))}",
                    f"- 当前恢复锚点：{progress_anchor or '.skill-iterations/current-round-memory.md'}",
                    "",
                ]
            )
        else:
            lines.extend(
                [
                    "## Optimization Loop",
                    f"- Objective mode: bounded iteration with online cap {iteration_profile.get('round_cap_online', 0)} and offline cap {iteration_profile.get('round_cap_offline', 0)}.",
                    f"- Allowed decisions: {', '.join(iteration_profile.get('allowed_decisions', []))}",
                    f"- Current resume anchor: {progress_anchor or '.skill-iterations/current-round-memory.md'}",
                    "",
                ]
            )

    return "\n".join(lines).rstrip() + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a unified response pack from router output.")
    parser.add_argument("--text", required=True, help="User request text.")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG_PATH), help="Path to routing config JSON.")
    parser.add_argument("--repo", default=".", help="Repository path for strategy detection.")
    parser.add_argument("--output", help="Optional markdown file path.")
    parser.add_argument(
        "--template",
        choices=["auto", "default", "review", "planning", "release", "iteration"],
        default="auto",
        help="Response pack template to use.",
    )
    parser.add_argument(
        "--language",
        choices=["auto", "en", "zh"],
        default="auto",
        help="Response pack language to use.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = route_request.load_config(Path(args.config).resolve())
    result = route_request.route_request(
        text=args.text,
        config=config,
        repo_path=Path(args.repo).resolve(),
    )
    markdown = build_response_pack(result, template=args.template, language=args.language)
    if args.output:
        output_path = Path(args.output).resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(markdown, encoding="utf-8")
    print(markdown, end="")


if __name__ == "__main__":
    main()
