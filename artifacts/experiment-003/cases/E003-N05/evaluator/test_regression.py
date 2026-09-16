import unittest

from line_protocol import TransactionParser


class TransactionRegressionTests(unittest.TestCase):
    def test_malformed_lines_are_ignored_between_valid_records(self):
        parser = TransactionParser()
        self.assertEqual(
            parser.feed("BEGIN ok\nFIELD a=b\nNOISE\nCOMMIT\n"),
            [{"id": "ok", "fields": {"a": "b"}}],
        )


if __name__ == "__main__":
    unittest.main()
