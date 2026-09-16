import unittest

from catalog import Catalog


class CatalogBehaviorTests(unittest.TestCase):
    def test_discard_invalidates_each_warmed_tag_view(self):
        catalog = Catalog()
        catalog.add("a", tags=["red", "small"])
        catalog.add("b", tags=["red", "large"])
        self.assertEqual(catalog.ids_for_tag("red"), ("a", "b"))
        self.assertEqual(catalog.ids_for_tag("small"), ("a",))

        catalog.discard("a")
        self.assertEqual(catalog.ids_for_tag("red"), ("b",))
        self.assertEqual(catalog.ids_for_tag("small"), ())

        catalog.add("c", tags=["red"])
        self.assertEqual(catalog.ids_for_tag("red"), ("b", "c"))


if __name__ == "__main__":
    unittest.main()
