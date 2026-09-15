import os
import tempfile
import unittest
from pathlib import Path

from asset_index import discover_python_files


class DiscoveryTests(unittest.TestCase):
    def test_files_outside_project_are_not_indexed(self):
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory)
            project = parent / "project"
            outside = parent / "project-cache"
            project.mkdir()
            outside.mkdir()
            (project / "main.py").write_text("main = True\n", encoding="utf-8")
            external = outside / "generated.py"
            external.write_text("generated = True\n", encoding="utf-8")
            link = project / "generated.py"
            try:
                link.symlink_to(external)
            except OSError as exc:
                self.skipTest(f"symlinks unavailable: {exc}")

            self.assertEqual(discover_python_files(project), ["main.py"])


if __name__ == "__main__":
    unittest.main()
