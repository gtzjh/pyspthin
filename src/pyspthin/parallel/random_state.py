"""Seed management for reproducible runs."""

from __future__ import annotations

import numpy as np


def derive_child_seeds(master_seed: int, count: int, namespace: tuple[int, ...] = ()) -> list[int]:
    if count <= 0:
        return []
    seed_sequence = np.random.SeedSequence([master_seed, *namespace])
    return [
        int(child.generate_state(1, dtype=np.uint32)[0]) for child in seed_sequence.spawn(count)
    ]
