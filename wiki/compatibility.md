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
- stable `record_id` support for row restoration
- structured outputs instead of untyped lists and side-effect-only workflows
- explicit `rep` and `species` parallel modes in Python

The repository includes [run_r_reference.R](https://github.com/gtzjh/pyspthin/blob/main/spThin-R/scripts/run_r_reference.R) and [test_r_reference.py](https://github.com/gtzjh/pyspthin/blob/main/tests/regression/test_r_reference.py) to keep a small R reference path in the workflow.
