from __future__ import annotations

import unittest

from pyspthin import thin

from tests.test_support import load_fixture


class FailureModeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.single = load_fixture("single_species.csv")

    def test_empty_input_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            thin(self.single.iloc[0:0], thin_par=8.0, reps=2)

    def test_conflict_edge_guard_raises(self) -> None:
        with self.assertRaises(ValueError):
            thin(self.single, thin_par=8.0, reps=2, max_conflict_edges=1)


if __name__ == "__main__":
    unittest.main()
