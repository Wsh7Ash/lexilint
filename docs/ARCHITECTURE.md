# Architecture

## Layers

```text
            ┌────────────┐
            │   cli.py   │  argparse, exit codes, rendering
            └─────┬──────┘
      ┌───────────┼───────────┐
      ▼           ▼           ▼
┌──────────┐ ┌─────────┐ ┌───────────┐
│ engine   │ │ grader  │ │ exercises │
│ (lint)   │ │ (grade) │ │ (library) │
└────┬─────┘ └────┬────┘ └─────┬─────┘
     ▼            ▼            ▼
┌────────────────────────────────────┐
│              rules.py              │
│   Rule registry: checks + why/fix  │
└────────────────────────────────────┘
```

- **rules.py** — the single source of truth. Each `Rule` bundles a check
  function (`ast.Module, lines -> list[Violation]`) with learner-facing
  `why` and `fix_hint` text. Adding a rule is one `Rule(...)` entry plus a
  check function; the CLI, engine, and docs pick it up automatically.
- **engine.py** — `ast.parse` the source, run every rule, sort findings by
  (line, col, rule id). Raises `LintSyntaxError` on unparseable input so the
  CLI can exit 2 with a precise message.
- **exercises.py** — frozen dataclass challenges. Integrity invariant
  (enforced by tests): the flawed source must trigger every target rule, and
  the reference must lint clean *and* pass its own behavior cases.
- **grader.py** — lints the submission, diffs rule coverage against the
  flawed baseline, executes behavior cases under `redirect_stdout`, and
  treats any captured stdout as a leak. Syntax errors are reported as a
  pseudo-violation (`SYNTAX`) instead of raising.

## Grading model

```text
baseline  = lint(challenge.flawed)          # rules the learner must fix
remaining = lint(submission)                # still violating
fixed     = baseline_ids - remaining_ids    # only clean counts
passed    = targets ⊆ fixed
            and all(behavior cases ok)
            and remaining == []
            and stdout leak == none
```

The behavior gate exists because lint rules can be "satisfied" by deletion:
removing the buggy function silences every rule. Behavior cases make the
grader refuse that path.

## Exit codes

| Code | Meaning |
| ---- | ------- |
| 0 | success (clean lint, passed grade, info command) |
| 1 | findings present / grade not passed |
| 2 | usage or input error (bad path, syntax error, unknown challenge) |

## Data flow of a grade run

```text
submission file ──▶ grader ──▶ engine.lint ──▶ Violation[]
                     │
                     ├─▶ behavior eval (exec/eval under redirect_stdout)
                     ├─▶ stdout-leak capture
                     └─▶ GradeReport ──▶ cli renders text or JSON
```
