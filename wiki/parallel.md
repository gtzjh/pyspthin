# Parallel Execution

Supported modes:

- `parallel_mode="rep"`: multiple replicates of one species may run concurrently
- `parallel_mode="species"`: multiple species may run concurrently, with each species processed serially internally

Implementation notes:

- the code prefers process-based execution for deterministic isolation
- if the current platform cannot execute the pool cleanly, the implementation falls back to serial execution with a warning
- nested parallelism is not enabled by default

