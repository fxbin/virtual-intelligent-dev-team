#!/usr/bin/env python3
"""Minimal export-parent fixture for version-sync compatibility tests."""

from __future__ import annotations

import json
import re
from pathlib import Path

TARGET_SKILL = "virtual-intelligent-dev-team"
DOC_HTML_FILES = ("index.html", "architecture.html", "engineering.html", "agents.html", "matrix.html")


def replace_first(text: str, pattern: str, repl: str) -> tuple[str, bool]:
    updated, count = re.subn(pattern, repl, text, count=1, flags=re.MULTILINE)
    return updated, count > 0


def update_readme_text(text: str, version: str) -> tuple[str, bool]:
    changed = False
    text, hit = replace_first(text, rf"(\| `{re.escape(TARGET_SKILL)}` \| `)v[^`]+(` \|)", f"\\g<1>{version}\\2")
    changed = changed or hit
    text, hit = replace_first(text, rf"(\| `{re.escape(TARGET_SKILL)}` \| Virtual Intelligent Dev Team \| `)v[^`]+(` \|)", f"\\g<1>{version}\\2")
    return text, changed or hit


def sync_readme(repo_root: Path, version: str) -> bool:
    path = repo_root / "README.md"
    text = path.read_text(encoding="utf-8")
    updated, changed = update_readme_text(text, version)
    if changed:
        path.write_text(updated, encoding="utf-8")
    return changed


def update_skill_readme_text(text: str, version: str) -> tuple[str, bool]:
    return replace_first(text, r"(shields\.io/badge/version-)v[^-]+(-8b5cf6\?style=flat-square)", f"\\g<1>{version}\\2")


def sync_skill_readme(skill_dir: Path, version: str) -> bool:
    path = skill_dir / "README.md"
    text = path.read_text(encoding="utf-8")
    updated, changed = update_skill_readme_text(text, version)
    if changed:
        path.write_text(updated, encoding="utf-8")
    return changed


def update_docs_html_text(text: str, version: str) -> tuple[str, bool]:
    updated, count = re.subn(r"v\d+\.\d+\.\d+", version, text)
    return updated, count > 0 and updated != text


def sync_docs_html(skill_dir: Path, version: str) -> dict[str, bool]:
    changed: dict[str, bool] = {}
    for filename in DOC_HTML_FILES:
        path = skill_dir / "docs" / filename
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        updated, file_changed = update_docs_html_text(text, version)
        if file_changed:
            path.write_text(updated, encoding="utf-8")
        changed[f"{TARGET_SKILL}/docs/{filename}"] = file_changed
    return changed


def sync_skills_index(repo_root: Path, version: str) -> bool:
    path = repo_root / "skills-index.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    changed = False
    for item in payload.get("skills", []):
        if isinstance(item, dict) and item.get("id") == TARGET_SKILL and item.get("version") != version:
            item["version"] = version
            changed = True
    if changed:
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return changed


def sync_routing_rules(skill_dir: Path, version: str) -> bool:
    path = skill_dir / "references" / "routing-rules.json"
    text = path.read_text(encoding="utf-8")
    payload = json.loads(text)
    meta = payload.get("meta", {})
    if meta.get("version") == version:
        return False
    updated, count = re.subn(r'(?s)("meta"\s*:\s*\{.*?"version"\s*:\s*")[^"]+("\s*,)', rf"\g<1>{version}\2", text, count=1)
    if count != 1:
        raise RuntimeError("routing-rules.json meta.version could not be located")
    json.loads(updated)
    path.write_text(updated, encoding="utf-8")
    return True


def inspect_skills_index_version(repo_root: Path) -> str | None:
    payload = json.loads((repo_root / "skills-index.json").read_text(encoding="utf-8"))
    for item in payload.get("skills", []):
        if isinstance(item, dict) and item.get("id") == TARGET_SKILL:
            value = item.get("version")
            return str(value).strip() if value is not None else None
    return None


def inspect_routing_rules_version(skill_dir: Path) -> str | None:
    payload = json.loads((skill_dir / "references" / "routing-rules.json").read_text(encoding="utf-8"))
    value = payload.get("meta", {}).get("version")
    return str(value).strip() if value is not None else None


def sync_all(repo_root: Path) -> dict[str, object]:
    skill_dir = repo_root / TARGET_SKILL
    version = (skill_dir / "VERSION").read_text(encoding="utf-8").strip()
    changed = {
        "README.md": sync_readme(repo_root, version),
        f"{TARGET_SKILL}/README.md": sync_skill_readme(skill_dir, version),
        "skills-index.json": sync_skills_index(repo_root, version),
        f"{TARGET_SKILL}/references/routing-rules.json": sync_routing_rules(skill_dir, version),
    }
    changed.update(sync_docs_html(skill_dir, version))
    return {"skill": TARGET_SKILL, "version": version, "changed": changed}


def check_all(repo_root: Path) -> dict[str, object]:
    skill_dir = repo_root / TARGET_SKILL
    version = (skill_dir / "VERSION").read_text(encoding="utf-8").strip()
    readme = (repo_root / "README.md").read_text(encoding="utf-8")
    updated_readme, _ = update_readme_text(readme, version)
    skill_readme = (skill_dir / "README.md").read_text(encoding="utf-8")
    updated_skill_readme, _ = update_skill_readme_text(skill_readme, version)
    changed = {
        "README.md": readme != updated_readme,
        f"{TARGET_SKILL}/README.md": skill_readme != updated_skill_readme,
        "skills-index.json": inspect_skills_index_version(repo_root) != version,
        f"{TARGET_SKILL}/references/routing-rules.json": inspect_routing_rules_version(skill_dir) != version,
    }
    for filename in DOC_HTML_FILES:
        path = skill_dir / "docs" / filename
        if path.exists():
            text = path.read_text(encoding="utf-8")
            updated, _ = update_docs_html_text(text, version)
            changed[f"{TARGET_SKILL}/docs/{filename}"] = text != updated
    return {"skill": TARGET_SKILL, "version": version, "changed": changed}
