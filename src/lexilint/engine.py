"""Core linting engine: parse source, run all rules, sort violations."""

from __future__ import annotations

import ast
from pathlib import Path

from .rules import RULES, Violation


class LintSyntaxError(Exception):
    """Raised when the submitted source cannot be parsed as Python."""

    def __init__(self, path: str | Path, error: SyntaxError) -> None:
        self.path = str(path)
        self.error = error
        super().__init__(
            f"{self.path}:{error.lineno}:{error.offset}: syntax error: {error.msg}"
        )


def lint_source(source: str, *, filename: str = "<source>") -> list[Violation]:
    """Lint one Python source string and return sorted violations."""
    try:
        tree = ast.parse(source, filename=filename)
    except SyntaxError as err:
        raise LintSyntaxError(filename, err) from err
    lines = source.splitlines()
    violations: list[Violation] = []
    for rule in RULES:
        violations.extend(rule.check(tree, lines))
    violations.sort(key=lambda v: (v.line, v.col, v.rule_id))
    # Deduplicate identical findings (chained binary ops can match twice).
    deduped: list[Violation] = []
    seen: set[tuple[str, int, int, str]] = set()
    for violation in violations:
        key = (violation.rule_id, violation.line, violation.col, violation.message)
        if key not in seen:
            seen.add(key)
            deduped.append(violation)
    return deduped


def lint_file(path: str | Path) -> list[Violation]:
    """Lint a Python file on disk."""
    p = Path(path)
    source = p.read_text(encoding="utf-8")
    return lint_source(source, filename=str(p))
