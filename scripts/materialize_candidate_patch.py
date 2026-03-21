#!/usr/bin/env python3
"""Materialize a candidate brief with a structured mutation plan into a patch artifact."""

from __future__ import annotations

import argparse
import copy
import difflib
import json
import os
from pathlib import Path


def load_json(path: Path) -> dict[str, object]:
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, dict):
        raise RuntimeError(f"{path} must contain a JSON object")
    return data


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def resolve_repo_path(candidate_root: Path, value: object) -> tuple[Path, str]:
    if not isinstance(value, str) or value.strip() == "":
        raise RuntimeError("mutation operation is missing a relative path")
    candidate_root = candidate_root.resolve()
    target = (candidate_root / value).resolve()
    if os.path.commonpath([str(candidate_root), str(target)]) != str(candidate_root):
        raise RuntimeError(f"mutation path escapes candidate root: {value}")
    return target, target.relative_to(candidate_root).as_posix()


def nth_index(content: str, needle: str, occurrence: int) -> int:
    if needle == "":
        raise RuntimeError("anchor text cannot be empty")
    if occurrence < 1:
        raise RuntimeError("occurrence must be >= 1")
    start = 0
    index = -1
    for _ in range(occurrence):
        index = content.find(needle, start)
        if index < 0:
            raise RuntimeError(f"anchor not found: {needle}")
        start = index + len(needle)
    return index


def ensure_text_state(state: dict[str, object]) -> str:
    current_exists = bool(state["current_exists"])
    current_text = state["current_text"]
    if not current_exists or not isinstance(current_text, str):
        raise RuntimeError(f"operation requires an existing text file: {state['relative_path']}")
    return current_text


def render_json_document(document: object) -> str:
    return json.dumps(document, ensure_ascii=False, indent=2) + "\n"


def load_json_document(
    state: dict[str, object],
    op: str,
    *,
    create_missing: bool = False,
    default_root: object | None = None,
) -> object:
    current_exists = bool(state["current_exists"])
    current_text = state["current_text"]
    if current_exists:
        if not isinstance(current_text, str):
            raise RuntimeError(f"{op} requires valid JSON text in {state['relative_path']}")
        try:
            return json.loads(current_text)
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                f"{op} requires valid JSON in {state['relative_path']}: {exc.msg}"
            ) from exc
    if not create_missing:
        raise RuntimeError(f"{op} requires an existing JSON file: {state['relative_path']}")
    if default_root is None:
        return {}
    return copy.deepcopy(default_root)


def token_prefers_list(token: str | None) -> bool:
    return token == "-" or (token is not None and token.isdigit())


def parse_json_pointer(pointer: object, op: str) -> list[str]:
    if not isinstance(pointer, str):
        raise RuntimeError(f"{op} requires a string pointer")
    if pointer == "":
        return []
    if not pointer.startswith("/"):
        raise RuntimeError(f"{op} pointer must be empty or start with '/': {pointer}")
    return [
        token.replace("~1", "/").replace("~0", "~")
        for token in pointer.split("/")[1:]
    ]


def parse_array_index(
    token: str,
    *,
    allow_append: bool,
    relative_path: str,
    pointer: str,
) -> int | None:
    if token == "-" and allow_append:
        return None
    if not token.isdigit():
        raise RuntimeError(
            f"pointer {pointer} uses a non-numeric array token in {relative_path}: {token}"
        )
    return int(token)


def default_container_for_token(token: str | None) -> object:
    return [] if token_prefers_list(token) else {}


