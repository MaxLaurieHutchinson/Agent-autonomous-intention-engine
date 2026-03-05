import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


class CliIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir_obj = tempfile.TemporaryDirectory()
        self.temp_dir = Path(self.temp_dir_obj.name)

        self.memory_dir = self.temp_dir / "memory"
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        (self.memory_dir / "INTENT.md").write_text("# Intent\nFocus on reliable Python tooling\n", encoding="utf-8")
        (self.memory_dir / "PHILOSOPHY.md").write_text("# Philosophy\nHuman gate for sensitive work\n", encoding="utf-8")

        self.knowledge_dir = self.memory_dir / "knowledge"
        (self.knowledge_dir / "frameworks").mkdir(parents=True, exist_ok=True)
        (self.knowledge_dir / "patterns").mkdir(parents=True, exist_ok=True)
        (self.knowledge_dir / "insights").mkdir(parents=True, exist_ok=True)

        (self.knowledge_dir / "frameworks" / "f1.md").write_text(
            "OODA observe orient decide act workflow architecture", encoding="utf-8"
        )
        (self.knowledge_dir / "patterns" / "p1.md").write_text(
            "deterministic replayability guardrails evidence", encoding="utf-8"
        )
        (self.knowledge_dir / "insights" / "i1.md").write_text(
            "agent infrastructure trend risk controls", encoding="utf-8"
        )

        self.proposals_dir = self.memory_dir / "proposals"
        self.metrics_dir = self.memory_dir / "metrics"
        self.briefings_dir = self.memory_dir / "briefings"
        self.data_dir = self.temp_dir / "data"
        self.logs_dir = self.temp_dir / "logs"
        self.replay_dir = self.data_dir / "intention-engine-runs"

        self.cron_jobs_path = self.temp_dir / "cron" / "jobs.json"
        self.cron_jobs_path.parent.mkdir(parents=True, exist_ok=True)
        self.cron_jobs_path.write_text(
            json.dumps(
                {
                    "jobs": [
                        {
                            "id": "demo-job",
                            "name": "IE Deep Run (Orchestrated)",
                            "state": {"lastError": "cron announce delivery failed"},
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )

        self.config_path = self.temp_dir / "runtime.json"
        self.config_path.write_text(
            json.dumps(
                {
                    "daily_budget_gbp": 2.0,
                    "reserve_budget_gbp": 0.2,
                    "mode_profiles": {
                        "micro": {
                            "enabled": True,
                            "max_items": 2,
                            "max_run_cost": 0.05,
                            "validation": "smoke",
                            "delegation": False,
                            "checkpointing": False,
                        },
                        "deep": {
                            "enabled": True,
                            "max_items": 5,
                            "max_run_cost": 0.2,
                            "validation": "smoke",
                            "delegation": True,
                            "checkpointing": False,
                        },
                        "research_deep": {
                            "enabled": False,
                            "max_items": 8,
                            "max_run_cost": 0.4,
                            "validation": "full",
                            "delegation": True,
                            "checkpointing": True,
                        },
                    },
                    "paths": {
                        "intent_path": str(self.memory_dir / "INTENT.md"),
                        "reflect_path": str(self.memory_dir / "REFLECT.md"),
                        "philosophy_path": str(self.memory_dir / "PHILOSOPHY.md"),
                        "proposals_dir": str(self.proposals_dir),
                        "briefings_dir": str(self.briefings_dir),
                        "metrics_dir": str(self.metrics_dir),
                        "budget_state_path": str(self.data_dir / "intention-engine-budget.json"),
                        "lock_path": str(self.data_dir / "intention-engine.lock"),
                        "logs_path": str(self.logs_dir / "engine.jsonl"),
                        "replay_dir": str(self.replay_dir),
                        "cron_jobs_path": str(self.cron_jobs_path),
                    },
                    "context_sources": [
                        {"name": "intent", "path": str(self.memory_dir / "INTENT.md"), "weight": 1.3},
                        {"name": "philosophy", "path": str(self.memory_dir / "PHILOSOPHY.md"), "weight": 1.2},
                        {
                            "name": "knowledge_patterns",
                            "path": str(self.knowledge_dir / "patterns" / "*.md"),
                            "weight": 1.1,
                        },
                        {
                            "name": "knowledge_frameworks",
                            "path": str(self.knowledge_dir / "frameworks" / "*.md"),
                            "weight": 1.0,
                        },
                        {
                            "name": "knowledge_insights",
                            "path": str(self.knowledge_dir / "insights" / "*.md"),
                            "weight": 0.9,
                        },
                    ],
                    "sources": [
                        {
                            "id": "fixture-intake",
                            "type": "fixture",
                            "name": "test-fixture",
                            "enabled": True,
                            "limit": 10,
                            "timeout_s": 5,
                            "filters": {
                                "max_age_hours": 720
                            },
                            "items": [
                                {
                                    "title": "Agent architecture benchmark",
                                    "url": "https://example.com/a",
                                    "engagement": 22,
                                    "created_at": "2026-03-03T10:00:00Z",
                                },
                                {
                                    "title": "Auth migration checklist",
                                    "url": "https://example.com/b",
                                    "engagement": 18,
                                    "created_at": "2026-03-03T11:00:00Z",
                                },
                            ],
                        }
                    ],
                    "routing": {
                        "auto_safe_threshold": 0.1,
                        "policy_guarded_threshold": 0.1,
                        "defer_threshold": 0.0,
                        "min_relevance_threshold": 0.0,
                        "allow_policy_guarded_auto": False,
                        "guarded_keywords": ["migration", "oauth", "security", "auth"],
                        "always_human_gate_keywords": ["password", "token", "production"],
                    },
                },
                indent=2,
            ),
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.temp_dir_obj.cleanup()

    def run_cli(self, args):
        cli_bin = shutil.which("intention-engine")
        if cli_bin:
            cmd = [cli_bin, "--config", str(self.config_path)] + list(args)
        else:
            cmd = ["python3", "-m", "intention_engine_core.cli", "--config", str(self.config_path)] + list(args)
        return subprocess.run(cmd, capture_output=True, text=True, check=False)

    def parse_stdout_json(self, completed: subprocess.CompletedProcess):
        self.assertNotEqual(completed.stdout.strip(), "", msg=completed.stderr)
        return json.loads(completed.stdout)

    def test_run_micro_writes_artifacts(self) -> None:
        completed = self.run_cli(["run", "--mode", "micro"])
        self.assertEqual(completed.returncode, 0, msg=completed.stderr)
        payload = self.parse_stdout_json(completed)

        self.assertEqual(payload["status"], "ok")
        self.assertIn("run_id", payload)

        run_id = payload["run_id"]
        bundle = self.replay_dir / run_id
        self.assertTrue((bundle / "inputs.json").exists())
        self.assertTrue((bundle / "scores.json").exists())
        self.assertTrue((bundle / "decisions.json").exists())
        self.assertTrue((bundle / "config-hash.txt").exists())
        self.assertTrue((self.data_dir / "intention-engine-budget.json").exists())

        inputs_payload = json.loads((bundle / "inputs.json").read_text(encoding="utf-8"))
        scores_payload = json.loads((bundle / "scores.json").read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(inputs_payload.get("context_sources", [])), 3)
        self.assertGreaterEqual(len(scores_payload.get("context_sources", [])), 3)

    def test_status_json_contains_contract_fields(self) -> None:
        self.run_cli(["run", "--mode", "micro"])
        completed = self.run_cli(["status", "--json"])
        self.assertEqual(completed.returncode, 0, msg=completed.stderr)

        payload = self.parse_stdout_json(completed)
        self.assertIn("budget", payload)
        self.assertIn("queues", payload)
        self.assertIn("last_run", payload)
        self.assertIn("health", payload)
        self.assertIn("failure_taxonomy", payload["health"])
        self.assertGreaterEqual(len(payload["health"]["announce_failures"]), 1)
        self.assertGreaterEqual(len(payload["health"]["actionable_errors"]), 1)

    def test_replay_reproduces_route_decisions(self) -> None:
        run = self.run_cli(["run", "--mode", "micro"])
        run_payload = self.parse_stdout_json(run)

        replay = self.run_cli(["replay", "--run-id", run_payload["run_id"]])
        self.assertEqual(replay.returncode, 0, msg=replay.stderr)
        replay_payload = self.parse_stdout_json(replay)

        self.assertEqual(replay_payload["status"], "ok")
        self.assertEqual(replay_payload["mismatches"], [])
        self.assertTrue(replay_payload["context_sources_present"])

    def test_replay_mismatch_is_detected(self) -> None:
        run = self.run_cli(["run", "--mode", "micro"])
        run_payload = self.parse_stdout_json(run)

        bundle = self.replay_dir / run_payload["run_id"]
        decisions_path = bundle / "decisions.json"
        decisions_payload = json.loads(decisions_path.read_text(encoding="utf-8"))
        if decisions_payload.get("decisions"):
            decisions_payload["decisions"][0]["route"] = "deferred"
            decisions_path.write_text(json.dumps(decisions_payload, indent=2) + "\n", encoding="utf-8")

        replay = self.run_cli(["replay", "--run-id", run_payload["run_id"]])
        self.assertNotEqual(replay.returncode, 0)
        replay_payload = self.parse_stdout_json(replay)
        self.assertEqual(replay_payload["status"], "error")
        self.assertEqual(replay_payload["error_code"], "ROUTE_MISMATCH_DETECTED")
        self.assertGreaterEqual(len(replay_payload["mismatches"]), 1)

    def test_research_mode_is_disabled(self) -> None:
        completed = self.run_cli(["run", "--mode", "research_deep"])
        self.assertNotEqual(completed.returncode, 0)
        payload = self.parse_stdout_json(completed)
        self.assertEqual(payload["status"], "mode_disabled")

    def test_missing_subcommand_fails(self) -> None:
        completed = self.run_cli([])
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("the following arguments are required: command", completed.stderr)

    def test_validate_rejects_deprecated_fields(self) -> None:
        payload = json.loads(self.config_path.read_text(encoding="utf-8"))
        payload["intake"] = {"default_saga_id": "S02"}
        self.config_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

        completed = self.run_cli(["validate", "--json"])
        self.assertNotEqual(completed.returncode, 0)
        validate_payload = self.parse_stdout_json(completed)
        self.assertIn("intake is no longer supported in this runtime contract", validate_payload["errors"])

    def test_validate_rejects_unsupported_source_type(self) -> None:
        payload = json.loads(self.config_path.read_text(encoding="utf-8"))
        payload["sources"][0]["type"] = "foorilla"
        self.config_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

        completed = self.run_cli(["validate", "--json"])
        self.assertNotEqual(completed.returncode, 0)
        validate_payload = self.parse_stdout_json(completed)
        error_text = "\n".join(validate_payload.get("errors", []))
        self.assertIn("unsupported", error_text.lower())


if __name__ == "__main__":
    unittest.main()
