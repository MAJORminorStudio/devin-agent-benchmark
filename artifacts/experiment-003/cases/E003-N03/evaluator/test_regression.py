import unittest

from record_export import to_plain


class ConversionRegressionTests(unittest.TestCase):
    def test_scalars_and_alias_free_mappings_are_unchanged(self):
        self.assertEqual(
            to_plain({"values": [1, "two", None]}, aliases=False),
            {"values": [1, "two", None]},
        )


if __name__ == "__main__":
    unittest.main()
