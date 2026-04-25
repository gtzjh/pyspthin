# Usage

```python
import pandas as pd
from pyspthin import plot_thin, summary_thin, thin, thin_many

data = pd.read_csv("occurrences.csv")

result = thin(
    data,
    thin_par=10.0,
    reps=20,
    lat_col="LAT",
    long_col="LONG",
    species_col="SPEC",
    seed=123,
)

summary = summary_thin(result)
figure = plot_thin(result)
best_rows = result.best_dataframe
```

Generated columns in `best_rows` use the `pyspthin_` prefix:

- `pyspthin_record_id`
- `pyspthin_replicate_id`
- `pyspthin_replicate_rank`
- `pyspthin_retained_count`
- `pyspthin_species`

For multi-species input:

```python
many = thin_many(
    data,
    thin_par=10.0,
    reps=20,
    lat_col="LAT",
    long_col="LONG",
    species_col="SPEC",
    parallel_mode="species",
    n_jobs=4,
    seed=123,
)
```

Important behavior:

- `thin(...)` accepts exactly one species
- `thin_many(...)` is the multi-species entry point
- validation is strict; invalid required coordinates, species values, or explicit record IDs fail before thinning starts
- `missing_policy` is not supported
- if `record_id_col` is supplied, it is used only as the source for `pyspthin_record_id`
- if no explicit `record_id_col` is supplied, `pyspthin` uses a unique `OBS_ID`, `obs_id`, `ID`, or `id` column when available, otherwise it generates stable `record-000000` values in `pyspthin_record_id`
