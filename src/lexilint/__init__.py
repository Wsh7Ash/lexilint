"""lexilint: learn linting by fixing deliberately flawed code."""

from .engine import LintSyntaxError, lint_file, lint_source
from .exercises import CHALLENGES, Challenge, get_challenge
from .grader import GradeReport, grade_submission
from .rules import MAX_LINE_LENGTH, RULES, RULES_BY_ID, Rule, Violation

__version__ = "1.0.0"

__all__ = [
    "LintSyntaxError",
    "lint_file",
    "lint_source",
    "CHALLENGES",
    "Challenge",
    "get_challenge",
    "GradeReport",
    "grade_submission",
    "MAX_LINE_LENGTH",
    "RULES",
    "RULES_BY_ID",
    "Rule",
    "Violation",
    "__version__",
]
