# Results

## Environment

| Item | Value |
| --- | --- |
| OS | Windows (win32), bash (MSYS) |
| Python | 3.14.3 |
| Dependencies | zero (standard library only) |
| Working directory | repository root |

## Validation performed

| Check | Command | Result |
| --- | --- | --- |
| Unit + CLI tests | `PYTHONPATH=src python -m unittest discover -s tests` | **PASS** — `Ran 50 tests`, `OK` (exit 0) |
| Demo run | `PYTHONPATH=src python demo.py` | **PASS** — 3 artifacts written, `all reference solutions pass: True` |
| CLI smoke: rules | `PYTHONPATH=src python -m lexilint rules` | **PASS** — 8 rules with why/fix, exit 0 |
| CLI smoke: show | `PYTHONPATH=src python -m lexilint show C1` | **PASS** — brief + flawed source, exit 0 |
| CLI smoke: lint (violations) | `PYTHONPATH=src python -m lexilint lint examples/flaky.py` | **PASS** — findings + explanations, exit 1 |
| CLI smoke: grade pass | `PYTHONPATH=src python -m lexilint grade C1 examples/c1-solution.py` | **PASS** — `result: PASS`, exit 0 |
| CLI smoke: grade fail | grade flawed source | **PASS** (expected failure) — `result: NOT YET`, exit 1 |
| Lint/type check | n/a (stdlib-only project; runtime is the check) | N/A |

## Commands executed

```console
PYTHONPATH=src python -m unittest discover -s tests
PYTHONPATH=src python demo.py
PYTHONPATH=src python -m lexilint rules
PYTHONPATH=src python -m lexilint show C1
PYTHONPATH=src python -m lexilint lint examples/flaky.py
PYTHONPATH=src python -m lexilint grade C1 examples/c1-solution.py
```

## Observed result

- 50/50 tests pass, covering every rule, challenge integrity, grader
  pass/fail/anti-cheese paths, and the CLI.
- All four reference solutions grade `PASS` (rule coverage + behavior + no
  stdout leak); all four flawed sources grade `NOT YET`.
- Demo artifacts committed under `results/`.

## Generated artifacts

- `results/rules.md` — the explained rule catalog
- `results/flawed-reports.md` — lint reports of every flawed challenge source
- `results/reference-grades.json` — grading of every reference solution

## Known limitations

- Eight rules is a teaching slice, not full linter coverage.
- Behavior checks compare exact `repr`, so alternate-but-equivalent output
  formats fail; intentional for grading precision.
- The grader runs submissions in-process; it is a classroom tool, not a
  security sandbox.
