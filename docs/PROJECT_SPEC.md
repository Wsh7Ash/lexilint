# Project Spec — lexilint

- **Name:** lexilint
- **Category:** learner-tool
- **Target user:** Python beginners and coding instructors who want linter
  literacy, not just linter output.
- **Problem:** Linters report violations without teaching the reasoning
  behind them; learners silence warnings with `# noqa` instead of
  understanding them, and have no safe gym to practice real fixes.
- **Solution:** A zero-dependency CLI + library where every rule carries an
  explanation and a fix hint, and graded challenges verify that fixes
  preserve behavior instead of deleting functionality.
- **Core workflow:** show challenge → fix flawed source in an editor →
  grade submission → iterate to PASS.
- **Must-have features:**
  - rule registry with `why` + `fix` text per rule (8 rules)
  - `lint` command with explained findings and meaningful exit codes
  - 4 challenges whose flawed sources trigger their target rules
  - grader requiring rule coverage + behavior cases + no stdout leak
  - JSON grading output for courseware integration
- **Nice-to-have features:** progress tracking, custom challenge packs,
  diff-against-reference mode (roadmap).
- **Stack:** Python 3.11+, standard library only.
- **Test strategy:** unit tests per rule, challenge integrity tests
  (flawed triggers targets, reference clean), grader pass/fail/cheese
  paths, full CLI exit-code coverage.
- **Demo/result strategy:** `demo.py` regenerates `results/` artifacts:
  rule catalog, flawed-source reports, reference-solution grades.
- **Safety considerations:** grader executes submitted code locally; the
  README and SECURITY notes say explicitly to only grade your own code.
  No network access anywhere.
- **Definition of done:** all tests pass, demo artifacts generated,
  README commands verified, secret scan clean, published to GitHub.

## Uniqueness fingerprint

`learner-tool|python-beginner|linter-warnings-silenced-not-understood|explained-rules-plus-behavior-gated-challenges|graded-fix-report`

No prior project in `factory_state.json` targets lint-rule pedagogy or a
behavior-gated fixing gym.
