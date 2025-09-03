Title: Clean CI, fix tests, remove duplicates, add utcnow guard

Summary
- Consolidates CI into a single workflow that runs Ruff, pytest, and the email guard on PRs and pushes.
- Converts three tests to use assertions (eliminates PyTestReturnNotNone warnings).
- Removes unused duplicate postprocess modules under `src/postprocess/` in favor of canonical `bulletin_builder.postprocess`.
- Adds a pre-commit hook that blocks `datetime.utcnow()` usage across `src/`, `scripts/`, and `tools/`.

Changes
- CI: `.github/workflows/ci.yml` unified; uses `actions/setup-python@v5` with Python 3.11, installs deps, runs `ruff check .`, `pytest -q`, then email guard.
- Tests (assert conversions):
  - `tests/test_https_functionality.py`
  - `tests/test_minimal_gui.py`
  - `tests/test_step_by_step.py`
- Postprocess cleanup:
  - Deleted: `src/postprocess/email_postprocess.py`
  - Deleted: `src/postprocess/email_postprocess_plus.py`
- Pre-commit:
  - Added: `tools/check_utcnow.py`
  - Updated: `.pre-commit-config.yaml` to add local hook `no-utcnow` (runs on commit); existing pytest hook remains on pre-push.
- UTC fixups already applied earlier:
  - `src/bulletin_builder/actions_log.py`: use `datetime.datetime.now(datetime.UTC)`
  - `src/bulletin_builder/event_feed.py`: use `datetime.now(datetime.UTC)`

Rationale
- Avoid CI duplication/override and ensure consistent lint+test gates.
- Assertion-based tests remove warnings and clarify expected outcomes.
- Removing dead duplicate modules prevents drift; canonical imports already point to `bulletin_builder.postprocess`.
- Pre-commit guard prevents timezone regressions from `utcnow()` usage.

Validation
- Local run: `68 passed` in ~5–8s, zero warnings.
- Verified no imports reference removed modules (`src/postprocess/*`).
- Hook correctly detects forbidden usage; currently clean.

Notes
- `src/postprocess` directory was removed after deleting its files.
- GUI-related smoke tests remain non-interactive and pass locally.

Rollout
- Merge normally. CI should run Ruff, tests, and email guard.
- Developers should run `pre-commit install` to enable hooks locally.
