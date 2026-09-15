import unittest

from line_protocol import TransactionParser


class TransactionTests(unittest.TestCase):
    def test_new_transaction_replaces_an_incomplete_one(self):
        parser = TransactionParser()

        records = parser.feed(
            "BEGIN old\nFIELD status=stale\n"
            "BEGIN new\nFIELD status=ready\nCOMMIT\n"
        )

        self.assertEqual(records, [{"id": "new", "fields": {"status": "ready"}}])


if __name__ == "__main__":
    unittest.main()
