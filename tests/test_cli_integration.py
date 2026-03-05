import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

MODULE_ROOT = Path(__file__).resolve().parents[1]


class CliIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir_obj = tempfile.TemporaryDirectory()
        self.temp_dir = Path(self.temp_dir_obj.name)

        self.memory_dir = self.temp_dir / "memory"
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        (self.memory_dir / "INTENT.md").write_text("# Intent\nFocus on reliable Python tooling\n", encoding="utf-8")
        (self.memory_dir / "PHILOSOPHY.md").write_text("# Philosophy\nHuman gate for sensitive work\n", encoding="utf-8")

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
                    "sources": [
                        {
                            "type": "fixture",
                            "name": "test-fixture",
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
        env = dict(**os.environ)
        src_path = str(MODULE_ROOT / "src")
        env["PYTHONPATH"] = f"{src_path}:{env['PYTHONPATH']}" if env.get("PYTHONPATH") else src_path
        cmd = [sys.executable, "-m", "intention_engine_core.cli", "--config", str(self.config_path)] + list(args)
        return subprocess.run(cmd, capture_output=True, text=True, check=False, env=env)

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

    def test_status_json_contains_contract_fields(self) -> None:
        self.run_cli(["run", "--mode", "micro"])
        completed = self.run_cli(["status", "--json"])
        self.assertEqual(completed.returncode, 0, msg=completed.stderr)

        payload = self.parse_stdout_json(completed)
        self.assertIn("budget", payload)
        self.assertIn("queues", payload)
        self.assertIn("last_run", payload)
        self.assertIn("health", payload)
        self.assertGreaterEqual(len(payload["health"]["announce_failures"]), 1)

    def test_replay_reproduces_route_decisions(self) -> None:
        run = self.run_cli(["run", "--mode", "micro"])
        run_payload = self.parse_stdout_json(run)

        replay = self.run_cli(["replay", "--run-id", run_payload["run_id"]])
        self.assertEqual(replay.returncode, 0, msg=replay.stderr)
        replay_payload = self.parse_stdout_json(replay)

        self.assertEqual(replay_payload["status"], "ok")
        self.assertEqual(replay_payload["mismatches"], [])

    def test_research_mode_is_disabled(self) -> None:
        completed = self.run_cli(["run", "--mode", "research_deep"])
        self.assertNotEqual(completed.returncode, 0)
        payload = self.parse_stdout_json(completed)
        self.assertEqual(payload["status"], "mode_disabled")

    def test_missing_subcommand_fails(self) -> None:
        completed = self.run_cli([])
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("the following arguments are required: command", completed.stderr)

    def test_workspace_wrappers_execute(self) -> None:
        env = dict(**os.environ, INTENTION_ENGINE_CONFIG=str(self.config_path))

        micro_wrapper = MODULE_ROOT / "ops" / "ie_micro.sh"
        status_wrapper = MODULE_ROOT / "ops" / "ie_status.sh"

        micro_run = subprocess.run(
            ["bash", str(micro_wrapper), "--dry-run"],
            capture_output=True,
            text=True,
            check=False,
            env=env,
        )
        self.assertEqual(micro_run.returncode, 0, msg=micro_run.stderr)

        status_run = subprocess.run(
            ["bash", str(status_wrapper)],
            capture_output=True,
            text=True,
            check=False,
            env=env,
        )
        self.assertEqual(status_run.returncode, 0, msg=status_run.stderr)
        payload = json.loads(status_run.stdout)
        self.assertIn("budget", payload)

    def test_module_entrypoint_executes(self) -> None:
        env = dict(**os.environ)
        src_path = str(MODULE_ROOT / "src")
        env["PYTHONPATH"] = f"{src_path}:{env['PYTHONPATH']}" if env.get("PYTHONPATH") else src_path

        cmd = [
            sys.executable,
            "-m",
            "intention_engine_core.cli",
            "--config",
            str(self.config_path),
            "run",
            "--mode",
            "micro",
            "--dry-run",
        ]
        completed = subprocess.run(cmd, capture_output=True, text=True, check=False, env=env)
        self.assertEqual(completed.returncode, 0, msg=completed.stderr)

        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "dry_run")


if __name__ == "__main__":
    unittest.main()
