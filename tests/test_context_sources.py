import tempfile
import unittest
from pathlib import Path

import sys

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_DIR))

import intention_engine_core.runtime as ie


class ContextSourcesTests(unittest.TestCase):
    def test_weighted_context_sources_are_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            memory = root / "memory"
            knowledge = memory / "knowledge"
            frameworks = knowledge / "frameworks"
            patterns = knowledge / "patterns"
            insights = knowledge / "insights"

            frameworks.mkdir(parents=True, exist_ok=True)
            patterns.mkdir(parents=True, exist_ok=True)
            insights.mkdir(parents=True, exist_ok=True)

            intent_path = memory / "INTENT.md"
            philosophy_path = memory / "PHILOSOPHY.md"
            reflect_path = memory / "REFLECT.md"

            intent_path.write_text("signal roadmap", encoding="utf-8")
            philosophy_path.write_text("signal safety", encoding="utf-8")
            reflect_path.write_text("# REFLECT\n", encoding="utf-8")

            (frameworks / "f1.md").write_text("signal noise", encoding="utf-8")
            (patterns / "p1.md").write_text("signal signal", encoding="utf-8")
            (insights / "i1.md").write_text("noise noise", encoding="utf-8")

            paths = ie.RuntimePaths(
                intent_path=intent_path,
                reflect_path=reflect_path,
                philosophy_path=philosophy_path,
                philosophy_fallback_path=philosophy_path,
                proposals_dir=memory / "proposals",
                inbox_dir=memory / "proposals" / "inbox",
                approved_dir=memory / "proposals" / "approved",
                rejected_dir=memory / "proposals" / "rejected",
                deferred_dir=memory / "proposals" / "deferred",
                briefings_dir=memory / "briefings",
                metrics_dir=memory / "metrics",
                budget_state_path=root / "data" / "budget.json",
                lock_path=root / "data" / "lock",
                logs_path=root / "logs" / "engine.jsonl",
                replay_dir=root / "data" / "runs",
                cron_jobs_path=root / "cron" / "jobs.json",
            )

            config = {
                "context_sources": [
                    {"name": "intent", "path": str(intent_path), "weight": 1.0},
                    {"name": "philosophy", "path": str(philosophy_path), "weight": 1.0},
                    {"name": "frameworks", "path": str(frameworks / "*.md"), "weight": 0.5},
                    {"name": "patterns", "path": str(patterns / "*.md"), "weight": 2.0},
                    {"name": "insights", "path": str(insights / "*.md"), "weight": 0.5},
                ]
            }

            first_keywords, first_context = ie.extract_keywords(paths, config, limit=10)
            second_keywords, second_context = ie.extract_keywords(paths, config, limit=10)

            self.assertEqual(first_keywords, second_keywords)
            self.assertEqual(first_context, second_context)
            self.assertIn("signal", first_keywords)
            self.assertIn("noise", first_keywords)
            self.assertLess(first_keywords.index("signal"), first_keywords.index("noise"))
            self.assertEqual(len(first_context), 5)


if __name__ == "__main__":
    unittest.main()
