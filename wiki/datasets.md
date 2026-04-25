# Test And Benchmark Datasets

Current fixture datasets:

- [tests/fixtures/single_species.csv](https://github.com/gtzjh/pyspthin/blob/main/tests/fixtures/single_species.csv)
  Deterministic single-species chain example used for regression and summary checks.
- [tests/fixtures/single_species_ties.csv](https://github.com/gtzjh/pyspthin/blob/main/tests/fixtures/single_species_ties.csv)
  Symmetric tie-heavy single-species example used for serial/parallel reproducibility checks.
- [tests/fixtures/multi_species.csv](https://github.com/gtzjh/pyspthin/blob/main/tests/fixtures/multi_species.csv)
  Two-species example used for `thin_many(...)`.

Benchmark data is generated on demand by [benchmarks/run_benchmarks.py](https://github.com/gtzjh/pyspthin/blob/main/benchmarks/run_benchmarks.py).
