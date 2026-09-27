# Contributing

Thanks for considering a contribution to lexilint.

## Ground rules

- Python 3.11+ standard library only — no runtime dependencies.
- Every new rule needs: an id in the `LLxxx` space, a check function, a
  `why`, a `fix_hint`, and unit tests including a clean-counterexample.
- Every new challenge needs: a unique id, a brief, target rules that the
  flawed source actually triggers, a reference solution that lints clean
  and passes its own behavior cases (the test suite enforces this).
- Keep the grader strict: no loosening of the behavior gate or the
  stdout-leak check without a strong rationale.

## Workflow

1. Fork/branch.
2. `PYTHONPATH=src python -m unittest discover -s tests` must stay green.
3. Update `docs/` and `CHANGELOG.md` for user-visible changes.
4. Open a pull request describing the motivation.

## Code style

- Small modules, typed signatures, dataclasses over dicts.
- Explanatory text (`why`/`fix_hint`) is part of the product: write it for
  a learner, not for a linter maintainer.
