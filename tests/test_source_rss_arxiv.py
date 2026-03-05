import datetime as dt
import unittest
from pathlib import Path
from unittest.mock import patch
import sys

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_DIR))

from intention_engine_core.sources.arxiv import ArxivSourceAdapter
from intention_engine_core.sources.common import SourceFetchException
from intention_engine_core.sources.rss import RSSSourceAdapter, parse_feed_items


RSS_SAMPLE = """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<rss version=\"2.0\">
  <channel>
    <title>Demo Feed</title>
    <item>
      <title>Agent systems in production</title>
      <link>https://example.org/a?utm_source=x</link>
      <pubDate>Thu, 05 Mar 2026 10:00:00 +0000</pubDate>
    </item>
    <item>
      <title>Benchmarking LLM planning</title>
      <link>https://example.org/b</link>
      <pubDate>Thu, 05 Mar 2026 09:00:00 +0000</pubDate>
    </item>
  </channel>
</rss>
"""


class RSSAndArxivTests(unittest.TestCase):
    def test_parse_feed_items_rss(self) -> None:
        items = parse_feed_items(RSS_SAMPLE)
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0]["title"], "Agent systems in production")

    def test_parse_feed_items_invalid_xml(self) -> None:
        with self.assertRaises(SourceFetchException):
            parse_feed_items("<rss><broken>")

    @patch("intention_engine_core.sources.rss.fetch_text", return_value=RSS_SAMPLE)
    def test_rss_adapter_fetches_candidates(self, _mock_fetch_text) -> None:
        adapter = RSSSourceAdapter()
        result = adapter.fetch(
            {
                "id": "rss-demo",
                "name": "Demo RSS",
                "type": "rss",
                "feed_url": "https://example.org/feed.xml",
                "limit": 10,
                "timeout_s": 5,
                "_source_index": 0,
            },
            dt.datetime(2026, 3, 5, 12, 0, tzinfo=dt.timezone.utc),
        )

        self.assertEqual(len(result.errors), 0)
        self.assertEqual(len(result.candidates), 2)
        self.assertEqual(result.candidates[0].canonical_url, "https://example.org/a")

    @patch("intention_engine_core.sources.arxiv.fetch_text", return_value=RSS_SAMPLE)
    def test_arxiv_adapter_fetches_without_network(self, _mock_fetch_text) -> None:
        adapter = ArxivSourceAdapter()
        result = adapter.fetch(
            {
                "id": "arxiv-core",
                "name": "arXiv",
                "type": "arxiv",
                "categories": ["cs.AI", "cs.LG"],
                "limit": 3,
                "timeout_s": 5,
                "_source_index": 1,
            },
            dt.datetime(2026, 3, 5, 12, 0, tzinfo=dt.timezone.utc),
        )

        self.assertEqual(len(result.errors), 0)
        self.assertEqual(len(result.candidates), 3)
        self.assertTrue(all(item.source_type == "arxiv" for item in result.candidates))


if __name__ == "__main__":
    unittest.main()
