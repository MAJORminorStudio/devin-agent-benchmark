import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import validate_public_surface  # noqa: E402


class PublicSurfaceTests(unittest.TestCase):
    def test_tracked_content_has_no_public_surface_findings(self):
        self.assertEqual(validate_public_surface.scan(), [])


if __name__ == "__main__":
    unittest.main()
