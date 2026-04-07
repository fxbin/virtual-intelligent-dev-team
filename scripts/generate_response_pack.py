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


def _bullet_list(items: list[str]) -> str:
    if not items:
        return "- none"
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


def build_response_pack(result: dict[str, object], template: str = "auto") -> str:
    lead = str(result.get("lead_agent", "unknown"))
    assistants = result.get("assistant_agents", [])
    if not isinstance(assistants, list):
        assistants = []
    workflow_bundle = str(result.get("workflow_bundle", "direct-execution"))
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

    lines = [
        "## Team Dispatch",
        f"- Lead agent: {lead}",
        f"- Assistant agents: {', '.join(assistants) if assistants else 'none'}",
        f"- Workflow bundle: {workflow_bundle}",
        f"- Bundle confidence: {bundle_confidence}",
        f"- Why this route: {workflow_reason or 'See router reasoning.'}",
        "",
    ]

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
                f"- Main risks: governance track `{privy.get('selected_track', 'regular track')}`, process skills `{', '.join(process_skills) if process_skills else 'none'}`.",
            ]
        )

    lines.extend(
        [
            (
                f"- Assistant delta contract: required fields {', '.join(contract.get('required_fields', []))}."
                if contract.get("enabled")
                else "- Assistant delta contract: not required."
            ),
            "",
            "## Next Step",
            f"- Smallest executable action: {workflow_steps[0] if workflow_steps else 'execute the next direct step under the lead.'}",
            f"- Progress anchor: {progress_anchor or 'not required'}",
            "- Resume artifacts:",
            _bullet_list([str(item) for item in resume_artifacts]),
            "",
            "## Git Workflow",
            f"- using-git-worktrees: {'yes' if result.get('needs_worktree') else 'no'}",
            f"- git-workflow: {'yes' if result.get('needs_git_workflow') else 'no'}",
            f"- Suggested branch: {templates.get('branch_name', 'n/a')}",
            f"- Suggested commit: {templates.get('commit_message', 'n/a')}",
            f"- Suggested PR title: {templates.get('pr_title', 'n/a')}",
            "",
            "## Governance",
            f"- Roundtable enabled: {'yes' if governance.get('roundtable_enabled') else 'no'}",
            f"- Selected governance track: {privy.get('selected_track', 'regular track')}",
            f"- Risk level: {governance.get('risk_level', 'unknown')}",
            f"- Dual-sign required: {'yes' if privy.get('dual_sign_required') else 'no'}",
            "",
        ]
    )

    if needs_planning:
        lines.extend(
            [
                "## Planning Pack",
                "- Confirmed path: lightweight pre-development planning before implementation.",
                f"- Recommended anchor: {progress_anchor or 'docs/progress/MASTER.md'}",
                "- Workflow steps:",
                _bullet_list([str(item) for item in workflow_steps]),
                "",
            ]
        )

    if needs_iteration:
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
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = route_request.load_config(Path(args.config).resolve())
    result = route_request.route_request(
        text=args.text,
        config=config,
        repo_path=Path(args.repo).resolve(),
    )
    markdown = build_response_pack(result, template=args.template)
    if args.output:
        output_path = Path(args.output).resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(markdown, encoding="utf-8")
    print(markdown, end="")


if __name__ == "__main__":
    main()
