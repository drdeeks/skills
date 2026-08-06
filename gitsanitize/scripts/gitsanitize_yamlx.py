#!/usr/bin/env python3
"""Minimal YAML subset parser used when PyYAML is not installed.

Supports nested maps (indent-based), block lists, inline scalar lists, and
scalar types (str/int/float/bool/null). Keeps GitSanitize dependency-free
while still accepting real YAML when PyYAML is present.

The `load` entry point prefers PyYAML if available.
"""
from __future__ import annotations

import re
from pathlib import Path

try:
    import yaml as _pyyaml
    HAS_PYYAML = True
except ImportError:  # pragma: no cover
    _pyyaml = None
    HAS_PYYAML = False

_KEY_RE = re.compile(r"^[A-Za-z0-9_.-]+$")


def _strip_quotes(s: str) -> str:
    s = s.strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in ("'", '"'):
        return s[1:-1]
    return s


def _split_map(text: str):
    """Split 'key: value'. Returns (key, value) where value may be None for
    a key that opens a nested block."""
    key, sep, rest = text.partition(":")
    if not sep:
        raise ValueError(f"not a mapping line: {text!r}")
    key = _strip_quotes(key).strip()
    rest = rest.strip()
    if rest == "" or rest.startswith("#"):
        return key, None
    if rest.startswith("#"):
        return key, None
    return key, _parse_scalar(rest)


def _is_map_item(content: str) -> bool:
    if ":" not in content:
        return False
    key, _, rest = content.partition(":")
    key = _strip_quotes(key).strip()
    if not _KEY_RE.match(key):
        return False
    return True


def _parse_scalar(text: str):
    t = text.strip()
    if t == "" or t.startswith("#"):
        return None
    if t.lower() in ("null", "~"):
        return None
    if t.lower() == "true":
        return True
    if t.lower() == "false":
        return False
    if re.fullmatch(r"-?\d+", t):
        return int(t)
    if re.fullmatch(r"-?\d*\.\d+", t):
        return float(t)
    if t.startswith("[") and t.endswith("]"):
        inner = t[1:-1].strip()
        if not inner:
            return []
        return [_parse_scalar(x) for x in inner.split(",")]
    if t.startswith("{") and t.endswith("}"):
        inner = t[1:-1].strip()
        out = {}
        for pair in inner.split(","):
            if ":" not in pair:
                continue
            k, v = pair.split(":", 1)
            out[_strip_quotes(k).strip()] = _parse_scalar(v)
        return out
    return _strip_quotes(t)


def _next_indent(lines, start):
    for j in range(start, len(lines)):
        ind, txt = lines[j]
        if txt.strip() and not txt.strip().startswith("#"):
            return ind
    return None


def _next_indent_and_kind(lines, start):
    """Like _next_indent, but also reports whether that next line opens a
    block sequence (starts with "-") -- needed to tell a same-indent list
    value apart from a same-indent sibling key."""
    for j in range(start, len(lines)):
        ind, txt = lines[j]
        if txt.strip() and not txt.strip().startswith("#"):
            return ind, txt.startswith("-")
    return None, False


