from __future__ import annotations

import unittest

from pyspthin import thin, thin_many
from tests.test_support import load_fixture


class ValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.single = load_fixture("single_species.csv")
        self.multi = load_fixture("multi_species.csv")

    def test_invalid_latitude_raises(self) -> None:
        bad = self.single.copy()
        bad.loc[0, "LAT"] = 95.0

        with self.assertRaises(ValueError):
            thin(bad, thin_par=8.0, reps=2)

    def test_non_numeric_longitude_reports_row_field_value_and_reason(self) -> None:
        bad = self.single.copy()
        bad["LONG"] = bad["LONG"].astype(object)
        bad.loc[0, "LONG"] = "abc"

        with self.assertRaises(ValueError) as error:
            thin(bad, thin_par=8.0, reps=2)

        message = str(error.exception)
        self.assertIn("Validation failed", message)
        self.assertIn("row 0", message)
        self.assertIn("field LONG", message)
        self.assertIn("value 'abc'", message)
        self.assertIn("must be numeric", message)

    def test_missing_coordinate_reports_row_field_and_reason(self) -> None:
        bad = self.single.copy()
        bad.loc[1, "LAT"] = None

        with self.assertRaises(ValueError) as error:
            thin(bad, thin_par=8.0, reps=2)

        message = str(error.exception)
        self.assertIn("Validation failed", message)
        self.assertIn("row 1", message)
        self.assertIn("field LAT", message)
        self.assertIn("is missing", message)

    def test_empty_species_reports_row_field_and_reason(self) -> None:
        bad = self.single.copy()
        bad.loc[0, "SPEC"] = " "

        with self.assertRaises(ValueError) as error:
            thin(bad, thin_par=8.0, reps=2)

        message = str(error.exception)
        self.assertIn("Validation failed", message)
        self.assertIn("row 0", message)
        self.assertIn("field SPEC", message)
        self.assertIn("must be non-empty", message)

    def test_missing_required_column_raises(self) -> None:
        bad = self.single.drop(columns=["LONG"])

        with self.assertRaises(ValueError):
            thin(bad, thin_par=8.0, reps=2)

    def test_duplicate_explicit_record_id_raises(self) -> None:
        bad = self.single.copy()
        bad.loc[1, "OBS_ID"] = bad.loc[0, "OBS_ID"]

        with self.assertRaises(ValueError):
            thin(bad, thin_par=8.0, reps=2, record_id_col="OBS_ID")

    def test_explicit_record_id_duplicate_reports_row_field_value_and_reason(self) -> None:
        bad = self.single.copy()
        bad.loc[1, "OBS_ID"] = bad.loc[0, "OBS_ID"]

        with self.assertRaises(ValueError) as error:
            thin(bad, thin_par=8.0, reps=2, record_id_col="OBS_ID")

        message = str(error.exception)
        self.assertIn("Validation failed", message)
        self.assertIn("row 1", message)
        self.assertIn("field OBS_ID", message)
        self.assertIn("value 'obs-1'", message)
        self.assertIn("must be unique", message)

    def test_negative_seed_is_rejected_during_configuration_validation(self) -> None:
        with self.assertRaises(ValueError) as error:
            thin(self.single, thin_par=8.0, reps=2, seed=-1)

        self.assertIn("seed", str(error.exception))

    def test_missing_policy_argument_is_removed(self) -> None:
        with self.assertRaises(ValueError) as error:
            thin(self.single, thin_par=8.0, reps=2, missing_policy="drop")

        self.assertIn("missing_policy", str(error.exception))

    def test_multiple_species_are_rejected_by_thin(self) -> None:
        with self.assertRaises(ValueError):
            thin(self.multi, thin_par=8.0, reps=2)

    def test_invalid_parallel_mode_raises(self) -> None:
        with self.assertRaises(ValueError):
            thin_many(self.multi, thin_par=8.0, reps=2, parallel_mode="auto")


if __name__ == "__main__":
    unittest.main()
