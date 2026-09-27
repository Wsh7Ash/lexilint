# Usage

All commands work via `PYTHONPATH=src python -m lexilint ...` from a checkout,
or plain `lexilint ...` after `pip install .`.

## Explore the curriculum

```console
$ lexilint rules                # table of every rule with why + fix
$ lexilint rules --format json  # machine-readable catalog
$ lexilint show C1              # brief + flawed source + target rules
```

## Lint with explanations

```console
$ lexilint lint path/to/file.py
```

Exit codes: `0` clean, `1` violations found, `2` input/syntax error.

## The practice loop

1. `lexilint show C2` — read the brief and the flawed source.
2. Copy the flawed source into a working file and fix it in your editor.
3. `lexilint grade C2 work.py` — iterate until you see `result: PASS`.

Grading is strict on purpose:

- every target rule must actually be fixed,
- the file must lint clean overall,
- behavior cases must produce exactly the expected results,
- the code must run silently (no `print` leaks).

## JSON grading for courseware

```console
$ lexilint grade C2 work.py --json
```

Returns a machine-readable report with `passed`, `rules_complete`, `fixed`,
`remaining`, `behavior`, and `stdout_leak`. Exit code `0` only on a pass.

## Library API

```python
from lexilint import get_challenge, grade_submission, lint_source

violations = lint_source("x == None\n")
report = grade_submission(get_challenge("C3"), student_code)
```

Build custom challenge packs by constructing `Challenge` and `BehaviorCase`
objects and grading them with the same engine.

## Regenerating demo artifacts

```console
$ PYTHONPATH=src python demo.py
```

Writes `results/rules.md`, `results/flawed-reports.md`, and
`results/reference-grades.json`.
