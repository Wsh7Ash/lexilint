"""Tests for challenge integrity and the grading engine."""

from __future__ import annotations

import unittest

from lexilint.engine import lint_source
from lexilint.exercises import CHALLENGES, get_challenge
from lexilint.grader import grade_submission


class ChallengeIntegrityTests(unittest.TestCase):
    def test_challenges_exist(self) -> None:
        self.assertGreaterEqual(len(CHALLENGES), 4)

    def test_ids_unique(self) -> None:
        ids = [c.challenge_id for c in CHALLENGES]
        self.assertEqual(len(ids), len(set(ids)))

    def test_flawed_triggers_all_target_rules(self) -> None:
        for challenge in CHALLENGES:
            violations = lint_source(challenge.flawed, filename="flawed")
            triggered = {v.rule_id for v in violations}
            missing = set(challenge.target_rules) - triggered
            self.assertEqual(missing, set(), challenge.challenge_id)

    def test_reference_lints_clean(self) -> None:
        for challenge in CHALLENGES:
            violations = lint_source(challenge.reference, filename="reference")
            self.assertEqual(violations, [], challenge.challenge_id)

    def test_get_challenge_roundtrip(self) -> None:
        first = CHALLENGES[0]
        self.assertIs(get_challenge(first.challenge_id), first)

    def test_get_challenge_unknown_raises(self) -> None:
        with self.assertRaises(KeyError):
            get_challenge("NOPE")


class GraderTests(unittest.TestCase):
    def test_reference_solution_passes_every_challenge(self) -> None:
        for challenge in CHALLENGES:
            report = grade_submission(challenge, challenge.reference)
            self.assertTrue(
                report.passed,
                f"{challenge.challenge_id}: remaining={report.remaining_violations} "
                f"behavior={report.behavior_results}",
            )

    def test_flawed_source_fails(self) -> None:
        for challenge in CHALLENGES:
            report = grade_submission(challenge, challenge.flawed)
            self.assertFalse(report.passed, challenge.challenge_id)
            self.assertFalse(report.rules_complete, challenge.challenge_id)

    def test_deleting_functionality_fails_behavior(self) -> None:
        challenge = get_challenge("C1")
        gutted = "def load_numbers(values):\n    return []\n"
        report = grade_submission(challenge, gutted)
        self.assertTrue(report.rules_complete)
        self.assertFalse(report.behavior_ok)
        self.assertFalse(report.passed)

    def test_partial_fix_reports_remaining(self) -> None:
        challenge = get_challenge("C1")
        partial = challenge.flawed.replace(
            'print("skipping " + str(value))', "pass"
        )
        report = grade_submission(challenge, partial)
        # The partial fix removed the skip-print but left the total-print,
        # the bare except, and the concatenation: nothing is fully fixed.
        remaining_ids = {v.rule_id for v in report.remaining_violations}
        self.assertTrue({"LL201", "LL202", "LL206"} <= remaining_ids)
        self.assertFalse(report.passed)

    def test_syntax_error_submission_is_reported(self) -> None:
        challenge = get_challenge("C2")
        report = grade_submission(challenge, "def broken(:\n")
        self.assertFalse(report.passed)
        self.assertEqual(
            report.remaining_violations[0].rule_id, "SYNTAX"
        )

    def test_behavior_mismatch_detected(self) -> None:
        challenge = get_challenge("C2")
        wrong = (
            "def new_basket(items=None, coupon=None):\n"
            "    if items is None:\n"
            "        items = []\n"
            "    if coupon is None:\n"
            "        coupon = 'fallback'\n"
            "    items = [*items, coupon]\n"
            "    return items\n"
        )
        report = grade_submission(challenge, wrong)
        self.assertFalse(report.behavior_ok)

    def test_stdout_leak_detected(self) -> None:
        challenge = get_challenge("C1")
        leaky = (
            "def load_numbers(values):\n"
            "    print('loading')\n"
            "    out = []\n"
            "    for value in values:\n"
            "        try:\n"
            "            out.append(int(value))\n"
            "        except ValueError:\n"
            "            continue\n"
            "    return out\n"
        )
        report = grade_submission(challenge, leaky)
        self.assertIsNotNone(report.stdout_leak)
        self.assertFalse(report.passed)  # LL201 never fixed


if __name__ == "__main__":
    unittest.main()
