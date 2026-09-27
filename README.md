# lexilint

**Learn linting by fixing deliberately flawed Python** — a terminal playground
where every rule comes with an explanation of *why* it exists, every challenge
is graded on rule coverage *and* preserved behavior, and deleting the buggy
code counts as failing.

## The problem

Beginners run a linter, see `E722 bare except`, google "how to make E722 go
away", and add `# noqa`. The warning disappears; the bug stays. What's missing
is the *reasoning layer*: why the rule exists, what the fix looks like, and a
safe place to practice it. Existing linters report; they do not teach.

## Key features

- **8 explained rules (LL101–LL206)** — each carries a `why` (the reasoning)
  and a `fix` hint (the concrete remedy), shown on every violation.
- **4 graded challenges** — deliberately flawed source, a mission brief, and
  target rules; solutions are graded on rule coverage, not on looks.
- **Behavior gate** — every challenge ships executable behavior cases. A
  "fix" that deletes functionality fails grading, so you cannot cheese the
  linter by gutting the code.
- **stdout-leak detector** — graded submissions must run silently; `print`
  debugging your way to "clean" fails too.
- **CLI + library** — use `lexilint` from a terminal or embed the engine,
  grader, and challenge library in your own courseware.
- **Zero dependencies** — Python 3.11+ standard library only.

## Example session

```console
$ lexilint show C1
C1 — The Chatty Ingestor

This loader works, but it talks directly to stdout and hides real
errors. Make it silent, catch only what it can handle, and stop
building output with string concatenation.

Rules to satisfy: LL201, LL202, LL206

--- flawed source ---
def load_numbers(values):
    total = 0
    seen = []
    ...

$ lexilint lint my_buggy.py
my_buggy.py:7:8: LL202 bare except: catches KeyboardInterrupt/SystemExit and hides bugs
    why: A bare 'except:' also catches KeyboardInterrupt and SystemExit, and hides
    real bugs like NameError, making failures invisible.
    fix: Catch the specific exception you can handle, e.g. 'except ValueError:'.

$ lexilint grade C1 my_fix.py
challenge C1:
  LL201: fixed
  LL202: fixed
  LL206: fixed
  behavior [ok] load_numbers(["3", "x", "5"]) -> [3, 5]
result: PASS
```

## Architecture summary

Four small layers, dependency-free:

- `rules.py` — rule registry: AST/pattern checks + per-rule `why`/`fix` text
- `engine.py` — parses source, runs rules, sorts violations
- `exercises.py` — challenge library (flawed source, reference, behavior cases)
- `grader.py` — coverage + behavior + stdout-leak verification
- `cli.py` — `rules` / `show` / `lint` / `grade` subcommands

See `docs/ARCHITECTURE.md` for the full map.

## Requirements

- Python **3.11+** (developed and tested on 3.14)
- Nothing else — no pip installs, no network access.

## Installation

```console
$ git clone https://github.com/Wsh7Ash/lexilint
$ cd lexilint
# run straight from the checkout:
$ PYTHONPATH=src python -m lexilint --help
# or install:
$ pip install .
```

## Quick start

```console
$ lexilint rules                 # every rule, with why + fix
$ lexilint show C1               # read the mission brief
$ lexilint show C1 > c1.py       # ...then edit the flawed part into shape
$ lexilint grade C1 c1.py        # submit when you think you are done
```

## Usage examples

Lint any Python file with explanations attached to each finding:

```console
$ lexilint lint examples/flaky.py
```

Machine-readable grading for courseware integration:

```console
$ lexilint grade C2 my_basket.py --json
{
  "challenge": "C2",
  "passed": true,
  "rules_complete": true,
  ...
}
```

Library use — grade a string in-process:

```python
from lexilint import get_challenge, grade_submission

challenge = get_challenge("C3")
report = grade_submission(challenge, student_source)
print(report.passed, report.violations_fixed)
```

## Configuration

lexilint is intentionally configuration-free. The rule set is the curriculum:
fixed, ordered, and explained. Custom challenge packs can be built on the
library API (`Challenge`, `BehaviorCase`, `grade_submission`).

## Testing

```console
$ PYTHONPATH=src python -m unittest discover -s tests -v
```

50 tests cover every rule, every challenge's integrity (flawed source triggers
its targets; reference lints clean), grader pass/fail/cheese paths, and the
full CLI surface including exit codes.

## Project structure

```text
lexilint/
├─ src/lexilint/
│  ├─ rules.py        # rule registry + explanations
│  ├─ engine.py       # parse + run + sort
│  ├─ exercises.py    # challenge library
│  ├─ grader.py       # grading engine
│  ├─ cli.py          # argparse CLI
│  └─ __main__.py
├─ tests/             # 50 unit/CLI tests
├─ examples/          # sample files for `lint`
├─ results/           # generated demo artifacts
├─ docs/              # architecture, usage, spec
├─ demo.py            # regenerates results/
└─ pyproject.toml
```

## Limitations

- Eight rules is a curriculum slice, not pylint coverage; the rule engine is
  the point, the rule count is not.
- Behavior cases compare exact `repr` output, so acceptable-but-differently
  formatted return values fail; by design — precision is the lesson.
- AST rules are line-based for LL101/LL102; exotic line-continuations may
  shift reported positions.
- The grader executes submitted code in-process (sandboxed only by
  `redirect_stdout`); it is a classroom tool, not a sandbox.

## Roadmap

- More challenges per rule tier (basics → idioms → design smells)
- `lexilint progress` with a local JSON progress log
- Optional diff mode showing the reference side-by-side after grading
- Pluggable custom challenge packs loaded from a directory

## Security notes

The `grade` command executes the submitted file's code on your machine — that
is the point of a behavior gate. Only grade your own code; do not grade
strangers' submissions on shared infrastructure. No network access anywhere.

## License

MIT — see `LICENSE`.
