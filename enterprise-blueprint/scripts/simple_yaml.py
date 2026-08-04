#!/usr/bin/env python3
"""
simple_yaml.py — Minimal stdlib-only YAML subset (dump + load).

This skill's contract is "zero external dependencies — Python 3.8+ stdlib
only" (SKILL.md), but `interactive_setup.py` previously did `import yaml`
(PyYAML) — an external package with no fallback. On a machine without it
installed, every model-map write would crash; on this machine it happened
to be present, which is exactly the kind of silent, environment-dependent
gap the "zero external dependencies" claim exists to prevent. This module
replaces it.

Scope: block-style YAML only (no flow style `{a: b}`/`[a, b]`, no anchors/
aliases/tags). Supports: nested mappings via indentation, block sequences
of scalars (`- item`) and of mappings (`- key: value` followed by more
indented keys at the same level), string/int/float/bool/null scalars,
single/double-quoted strings, and `#`-comments (including trailing inline
comments on a scalar line). This is exactly what `agent-model-map.yaml`/
`crew-model-map.yaml` (references/templates/) use — it is not a general
YAML 1.2 implementation and will not round-trip flow-style or anchor-using
documents.
"""

import re
from typing import Any


# ── Dump ─────────────────────────────────────────────────────────────────

def dump(data: Any, sort_keys: bool = False, default_flow_style: bool = False) -> str:
    """Serialize a dict/list/scalar tree to block-style YAML text."""
    if default_flow_style:
        raise NotImplementedError("simple_yaml only supports block style")
    lines = []
    _dump_node(data, indent=0, lines=lines, sort_keys=sort_keys)
    return "\n".join(lines) + "\n"


def _scalar_to_yaml(v: Any) -> str:
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return str(v)
    s = str(v)
    if s == "" or s in ("null", "true", "false", "~") or re.match(r"^-?\d+(\.\d+)?$", s):
        return f'"{s}"'
    if re.search(r'[:#\[\]{}",&*!|>%@`]|^[\s\-?]|\s$', s):
        escaped = s.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    return s


def _dump_node(node: Any, indent: int, lines: list, sort_keys: bool):
    pad = "  " * indent
    if isinstance(node, dict):
        keys = sorted(node.keys()) if sort_keys else list(node.keys())
        for k in keys:
            v = node[k]
            key_str = _scalar_to_yaml(k) if not re.match(r"^[A-Za-z_][A-Za-z0-9_\-]*$", str(k)) else str(k)
            if isinstance(v, dict) and v:
                lines.append(f"{pad}{key_str}:")
                _dump_node(v, indent + 1, lines, sort_keys)
            elif isinstance(v, list) and v:
                lines.append(f"{pad}{key_str}:")
                _dump_node(v, indent + 1, lines, sort_keys)
            elif isinstance(v, (dict, list)):
                lines.append(f"{pad}{key_str}: {'{}' if isinstance(v, dict) else '[]'}")
            else:
                lines.append(f"{pad}{key_str}: {_scalar_to_yaml(v)}")
    elif isinstance(node, list):
        for item in node:
            if isinstance(item, dict):
                sub_lines = []
                _dump_node(item, 0, sub_lines, sort_keys)
                if sub_lines:
                    lines.append(f"{pad}- {sub_lines[0].lstrip()}")
                    for sl in sub_lines[1:]:
                        lines.append(f"{pad}  {sl}")
            elif isinstance(item, list):
                lines.append(f"{pad}-")
                _dump_node(item, indent + 1, lines, sort_keys)
            else:
                lines.append(f"{pad}- {_scalar_to_yaml(item)}")
    else:
        lines.append(f"{pad}{_scalar_to_yaml(node)}")


# ── Load ─────────────────────────────────────────────────────────────────

def safe_load(text: str) -> Any:
    """Parse block-style YAML text into a dict/list/scalar tree."""
    raw_lines = text.split("\n")
    entries = []  # (indent, content)
    for raw in raw_lines:
        line = _strip_comment(raw)
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip(" "))
        entries.append((indent, line.strip()))
    if not entries:
        return {}
    value, _ = _parse_block(entries, 0, entries[0][0])
    return value


def _strip_comment(line: str) -> str:
    """Remove a # comment, respecting quotes."""
    in_single = in_double = False
    for i, ch in enumerate(line):
        if ch == "'" and not in_double:
            in_single = not in_single
        elif ch == '"' and not in_single:
            in_double = not in_double
        elif ch == "#" and not in_single and not in_double:
            if i == 0 or line[i - 1] == " ":
                return line[:i].rstrip()
    return line.rstrip()


