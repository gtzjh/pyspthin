# pyspthin Compatibility Notes

`pyspthin` is a semantic reimplementation of `spThin`, not a line-by-line translation.

What is intentionally aligned:

- conflict threshold meaning
- greedy removal rule
- random tie-breaking per replicate
- replicate sorting by retained count
- summary-level interpretation of replicate counts

What is intentionally improved:

- no dense `N x N` distance matrix in production code
- stable `pyspthin_record_id` support for row restoration without overwriting user columns
- structured outputs instead of untyped lists and side-effect-only workflows
- explicit `rep` and `species` parallel modes in Python

Breaking Python-side schema change:

- generated output columns now use the `pyspthin_` prefix, for example `pyspthin_record_id` and `pyspthin_replicate_id`
- invalid required data fails before thinning; implicit missing-value dropping and `missing_policy` are no longer supported

The repository includes [run_r_reference.R](https://github.com/gtzjh/pyspthin/blob/main/spThin-R/scripts/run_r_reference.R) and [test_r_reference.py](https://github.com/gtzjh/pyspthin/blob/main/tests/regression/test_r_reference.py) to keep a small R reference path in the workflow.
