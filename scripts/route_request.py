#!/usr/bin/env python3
"""
Route a natural-language request to the most suitable agent team configuration.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta
import importlib.util
import json
import os
import re
import shlex
import subprocess
from pathlib import Path
from typing import Literal, TypedDict


SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_CONFIG_PATH = SCRIPT_DIR.parent / "references" / "routing-rules.json"
DECISION_LOG_PATH = ".vidt/metrics/decision-log.jsonl"
RESUME_FROM_AUTOMATION_STATE_SCRIPT = SCRIPT_DIR / "resume_from_automation_state.py"
ASCII_WORD_CLASS = "a-z0-9"
TRACK_REGULAR = "regular track"
TRACK_FAST = "fast track"
AUTO_TRIGGER_RE = re.compile(r"(?<!\S)/auto\b", re.IGNORECASE)
AUTO_RESERVED_TOKENS = ("setup", "go", "safe", "background", "resume")
AUTO_ELIGIBLE_WORKFLOWS = {
    "root-cause-remediate",
    "ship-hold-remediate",
    "post-release-close-loop",
}
QUALITY_GUARDRAIL_REFERENCE = "references/execution-quality-guardrails.md"
HARNESS_CONSTRAINT_REFERENCE = "references/harness-engineering-constraint-protocol.md"
TEAM_ENGINE_REFERENCE = "references/team-engine-lite-protocol.md"
WORKER_VERIFIER_REFERENCE = "references/worker-verifier-cycle-protocol.md"
EXTERNAL_AGENT_BACKEND_REFERENCE = "references/external-agent-backend-orchestration-protocol.md"
REAL_SUBAGENT_RUNTIME_REFERENCE = "references/real-subagent-runtime-protocol.md"
SHARED_LANGUAGE_REFERENCE = "references/shared-language-and-decision-capture.md"
FEEDBACK_LOOP_FIRST_REFERENCE = "references/feedback-loop-first-protocol.md"
VERTICAL_SLICE_REFERENCE = "references/vertical-slice-delivery-protocol.md"
SYSTEM_MAP_REFERENCE = "references/system-map-protocol.md"
ARCHITECTURE_DEEPENING_REFERENCE = "references/architecture-deepening-protocol.md"
CHANGE_LOCALIZATION_REFERENCE = "references/change-localization-protocol.md"
PROJECT_KNOWLEDGE_PYRAMID_REFERENCE = "references/project-knowledge-pyramid-protocol.md"
STAGE_COUNCIL_REFERENCE = "references/stage-council-protocol.md"
STAGE_COUNCIL_TEMPLATE = "assets/stage-council-plan-template.json"
HARNESS_CONSTRAINT_ARTIFACT = ".vidt/harness/engineering-constraints.md"
HARNESS_CONSTRAINT_COMMAND = "python scripts/init_harness_constraints.py --root . --summary \"<task summary>\" --pretty"
HARNESS_CONSTRAINT_WORKFLOWS = {
    "plan-first-build",
    "product-spec-deliver",
    "quick-slice-deliver",
    "audit-fix-deliver",
    "govern-change-safely",
    "root-cause-remediate",
}
TEAM_ENGINE_REQUIRED_WORKFLOWS = {
    "plan-first-build",
    "product-spec-deliver",
    "quick-slice-deliver",
    "audit-fix-deliver",
    "govern-change-safely",
    "root-cause-remediate",
    "ship-hold-remediate",
}
REAL_SUBAGENT_TRIGGER_KEYWORDS = [
    "multi-agent",
    "multi agent",
    "subagent",
    "sub-agent",
    "subagents",
    "sub-agents",
    "parallel agent",
    "parallel agents",
    "spawn agent",
    "spawn agents",
    "agent team",
    "agent teams",
    "separate agents",
    "dynamic workflow",
    "dynamic workflows",
    "claude code dynamic workflow",
    "多 agent",
    "多agent",
    "多智能体",
    "并行 agent",
    "并行agent",
    "并行智能体",
    "自主唤起",
    "唤起多",
    "分头执行",
    "分头查",
]
FUZZY_INTENT_KEYWORDS = [
    "idea",
    "hunch",
    "rough thought",
    "rough idea",
    "not sure",
    "maybe",
    "vague",
    "unclear",
    "worth doing",
    "what should i do",
    "figure out",
    "where to start",
    "direction",
    "模糊",
    "猜想",
    "想法",
    "不确定",
    "可能",
    "也许",
    "大概",
    "不知道",
    "该怎么办",
    "值不值得",
    "判断方向",
    "方向",
    "脑子里",
]
ROUTE_CHOICE_KEYWORDS = [
    "or",
    "whether",
    "which direction",
    "which path",
    "route",
    "choose",
    "decide",
    "confirm intent",
    "还是",
    "或者",
    "哪种",
    "哪个方向",
    "判断",
    "选择",
    "确认意图",
]
INTENT_CATEGORY_KEYWORDS = {
    "product-opportunity": [
        "product",
        "product strategy",
        "requirement",
        "requirements",
        "prd",
        "user",
        "market",
        "opportunity",
        "需求",
        "产品",
        "产品验证",
        "用户",
        "价值",
        "机会",
        "市场",
    ],
    "prototype-exploration": [
        "prototype",
        "mockup",
        "ux",
        "ui",
        "design",
        "high-fidelity",
        "原型",
        "设计",
        "交互",
        "高保真",
        "页面",
    ],
    "technical-feasibility": [
        "technical",
        "feasibility",
        "implementation",
        "build",
        "code",
        "技术",
        "可行性",
        "实现",
        "代码",
        "技术可行",
    ],
    "architecture-risk": [
        "architecture",
        "refactor",
        "migration",
        "risk",
        "core module",
        "架构",
        "重构",
        "迁移",
        "风险",
        "核心模块",
    ],
    "delivery-plan": [
        "plan",
        "delivery",
        "milestone",
        "roadmap",
        "break down",
        "计划",
        "交付",
        "拆解",
        "排期",
        "里程碑",
        "路线图",
    ],
}


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


automation_state_resumer = load_module(
    "virtual_team_route_request_resume_from_automation_state",
    RESUME_FROM_AUTOMATION_STATE_SCRIPT,
)


def load_config(config_path: Path) -> dict[str, object]:
    if not config_path.exists():
        raise FileNotFoundError(f"Routing config not found: {config_path}")

    with config_path.open("r", encoding="utf-8") as file:
        config = json.load(file)

    required_keys = ("thresholds", "agent_order", "agent_rules", "process_skill_rules")
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Routing config missing required key: {key}")
    return config


def get_threshold(config: dict[str, object], name: str, default: float) -> float:
    thresholds = config.get("thresholds", {})
    if not isinstance(thresholds, dict):
        return default
    value = thresholds.get(name, default)
    if isinstance(value, (int, float)):
        return float(value)
    return default


def has_cjk(text: str) -> bool:
    for char in text:
        if "\u4e00" <= char <= "\u9fff":
            return True
    return False


def keyword_matches(text: str, keyword: str) -> bool:
    token = keyword.lower().strip()
    if token == "":
        return False

    # Chinese or mixed Chinese keywords keep substring semantics.
    if has_cjk(token):
        return token in text

    # English keywords use word-boundary-like matching to avoid
    # false positives such as "pr" in "improve" or "ui" in "build".
    pattern = rf"(?<![{ASCII_WORD_CLASS}]){re.escape(token)}(?![{ASCII_WORD_CLASS}])"
    return re.search(pattern, text) is not None


def strip_auto_triggers(text: str) -> str:
    return str(detect_auto_mode(text).get("normalized_text", text)).strip()


def detect_auto_mode(text: str) -> dict[str, object]:
    match = AUTO_TRIGGER_RE.search(text)
    if match is None:
        return {
            "enabled": False,
            "trigger": "none",
            "requested_phase": "manual",
            "run_style": "foreground",
            "safety_level": "standard",
            "resume_requested": False,
            "detached_ready": False,
            "modifier_tokens": [],
            "normalized_text": text.strip(),
            "original_text": text,
        }

    before = text[: match.start()].strip()
    remainder = text[match.end() :]
    modifier_tokens: list[str] = []
    while True:
        token_match = re.match(r"\s*(setup|go|safe|background|resume)\b", remainder, re.IGNORECASE)
        if token_match is None:
            break
        modifier_tokens.append(str(token_match.group(1)).lower())
        remainder = remainder[token_match.end() :]

    normalized_text = " ".join(part for part in [before, remainder.strip()] if part)
    requested_phase = "go" if "go" in modifier_tokens else "setup"
    run_style = "background" if "background" in modifier_tokens else "foreground"
    safety_level = "safe" if "safe" in modifier_tokens else "standard"
    resume_requested = "resume" in modifier_tokens
    return {
        "enabled": True,
        "trigger": "/auto",
        "requested_phase": requested_phase,
        "run_style": run_style,
        "safety_level": safety_level,
        "resume_requested": resume_requested,
        "detached_ready": run_style == "background",
        "modifier_tokens": modifier_tokens,
        "normalized_text": normalized_text or text.strip(),
        "original_text": text,
    }


def compute_scores(
    text: str, config: dict[str, object]
) -> tuple[dict[str, int], dict[str, dict[str, list[str]]]]:
    lowered = text.lower()
    agent_order = config.get("agent_order", [])
    if not isinstance(agent_order, list):
        raise ValueError("routing config key 'agent_order' must be a list")

    agent_rules = config.get("agent_rules", {})
    if not isinstance(agent_rules, dict):
        raise ValueError("routing config key 'agent_rules' must be a map")

    max_score = int(get_threshold(config, "max_agent_score", 20))
    scores: dict[str, int] = {}
    hits: dict[str, dict[str, list[str]]] = {}

    for agent in agent_order:
        if not isinstance(agent, str):
            continue

        rules = agent_rules.get(agent, {})
        if not isinstance(rules, dict):
            rules = {}

        positive_rules = rules.get("positive", [])
        negative_rules = rules.get("negative", [])
        if not isinstance(positive_rules, list):
            positive_rules = []
        if not isinstance(negative_rules, list):
            negative_rules = []

        positive_hits: list[str] = []
        negative_hits: list[str] = []
        positive_score = 0
        negative_score = 0

        for item in positive_rules:
            if not isinstance(item, dict):
                continue
            keyword = str(item.get("keyword", "")).lower()
            rule_score = int(item.get("score", 0))
            if keyword and keyword_matches(lowered, keyword):
                positive_hits.append(keyword)
                positive_score += max(rule_score, 0)

        for item in negative_rules:
            if not isinstance(item, dict):
                continue
            keyword = str(item.get("keyword", "")).lower()
            penalty = abs(int(item.get("score", 0)))
            if keyword and keyword_matches(lowered, keyword):
                negative_hits.append(keyword)
                negative_score += penalty

        final_score = max(0, min(max_score, positive_score - negative_score))
        scores[agent] = final_score
        hits[agent] = {"positive": positive_hits, "negative": negative_hits}

    return scores, hits


def normalize_process_hit(hit: str) -> str:
    if hit.startswith("fallback:"):
        return hit.split(":", 1)[1]
    return hit


def is_git_review_context_only(text: str, git_hits: list[str]) -> bool:
    if len(git_hits) == 0:
        return False
    review_only_hits = {"pr", "mr", "pull request", "merge request", "拉取请求"}
    normalized_hits = {normalize_process_hit(hit) for hit in git_hits}
    if len(normalized_hits) == 0 or not normalized_hits.issubset(review_only_hits):
        return False

    lowered = text.lower()
    audit_context_keywords = [
        "review",
        "code review",
        "pr review",
        "security review",
        "审计",
        "代码审查",
        "安全检查",
        "漏洞",
    ]
    return any(keyword_matches(lowered, keyword.lower()) for keyword in audit_context_keywords)


def is_frontend_checkout_context(text: str, git_hits: list[str]) -> bool:
    if len(git_hits) == 0:
        return False
    normalized_hits = {normalize_process_hit(hit) for hit in git_hits}
    if normalized_hits != {"checkout"}:
        return False

    lowered = text.lower()
    frontend_context_keywords = [
        "ux",
        "ui",
        "accessibility",
        "a11y",
        "mobile",
        "responsive",
        "react",
        "tailwind",
        "design",
        "interaction",
        "dashboard",
        "page",
        "frontend",
        "front-end",
    ]
    return any(keyword_matches(lowered, keyword) for keyword in frontend_context_keywords)


def is_frontend_backend_contract_context(text: str) -> bool:
    """Keep product/UX ownership when a frontend flow also touches an API contract."""
    lowered = text.lower()
    frontend_cues = [
        "frontend",
        "front-end",
        "react",
        "next.js",
        "page",
        "dashboard",
        "form",
        "user flow",
        "login flow",
        "ui",
        "ux",
        "页面",
        "表单",
        "交互",
        "用户流",
        "前端",
    ]
    contract_cues = [
        "backend api",
        "api contract",
        "backend contract",
        "frontend-backend",
        "auth api",
        "error state",
        "后端 api",
        "api 契约",
        "接口契约",
        "后端接口",
        "接口失败",
        "联调",
    ]
    return any(keyword_matches(lowered, cue) for cue in frontend_cues) and any(
        keyword_matches(lowered, cue) for cue in contract_cues
    )


def is_domain_checkout_context(text: str, git_hits: list[str]) -> bool:
    if len(git_hits) == 0:
        return False
    normalized_hits = {normalize_process_hit(hit) for hit in git_hits}
    if "checkout" not in normalized_hits:
        return False

    lowered = text.lower()
    domain_keywords = [
        "api",
        "payment",
        "cart",
        "order",
        "form",
        "flow",
        "ux",
        "frontend",
        "backend",
        "regression test",
        "业务",
        "支付",
        "订单",
        "购物车",
        "结账",
        "接口",
    ]
    git_context_keywords = [
        "git checkout",
        "branch",
        "分支",
    ]
    return any(keyword_matches(lowered, keyword) for keyword in domain_keywords) and not any(
        keyword_matches(lowered, keyword) for keyword in git_context_keywords
    )


def is_release_readiness_context_only(
    git_hits: list[str], release_hits: list[str]
) -> bool:
    if len(git_hits) == 0 or len(release_hits) == 0:
        return False
    normalized_git_hits = {normalize_process_hit(hit) for hit in git_hits}
    ambiguous_release_submission_hits = {"submit", "提交", "release", "发版", "发布"}
    return len(normalized_git_hits) > 0 and normalized_git_hits.issubset(
        ambiguous_release_submission_hits
    )


def is_post_release_feedback_context(text: str) -> bool:
    lowered = text.lower()
    post_release_markers = [
        "post-release",
        "post release",
        "after launch",
        "after release",
        "already live",
        "release is already live",
        "rollout feedback",
        "production feedback",
        "customer feedback",
        "telemetry",
        "support",
        "user feedback",
        "monitor",
        "reopen iteration",
        "发布后",
        "上线后",
        "上线反馈",
        "用户反馈回流",
        "真实反馈",
        "生产反馈",
        "发布后复盘",
        "放量后",
        "灰度后",
    ]
    return any(keyword_matches(lowered, keyword) for keyword in post_release_markers)


def should_suppress_git_workflow(text: str, process_hits: dict[str, list[str]]) -> bool:
    git_hits = process_hits.get("git-workflow", [])
    release_hits = process_hits.get("release-gate", [])
    return (
        is_post_release_feedback_context(text)
        or
        is_git_review_context_only(text, git_hits)
        or is_frontend_checkout_context(text, git_hits)
        or is_domain_checkout_context(text, git_hits)
        or is_release_readiness_context_only(git_hits, release_hits)
    )


def should_suppress_bounded_iteration(text: str, process_hits: dict[str, list[str]]) -> bool:
    if is_post_release_feedback_context(text):
        return True
    iteration_hits = process_hits.get("bounded-iteration", [])
    release_hits = process_hits.get("release-gate", [])
    # Suppress bounded-iteration when the only signal is a generic "优化/optimize"
    # keyword and no other process skill (planning/release/git/iteration-loop markers)
    # is present. This keeps simple single-domain optimization questions on the
    # lightweight Direct Answer route instead of escalating them to a root-cause
    # iteration loop, per the skill's "keep routing lightweight for simple
    # single-domain tasks" rule.
    normalized_iteration_hits = {normalize_process_hit(hit) for hit in iteration_hits}
    if normalized_iteration_hits == {"优化"} or normalized_iteration_hits == {"optimize"}:
        loop_intent_markers = [
            "再来一轮",
            "下一轮",
            "until stable",
            "until it is stable",
            "迭代到稳定",
            "多轮",
            "multi-round",
            "max rounds",
            "最大轮次",
            "benchmark loop",
            "compare against baseline",
            "对比基线",
            "another round",
        ]
        lowered = text.lower()
        has_loop_intent = any(keyword_matches(lowered, marker) for marker in loop_intent_markers)
        other_process_active = any(
            key in process_hits
            for key in (
                "pre-development-planning",
                "release-gate",
                "git-workflow",
                "project-knowledge-capture",
                "using-git-worktrees",
            )
        )
        if not has_loop_intent and not other_process_active:
            return True
    if len(iteration_hits) == 0 or len(release_hits) == 0:
        lowered = text.lower()
        if normalized_iteration_hits.issubset({"regression", "回归"}):
            targeted_test_keywords = [
                "regression test",
                "regression tests",
                "run regression",
                "verify the regression",
                "回归测试",
                "跑回归",
            ]
            return any(keyword_matches(lowered, keyword) for keyword in targeted_test_keywords)
        return False
    weak_benchmark_reference_hits = {"benchmark", "基准"}
    return len(normalized_iteration_hits) > 0 and normalized_iteration_hits.issubset(
        weak_benchmark_reference_hits
    )


def should_suppress_worktree(text: str, process_hits: dict[str, list[str]]) -> bool:
    """Suppress explicit negation and generic planning-only worktree hits."""
    lowered = text.lower()
    explicit_negation_patterns = [
        r"\b(?:do not|don't|should not|must not|without)\s+(?:use|create|need)?\s*(?:a\s+)?worktree\b",
        r"(?:不使用|不要使用|无需|不需要|别用|不要建|不创建).{0,6}worktree",
        r"worktree.{0,6}(?:不使用|不要|无需|不需要)",
    ]
    if any(re.search(pattern, lowered, re.IGNORECASE) for pattern in explicit_negation_patterns):
        return True

    strong_worktree_intent = any(
        keyword_matches(lowered, marker)
        for marker in [
            "git worktree",
            "使用 worktree",
            "用 worktree",
            "创建 worktree",
            "worktree 隔离",
            "并行开发",
            "多分支并行",
            "同仓多任务",
        ]
    )
    read_only_patterns = [
        r"(?:不改代码|不要改代码|只评估|仅评估|只讨论|仅讨论)",
    ]
    if (
        not strong_worktree_intent
        and any(re.search(pattern, lowered, re.IGNORECASE) for pattern in read_only_patterns)
    ):
        return True

    worktree_hits = {
        normalize_process_hit(hit)
        for hit in process_hits.get("using-git-worktrees", [])
    }
    weak_hits = {"同时推进", "交替推进"}
    if worktree_hits and worktree_hits.issubset(weak_hits):
        isolation_anchors = [
            "worktree",
            "git",
            "仓库",
            "代码",
            "开发",
            "实现",
            "分支",
            "隔离",
            "并行开发",
            "互不干扰",
            "不影响主线",
        ]
        return not any(keyword_matches(lowered, anchor) for anchor in isolation_anchors)
    return False


def should_suppress_git_agent_scoring(
    git_reason_hits: list[str], needs_release_gate: bool, needs_git_workflow: bool
) -> bool:
    if not needs_release_gate or needs_git_workflow or len(git_reason_hits) == 0:
        return False
    normalized_hits = {normalize_process_hit(hit) for hit in git_reason_hits}
    ambiguous_release_decision_hits = {"提交", "release", "发版", "发布"}
    return len(normalized_hits) > 0 and normalized_hits.issubset(
        ambiguous_release_decision_hits
    )


def is_simple_direct_answer_request(text: str, lead_agent: str) -> bool:
    lowered = text.lower()
    if lead_agent not in {"Technical Trinity", "World-Class Product Architect"}:
        return False
    if is_quick_slice_context(text):
        return False

    direct_answer_cues = [
        "怎么",
        "如何",
        "怎么优化",
        "如何优化",
        "怎么提升",
        "如何提升",
        "how to",
        "how do i",
        "what is the best way",
        "recommend",
        "?",
        "？",
    ]
    single_domain_subjects = [
        "前端",
        "页面",
        "react",
        "next.js",
        "css",
        "性能",
        "加载",
        "打包",
        "bundle",
        "bug",
        "报错",
        "error",
        "接口慢",
        "api slow",
        "优化",
        "performance",
    ]
    escalation_markers = [
        "实现",
        "开发",
        "重做",
        "改造",
        "重构",
        "迁移",
        "规划",
        "计划",
        "方案",
        "prd",
        "验收",
        "用户流",
        "backend contract",
        "api contract",
        "commit",
        "push",
        "pull request",
        "merge",
        "release",
        "发布",
        "上线",
        "内测",
        "多轮",
        "下一轮",
        "全面",
        "跨域",
        "多域",
        "系统",
        "项目",
        "架构",
        "安全",
        "审计",
    ]

    return (
        text_has_any_keyword(lowered, direct_answer_cues)
        and text_has_any_keyword(lowered, single_domain_subjects)
        and not text_has_any_keyword(lowered, escalation_markers)
    )


def detect_process_skills(
    text: str, config: dict[str, object]
) -> tuple[bool, bool, bool, bool, bool, bool, list[str], dict[str, list[str]]]:
    lowered = text.lower()
    process_rules = config.get("process_skill_rules", {})
    if not isinstance(process_rules, dict):
        raise ValueError("routing config key 'process_skill_rules' must be a map")

    process_hits: dict[str, list[str]] = {}
    for skill_name, rules in process_rules.items():
        if not isinstance(skill_name, str) or not isinstance(rules, list):
            continue
        for rule in rules:
            if not isinstance(rule, dict):
                continue
            keyword = str(rule.get("keyword", "")).lower()
            if keyword and keyword_matches(lowered, keyword):
                process_hits.setdefault(skill_name, []).append(keyword)

    # Fallback: infer git workflow intent from common command-like expressions,
    # even when explicit process keywords are not provided.
    if "git-workflow" not in process_hits:
        git_anchor = keyword_matches(lowered, "git")
        git_action_keywords = [
            "commit",
            "push",
            "branch",
            "checkout",
            "merge",
            "rebase",
            "tag",
            "pull request",
            "merge request",
            "pr",
            "mr",
            "提交",
            "推送",
            "分支",
            "合并",
            "拉取请求",
        ]
        action_hits = [
            keyword for keyword in git_action_keywords if keyword_matches(lowered, keyword)
        ]
        strong_action_count = len(set(action_hits))
        if (git_anchor and strong_action_count > 0) or strong_action_count >= 2:
            process_hits["git-workflow"] = [
                f"fallback:{keyword}" for keyword in sorted(set(action_hits))
            ]

    if should_suppress_git_workflow(text, process_hits):
        process_hits.pop("git-workflow", None)
    if should_suppress_bounded_iteration(text, process_hits):
        process_hits.pop("bounded-iteration", None)
    if should_suppress_worktree(text, process_hits):
        process_hits.pop("using-git-worktrees", None)

    needs_pre_development_planning = "pre-development-planning" in process_hits
    needs_iteration = "bounded-iteration" in process_hits
    needs_project_knowledge_capture = "project-knowledge-capture" in process_hits
    needs_worktree = "using-git-worktrees" in process_hits
    needs_release_gate = "release-gate" in process_hits
    needs_git_workflow = "git-workflow" in process_hits
    process_skills = [
        skill
        for skill in (
            "pre-development-planning",
            "bounded-iteration",
            "project-knowledge-capture",
            "using-git-worktrees",
            "release-gate",
            "git-workflow",
        )
        if skill in process_hits
    ]
    return (
        needs_pre_development_planning,
        needs_iteration,
        needs_project_knowledge_capture,
        needs_worktree,
        needs_release_gate,
        needs_git_workflow,
        process_skills,
        process_hits,
    )


def detect_languages(
    text: str, config: dict[str, object]
) -> tuple[list[str], dict[str, list[str]], dict[str, str]]:
    lowered = text.lower()
    profiles = config.get("language_profiles", {})
    if not isinstance(profiles, dict):
        return [], {}, {}

    language_hits: dict[str, list[str]] = {}
    language_routing: dict[str, str] = {}

    for language, profile in profiles.items():
        if not isinstance(language, str) or not isinstance(profile, dict):
            continue
        keywords = profile.get("keywords", [])
        context_keywords = profile.get("context_keywords", [])
        bare_keyword = profile.get("bare_keyword")
        if not isinstance(keywords, list):
            continue
        if not isinstance(context_keywords, list):
            context_keywords = []
        if not isinstance(bare_keyword, str):
            bare_keyword = ""
        hits: list[str] = []
        for keyword in keywords:
            if not isinstance(keyword, str):
                continue
            token = keyword.lower()
            if token and keyword_matches(lowered, token):
                hits.append(token)

        # Optional bare language word with context constraint.
        if bare_keyword:
            bare = bare_keyword.lower()
            if keyword_matches(lowered, bare):
                context_hits = []
                for ctx in context_keywords:
                    if not isinstance(ctx, str):
                        continue
                    ctx_token = ctx.lower()
                    if ctx_token and keyword_matches(lowered, ctx_token):
                        context_hits.append(ctx_token)
                if len(context_hits) > 0:
                    hits.append(bare)
                    hits.extend([f"context:{ctx}" for ctx in context_hits])
        if hits:
            language_hits[language] = hits
            lead_agent = str(profile.get("lead_agent", "Technical Trinity"))
            language_routing[language] = lead_agent

    detected_languages = list(language_hits.keys())
    return detected_languages, language_hits, language_routing


def detect_repo_strategy(repo_path: Path) -> dict[str, str]:
    default = {"strategy": "unknown", "base_branch": "main"}
    cmd = [
        "git",
        "-C",
        str(repo_path),
        "for-each-ref",
        "--format=%(refname:short)",
        "refs/heads",
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    except Exception:
        return default
    if proc.returncode != 0:
        return default

    branches = {line.strip() for line in (proc.stdout or "").splitlines() if line.strip()}
    has_main = "main" in branches
    has_master = "master" in branches
    has_develop = "develop" in branches

    if has_develop and (has_main or has_master):
        return {"strategy": "git-flow-lite", "base_branch": "main" if has_main else "master"}
    if has_main:
        return {"strategy": "trunk-main", "base_branch": "main"}
    if has_master:
        return {"strategy": "trunk-master", "base_branch": "master"}
    if has_develop:
        return {"strategy": "develop-only", "base_branch": "develop"}
    return default


def resolve_repository_roots(repo_path: Path) -> dict[str, object]:
    """Resolve the main worktree (state-root) and current checkout (execution-root)."""
    execution_root = repo_path.resolve()
    state_root = execution_root
    resolution = "fallback-execution-root"
    try:
        proc = subprocess.run(
            ["git", "-C", str(execution_root), "worktree", "list", "--porcelain", "-z"],
            capture_output=True,
            check=False,
        )
        if proc.returncode == 0:
            for record in (proc.stdout or b"").split(b"\0"):
                if record.startswith(b"worktree "):
                    candidate = Path(os.fsdecode(record.removeprefix(b"worktree "))).resolve()
                    if candidate.exists():
                        state_root = candidate
                        resolution = "git-worktree-list"
                    break
    except (OSError, ValueError):
        pass
    return {
        "state_root": str(state_root),
        "execution_root": str(execution_root),
        "separated": state_root != execution_root,
        "resolution": resolution,
    }


def build_git_templates(repo_strategy: dict[str, str]) -> dict[str, object]:
    strategy = repo_strategy.get("strategy", "unknown")
    base_branch = repo_strategy.get("base_branch", "main")
    branch_prefix = "feature" if strategy == "git-flow-lite" else "feat"
    return {
        "branch_name": f"{branch_prefix}/<ticket>-<summary>",
        "commit_message": "fix: 修复 <模块> 的 <问题>",
        "pr_title": "fix: <模块> - <变更摘要>",
        "pr_sections": ["背景", "改动点", "风险与回滚", "验证结果"],
        "base_branch": base_branch,
    }


def build_auto_execute_policy() -> dict[str, str]:
    return {
        "low_risk": "auto_execute",
        "medium_risk": "confirm_before_execute",
        "high_risk": "must_confirm_and_explain_risk",
    }


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def ensure_list_str(value: object, default: list[str]) -> list[str]:
    if not isinstance(value, list):
        return default
    result: list[str] = []
    for item in value:
        if isinstance(item, str):
            result.append(item)
    return result if len(result) > 0 else default


def build_iteration_profile(config: dict[str, object], enabled: bool) -> dict[str, object]:
    governance = config.get("governance", {})
    if not isinstance(governance, dict):
        governance = {}
    iteration_control = governance.get("iteration_control", {})
    if not isinstance(iteration_control, dict):
        iteration_control = {}

    required_artifacts = ensure_list_str(
        iteration_control.get("required_artifacts"),
        [
            "assets/iteration-ledger-template.md",
            "assets/round-reflection-template.md",
            "assets/round-memory-template.md",
            "assets/self-feedback-template.md",
            "assets/distilled-patterns-template.md",
        ],
    )
    allowed_decisions = ensure_list_str(
        iteration_control.get("allowed_decisions"),
        ["keep", "retry", "rollback", "stop"],
    )

    return {
        "enabled": enabled,
        "round_cap_online": max(int(iteration_control.get("default_online_round_cap", 3)), 1),
        "round_cap_offline": max(int(iteration_control.get("default_offline_round_cap", 120)), 1),
        "max_same_hypothesis_retries": max(
            int(iteration_control.get("max_same_hypothesis_retries", 2)), 1
        ),
        "require_objective_signal": bool(
            iteration_control.get("require_objective_signal", True)
        ),
        "allowed_decisions": allowed_decisions,
        "required_artifacts": required_artifacts,
    }


def keyword_hits(text: str, keywords: list[str]) -> list[str]:
    lowered = text.lower()
    hits: list[str] = []
    for keyword in keywords:
        token = keyword.lower().strip()
        if token != "" and keyword_matches(lowered, token):
            hits.append(keyword)
    return hits


def is_audit_batch_fix_context(text: str) -> bool:
    """Detect explicit code-audit findings that must be fixed in separate batches."""
    lowered = text.lower()

    def has_any(keywords: list[str]) -> bool:
        return any(
            keyword.lower() in lowered or keyword_matches(lowered, keyword)
            for keyword in keywords
        )

    audit_hits = [
        "audit",
        "review",
        "code review",
        "pr review",
        "security review",
        "finding",
        "findings",
        "审查",
        "审计",
        "代码审查",
        "发现",
        "审查完成",
    ]
    severity_hits = [
        "p0",
        "p1",
        "p2",
        "p0/p1/p2",
        "severity",
        "严重级别",
        "分级",
        "优先级",
    ]
    batch_hits = [
        "batch",
        "batches",
        "separate",
        "separate commit",
        "separate commits",
        "each commit",
        "分批",
        "逐批",
        "每批",
        "独立",
        "单独",
    ]
    fix_hits = ["fix", "remediate", "修复", "整改", "处理"]
    commit_hits = ["commit", "提交"]
    return (
        has_any(audit_hits)
        and has_any(severity_hits)
        and has_any(batch_hits)
        and has_any(fix_hits)
        and has_any(commit_hits)
    )


def detect_priority_lead(text: str, config: dict[str, object]) -> dict[str, object] | None:
    lowered = text.lower()
    rules = config.get("priority_routing_rules", [])
    if not isinstance(rules, list):
        return None

    for rule in rules:
        if not isinstance(rule, dict):
            continue

        agent = str(rule.get("agent", "")).strip()
        any_keywords = ensure_list_str(rule.get("any_keywords"), [])
        all_keywords = ensure_list_str(rule.get("all_keywords"), [])
        exclude_keywords = ensure_list_str(rule.get("exclude_if_any_keywords"), [])
        if agent == "" or (len(any_keywords) == 0 and len(all_keywords) == 0):
            continue

        any_hits = [keyword for keyword in any_keywords if keyword_matches(lowered, keyword.lower())]
        all_hits = [keyword for keyword in all_keywords if keyword_matches(lowered, keyword.lower())]
        exclude_hits = [
            keyword for keyword in exclude_keywords if keyword_matches(lowered, keyword.lower())
        ]

        if len(all_keywords) > 0 and len(all_hits) != len(all_keywords):
            continue
        if len(any_keywords) > 0 and len(any_hits) == 0:
            continue
        if agent == "Git Workflow Guardian" and (
            is_frontend_checkout_context(text, any_hits + all_hits)
            or is_domain_checkout_context(text, any_hits + all_hits)
            or is_post_release_feedback_context(text)
        ):
            continue
        if len(exclude_hits) > 0:
            continue

        return {
            "agent": agent,
            "matched_keywords": dedupe_agents(any_hits + all_hits),
        }
    return None


def parse_iso_time(value: str) -> datetime | None:
    try:
        return datetime.fromisoformat(value)
    except Exception:
        return None


def load_decision_log_entries(repo_path: Path) -> list[dict[str, object]]:
    file_path = repo_path / DECISION_LOG_PATH
    if not file_path.exists():
        return []
    events: list[dict[str, object]] = []
    try:
        with file_path.open("r", encoding="utf-8") as file:
            for line in file:
                raw = line.strip()
                if raw == "":
                    continue
                try:
                    item = json.loads(raw)
                except json.JSONDecodeError:
                    continue
                if isinstance(item, dict):
                    events.append(item)
    except Exception:
        return []
    return events


def append_decision_log_entry(
    repo_path: Path,
    payload: dict[str, object],
    *,
    decision: str | None = None,
    verifier: str | None = None,
    reason: str | None = None,
    evidence: str | None = None,
) -> None:
    """Append one canonical entry to `.vidt/metrics/decision-log.jsonl`."""
    file_path = repo_path / DECISION_LOG_PATH
    file_path.parent.mkdir(parents=True, exist_ok=True)
    enriched: dict[str, object] = dict(payload)
    if decision is not None:
        enriched["decision"] = decision
    if verifier is not None:
        enriched["verifier"] = verifier
    if reason is not None:
        enriched["reason"] = reason
    if evidence is not None:
        enriched["evidence"] = evidence
    with file_path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(enriched, ensure_ascii=False) + "\n")


def get_fast_track_stats(
    repo_path: Path,
    window_hours: int,
) -> dict[str, object]:
    now = datetime.now()
    events = load_decision_log_entries(repo_path)
    window_start = now - timedelta(hours=max(window_hours, 1))

    count_24h = 0
    latest_fast_track: datetime | None = None
    for event in events:
        timestamp = event.get("timestamp")
        track = event.get("selected_track")
        if not isinstance(timestamp, str) or not isinstance(track, str):
            continue
        dt = parse_iso_time(timestamp)
        if dt is None:
            continue
        if track != TRACK_FAST:
            continue
        if dt >= window_start:
            count_24h += 1
        if latest_fast_track is None or dt > latest_fast_track:
            latest_fast_track = dt

    return {
        "count_in_window": count_24h,
        "window_hours": max(window_hours, 1),
        "latest_fast_track_at": latest_fast_track.isoformat(timespec="seconds")
        if latest_fast_track is not None
        else None,
    }


def get_governance_defaults(config: dict[str, object]) -> dict[str, object]:
    governance = config.get("governance", {})
    if not isinstance(governance, dict):
        governance = {}
    roundtable = governance.get("roundtable", {})
    if not isinstance(roundtable, dict):
        roundtable = {}
    privy_council = governance.get("privy_council", {})
    if not isinstance(privy_council, dict):
        privy_council = {}
    anti_gaming = governance.get("anti_gaming", {})
    if not isinstance(anti_gaming, dict):
        anti_gaming = {}
    fast_track_control = governance.get("fast_track_control", {})
    if not isinstance(fast_track_control, dict):
        fast_track_control = {}
    execution_control = governance.get("execution_control", {})
    if not isinstance(execution_control, dict):
        execution_control = {}
    audit_control = governance.get("audit_control", {})
    if not isinstance(audit_control, dict):
        audit_control = {}

    defaults = {
        "assistant_count_min": 1,
        "confidence_max": 0.75,
        "force_keywords": [
            "圆桌会议",
            "多智能体治理",
            "cross-functional",
            "governance",
            "roundtable governance",
            "regular governance",
        ],
    }
    privy_defaults = {
        "prefer_regular_for_git": True,
        "allow_high_risk_fast_track": False,
        "force_fast_track_keywords": ["紧急", "立即", "阻塞", "P0", "hotfix", "实验性", "快速验证"],
        "force_regular_keywords": ["审计", "合规", "高风险", "核心模块", "双签"],
    }
    anti_defaults = {
        "min_objective_signals_for_fast_track": 1,
        "urgent_keywords": ["紧急", "立即", "阻塞", "P0", "hotfix", "实验性", "快速验证"],
        "objective_keywords": ["生产故障", "告警", "失败", "回滚", "error", "exception", "500", "timeout"],
    }
    fast_control_defaults = {
        "quota_per_24h": 3,
        "cooldown_minutes": 30,
        "window_hours": 24,
        "write_event_log": True,
    }
    execution_defaults = {
        "require_dri": True,
        "slo_minutes": {"low": 120, "medium": 60, "high": 30},
    }
    audit_defaults = {
        "archive_levels": ["draft", "verified", "gold"],
        "default_archive_level": "draft",
        "promotion_rules": [
            "双签通过后可从 draft 提升到 verified",
            "连续稳定达标后可从 verified 提升到 gold",
        ],
    }

    return {
        "roundtable": {
            "assistant_count_min": int(roundtable.get("assistant_count_min", defaults["assistant_count_min"])),
            "confidence_max": float(roundtable.get("confidence_max", defaults["confidence_max"])),
            "force_keywords": ensure_list_str(roundtable.get("force_keywords"), defaults["force_keywords"]),
        },
        "privy_council": {
            "prefer_regular_for_git": bool(
                privy_council.get("prefer_regular_for_git", privy_defaults["prefer_regular_for_git"])
            ),
            "allow_high_risk_fast_track": bool(
                privy_council.get(
                    "allow_high_risk_fast_track",
                    privy_defaults["allow_high_risk_fast_track"],
                )
            ),
            "force_fast_track_keywords": ensure_list_str(
                privy_council.get("force_fast_track_keywords"),
                privy_defaults["force_fast_track_keywords"],
            ),
            "force_regular_keywords": ensure_list_str(
                privy_council.get("force_regular_keywords"),
                privy_defaults["force_regular_keywords"],
            ),
        },
        "anti_gaming": {
            "min_objective_signals_for_fast_track": int(
                anti_gaming.get(
                    "min_objective_signals_for_fast_track",
                    anti_defaults["min_objective_signals_for_fast_track"],
                )
            ),
            "urgent_keywords": ensure_list_str(
                anti_gaming.get("urgent_keywords"),
                anti_defaults["urgent_keywords"],
            ),
            "objective_keywords": ensure_list_str(
                anti_gaming.get("objective_keywords"),
                anti_defaults["objective_keywords"],
            ),
        },
        "fast_track_control": {
            "quota_per_24h": int(
                fast_track_control.get("quota_per_24h", fast_control_defaults["quota_per_24h"])
            ),
            "cooldown_minutes": int(
                fast_track_control.get("cooldown_minutes", fast_control_defaults["cooldown_minutes"])
            ),
            "window_hours": int(
                fast_track_control.get("window_hours", fast_control_defaults["window_hours"])
            ),
            "write_event_log": bool(
                fast_track_control.get("write_event_log", fast_control_defaults["write_event_log"])
            ),
        },
        "execution_control": {
            "require_dri": bool(execution_control.get("require_dri", execution_defaults["require_dri"])),
            "slo_minutes": execution_control.get("slo_minutes", execution_defaults["slo_minutes"]),
        },
        "audit_control": {
            "archive_levels": ensure_list_str(
                audit_control.get("archive_levels"),
                audit_defaults["archive_levels"],
            ),
            "default_archive_level": str(
                audit_control.get("default_archive_level", audit_defaults["default_archive_level"])
            ),
            "promotion_rules": ensure_list_str(
                audit_control.get("promotion_rules"),
                audit_defaults["promotion_rules"],
            ),
        },
    }


def should_enable_roundtable(
    text: str,
    assistants: list[str],
    confidence: float,
    sentinel_overlay: bool,
    governance_defaults: dict[str, object],
) -> bool:
    roundtable = governance_defaults.get("roundtable", {})
    if not isinstance(roundtable, dict):
        roundtable = {}
    assistant_count_min = int(roundtable.get("assistant_count_min", 1))
    confidence_max = float(roundtable.get("confidence_max", 0.75))
    force_keywords = roundtable.get("force_keywords", [])
    if not isinstance(force_keywords, list):
        force_keywords = []

    if sentinel_overlay:
        return True
    if len(assistants) >= assistant_count_min and confidence <= confidence_max:
        return True
    lowered = text.lower()
    for keyword in force_keywords:
        if not isinstance(keyword, str):
            continue
        if keyword_matches(lowered, keyword.lower()):
            return True
    return False


def should_use_fast_track(
    text: str,
    sentinel_overlay: bool,
    needs_git_workflow: bool,
    repo_path: Path,
    governance_defaults: dict[str, object],
) -> dict[str, object]:
    privy = governance_defaults.get("privy_council", {})
    if not isinstance(privy, dict):
        privy = {}
    anti = governance_defaults.get("anti_gaming", {})
    if not isinstance(anti, dict):
        anti = {}
    fast_control = governance_defaults.get("fast_track_control", {})
    if not isinstance(fast_control, dict):
        fast_control = {}

    prefer_regular_for_git = bool(privy.get("prefer_regular_for_git", True))
    allow_high_risk_fast_track = bool(privy.get("allow_high_risk_fast_track", False))
    force_fast_track_keywords = ensure_list_str(privy.get("force_fast_track_keywords"), [])
    force_regular_keywords = ensure_list_str(privy.get("force_regular_keywords"), [])

    min_objective_signals = int(anti.get("min_objective_signals_for_fast_track", 1))
    urgent_keywords = ensure_list_str(anti.get("urgent_keywords"), [])
    objective_keywords = ensure_list_str(anti.get("objective_keywords"), [])

    quota_per_24h = max(int(fast_control.get("quota_per_24h", 3)), 0)
    cooldown_minutes = max(int(fast_control.get("cooldown_minutes", 30)), 0)
    window_hours = max(int(fast_control.get("window_hours", 24)), 1)

    rationale: list[str] = []
    blockers: list[str] = []
    selected = False

    forced_regular_hits = keyword_hits(text, force_regular_keywords)
    forced_fast_hits = keyword_hits(text, force_fast_track_keywords)
    urgent_hits = keyword_hits(text, urgent_keywords)
    objective_hits = keyword_hits(text, objective_keywords)

    suspicious_manipulation = len(urgent_hits) > 0 and len(objective_hits) < min_objective_signals
    if suspicious_manipulation:
        blockers.append("疑似关键词操纵：紧急词存在但客观信号不足")

    if sentinel_overlay and not allow_high_risk_fast_track:
        blockers.append("命中高风险信号，禁止直通轨")

    if len(forced_regular_hits) > 0:
        blockers.append(f"命中常规轨强制关键词: {', '.join(forced_regular_hits)}")

    if needs_git_workflow and prefer_regular_for_git:
        blockers.append("Git 流程默认走常规轨")

    if len(forced_fast_hits) > 0:
        rationale.append(f"命中直通轨关键词: {', '.join(forced_fast_hits)}")
        selected = True
    elif len(urgent_hits) > 0 and len(objective_hits) >= min_objective_signals:
        rationale.append("命中紧急信号且客观信号达标")
        selected = True

    stats = get_fast_track_stats(
        repo_path=repo_path,
        window_hours=window_hours,
    )
    if selected:
        if quota_per_24h > 0 and int(stats.get("count_in_window", 0)) >= quota_per_24h:
            blockers.append("直通轨配额已达上限")
        latest = stats.get("latest_fast_track_at")
        if isinstance(latest, str):
            latest_dt = parse_iso_time(latest)
            if latest_dt is not None and cooldown_minutes > 0:
                until = latest_dt + timedelta(minutes=cooldown_minutes)
                if datetime.now() < until:
                    blockers.append("直通轨处于冷却期")

    enabled = selected and len(blockers) == 0
    return {
        "enabled": enabled,
        "rationale": rationale,
        "blockers": blockers,
        "signals": {
            "forced_fast_hits": forced_fast_hits,
            "forced_regular_hits": forced_regular_hits,
            "urgent_hits": urgent_hits,
            "objective_hits": objective_hits,
            "suspicious_manipulation": suspicious_manipulation,
        },
        "stats": stats,
        "policy": {
            "quota_per_24h": quota_per_24h,
            "cooldown_minutes": cooldown_minutes,
            "decision_log_path": DECISION_LOG_PATH,
            "window_hours": window_hours,
            "min_objective_signals_for_fast_track": min_objective_signals,
        },
    }


def dedupe_agents(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        if item not in seen:
            result.append(item)
            seen.add(item)
    return result


def apply_assistant_routing_rules(
    text: str,
    lead_agent: str,
    assistants: list[str],
    scores: dict[str, int],
    config: dict[str, object],
) -> list[str]:
    rules = config.get("assistant_routing_rules", [])
    if not isinstance(rules, list):
        return assistants

    lowered = text.lower()
    merged = list(assistants)
    for rule in rules:
        if not isinstance(rule, dict):
            continue
        if str(rule.get("lead_agent", "")).strip() != lead_agent:
            continue

        when_any_keywords = rule.get("when_any_keywords", [])
        add_assistants = rule.get("add_assistants", [])
        if not isinstance(when_any_keywords, list) or not isinstance(add_assistants, list):
            continue

        matched = any(
            isinstance(keyword, str) and keyword_matches(lowered, keyword.lower())
            for keyword in when_any_keywords
        )
        if not matched:
            continue

        for agent in add_assistants:
            if not isinstance(agent, str) or agent == lead_agent:
                continue
            if scores.get(agent, 0) > 0 or agent == "Technical Trinity":
                merged.append(agent)

    return dedupe_agents(merged)


def apply_language_copilot_rules(
    lead_agent: str,
    assistants: list[str],
    detected_languages: list[str],
    language_routing: dict[str, str],
    needs_worktree: bool,
    needs_git_workflow: bool,
) -> list[str]:
    merged = list(assistants)

    language_assistants: list[str] = []
    for language in detected_languages:
        candidate = language_routing.get(language)
        if isinstance(candidate, str) and candidate.strip():
            language_assistants.append(candidate)
    language_assistants = dedupe_agents(language_assistants)

    if lead_agent == "Code Audit Council":
        merged.extend(language_assistants)

    if lead_agent == "Git Workflow Guardian" and needs_worktree and needs_git_workflow:
        merged.extend(language_assistants)

    return dedupe_agents([agent for agent in merged if agent != lead_agent])


def pick_ministry_owner(
    ministry: str,
    lead_agent: str,
    assistants: list[str],
    scores: dict[str, int],
    sentinel_overlay: bool,
    needs_git_workflow: bool,
) -> str:
    if ministry == "吏部":
        return lead_agent
    if ministry == "户部":
        return "Git Workflow Guardian" if needs_git_workflow else "Technical Trinity"
    if ministry == "礼部":
        if scores.get("World-Class Product Architect", 0) > 0:
            return "World-Class Product Architect"
        return lead_agent
    if ministry == "兵部":
        if sentinel_overlay:
            return "Sentinel Architect (NB)"
        return "Code Audit Council"
    if ministry == "刑部":
        return "Code Audit Council"
    if ministry == "工部":
        engineering_agents = {
            "Java Virtuoso",
            "Technical Trinity",
            "Git Workflow Guardian",
            "World-Class Product Architect",
        }
        if lead_agent in engineering_agents:
            return lead_agent
        for agent in assistants:
            if agent in engineering_agents:
                return agent
        return "Technical Trinity"
    return lead_agent


def build_governance_plan(
    text: str,
    repo_path: Path,
    lead_agent: str,
    assistants: list[str],
    scores: dict[str, int],
    confidence: float,
    sentinel_overlay: bool,
    needs_git_workflow: bool,
    governance_defaults: dict[str, object],
) -> dict[str, object]:
    roundtable_enabled = should_enable_roundtable(
        text=text,
        assistants=assistants,
        confidence=confidence,
        sentinel_overlay=sentinel_overlay,
        governance_defaults=governance_defaults,
    )
    fast_track_decision = should_use_fast_track(
        text=text,
        sentinel_overlay=sentinel_overlay,
        needs_git_workflow=needs_git_workflow,
        repo_path=repo_path,
        governance_defaults=governance_defaults,
    )
    fast_track_enabled = bool(fast_track_decision.get("enabled", False))
    fast_track_rationale = fast_track_decision.get("rationale", [])
    fast_track_blockers = fast_track_decision.get("blockers", [])
    if not isinstance(fast_track_rationale, list):
        fast_track_rationale = []
    if not isinstance(fast_track_blockers, list):
        fast_track_blockers = []

    execution_control = governance_defaults.get("execution_control", {})
    if not isinstance(execution_control, dict):
        execution_control = {}
    audit_control = governance_defaults.get("audit_control", {})
    if not isinstance(audit_control, dict):
        audit_control = {}

    proposal_agents = dedupe_agents([lead_agent] + assistants[:1])
    review_agents = dedupe_agents(
        [
            "Code Audit Council",
            "Sentinel Architect (NB)" if sentinel_overlay else "",
        ]
    )
    review_agents = [agent for agent in review_agents if agent != ""]
    execution_agents = dedupe_agents([lead_agent] + assistants)

    ministries = [
        ("吏部", "智能体选派与优先级"),
        ("户部", "预算与资源编排"),
        ("礼部", "输出规范与对齐"),
        ("兵部", "安全与风险防线"),
        ("刑部", "质量门禁与裁决"),
        ("工部", "工程实施与交付"),
    ]
    ministry_assignments: list[dict[str, str]] = []
    for name, duty in ministries:
        owner = pick_ministry_owner(
            ministry=name,
            lead_agent=lead_agent,
            assistants=assistants,
            scores=scores,
            sentinel_overlay=sentinel_overlay,
            needs_git_workflow=needs_git_workflow,
        )
        ministry_assignments.append(
            {
                "name": name,
                "owner_agent": owner,
                "duty": duty,
            }
        )

    selected_track = TRACK_FAST if fast_track_enabled else TRACK_REGULAR
    if sentinel_overlay:
        risk_level = "high"
    elif len(assistants) > 0 or roundtable_enabled:
        risk_level = "medium"
    else:
        risk_level = "low"

    dual_sign_required = sentinel_overlay or (risk_level == "high")
    post_audit_required = fast_track_enabled
    archive_levels = ensure_list_str(audit_control.get("archive_levels"), ["draft", "verified", "gold"])
    default_archive_level = str(audit_control.get("default_archive_level", "draft"))
    promotion_rules = ensure_list_str(
        audit_control.get("promotion_rules"),
        ["双签通过后可从 draft 提升到 verified"],
    )
    risk_to_slo = execution_control.get("slo_minutes", {"low": 120, "medium": 60, "high": 30})
    if not isinstance(risk_to_slo, dict):
        risk_to_slo = {"low": 120, "medium": 60, "high": 30}
    slo_minutes = int(risk_to_slo.get(risk_level, risk_to_slo.get("medium", 60)))
    require_dri = bool(execution_control.get("require_dri", True))
    dri_agent = lead_agent if require_dri else ""

    if dual_sign_required:
        decision_protocol = "双签通过：Sentinel Architect (NB) + Code Audit Council"
    elif fast_track_enabled:
        decision_protocol = "快速执行 + 限时回审"
    elif roundtable_enabled:
        decision_protocol = "圆桌共识 + 主责智能体拍板"
    elif len(assistants) > 0:
        decision_protocol = "多方会签后主责拍板"
    else:
        decision_protocol = "主责智能体直接决策"

    return {
        "roundtable_enabled": roundtable_enabled,
        "risk_level": risk_level,
        "privy_council": {
            "name": "governance council",
            "selected_track": selected_track,
            "rationale": fast_track_rationale,
            "blockers": fast_track_blockers,
            "signal_evidence": fast_track_decision.get("signals", {}),
            "track_control": fast_track_decision.get("policy", {}),
            "track_stats": fast_track_decision.get("stats", {}),
            "dual_sign_required": dual_sign_required,
            "post_audit_required": post_audit_required,
        },
        "tracks": {
            "regular": {
                "name": TRACK_REGULAR,
                "flow": ["提案分流", "风险审议", "执行分发", "交付跟进"],
            },
            "fast": {
                "name": TRACK_FAST,
                "flow": ["快速指派", "执行直达", "快速反馈", "结果回传"],
            },
        },
        "agenda": [
            "议题定义",
            "方案辩论（提案组）",
            "风险投票（审议组）",
            "执行决议（执行组）",
        ],
        "governance_groups": {
            "proposal_group": {"label": "提案组", "role": "proposal", "agents": proposal_agents},
            "review_group": {"label": "审议组", "role": "review", "agents": review_agents},
            "execution_group": {"label": "执行组", "role": "execution", "agents": execution_agents},
        },
        "delivery_lanes": ministry_assignments,
        "execution_contract": {
            "dri_required": require_dri,
            "dri_agent": dri_agent,
            "slo_minutes": max(slo_minutes, 1),
            "checkpoints": ["start", "mid", "final"],
        },
        "decision_protocol": decision_protocol,
        "dual_sign": {
            "required": dual_sign_required,
            "signers": ["Sentinel Architect (NB)", "Code Audit Council"] if dual_sign_required else [],
            "evidence_template": [
                "risk_summary",
                "impact_scope",
                "rollback_plan",
                "verification_plan",
            ],
        },
        "post_audit": {
            "required": post_audit_required,
            "flow": ["T+0执行", "T+1审计复盘", "T+2规则回写"],
            "archive_target": "governance knowledge base",
            "archive_level": default_archive_level,
            "archive_levels": archive_levels,
            "promotion_rules": promotion_rules,
        },
        "feedback_loop": {
            "enabled": True,
            "loop": ["结果回奏", "指标归档", "规则调优"],
        },
        "minority_report": "允许记录少数意见，写入最终决议作为风险备忘",
    }


def build_process_plan(
    needs_pre_development_planning: bool = False,
    needs_iteration: bool = False,
    needs_project_knowledge_capture: bool = False,
    needs_worktree: bool = False,
    needs_release_gate: bool = False,
    needs_git_workflow: bool = False,
    repo_strategy: dict[str, str] | None = None,
    iteration_profile: dict[str, object] | None = None,
    lead_agent: str | None = None,
    workflow_bundle_name: str | None = None,
    auto_run_profile: dict[str, object] | None = None,
    state_root: Path | None = None,
) -> list[dict[str, object]]:
    plan: list[dict[str, object]] = []
    if not isinstance(repo_strategy, dict):
        repo_strategy = {"strategy": "unknown", "base_branch": "main"}
    base_branch = str(repo_strategy.get("base_branch", "main"))
    iteration_owner = lead_agent or "<lead-owner>"
    if state_root is not None:
        state_root_command = f"STATE_ROOT={shlex.quote(str(state_root))}"
    else:
        state_root_command = (
            'STATE_ROOT="$(git worktree list --porcelain | '
            "sed -n 's/^worktree //p' | head -n 1)\""
        )
    iteration_workspace = '"$STATE_ROOT/.vidt/iterations"' if needs_worktree else ".vidt/iterations"
    if not isinstance(auto_run_profile, dict):
        auto_run_profile = {"enabled": False}
    if not isinstance(iteration_profile, dict):
        iteration_profile = {
            "round_cap_online": 3,
            "round_cap_offline": 120,
            "max_same_hypothesis_retries": 2,
            "require_objective_signal": True,
            "allowed_decisions": ["keep", "retry", "rollback", "stop"],
            "required_artifacts": [
                "assets/iteration-ledger-template.md",
                "assets/round-reflection-template.md",
                "assets/round-memory-template.md",
                "assets/self-feedback-template.md",
                "assets/distilled-patterns-template.md",
            ],
        }
    if needs_pre_development_planning:
        plan.append(
            {
                "skill": "pre-development-planning",
                "reference": "references/pre-development-planning-playbook.md",
                "steps": [
                    "先锁定 transformation scope、target、constraints 和 primary priority",
                    "只分析支撑规划所需的 architecture、entry points、key modules 和 risks",
                    "生成轻量 planning pack，而不是提前进入重实现",
                    "当任务足够大时，再补 phase lanes、merge risk 和 resume protocol",
                    "建立 docs/progress/MASTER.md 作为跨会话 progress anchor",
                    "按 pre-development output template 向用户汇报 planning pack",
                    "规划完成后，再回到正常 lead / assistant / governance / iteration / release 路径",
                ],
                "commands": [
                    "python scripts/init_project_memory.py --root . --mode planning --pretty",
                    "python scripts/init_pre_development_plan.py --root . --task-name \"<task-name>\" --task-description \"<task-description>\" --phase-name foundation --pretty",
                    "python scripts/route_request.py --text \"<rewrite-or-migration-request>\" --config references/routing-rules.json --pretty",
                ],
                "artifacts": [
                    "docs/analysis/project-overview.md",
                    "docs/plan/task-breakdown.md",
                    "docs/progress/MASTER.md",
                    "docs/progress/phase-1-foundation.md",
                    "docs/progress/phase-2-architecture.md",
                    "docs/progress/phase-3-execution.md",
                    "docs/progress/phase-4-cutover.md",
                ],
                "resume_anchor": "docs/progress/MASTER.md",
                "resume_artifacts": [
                    "docs/progress/MASTER.md",
                    "docs/analysis/project-overview.md",
                    "docs/plan/task-breakdown.md",
                ],
            }
        )
    if needs_iteration:
        iteration_commands = []
        if needs_worktree:
            iteration_commands.append(state_root_command)
        iteration_commands.extend(
            [
                (
                    'python scripts/init_project_memory.py --root "$STATE_ROOT" '
                    "--mode iteration --pretty"
                    if needs_worktree
                    else "python scripts/init_project_memory.py --root . --mode iteration --pretty"
                ),
                f"mkdir -p {iteration_workspace}",
                f"cp assets/iteration-plan-template.json {iteration_workspace}/iteration-plan.json",
                f"python scripts/register_benchmark_baseline.py --workspace {iteration_workspace} --label stable --report <baseline-report> --pretty",
                f"python scripts/run_iteration_cycle.py --workspace {iteration_workspace} --round-id round-01 --objective \"<goal>\" --baseline-label stable --owner \"{iteration_owner}\" --candidate \"<candidate-change>\" --candidate-worktree ../wt-round-01 --candidate-output-dir .tmp-iteration-round-01 --pretty",
                f"python scripts/compare_benchmark_results.py --baseline {iteration_workspace}/baselines/stable/benchmark-results.json --candidate .tmp-iteration-round-01/benchmark-results.json --pretty",
                f"python scripts/promote_iteration_baseline.py --workspace {iteration_workspace} --round-id round-01 --label accepted-round-01 --pretty",
                f"python scripts/sync_distilled_patterns.py --workspace {iteration_workspace} --pretty",
                f"python scripts/materialize_candidate_patch.py --brief {iteration_workspace}/candidate-briefs/round-01.json --candidate-root ../wt-round-01 --patch-output {iteration_workspace}/patches/round-01.patch --pretty",
                f"python scripts/run_iteration_loop.py --workspace {iteration_workspace} --plan {iteration_workspace}/iteration-plan.json --pretty",
                f"python scripts/run_iteration_loop.py --workspace {iteration_workspace} --plan {iteration_workspace}/iteration-plan.json --resume --pretty",
            ]
        )
        plan.append(
            {
                "skill": "bounded-iteration",
                "reference": "references/iteration-protocol.md",
                "state_root": str(state_root) if state_root is not None else None,
                "steps": [
                    "定义目标函数、基线和本轮唯一候选改动",
                    "保留语义主责 owner，并准备 iteration workspace 与计划文件",
                    "先注册可复用 baseline",
                    "运行一轮有状态的 iteration cycle，或按计划运行多轮 iteration loop",
                    "由 cycle 自动写入 ledger / reflection / state / open loops",
                    "读取 round-memory / self-feedback / iteration-context-chain 作为下一轮输入",
                    "如需把 synthesized candidate 落成真实改动，先写 candidate brief，再交给 materialize command 生成 patch 或工作区变更",
                    "当候选改动能用结构化文件操作表达时，优先使用内置 materialize_candidate_patch",
                    "深度离线 loop 中断后，使用持久化 loop state 安全续跑",
                    "按 keep / retry / rollback / stop 做轮次决策",
                ],
                "commands": iteration_commands,
                "round_caps": {
                    "online": int(iteration_profile.get("round_cap_online", 3)),
                    "offline": int(iteration_profile.get("round_cap_offline", 120)),
                },
                "max_same_hypothesis_retries": int(
                    iteration_profile.get("max_same_hypothesis_retries", 2)
                ),
                "require_objective_signal": bool(
                    iteration_profile.get("require_objective_signal", True)
                ),
                "allowed_decisions": iteration_profile.get(
                    "allowed_decisions", ["keep", "retry", "rollback", "stop"]
                ),
                "artifacts": iteration_profile.get(
                    "required_artifacts",
                        [
                            "assets/iteration-ledger-template.md",
                            "assets/round-reflection-template.md",
                            "assets/round-memory-template.md",
                            "assets/self-feedback-template.md",
                            "assets/distilled-patterns-template.md",
                        ],
                    ),
                "plan_template": "assets/iteration-plan-template.json",
                "resume_anchor": ".vidt/iterations/current-round-memory.md",
                "resume_artifacts": [
                    ".vidt/iterations/current-round-memory.md",
                    ".vidt/iterations/distilled-patterns.md",
                ],
            }
        )
    if needs_project_knowledge_capture:
        plan.append(
            {
                "skill": "project-knowledge-capture",
                "reference": "skill-forge/references/project-knowledge-capture-protocol.md",
                "steps": [
                    "先盘点现有 AGENTS.md、.agents/skills、README、docs、配置、入口文件、测试与脚本",
                    "只在代码库足够大时拆分独立分析 lanes，且每条 lane 必须有明确范围和预期产出",
                    "将 lane 结果汇总去重，删除无法由仓库事实验证的泛泛建议",
                    "把仓库级短规则写入 AGENTS.md，把可重复开发场景写成项目本地 .agents/skills",
                    "确认所有引用路径、命令、目录和文件名真实存在，未确认信息必须显式标注",
                ],
                "commands": [
                    "rg --files",
                    "find . -maxdepth 3 -name AGENTS.md -o -path '*/.agents/skills/*'",
                    "git diff -- AGENTS.md .agents/skills",
                    "python validate.py --repo-only",
                ],
                "artifacts": [
                    "AGENTS.md",
                    ".agents/skills/",
                    "skill-forge/references/project-knowledge-capture-protocol.md",
                ],
                "resume_anchor": "AGENTS.md",
                "resume_artifacts": [
                    "AGENTS.md",
                    ".agents/skills/",
                ],
            }
        )
    if needs_worktree:
        plan.append(
            {
                "skill": "using-git-worktrees",
                "reference": "references/using-git-worktrees-playbook.md",
                "state_root": str(state_root) if state_root is not None else None,
                "steps": [
                    "needs_worktree 是关键词初筛结果；运行时按 SKILL.md worktree 语义复核步骤确认任务是否真需要并行隔离，若误判可降级不强制 worktree",
                    f"确定基线分支（当前建议为 {base_branch}）",
                    "为每个任务创建独立 worktree 与分支",
                    "在各自 worktree 内开发与提交",
                    "状态目录留主仓根（state-root），worktree 只放代码改动与一次性执行产物；归属表与路径约定见 references/worktree-state-placement-protocol.md",
                    "任务完成后清理已合并 worktree",
                ],
                "commands": [
                    "git worktree list",
                    f"git worktree add ../wt-<task> -b <branch> {base_branch}",
                    state_root_command,
                    "git worktree remove ../wt-<task>",
                    "git worktree prune",
                ],
            }
        )
    if needs_release_gate:
        plan.append(
            {
                "skill": "release-gate",
                "reference": "references/release-gate-playbook.md",
                "steps": [
                    "先运行正式 release gate，而不是只看一次 benchmark 摘要",
                    "让 gate 自动汇总 tests / semantic validator / evals / offline drill，必要时并入最近一轮 beta gate",
                    "在 ship 前确认 .vidt/evidence/completion-evidence.json 已经补全且通过完成证据校验",
                    "读取 ship 或 hold 决策、失败原因、以及产物路径",
                    "若结论为 hold，则把阻塞项回写到 iteration ledger 或发布清单，再进入下一轮",
                ],
                "commands": [
                    "mkdir -p .vidt/evidence && cp assets/completion-evidence-template.json .vidt/evidence/completion-evidence.json",
                    "python scripts/verify_completion_evidence.py --evidence .vidt/evidence/completion-evidence.json --pretty",
                    "python scripts/run_release_gate.py --output-dir evals/release-gate --pretty",
                    "python scripts/run_release_gate.py --output-dir evals/release-gate --previous-output evals/benchmark-results/benchmark-results.json --pretty",
                    "python scripts/run_release_gate.py --output-dir evals/release-gate --beta-decision-dir .vidt/beta/round-decisions --pretty",
                    "python scripts/run_release_gate.py --output-dir evals/release-gate --beta-report-dir .vidt/beta/reports --pretty",
                    "python scripts/run_release_gate.py --output-dir evals/release-gate --completion-evidence .vidt/evidence/completion-evidence.json --pretty",
                    "python scripts/run_release_gate.py --output-dir evals/release-gate --iteration-workspace .vidt/iterations --release-label release-ready --pretty",
                    "python scripts/run_release_gate.py --output-dir evals/release-gate --iteration-workspace .vidt/iterations --auto-run-next-iteration-on-hold --hold-loop-max-rounds 3 --pretty",
                ],
                "decisions": ["ship", "hold"],
                "artifacts": [
                    "evals/release-gate/release-gate-results.json",
                    "evals/release-gate/release-gate-report.md",
                    "evals/release-gate/next-iteration-brief.json",
                    "evals/release-gate/release-closure.json",
                    ".vidt/iterations/iteration-plan.release-gate.json",
                    ".vidt/evidence/completion-evidence.json",
                    "evals/release-gate/benchmark-results.json",
                    "evals/release-gate/benchmark-report.md",
                ],
                "resume_anchor": "evals/release-gate/release-gate-report.md",
                "resume_artifacts": [
                    "evals/release-gate/release-gate-report.md",
                    "evals/release-gate/next-iteration-brief.json",
                ],
            }
        )
    if needs_git_workflow:
        templates = build_git_templates(repo_strategy)
        plan.append(
            {
                "skill": "git-workflow",
                "reference": "references/git-workflow-playbook.md",
                "steps": [
                    "R0 画像：识别仓库分支策略与基线分支",
                    "G0 检查：确认分支、工作区、远端状态",
                    "G1 暂存：仅暂存本次任务必需改动",
                    "G2 提交：按语义前缀提交单一意图变更",
                    "G3 同步：与远端同步并处理冲突",
                    "G4 推送/PR：推送分支并按门禁发起评审",
                ],
                "commands": [
                    "python scripts/git_workflow_guardrail.py --repo . --detect-repo-strategy --print-templates --pretty",
                    "python scripts/git_workflow_guardrail.py --repo . --stage G0 --pretty",
                    "git status --short --branch",
                    f"git checkout -b {templates['branch_name']}",
                    "python scripts/git_workflow_guardrail.py --repo . --stage G1 --pretty",
                    "git add <files>",
                    f"python scripts/git_workflow_guardrail.py --repo . --stage G2 --commit-message \"{templates['commit_message']}\" --pretty",
                    f"git commit -m \"{templates['commit_message']}\"",
                    "python scripts/git_workflow_guardrail.py --repo . --stage G3 --pretty",
                    f"git pull --rebase origin {templates['base_branch']}",
                    "python scripts/git_workflow_guardrail.py --repo . --stage G4 --pretty",
                    f"git push -u origin {templates['branch_name']}",
                ],
                "auto_execute_policy": build_auto_execute_policy(),
                "repo_strategy": repo_strategy,
                "templates": templates,
                "kpis": [
                    "first_push_success_rate",
                    "rebase_conflict_rate",
                    "rollback_rate",
                    "manual_intervention_rate",
                ],
            }
        )
    if workflow_bundle_name == "post-release-close-loop":
        plan.append(
            {
                "skill": "post-release-feedback",
                "reference": "references/post-release-feedback-playbook.md",
                "steps": [
                    "先初始化已发布反馈工作区",
                    "把 telemetry、support 与真实用户反馈写入 current signal report",
                    "运行 post-release gate，判断 monitor、iterate 或 escalate",
                    "把回写结果同步回产品或技术治理锚点后再决定是否 reopen",
                ],
                "commands": [
                    "python scripts/init_post_release_feedback.py --root . --pretty",
                    "python scripts/evaluate_post_release_feedback.py --report .vidt/post-release/current-signals.json --pretty",
                ],
                "artifacts": [
                    ".vidt/post-release/rollout-summary.md",
                    ".vidt/post-release/feedback-ledger.md",
                    ".vidt/post-release/current-signals.json",
                    ".vidt/post-release/triage-summary.md",
                ],
                "resume_anchor": ".vidt/post-release/triage-summary.md",
                "resume_artifacts": [
                    ".vidt/post-release/triage-summary.md",
                    ".vidt/post-release/current-signals.json",
                ],
            }
        )
    if bool(auto_run_profile.get("enabled")):
        target_skill_by_bundle = {
            "root-cause-remediate": "bounded-iteration",
            "ship-hold-remediate": "release-gate",
            "post-release-close-loop": "post-release-feedback",
        }
        target_skill = target_skill_by_bundle.get(str(auto_run_profile.get("workflow_bundle", "")))
        if target_skill is not None:
            for entry in plan:
                if entry.get("skill") != target_skill:
                    continue
                entry["auto_run"] = {
                    "enabled": bool(auto_run_profile.get("workflow_supported")),
                    "requested_phase": str(auto_run_profile.get("requested_phase", "setup")),
                    "run_style": str(auto_run_profile.get("run_style", "foreground")),
                    "safety_level": str(auto_run_profile.get("safety_level", "standard")),
                    "resume_requested": bool(auto_run_profile.get("resume_requested")),
                    "detached_ready": bool(auto_run_profile.get("detached_ready")),
                    "requires_explicit_go": bool(auto_run_profile.get("requires_explicit_go", True)),
                    "setup_command": str(auto_run_profile.get("setup_command", "")),
                    "go_command": str(auto_run_profile.get("go_command", "")),
                    "resume_anchor": str(auto_run_profile.get("resume_anchor", "")),
                }
                break
    return plan


def pick_process_lead_agent(process_skills: list[str], config: dict[str, object]) -> str:
    mapping = config.get("process_skill_lead_agents", {})
    if isinstance(mapping, dict):
        for skill in process_skills:
            candidate = mapping.get(skill)
            if isinstance(candidate, str) and candidate.strip():
                return candidate
    return str(config.get("default_process_lead_agent", "Technical Trinity"))


def rebalance_git_lead_for_semantic_owner(
    lead_agent: str,
    priority_route: dict[str, object] | None,
    scores: dict[str, int],
    needs_git_workflow: bool,
) -> str:
    if lead_agent != "Git Workflow Guardian" or not needs_git_workflow:
        return lead_agent
    if priority_route is not None:
        return lead_agent

    semantic_owners = [
        "Code Audit Council",
        "World-Class Product Architect",
        "Technical Trinity",
    ]
    git_score = scores.get("Git Workflow Guardian", 0)
    for agent in semantic_owners:
        if scores.get(agent, 0) >= max(5, git_score // 2):
            return agent
    return lead_agent


def is_quick_slice_context(text: str) -> bool:
    quick_slice_keywords = [
        "implement",
        "build",
        "add",
        "fix",
        "bugfix",
        "patch",
        "small feature",
        "tiny feature",
        "quick fix",
        "wire up",
        "hook up",
        "bug",
        "refactor this",
        "refactor the",
        "refactor a",
        "refactor code",
        "refactor function",
        "edit code",
        "change code",
        "modify code",
        "make the change",
        "实现",
        "开发",
        "修复",
        "修一下",
        "直接修",
        "重构这段",
        "重构这个函数",
        "重构一下",
        "重构代码",
        "修改代码",
        "改代码",
        "改一下",
        "小功能",
        "小改动",
        "小 bug",
        "小bug",
        "补一个",
        "加一个",
        "接一下",
        "跑回归",
    ]
    return text_has_any_keyword(text, quick_slice_keywords)


def pick_mode(
    confidence: float,
    sentinel_overlay: bool,
    needs_pre_development_planning: bool,
    process_only: bool,
    language_only: bool,
    unknown_only: bool,
    roundtable_enabled: bool,
    fast_track_enabled: bool,
    assistant_count: int,
    high_confidence: float,
    medium_confidence: float,
) -> str:
    if fast_track_enabled:
        return "模式 G：快速治理（fast track）"
    if needs_pre_development_planning and process_only:
        return "规划驱动模式：先做开发前准备"
    if roundtable_enabled:
        return "模式 F：圆桌治理（regular track）"
    if process_only:
        return "流程驱动模式：按流程技能执行"
    if language_only:
        return "语言驱动模式：按语言栈执行"
    if unknown_only:
        return "低置信分流：等待用户补充信息"
    if sentinel_overlay:
        return "模式 D：高风险治理"
    if assistant_count > 0:
        return "模式 B：评审-实现 或 模式 C：战略-技术双轨"
    if confidence >= high_confidence:
        return "模式 A：单点执行"
    if confidence >= medium_confidence:
        return "模式 B：评审-实现 或 模式 C：战略-技术双轨"
    if assistant_count == 0:
        return "低置信分流：需要澄清问题"
    return "低置信分流：主责+2辅助并补澄清问题"


def build_clarifying_question(text: str, need_clarify: bool) -> str | None:
    if not need_clarify:
        return None
    if has_cjk(text):
        return "请补充技术栈、目标和期望产出（代码、方案或审计）？"
    return "Please share tech stack, target outcome, and expected output type (code, architecture, or review)."


def detect_intent_categories(text: str) -> list[str]:
    categories: list[str] = []
    for category, keywords in INTENT_CATEGORY_KEYWORDS.items():
        if text_has_any_keyword(text, keywords):
            categories.append(category)
    return categories


def is_fuzzy_intent_request(text: str) -> bool:
    fuzzy_hits = keyword_hits(text, FUZZY_INTENT_KEYWORDS)
    if len(fuzzy_hits) == 0:
        return False
    category_hits = detect_intent_categories(text)
    choice_hits = keyword_hits(text, ROUTE_CHOICE_KEYWORDS)
    return len(category_hits) >= 2 or len(choice_hits) > 0


def build_scope_boundary(text: str, *, unknown_only: bool) -> dict[str, str]:
    """Classify explicit cross-skill requests before an execution route is claimed."""
    if text_has_any_keyword(
        text,
        ["写一本", "小说", "网文", "连载", "novel writing", "write a novel"],
    ):
        return {
            "status": "out_of_scope",
            "reason": "The request is long-form fiction production, not software delivery.",
            "recommended_skill": "novel-studio",
            "next_step": "Route the request to novel-studio or another novel-forge skill.",
        }
    if text_has_any_keyword(
        text,
        ["深度研究报告", "deep research report", "竞品公司", "竞品截面", "时间线和竞品"],
    ):
        return {
            "status": "out_of_scope",
            "reason": "The request is evidence-led company or competitor research, not software delivery.",
            "recommended_skill": "deep-research-forge",
            "next_step": "Route the request to deep-research-forge.",
        }
    concrete_software_task = text_has_any_keyword(
        text,
        [
            "implement",
            "implementation",
            "refactor",
            "fix",
            "bug",
            "api",
            "code",
            "unit test",
            "run tests",
            ".py",
            ".java",
            ".ts",
            ".js",
            "实现",
            "重构",
            "修复",
            "代码",
            "接口",
            "测试",
        ],
    )
    if unknown_only and not concrete_software_task:
        return {
            "status": "insufficient_information",
            "reason": "No concrete software task, stack, artifact, or delivery action was detected.",
            "recommended_skill": "",
            "next_step": "Ask for the concrete software task, affected artifact, and desired outcome.",
        }
    return {
        "status": "in_scope",
        "reason": "The request contains a concrete software delivery or governance signal.",
        "recommended_skill": "",
        "next_step": "Proceed with the selected software workflow.",
    }


def build_intent_confirmation_options(language: str) -> list[dict[str, str]]:
    if language == "zh":
        return [
            {
                "id": "product-opportunity",
                "label": "判断产品机会/需求价值",
                "description": "先确认目标用户、需求强度、价值假设和是否值得进入产品切片。",
                "target_lead": "World-Class Product Architect",
                "target_bundle": "product-spec-deliver",
                "target_council": "product-discovery-council",
            },
            {
                "id": "prototype-exploration",
                "label": "做原型/体验方向探索",
                "description": "先产出交互方向、设计约束和最小可运行高保真原型。",
                "target_lead": "World-Class Product Architect",
                "target_bundle": "product-spec-deliver",
                "target_council": "prototype-design-council",
            },
            {
                "id": "technical-feasibility",
                "label": "验证技术可行性/实现路径",
                "description": "先验证技术约束、实现路径、关键风险和最小工程切片。",
                "target_lead": "Technical Trinity",
                "target_bundle": "quick-slice-deliver",
                "target_council": "",
            },
            {
                "id": "architecture-risk",
                "label": "评估架构风险/治理边界",
                "description": "先评估架构影响、迁移风险、回滚条件和是否需要治理门禁。",
                "target_lead": "Sentinel Architect (NB)",
                "target_bundle": "govern-change-safely",
                "target_council": "",
            },
            {
                "id": "delivery-plan",
                "label": "拆成可执行交付计划",
                "description": "先拆范围、里程碑、验收标准、恢复锚点和下一步执行顺序。",
                "target_lead": "Technical Trinity",
                "target_bundle": "plan-first-build",
                "target_council": "",
            },
        ]
    return [
        {
            "id": "product-opportunity",
            "label": "Assess product opportunity / requirement value",
            "description": "Confirm user, demand strength, value hypothesis, and whether this should enter product slicing.",
            "target_lead": "World-Class Product Architect",
            "target_bundle": "product-spec-deliver",
            "target_council": "product-discovery-council",
        },
        {
            "id": "prototype-exploration",
            "label": "Explore prototype / experience direction",
            "description": "Confirm interaction direction, design constraints, and the smallest runnable high-fidelity prototype.",
            "target_lead": "World-Class Product Architect",
            "target_bundle": "product-spec-deliver",
            "target_council": "prototype-design-council",
        },
        {
            "id": "technical-feasibility",
            "label": "Validate technical feasibility / implementation path",
            "description": "Check technical constraints, implementation path, key risks, and the smallest engineering slice.",
            "target_lead": "Technical Trinity",
            "target_bundle": "quick-slice-deliver",
            "target_council": "",
        },
        {
            "id": "architecture-risk",
            "label": "Assess architecture risk / governance boundary",
            "description": "Evaluate architecture impact, migration risk, rollback conditions, and whether governance gates are needed.",
            "target_lead": "Sentinel Architect (NB)",
            "target_bundle": "govern-change-safely",
            "target_council": "",
        },
        {
            "id": "delivery-plan",
            "label": "Break this into an executable delivery plan",
            "description": "Clarify scope, milestones, acceptance criteria, resume anchor, and next execution order.",
            "target_lead": "Technical Trinity",
            "target_bundle": "plan-first-build",
            "target_council": "",
        },
    ]


def build_intent_confirmation(
    *,
    text: str,
    need_clarify: bool,
    lead_agent: str,
    workflow_bundle: dict[str, object],
) -> dict[str, object]:
    language = "zh" if has_cjk(text) else "en"
    fuzzy_hits = keyword_hits(text, FUZZY_INTENT_KEYWORDS)
    category_hits = detect_intent_categories(text)
    route_choice_hits = keyword_hits(text, ROUTE_CHOICE_KEYWORDS)
    explicit_multi_agent_execution = (
        text_has_any_keyword(text, REAL_SUBAGENT_TRIGGER_KEYWORDS)
        and text_has_any_keyword(
            text,
            [
                "implement",
                "implementation",
                "refactor",
                "fix",
                "run tests",
                "verify",
                "实现",
                "重构",
                "修复",
                "测试",
                "验证",
                "验收",
            ],
        )
    )
    required = (need_clarify or is_fuzzy_intent_request(text)) and not explicit_multi_agent_execution
    options = build_intent_confirmation_options(language) if required else []
    provisional_route = {
        "lead_agent": lead_agent,
        "workflow_bundle": str(workflow_bundle.get("name", "direct-execution")),
        "bundle_confidence": workflow_bundle.get("confidence", 0.0),
        "workflow_bundle_source": str(workflow_bundle.get("source", "unknown")),
    }

    if not required:
        return {
            "required": False,
            "reason": "",
            "question": None,
            "option_ids": [],
            "options": [],
            "provisional_route": provisional_route,
            "fuzzy_markers": fuzzy_hits,
            "detected_categories": category_hits,
            "route_choice_markers": route_choice_hits,
        }

    if language == "zh":
        reason = (
            "请求是低信息量或模糊猜想，且不同意图会改变 lead、workflow bundle 或阶段专家团。"
        )
        question = "这会影响专家路由。我先确认：你更想让我从哪个方向切入？"
    else:
        reason = (
            "The request is low-information or a fuzzy idea, and different intents would change "
            "the lead, workflow bundle, or stage council."
        )
        question = "This changes the expert route. Which intent should I confirm first?"

    return {
        "required": True,
        "reason": reason,
        "question": question,
        "option_ids": [str(item["id"]) for item in options],
        "options": options,
        "provisional_route": provisional_route,
        "fuzzy_markers": fuzzy_hits,
        "detected_categories": category_hits,
        "route_choice_markers": route_choice_hits,
    }


def text_has_any_keyword(text: str, keywords: list[str]) -> bool:
    lowered = text.lower()
    return any(keyword_matches(lowered, keyword.lower()) for keyword in keywords)


def build_stage_council_plan(
    *,
    text: str,
    lead_agent: str,
    workflow_bundle: dict[str, object],
) -> dict[str, object]:
    bundle_name = str(workflow_bundle.get("name", "direct-execution"))
    product_keywords = [
        "product strategy",
        "product council",
        "product expert team",
        "prd",
        "feature spec",
        "requirement analysis",
        "requirements",
        "user research",
        "competitive analysis",
        "competitor",
        "metrics",
        "roadmap",
        "sprint",
        "stakeholder",
        "brainstorm",
        "产品战略",
        "产品专家团",
        "产品团队",
        "功能规格",
        "需求分析",
        "用户研究",
        "竞品",
        "指标",
        "路线图",
        "迭代规划",
        "干系人",
        "产品头脑风暴",
    ]
    prototype_keywords = [
        "prototype",
        "prototype design",
        "design prototype",
        "interactive prototype",
        "high-fidelity",
        "hi-fi",
        "html prototype",
        "design system",
        "visual design",
        "page design",
        "brand tone",
        "原型",
        "原型设计",
        "原型专家团",
        "设计原型",
        "高保真",
        "交互原型",
        "html 原型",
        "可运行原型",
        "设计系统",
        "视觉设计",
        "页面设计",
        "品牌调性",
    ]
    explicit_team_keywords = [
        "expert team",
        "council",
        "multi-role",
        "专家团",
        "多角色",
        "团队协作",
    ]

    enabled = lead_agent == "World-Class Product Architect" and bundle_name == "product-spec-deliver"
    product_active = enabled and text_has_any_keyword(text, product_keywords)
    prototype_active = enabled and text_has_any_keyword(text, prototype_keywords)
    explicit_team_request = text_has_any_keyword(text, explicit_team_keywords)
    councils: list[dict[str, object]] = []

    if product_active:
        councils.append(
            {
                "name": "product-discovery-council",
                "lead": "World-Class Product Architect",
                "activation_reason": (
                    "Product discovery, strategy, research, metrics, or roadmap signals require "
                    "stage-level product specialists before implementation."
                ),
                "roles": [
                    {
                        "role": "requirement-analyst",
                        "owns": ["scope", "P0/P1/P2 requirements", "acceptance criteria", "non-goals"],
                    },
                    {
                        "role": "user-researcher",
                        "owns": ["target user", "jobs-to-be-done", "research synthesis", "user risk"],
                    },
                    {
                        "role": "competitive-analyst",
                        "owns": ["competitor patterns", "differentiation", "market proof"],
                    },
                    {
                        "role": "data-analyst",
                        "owns": ["success metrics", "funnel or retention signals", "decision evidence"],
                    },
                    {
                        "role": "roadmap-planner",
                        "owns": ["sequencing", "milestones", "stakeholder update", "delivery tradeoffs"],
                    },
                ],
                "sequence": [
                    "collect current user, market, data, and constraint evidence",
                    "synthesize P0/P1/P2 scope and non-goals",
                    "turn the product decision into acceptance criteria and slice boundaries",
                    "hand the accepted product slice back to product-spec-deliver",
                ],
                "quality_gates": [
                    "scope_gate",
                    "user_evidence_gate",
                    "competitive_or_market_evidence_gate",
                    "metric_gate",
                    "roadmap_sequence_gate",
                ],
                "output_artifacts": [
                    ".vidt/product/current-slice.md",
                    ".vidt/product/acceptance-criteria.md",
                    ".vidt/product/stage-council-plan.json",
                ],
                "resume_anchor": ".vidt/product/current-slice.md",
            }
        )

    if prototype_active:
        councils.append(
            {
                "name": "prototype-design-council",
                "lead": "World-Class Product Architect",
                "activation_reason": (
                    "Prototype, design system, high-fidelity UI, or visual design signals require "
                    "stage-level design specialists instead of a single product generalist."
                ),
                "roles": [
                    {
                        "role": "ux-discovery",
                        "owns": ["surface", "audience", "task flow", "content scale", "interaction constraints"],
                    },
                    {
                        "role": "design-system-curator",
                        "owns": ["design system choice", "tokens", "component conventions", "brand fit"],
                    },
                    {
                        "role": "prototype-builder",
                        "owns": ["runnable prototype", "responsive states", "component composition"],
                    },
                    {
                        "role": "visual-critic",
                        "owns": ["visual hierarchy", "specificity", "restraint", "anti-generic review"],
                    },
                    {
                        "role": "accessibility-reviewer",
                        "owns": ["keyboard path", "contrast", "focus states", "mobile readability"],
                    },
                ],
                "sequence": [
                    "lock design brief and surface constraints",
                    "select or derive design tokens before prototype work",
                    "build the smallest runnable high-fidelity prototype",
                    "review visual quality and accessibility before implementation handoff",
                ],
                "quality_gates": [
                    "design_brief_gate",
                    "design_token_gate",
                    "prototype_runnable_gate",
                    "visual_quality_gate",
                    "accessibility_gate",
                ],
                "output_artifacts": [
                    ".vidt/product/prototype-design-brief.md",
                    ".vidt/product/stage-council-plan.json",
                ],
                "resume_anchor": ".vidt/product/prototype-design-brief.md",
            }
        )

    return {
        "enabled": len(councils) > 0,
        "reference": STAGE_COUNCIL_REFERENCE,
        "template": STAGE_COUNCIL_TEMPLATE,
        "workflow_bundle": bundle_name,
        "lead_agent": lead_agent,
        "activation_rule": (
            "Only expand a stage council under product-spec-deliver when product-discovery "
            "or prototype-design signals are explicit enough to change the artifact sequence."
        ),
        "explicit_team_request": explicit_team_request,
        "active_councils": [str(item.get("name", "")) for item in councils],
        "councils": councils,
        "fallback": (
            "Keep World-Class Product Architect as a single lead when no product-discovery "
            "or prototype-design council signal is present."
        ),
    }


def build_micro_practices(
    *,
    text: str,
    workflow_bundle: dict[str, object],
    lead_agent: str,
    needs_pre_development_planning: bool,
    needs_iteration: bool,
) -> list[dict[str, object]]:
    lowered = text.lower()
    bundle_name = str(workflow_bundle.get("name", "direct-execution"))
    active: list[dict[str, object]] = []

    def add(name: str, reference: str, reason: str, evidence: list[str]) -> None:
        if any(item.get("name") == name for item in active):
            return
        active.append(
            {
                "name": name,
                "reference": reference,
                "reason": reason,
                "evidence": evidence,
            }
        )

    shared_language_keywords = [
        "acceptance criteria",
        "user flow",
        "api contract",
        "domain",
        "glossary",
        "ubiquitous language",
        "terminology",
        "prd",
        "需求",
        "验收标准",
        "用户流",
        "接口契约",
        "术语",
        "领域语言",
    ]
    feedback_keywords = [
        "bug",
        "fix",
        "fails",
        "failed",
        "still fails",
        "regression",
        "repro",
        "root cause",
        "debug",
        "diagnose",
        "logs",
        "trace",
        "排查",
        "复现",
        "根因",
        "日志",
        "回归",
    ]
    vertical_slice_keywords = [
        "vertical slice",
        "tracer bullet",
        "acceptance criteria",
        "backend contract",
        "api contract",
        "end-to-end",
        "e2e",
        "afk",
        "hitl",
        "issue",
        "ticket",
        "切片",
        "纵向",
        "验收标准",
        "接口契约",
    ]
    system_map_keywords = [
        "zoom out",
        "map the code",
        "module map",
        "callers",
        "callee",
        "call graph",
        "entry points",
        "data flow",
        "event flow",
        "seam",
        "seams",
        "adapter",
        "adapters",
        "模块地图",
        "调用链",
        "入口",
        "调用方",
    ]
    architecture_deepening_keywords = [
        "architecture",
        "architectural",
        "shallow module",
        "deep module",
        "deepening",
        "seam",
        "seams",
        "adapter",
        "adapters",
        "locality",
        "leverage",
        "testability",
        "refactor opportunity",
        "架构",
        "模块",
        "接口",
        "适配器",
        "可测试",
    ]
    change_localization_keywords = [
        "pinpoint",
        "locate the change",
        "where to change",
        "exact files",
        "call chain",
        "call-chain",
        "code site",
        "change site",
        "改动点",
        "改动位置",
        "调用链",
    ]
    project_knowledge_keywords = [
        "onboarding",
        "onboard",
        "unfamiliar codebase",
        "unfamiliar repo",
        "large codebase",
        "project map",
        "knowledge base",
        "code knowledge",
        "project knowledge",
        "上手",
        "陌生",
        "大型项目",
        "代码知识库",
        "项目知识",
    ]

    if bundle_name == "product-spec-deliver" or text_has_any_keyword(lowered, shared_language_keywords):
        add(
            "shared-language-and-decision-capture",
            SHARED_LANGUAGE_REFERENCE,
            "Product, contract, or domain terms should be sharpened before implementation.",
            [
                "confirm or add stable vocabulary",
                "record only hard-to-reverse decisions",
                "use accepted terms in acceptance criteria and slice names",
            ],
        )

    if bundle_name in {"quick-slice-deliver", "root-cause-remediate"} and text_has_any_keyword(
        lowered, feedback_keywords
    ):
        add(
            "feedback-loop-first",
            FEEDBACK_LOOP_FIRST_REFERENCE,
            "Bug or root-cause work needs a runnable pass/fail signal before patching.",
            [
                "feedback loop type",
                "repro command or evidence source",
                "failure before fix and verification after fix",
            ],
        )

    if bundle_name in {"plan-first-build", "product-spec-deliver"} or text_has_any_keyword(
        lowered, vertical_slice_keywords
    ):
        add(
            "vertical-slice-delivery",
            VERTICAL_SLICE_REFERENCE,
            "Planning or product delivery should split into demoable vertical slices rather than horizontal layers.",
            [
                "AFK/HITL classification",
                "dependencies",
                "acceptance and verification evidence per slice",
            ],
        )

    if needs_pre_development_planning or text_has_any_keyword(lowered, system_map_keywords):
        add(
            "system-map",
            SYSTEM_MAP_REFERENCE,
            "The team should zoom out to modules, callers, data flow, and seams before changing code.",
            [
                "entry points",
                "modules and callers",
                "seams and unknowns",
            ],
        )

    if (
        lead_agent == "Technical Trinity"
        and text_has_any_keyword(lowered, architecture_deepening_keywords)
    ) or (
        bundle_name in {"plan-first-build", "govern-change-safely"}
        and text_has_any_keyword(lowered, architecture_deepening_keywords)
    ):
        add(
            "architecture-deepening",
            ARCHITECTURE_DEEPENING_REFERENCE,
            "Architecture work should evaluate depth, locality, leverage, seams, and adapter evidence.",
            [
                "deletion test",
                "adapter reality test",
                "test surface and locality evidence",
            ],
        )

    if needs_iteration and text_has_any_keyword(lowered, feedback_keywords):
        add(
            "feedback-loop-first",
            FEEDBACK_LOOP_FIRST_REFERENCE,
            "Iteration on a regression needs a stable signal before comparing candidates.",
            [
                "baseline failure signal",
                "candidate verification command",
                "keep/retry/rollback/stop evidence",
            ],
        )

    localization_read_only_markers = [
        "只读",
        "不改代码",
        "不要改代码",
        "只审计",
        "仅审计",
        "read-only",
        "read only",
        "audit only",
        "do not change code",
        "no code changes",
    ]
    localization_requested = text_has_any_keyword(lowered, change_localization_keywords)
    localization_read_only = text_has_any_keyword(lowered, localization_read_only_markers)
    if (bundle_name == "audit-fix-deliver" or localization_requested) and not localization_read_only:
        add(
            "change-localization",
            CHANGE_LOCALIZATION_REFERENCE,
            "Pinpoint exact change sites and call chains before editing code, with a bounded token budget per step.",
            [
                "finalized files and line ranges",
                "call chain evidence",
                "step that produced each site",
            ],
        )

    if bundle_name in {"plan-first-build", "capture-project-knowledge"} and (
        needs_pre_development_planning
        or text_has_any_keyword(lowered, project_knowledge_keywords)
    ):
        add(
            "project-knowledge-pyramid",
            PROJECT_KNOWLEDGE_PYRAMID_REFERENCE,
            "A large or unfamiliar target project needs a tiered, drift-checked knowledge map before planning.",
            [
                "L1 overview, L2 module-level, L3 semantic bridge",
                "SHA drift baseline",
                "stale entries and resolution",
            ],
        )

    return active


def build_workflow_bundle(
    *,
    text: str,
    lead_agent: str,
    needs_pre_development_planning: bool,
    needs_iteration: bool,
    needs_project_knowledge_capture: bool,
    needs_release_gate: bool,
    needs_git_workflow: bool,
    sentinel_overlay: bool,
) -> dict[str, object]:
    root_cause_keywords = [
        "root cause",
        "根因",
        "still fails",
        "failed again",
        "logs",
        "log",
        "repro",
        "复现",
        "排查",
        "investigate",
        "debug",
        "why is this broken",
    ]
    audit_keywords = [
        "review",
        "audit",
        "security review",
        "审计",
        "代码审查",
        "漏洞",
        "refactor advice",
    ]
    product_keywords = [
        "product brief",
        "prd",
        "acceptance criteria",
        "user flow",
        "scope",
        "mvp",
        "onboarding",
        "signup",
        "feature brief",
        "需求拆解",
        "验收标准",
        "用户流",
        "用户旅程",
        "范围",
        "需求文档",
    ]
    beta_keywords = [
        "beta",
        "closed beta",
        "internal beta",
        "dogfood",
        "pilot users",
        "user testing",
        "usability test",
        "feedback cohort",
        "cohort",
        "内测",
        "灰度用户",
        "试用用户",
        "用户反馈",
        "可用性测试",
        "种子用户",
    ]
    post_release_keywords = [
        "post-release",
        "post release",
        "after launch",
        "after release",
        "rollout feedback",
        "production feedback",
        "customer feedback",
        "telemetry",
        "observability",
        "发布后",
        "上线后",
        "上线反馈",
        "用户反馈回流",
        "真实反馈",
        "生产反馈",
        "发布后复盘",
        "放量后",
        "灰度后",
    ]
    governance_keywords = [
        "governance",
        "review bar",
        "release checklist",
        "rollback",
        "stop condition",
        "branch policy",
        "release hygiene",
        "风险门禁",
        "回滚",
        "停止条件",
        "发布门禁",
        "提交流程",
        "分支策略",
    ]
    multi_expert_split_keywords = [
        "微服务",
        "microservice",
        "micro-service",
        "services split",
        "服务拆分",
        "服务化拆分",
        "模块拆分",
        "拆分迁移",
        "monolith to",
        "单体拆分",
        "单体重构",
        "decompose",
        "解耦",
        "多模块",
        "多服务",
        "多域",
        "multi-domain",
        "跨域",
        "系统拆分",
        "架构拆分",
        "架构重构",
    ]
    multi_expert_frontend_keywords = [
        "React性能全面优化",
        "React 性能全面优化",
        "React 应用全面性能优化",
        "react performance overhaul",
        "react app performance overhaul",
        "全面性能优化",
        "全面前端性能优化",
        "frontend performance overhaul",
    ]
    multi_expert_system_keywords = [
        "系统重构方案",
        "系统重构规划",
        "整体重构方案",
        "大型系统重构",
        "system refactor plan",
        "system redesign plan",
        "system re-architecture",
    ]

    def build_multi_expert_bundle(kind: str) -> dict[str, object]:
        if kind == "frontend":
            reason = (
                "The request is a broad frontend performance overhaul, so runtime, build, "
                "and code-quality specialists should collaborate before reducing it to a single product-delivery path."
            )
            experts = [
                {
                    "role": "frontend-performance-specialist",
                    "focus": "runtime rendering, hydration, interaction latency, and browser profiling",
                },
                {
                    "role": "build-tool-specialist",
                    "focus": "bundle size, code splitting, asset loading, and build pipeline bottlenecks",
                },
                {
                    "role": "code-review-specialist",
                    "focus": "component structure, state boundaries, memoization, and regression risk",
                },
            ]
            steps = [
                "separate runtime, build, and code-structure performance hypotheses",
                "identify the cheapest measurement for each hypothesis before changing code",
                "rank fixes by user-visible impact, implementation risk, and rollback cost",
                "turn the selected path into narrow implementation slices only after the diagnosis is coherent",
            ]
            progress_anchor = ".vidt/performance/frontend-performance-plan.md"
            resume_artifacts = [
                ".vidt/performance/frontend-performance-plan.md",
                ".vidt/performance/performance-hypotheses.md",
            ]
        elif kind == "system":
            reason = (
                "The request is a broad system refactor plan, so architecture, data, and delivery specialists "
                "should collaborate before committing to one execution path."
            )
            experts = [
                {
                    "role": "architecture-specialist",
                    "focus": "module boundaries, ownership seams, coupling, and architecture risk",
                },
                {
                    "role": "data-persistence-specialist",
                    "focus": "state ownership, migration sequencing, compatibility, and rollback",
                },
                {
                    "role": "delivery-devops-specialist",
                    "focus": "release slicing, observability, deployment safety, and incremental rollout",
                },
            ]
            steps = [
                "map the current system boundaries and high-risk dependencies",
                "separate architecture, data, and delivery decisions before coding",
                "identify reversible slices and irreversible decisions",
                "define the first executable planning artifact and evidence needed to proceed",
            ]
            progress_anchor = ".vidt/architecture/system-refactor-plan.md"
            resume_artifacts = [
                ".vidt/architecture/system-refactor-plan.md",
                ".vidt/architecture/refactor-decisions.md",
            ]
        else:
            reason = "The request is a multi-domain architecture split or decomposition (e.g. microservices, monolith-to-services, cross-domain refactor), so multiple specialists (architecture, data/persistence, delivery/DevOps) should collaborate up front rather than a single expert defaulting to direct execution."
            experts = [
                {
                    "role": "architecture-specialist",
                    "focus": "service boundaries, coupling, migration risk, and ownership seams",
                },
                {
                    "role": "data-persistence-specialist",
                    "focus": "data ownership, migration sequencing, consistency, and rollback",
                },
                {
                    "role": "delivery-devops-specialist",
                    "focus": "deployment topology, observability, release safety, and incremental rollout",
                },
            ]
            steps = [
                "convene the relevant specialists: architecture, data/persistence, and delivery/DevOps",
                "align on split boundaries, data ownership, and deployment contracts before coding",
                "capture cross-cutting decisions and risks that no single specialist owns alone",
                "split execution into vertical slices that respect the agreed boundaries",
            ]
            progress_anchor = ".vidt/architecture/split-decisions.md"
            resume_artifacts = [
                ".vidt/architecture/split-decisions.md",
                ".vidt/architecture/data-ownership.md",
            ]

        return {
            "name": "multi-expert-execution",
            "confidence": 0.9,
            "source": f"{kind}-keyword",
            "reason": reason,
            "runtime_claim": "soft_orchestration_until_runtime_evidence",
            "multi_expert_plan": {
                "runtime_evidence_required": True,
                "runtime_evidence": [
                    "spawn",
                    "wait",
                    "merge",
                ],
                "fallback": "Use clearly labeled specialist lenses in one response when the host does not expose real subagent runtime evidence.",
                "experts": experts,
            },
            "steps": steps,
            "progress_anchor_recommended": progress_anchor,
            "resume_artifacts": resume_artifacts,
        }

    if needs_project_knowledge_capture:
        return {
            "name": "capture-project-knowledge",
            "confidence": 0.94,
            "source": "process-skill",
            "reason": "The request is repository AI onboarding or project-local skill capture, so software-risk lanes should be identified first and context writing should follow skill-forge's project knowledge capture protocol.",
            "steps": [
                "inventory existing project guidance, docs, config, tests, scripts, and entrypoints",
                "split only independent codebase analysis lanes and avoid duplicated subagent work",
                "synthesize verified facts into concise AGENTS.md guidance",
                "create or update only scenario-specific project-local .agents/skills",
                "validate referenced files, commands, and remaining unknowns before handoff",
            ],
            "progress_anchor_recommended": "AGENTS.md",
            "resume_artifacts": [
                "AGENTS.md",
                ".agents/skills/",
                "skill-forge/references/project-knowledge-capture-protocol.md",
            ],
        }

    if needs_release_gate:
        return {
            "name": "ship-hold-remediate",
            "confidence": 0.98,
            "source": "process-skill",
            "reason": "Formal release readiness or acceptance is central, so release gate drives the journey.",
            "steps": [
                "run the release gate first",
                "answer ship or hold with explicit evidence",
                "if hold, generate the next remediation brief",
                "resume through the release-gate outputs instead of restarting from scratch",
            ],
            "progress_anchor_recommended": "evals/release-gate/release-gate-report.md",
            "resume_artifacts": [
                "evals/release-gate/release-gate-report.md",
                "evals/release-gate/next-iteration-brief.json",
            ],
        }

    if needs_pre_development_planning:
        return {
            "name": "plan-first-build",
            "confidence": 0.96,
            "source": "process-skill",
            "reason": "The request is rewrite/migration/plan-first shaped, so planning pack and durable progress anchor come before execution.",
            "steps": [
                "lock transformation scope, target, and constraints",
                "create a compact system map when module ownership or callers are unclear",
                "generate the planning pack",
                "split execution into AFK/HITL vertical slices",
                "create or refresh the progress anchor",
                "return to normal delivery routing only after the planning pack exists",
            ],
            "progress_anchor_recommended": "docs/progress/MASTER.md",
            "resume_artifacts": [
                "docs/progress/MASTER.md",
                "docs/analysis/project-overview.md",
                "docs/plan/task-breakdown.md",
            ],
        }

    if text_has_any_keyword(text, post_release_keywords):
        return {
            "name": "post-release-close-loop",
            "confidence": 0.89,
            "source": "keyword",
            "reason": "The request is post-release feedback shaped, so shipped signals, telemetry, and real-user feedback should feed a structured triage and remediation loop instead of ad hoc notes.",
            "steps": [
                "initialize the post-release workspace and current signal report",
                "cluster shipped signals by source, severity, and affected area",
                "evaluate whether to monitor, iterate, or escalate",
                "write feedback back into product or governance anchors before reopening remediation",
            ],
            "progress_anchor_recommended": ".vidt/post-release/triage-summary.md",
            "resume_artifacts": [
                ".vidt/post-release/rollout-summary.md",
                ".vidt/post-release/current-signals.json",
                ".vidt/post-release/triage-summary.md",
            ],
        }

    if needs_iteration or (
        (lead_agent == "Sentinel Architect (NB)" or sentinel_overlay)
        and text_has_any_keyword(text, root_cause_keywords)
    ):
        keyword_triggered = text_has_any_keyword(text, root_cause_keywords)
        return {
            "name": "root-cause-remediate",
            "confidence": 0.93 if needs_iteration else 0.84,
            "source": "process-skill" if needs_iteration else "keyword+lead",
            "reason": "The request needs evidence-backed diagnosis or bounded remediation, so the loop should preserve validating evidence and rollback decisions.",
            "steps": [
                "freeze guesswork and summarize what is already known",
                "establish the smallest reliable feedback loop",
                "collect the missing evidence or run the next validating check",
                "test one remediation hypothesis at a time",
                "keep, retry, rollback, or stop based on evidence",
            ],
            "progress_anchor_recommended": ".vidt/iterations/current-round-memory.md",
            "resume_artifacts": [
                ".vidt/iterations/current-round-memory.md",
                ".vidt/iterations/distilled-patterns.md",
            ],
        }

    audit_batch_fix = is_audit_batch_fix_context(text)
    if lead_agent == "Code Audit Council" or text_has_any_keyword(text, audit_keywords) or audit_batch_fix:
        keyword_triggered = text_has_any_keyword(text, audit_keywords) or audit_batch_fix
        steps = [
            "produce findings first",
            "separate blockers from follow-up improvements",
            "define the smallest safe remediation step",
            "enter Git delivery only if commit, push, or PR actions are requested",
        ]
        if audit_batch_fix:
            steps = [
                "freeze the audit finding list before implementation",
                "classify findings into P0/P1/P2 batches with scope and dependencies",
                "fix one severity batch at a time, starting with P0",
                "verify each batch independently before staging it",
                "create one independent commit per accepted batch using the repo commit convention",
                "carry unresolved lower-severity findings into the remaining-findings ledger",
            ]
        return {
            "name": "audit-fix-deliver",
            "confidence": 0.9
            if audit_batch_fix
            else 0.88
            if lead_agent == "Code Audit Council" and keyword_triggered
            else 0.78,
            "source": "audit-batch-fix"
            if audit_batch_fix
            else "lead+keyword"
            if keyword_triggered
            else "lead-default",
            "reason": (
                "The request is review-led; when the user asks for P0/P1/P2 batch "
                "remediation, findings must be frozen, fixed one batch at a time, "
                "verified independently, and committed separately."
            ),
            "steps": steps,
            "progress_anchor_recommended": ".vidt/iterations/current-round-memory.md",
            "resume_artifacts": [
                ".vidt/iterations/current-round-memory.md",
                ".vidt/iterations/distilled-patterns.md",
            ],
        }

    if lead_agent == "World-Class Product Architect" and text_has_any_keyword(text, beta_keywords):
        return {
            "name": "beta-feedback-ramp",
            "confidence": 0.9,
            "source": "lead+keyword",
            "reason": "The request is beta-validation shaped, so product promise, cohort design, round-by-round sample growth, and structured feedback gates should be explicit before broader rollout.",
            "steps": [
                "define the validation objective, release boundary, and exit criteria for each beta round",
                "start with a small simulated or seed-user cohort before implementation or broad exposure",
                "expand to larger internal-beta cohorts only when the previous round clears its gate",
                "log feedback, severity, and ship-or-hold decisions round by round",
            ],
            "progress_anchor_recommended": ".vidt/beta/program-overview.md",
            "resume_artifacts": [
                ".vidt/beta/program-overview.md",
                ".vidt/beta/cohort-matrix.md",
                ".vidt/beta/feedback-ledger.md",
            ],
        }

    if is_simple_direct_answer_request(text, lead_agent):
        return {
            "name": "direct-execution",
            "confidence": 0.78,
            "source": "single-domain-direct-answer",
            "reason": "The request is a simple single-domain question, so the answer should stay direct and avoid product, harness, Team Engine, or resume-artifact overhead.",
            "steps": [
                "answer the technical question directly",
                "include concrete checks or examples only when they help the user act",
                "avoid workflow artifacts unless the user asks to implement, verify, commit, release, or iterate",
            ],
            "progress_anchor_recommended": None,
            "resume_artifacts": [],
        }

    if text_has_any_keyword(text, multi_expert_frontend_keywords):
        return build_multi_expert_bundle("frontend")

    if text_has_any_keyword(text, multi_expert_system_keywords):
        return build_multi_expert_bundle("system")

    if text_has_any_keyword(text, multi_expert_split_keywords):
        return build_multi_expert_bundle("architecture")

    if lead_agent == "World-Class Product Architect" or text_has_any_keyword(text, product_keywords):
        return {
            "name": "product-spec-deliver",
            "confidence": 0.86 if lead_agent == "World-Class Product Architect" else 0.74,
            "source": "lead-default" if lead_agent == "World-Class Product Architect" else "keyword",
            "reason": "The request is product-definition or UX-delivery shaped, so the journey should lock scope, user flow, acceptance criteria, and frontend/backend contract questions before implementation drifts.",
            "steps": [
                "define the target user, outcome, and smallest acceptable scope",
                "sharpen shared language for ambiguous product, state, or contract terms",
                "write the core user flow and key failure states",
                "turn the request into acceptance criteria the team can verify",
                "split multi-layer work into AFK/HITL vertical slices when needed",
                "surface frontend/backend contract questions before coding",
            ],
            "progress_anchor_recommended": ".vidt/product/current-slice.md",
            "resume_artifacts": [
                ".vidt/product/current-slice.md",
                ".vidt/product/acceptance-criteria.md",
                ".vidt/product/contract-questions.md",
            ],
        }

    if lead_agent in {"Git Workflow Guardian", "Sentinel Architect (NB)"} or text_has_any_keyword(
        text, governance_keywords
    ):
        return {
            "name": "govern-change-safely",
            "confidence": 0.82 if lead_agent in {"Git Workflow Guardian", "Sentinel Architect (NB)"} else 0.7,
            "source": "lead-default"
            if lead_agent in {"Git Workflow Guardian", "Sentinel Architect (NB)"}
            else "keyword",
            "reason": "The request is workflow- or risk-governance shaped, so execution mode, verification, rollback, and delivery sequencing should be explicit before commands or release actions begin.",
            "steps": [
                "define the owner, execution mode, and stop conditions",
                "lock the smallest safe next action",
                "state verification evidence and rollback conditions",
                "enter git or release actions only after the guardrails are explicit",
            ],
            "progress_anchor_recommended": ".vidt/governance/change-plan.md",
            "resume_artifacts": [
                ".vidt/governance/change-plan.md",
                ".vidt/governance/release-checklist.md",
            ],
        }

    if is_quick_slice_context(text) and not needs_git_workflow:
        return {
            "name": "quick-slice-deliver",
            "confidence": 0.72,
            "source": "keyword+lead",
            "reason": "The request is a narrow implementation or bug-fix slice, so it should keep a small delivery brief, durable project context, targeted verification, and self-review without expanding into a full planning or product workflow.",
            "steps": [
                "clarify only route-changing gaps",
                "build or name the feedback loop first when the slice is a bug or regression",
                "record intent, non-goals, acceptance criteria, and verification evidence",
                "create or refresh durable project context when needed",
                "implement the smallest coherent change and self-review it",
            ],
            "progress_anchor_recommended": ".vidt/delivery/current-slice.md",
            "resume_artifacts": [
                ".vidt/delivery/current-slice.md",
                ".vidt/delivery/status.yaml",
                ".vidt/context/project-context.md",
            ],
        }

    return {
        "name": "direct-execution",
        "confidence": 0.35,
        "source": "fallback",
        "reason": "No larger recurring journey is needed beyond the selected lead and process skills.",
        "steps": [
            "keep the route lightweight",
            "execute the smallest next action under the current lead",
        ],
        "progress_anchor_recommended": None,
        "resume_artifacts": [],
    }


def build_workflow_bundle_bootstrap(
    bundle_name: str,
    micro_practice_names: list[str] | None = None,
) -> dict[str, object]:
    active_practice_names = [name for name in (micro_practice_names or []) if str(name).strip()]

    def with_micro_practices(block: dict[str, object]) -> dict[str, object]:
        if not active_practice_names:
            return block
        commands = block.get("commands", [])
        artifacts = block.get("artifacts", [])
        if not isinstance(commands, list):
            commands = []
        if not isinstance(artifacts, list):
            artifacts = []
        practice_command = 'python scripts/init_micro_practices.py --root . --text "<user request>" --pretty'
        update_command = "python scripts/update_micro_practices.py --ledger .vidt/practices/micro-practice-ledger.json --name <practice-name> --status satisfied --evidence \"<evidence>\" --pretty"
        evaluation_command = "python scripts/evaluate_micro_practices.py --ledger .vidt/practices/micro-practice-ledger.json --pretty"
        practice_artifacts = [
            ".vidt/practices/micro-practice-ledger.json",
            ".vidt/practices/micro-practice-ledger.md",
        ]
        block["commands"] = [*commands, practice_command]
        block["artifacts"] = [*artifacts, *practice_artifacts]
        block["micro_practice_ledger"] = {
            "required": True,
            "active_practices": active_practice_names,
            "command": practice_command,
            "update_command": update_command,
            "evaluation_command": evaluation_command,
            "resume_anchor": ".vidt/practices/micro-practice-ledger.json",
            "schema": "references/micro-practice-ledger.schema.json",
            "evaluation_schema": "references/micro-practice-evaluation.schema.json",
        }
        return block

    if bundle_name == "beta-feedback-ramp":
        return with_micro_practices({
            "required": True,
            "reference": "references/beta-validation-playbook.md",
            "commands": [
                "python scripts/init_beta_validation.py --root . --pretty",
                "python scripts/init_beta_simulation.py --root . --round-id round-0 --phase \"pre-build concept smoke\" --objective \"<objective>\" --pretty",
            ],
            "artifacts": [
                ".vidt/beta/program-overview.md",
                ".vidt/beta/cohort-matrix.md",
                ".vidt/beta/feedback-ledger.md",
                ".vidt/beta/personas",
                ".vidt/beta/simulation-configs/round-0.json",
            ],
            "resume_anchor": ".vidt/beta/program-overview.md",
        })
    if bundle_name == "product-spec-deliver":
        return with_micro_practices({
            "required": True,
            "reference": "references/product-delivery-playbook.md",
            "commands": [
                "python scripts/init_product_delivery.py --root . --pretty",
            ],
            "artifacts": [
                ".vidt/product/current-slice.md",
                ".vidt/product/acceptance-criteria.md",
                ".vidt/product/contract-questions.md",
            ],
            "resume_anchor": ".vidt/product/current-slice.md",
        })
    if bundle_name == "quick-slice-deliver":
        return with_micro_practices({
            "required": True,
            "reference": "references/quick-slice-delivery-playbook.md",
            "commands": [
                "python scripts/init_project_context.py --root . --pretty",
                "python scripts/init_quick_slice.py --root . --pretty",
            ],
            "artifacts": [
                ".vidt/context/project-context.md",
                ".vidt/delivery/current-slice.md",
                ".vidt/delivery/status.yaml",
            ],
            "resume_anchor": ".vidt/delivery/current-slice.md",
        })
    if bundle_name == "govern-change-safely":
        return with_micro_practices({
            "required": True,
            "reference": "references/technical-governance-playbook.md",
            "commands": [
                "python scripts/init_technical_governance.py --root . --pretty",
            ],
            "artifacts": [
                ".vidt/governance/change-plan.md",
                ".vidt/governance/release-checklist.md",
            ],
            "resume_anchor": ".vidt/governance/change-plan.md",
        })
    if bundle_name == "post-release-close-loop":
        return with_micro_practices({
            "required": True,
            "reference": "references/post-release-feedback-playbook.md",
            "commands": [
                "python scripts/init_post_release_feedback.py --root . --pretty",
            ],
            "artifacts": [
                ".vidt/post-release/rollout-summary.md",
                ".vidt/post-release/feedback-ledger.md",
                ".vidt/post-release/current-signals.json",
                ".vidt/post-release/triage-summary.md",
            ],
            "resume_anchor": ".vidt/post-release/triage-summary.md",
        })
    if bundle_name == "capture-project-knowledge":
        return with_micro_practices({
            "required": True,
            "reference": "skill-forge/references/project-knowledge-capture-protocol.md",
            "commands": [
                "rg --files",
                "find . -maxdepth 3 -name AGENTS.md -o -path '*/.agents/skills/*'",
                "python validate.py --repo-only",
            ],
            "artifacts": [
                "AGENTS.md",
                ".agents/skills/",
            ],
            "resume_anchor": "AGENTS.md",
        })
    return with_micro_practices({
        "required": False,
        "reference": None,
        "commands": [],
        "artifacts": [],
        "resume_anchor": None,
    })


def build_quality_gate(
    *,
    lead_agent: str,
    assistants: list[str],
    workflow_bundle: dict[str, object],
    clarifying_question: str | None,
) -> dict[str, object]:
    bundle_name = str(workflow_bundle.get("name", "direct-execution"))
    steps = [str(item) for item in workflow_bundle.get("steps", []) if str(item).strip()]
    route_assumption = (
        "Request is clear enough to route."
        if clarifying_question is None
        else "Route is provisional until the clarification answer changes scope, stack, or expected output."
    )
    if bundle_name == "plan-first-build":
        verification = "planning pack and docs/progress/MASTER.md exist before implementation starts"
    elif bundle_name == "product-spec-deliver":
        verification = "current slice, acceptance criteria, and contract questions are written"
    elif bundle_name == "quick-slice-deliver":
        verification = "quick slice brief, delivery status, project context, and targeted verification evidence are present"
    elif bundle_name == "beta-feedback-ramp":
        verification = "cohort plan, ramp plan, feedback ledger, and round gate evidence exist"
    elif bundle_name == "audit-fix-deliver":
        verification = "severity-ordered findings and the smallest remediation step are explicit"
    elif bundle_name == "govern-change-safely":
        verification = "owner, stop conditions, verification evidence, and rollback conditions are explicit"
    elif bundle_name == "root-cause-remediate":
        verification = "one hypothesis is tested against evidence and ends in keep, retry, rollback, or stop"
    elif bundle_name == "ship-hold-remediate":
        verification = "release gate returns ship or hold and preserves the follow-up artifact"
    elif bundle_name == "post-release-close-loop":
        verification = "post-release signals are triaged into monitor, iterate, or escalate"
    elif bundle_name == "capture-project-knowledge":
        verification = "AGENTS.md and any project-local .agents/skills contain only repository-verified facts and validated references"
    else:
        verification = "the lead can name the smallest next action and observable result"

    return {
        "reference": QUALITY_GUARDRAIL_REFERENCE,
        "principles": [
            "surface-assumptions",
            "smallest-defensible-bundle",
            "surgical-execution",
            "verifiable-closure",
        ],
        "assumption_check": route_assumption,
        "minimality_check": (
            f"{bundle_name} is selected because it is the smallest bundle matching the route; "
            f"assistants={assistants or []}."
        ),
        "surgical_scope": {
            "lead_owner": lead_agent,
            "assistants": assistants,
            "workflow_bundle": bundle_name,
            "in_scope_lanes": steps,
        },
        "verification_check": verification,
        "clarification_required": clarifying_question is not None,
    }


def build_harness_constraint_gate(
    *,
    workflow_bundle: dict[str, object],
    lead_agent: str,
    assistants: list[str],
    request_text: str,
) -> dict[str, object]:
    bundle_name = str(workflow_bundle.get("name", "direct-execution"))
    required = bundle_name in HARNESS_CONSTRAINT_WORKFLOWS
    task_summary = " ".join(request_text.split())[:160] or "<task summary>"
    if required:
        reason = "Code-facing routes must create or refresh the Harness engineering constraints before implementation."
    elif bundle_name == "direct-execution":
        reason = "Direct-answer routes stay lightweight; Harness constraints are optional unless the user asks to implement or verify code."
    else:
        reason = "This route is evidence, release, beta, or post-release focused; Harness constraints are optional unless implementation begins."

    return {
        "required": required,
        "reference": HARNESS_CONSTRAINT_REFERENCE,
        "artifact": HARNESS_CONSTRAINT_ARTIFACT,
        "command": HARNESS_CONSTRAINT_COMMAND,
        "principles": [
            "constraints-before-code",
            "single-constraint-file",
            "current-rules-not-history",
            "verify-before-implementation",
        ],
        "lead_owner": lead_agent,
        "assistants": assistants,
        "workflow_bundle": bundle_name,
        "task_summary": task_summary,
        "reason": reason,
        "verification_check": (
            f"{HARNESS_CONSTRAINT_ARTIFACT} exists and records scope, non-negotiable constraints, "
            "forbidden changes, verification evidence, and rollback/stop conditions."
        ),
    }


def build_team_engine_gate(
    *,
    workflow_bundle: dict[str, object],
    lead_agent: str,
    assistants: list[str],
    needs_release_gate: bool,
    needs_git_workflow: bool,
    needs_iteration: bool,
) -> dict[str, object]:
    bundle_name = str(workflow_bundle.get("name", "direct-execution"))
    required = (
        bundle_name in TEAM_ENGINE_REQUIRED_WORKFLOWS
        or needs_release_gate
        or needs_git_workflow
        or needs_iteration
    )
    max_cycles = 3
    if bundle_name == "root-cause-remediate":
        max_cycles = 3
    elif bundle_name == "ship-hold-remediate":
        max_cycles = 2
    acceptance_gates_by_bundle = {
        "plan-first-build": [
            "scope_gate",
            "planning_pack_gate",
            "dependency_gate",
            "role_separation_gate",
            "delivery_cycle_report_gate",
        ],
        "product-spec-deliver": [
            "scope_gate",
            "shared_language_gate",
            "acceptance_criteria_gate",
            "vertical_slice_gate",
            "frontend_backend_contract_gate",
            "role_separation_gate",
            "delivery_cycle_report_gate",
        ],
        "quick-slice-deliver": [
            "scope_gate",
            "acceptance_criteria_gate",
            "feedback_loop_gate",
            "tests_or_verification_gate",
            "role_separation_gate",
            "delivery_cycle_report_gate",
        ],
        "audit-fix-deliver": [
            "finding_evidence_gate",
            "severity_gate",
            "remediation_patch_gate",
            "false_positive_risk_gate",
            "role_separation_gate",
        ],
        "govern-change-safely": [
            "owner_gate",
            "stop_condition_gate",
            "rollback_gate",
            "verification_evidence_gate",
            "role_separation_gate",
        ],
        "root-cause-remediate": [
            "reproduction_or_evidence_gate",
            "feedback_loop_gate",
            "single_hypothesis_gate",
            "remediation_patch_gate",
            "rollback_decision_gate",
            "role_separation_gate",
        ],
        "ship-hold-remediate": [
            "release_gate_result_gate",
            "blocking_issue_gate",
            "rollback_gate",
            "post_release_feedback_gate",
            "ship_hold_evidence_gate",
        ],
    }
    gates = acceptance_gates_by_bundle.get(
        bundle_name,
        ["scope_gate", "verification_evidence_gate", "role_separation_gate"],
    )
    worker_role = "implementation-worker"
    if lead_agent == "Code Audit Council":
        worker_role = "remediation-worker"
    elif lead_agent == "World-Class Product Architect":
        worker_role = "product-delivery-worker"
    elif lead_agent == "Git Workflow Guardian":
        worker_role = "delivery-governance-worker"
    verifier_role = "delivery-verifier"
    if lead_agent == "Code Audit Council":
        verifier_role = "audit-verifier"
    elif bundle_name == "ship-hold-remediate":
        verifier_role = "release-verifier"

    return {
        "required": required,
        "reference": TEAM_ENGINE_REFERENCE,
        "cycle_reference": WORKER_VERIFIER_REFERENCE,
        "workflow_bundle": bundle_name,
        "state_machine": [
            "planned",
            "spawned",
            "running",
            "produced",
            "verifying",
            "retrying",
            "passed",
            "failed",
            "spec_violation",
            "hold",
            "escalated",
            "accepted",
        ],
        "work_order_contract": "WorkOrder",
        "worker_output_contract": "ImplementationOutput",
        "verifier_output_contract": "VerificationReport",
        "remediation_patch_contract": "RemediationPatch",
        "cycle_report_contract": "DeliveryCycleReport",
        "lead_role": lead_agent,
        "worker_role": worker_role,
        "verifier_role": verifier_role,
        "assistants": assistants,
        "max_cycles": max_cycles,
        "acceptance_gates": gates,
        "producer_can_self_pass": False,
        "leader_accept_requires_cycle_report": True,
        "verifier_fail_requires_remediation_patch": True,
        "runtime_claim": "soft_orchestration_only",
        "team_engine_closure_verdict": "pass_with_watch" if required else "optional",
        "reason": (
            "This route needs independent Worker/Verifier evidence before Lead acceptance."
            if required
            else "This route can stay lightweight unless it turns into code, release, Git, or user-visible delivery."
        ),
    }


def build_external_agent_backend_plan(
    *,
    workflow_bundle: dict[str, object],
    lead_agent: str,
    team_engine_gate: dict[str, object],
) -> dict[str, object]:
    bundle_name = str(workflow_bundle.get("name", "direct-execution"))
    worker_role = str(team_engine_gate.get("worker_role", "implementation-worker"))
    verifier_role = str(team_engine_gate.get("verifier_role", "delivery-verifier"))
    task_id = bundle_name.replace("-", "_") + "_task"
    return {
        "enabled": bool(team_engine_gate.get("required")),
        "reference": EXTERNAL_AGENT_BACKEND_REFERENCE,
        "orchestration_mode": "soft_external_backend",
        "runtime_claim": "soft_orchestration_only",
        "task_id": task_id,
        "objective": str(workflow_bundle.get("reason", "coordinate delivery through role-separated soft orchestration")),
        "backend_matrix": {
            "lead": {
                "backend_id": "lead-session-001",
                "provider": "codex",
                "role": "lead",
                "context_policy": "summary_plus_artifact",
                "output_contract": "WorkOrder",
                "can_write_artifact": False,
                "can_write_verdict": False,
                "can_accept_task": False,
            },
            "worker": {
                "backend_id": "worker-session-001",
                "provider": "codex",
                "role": worker_role,
                "context_policy": "task_only",
                "output_contract": "ImplementationOutput",
                "can_write_artifact": True,
                "can_write_verdict": False,
                "can_accept_task": False,
            },
            "verifier": {
                "backend_id": "verifier-session-001",
                "provider": "codex",
                "role": verifier_role,
                "context_policy": "artifact_only",
                "output_contract": "VerificationReport + RemediationPatch",
                "can_write_artifact": False,
                "can_write_verdict": True,
                "can_accept_task": False,
            },
        },
        "isolation_contract": {
            "shared_full_context_allowed": False,
            "worker_reads_verifier_private_reasoning": False,
            "verifier_reads_worker_private_reasoning": False,
            "user_messages_route_to": "lead",
        },
        "fallback_policy": {
            "unavailable_backend": "downgrade to single_thread_simulated and mark backend_orchestration_verdict = simulated",
            "malformed_output": "request structured repair once, then hold",
            "role_boundary_violation": "hold and regenerate WorkOrder with stricter role boundaries",
            "max_cycles_exhausted": "escalate to human decision",
        },
        "required_outputs": [
            "WorkOrder",
            "ImplementationOutput",
            "VerificationReport",
            "RemediationPatch",
            "DeliveryCycleReport",
        ],
        "backend_orchestration_verdict": "simulated",
        "team_engine_closure_verdict": str(team_engine_gate.get("team_engine_closure_verdict", "pass_with_watch")),
        "boundary_note": (
            f"{lead_agent} remains the semantic lead, but acceptance requires DeliveryCycleReport evidence."
        ),
    }


class HostCapabilities(TypedDict):
    """Host 能力探测结果

    字段:
        spawn_supported/wait_supported/merge_supported: real-subagent 完整链路
        create_session_supported/kill_session_supported/restart_session_supported:
            multi-session 完整生命周期
        evidence_source: 能力来源（declared=环境变量声明 / probed=自动探测）
    """
    spawn_supported: bool
    wait_supported: bool
    merge_supported: bool
    create_session_supported: bool
    kill_session_supported: bool
    restart_session_supported: bool
    evidence_source: Literal["declared", "probed"]


class TierSelectionResult(TypedDict):
    """Tier 选择结果

    字段:
        runtime_claim: 最终选择的 tier
        evidence: 选择证据（含 evidence_source 和 smoke_test 结果）
        downgraded_from: 如果降级，原始 candidate tier
        downgrade_reason: 降级原因
    """
    runtime_claim: str
    evidence: dict[str, object]
    downgraded_from: str
    downgrade_reason: str


def probe_host_capabilities() -> HostCapabilities:
    """探测 host 的 runtime 能力

    两层设计：
    1. 优先读取六个原子能力环境变量（host 主动声明）
    2. 无环境变量时 fallback 到自动探测（检查可用工具）

    返回:
        HostCapabilities TypedDict
    """
    env_names = {
        "spawn_supported": "HOST_SUPPORTS_SPAWN",
        "wait_supported": "HOST_SUPPORTS_WAIT",
        "merge_supported": "HOST_SUPPORTS_MERGE",
        "create_session_supported": "HOST_SUPPORTS_CREATE_SESSION",
        "kill_session_supported": "HOST_SUPPORTS_KILL_SESSION",
        "restart_session_supported": "HOST_SUPPORTS_RESTART_SESSION",
    }
    declared = {
        field: os.environ.get(env_name, "").strip().lower()
        for field, env_name in env_names.items()
    }

    if any(declared.values()):
        return HostCapabilities(
            **{
                field: value in ("1", "true", "yes")
                for field, value in declared.items()
            },
            evidence_source="declared",
        )

    return HostCapabilities(
        spawn_supported=False,
        wait_supported=False,
        merge_supported=False,
        create_session_supported=False,
        kill_session_supported=False,
        restart_session_supported=False,
        evidence_source="probed",
    )


def runtime_smoke_test(
    tier: str,
    host_capabilities: HostCapabilities,
) -> dict[str, object]:
    """对选择的 tier 执行最小化 smoke test

    参数:
        tier: 已选择的 runtime_claim
        host_capabilities: probe_host_capabilities 的输出

    返回:
        dict 含 passed / reason 字段
    """
    if tier == "soft_orchestration_only":
        return {"passed": True, "reason": "soft_orchestration_only 无需 smoke test"}

    if tier == "real_subagent_runtime":
        required = ("spawn_supported", "wait_supported", "merge_supported")
        missing = [name.removesuffix("_supported") for name in required if not host_capabilities.get(name, False)]
        if missing:
            return {"passed": False, "reason": f"host 缺少 {'/'.join(missing)}，smoke test 失败"}
        return {"passed": True, "reason": "spawn/wait/merge 完整链路已声明"}

    if tier == "single_backend_multi_session":
        required = (
            "create_session_supported",
            "kill_session_supported",
            "restart_session_supported",
        )
        missing = [name.removesuffix("_supported") for name in required if not host_capabilities.get(name, False)]
        if missing:
            return {"passed": False, "reason": f"host 缺少 {'/'.join(missing)}，smoke test 失败"}
        return {"passed": True, "reason": "create_session/kill_session/restart_session 完整链路已声明"}

    return {"passed": False, "reason": f"未知 tier: {tier}"}


def select_runtime_tier(
    candidate_runtime_claim: str,
    candidate_multi_session_claim: str,
    host_capabilities: HostCapabilities | None = None,
    run_smoke_test: bool = True,
) -> TierSelectionResult:
    """基于 host 实际能力选择最终 runtime tier

    参数:
        candidate_runtime_claim: real_subagent_runtime 或 soft_orchestration_only
        candidate_multi_session_claim: single_backend_multi_session 或 soft_orchestration_only
        host_capabilities: probe_host_capabilities 的输出，None 时内部调用
        run_smoke_test: 是否执行 runtime smoke test

    返回:
        TierSelectionResult TypedDict
    """
    if host_capabilities is None:
        host_capabilities = probe_host_capabilities()

    allowed_candidates = ["soft_orchestration_only"]
    if candidate_multi_session_claim == "single_backend_multi_session":
        allowed_candidates.append("single_backend_multi_session")
    if candidate_runtime_claim == "real_subagent_runtime":
        allowed_candidates.append("real_subagent_runtime")

    real_chain_ready = all(
        bool(host_capabilities.get(name, False))
        for name in ("spawn_supported", "wait_supported", "merge_supported")
    )
    session_chain_ready = all(
        bool(host_capabilities.get(name, False))
        for name in (
            "create_session_supported",
            "kill_session_supported",
            "restart_session_supported",
        )
    )
    host_candidates = ["soft_orchestration_only"]
    if session_chain_ready:
        host_candidates.append("single_backend_multi_session")
    if real_chain_ready:
        host_candidates.append("real_subagent_runtime")

    tier_rank = {
        "soft_orchestration_only": 0,
        "single_backend_multi_session": 1,
        "real_subagent_runtime": 2,
    }
    enforceable = set(allowed_candidates) & set(host_candidates)
    selected = max(enforceable, key=lambda tier: tier_rank[tier])
    candidate_ceiling = max(allowed_candidates, key=lambda tier: tier_rank[tier])
    downgraded_from = ""
    downgrade_reason = ""
    if tier_rank[selected] < tier_rank[candidate_ceiling]:
        downgraded_from = candidate_ceiling
        if selected == "single_backend_multi_session":
            downgrade_reason = "host 未证明 spawn/wait/merge 完整链路，降级到 single_backend_multi_session"
        else:
            downgrade_reason = (
                "host 未证明候选 tier 所需的完整能力链，降级到 soft_orchestration_only"
            )

    evidence: dict[str, object] = {
        "evidence_source": host_capabilities["evidence_source"],
        "spawn_supported": bool(host_capabilities.get("spawn_supported", False)),
        "wait_supported": bool(host_capabilities.get("wait_supported", False)),
        "merge_supported": bool(host_capabilities.get("merge_supported", False)),
        "create_session_supported": bool(host_capabilities.get("create_session_supported", False)),
        "kill_session_supported": bool(host_capabilities.get("kill_session_supported", False)),
        "restart_session_supported": bool(host_capabilities.get("restart_session_supported", False)),
        "real_chain_ready": real_chain_ready,
        "session_chain_ready": session_chain_ready,
        "candidate_ceiling": candidate_ceiling,
    }

    if run_smoke_test:
        smoke_result = runtime_smoke_test(selected, host_capabilities)
        evidence["smoke_test"] = smoke_result
        if not smoke_result["passed"]:
            downgraded_from = selected
            downgrade_reason = f"smoke test 失败: {smoke_result['reason']}"
            selected = "soft_orchestration_only"

    return TierSelectionResult(
        runtime_claim=selected,
        evidence=evidence,
        downgraded_from=downgraded_from,
        downgrade_reason=downgrade_reason,
    )


def build_real_subagent_runtime_plan(
    *,
    text: str,
    workflow_bundle: dict[str, object],
    lead_agent: str,
    assistants: list[str],
    team_engine_gate: dict[str, object],
    auto_run_profile: dict[str, object],
    host_capabilities: HostCapabilities | None = None,
    run_smoke_test: bool = True,
) -> dict[str, object]:
    bundle_name = str(workflow_bundle.get("name", "direct-execution"))
    explicit_request = text_has_any_keyword(text, REAL_SUBAGENT_TRIGGER_KEYWORDS)
    auto_supported = bool(auto_run_profile.get("enabled")) and bool(auto_run_profile.get("workflow_supported"))
    high_risk_team_route = bool(team_engine_gate.get("required")) and bundle_name in {
        "plan-first-build",
        "audit-fix-deliver",
        "govern-change-safely",
        "root-cause-remediate",
        "ship-hold-remediate",
    }
    eligible = explicit_request or auto_supported
    activation_reason = "not requested"
    if explicit_request:
        activation_reason = "user explicitly requested multi-agent or subagent execution"
    elif auto_supported:
        activation_reason = "explicit /auto request is on an auto-run eligible workflow"
    elif high_risk_team_route:
        activation_reason = "high-risk route should propose subagents only after lead explains why local execution is insufficient"

    worker_role = str(team_engine_gate.get("worker_role", "implementation-worker"))
    verifier_role = str(team_engine_gate.get("verifier_role", "delivery-verifier"))
    agents = [
        {
            "role": "worker",
            "task": "produce the scoped implementation or artifact from the WorkOrder",
            "write_scope": "assigned files only; must be disjoint when multiple Workers are spawned",
            "context_policy": "task_only",
            "output_contract": "ImplementationOutput",
            "can_write_artifact": True,
            "can_write_verdict": False,
            "mapped_role": worker_role,
        },
        {
            "role": "verifier",
            "task": "check Worker output against acceptance gates and return pass/fail/hold evidence",
            "write_scope": "verification report and remediation patch only",
            "context_policy": "artifact_only",
            "output_contract": "VerificationReport + RemediationPatch",
            "can_write_artifact": False,
            "can_write_verdict": True,
            "mapped_role": verifier_role,
        },
    ]
    if assistants:
        agents.append(
            {
                "role": "explorer",
                "task": "answer bounded sidecar questions for the Lead without editing files",
                "write_scope": "none",
                "context_policy": "summary_plus_artifact",
                "output_contract": "AssistantDelta",
                "can_write_artifact": False,
                "can_write_verdict": False,
                "mapped_role": assistants[0],
            }
        )

    candidate_runtime_claim = "real_subagent_runtime" if eligible else "soft_orchestration_only"
    candidate_multi_session_claim = "single_backend_multi_session" if eligible else "soft_orchestration_only"

    tier_selection = select_runtime_tier(
        candidate_runtime_claim=candidate_runtime_claim,
        candidate_multi_session_claim=candidate_multi_session_claim,
        host_capabilities=host_capabilities,
        run_smoke_test=run_smoke_test,
    )

    max_subagents_const = 3
    failure_threshold_const = 3

    return {
        "eligible": eligible,
        "reference": REAL_SUBAGENT_RUNTIME_REFERENCE,
        "runtime_claim": tier_selection["runtime_claim"],
        "candidate_runtime_claim": candidate_runtime_claim,
        "candidate_multi_session_claim": candidate_multi_session_claim,
        "runtime_evidence_required": bool(eligible),
        "runtime_evidence": tier_selection["evidence"],
        "runtime_downgraded_from": tier_selection["downgraded_from"],
        "runtime_downgrade_reason": tier_selection["downgrade_reason"],
        "activation_reason": activation_reason,
        "workflow_bundle": bundle_name,
        "max_subagents": max_subagents_const if eligible else 0,
        "tier_selection_algorithm": (
            "if host exposes spawn/wait/merge: real_subagent_runtime; "
            "elif host exposes create_session/kill_session/restart_session: single_backend_multi_session; "
            "else: soft_orchestration_only"
        ),
        "tier_selection_function": "select_runtime_tier()",
        "session_circuit_breaker": {
            "applicable_tier": "single_backend_multi_session",
            "failure_threshold": failure_threshold_const,
            "kill": "session exceeding failure threshold is killed; partial output discarded",
            "restart": "fresh session created with clean context and narrowed WorkOrder",
            "isolate_context": "killed session context must not leak into replacement; only verified artifacts carry over",
            "escalation": "2 kills for same failure reason → escalate to human",
            "owner": "Lead owns session lifecycle decisions; Workers/Verifiers cannot kill their own sessions",
        },
        "spawn_policy": {
            "user_explicit_or_auto_required": True,
            "no_default_swarm": True,
            "blocking_work_stays_local": True,
            "parallel_tasks_must_be_independent": True,
            "code_workers_need_disjoint_write_scopes": True,
        },
        "agents": agents if eligible else [],
        "merge_policy": {
            "lead_merges_only": True,
            "verifier_before_acceptance": bool(team_engine_gate.get("required")),
            "delivery_cycle_report_required": bool(team_engine_gate.get("required")),
            "conflict_resolution": "hold unless objective evidence resolves Worker/Verifier disagreement",
        },
        "fallback": {
            "unavailable_runtime": "downgrade to single_backend_multi_session if host supports sessions, else external-agent-backend soft orchestration",
            "multi_session_unavailable": "downgrade to external-agent-backend soft orchestration (known-shortcut: no session isolation)",
            "malformed_output": "request one structured repair, then hold",
            "role_boundary_violation": "close or ignore violating subagent output and regenerate WorkOrder",
            "session_killed": "discard partial output, restart with fresh context and narrowed WorkOrder",
        },
    }


def build_assistant_delta_contract(
    lead_agent: str, assistants: list[str], workflow_bundle: str | None
) -> dict[str, object]:
    per_agent_fields = {
        "Code Audit Council": ["claim", "evidence", "severity", "fix"],
        "Git Workflow Guardian": ["claim", "evidence", "stage", "next_action"],
        "Technical Trinity": ["claim", "evidence", "decision", "next_action"],
        "World-Class Product Architect": [
            "claim",
            "evidence",
            "decision",
            "acceptance_criteria",
            "ux_impact",
        ],
        "Sentinel Architect (NB)": ["claim", "evidence", "decision", "risk", "next_action"],
        "Java Virtuoso": ["claim", "evidence", "decision", "jvm_implication"],
    }
    by_agent = {
        agent: per_agent_fields.get(agent, ["claim", "evidence", "decision", "next_action"])
        for agent in assistants
    }
    return {
        "enabled": len(assistants) > 0,
        "lead_owner": lead_agent,
        "assistants": assistants,
        "workflow_bundle": workflow_bundle,
        "required_fields": ["claim", "evidence", "decision"],
        "optional_fields": ["risk", "next_action"],
        "by_agent": by_agent,
        "strict_mode": True,
        "rule": "Assistants should return only the delta that materially changes the lead decision.",
    }


def build_beta_validation_plan(text: str, workflow_bundle_name: str) -> dict[str, object]:
    if workflow_bundle_name != "beta-feedback-ramp":
        return {}

    wants_wider_rollout = text_has_any_keyword(
        text,
        [
            "scale up",
            "wider beta",
            "public beta",
            "launch",
            "rollout",
            "逐步放量",
            "扩大内测",
            "发布前",
            "上线前",
        ],
    )
    rounds = [
        {
            "round_id": "round-0",
            "phase": "pre-build concept smoke",
            "sample_size": 5,
            "participant_mode": "simulated target users",
            "archetypes": [
                "first-time novice",
                "goal-driven power user",
                "skeptical evaluator",
            ],
            "goal": "Validate the product promise, user motivation, and major workflow confusion before implementation hardens.",
            "exit_criteria": "The core value proposition is understandable, the top workflow is coherent, and no blocker-level confusion remains.",
        },
        {
            "round_id": "round-1",
            "phase": "closed beta",
            "sample_size": 12,
            "participant_mode": "seed users",
            "archetypes": [
                "first-time novice",
                "daily operator",
                "power user",
                "edge-case breaker",
            ],
            "goal": "Validate the implemented slice, log usability failures, and confirm that acceptance criteria hold under real tasks.",
            "exit_criteria": "No P0-P1 workflow blockers remain, the key task succeeds consistently, and top feedback themes are stable enough to cluster.",
        },
        {
            "round_id": "round-2",
            "phase": "expanded internal beta",
            "sample_size": 30,
            "participant_mode": "mixed internal and trusted external users",
            "archetypes": [
                "new user",
                "returning user",
                "power user",
                "skeptical evaluator",
                "edge-case breaker",
            ],
            "goal": "Pressure-test stability, messaging, and operational readiness before broader rollout.",
            "exit_criteria": "Feedback severity is trending down, repeated blocker classes are closed, and rollout readiness can be judged with explicit evidence.",
        },
    ]
    if wants_wider_rollout:
        rounds.append(
            {
                "round_id": "round-3",
                "phase": "risk-gated wider beta",
                "sample_size": 80,
                "participant_mode": "broader invited users",
                "archetypes": [
                    "new user",
                    "habitual user",
                    "power user",
                    "skeptical evaluator",
                    "long-tail edge-case user",
                ],
                "goal": "Confirm that the product still holds when the cohort broadens and variance increases.",
                "exit_criteria": "No new severe cohort-specific failures appear and the rollout decision can move from internal beta to release governance.",
            }
        )
    return {
        "enabled": True,
        "simulation_allowed": True,
        "feedback_anchor": ".vidt/beta/feedback-ledger.md",
        "cohort_artifact": ".vidt/beta/cohort-matrix.md",
        "cohort_plan_template": "assets/beta-cohort-plan-template.json",
        "cohort_plan_schema": "references/beta-cohort-plan.schema.json",
        "cohort_plan_path": ".vidt/beta/cohort-plan.json",
        "ramp_plan_template": "assets/beta-ramp-plan-template.json",
        "ramp_plan_schema": "references/beta-ramp-plan.schema.json",
        "ramp_plan_path": ".vidt/beta/ramp-plan.json",
        "simulation_profile_template": "assets/simulated-user-profile-template.json",
        "simulation_profile_dir": ".vidt/beta/personas",
        "simulation_persona_library": "references/simulation-persona-library.json",
        "simulation_cohort_fixtures": "references/simulation-cohort-fixtures.json",
        "simulation_config_template": "assets/beta-simulation-config-template.json",
        "simulation_config_dir": ".vidt/beta/simulation-configs",
        "simulation_scenario_packs": "references/simulation-scenario-packs.json",
        "simulation_trace_catalog": "references/simulation-trace-catalog.json",
        "simulation_preview_dir": ".vidt/beta/fixture-previews",
        "simulation_diff_dir": ".vidt/beta/fixture-diffs",
        "simulation_run_dir": ".vidt/beta/simulation-runs",
        "simulation_init_command_template": (
            "python scripts/init_beta_simulation.py --root . --round-id <round-id> "
            "--phase \"<phase>\" --objective \"<objective>\" --pretty"
        ),
        "simulation_preview_command_template": (
            "python scripts/preview_beta_simulation_fixture.py "
            "--config .vidt/beta/simulation-configs/<round-id>.json --pretty"
        ),
        "simulation_diff_command_template": (
            "python scripts/compare_beta_simulation_manifests.py "
            "--previous .vidt/beta/fixture-previews/<previous-round-id>/beta-simulation-manifest.json "
            "--current .vidt/beta/fixture-previews/<round-id>/beta-simulation-manifest.json --pretty"
        ),
        "simulation_run_command_template": (
            "python scripts/run_beta_simulation.py --config .vidt/beta/simulation-configs/<round-id>.json --pretty"
        ),
        "simulation_summary_command_template": (
            "python scripts/summarize_beta_simulation.py --run .vidt/beta/simulation-runs/<round-id>/beta-simulation-run.json "
            "--feedback-ledger-out .vidt/beta/feedback-ledger.md --round-report-out .vidt/beta/reports/<round-id>.json --pretty"
        ),
        "report_template": "assets/beta-round-report-template.json",
        "report_dir": ".vidt/beta/reports",
        "decision_dir": ".vidt/beta/round-decisions",
        "gate_command_template": "python scripts/evaluate_beta_round.py --report .vidt/beta/reports/<round-id>.json --pretty",
        "rounds": rounds,
    }


def build_auto_run_profile(
    *,
    auto_mode: dict[str, object],
    workflow_bundle_name: str,
    progress_anchor: object,
    iteration_profile: dict[str, object],
    repo_root: Path,
) -> dict[str, object]:
    enabled = bool(auto_mode.get("enabled"))
    requested_phase = str(auto_mode.get("requested_phase", "manual")).strip() or "manual"
    normalized_text = str(auto_mode.get("normalized_text", "")).strip()
    original_text = str(auto_mode.get("original_text", "")).strip()
    run_style = str(auto_mode.get("run_style", "foreground")).strip() or "foreground"
    if run_style not in {"foreground", "background"}:
        run_style = "foreground"
    safety_level = str(auto_mode.get("safety_level", "standard")).strip() or "standard"
    if safety_level not in {"standard", "safe"}:
        safety_level = "standard"
    resume_requested = bool(auto_mode.get("resume_requested"))
    workflow_supported = workflow_bundle_name in AUTO_ELIGIBLE_WORKFLOWS
    execution_mode = "manual"
    if enabled and requested_phase == "go":
        execution_mode = "auto-go"
    elif enabled:
        execution_mode = "auto-setup"

    if workflow_supported:
        setup_command = (
            f'python scripts/run_auto_workflow.py --text "{original_text or "<original-request-with-/auto-modifiers>"}" '
            "--mode setup --pretty"
        )
        go_command = (
            "python scripts/run_auto_workflow.py --mode go "
            "--plan .vidt/auto/auto-run-plan.json --pretty"
        )
        recommended_resume_anchor = ".vidt/auto/auto-run-plan.md"
        eligibility_reason = (
            "This workflow supports explicit auto setup/go orchestration with bounded safety guards."
        )
    elif enabled:
        setup_command = ""
        go_command = ""
        recommended_resume_anchor = str(progress_anchor or "")
        eligibility_reason = (
            "Auto mode is explicit, but this workflow is not on the current auto-run whitelist."
        )
    else:
        setup_command = ""
        go_command = ""
        recommended_resume_anchor = str(progress_anchor or "")
        eligibility_reason = "Auto mode is not requested."

    state_resume_context = {
        "resume_strategy": "plan-reuse",
        "state_resume_available": False,
        "state_resume_selection_mode": "",
        "state_resume_state_path": "",
        "state_resume_decision_id": "",
        "state_resume_decision_label": "",
        "state_resume_decision_reason": "",
        "state_resume_command": "",
        "state_resume_anchor": "",
        "state_resume_playbooks": [],
        "state_resume_blocking_conditions": [],
        "state_resume_command_allowed": False,
        "state_resume_dry_run_command": "",
        "state_resume_execute_command": "",
        "state_resume_error": "",
    }
    if resume_requested and workflow_supported:
        dry_run_command = (
            f"python scripts/resume_from_automation_state.py --repo . --workflow {workflow_bundle_name} --pretty"
        )
        execute_command = (
            f"python scripts/resume_from_automation_state.py --repo . --workflow {workflow_bundle_name} --execute --pretty"
        )
        state_resume_context["state_resume_dry_run_command"] = dry_run_command
        state_resume_context["state_resume_execute_command"] = execute_command
        try:
            resume_probe = automation_state_resumer.build_resume_payload(
                repo_root=repo_root,
                workflow=workflow_bundle_name,
                execute=False,
            )
        except Exception as exc:
            state_resume_context["state_resume_error"] = str(exc)
        else:
            decision_card = resume_probe.get("decision_card", {})
            if not isinstance(decision_card, dict):
                decision_card = {}
            state_resume_context.update(
                {
                    "resume_strategy": "state-first" if bool(resume_probe.get("ok")) else "plan-reuse",
                    "state_resume_available": bool(resume_probe.get("ok")),
                    "state_resume_selection_mode": str(resume_probe.get("selection_mode", "")),
                    "state_resume_state_path": str(resume_probe.get("selected_state_path", "")),
                    "state_resume_decision_id": str(decision_card.get("decision_id", "")),
                    "state_resume_decision_label": str(decision_card.get("decision_label", "")),
                    "state_resume_decision_reason": str(decision_card.get("decision_reason", "")),
                    "state_resume_command": str(resume_probe.get("recommended_command", "")),
                    "state_resume_anchor": str(decision_card.get("resume_anchor", "")),
                    "state_resume_playbooks": [
                        str(item) for item in decision_card.get("playbooks", []) if str(item).strip()
                    ],
                    "state_resume_blocking_conditions": [
                        str(item)
                        for item in decision_card.get("blocking_conditions", [])
                        if str(item).strip()
                    ],
                    "state_resume_command_allowed": bool(resume_probe.get("command_allowed")),
                    "state_resume_error": str(resume_probe.get("error", "")),
                }
            )
            if bool(resume_probe.get("ok")):
                eligibility_reason = (
                    "Resume mode found a latest automation-state decision, so the workflow can recover from state before reusing the saved plan."
                )

    online_round_cap = int(iteration_profile.get("round_cap_online", 3)) if isinstance(
        iteration_profile, dict
    ) else 3
    if safety_level == "safe":
        online_round_cap = min(max(online_round_cap, 1), 1)
    release_hold_loop_max_rounds = 1 if safety_level == "safe" else 3
    safety_guards = [
        "default mode stays manual unless /auto is explicit",
        "auto mode is limited to root-cause-remediate, ship-hold-remediate, and post-release-close-loop",
        "setup and go are separate phases; go must be explicit",
        "do not run destructive git actions automatically",
        "persist a resume plan before the go phase starts",
    ]
    if safety_level == "safe":
        safety_guards.append("safe mode clamps automation to a single bounded pass before any further escalation")
    if run_style == "background":
        safety_guards.append("background mode only changes the resumable contract; it does not imply unmanaged daemon execution")
    if resume_requested:
        safety_guards.append("resume mode reuses the latest saved plan or state when the workflow supports it")
        if bool(state_resume_context.get("state_resume_available")):
            safety_guards.append("resume mode prefers the latest automation-state decision before falling back to plain plan reuse")
    return {
        "enabled": enabled,
        "trigger": str(auto_mode.get("trigger", "none")),
        "requested_phase": requested_phase,
        "execution_mode": execution_mode,
        "run_style": run_style,
        "safety_level": safety_level,
        "resume_requested": resume_requested,
        "detached_ready": run_style == "background",
        "workflow_bundle": workflow_bundle_name,
        "workflow_supported": workflow_supported,
        "eligible_workflows": sorted(AUTO_ELIGIBLE_WORKFLOWS),
        "modifier_tokens": auto_mode.get("modifier_tokens", []),
        "text_without_trigger": normalized_text,
        "requires_explicit_go": enabled and workflow_supported,
        "eligibility_reason": eligibility_reason,
        "state_root": ".vidt/auto",
        "state_dir": ".vidt/auto/state",
        "plan_json": ".vidt/auto/auto-run-plan.json",
        "plan_markdown": ".vidt/auto/auto-run-plan.md",
        "resume_anchor": recommended_resume_anchor,
        "automation_state_schema": "references/automation-state.schema.json",
        "setup_command": setup_command,
        "go_command": go_command,
        "stop_caps": {
            "iteration_online_round_cap": max(online_round_cap, 1),
            "release_hold_loop_max_rounds": release_hold_loop_max_rounds,
        },
        "safety_guards": safety_guards,
        **state_resume_context,
    }


HOOK_SPEC_MAP: dict[str, dict[str, list[str]]] = {
    "Java Virtuoso": {
        "spec_files": ["references/routing-rules.json", "references/execution-quality-guardrails.md"],
        "spec_sections": ["routing-rules.json#java-profile", "language-profiles.yaml#java"],
    },
    "API Contract Sentinel": {
        "spec_files": ["references/routing-rules.json", "references/execution-quality-guardrails.md"],
        "spec_sections": ["routing-rules.json#api-contract"],
    },
    "Sentinel Architect (NB)": {
        "spec_files": ["references/routing-rules.json", "references/anti-entropy-governance.md"],
        "spec_sections": ["routing-rules.json#architecture"],
    },
    "Code Audit Council": {
        "spec_files": ["references/routing-rules.json", "references/execution-quality-guardrails.md"],
        "spec_sections": ["routing-rules.json#audit"],
    },
    "Git Workflow Guardian": {
        "spec_files": ["references/routing-rules.json", "references/git-workflow-playbook.md"],
        "spec_sections": ["routing-rules.json#git-workflow"],
    },
    "World-Class Product Architect": {
        "spec_files": ["references/routing-rules.json", "references/goal-framing-protocol.md", "references/execution-quality-guardrails.md"],
        "spec_sections": ["routing-rules.json#product", "routing-rules.json#frontend-profile"],
    },
    "Technical Trinity": {
        "spec_files": ["references/routing-rules.json", "references/execution-quality-guardrails.md"],
        "spec_sections": ["routing-rules.json#fullstack"],
    },
    "Data Pipeline Guardian": {
        "spec_files": ["references/routing-rules.json", "references/execution-quality-guardrails.md"],
        "spec_sections": ["routing-rules.json#data"],
    },
}


def validate_hook_spec_references(
    skill_dir: Path | None = None,
    hook_spec_map: dict[str, dict[str, list[str]]] | None = None,
) -> dict[str, object]:
    """Validate that hook files exist and language-profile sections resolve."""
    resolved_skill_dir = (skill_dir or SCRIPT_DIR.parent).resolve()
    spec_map = HOOK_SPEC_MAP if hook_spec_map is None else hook_spec_map
    language_profile_path = resolved_skill_dir / "references" / "language-profiles.yaml"
    profile_names: set[str] = set()
    if language_profile_path.exists():
        profile_names = {
            match.group(1)
            for match in re.finditer(
                r"^  ([A-Za-z0-9_-]+):\s*$",
                language_profile_path.read_text(encoding="utf-8"),
                re.MULTILINE,
            )
        }

    errors: list[str] = []
    for lead_agent, mapping in spec_map.items():
        for spec_file in mapping.get("spec_files", []):
            if not (resolved_skill_dir / spec_file).is_file():
                errors.append(f"{lead_agent}: missing spec file {spec_file}")
        for spec_section in mapping.get("spec_sections", []):
            if "#" not in spec_section:
                errors.append(f"{lead_agent}: malformed spec section {spec_section}")
                continue
            filename, section = spec_section.split("#", 1)
            section_path = resolved_skill_dir / "references" / filename
            if not section_path.is_file():
                errors.append(f"{lead_agent}: missing section file references/{filename}")
                continue
            if filename == "language-profiles.yaml" and section not in profile_names:
                errors.append(f"{lead_agent}: unknown language profile {section}")

    return {
        "ok": not errors,
        "checked_agents": len(spec_map),
        "language_profiles": sorted(profile_names),
        "errors": errors,
    }


def build_hook_directives(lead_agent: str) -> dict[str, object]:
    """根据 lead_agent 构建 hook 注入指令(P1-19)

    将相关 spec 条目通过 hook 挂载进 Worker 的上下文,
    Worker 不需要手动找规范。
    """
    validation = validate_hook_spec_references()
    if not validation["ok"]:
        raise RuntimeError(f"Invalid hook spec references: {validation['errors']}")
    mapping = HOOK_SPEC_MAP.get(lead_agent, {})
    return {
        "spec_files": mapping.get("spec_files", []),
        "spec_sections": mapping.get("spec_sections", []),
        "inject_target": "worker",
    }


def route_request(text: str, config: dict[str, object], repo_path: Path) -> dict[str, object]:
    repository_roots = resolve_repository_roots(repo_path)
    state_root = Path(str(repository_roots["state_root"]))
    auto_mode = detect_auto_mode(text)
    routed_text = str(auto_mode.get("normalized_text", text)).strip() or text
    scores, reasons = compute_scores(routed_text, config)
    (
        needs_pre_development_planning,
        needs_iteration,
        needs_project_knowledge_capture,
        needs_worktree,
        needs_release_gate,
        needs_git_workflow,
        process_skills,
        process_hits,
    ) = detect_process_skills(routed_text, config)
    git_reason_hits = reasons.get("Git Workflow Guardian", {}).get("positive", [])
    if isinstance(git_reason_hits, list) and should_suppress_git_agent_scoring(
        git_reason_hits=git_reason_hits,
        needs_release_gate=needs_release_gate,
        needs_git_workflow=needs_git_workflow,
    ):
        scores["Git Workflow Guardian"] = 0
        reasons["Git Workflow Guardian"] = {
            "positive": [],
            "negative": reasons.get("Git Workflow Guardian", {}).get("negative", []),
        }
    detected_languages, language_hits, language_routing = detect_languages(routed_text, config)
    repo_strategy = detect_repo_strategy(repo_path)
    git_templates = build_git_templates(repo_strategy)
    iteration_profile = build_iteration_profile(config=config, enabled=needs_iteration)

    agent_order = config.get("agent_order", [])
    if not isinstance(agent_order, list) or len(agent_order) == 0:
        raise ValueError("routing config key 'agent_order' must be a non-empty list")
    order_index = {str(name): index for index, name in enumerate(agent_order)}

    sorted_agents = sorted(
        scores.items(),
        key=lambda item: (-item[1], order_index.get(item[0], 999)),
    )
    lead_agent, lead_score = sorted_agents[0]
    priority_route = detect_priority_lead(routed_text, config)
    if priority_route is not None:
        priority_agent = str(priority_route.get("agent", "")).strip()
        if (
            priority_agent == "Git Workflow Guardian"
            and needs_release_gate
            and not needs_git_workflow
        ):
            priority_route = None
        elif priority_agent != "":
            lead_agent = priority_agent
            lead_score = scores.get(lead_agent, 0)
    if is_audit_batch_fix_context(routed_text):
        lead_agent = "Code Audit Council"
        scores[lead_agent] = max(scores.get(lead_agent, 0), 6)
        lead_score = scores[lead_agent]
        priority_route = {
            "agent": lead_agent,
            "matched_keywords": ["audit-batch-fix"],
        }
    elif (
        is_frontend_backend_contract_context(routed_text)
        and (priority_route or {}).get("agent") != "Code Audit Council"
    ):
        lead_agent = "World-Class Product Architect"
        scores[lead_agent] = max(scores.get(lead_agent, 0), 6)
        lead_score = scores[lead_agent]
    lead_agent = rebalance_git_lead_for_semantic_owner(
        lead_agent=lead_agent,
        priority_route=priority_route,
        scores=scores,
        needs_git_workflow=needs_git_workflow,
    )
    lead_score = scores.get(lead_agent, 0)

    process_only = lead_score == 0 and len(process_skills) > 0
    language_only = lead_score == 0 and len(process_skills) == 0 and len(detected_languages) > 0
    unknown_only = lead_score == 0 and len(process_skills) == 0 and len(detected_languages) == 0
    scope_boundary = build_scope_boundary(routed_text, unknown_only=unknown_only)
    if process_only:
        lead_agent = pick_process_lead_agent(process_skills=process_skills, config=config)
        lead_score = scores.get(lead_agent, 0)
    elif language_only:
        lead_agent = language_routing.get(detected_languages[0], "Technical Trinity")
        lead_score = scores.get(lead_agent, 0)
    elif unknown_only:
        default_lead = str(config.get("default_unknown_lead_agent", "Technical Trinity"))
        lead_agent = default_lead
        lead_score = scores.get(lead_agent, 0)
    elif (
        lead_agent == "Git Workflow Guardian"
        and not needs_git_workflow
        and priority_route is None
        and is_quick_slice_context(routed_text)
    ):
        lead_agent = "Technical Trinity"
        lead_score = max(scores.get(lead_agent, 0), 1)

    top_three_total = sum(score for _, score in sorted_agents[:3])
    confidence = round(lead_score / max(top_three_total, 1), 3) if top_three_total > 0 else 0.0

    high_confidence = get_threshold(config, "high_confidence", 0.55)
    medium_confidence = get_threshold(config, "medium_confidence", 0.35)
    sentinel_threshold = int(get_threshold(config, "sentinel_overlay_threshold", 6))
    sentinel_score = scores.get("Sentinel Architect (NB)", 0)
    sentinel_overlay = sentinel_score >= sentinel_threshold and sentinel_score > 0

    assistant_candidates = [agent for agent, _ in sorted_agents if agent != lead_agent]
    if process_only or language_only or unknown_only or confidence >= high_confidence:
        assistants = []
    elif confidence >= medium_confidence:
        assistants = assistant_candidates[:1]
    else:
        assistants = assistant_candidates[:2]

    # Avoid duplicate value-add when assistant score is zero.
    assistants = [
        agent for agent in assistants if scores.get(agent, 0) > 0 and agent != lead_agent
    ]
    assistants = apply_assistant_routing_rules(
        text=text,
        lead_agent=lead_agent,
        assistants=assistants,
        scores=scores,
        config=config,
    )
    assistants = apply_language_copilot_rules(
        lead_agent=lead_agent,
        assistants=assistants,
        detected_languages=detected_languages,
        language_routing=language_routing,
        needs_worktree=needs_worktree,
        needs_git_workflow=needs_git_workflow,
    )
    if (
        lead_agent == "Code Audit Council"
        and needs_git_workflow
        and is_audit_batch_fix_context(routed_text)
    ):
        assistants = dedupe_agents(assistants + ["Git Workflow Guardian"])
    git_reason_hits = reasons.get("Git Workflow Guardian", {}).get("positive", [])
    if (
        lead_agent != "Git Workflow Guardian"
        and isinstance(git_reason_hits, list)
        and is_git_review_context_only(routed_text, git_reason_hits)
    ):
        assistants = [agent for agent in assistants if agent != "Git Workflow Guardian"]
    if sentinel_overlay and lead_agent != "Sentinel Architect (NB)":
        assistants = dedupe_agents(["Sentinel Architect (NB)"] + assistants)
    governance_defaults = get_governance_defaults(config)
    governance_plan = build_governance_plan(
        text=routed_text,
        repo_path=state_root,
        lead_agent=lead_agent,
        assistants=assistants,
        scores=scores,
        confidence=confidence,
        sentinel_overlay=sentinel_overlay,
        needs_git_workflow=needs_git_workflow,
        governance_defaults=governance_defaults,
    )
    fast_track_control = governance_defaults.get("fast_track_control", {})
    if not isinstance(fast_track_control, dict):
        fast_track_control = {}
    decision_log_write: dict[str, object] = {
        "attempted": False,
        "written": False,
        "path": str(state_root / DECISION_LOG_PATH),
        "error": None,
    }
    if bool(fast_track_control.get("write_event_log", True)):
        decision_log_write["attempted"] = True
        try:
            append_decision_log_entry(
                repo_path=state_root,
                payload={
                    "timestamp": now_iso(),
                    "lead_agent": lead_agent,
                    "risk_level": governance_plan.get("risk_level"),
                    "selected_track": ((governance_plan.get("privy_council") or {}).get("selected_track")),
                    "mode_hint": "route_request",
                },
                decision="route_selected",
                verifier="n_a",
                reason=str(
                    governance_plan.get("selection_reason")
                    or governance_plan.get("reason")
                    or ""
                ),
            )
            decision_log_write["written"] = True
        except (OSError, ValueError) as exc:
            decision_log_write["error"] = f"{type(exc).__name__}: {exc}"
    mode = pick_mode(
        confidence=confidence,
        sentinel_overlay=sentinel_overlay,
        needs_pre_development_planning=needs_pre_development_planning,
        process_only=process_only,
        language_only=language_only,
        unknown_only=unknown_only,
        roundtable_enabled=bool(governance_plan.get("roundtable_enabled", False)),
        fast_track_enabled=(
            (governance_plan.get("privy_council") or {}).get("selected_track") == TRACK_FAST
        ),
        assistant_count=len(assistants),
        high_confidence=high_confidence,
        medium_confidence=medium_confidence,
    )
    need_clarify = unknown_only or (
        confidence < medium_confidence
        and len(assistants) == 0
        and not process_only
        and not language_only
    )
    workflow_bundle = build_workflow_bundle(
        text=routed_text,
        lead_agent=lead_agent,
        needs_pre_development_planning=needs_pre_development_planning,
        needs_iteration=needs_iteration,
        needs_project_knowledge_capture=needs_project_knowledge_capture,
        needs_release_gate=needs_release_gate,
        needs_git_workflow=needs_git_workflow,
        sentinel_overlay=sentinel_overlay,
    )
    intent_confirmation = build_intent_confirmation(
        text=routed_text,
        need_clarify=need_clarify and scope_boundary["status"] != "out_of_scope",
        lead_agent=lead_agent,
        workflow_bundle=workflow_bundle,
    )
    intent_question = intent_confirmation.get("question")
    if bool(intent_confirmation.get("required")) and isinstance(intent_question, str) and intent_question.strip():
        clarifying_question = intent_question
    else:
        clarifying_question = build_clarifying_question(text=text, need_clarify=need_clarify)
    stage_council_plan = build_stage_council_plan(
        text=routed_text,
        lead_agent=lead_agent,
        workflow_bundle=workflow_bundle,
    )
    if bool(intent_confirmation.get("required")):
        stage_council_plan = {
            **stage_council_plan,
            "enabled": False,
            "active_councils": [],
            "councils": [],
            "fallback": (
                "Intent confirmation is required before activating product-discovery "
                "or prototype-design stage councils."
            ),
        }
    micro_practices = build_micro_practices(
        text=routed_text,
        workflow_bundle=workflow_bundle,
        lead_agent=lead_agent,
        needs_pre_development_planning=needs_pre_development_planning,
        needs_iteration=needs_iteration,
    )
    micro_practice_names = [
        str(item.get("name", ""))
        for item in micro_practices
        if str(item.get("name", "")).strip()
    ]
    workflow_bundle_bootstrap = build_workflow_bundle_bootstrap(
        str(workflow_bundle.get("name", "direct-execution")),
        micro_practice_names=micro_practice_names,
    )
    resume_artifacts = [
        str(item)
        for item in workflow_bundle.get("resume_artifacts", [])
        if str(item).strip()
    ]
    for item in workflow_bundle_bootstrap.get("artifacts", []):
        artifact = str(item).strip()
        if artifact and artifact.startswith(".vidt/practices/") and artifact not in resume_artifacts:
            resume_artifacts.append(artifact)
    quality_gate = build_quality_gate(
        lead_agent=lead_agent,
        assistants=assistants,
        workflow_bundle=workflow_bundle,
        clarifying_question=clarifying_question,
    )
    harness_constraint_gate = build_harness_constraint_gate(
        workflow_bundle=workflow_bundle,
        lead_agent=lead_agent,
        assistants=assistants,
        request_text=routed_text,
    )
    team_engine_gate = build_team_engine_gate(
        workflow_bundle=workflow_bundle,
        lead_agent=lead_agent,
        assistants=assistants,
        needs_release_gate=needs_release_gate,
        needs_git_workflow=needs_git_workflow,
        needs_iteration=needs_iteration,
    )
    external_agent_backend_plan = build_external_agent_backend_plan(
        workflow_bundle=workflow_bundle,
        lead_agent=lead_agent,
        team_engine_gate=team_engine_gate,
    )
    assistant_delta_contract = build_assistant_delta_contract(
        lead_agent=lead_agent,
        assistants=assistants,
        workflow_bundle=str(workflow_bundle.get("name")),
    )
    beta_validation_plan = build_beta_validation_plan(
        text=routed_text,
        workflow_bundle_name=str(workflow_bundle.get("name")),
    )
    auto_run_profile = build_auto_run_profile(
        auto_mode=auto_mode,
        workflow_bundle_name=str(workflow_bundle.get("name", "direct-execution")),
        progress_anchor=workflow_bundle.get("progress_anchor_recommended"),
        iteration_profile=iteration_profile,
        repo_root=state_root,
    )
    real_subagent_runtime_plan = build_real_subagent_runtime_plan(
        text=routed_text,
        workflow_bundle=workflow_bundle,
        lead_agent=lead_agent,
        assistants=assistants,
        team_engine_gate=team_engine_gate,
        auto_run_profile=auto_run_profile,
    )
    process_plan = build_process_plan(
        needs_pre_development_planning=needs_pre_development_planning,
        needs_iteration=needs_iteration,
        needs_project_knowledge_capture=needs_project_knowledge_capture,
        needs_worktree=needs_worktree,
        needs_release_gate=needs_release_gate,
        needs_git_workflow=needs_git_workflow,
        repo_strategy=repo_strategy,
        iteration_profile=iteration_profile,
        lead_agent=lead_agent,
        workflow_bundle_name=str(workflow_bundle.get("name", "direct-execution")),
        auto_run_profile=auto_run_profile,
        state_root=state_root,
    )

    reason = {
        "lead_positive_hits": reasons.get(lead_agent, {}).get("positive", []),
        "lead_negative_hits": reasons.get(lead_agent, {}).get("negative", []),
        "assistant_hits": {agent: reasons.get(agent, {}) for agent in assistants},
        "sentinel_overlay": sentinel_overlay,
        "process_only_fallback": process_only,
        "language_only_fallback": language_only,
        "unknown_only_fallback": unknown_only,
        "priority_routing": priority_route,
        "language_hits": language_hits,
        "process_skill_hits": process_hits,
        "workflow_bundle_reason": workflow_bundle.get("reason"),
        "quality_gate_reference": quality_gate.get("reference"),
        "harness_constraint_reference": harness_constraint_gate.get("reference"),
        "team_engine_reference": team_engine_gate.get("reference"),
        "worker_verifier_reference": team_engine_gate.get("cycle_reference"),
        "external_agent_backend_reference": external_agent_backend_plan.get("reference"),
        "real_subagent_runtime_reference": real_subagent_runtime_plan.get("reference"),
        "real_subagent_runtime_eligible": real_subagent_runtime_plan.get("eligible"),
        "intent_confirmation_required": intent_confirmation.get("required"),
        "intent_confirmation_option_ids": intent_confirmation.get("option_ids", []),
        "stage_council_reference": stage_council_plan.get("reference"),
        "active_councils": stage_council_plan.get("active_councils", []),
        "assistant_delta_contract_enabled": assistant_delta_contract.get("enabled"),
        "micro_practices": micro_practices,
        "micro_practice_names": micro_practice_names,
        "auto_mode": auto_run_profile,
    }

    return {
        "lead_agent": lead_agent,
        "assistant_agents": assistants,
        "detected_languages": detected_languages,
        "needs_pre_development_planning": needs_pre_development_planning,
        "language_routing": language_routing,
        "needs_iteration": needs_iteration,
        "needs_project_knowledge_capture": needs_project_knowledge_capture,
        "needs_worktree": needs_worktree,
        "needs_release_gate": needs_release_gate,
        "needs_git_workflow": needs_git_workflow,
        "process_skills": process_skills,
        "builtin_process_enabled": True,
        "process_plan": process_plan,
        "repository_roots": repository_roots,
        "decision_log_write": decision_log_write,
        "iteration_profile": iteration_profile,
        "governance_plan": governance_plan,
        "git_workflow_profile": {
            "repo_strategy": repo_strategy,
            "auto_execute_policy": build_auto_execute_policy(),
            "templates": git_templates,
            "kpis": [
                "first_push_success_rate",
                "rebase_conflict_rate",
                "rollback_rate",
                "manual_intervention_rate",
            ],
        },
        "confidence": confidence,
        "request_language": "zh" if has_cjk(text) else "en",
        "mode": mode,
        "auto_mode_enabled": auto_run_profile.get("enabled"),
        "auto_mode_source": auto_run_profile.get("trigger"),
        "execution_mode": auto_run_profile.get("execution_mode"),
        "auto_run_profile": auto_run_profile,
        "clarifying_question": clarifying_question,
        "intent_confirmation": intent_confirmation,
        "scope_boundary": scope_boundary,
        "workflow_bundle": workflow_bundle.get("name"),
        "bundle_confidence": workflow_bundle.get("confidence"),
        "workflow_bundle_source": workflow_bundle.get("source"),
        "workflow_runtime_claim": workflow_bundle.get("runtime_claim", ""),
        "multi_expert_plan": workflow_bundle.get("multi_expert_plan", {}),
        "multi_expert_roles": [
            str(expert.get("role", ""))
            for expert in (
                (workflow_bundle.get("multi_expert_plan", {}) or {}).get("experts", [])
                if isinstance(workflow_bundle.get("multi_expert_plan", {}), dict)
                else []
            )
            if str(expert.get("role", "")).strip()
        ],
        "workflow_steps": workflow_bundle.get("steps", []),
        "workflow_reason": workflow_bundle.get("reason"),
        "stage_council_plan": stage_council_plan,
        "active_councils": stage_council_plan.get("active_councils", []),
        "micro_practices": micro_practices,
        "micro_practice_names": micro_practice_names,
        "quality_gate": quality_gate,
        "harness_constraint_gate": harness_constraint_gate,
        "team_engine_gate": team_engine_gate,
        "external_agent_backend_plan": external_agent_backend_plan,
        "real_subagent_runtime": real_subagent_runtime_plan,
        "progress_anchor_recommended": workflow_bundle.get("progress_anchor_recommended"),
        "resume_artifacts": resume_artifacts,
        "workflow_bundle_bootstrap": workflow_bundle_bootstrap,
        "beta_validation_plan": beta_validation_plan,
        "assistant_delta_contract": assistant_delta_contract,
        "hook_directives": build_hook_directives(lead_agent),
        "scores": scores,
        "reason": reason,
        "repo_root_hint": str(state_root),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Route request to virtual-intelligent-dev-team.")
    parser.add_argument("--text", required=True, help="User request text.")
    parser.add_argument(
        "--config",
        default=str(DEFAULT_CONFIG_PATH),
        help="Path to routing config JSON.",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output.",
    )
    parser.add_argument(
        "--repo",
        default=".",
        help="Repository path for strategy detection.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config_path = Path(args.config).resolve()
    repo_path = Path(args.repo).resolve()
    config = load_config(config_path)
    result = route_request(args.text, config, repo_path=repo_path)
    result["routing_config"] = {
        "path": str(config_path),
        "version": str(config.get("meta", {}).get("version", "unknown")),
    }
    if args.pretty:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
