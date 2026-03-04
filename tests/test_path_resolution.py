import unittest
from pathlib import Path

import sys

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_DIR))

from intention_engine_core.path_resolver import resolve_path_value


class PathResolutionTests(unittest.TestCase):
    def test_relative_path_resolves_from_workspace_root(self) -> None:
        workspace_root = Path("/tmp/workspace-root")
        resolved = resolve_path_value("memory/INTENT.md", workspace_root)
        self.assertEqual(resolved, (workspace_root / "memory/INTENT.md").resolve())

    def test_absolute_path_preserved(self) -> None:
        workspace_root = Path("/tmp/workspace-root")
        resolved = resolve_path_value("/var/tmp/custom.json", workspace_root)
        self.assertEqual(resolved, Path("/var/tmp/custom.json"))

    def test_tilde_path_expands_home(self) -> None:
        workspace_root = Path("/tmp/workspace-root")
        resolved = resolve_path_value("~/openclaw/jobs.json", workspace_root)
        self.assertEqual(resolved, Path.home() / "openclaw/jobs.json")


if __name__ == "__main__":
    unittest.main()
