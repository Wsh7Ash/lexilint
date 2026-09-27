"""Generate demo output artifacts into results/ and print them."""

from __future__ import annotations

import json
from pathlib import Path

from lexilint.engine import lint_source
from lexilint.exercises import CHALLENGES
from lexilint.grader import grade_submission
from lexilint.rules import RULES_BY_ID

RESULTS = Path(__file__).resolve().parents[0] / "results"


def main() -> int:
    RESULTS.mkdir(exist_ok=True)

    # 1. Rules catalog
    lines = ["# lexilint rule catalog", ""]
    for rule_id, rule in RULES_BY_ID.items():
        lines.append(f"## {rule_id}")
        lines.append(f"- why: {rule.why}")
        lines.append(f"- fix: {rule.fix_hint}")
        lines.append("")
    (RESULTS / "rules.md").write_text("\n".join(lines), encoding="utf-8")

    # 2. Lint the flawed source of every challenge
    report_lines = ["# Flawed-source lint reports", ""]
    for challenge in CHALLENGES:
        report_lines.append(f"## {challenge.challenge_id} — {challenge.title}")
        for violation in lint_source(challenge.flawed):
            report_lines.append(
                f"- line {violation.line}: {violation.rule_id} {violation.message}"
            )
        report_lines.append("")
    (RESULTS / "flawed-reports.md").write_text(
        "\n".join(report_lines), encoding="utf-8"
    )

    # 3. Grade every reference solution (should all pass)
    grades = {}
    for challenge in CHALLENGES:
        report = grade_submission(challenge, challenge.reference)
        grades[challenge.challenge_id] = {
            "passed": report.passed,
            "fixed": report.violations_fixed,
            "behavior_ok": report.behavior_ok,
        }
    (RESULTS / "reference-grades.json").write_text(
        json.dumps(grades, indent=2), encoding="utf-8"
    )

    print(f"wrote {RESULTS / 'rules.md'}")
    print(f"wrote {RESULTS / 'flawed-reports.md'}")
    print(f"wrote {RESULTS / 'reference-grades.json'}")
    print(f"all reference solutions pass: {all(g['passed'] for g in grades.values())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
