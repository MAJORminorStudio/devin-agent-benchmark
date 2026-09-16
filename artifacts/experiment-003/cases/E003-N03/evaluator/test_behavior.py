import unittest

from record_export import Invoice, Line, Recipient, to_plain


class ConversionBehaviorTests(unittest.TestCase):
    def test_nested_mixed_containers_are_plain_and_keep_shape(self):
        value = {
            "invoice": Invoice(Recipient("A. Reader", "reader@example.test"), (Line("book", 2),)),
            "bundles": [(Line("pen", 3),)],
        }
        self.assertEqual(
            to_plain(value, aliases=False, omit_none=True),
            {
                "invoice": {
                    "recipient": {"name": "A. Reader", "email": "reader@example.test"},
                    "lines": ({"sku": "book", "quantity": 2},),
                },
                "bundles": [({"sku": "pen", "quantity": 3},)],
            },
        )


if __name__ == "__main__":
    unittest.main()
