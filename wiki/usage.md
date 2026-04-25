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
- if no explicit `record_id_col` is supplied, `pyspthin` generates a stable internal `record_id`