def navigate_json_parent(
    document: object,
    tokens: list[str],
    *,
    create_missing: bool,
    relative_path: str,
    pointer: str,
) -> tuple[object, str]:
    if not tokens:
        raise RuntimeError(f"pointer cannot be empty for this operation in {relative_path}")
    current = document
    for index, token in enumerate(tokens[:-1]):
        next_token = tokens[index + 1] if index + 1 < len(tokens) else None
        if isinstance(current, dict):
            if token not in current:
                if not create_missing:
                    raise RuntimeError(f"missing pointer segment in {relative_path}: {pointer}")
                current[token] = default_container_for_token(next_token)
            current = current[token]
            continue
        if isinstance(current, list):
            parsed = parse_array_index(
                token,
                allow_append=create_missing,
                relative_path=relative_path,
                pointer=pointer,
            )
            if parsed is None:
                new_value = default_container_for_token(next_token)
                current.append(new_value)
                current = new_value
                continue
            if parsed < len(current):
                current = current[parsed]
                continue
            if parsed == len(current) and create_missing:
                new_value = default_container_for_token(next_token)
                current.append(new_value)
                current = new_value
                continue
            raise RuntimeError(f"pointer {pointer} is out of range in {relative_path}")
        raise RuntimeError(
            f"pointer {pointer} traverses a non-container value in {relative_path}"
        )
    return current, tokens[-1]


def get_json_value(
    document: object,
    tokens: list[str],
    *,
    relative_path: str,
    pointer: str,
) -> object | None:
    current = document
    for token in tokens:
        if isinstance(current, dict):
            if token not in current:
                return None
            current = current[token]
            continue
        if isinstance(current, list):
            parsed = parse_array_index(
                token,
                allow_append=False,
                relative_path=relative_path,
                pointer=pointer,
            )
            if parsed is None or parsed >= len(current):
                return None
            current = current[parsed]
            continue
        return None
    return current


def set_json_value(
    document: object,
    tokens: list[str],
    value: object,
    *,
    create_missing: bool,
    relative_path: str,
    pointer: str,
) -> object:
    if not tokens:
        return copy.deepcopy(value)

    parent, token = navigate_json_parent(
        document,
        tokens,
        create_missing=create_missing,
        relative_path=relative_path,
        pointer=pointer,
    )
    if isinstance(parent, dict):
        parent[token] = copy.deepcopy(value)
        return document
    if isinstance(parent, list):
        parsed = parse_array_index(
            token,
            allow_append=create_missing,
            relative_path=relative_path,
            pointer=pointer,
        )
        if parsed is None or parsed == len(parent):
            parent.append(copy.deepcopy(value))
            return document
        if parsed < len(parent):
            parent[parsed] = copy.deepcopy(value)
            return document
        raise RuntimeError(f"pointer {pointer} is out of range in {relative_path}")
    raise RuntimeError(f"pointer {pointer} targets a non-container value in {relative_path}")


def delete_json_value(
    document: object,
    tokens: list[str],
    *,
    relative_path: str,
    pointer: str,
) -> object:
    if not tokens:
        raise RuntimeError(f"json_delete cannot delete the root document in {relative_path}")

    parent, token = navigate_json_parent(
        document,
        tokens,
        create_missing=False,
        relative_path=relative_path,
        pointer=pointer,
    )
    if isinstance(parent, dict):
        if token not in parent:
            raise RuntimeError(f"pointer {pointer} does not exist in {relative_path}")
        del parent[token]
        return document
    if isinstance(parent, list):
        parsed = parse_array_index(
            token,
            allow_append=False,
            relative_path=relative_path,
            pointer=pointer,
        )
        if parsed is None or parsed >= len(parent):
            raise RuntimeError(f"pointer {pointer} is out of range in {relative_path}")
        parent.pop(parsed)
        return document
    raise RuntimeError(f"pointer {pointer} targets a non-container value in {relative_path}")


def deep_merge_json(base: object, patch: object) -> object:
    if not isinstance(base, dict) or not isinstance(patch, dict):
        return copy.deepcopy(patch)
    merged = copy.deepcopy(base)
    for key, value in patch.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = deep_merge_json(merged[key], value)
        else:
            merged[key] = copy.deepcopy(value)
    return merged


