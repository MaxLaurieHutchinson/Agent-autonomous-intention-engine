import datetime as dt
import unittest
from pathlib import Path
from unittest.mock import patch
import sys

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_DIR))

import intention_engine_core.runtime as ie

RSS_SAMPLE = """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<rss version=\"2.0\"><channel>
<item><title>Agent systems in production</title><link>https://example.org/a?utm_source=x</link><pubDate>Thu, 05 Mar 2026 10:00:00 +0000</pubDate></item>
<item><title>Reasoning benchmark suite</title><link>https://example.org/b</link><pubDate>Thu, 05 Mar 2026 09:30:00 +0000</pubDate></item>
</channel></rss>
"""


class SourceDiscoveryIntegrationTests(unittest.TestCase):
    @patch("intention_engine_core.sources.rss.fetch_text", return_value=RSS_SAMPLE)
    @patch("intention_engine_core.sources.arxiv.fetch_text", return_value=RSS_SAMPLE)
    def test_discovery_mixed_sources_is_deterministic(self, _mock_arxiv, _mock_rss) -> None:
        now = dt.datetime(2026, 3, 5, 12, 0, tzinfo=dt.timezone.utc)
        config = {
            "sources": [
                {
                    "id": "fixture-source",
                    "name": "fixture",
                    "type": "fixture",
                    "enabled": True,
                    "limit": 5,
                    "timeout_s": 5,
                    "filters": {},
                    "items": [
                        {
                            "title": "MCP agent orchestration",
                            "url": "https://example.org/mcp",
                            "engagement": 7,
                            "created_at": "2026-03-05T09:00:00Z",
                        }
                    ],
                },
                {
                    "id": "rss-source",
                    "name": "rss",
                    "type": "rss",
                    "feed_url": "https://aifeed.dev/feed.xml",
                    "enabled": True,
                    "limit": 5,
                    "timeout_s": 5,
                    "filters": {},
                },
                {
                    "id": "arxiv-source",
                    "name": "arxiv",
                    "type": "arxiv",
                    "categories": ["cs.AI", "cs.LG"],
                    "enabled": True,
                    "limit": 5,
                    "timeout_s": 5,
                    "filters": {},
                },
            ]
        }

        first_candidates, first_errors, first_source_stats, first_dedupe = ie.discover_candidates(config, now)
        second_candidates, second_errors, second_source_stats, second_dedupe = ie.discover_candidates(config, now)

        self.assertEqual(first_errors, second_errors)
        self.assertEqual(first_source_stats, second_source_stats)
        self.assertEqual(first_dedupe, second_dedupe)
        self.assertEqual(
            [candidate.canonical_url for candidate in first_candidates],
            [candidate.canonical_url for candidate in second_candidates],
        )
        self.assertGreaterEqual(len(first_candidates), 3)


if __name__ == "__main__":
    unittest.main()
