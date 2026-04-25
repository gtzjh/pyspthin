# pyspthin

`pyspthin` is a Python reimplementation of `spThin` that keeps the original greedy thinning semantics while using a sparse conflict graph instead of a dense `N x N` distance matrix.

## What It Does

- validates tabular occurrence input with Pydantic
- works on longitude/latitude coordinates in kilometers
- runs repeated spatial thinning replicates with reproducible random seeds
- preserves original rows and extra columns without overwriting user columns
- writes generated metadata columns with a `pyspthin_` prefix, including `pyspthin_record_id`
- exposes `thin(...)`, `thin_many(...)`, `summary_thin(...)`, and `plot_thin(...)`

## Repository Layout

- `src/pyspthin/`: Python package
- `main.py`: runnable example script
- `tests/`: unit, regression, property, and failure-mode tests
- `wiki/`: source Markdown pages synced to the GitHub Wiki
- `spThin-R/`: archived original R-package-related material and R reference tooling

## Quick Start

Install the package in editable mode and run the example:

```bash
pip install -e .
PYTHONPATH=src python3 main.py
```

You can also call the package directly:

```python
import pandas as pd
from pyspthin import summary_thin, thin

data = pd.DataFrame(
    [
        {"SPEC": "sp1", "LONG": 0.00, "LAT": 0.00, "OBS_ID": "obs-1"},
        {"SPEC": "sp1", "LONG": 0.00, "LAT": 0.05, "OBS_ID": "obs-2"},
        {"SPEC": "sp1", "LONG": 0.00, "LAT": 0.10, "OBS_ID": "obs-3"},
        {"SPEC": "sp1", "LONG": 1.00, "LAT": 1.00, "OBS_ID": "obs-4"},
    ]
)

result = thin(data, thin_par=8.0, reps=4, seed=123)
print(summary_thin(result))
print(result.best_dataframe)
```

Input validation is strict: required coordinates, species values, and explicit record IDs must be valid before the thinning algorithm runs. If `record_id_col` is supplied, it is used only as the source for `pyspthin_record_id`; the source column is preserved unchanged.

## Notes

- The archived R package content is now under `spThin-R/`.
- The R reference script used by regression tests is at `spThin-R/scripts/run_r_reference.R`.
- Usage, development, compatibility, and release notes are maintained in `wiki/` and synced to the GitHub Wiki.
