#!/usr/bin/env python3
"""Generate a unified response pack from virtual-intelligent-dev-team routing output."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
ROUTE_SCRIPT = SCRIPT_DIR / "route_request.py"
RESPONSE_CONTRACT_SCRIPT = SCRIPT_DIR / "response_contract.py"
DEFAULT_CONFIG_PATH = SKILL_DIR / "references" / "routing-rules.json"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


route_request = load_module("virtual_team_generate_response_pack_route_request", ROUTE_SCRIPT)
response_contract = load_module("virtual_team_generate_response_pack_response_contract", RESPONSE_CONTRACT_SCRIPT)


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
    if str(result.get("workflow_bundle")) == "product-spec-deliver":
        return "product"
    if str(result.get("workflow_bundle")) == "govern-change-safely":
        return "governance"
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
        "product-spec-deliver": "当前请求以产品切片交付为主，应先锁定范围、用户流、验收标准和契约问题。",
        "govern-change-safely": "当前请求以技术治理和交付安全为主，应先明确执行模式、验证方式和回滚条件。",
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
        "product-spec-deliver": [
            "先锁定目标用户、目标结果和最小可接受范围",
            "写出核心用户流和关键失败状态",
            "把需求转成可验证的验收标准",
            "编码前先显式列出前后端契约问题",
        ],
        "govern-change-safely": [
            "先定义 owner、执行模式和停止条件",
            "锁定最小安全下一步",
            "写清验证证据和回滚条件",
            "确认 guardrail 后再进入 Git 或 release 动作",
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


def build_response_pack_payload(
    result: dict[str, object],
    template: str = "auto",
    language: str = "auto",
) -> dict[str, object]:
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
    bundle_bootstrap = result.get("workflow_bundle_bootstrap", {})
    if not isinstance(bundle_bootstrap, dict):
        bundle_bootstrap = {}
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
    assistant_contract_summary = (
        f"必填字段 {', '.join(contract.get('required_fields', []))}"
        if selected_language == "zh" and contract.get("enabled")
        else "当前不需要"
        if selected_language == "zh"
        else f"required fields {', '.join(contract.get('required_fields', []))}"
        if contract.get("enabled")
        else "not required"
    )

    if selected_language == "zh":
        if selected_template == "review":
            execution_result = {
                "key_conclusion": "先出 review 结论，再进入修复与交付。",
                "key_decision": f"由 `{lead}` 持有最终审计判断。",
                "main_risks": f"{', '.join(process_skills) if process_skills else '行为回归与修复顺序失真'}。",
            }
        elif selected_template == "planning":
            execution_result = {
                "key_conclusion": "在 planning pack 建好之前，不进入实现阶段。",
                "key_decision": f"由 `{lead}` 负责范围收敛与规划闭环。",
                "main_risks": f"治理轨道 `{privy.get('selected_track', 'regular track')}`、缺少进度锚点、迁移范围收口不足。",
            }
        elif selected_template == "release":
            execution_result = {
                "key_conclusion": "先跑正式 release gate，再决定 ship 还是 hold。",
                "key_decision": f"由 `{lead}` 持有发版判断。",
                "main_risks": f"{', '.join(process_skills) if process_skills else '潜在 release blocker 还未被显式暴露'}。",
            }
        elif selected_template == "iteration":
            execution_result = {
                "key_conclusion": "保持在有边界的迭代环里，每轮只改一个变量。",
                "key_decision": f"由 `{lead}` 持有优化闭环的语义所有权。",
                "main_risks": f"证据不足、静默回归，以及超过 `{iteration_profile.get('round_cap_online', 0)}` 轮在线迭代后的 loop drift。",
            }
        elif selected_template == "product":
            execution_result = {
                "key_conclusion": "先把产品切片写实，再进入实现。",
                "key_decision": f"由 `{lead}` 持有用户流、验收标准和契约问题的收口。",
                "main_risks": "范围漂移、验收标准失真，以及前后端契约遗漏。",
            }
        elif selected_template == "governance":
            execution_result = {
                "key_conclusion": "先收紧治理与回滚边界，再进入交付动作。",
                "key_decision": f"由 `{lead}` 持有执行模式、验证方式和回滚条件。",
                "main_risks": "跳过 guardrail、回滚条件不清、以及交付顺序失控。",
            }
        else:
            execution_result = {
                "key_conclusion": "按当前主责与工作流 bundle 执行最小下一步。",
                "key_decision": f"保持 `{lead}` 为当前语义主责。",
                "main_risks": f"治理轨道 `{privy.get('selected_track', 'regular track')}`，流程技能 `{', '.join(process_skills) if process_skills else none_text}`。",
            }
    else:
        if selected_template == "review":
            execution_result = {
                "key_conclusion": "review-first path with remediation after findings are clear.",
                "key_decision": f"keep `{lead}` as owner of the review verdict.",
                "main_risks": f"{', '.join(process_skills) if process_skills else 'behavioral regression and missing remediation sequencing'}.",
            }
        elif selected_template == "planning":
            execution_result = {
                "key_conclusion": "do not jump into implementation before the planning pack exists.",
                "key_decision": f"keep `{lead}` as owner of scope and planning closure.",
                "main_risks": f"governance track `{privy.get('selected_track', 'regular track')}`, missing progress anchor, and under-scoped migration risks.",
            }
        elif selected_template == "release":
            execution_result = {
                "key_conclusion": "run the formal release gate before making a ship decision.",
                "key_decision": f"keep `{lead}` as release decision owner.",
                "main_risks": f"{', '.join(process_skills) if process_skills else 'release blockers not yet surfaced'}.",
            }
        elif selected_template == "iteration":
            execution_result = {
                "key_conclusion": "stay inside the bounded loop and change only one variable per round.",
                "key_decision": f"keep `{lead}` as the semantic owner of the optimization loop.",
                "main_risks": f"weak evidence, silent regression, and loop drift beyond `{iteration_profile.get('round_cap_online', 0)}` online rounds.",
            }
        elif selected_template == "product":
            execution_result = {
                "key_conclusion": "lock the product slice before implementation drifts.",
                "key_decision": f"keep `{lead}` as owner of user flow, acceptance criteria, and contract closure.",
                "main_risks": "scope drift, vague acceptance criteria, and missed frontend/backend contract questions.",
            }
        elif selected_template == "governance":
            execution_result = {
                "key_conclusion": "tighten governance and rollback boundaries before delivery actions begin.",
                "key_decision": f"keep `{lead}` as owner of execution mode, verification, and rollback conditions.",
                "main_risks": "skipped guardrails, weak rollback conditions, and unsafe delivery sequencing.",
            }
        else:
            execution_result = {
                "key_conclusion": "Follow the selected workflow bundle under the current lead.",
                "key_decision": f"Keep `{lead}` as semantic owner.",
                "main_risks": f"governance track `{privy.get('selected_track', 'regular track')}`, process skills `{', '.join(process_skills) if process_skills else none_text}`.",
            }

    payload: dict[str, object] = {
        "schema_version": response_contract.SIDECAR_SCHEMA_VERSION,
        "language": selected_language,
        "template": selected_template,
        "team_dispatch": {
            "lead_agent": lead,
            "assistant_agents": assistants,
            "workflow_bundle": workflow_bundle,
            "bundle_confidence": bundle_confidence,
            "workflow_bundle_source": workflow_bundle_source,
            "route_reason": localized_workflow_reason or ("详见路由结果。" if selected_language == "zh" else "See router reasoning."),
            "workflow_source_explanation": workflow_source_explanation or ("当前没有额外来源解释。" if selected_language == "zh" else "No extra source explanation is available."),
        },
        "execution_result": execution_result,
        "evidence": {
            "route_evidence": localized_workflow_reason or ("详见路由结果。" if selected_language == "zh" else "See router reasoning."),
            "workflow_source_explanation": workflow_source_explanation or ("当前没有额外来源解释。" if selected_language == "zh" else "No extra source explanation is available."),
            "process_skills": process_skills,
            "assistant_delta_contract": {
                "enabled": bool(contract.get("enabled")),
                "summary": assistant_contract_summary,
            },
        },
        "next_action": {
            "smallest_executable_action": localized_workflow_steps[0] if localized_workflow_steps else direct_step_text,
            "current_owner": lead,
        },
        "resume": {
            "progress_anchor": progress_anchor or not_required_text,
            "resume_artifacts": [str(item) for item in resume_artifacts],
        },
        "git_workflow": {
            "using_git_worktrees": bool(result.get("needs_worktree")),
            "git_workflow": bool(result.get("needs_git_workflow")),
            "suggested_branch": format_missing(templates.get("branch_name", ""), selected_language),
            "suggested_commit": format_missing(templates.get("commit_message", ""), selected_language),
            "suggested_pr_title": format_missing(templates.get("pr_title", ""), selected_language),
        },
        "governance": {
            "roundtable_enabled": bool(governance.get("roundtable_enabled")),
            "selected_track": privy.get("selected_track", "regular track"),
            "risk_level": governance.get("risk_level", "unknown"),
            "dual_sign_required": bool(privy.get("dual_sign_required")),
        },
    }
    if bool(bundle_bootstrap.get("required")):
        payload["bundle_bootstrap"] = {
            "required": True,
            "reference": format_missing(bundle_bootstrap.get("reference", ""), selected_language),
            "commands": [str(item) for item in bundle_bootstrap.get("commands", []) if str(item).strip()],
            "artifacts": [str(item) for item in bundle_bootstrap.get("artifacts", []) if str(item).strip()],
            "resume_anchor": format_missing(bundle_bootstrap.get("resume_anchor", ""), selected_language),
        }
    if needs_planning:
        payload["planning_pack"] = {
            "recommended_anchor": progress_anchor or "docs/progress/MASTER.md",
            "workflow_steps": localized_workflow_steps,
        }
    if needs_iteration:
        payload["optimization_loop"] = {
            "round_cap_online": iteration_profile.get("round_cap_online", 0),
            "round_cap_offline": iteration_profile.get("round_cap_offline", 0),
            "allowed_decisions": iteration_profile.get("allowed_decisions", []),
            "resume_anchor": progress_anchor or ".skill-iterations/current-round-memory.md",
        }
    return payload


def build_response_pack(
    result: dict[str, object],
    template: str = "auto",
    language: str = "auto",
) -> str:
    payload = build_response_pack_payload(result, template=template, language=language)
    selected_language = str(payload["language"])
    team_dispatch = payload["team_dispatch"] if isinstance(payload.get("team_dispatch"), dict) else {}
    execution_result = payload["execution_result"] if isinstance(payload.get("execution_result"), dict) else {}
    evidence = payload["evidence"] if isinstance(payload.get("evidence"), dict) else {}
    next_action = payload["next_action"] if isinstance(payload.get("next_action"), dict) else {}
    resume = payload["resume"] if isinstance(payload.get("resume"), dict) else {}
    git_workflow = payload["git_workflow"] if isinstance(payload.get("git_workflow"), dict) else {}
    governance = payload["governance"] if isinstance(payload.get("governance"), dict) else {}
    planning_pack = payload["planning_pack"] if isinstance(payload.get("planning_pack"), dict) else None
    optimization_loop = payload["optimization_loop"] if isinstance(payload.get("optimization_loop"), dict) else None
    bundle_bootstrap = payload["bundle_bootstrap"] if isinstance(payload.get("bundle_bootstrap"), dict) else None
    none_text = "无" if selected_language == "zh" else "none"

    if selected_language == "zh":
        lines = [
            "## 团队派工",
            f"- 主责智能体：{team_dispatch.get('lead_agent', 'unknown')}",
            f"- 协作智能体：{', '.join(team_dispatch.get('assistant_agents', [])) if isinstance(team_dispatch.get('assistant_agents'), list) and team_dispatch.get('assistant_agents') else none_text}",
            f"- 工作流 bundle：{team_dispatch.get('workflow_bundle', 'direct-execution')}",
            f"- bundle 置信度：{team_dispatch.get('bundle_confidence', 0.0)}（来源：{team_dispatch.get('workflow_bundle_source', 'unknown')}）",
            f"- 路由原因：{team_dispatch.get('route_reason', '详见路由结果。')}",
            f"- 工作流来源解释：{team_dispatch.get('workflow_source_explanation', '当前没有额外来源解释。')}",
            "",
        ]
    else:
        lines = [
            "## Team Dispatch",
            f"- Lead agent: {team_dispatch.get('lead_agent', 'unknown')}",
            f"- Assistant agents: {', '.join(team_dispatch.get('assistant_agents', [])) if isinstance(team_dispatch.get('assistant_agents'), list) and team_dispatch.get('assistant_agents') else none_text}",
            f"- Workflow bundle: {team_dispatch.get('workflow_bundle', 'direct-execution')}",
            f"- Bundle confidence: {team_dispatch.get('bundle_confidence', 0.0)} ({team_dispatch.get('workflow_bundle_source', 'unknown')})",
            f"- Why this route: {team_dispatch.get('route_reason', 'See router reasoning.')}",
            f"- Workflow source explanation: {team_dispatch.get('workflow_source_explanation', 'No extra source explanation is available.')}",
            "",
        ]

    if selected_language == "zh":
        lines.extend(
            [
                "## 执行结论",
                f"- 关键结论：{execution_result.get('key_conclusion', '')}",
                f"- 关键决策：{execution_result.get('key_decision', '')}",
                f"- 主要风险：{execution_result.get('main_risks', '')}",
            ]
        )
    else:
        lines.extend(
            [
                "## Execution Result",
                f"- Key conclusion: {execution_result.get('key_conclusion', '')}",
                f"- Key decision: {execution_result.get('key_decision', '')}",
                f"- Main risks: {execution_result.get('main_risks', '')}",
            ]
        )

    if selected_language == "zh":
        lines.extend(
            [
                "",
                "## 证据与约束",
                f"- 路由证据：{evidence.get('route_evidence', '详见路由结果。')}",
                f"- 工作流来源解释：{evidence.get('workflow_source_explanation', '当前没有额外来源解释。')}",
                f"- 流程技能：{', '.join(evidence.get('process_skills', [])) if isinstance(evidence.get('process_skills'), list) and evidence.get('process_skills') else none_text}",
                f"- Assistant delta contract：{((evidence.get('assistant_delta_contract') or {}).get('summary', '当前不需要')) if isinstance(evidence.get('assistant_delta_contract'), dict) else '当前不需要'}",
                "",
                "## 下一动作",
                f"- 最小可执行动作：{next_action.get('smallest_executable_action', '')}",
                f"- 当前主责：{next_action.get('current_owner', 'unknown')}",
                "",
                "## 恢复信息",
                f"- 进度锚点：{resume.get('progress_anchor', '当前不需要')}",
                "- 恢复工件：",
                _bullet_list([str(item) for item in (resume.get('resume_artifacts', []) if isinstance(resume.get('resume_artifacts'), list) else [])], none_text),
                "",
                "## Git 工作流",
                f"- using-git-worktrees：{format_bool(git_workflow.get('using_git_worktrees'), selected_language)}",
                f"- git-workflow：{format_bool(git_workflow.get('git_workflow'), selected_language)}",
                f"- 建议分支：{git_workflow.get('suggested_branch', '无')}",
                f"- 建议提交：{git_workflow.get('suggested_commit', '无')}",
                f"- 建议 PR 标题：{git_workflow.get('suggested_pr_title', '无')}",
                "",
                "## 治理信息",
                f"- 是否开启 roundtable：{format_bool(governance.get('roundtable_enabled'), selected_language)}",
                f"- 当前治理轨道：{governance.get('selected_track', 'regular track')}",
                f"- 风险等级：{governance.get('risk_level', 'unknown')}",
                f"- 是否需要双签：{format_bool(governance.get('dual_sign_required'), selected_language)}",
                "",
            ]
        )
    else:
        lines.extend(
            [
                "",
                "## Evidence",
                f"- Route evidence: {evidence.get('route_evidence', 'See router reasoning.')}",
                f"- Workflow source explanation: {evidence.get('workflow_source_explanation', 'No extra source explanation is available.')}",
                f"- Process skills: {', '.join(evidence.get('process_skills', [])) if isinstance(evidence.get('process_skills'), list) and evidence.get('process_skills') else none_text}",
                f"- Assistant delta contract: {((evidence.get('assistant_delta_contract') or {}).get('summary', 'not required')) if isinstance(evidence.get('assistant_delta_contract'), dict) else 'not required'}",
                "",
                "## Next Action",
                f"- Smallest executable action: {next_action.get('smallest_executable_action', '')}",
                f"- Current owner: {next_action.get('current_owner', 'unknown')}",
                "",
                "## Resume",
                f"- Progress anchor: {resume.get('progress_anchor', 'not required')}",
                "- Resume artifacts:",
                _bullet_list([str(item) for item in (resume.get('resume_artifacts', []) if isinstance(resume.get('resume_artifacts'), list) else [])], none_text),
                "",
                "## Git Workflow",
                f"- using-git-worktrees: {format_bool(git_workflow.get('using_git_worktrees'), selected_language)}",
                f"- git-workflow: {format_bool(git_workflow.get('git_workflow'), selected_language)}",
                f"- Suggested branch: {git_workflow.get('suggested_branch', 'n/a')}",
                f"- Suggested commit: {git_workflow.get('suggested_commit', 'n/a')}",
                f"- Suggested PR title: {git_workflow.get('suggested_pr_title', 'n/a')}",
                "",
                "## Governance",
                f"- Roundtable enabled: {format_bool(governance.get('roundtable_enabled'), selected_language)}",
                f"- Selected governance track: {governance.get('selected_track', 'regular track')}",
                f"- Risk level: {governance.get('risk_level', 'unknown')}",
                f"- Dual-sign required: {format_bool(governance.get('dual_sign_required'), selected_language)}",
                "",
            ]
        )

    if isinstance(planning_pack, dict):
        if selected_language == "zh":
            lines.extend(
                [
                    "## 规划包",
                    "- 已确认路径：先做轻量开发前规划，再进入实现。",
                    f"- 推荐锚点：{planning_pack.get('recommended_anchor', 'docs/progress/MASTER.md')}",
                    "- 工作流步骤：",
                    _bullet_list([str(item) for item in (planning_pack.get('workflow_steps', []) if isinstance(planning_pack.get('workflow_steps'), list) else [])], none_text),
                    "",
                ]
            )
        else:
            lines.extend(
                [
                    "## Planning Pack",
                    "- Confirmed path: lightweight pre-development planning before implementation.",
                    f"- Recommended anchor: {planning_pack.get('recommended_anchor', 'docs/progress/MASTER.md')}",
                    "- Workflow steps:",
                    _bullet_list([str(item) for item in (planning_pack.get('workflow_steps', []) if isinstance(planning_pack.get('workflow_steps'), list) else [])], none_text),
                    "",
                ]
            )

    if isinstance(bundle_bootstrap, dict):
        if selected_language == "zh":
            lines.extend(
                [
                    "## Bundle 起盘",
                    f"- 是否需要初始化：{format_bool(bundle_bootstrap.get('required'), selected_language)}",
                    f"- 参考文档：{bundle_bootstrap.get('reference', '无')}",
                    f"- 恢复锚点：{bundle_bootstrap.get('resume_anchor', '无')}",
                    "- 初始化命令：",
                    _bullet_list([str(item) for item in bundle_bootstrap.get("commands", [])], none_text),
                    "- 初始化工件：",
                    _bullet_list([str(item) for item in bundle_bootstrap.get("artifacts", [])], none_text),
                    "",
                ]
            )
        else:
            lines.extend(
                [
                    "## Bundle Bootstrap",
                    f"- Initialization required: {format_bool(bundle_bootstrap.get('required'), selected_language)}",
                    f"- Reference: {bundle_bootstrap.get('reference', 'n/a')}",
                    f"- Resume anchor: {bundle_bootstrap.get('resume_anchor', 'n/a')}",
                    "- Commands:",
                    _bullet_list([str(item) for item in bundle_bootstrap.get("commands", [])], none_text),
                    "- Artifacts:",
                    _bullet_list([str(item) for item in bundle_bootstrap.get("artifacts", [])], none_text),
                    "",
                ]
            )

    if isinstance(optimization_loop, dict):
        if selected_language == "zh":
            lines.extend(
                [
                    "## 优化闭环",
                    f"- 当前模式：bounded iteration，在线上限 {optimization_loop.get('round_cap_online', 0)} 轮，离线上限 {optimization_loop.get('round_cap_offline', 0)} 轮。",
                    f"- 允许决策：{', '.join(optimization_loop.get('allowed_decisions', [])) if isinstance(optimization_loop.get('allowed_decisions'), list) else ''}",
                    f"- 当前恢复锚点：{optimization_loop.get('resume_anchor', '.skill-iterations/current-round-memory.md')}",
                    "",
                ]
            )
        else:
            lines.extend(
                [
                    "## Optimization Loop",
                    f"- Objective mode: bounded iteration with online cap {optimization_loop.get('round_cap_online', 0)} and offline cap {optimization_loop.get('round_cap_offline', 0)}.",
                    f"- Allowed decisions: {', '.join(optimization_loop.get('allowed_decisions', [])) if isinstance(optimization_loop.get('allowed_decisions'), list) else ''}",
                    f"- Current resume anchor: {optimization_loop.get('resume_anchor', '.skill-iterations/current-round-memory.md')}",
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
    parser.add_argument("--json-output", help="Optional JSON sidecar path.")
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
    payload = build_response_pack_payload(result, template=args.template, language=args.language)
    response_contract.validate_response_pack_payload(payload)
    markdown = build_response_pack(result, template=args.template, language=args.language)
    if args.output:
        output_path = Path(args.output).resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(markdown, encoding="utf-8")
        json_output = Path(args.json_output).resolve() if args.json_output else output_path.with_suffix(".json")
        json_output.parent.mkdir(parents=True, exist_ok=True)
        json_output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    elif args.json_output:
        json_output = Path(args.json_output).resolve()
        json_output.parent.mkdir(parents=True, exist_ok=True)
        json_output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(markdown, end="")


if __name__ == "__main__":
    main()
