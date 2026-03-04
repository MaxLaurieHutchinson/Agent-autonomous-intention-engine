import unittest
from pathlib import Path
import sys

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_DIR))

import intention_engine_core.runtime as ie


class RoutingGuardrailTests(unittest.TestCase):
    def setUp(self) -> None:
        self.routing = {
            "auto_safe_threshold": 0.75,
            "policy_guarded_threshold": 0.7,
            "defer_threshold": 0.45,
            "min_relevance_threshold": 0.08,
            "allow_policy_guarded_auto": False,
            "guarded_keywords": ["migration", "oauth", "security"],
            "always_human_gate_keywords": ["password", "token", "production"],
        }

    def test_human_gate_keyword_forces_human_gate(self) -> None:
        risk, _, autonomy_class = ie.classify_risk(
            "Rotate production token today",
            "https://example.com/runbook",
            self.routing,
        )
        self.assertEqual(autonomy_class, "human_gate")
        self.assertGreaterEqual(risk, 0.9)

    def test_policy_guarded_not_auto_approved_by_default(self) -> None:
        route = ie.route_from_values(
            score=1.2,
            relevance=0.5,
            autonomy_class="policy_guarded",
            routing=self.routing,
        )
        self.assertEqual(route, "inbox")

    def test_routing_thresholds_are_config_driven(self) -> None:
        conservative = dict(self.routing)
        conservative["defer_threshold"] = 0.9

        permissive = dict(self.routing)
        permissive["defer_threshold"] = 0.1

        strict_route = ie.route_from_values(0.4, 0.4, "auto_safe", conservative)
        loose_route = ie.route_from_values(0.4, 0.4, "auto_safe", permissive)

        self.assertEqual(strict_route, "deferred")
        self.assertEqual(loose_route, "inbox")


if __name__ == "__main__":
    unittest.main()