def _parse_scalar(text: str) -> Any:
    text = text.strip()
    if text == "" or text == "~" or text.lower() == "null":
        return None
    if text.lower() == "true":
        return True
    if text.lower() == "false":
        return False
    # Minimal flow-style scalar list support: `[a, "b", 3]`. Not general
    # flow-mapping/nested-flow-sequence support — just what the shipped
    # crew-model-map template actually uses (`phases: [...]`).
    if len(text) >= 2 and text[0] == "[" and text[-1] == "]":
        inner = text[1:-1].strip()
        if not inner:
            return []
        return [_parse_scalar(part) for part in _split_flow_items(inner)]
    if len(text) >= 2 and text[0] == '"' and text[-1] == '"':
        return text[1:-1].replace('\\"', '"').replace("\\\\", "\\")
    if len(text) >= 2 and text[0] == "'" and text[-1] == "'":
        return text[1:-1]
    if re.match(r"^-?\d+$", text):
        return int(text)
    if re.match(r"^-?\d+\.\d+$", text):
        return float(text)
    return text


def _split_flow_items(inner: str) -> list:
    """Split 'a, "b, c", 3' on top-level commas, respecting quotes."""
    items = []
    buf = []
    in_single = in_double = False
    for ch in inner:
        if ch == "'" and not in_double:
            in_single = not in_single
            buf.append(ch)
        elif ch == '"' and not in_single:
            in_double = not in_double
            buf.append(ch)
        elif ch == "," and not in_single and not in_double:
            items.append("".join(buf))
            buf = []
        else:
            buf.append(ch)
    if buf:
        items.append("".join(buf))
    return [i.strip() for i in items]


def _parse_block(entries, start: int, indent: int):
    """Parse a mapping or sequence starting at entries[start], all at `indent`.
    Returns (value, next_index)."""
    if start >= len(entries):
        return {}, start
    first_indent, first_content = entries[start]
    if first_indent != indent:
        return {}, start

    if first_content.startswith("- "):
        return _parse_sequence(entries, start, indent)
    return _parse_mapping(entries, start, indent)


def _parse_sequence(entries, start: int, indent: int):
    items = []
    i = start
    while i < len(entries):
        cur_indent, content = entries[i]
        if cur_indent != indent or not content.startswith("-"):
            break
        rest = content[1:].strip()
        if not rest:
            # Nested block sequence/mapping on following, deeper-indented lines
            i += 1
            if i < len(entries) and entries[i][0] > indent:
                value, i = _parse_block(entries, i, entries[i][0])
                items.append(value)
            else:
                items.append(None)
            continue
        if ":" in rest and _is_mapping_line(rest):
            # "- key: value" starts a mapping; item spans this line plus any
            # deeper-indented continuation lines (item_indent = indent+2 by
            # convention of the "- " prefix width)
            item_indent = cur_indent + 2
            synthetic = [(item_indent, rest)]
            j = i + 1
            while j < len(entries) and entries[j][0] > cur_indent and not (
                entries[j][0] == item_indent and entries[j][1].startswith("- ") is False and False
            ):
                if entries[j][0] < item_indent:
                    break
                synthetic.append((entries[j][0], entries[j][1]))
                j += 1
            value, _ = _parse_mapping(synthetic, 0, item_indent)
            items.append(value)
            i = j
            continue
        items.append(_parse_scalar(rest))
        i += 1
    return items, i


def _is_mapping_line(text: str) -> bool:
    """True if 'key: value' (colon not inside quotes)."""
    in_single = in_double = False
    for i, ch in enumerate(text):
        if ch == "'" and not in_double:
            in_single = not in_single
        elif ch == '"' and not in_single:
            in_double = not in_double
        elif ch == ":" and not in_single and not in_double:
            return i + 1 == len(text) or text[i + 1] == " "
    return False


def _parse_mapping(entries, start: int, indent: int):
    result = {}
    i = start
    while i < len(entries):
        cur_indent, content = entries[i]
        if cur_indent != indent:
            break
        if content.startswith("- "):
            break
        if not _is_mapping_line(content):
            i += 1
            continue
        key_part, _, value_part = content.partition(":")
        key = _parse_scalar(key_part)
        value_part = value_part.strip()
        if value_part:
            result[key] = _parse_scalar(value_part)
            i += 1
        else:
            i += 1
            if i < len(entries) and entries[i][0] > indent:
                value, i = _parse_block(entries, i, entries[i][0])
                result[key] = value
            else:
                result[key] = None
    return result, i


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2 or sys.argv[1] in ("--help", "-h"):
        print(__doc__)
        print("Usage: simple_yaml.py <file.yaml>  # parses and pretty-prints as JSON")
        sys.exit(0)
    import json
    from pathlib import Path
    path = Path(sys.argv[1])
    if not path.is_file():
        print(f"Error: not a file: {path}", file=sys.stderr)
        sys.exit(1)
    print(json.dumps(safe_load(path.read_text()), indent=2))