def _parse_node(lines, i: int, indent: int):
    """Parse the block starting at line i. Returns (value, next_index)."""
    if i >= len(lines):
        return None, i
    ind, text = lines[i]
    if ind != indent:
        return None, i

    if text.startswith("-"):
        node = []
        while i < len(lines):
            ind, text = lines[i]
            if ind != indent:
                break
            if text.startswith("#"):
                i += 1
                continue
            if not text.startswith("-"):
                break
            content = text[1:].strip()
            if content.startswith("#") or content == "":
                child_ind = _next_indent(lines, i + 1)
                if child_ind is None or child_ind <= indent:
                    node.append(None)
                else:
                    item, i = _parse_node(lines, i + 1, child_ind)
                    node.append(item if item is not None else None)
                continue
            if _is_map_item(content):
                key, val = _split_map(content)
                if val is None:
                    child_ind = _next_indent(lines, i + 1)
                    if child_ind is not None and child_ind > indent:
                        item, i = _parse_node(lines, i + 1, child_ind)
                        node.append({key: item})
                    else:
                        node.append({key: {}})
                        i += 1
                else:
                    d = {key: val}
                    node.append(d)
                    i += 1
                    # absorb indented continuation keys for this item
                    child_ind = _next_indent(lines, i)
                    if child_ind is not None and child_ind > indent:
                        extra, i = _parse_node(lines, i, child_ind)
                        if isinstance(extra, dict):
                            d.update(extra)
            else:
                node.append(_parse_scalar(content))
                i += 1
        return node, i

    node = {}
    while i < len(lines):
        ind, text = lines[i]
        if ind != indent:
            break
        if text.startswith("#"):
            i += 1
            continue
        if text.startswith("-"):
            break
        if ":" not in text:
            i += 1
            continue
        key, val = _split_map(text)
        if val is None:
            child_ind, child_is_seq = _next_indent_and_kind(lines, i + 1)
            # A block sequence value is valid YAML at the SAME indent as its
            # own key ("key:\n- item", exactly what dump() below emits) or
            # deeper. A nested MAPPING must be strictly deeper -- at the same
            # indent it would be ambiguous with a sibling key. Requiring
            # strictly-greater indent for both (the previous behavior) silently
            # turned every same-indent list into an empty dict: `identity_rules:`
            # followed by a same-indent `- name: ...` list parsed to `{}`,
            # dropping every rule with no error until the schema check downstream
            # caught the shape mismatch.
            if child_ind is not None and (child_ind > indent or (child_ind == indent and child_is_seq)):
                child, i = _parse_node(lines, i + 1, child_ind)
                node[key] = child if child is not None else {}
            else:
                node[key] = {}
                i += 1
        else:
            node[key] = val
            i += 1
    return node, i


def parse_yaml(text: str):
    if HAS_PYYAML:
        return _pyyaml.safe_load(text)
    lines = []
    for lineno, raw in enumerate(text.splitlines(), 1):
        if not raw.strip():
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        if "\t" in raw[:indent]:
            raise ValueError(f"tabs are not allowed for indentation (line {lineno})")
        lines.append((indent, raw.lstrip()))
    if not lines:
        return {}
    try:
        value, _ = _parse_node(lines, 0, lines[0][0])
        return value if value is not None else {}
    except ValueError as exc:
        raise ValueError(f"invalid YAML (mini parser): {exc}") from exc


def load(path) -> dict:
    p = Path(path)
    data = parse_yaml(p.read_text(encoding="utf-8"))
    return data or {}


def _dump_scalar(v) -> str:
    if v is None:
        return "null"
    if v is True:
        return "true"
    if v is False:
        return "false"
    if isinstance(v, (int, float)):
        return str(v)
    if isinstance(v, (list, dict)):
        return _dump_inline(v)
    s = str(v)
    if "\n" in s:
        return "|\n" + "".join(f"    {l}\n" for l in s.splitlines())
    return f"{s!r}" if any(c in s for c in ":{}[],&*#?|-<>=!%@`") else s


def _dump_inline(v):
    if isinstance(v, list):
        return "[" + ", ".join(_dump_scalar(x) for x in v) + "]"
    if isinstance(v, dict):
        return "{ " + ", ".join(f"{k}: {_dump_scalar(x)}" for k, x in v.items()) + " }"
    return _dump_scalar(v)


def dump(obj, indent: int = 2) -> str:
    if HAS_PYYAML:
        try:
            return _pyyaml.safe_dump(obj, sort_keys=False)
        except Exception:
            pass
    out = []

    def emit(value, level):
        pad = " " * (indent * level)
        if isinstance(value, dict):
            for k, v in value.items():
                if isinstance(v, (dict, list)):
                    out.append(f"{pad}{k}:")
                    emit(v, level + 1)
                else:
                    out.append(f"{pad}{k}: {_dump_scalar(v)}")
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, (dict, list)):
                    out.append(f"{pad}-")
                    emit(item, level + 1)
                else:
                    out.append(f"{pad}- {_dump_scalar(item)}")

    emit(obj, 0)
    return "\n".join(out) + "\n"


if __name__ == "__main__":  # pragma: no cover
    import argparse as _argparse
    _p = _argparse.ArgumentParser(
        prog="gitsanitize_yamlx.py",
        description=(
            "gitsanitize library module: yamlx.py. This is implementation, "
            "not a standalone CLI -- run scripts/gitsanitize.py instead, "
            "which is the real entry point and imports this module itself."
        ),
    )
    _p.parse_args()  # no arguments defined: --help prints usage and exits 0;
                      # any unexpected argument is argparse's own clean
                      # "unrecognized arguments" error (exit 2), not a traceback
