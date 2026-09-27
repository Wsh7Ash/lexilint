"""Grading: rule coverage + behavior verification for a submission."""

from __future__ import annotations

import io
from contextlib import redirect_stdout
from dataclasses import dataclass

from .engine import LintSyntaxError, lint_source
from .exercises import BehaviorCase, Challenge


@dataclass(frozen=True)
class BehaviorResult:
    call: str
    expected: str
    actual: str
    ok: bool


@dataclass(frozen=True)
class GradeReport:
    challenge_id: str
    target_rules: tuple[str, ...]
    remaining_violations: list
    violations_fixed: list[str]
    behavior_results: list[BehaviorResult]
    stdout_leak: str | None

    @property
    def rules_complete(self) -> bool:
        return set(self.target_rules) <= set(self.violations_fixed)

    @property
    def behavior_ok(self) -> bool:
        return bool(self.behavior_results) and all(r.ok for r in self.behavior_results)

    @property
    def passed(self) -> bool:
        return self.rules_complete and self.behavior_ok and not self.remaining_violations


def _run_behavior(source: str, case: BehaviorCase) -> tuple[BehaviorResult, str]:
    namespace: dict = {}
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        try:
            exec(compile(source, "<submission>", "exec"), namespace)  # noqa: S102
            result = eval(case.call, namespace)  # noqa: S307
        except Exception as err:  # learner code may raise anything
            return (
                BehaviorResult(case.call, case.expected, f"raised {err!r}", False),
                "",
            )
    actual = repr(result)
    return (
        BehaviorResult(case.call, case.expected, actual, actual == case.expected),
        buffer.getvalue(),
    )


def grade_submission(challenge: Challenge, source: str) -> GradeReport:
    """Grade a learner submission: lint it and verify behavior."""
    baseline = lint_source(challenge.flawed, filename="flawed")
    baseline_ids = {v.rule_id for v in baseline}

    try:
        violations = lint_source(source, filename="submission")
    except LintSyntaxError as err:
        return GradeReport(
            challenge_id=challenge.challenge_id,
            target_rules=challenge.target_rules,
            remaining_violations=[
                type("V", (), {"rule_id": "SYNTAX", "line": 0, "col": 0,
                              "message": str(err)})()
            ],
            violations_fixed=[],
            behavior_results=[],
            stdout_leak=None,
        )

    remaining = list(violations)
    fixed_ids = baseline_ids - {v.rule_id for v in remaining}

    behavior_results = []
    leaked_chunks: list[str] = []
    for case in challenge.behavior:
        result, leaked = _run_behavior(source, case)
        behavior_results.append(result)
        leaked_chunks.append(leaked)

    # stdout leak check: defining and exercising the submission must print
    # nothing to stdout (module body, function bodies, everything).
    leak = "".join(chunk for chunk in leaked_chunks if chunk) or None

    return GradeReport(
        challenge_id=challenge.challenge_id,
        target_rules=challenge.target_rules,
        remaining_violations=remaining,
        violations_fixed=sorted(fixed_ids),
        behavior_results=behavior_results,
        stdout_leak=leak,
    )
