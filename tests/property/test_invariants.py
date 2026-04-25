from __future__ import annotations

import random
import unittest

import pandas as pd

from pyspthin import thin
from tests.test_support import haversine_km


def make_random_dataset(seed: int, n_points: int = 18) -> pd.DataFrame:
    rng = random.Random(seed)
    rows: list[dict[str, object]] = []
    for idx in range(n_points):
        rows.append(
            {
                "SPEC": "sp-random",
                "LONG": rng.uniform(-5.0, 5.0),
                "LAT": rng.uniform(-5.0, 5.0),
                "OBS_ID": f"obs-{seed}-{idx}",
                "SOURCE": "synthetic",
            }
        )
    return pd.DataFrame.from_records(rows)


class InvariantTests(unittest.TestCase):
    def test_retained_records_respect_distance_threshold_and_sorting(self) -> None:
        for seed in range(5):
            data = make_random_dataset(seed)
            result = thin(data, thin_par=300.0, reps=6, seed=seed)

            counts = [rep.retained_count for rep in result.replicates]
            self.assertEqual(counts, sorted(counts, reverse=True))

            original_ids = set(data["OBS_ID"])
            for rep in result.replicates:
                retained = rep.retained_dataframe
                self.assertTrue(set(rep.retained_record_ids).issubset(original_ids))
                self.assertTrue(set(data.columns).issubset(set(retained.columns)))
                self.assertEqual(
                    rep.retained_record_ids, retained["pyspthin_record_id"].astype(str).tolist()
                )

                generated_columns = set(retained.columns) - set(data.columns)
                self.assertEqual(
                    generated_columns,
                    {
                        "pyspthin_record_id",
                        "pyspthin_replicate_id",
                        "pyspthin_replicate_rank",
                        "pyspthin_retained_count",
                        "pyspthin_species",
                    },
                )
                self.assertTrue(all(column.startswith("pyspthin_") for column in generated_columns))

                coords = retained[["LONG", "LAT"]].to_records(index=False)
                for idx, left in enumerate(coords):
                    for right in coords[idx + 1 :]:
                        self.assertGreaterEqual(
                            haversine_km(left[0], left[1], right[0], right[1]),
                            300.0 - 1e-9,
                        )


if __name__ == "__main__":
    unittest.main()
