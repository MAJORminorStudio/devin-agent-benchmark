import unittest

from catalog import Catalog


class CatalogTests(unittest.TestCase):
    def test_discard_updates_a_warmed_tag_lookup(self):
        catalog = Catalog()
        catalog.add("blue-chair", tags=["furniture", "blue"])
        self.assertEqual(catalog.ids_for_tag("blue"), ("blue-chair",))

        catalog.discard("blue-chair")

        self.assertEqual(catalog.ids_for_tag("blue"), ())


if __name__ == "__main__":
    unittest.main()
