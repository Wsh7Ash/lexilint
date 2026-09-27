"""Command-line interface for lexilint."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .engine import LintSyntaxError, lint_file, lint_source
from .exercises import CHALLENGES, get_challenge
from .grader import grade_submission
from .rules import RULES_BY_ID


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="lexilint",
        description="Learn linting by fixing deliberately flawed Python.",
    )
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="command", required=True)

    p_rules = sub.add_parser("rules", help="List every rule with its explanation")
    p_rules.add_argument(
        "--format", choices=("table", "json"), default="table", dest="fmt"
    )

    p_show = sub.add_parser("show", help="Show a challenge and its brief")
    p_show.add_argument("challenge_id")

    p_lint = sub.add_parser(
        "lint", help="Lint a Python file and explain every violation"
    )
    p_lint.add_argument("path")

    p_gr = sub.add_parser("grade", help="Submit a fixed file for grading")
    p_gr.add_argument("challenge_id")
    p_gr.add_argument("path")
    p_gr.add_argument("--json", action="store_true", dest="as_json")

    return parser


def _cmd_rules(fmt: str) -> int:
    if fmt == "json":
        payload = [
            {
                "rule_id": rid,
                "why": RULES_BY_ID[rid].why,
                "fix_hint": RULES_BY_ID[rid].fix_hint,
            }
            for rid in RULES_BY_ID
        ]
        print(json.dumps(payload, indent=2))
        return 0
    for rule_id, rule in RULES_BY_ID.items():
        print(f"{rule_id}: {rule.why}")
        print(f"    fix: {rule.fix_hint}")
    return 0


def _cmd_show(challenge_id: str) -> int:
    try:
        challenge = get_challenge(challenge_id)
    except KeyError:
        print(
            f"lexilint: unknown challenge {challenge_id!r} "
            f"(available: {', '.join(c.challenge_id for c in CHALLENGES)})",
            file=sys.stderr,
        )
        return 2
    print(f"{challenge.challenge_id} — {challenge.title}")
    print()
    print(challenge.brief)
    print()
    print("Rules to satisfy:", ", ".join(challenge.target_rules))
    print()
    print("--- flawed source ---")
    print(challenge.flawed, end="")
    print("--- end ---")
    print()
    print("Run 'lexilint grade C1 your_fixed.py' when ready.")
    return 0


def _cmd_lint(path: str) -> int:
    try:
        violations = lint_file(path)
    except LintSyntaxError as err:
        print(f"lexilint: {err}", file=sys.stderr)
        return 2
    except OSError as err:
        print(f"lexilint: cannot read {path}: {err}", file=sys.stderr)
        return 2
    if not violations:
        print(f"{path}: clean")
        return 0
    for violation in violations:
        rule = RULES_BY_ID.get(violation.rule_id)
        print(f"{path}:{violation.line}:{violation.col}: {violation.rule_id} {violation.message}")
        if rule:
            print(f"    why: {rule.why}")
            print(f"    fix: {rule.fix_hint}")
    return 1


def _cmd_grade(challenge_id: str, path: str, as_json: bool) -> int:
    try:
        challenge = get_challenge(challenge_id)
        source = Path(path).read_text(encoding="utf-8")
    except KeyError:
        print(f"lexilint: unknown challenge {challenge_id!r}", file=sys.stderr)
        return 2
    except OSError as err:
        print(f"lexilint: cannot read {path}: {err}", file=sys.stderr)
        return 2

    report = grade_submission(challenge, source)
    if as_json:
        print(
            json.dumps(
                {
                    "challenge": report.challenge_id,
                    "passed": report.passed,
                    "rules_complete": report.rules_complete,
                    "fixed": report.violations_fixed,
                    "remaining": [
                        {"rule": v.rule_id, "line": v.line, "message": v.message}
                        for v in report.remaining_violations
                    ],
                    "behavior": [
                        {"call": b.call, "ok": b.ok, "actual": b.actual}
                        for b in report.behavior_results
                    ],
                    "stdout_leak": report.stdout_leak,
                },
                indent=2,
            )
        )
        return 0 if report.passed else 1

    print(f"challenge {report.challenge_id}:")
    for rule_id in report.target_rules:
        status = "fixed" if rule_id in report.violations_fixed else "NOT fixed"
        print(f"  {rule_id}: {status}")
    for violation in report.remaining_violations:
        print(f"  still violating: {violation.rule_id} line {violation.line}: {violation.message}")
    for result in report.behavior_results:
        mark = "ok" if result.ok else "FAIL"
        print(f"  behavior [{mark}] {result.call} -> {result.actual}")
        if not result.ok:
            print(f"    expected: {result.expected}")
    if report.stdout_leak:
        print(f"  stdout leak detected: {report.stdout_leak!r}")
    print(f"result: {'PASS' if report.passed else 'NOT YET'}")
    return 0 if report.passed else 1


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if args.command == "rules":
        return _cmd_rules(args.fmt)
    if args.command == "show":
        return _cmd_show(args.challenge_id)
    if args.command == "lint":
        return _cmd_lint(args.path)
    if args.command == "grade":
        return _cmd_grade(args.challenge_id, args.path, args.as_json)
    return 2


CHALLENGES_COUNT = len(CHALLENGES)
