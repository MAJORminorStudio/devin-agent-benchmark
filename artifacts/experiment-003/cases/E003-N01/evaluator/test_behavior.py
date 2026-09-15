import tempfile
import unittest
from pathlib import Path

from asset_index import discover_python_files


class DiscoveryBehaviorTests(unittest.TestCase):
    def test_boundary_and_in_project_links_are_handled_separately(self):
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory)
            project = parent / "app"
            sibling = parent / "app-cache"
            project.mkdir()
            sibling.mkdir()
            (project / "nested").mkdir()
            (project / "nested" / "worker.py").write_text("worker = True\n", encoding="utf-8")
            outside = sibling / "worker.py"
            outside.write_text("outside = True\n", encoding="utf-8")
            try:
                (project / "local-link.py").symlink_to(project / "nested" / "worker.py")
                (project / "external-link.py").symlink_to(outside)
            except OSError as exc:
                self.skipTest(f"symlinks unavailable: {exc}")

            self.assertEqual(
                set(discover_python_files(project)),
                {"nested/worker.py", "local-link.py"},
            )


if __name__ == "__main__":
    unittest.main()
