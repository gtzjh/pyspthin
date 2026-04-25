# Randomness Design

`pyspthin` does not rely on global RNG state.

- a master seed is validated in config
- replicate seeds are derived with `numpy.random.SeedSequence`
- `thin_many(...)` derives species-level seeds first, then each species run derives replicate seeds
- because seeds are derived before execution, serial and parallel runs stay reproducible under the same input/configuration

