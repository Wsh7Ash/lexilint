# Changelog

All notable changes to this project are documented here.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [1.0.0] — 2026-09-27

### Added

- Rule registry with 8 explained rules (LL101–LL206): long lines, TODO
  markers, `print` in library code, bare `except`, mutable defaults,
  `== None`, shadowed builtins, string concatenation.
- `lint` command with per-violation `why`/`fix` explanations and exit
  codes 0/1/2.
- 4 graded challenges (C1–C4) with briefs, flawed sources, reference
  solutions, and executable behavior cases.
- Grader enforcing rule coverage + behavior preservation + stdout-leak
  detection, with text and JSON output.
- `rules` and `show` exploration commands; JSON rules catalog.
- 50 tests covering rules, challenge integrity, grader paths, and CLI.
- Demo script generating `results/` artifacts.
