"""Evaluator-only behavioral checks for Black 16."""

from pathlib import Path
import re
import tempfile
import unittest

import black


class ExternalSymlinkBehaviorTest(unittest.TestCase):
    def test_external_python_symlink_is_ignored(self):
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary) / "workspace"
            outside = Path(temporary) / "outside.py"
            workspace.mkdir()
            inside = workspace / "inside.py"
            inside.write_text("value = 1\n", encoding="utf-8")
            outside.write_text("value = 2\n", encoding="utf-8")
            external_link = workspace / "linked.py"
            try:
                external_link.symlink_to(outside)
            except OSError as exc:
                self.skipTest("symbolic links are unavailable: %s" % exc)

            discovered = list(
                black.gen_python_files_in_dir(
                    workspace.resolve(),
                    workspace.resolve(),
                    re.compile(black.DEFAULT_INCLUDES),
                    re.compile(black.DEFAULT_EXCLUDES),
                    black.Report(),
                )
            )

            self.assertIn(inside.resolve(), discovered)
            self.assertNotIn(external_link.resolve(), discovered)
            self.assertNotIn(outside.resolve(), discovered)