def append_json_value(
    document: object,
    tokens: list[str],
    value: object,
    *,
    unique: bool,
    match_keys: list[str],
    relative_path: str,
    pointer: str,
) -> object:
    if not tokens:
        target = document
    else:
        target = get_json_value(
            document,
            tokens,
            relative_path=relative_path,
            pointer=pointer,
        )
        if target is None:
            document = set_json_value(
                document,
                tokens,
                [],
                create_missing=True,
                relative_path=relative_path,
                pointer=pointer,
            )
            target = get_json_value(
                document,
                tokens,
                relative_path=relative_path,
                pointer=pointer,
            )
    if not isinstance(target, list):
        raise RuntimeError(f"pointer {pointer} does not target a JSON array in {relative_path}")

    candidate = copy.deepcopy(value)
    if unique:
        for existing in target:
            if match_keys:
                if not isinstance(existing, dict) or not isinstance(candidate, dict):
                    continue
                if all(existing.get(key) == candidate.get(key) for key in match_keys):
                    return document
            elif existing == candidate:
                return document
    target.append(candidate)
    return document


def apply_json_operation(state: dict[str, object], operation: dict[str, object], op: str) -> None:
    pointer = str(operation.get("pointer", ""))
    tokens = parse_json_pointer(pointer, op)
    value = copy.deepcopy(operation.get("value"))
    default_root = default_container_for_token(tokens[0]) if tokens else {}

    if op == "json_set":
        document = load_json_document(
            state,
            op,
            create_missing=True,
            default_root=default_root,
        )
        document = set_json_value(
            document,
            tokens,
            value,
            create_missing=True,
            relative_path=str(state["relative_path"]),
            pointer=pointer,
        )
    elif op == "json_merge":
        if not isinstance(value, dict):
            raise RuntimeError(f"{op} requires an object value")
        document = load_json_document(
            state,
            op,
            create_missing=True,
            default_root=default_root,
        )
        if not tokens:
            if not isinstance(document, dict):
                raise RuntimeError(f"{op} requires the root document to be an object")
            document = deep_merge_json(document, value)
        else:
            existing = get_json_value(
                document,
                tokens,
                relative_path=str(state["relative_path"]),
                pointer=pointer,
            )
            if existing is None:
                document = set_json_value(
                    document,
                    tokens,
                    value,
                    create_missing=True,
                    relative_path=str(state["relative_path"]),
                    pointer=pointer,
                )
            else:
                if not isinstance(existing, dict):
                    raise RuntimeError(f"{op} requires the target pointer to be an object")
                document = set_json_value(
                    document,
                    tokens,
                    deep_merge_json(existing, value),
                    create_missing=False,
                    relative_path=str(state["relative_path"]),
                    pointer=pointer,
                )
    elif op == "json_delete":
        document = load_json_document(state, op, create_missing=False)
        document = delete_json_value(
            document,
            tokens,
            relative_path=str(state["relative_path"]),
            pointer=pointer,
        )
    elif op in {"json_append", "json_append_unique"}:
        document = load_json_document(
            state,
            op,
            create_missing=True,
            default_root=[] if not tokens else default_root,
        )
        match_keys_value = operation.get("match_keys")
        match_keys = (
            [str(item).strip() for item in match_keys_value if str(item).strip() != ""]
            if isinstance(match_keys_value, list)
            else []
        )
        document = append_json_value(
            document,
            tokens,
            value,
            unique=op == "json_append_unique",
            match_keys=match_keys,
            relative_path=str(state["relative_path"]),
            pointer=pointer,
        )
    else:
        raise RuntimeError(f"unsupported JSON mutation operation: {op}")

    state["current_text"] = render_json_document(document)
    state["current_exists"] = True


