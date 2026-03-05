import unittest
from pathlib import Path
import sys

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_DIR))

from intention_engine_core.sources.registry import get_source_adapter, supported_source_types


class SourceRegistryTests(unittest.TestCase):
    def test_supported_source_types_include_new_adapters(self) -> None:
        source_types = set(supported_source_types())
        self.assertIn("rss", source_types)
        self.assertIn("arxiv", source_types)
        self.assertIn("reddit", source_types)
        self.assertIn("hackernews", source_types)
        self.assertIn("github", source_types)
        self.assertIn("fixture", source_types)

    def test_registry_dispatch_returns_adapter(self) -> None:
        adapter = get_source_adapter("rss")
        self.assertIsNotNone(adapter)
        self.assertEqual(adapter.source_type, "rss")

        missing = get_source_adapter("unknown")
        self.assertIsNone(missing)


if __name__ == "__main__":
    unittest.main()
