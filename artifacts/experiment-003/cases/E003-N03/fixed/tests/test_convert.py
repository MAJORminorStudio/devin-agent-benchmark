import unittest

from record_export import Invoice, Line, Recipient, to_plain


class ConversionTests(unittest.TestCase):
    def test_nested_lines_keep_their_container_shape(self):
        invoice = Invoice(
            recipient=Recipient("A. Reader", "reader@example.test"),
            lines=(Line("book", 2), Line("pen", 3)),
        )

        result = to_plain(invoice)

        self.assertEqual(result["recipient"]["emailAddress"], "reader@example.test")
        self.assertEqual(result["lines"], ({"sku": "book", "quantity": 2}, {"sku": "pen", "quantity": 3}))


if __name__ == "__main__":
    unittest.main()
