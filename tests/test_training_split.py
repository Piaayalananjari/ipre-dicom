import unittest

from scripts.train import split_rows


class TrainingSplitTests(unittest.TestCase):
    def test_variants_from_same_source_never_cross_split(self):
        rows = []
        for source in range(20):
            for variant in range(4):
                rows.append({
                    "path": f"source-{source}-variant-{variant}.png",
                    "label": variant % 2,
                    "group": f"source-{source}",
                })
        train, validation, method = split_rows(rows)
        train_groups = {row["group"] for row in train}
        validation_groups = {row["group"] for row in validation}
        self.assertEqual(method, "grouped")
        self.assertFalse(train_groups & validation_groups)


if __name__ == "__main__":
    unittest.main()
