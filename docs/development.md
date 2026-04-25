# Development

Project layout:

- package code: [src/pyspthin](/Users/jarviski/workspace/spThin/src/pyspthin)
- unit/property/regression tests: [tests](/Users/jarviski/workspace/spThin/tests)
- R reference script: [run_r_reference.R](/Users/jarviski/workspace/spThin/spThin-R/scripts/run_r_reference.R)
- benchmark script: [benchmarks/run_benchmarks.py](/Users/jarviski/workspace/spThin/benchmarks/run_benchmarks.py)

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
