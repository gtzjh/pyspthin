# Task Plan: pyspthin Validation Core Hardening

## Goal

Harden `pyspthin` as a robust Python library core by enforcing strict row-level validation, preserving user columns, and moving all generated metadata columns to the `pyspthin_` namespace.

## Current Phase

Phase 8

## Phases

### Phase 1: Requirements & Discovery

- [x] Inspect current project layout, public API, example entry point, validation code, result models, graph construction, and tests.
- [x] Run available tests with the local environment.
- [x] Identify core risks for data engineering robustness.
- [x] Brainstorm and confirm user requirements.
- [x] Write and commit the design spec.
- **Status:** complete

### Phase 2: File-Based Planning & Recovery

- [x] Activate `planning-with-files` workflow.
- [x] Check for previous session catchup context.
- [x] Create `task_plan.md`, `findings.md`, and `progress.md`.
- [x] Re-read the committed design spec before implementation.
- [x] Confirm implementation task breakdown from the file plan.
- **Status:** complete

### Phase 3: Validation Model Implementation

- [x] Add failing tests for strict validation and row-level diagnostics.
- [x] Introduce validation error records and `PyspthinValidationError`.
- [x] Remove `missing_policy` from configuration and validation flow.
- [x] Validate numeric coordinates, coordinate ranges, non-empty species, explicit record IDs, and non-negative seed before graph construction.
- [x] Run targeted validation tests.
- **Status:** complete

### Phase 4: Metadata Column Namespace Implementation

- [x] Add failing tests proving user columns are never overwritten.
- [x] Generate `pyspthin_record_id` instead of `record_id`.
- [x] Restore replicate dataframes with `pyspthin_replicate_id`, `pyspthin_replicate_rank`, `pyspthin_retained_count`, and `pyspthin_species`.
- [x] Update `ThinResult.record_id_col` and `ReplicateResult.retained_record_ids`.
- [x] Update `thin_many(...)` child-run handling to use the new internal column name.
- [x] Run targeted API tests.
- **Status:** complete

### Phase 5: Regression, Property Tests, and Documentation

- [x] Update regression and property tests for the new metadata schema.
- [x] Add tests for `thin_many(..., parallel_mode="rep")` and `"species"` output consistency.
- [x] Update README and wiki docs to document strict validation, removed `missing_policy`, and `pyspthin_*` columns.
- [x] Run the full available test suite.
- **Status:** complete

### Phase 6: Final Verification & Delivery

- [x] Re-read `task_plan.md`, `findings.md`, and `progress.md`.
- [x] Run final verification commands available in this environment.
- [x] Record test results and remaining environment limitations in `progress.md`.
- [x] Summarize changed files, behavior changes, and verification results for the user.
- **Status:** complete

### Phase 7: Authorized Pytest And Process Parallel Verification

- [x] Install project dev test tooling now that network and filesystem restrictions are lifted.
- [x] Run `pytest` with the installed tooling.
- [x] Run coverage if available.
- [x] Run lint/type checks if available.
- [x] Run explicit process-parallel checks and confirm no fallback warning occurs.
- [x] Record results and any remaining issues.
- **Status:** complete

### Phase 8: CI Workflow, Commit, And Push

- [x] Add GitHub Actions steps for `ruff`, `mypy`, `pytest`, coverage, pytest-xdist, process-parallel smoke testing, build, and `twine check`.
- [x] Run fresh local verification equivalent to the workflow.
- [x] Record final verification results.
- [ ] Commit all intended project changes with a clear message.
- [ ] Push the commit to the configured remote branch.
- **Status:** local verification complete; commit/push are the next shell actions and cannot be recorded inside the same committed snapshot after they happen.

## Key Questions

1. Should generated metadata columns ever use legacy names such as `record_id` or `species`? Answer: No, always use `pyspthin_*`.
2. Should invalid rows ever be dropped by default? Answer: No, `missing_policy` is removed and invalid required data fails.
3. Should this be backward compatible? Answer: No, this is a breaking upgrade.
4. Should validation errors expose row-level context? Answer: Yes, message must include row, field, original value, and reason.
5. Is CLI or batch configuration part of this implementation? Answer: No, out of scope.

## Decisions Made

| Decision | Rationale |
|----------|-----------|
| Use `planning-with-files` for ongoing work | User explicitly requested this workflow after brainstorming. |
| Implement the confirmed design as a breaking upgrade | User selected direct breaking upgrade instead of compatibility modes. |
| Remove `missing_policy` | User explicitly chose removal, not a default-value change. |
| Always use `pyspthin_*` generated columns | Prevents overwriting user data and gives a stable generated-column namespace. |
| Keep function names `thin`, `thin_many`, `summary_thin`, and `plot_thin` | Hardens library behavior without expanding public API surface. |
| Keep CLI, coverage gates, and quality report files out of scope | CLI and enforced coverage thresholds remain deferred; GitHub Actions quality gates were later requested by the user in Phase 8. |
| Add authorized pytest/process-parallel verification as Phase 7 | User explicitly granted unrestricted execution and asked for pytest and parallel testing. |
| Add CI workflow quality gates as Phase 8 | User explicitly requested adding pytest, ruff, mypy, and related checks to workflow before commit/push. |

## Errors Encountered

| Error | Attempt | Resolution |
|-------|---------|------------|
| `pytest` was not installed in the local conda environment | 1 | Used `PYTHONPATH=src python3 -m unittest discover -s tests -p 'test*.py'` to run available tests. |
| Process-based parallel execution failed in sandbox with `[Errno 1] Operation not permitted` | 1 | Test run fell back to threaded execution; record limitation instead of claiming process pool coverage. |
| Running `main.py` from `/tmp` with bare `python3` used system Python 3.9 and missed `matplotlib` | 1 | Re-ran with `/Users/jarviski/miniconda3/bin/python3` and explicit `PYTHONPATH`. |
| Installing dev dependencies with escalated `pip install -e ".[dev]"` was rejected due approval service 503 | 1 | Do not retry the same install path without explicit approval; proceed with installed tooling only. |

## Notes

- Committed design spec: `docs/superpowers/specs/2026-04-25-pyspthin-validation-core-design.md`.
- Spec commit: `f8317f8 Document validation core hardening design`.
- Re-read this file before each implementation phase.
- Update `progress.md` after each phase and every verification run.
- Update `findings.md` after discoveries or after every two view/search/read operations.
