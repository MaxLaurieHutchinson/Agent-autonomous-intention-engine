import datetime as dt
import unittest
from pathlib import Path
import sys

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_DIR))

from intention_engine_core.sources.common import apply_source_filters, dedupe_candidates, make_candidate


class SourceFiltersAndDedupeTests(unittest.TestCase):
    def test_filters_and_dedupe_are_deterministic(self) -> None:
        now = dt.datetime(2026, 3, 5, 12, 0, tzinfo=dt.timezone.utc)

        candidates = [
            make_candidate(
                source_label="test",
                source_id="s1",
                source_name="test",
                source_type="fixture",
                source_index=0,
                title="Agent architecture benchmark",
                url="https://example.com/article?utm_source=x",
                engagement=10,
                created_at=now - dt.timedelta(hours=2),
            ),
            make_candidate(
                source_label="test",
                source_id="s1",
                source_name="test",
                source_type="fixture",
                source_index=0,
                title="Agent architecture benchmark",
                url="https://example.com/article",
                engagement=9,
                created_at=now - dt.timedelta(hours=3),
            ),
            make_candidate(
                source_label="test",
                source_id="s1",
                source_name="test",
                source_type="fixture",
                source_index=0,
                title="Sports transfer roundup",
                url="https://sports.example.com/news",
                engagement=200,
                created_at=now - dt.timedelta(hours=1),
            ),
        ]

        filtered, filter_stats = apply_source_filters(
            candidates,
            {
                "include_keywords": ["agent", "llm"],
                "exclude_keywords": ["sports"],
                "max_age_hours": 48,
                "min_engagement": 1,
                "domain_blocklist": ["blocked.example.com"],
            },
            now,
        )
        deduped, dedupe_stats = dedupe_candidates(filtered)

        self.assertEqual(len(filtered), 2)
        self.assertEqual(filter_stats["dropped_include_keywords"], 1)
        self.assertEqual(len(deduped), 1)
        self.assertEqual(dedupe_stats["dropped_canonical_url"], 1)
        self.assertEqual(deduped[0].canonical_url, "https://example.com/article")


if __name__ == "__main__":
    unittest.main()
