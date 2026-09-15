import unittest

from catalog import Catalog


class CatalogRegressionTests(unittest.TestCase):
    def test_empty_and_sorted_queries_are_stable(self):
        catalog = Catalog()
        self.assertEqual(catalog.ids_for_tag("missing"), ())
        catalog.add("z", tags=["blue"])
        catalog.add("a", tags=["blue"])
        self.assertEqual(catalog.ids_for_tag("blue"), ("a", "z"))


if __name__ == "__main__":
    unittest.main()
