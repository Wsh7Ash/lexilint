"""Tests for the lexilint rule engine and every individual rule."""

from __future__ import annotations

import unittest

from lexilint.engine import LintSyntaxError, lint_source
from lexilint.rules import MAX_LINE_LENGTH, RULES, RULES_BY_ID


class EngineTests(unittest.TestCase):
    def test_clean_source_has_no_violations(self) -> None:
        source = "value = 1\n"
        self.assertEqual(lint_source(source), [])

    def test_syntax_error_raises(self) -> None:
        with self.assertRaises(LintSyntaxError) as ctx:
            lint_source("def broken(:\n")
        self.assertIn("syntax error", str(ctx.exception))

    def test_violations_sorted_by_line(self) -> None:
        source = (
            "x == None\n"
            "def f(a=[]):\n"
            "    pass\n"
        )
        violations = lint_source(source)
        lines = [v.line for v in violations]
        self.assertEqual(lines, sorted(lines))

    def test_rule_registry_ids_unique(self) -> None:
        ids = [r.rule_id for r in RULES]
        self.assertEqual(len(ids), len(set(ids)))


class LineLengthTests(unittest.TestCase):
    def test_long_line_flagged(self) -> None:
        source = f"x = {'a' * (MAX_LINE_LENGTH + 1)}\n"
        violations = [v for v in lint_source(source) if v.rule_id == "LL101"]
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0].line, 1)

    def test_exact_limit_ok(self) -> None:
        source = f"x = {'a' * (MAX_LINE_LENGTH - 4)}\n"
        violations = [v for v in lint_source(source) if v.rule_id == "LL101"]
        self.assertEqual(violations, [])


class TodoTests(unittest.TestCase):
    def test_todo_and_fixme_flagged(self) -> None:
        source = "# TODO: later\n# FIXME: soon\n# plain note\n"
        violations = [v for v in lint_source(source) if v.rule_id == "LL102"]
        self.assertEqual([v.line for v in violations], [1, 2])

    def test_todo_inside_word_not_flagged(self) -> None:
        source = "word = 'autodidactic'\n"
        violations = [v for v in lint_source(source) if v.rule_id == "LL102"]
        self.assertEqual(violations, [])


class PrintTests(unittest.TestCase):
    def test_print_flagged(self) -> None:
        violations = [v for v in lint_source("print('hi')\n") if v.rule_id == "LL201"]
        self.assertEqual(len(violations), 1)

    def test_defined_print_not_flagged(self) -> None:
        source = "print = 3\n"
        violations = [v for v in lint_source(source) if v.rule_id == "LL201"]
        self.assertEqual(violations, [])

    def test_method_named_print_not_flagged(self) -> None:
        source = "obj.print('hi')\n"
        violations = [v for v in lint_source(source) if v.rule_id == "LL201"]
        self.assertEqual(violations, [])


class BareExceptTests(unittest.TestCase):
    def test_bare_except_flagged(self) -> None:
        source = "try:\n    pass\nexcept:\n    pass\n"
        violations = [v for v in lint_source(source) if v.rule_id == "LL202"]
        self.assertEqual(len(violations), 1)

    def test_typed_except_not_flagged(self) -> None:
        source = "try:\n    pass\nexcept ValueError:\n    pass\n"
        violations = [v for v in lint_source(source) if v.rule_id == "LL202"]
        self.assertEqual(violations, [])


class MutableDefaultTests(unittest.TestCase):
    def test_list_default_flagged(self) -> None:
        source = "def f(items=[]):\n    return items\n"
        violations = [v for v in lint_source(source) if v.rule_id == "LL203"]
        self.assertEqual(len(violations), 1)

    def test_dict_call_default_flagged(self) -> None:
        source = "def f(cfg=dict()):\n    return cfg\n"
        violations = [v for v in lint_source(source) if v.rule_id == "LL203"]
        self.assertEqual(len(violations), 1)

    def test_none_default_not_flagged(self) -> None:
        source = "def f(items=None):\n    return items\n"
        violations = [v for v in lint_source(source) if v.rule_id == "LL203"]
        self.assertEqual(violations, [])


class EqNoneTests(unittest.TestCase):
    def test_eq_none_flagged(self) -> None:
        violations = [v for v in lint_source("x == None\n") if v.rule_id == "LL204"]
        self.assertEqual(len(violations), 1)

    def test_is_none_not_flagged(self) -> None:
        violations = [v for v in lint_source("x is None\n") if v.rule_id == "LL204"]
        self.assertEqual(violations, [])

    def test_eq_number_not_flagged(self) -> None:
        violations = [v for v in lint_source("x == 3\n") if v.rule_id == "LL204"]
        self.assertEqual(violations, [])


class ShadowBuiltinTests(unittest.TestCase):
    def test_shadowing_function_flagged(self) -> None:
        source = "def sum(values):\n    return 0\n"
        violations = [v for v in lint_source(source) if v.rule_id == "LL205"]
        self.assertEqual(len(violations), 1)

    def test_plain_function_not_flagged(self) -> None:
        source = "def total(values):\n    return 0\n"
        violations = [v for v in lint_source(source) if v.rule_id == "LL205"]
        self.assertEqual(violations, [])


class StringConcatTests(unittest.TestCase):
    def test_str_plus_str_flagged(self) -> None:
        violations = [v for v in lint_source("s = 'a' + 'b'\n") if v.rule_id == "LL206"]
        self.assertEqual(len(violations), 1)

    def test_number_plus_number_not_flagged(self) -> None:
        violations = [v for v in lint_source("t = 1 + 2\n") if v.rule_id == "LL206"]
        self.assertEqual(violations, [])


class RegistryIntegrityTests(unittest.TestCase):
    def test_every_rule_has_why_and_hint(self) -> None:
        for rule in RULES:
            self.assertTrue(rule.why.strip(), rule.rule_id)
            self.assertTrue(rule.fix_hint.strip(), rule.rule_id)

    def test_rules_by_id_matches(self) -> None:
        self.assertEqual(len(RULES_BY_ID), len(RULES))


if __name__ == "__main__":
    unittest.main()
