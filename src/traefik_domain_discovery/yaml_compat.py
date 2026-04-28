from __future__ import annotations

import json
from typing import Any

try:
    import yaml as _pyyaml
except ModuleNotFoundError:  # pragma: no cover - exercised only without PyYAML
    _pyyaml = None


def safe_load(text: str) -> Any:
    if _pyyaml is not None:
        return _pyyaml.safe_load(text)

    stripped = text.lstrip()
    if stripped.startswith(("{", "[")):
        return json.loads(text)

    return _parse_simple_yaml(text)


def safe_dump(data: Any, sort_keys: bool = False) -> str:
    if _pyyaml is not None:
        return _pyyaml.safe_dump(data, sort_keys=sort_keys)
    return _dump_simple_yaml(data)


def _parse_simple_yaml(text: str) -> Any:
    root: dict[str, Any] = {}
    stack: list[tuple[int, dict[str, Any]]] = [(-1, root)]

    for raw_line in text.splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        line = raw_line.strip()
        if line.startswith("- "):
            continue
        if ":" not in line:
            continue

        key, raw_value = line.split(":", 1)
        key = key.strip().strip("'\"")
        raw_value = raw_value.strip()

        while stack and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]

        if raw_value == "":
            child: dict[str, Any] = {}
            parent[key] = child
            stack.append((indent, child))
        else:
            parent[key] = _parse_scalar(raw_value)

    return root


def _parse_scalar(value: str) -> Any:
    if value in {"null", "None", "~"}:
        return None
    if value == "true":
        return True
    if value == "false":
        return False
    return value.strip("'\"")


def _dump_simple_yaml(data: Any, indent: int = 0) -> str:
    lines = _dump_lines(data, indent)
    return "\n".join(lines) + "\n"


def _dump_lines(data: Any, indent: int) -> list[str]:
    prefix = " " * indent
    if isinstance(data, dict):
        lines: list[str] = []
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                lines.append(f"{prefix}{key}:")
                lines.extend(_dump_lines(value, indent + 2))
            else:
                lines.append(f"{prefix}{key}: {_format_scalar(value)}")
        return lines

    if isinstance(data, list):
        lines = []
        for item in data:
            if isinstance(item, dict):
                item_lines = _dump_lines(item, indent + 2)
                if item_lines:
                    lines.append(f"{prefix}- {item_lines[0].strip()}")
                    lines.extend(item_lines[1:])
                else:
                    lines.append(f"{prefix}- {{}}")
            elif isinstance(item, list):
                lines.append(f"{prefix}-")
                lines.extend(_dump_lines(item, indent + 2))
            else:
                lines.append(f"{prefix}- {_format_scalar(item)}")
        return lines

    return [f"{prefix}{_format_scalar(data)}"]


def _format_scalar(value: Any) -> str:
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, (int, float)):
        return str(value)
    text = str(value)
    if text == "" or text.startswith(("{", "[", "`")) or ": " in text or "#" in text:
        return json.dumps(text)
    return text

