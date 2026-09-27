"""Lint rules used by lexilint.

Every rule carries a human explanation (``why``) and a concrete ``fix_hint``
so learners learn the reason behind the rule, not just the rule id.
"""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from typing import Callable

MAX_LINE_LENGTH = 88


@dataclass(frozen=True)
class Violation:
    rule_id: str
    line: int
    col: int
    message: str


@dataclass(frozen=True)
class Rule:
    rule_id: str
    why: str
    fix_hint: str
    check: Callable[[ast.Module, list[str]], list[Violation]]


def _line_len_violations(tree: ast.Module, lines: list[str]) -> list[Violation]:
    out: list[Violation] = []
    for i, line in enumerate(lines, start=1):
        physical = len(line.rstrip("\n\r"))
        if physical > MAX_LINE_LENGTH:
            out.append(
                Violation(
                    "LL101",
                    i,
                    0,
                    f"line is {physical} characters (max {MAX_LINE_LENGTH})",
                )
            )
    return out


def _todo_violations(tree: ast.Module, lines: list[str]) -> list[Violation]:
    out: list[Violation] = []
    for i, line in enumerate(lines, start=1):
        if re.search(r"\b(TODO|FIXME|XXX)\b", line):
            out.append(
                Violation("LL102", i, 0, "unresolved TODO/FIXME marker left in source")
            )
    return out


def _print_violations(tree: ast.Module, lines: list[str]) -> list[Violation]:
    out: list[Violation] = []
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "print"
        ):
            out.append(
                Violation(
                    "LL201",
                    node.lineno,
                    node.col_offset,
                    "print() call in library code; use logging or return values",
                )
            )
    return out


def _bare_except_violations(tree: ast.Module, lines: list[str]) -> list[Violation]:
    out: list[Violation] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ExceptHandler) and node.type is None:
            out.append(
                Violation(
                    "LL202",
                    node.lineno,
                    node.col_offset,
                    "bare except: catches KeyboardInterrupt/SystemExit and hides bugs",
                )
            )
    return out


def _mutable_default_violations(tree: ast.Module, lines: list[str]) -> list[Violation]:
    out: list[Violation] = []
    mutable_calls = (ast.List, ast.Dict, ast.Set)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            args = [*node.args.args, *node.args.kwonlyargs]
            defaults = [*node.args.defaults, *node.args.kw_defaults]
            for arg, default in zip(args, defaults):
                if default is None:
                    continue
                if isinstance(default, mutable_calls) or (
                    isinstance(default, ast.Call)
                    and isinstance(default.func, ast.Name)
                    and default.func.id in {"list", "dict", "set"}
                ):
                    out.append(
                        Violation(
                            "LL203",
                            default.lineno,
                            default.col_offset,
                            f"mutable default for parameter {arg.arg!r}: the object is "
                            "shared across all calls",
                        )
                    )
    return out


def _eq_none_violations(tree: ast.Module, lines: list[str]) -> list[Violation]:
    out: list[Violation] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Compare):
            for op, comparator in zip(node.ops, node.comparators):
                if isinstance(op, (ast.Eq, ast.NotEq)) and isinstance(
                    comparator, ast.Constant
                ) and comparator.value is None:
                    hint = "is None" if isinstance(op, ast.Eq) else "is not None"
                    kind = "==" if isinstance(op, ast.Eq) else "!="
                    out.append(
                        Violation(
                            "LL204",
                            node.lineno,
                            node.col_offset,
                            f"comparison to None with {kind}; use '{hint}'",
                        )
                    )
    return out


def _shadow_builtin_violations(tree: ast.Module, lines: list[str]) -> list[Violation]:
    out: list[Violation] = []
    shadowed_builtins = {
        "list", "dict", "set", "tuple", "str", "int", "float", "bool",
        "sum", "min", "max", "len", "type", "id", "input", "format",
    }
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name in shadowed_builtins:
                out.append(
                    Violation(
                        "LL205",
                        node.lineno,
                        node.col_offset,
                        f"function name {node.name!r} shadows a builtin",
                    )
                )
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in shadowed_builtins:
                    out.append(
                        Violation(
                            "LL205",
                            node.lineno,
                            node.col_offset,
                            f"assignment shadows builtin {target.id!r}",
                        )
                    )
    return out


def _string_concat_violations(tree: ast.Module, lines: list[str]) -> list[Violation]:
    out: list[Violation] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
            left_is_str = isinstance(node.left, ast.Constant) and isinstance(
                node.left.value, str
            )
            right_is_str = isinstance(node.right, ast.Constant) and isinstance(
                node.right.value, str
            )
            if left_is_str or right_is_str:
                out.append(
                    Violation(
                        "LL206",
                        node.lineno,
                        node.col_offset,
                        "string built with +; prefer an f-string for clarity and speed",
                    )
                )
    return out


RULES: list[Rule] = [
    Rule(
        "LL101",
        "Long lines do not fit in side-by-side diffs, review panes, or terminals, "
        "which hides surrounding context from the reader.",
        "Break the line at a natural boundary, extract a variable, or use "
        "parenthesized continuation lines.",
        _line_len_violations,
    ),
    Rule(
        "LL102",
        "TODO/FIXME markers are promises that live forever once committed. "
        "Anything worth doing should be a tracked task, not a comment.",
        "Resolve it now, or move it to your issue tracker and delete the marker.",
        _todo_violations,
    ),
    Rule(
        "LL201",
        "print() in library code sends output to stdout even when the module is "
        "imported by another program, corrupting pipelines and CLI output.",
        "Use the logging module (logger.info/debug) or return the value to the caller.",
        _print_violations,
    ),
    Rule(
        "LL202",
        "A bare 'except:' also catches KeyboardInterrupt and SystemExit, and hides "
        "real bugs like NameError, making failures invisible.",
        "Catch the specific exception you can handle, e.g. 'except ValueError:'.",
        _bare_except_violations,
    ),
    Rule(
        "LL203",
        "A mutable default (list/dict/set) is created once at function definition "
        "and shared between every call, so state leaks between calls.",
        "Use None as the default and create the container inside the body: "
        "'def f(items=None): items = items or []'.",
        _mutable_default_violations,
    ),
    Rule(
        "LL204",
        "'x == None' uses value equality; a class can override __eq__ and make the "
        "comparison lie. Identity (is) is the correct test for None.",
        "Write 'x is None' or 'x is not None'.",
        _eq_none_violations,
    ),
    Rule(
        "LL205",
        "Shadowing builtins like 'list' or 'sum' disables them for the rest of the "
        "scope, causing confusing TypeErrors far from the cause.",
        "Rename the variable/function to something descriptive: 'items', 'total', ...",
        _shadow_builtin_violations,
    ),
    Rule(
        "LL206",
        "Concatenating strings with + creates an intermediate object per pair and "
        "reads poorly once more than two pieces are involved.",
        "Use an f-string: f\"hello {name}, you are {age}\".",
        _string_concat_violations,
    ),
]

RULES_BY_ID: dict[str, Rule] = {r.rule_id: r for r in RULES}
