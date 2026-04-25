# Development

Project layout:

- package code: [src/pyspthin](https://github.com/gtzjh/pyspthin/tree/main/src/pyspthin)
- unit/property/regression tests: [tests](https://github.com/gtzjh/pyspthin/tree/main/tests)
- R reference script: [run_r_reference.R](https://github.com/gtzjh/pyspthin/blob/main/spThin-R/scripts/run_r_reference.R)
- benchmark script: [benchmarks/run_benchmarks.py](https://github.com/gtzjh/pyspthin/blob/main/benchmarks/run_benchmarks.py)

Recommended local commands:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
Rscript spThin-R/scripts/run_r_reference.R tests/fixtures/single_species.csv /tmp/ref.json 8.0 4 LONG LAT 123
PYTHONPATH=src python3 benchmarks/run_benchmarks.py
```

Design boundaries:

- do not replace the greedy thinning semantics with a different optimization target
- keep output row restoration based on `record_id`
- keep serial and parallel runs reproducible from explicit child seeds
