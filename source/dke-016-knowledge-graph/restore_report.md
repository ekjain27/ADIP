# Restore Report

## Restore Summary
- Restored root: C:\Users\BAPS\Documents\Codex\2026-06-28\files-mentioned-by-the-user-003\outputs\dke-016-knowledge-graph
- Source used: C:\Users\BAPS\Documents\Codex\2026-06-29\c\outputs\dke-016-knowledge-graph
- Python files restored: 451
- Source Python files under src/: 402
- Top-level test files restored: 49
- Pytest collection: 606 tests collected
- Pytest regression: 606 passed
- src/dke/commercial_release.zip present: False

## Restored Module Families
- Documentation files: 27
- Validation files: 26
- Patent files: 21
- Research paper files: 33
- Commercial release files: 14

## Hygiene
- .gitignore updated with Python, test cache, type checker, virtual environment, build, and log rules.
- Cache artifacts were removed after validation.
- Final ZIP excludes .git, caches, virtual environments, node_modules, dist, build, and compiled Python files.

## Validation Commands
- python -m pytest --collect-only -> 606 tests collected
- python -m pytest -> 606 passed
