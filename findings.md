# Findings & Decisions

## Requirements

- Harden `pyspthin` as a Python library core for data engineering use.
- Preserve user input columns exactly.
- Use generated metadata columns with the `pyspthin_` prefix in every output dataframe.
- Remove `missing_policy` entirely.
- Fail invalid required data before graph construction or algorithm execution.
- Include row-level context in validation error messages: row, field, original value, and reason.
- Treat `record_id_col` as a source column only; never overwrite the source column.
- Accept breaking changes to output schema and default validation behavior.
- Keep CLI and batch configuration out of this implementation phase.
- Add GitHub Actions checks for `pytest`, coverage reporting, pytest-xdist, `ruff`, `mypy`, process-parallel smoke testing, package build, and `twine check` before committing and pushing.

## Research Findings

- Public API is exposed from `src/pyspthin/__init__.py` and currently imports `plot_thin`, `summary_thin`, `thin`, and `thin_many`.
- Root `main.py` is a runnable example, not an installable CLI. It hardcodes example data, parameters, and `main_example_plot.png`.
- `main.py` sets `matplotlib.use("Agg")` after importing `pyspthin`; importing `pyspthin` currently imports plotting code, so backend selection can happen too late.
- Current validation lives in `src/pyspthin/validate.py`; it coerces coordinate columns with `pd.to_numeric(..., errors="coerce")`.
- Current `missing_policy` defaults to `"drop"` and can silently drop required-value failures with a warning.
- Current `_attach_record_id` writes a `record_id` column into the dataframe, which can overwrite a user-provided `record_id` column.
- Current replicate restoration writes `replicate_id`, `replicate_rank`, `retained_count`, and `species`, which can overwrite user columns of the same names.
- `thin_many(...)` currently forces child runs to use `record_id_col="record_id"`.
- Local unittest suite passed 14 tests with `PYTHONPATH=src python3 -m unittest discover -s tests -p 'test*.py'`.
- Local `pytest`, `coverage`, `ruff`, and `mypy` were not installed.
- CI currently installs dev dependencies and runs `python -m pytest -q`, but does not run coverage, ruff, mypy, or build verification.
- Phase 3 re-read confirmed `ThinConfig` still has `missing_policy`, `validate.py` still drops missing required values by default, and `tests/unit/test_validation.py` currently only checks broad `ValueError` cases without row-level diagnostics.
- Phase 4 re-read confirmed `api.py` still reads retained IDs from `record_id`, `restore.py` still writes unprefixed metadata columns, and `thin_many(...)` still forces child runs to `record_id_col="record_id"`.
- Phase 5 re-read found docs still describing stable internal `record_id` instead of `pyspthin_record_id`, and property tests did not yet assert the generated-column namespace.

## Technical Decisions

| Decision | Rationale |
|----------|-----------|
| Add custom validation exception | A single exception can present multiple row-level diagnostics cleanly. |
| Keep structured error records internal for now | User requested row-level messages, not a public machine-readable error API. |
| Use `pyspthin_record_id` for retained IDs | Makes generated identity stable while preserving user columns. |
| Use `pyspthin_replicate_id`, `pyspthin_replicate_rank`, `pyspthin_retained_count`, `pyspthin_species` | Prevents metadata from overwriting original data columns. |
| Remove `missing_policy` from docs and config | Invalid data should not be dropped implicitly in this phase. |
| Keep R reference regression count-based | R compatibility test should not depend on Python metadata column names. |
| Use TDD for implementation phases | Behavior changes must be protected by tests that fail before production code changes. |
| Add `py.typed` and `pandas-stubs` for mypy | The configured `mypy` command could not type-check the installed package without a PEP 561 marker and pandas stubs. |
| Apply project-wide ruff formatting | Running `ruff check .` for the first time exposed global import formatting and line-length issues; formatting the whole checked tree makes the configured lint command meaningful. |
| Add `pytest-xdist` to dev dependencies | The user explicitly requested parallel pytest execution, so the tool should be reproducible from the dev extra. |
| Mirror local verification in GitHub Actions | The user requested that pytest, ruff, and mypy run after pushing to the repository; the workflow should also include the coverage, xdist, process-parallel, build, and twine checks used locally. |

## Issues Encountered

| Issue | Resolution |
|-------|------------|
| Current environment lacks pytest/coverage/ruff/mypy | Use unittest for available verification and record tooling limitation. |
| Sandbox prevents process-pool validation | Do not claim process-based parallelism is verified locally; rely on serial/threaded behavior here. |
| Bare `python3` may resolve to system Python from some directories | Use explicit conda Python when verifying dependency-dependent behavior. |
| Previous planning flow started with `writing-plans`, but user requested `planning-with-files` | Switch to root-level persistent planning files and continue from there. |
| Initial `ruff check .` failed with 45 style issues | Ran `ruff check . --fix`, `ruff format .`, and small manual line-wrap/stacklevel fixes. |
| Initial `mypy` failed before package checking due missing `py.typed` | Added `src/pyspthin/py.typed` and package-data config. |
| `mypy` then found NumPy, pandas, and wrapper return-type issues | Added pandas stubs, NDArray type aliases/casts, return annotations, and a targeted pandas `isna` overload ignore. |

## Resources

- Design spec: `docs/superpowers/specs/2026-04-25-pyspthin-validation-core-design.md`
- API: `src/pyspthin/api.py`
- Config: `src/pyspthin/config.py`
- Validation: `src/pyspthin/validate.py`
- Models: `src/pyspthin/models.py`
- Restore helper: `src/pyspthin/io/restore.py`
- Unit tests: `tests/unit/test_api.py`, `tests/unit/test_validation.py`
- Property tests: `tests/property/test_invariants.py`
- Regression tests: `tests/regression/test_r_reference.py`
- Failure-mode tests: `tests/failure/test_failure_modes.py`
- Docs: `README.md`, `wiki/usage.md`, `wiki/compatibility.md`, `wiki/development.md`
- CI workflow: `.github/workflows/tests.yml`

## Visual/Browser Findings

- No browser or visual inspection was used for this task.

---

*Update this file after every 2 view/browser/search operations or any meaningful discovery.*
