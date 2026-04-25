# Development

Project layout:

- package code: [src/pyspthin](https://github.com/gtzjh/pyspthin/tree/main/src/pyspthin)
- unit/property/regression tests: [tests](https://github.com/gtzjh/pyspthin/tree/main/tests)
- benchmark script: [benchmarks/run_benchmarks.py](https://github.com/gtzjh/pyspthin/blob/main/benchmarks/run_benchmarks.py)

Recommended local commands:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
PYTHONPATH=src python3 benchmarks/run_benchmarks.py
```

Design boundaries:

- do not replace the greedy thinning semantics with a different optimization target
- keep output row restoration based on `pyspthin_record_id`
- never overwrite user-provided columns; generated columns must use the `pyspthin_` prefix
- fail invalid required data before graph construction
- include row-level context in validation errors when a specific row value is invalid
- keep serial and parallel runs reproducible from explicit child seeds