def apply_operation(state: dict[str, object], operation: dict[str, object]) -> None:
    op = str(operation.get("op", "")).strip()
    if op == "":
        raise RuntimeError("mutation operation is missing op")

    if op in {"json_set", "json_merge", "json_delete", "json_append", "json_append_unique"}:
        apply_json_operation(state, operation, op)
        return

    if op == "replace_text":
        current = ensure_text_state(state)
        old = str(operation.get("old", ""))
        new = str(operation.get("new", ""))
        count = int(operation.get("count", 1))
        occurrences = current.count(old)
        if occurrences == 0:
            raise RuntimeError(f"replace_text old text not found in {state['relative_path']}")
        if count <= 0:
            updated = current.replace(old, new)
        else:
            if occurrences < count:
                raise RuntimeError(f"replace_text expected at least {count} matches in {state['relative_path']}")
            updated = current.replace(old, new, count)
        state["current_text"] = updated
        state["current_exists"] = True
        return

    if op == "insert_after":
        current = ensure_text_state(state)
        anchor = str(operation.get("anchor", ""))
        text = str(operation.get("text", ""))
        occurrence = int(operation.get("occurrence", 1))
        index = nth_index(current, anchor, occurrence)
        insert_at = index + len(anchor)
        state["current_text"] = current[:insert_at] + text + current[insert_at:]
        state["current_exists"] = True
        return

    if op == "insert_before":
        current = ensure_text_state(state)
        anchor = str(operation.get("anchor", ""))
        text = str(operation.get("text", ""))
        occurrence = int(operation.get("occurrence", 1))
        insert_at = nth_index(current, anchor, occurrence)
        state["current_text"] = current[:insert_at] + text + current[insert_at:]
        state["current_exists"] = True
        return

    if op == "append_text":
        current = state["current_text"] if isinstance(state["current_text"], str) else ""
        state["current_text"] = current + str(operation.get("text", ""))
        state["current_exists"] = True
        return

    if op == "prepend_text":
        current = state["current_text"] if isinstance(state["current_text"], str) else ""
        state["current_text"] = str(operation.get("text", "")) + current
        state["current_exists"] = True
        return

    if op == "write_file":
        state["current_text"] = str(operation.get("content", ""))
        state["current_exists"] = True
        return

    if op == "delete_file":
        state["current_text"] = None
        state["current_exists"] = False
        return

    raise RuntimeError(f"unsupported mutation operation: {op}")


def build_patch_block(
    relative_path: str,
    original_text: str | None,
    current_text: str | None,
    original_exists: bool,
    current_exists: bool,
) -> str:
    if original_exists == current_exists and original_text == current_text:
        return ""

    if not original_exists and current_exists:
        header = [
            f"diff --git a/{relative_path} b/{relative_path}\n",
            "new file mode 100644\n",
        ]
        diff_iter = difflib.unified_diff(
            [],
            (current_text or "").splitlines(keepends=True),
            fromfile="/dev/null",
            tofile=f"b/{relative_path}",
            lineterm="",
        )
    elif original_exists and not current_exists:
        header = [
            f"diff --git a/{relative_path} b/{relative_path}\n",
            "deleted file mode 100644\n",
        ]
        diff_iter = difflib.unified_diff(
            (original_text or "").splitlines(keepends=True),
            [],
            fromfile=f"a/{relative_path}",
            tofile="/dev/null",
            lineterm="",
        )
    else:
        header = [f"diff --git a/{relative_path} b/{relative_path}\n"]
        diff_iter = difflib.unified_diff(
            (original_text or "").splitlines(keepends=True),
            (current_text or "").splitlines(keepends=True),
            fromfile=f"a/{relative_path}",
            tofile=f"b/{relative_path}",
            lineterm="",
        )

    lines = header
    for line in diff_iter:
        if line.endswith("\n"):
            lines.append(line)
            continue
        lines.append(line + "\n")
        if not (line.startswith("--- ") or line.startswith("+++ ") or line.startswith("@@")):
            lines.append("\\ No newline at end of file\n")
    return "".join(lines)


