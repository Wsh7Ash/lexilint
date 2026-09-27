"""End-to-end CLI tests exercising exit codes and output formats."""

from __future__ import annotations

import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout

from lexilint.cli import main
from lexilint.exercises import CHALLENGES


def _run(argv: list[str]) -> tuple[int, str]:
    buffer = io.StringIO()
    with redirect_stdout(buffer), redirect_stderr(buffer):
        code = main(argv)
    return code, buffer.getvalue()


class CliRulesTests(unittest.TestCase):
    def test_rules_table(self) -> None:
        code, out = _run(["rules"])
        self.assertEqual(code, 0)
        self.assertIn("LL101", out)
        self.assertIn("LL206", out)
        self.assertIn("fix:", out)

    def test_rules_json(self) -> None:
        code, out = _run(["rules", "--format", "json"])
        self.assertEqual(code, 0)
        payload = json.loads(out)
        self.assertEqual(len(payload), 8)


class CliShowTests(unittest.TestCase):
    def test_show_known_challenge(self) -> None:
        code, out = _run(["show", "C1"])
        self.assertEqual(code, 0)
        self.assertIn("The Chatty Ingestor", out)
        self.assertIn("LL201", out)
        self.assertIn("flawed source", out)

    def test_show_unknown_challenge(self) -> None:
        code, out = _run(["show", "ZZ"])
        self.assertEqual(code, 2)
        self.assertIn("unknown challenge", out)


class CliLintTests(unittest.TestCase):
    def test_lint_clean_file(self) -> None:
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as handle:
            handle.write("value = 1\n")
            path = handle.name
        try:
            code, out = _run(["lint", path])
            self.assertEqual(code, 0)
            self.assertIn("clean", out)
        finally:
            os.unlink(path)

    def test_lint_violations_exit_1(self) -> None:
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as handle:
            handle.write("x == None\n")
            path = handle.name
        try:
            code, out = _run(["lint", path])
            self.assertEqual(code, 1)
            self.assertIn("LL204", out)
            self.assertIn("why:", out)
        finally:
            os.unlink(path)

    def test_lint_syntax_error_exit_2(self) -> None:
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as handle:
            handle.write("def broken(:\n")
            path = handle.name
        try:
            code, out = _run(["lint", path])
            self.assertEqual(code, 2)
        finally:
            os.unlink(path)

    def test_lint_missing_file_exit_2(self) -> None:
        code, out = _run(["lint", "no-such-file.py"])
        self.assertEqual(code, 2)
        self.assertIn("cannot read", out)


class CliGradeTests(unittest.TestCase):
    def _write(self, text: str) -> str:
        handle = tempfile.NamedTemporaryFile("w", suffix=".py", delete=False)
        handle.write(text)
        handle.close()
        return handle.name

    def test_grade_reference_passes(self) -> None:
        challenge = CHALLENGES[0]
        path = self._write(challenge.reference)
        try:
            code, out = _run(["grade", challenge.challenge_id, path])
            self.assertEqual(code, 0)
            self.assertIn("PASS", out)
        finally:
            os.unlink(path)

    def test_grade_flawed_fails(self) -> None:
        challenge = CHALLENGES[0]
        path = self._write(challenge.flawed)
        try:
            code, out = _run(["grade", challenge.challenge_id, path])
            self.assertEqual(code, 1)
            self.assertIn("NOT YET", out)
        finally:
            os.unlink(path)

    def test_grade_json_output(self) -> None:
        challenge = CHALLENGES[0]
        path = self._write(challenge.reference)
        try:
            code, out = _run(["grade", challenge.challenge_id, path, "--json"])
            self.assertEqual(code, 0)
            payload = json.loads(out)
            self.assertTrue(payload["passed"])
            self.assertTrue(payload["rules_complete"])
        finally:
            os.unlink(path)

    def test_grade_unknown_challenge(self) -> None:
        path = self._write("x = 1\n")
        try:
            code, out = _run(["grade", "ZZ", path])
            self.assertEqual(code, 2)
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
