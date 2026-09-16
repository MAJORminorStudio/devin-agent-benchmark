import unittest

from line_protocol import TransactionParser


class TransactionBehaviorTests(unittest.TestCase):
    def test_fragmentation_and_duplicate_commit_do_not_corrupt_state(self):
        parser = TransactionParser()
        chunks = [
            "BEGIN o",
            "ld\r\nFIELD x=1\r\nBE",
            "GIN new\nFIELD y=2\nCOM",
            "MIT\nCOMMIT\nBEGIN last\nFIELD z=3\nCOMMIT\n",
        ]
        records = []
        for chunk in chunks:
            records.extend(parser.feed(chunk))
        self.assertEqual(
            records,
            [
                {"id": "new", "fields": {"y": "2"}},
                {"id": "last", "fields": {"z": "3"}},
            ],
        )


if __name__ == "__main__":
    unittest.main()