def mutation_plan_from_payload(payload: dict[str, object]) -> dict[str, object] | None:
    plan = payload.get("mutation_plan")
    return plan if isinstance(plan, dict) else None


def can_materialize_brief_payload(payload: dict[str, object]) -> bool:
    plan = mutation_plan_from_payload(payload)
    if plan is None:
        return False
    operations = plan.get("operations")
    return isinstance(operations, list) and len([item for item in operations if isinstance(item, dict)]) > 0


def materialize_payload(
    payload: dict[str, object],
    candidate_root: Path,
    patch_output: Path,
    patch_strip: int = 1,
    brief_path: Path | None = None,
) -> dict[str, object]:
    plan = mutation_plan_from_payload(payload)
    if plan is None:
        raise RuntimeError("candidate brief has no mutation_plan")
    mode = str(plan.get("mode", "patch")).strip() or "patch"
    if mode != "patch":
        raise RuntimeError(f"unsupported mutation plan mode: {mode}")
    operations_value = plan.get("operations")
    if not isinstance(operations_value, list):
        raise RuntimeError("mutation_plan.operations must be a list")
    operations = [item for item in operations_value if isinstance(item, dict)]
    if not operations:
        raise RuntimeError("mutation_plan.operations must contain at least one operation")

    candidate_root = candidate_root.resolve()
    states: dict[str, dict[str, object]] = {}
    for operation in operations:
        target_path, relative_path = resolve_repo_path(candidate_root, operation.get("path"))
        state = states.get(relative_path)
        if state is None:
            original_exists = target_path.exists()
            original_text = target_path.read_text(encoding="utf-8") if original_exists else None
            state = {
                "target_path": target_path,
                "relative_path": relative_path,
                "original_exists": original_exists,
                "current_exists": original_exists,
                "original_text": original_text,
                "current_text": original_text,
            }
            states[relative_path] = state
        apply_operation(state, operation)

    patch_blocks = [
        build_patch_block(
            relative_path=relative_path,
            original_text=state["original_text"] if isinstance(state["original_text"], str) else None,
            current_text=state["current_text"] if isinstance(state["current_text"], str) else None,
            original_exists=bool(state["original_exists"]),
            current_exists=bool(state["current_exists"]),
        )
        for relative_path, state in sorted(states.items())
    ]
    patch_content = "".join(block for block in patch_blocks if block != "")
    if patch_content == "":
        raise RuntimeError("built-in materializer produced no patch content")

    write_text(patch_output, patch_content)
    return {
        "engine": "builtin-materialize-candidate-patch",
        "brief": str(brief_path.resolve()) if brief_path is not None else None,
        "candidate_root": str(candidate_root),
        "patch_output": str(patch_output.resolve()),
        "patch_strip": patch_strip,
        "mode": mode,
        "operation_count": len(operations),
        "changed_files": sorted(states.keys()),
        "returncode": 0,
        "passed": True,
    }


def materialize_brief(
    brief_path: Path,
    candidate_root: Path,
    patch_output: Path,
    patch_strip: int = 1,
) -> dict[str, object]:
    payload = load_json(brief_path)
    return materialize_payload(
        payload=payload,
        candidate_root=candidate_root,
        patch_output=patch_output,
        patch_strip=patch_strip,
        brief_path=brief_path,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Materialize a candidate brief into a patch artifact.")
    parser.add_argument("--brief", required=True, help="Candidate brief JSON file")
    parser.add_argument("--candidate-root", required=True, help="Candidate repo or worktree root")
    parser.add_argument("--patch-output", required=True, help="Patch file to write")
    parser.add_argument("--patch-strip", type=int, default=1, help="Patch strip count metadata")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = materialize_brief(
        brief_path=Path(args.brief).resolve(),
        candidate_root=Path(args.candidate_root).resolve(),
        patch_output=Path(args.patch_output).resolve(),
        patch_strip=args.patch_strip,
    )
    if args.pretty:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
