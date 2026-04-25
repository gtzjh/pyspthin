# Compatibility Checklist

`pyspthin` keeps the following R `spThin` semantics aligned:

- conflicts are defined by great-circle distance strictly less than `thin_par`
- each replicate starts from the same original conflict graph
- each iteration removes one point among those with the current maximum conflict count
- ties are broken randomly within a replicate-specific RNG stream
- replicates stop once no conflicts remain
- replicate outputs are sorted by retained count in descending order

Allowed implementation differences:

- Python uses a sparse conflict graph instead of a dense distance matrix
- Python preserves original input rows and extra columns via `record_id`
- parallel execution and structured result objects are explicit Python-side additions

