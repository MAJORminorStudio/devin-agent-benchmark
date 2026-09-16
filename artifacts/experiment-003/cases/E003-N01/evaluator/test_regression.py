import tempfile
import unittest
from pathlib import Path

from asset_index import discover_python_files


class DiscoveryRegressionTests(unittest.TestCase):
    def test_regular_nested_files_are_sorted(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "z.py").write_text("z = 1\n", encoding="utf-8")
            (root / "pkg").mkdir()
            (root / "pkg" / "a.py").write_text("a = 1\n", encoding="utf-8")
            self.assertEqual(discover_python_files(root), ["pkg/a.py", "z.py"])


if __name__ == "__main__":
    unittest.main()
