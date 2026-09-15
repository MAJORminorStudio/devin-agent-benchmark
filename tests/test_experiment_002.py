import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "isolation" / "experiment-002"))
import experiment_002_container  # noqa: E402
from allowlist_proxy import ALLOWED_HOSTS  # noqa: E402


class Experiment002InfrastructureTests(unittest.TestCase):
    def test_frozen_order_and_conditions(self):
        manifest = json.loads(
            (ROOT / "manifests" / "experiment-002-runs.json").read_text()
        )
        self.assertEqual(
            manifest["run_order"],
            [
                "E002-C02-M", "E002-C04-X", "E002-C01-M", "E002-C05-X",
                "E002-C03-M", "E002-C01-X", "E002-C04-M", "E002-C02-X",
                "E002-C05-M", "E002-C03-X",
            ],
        )
        self.assertEqual(
            [run["condition"] for run in manifest["runs"]],
            ["M", "X"] * 5,
        )
        self.assertEqual(
            {run["model"] for run in manifest["runs"]},
            {"swe-2-medium", "swe-2-max"},
        )

    def test_container_command_is_dangerous_but_unprivileged_and_unmounted(self):
        run = experiment_002_container.frozen_run("E002-C03-M")
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            workspace = root / "workspace"
            output = root / "output"
            credential = root / "credentials.toml"
            workspace.mkdir()
            output.mkdir()
            credential.write_text("placeholder\n")
            command = experiment_002_container.docker_command(
                run=run, workspace=workspace, output_dir=output,
                credential_file=credential, image="devin-e002:test",
                network="e002-internal", proxy_url="http://egress-proxy:3128",
            )
        self.assertIn("--permission-mode", command)
        self.assertEqual(command[command.index("--permission-mode") + 1], "dangerous")
        self.assertNotIn("--privileged", command)
        self.assertNotIn("/var/run/docker.sock", " ".join(command))
        self.assertNotIn(str(ROOT), " ".join(command))
        self.assertIn("--read-only", command)
        self.assertIn("--cap-drop", command)
        self.assertIn("ALL", command)
        self.assertNotIn(",rw", " ".join(command))
        self.assertIn("--model", command)
        self.assertIn("swe-2-medium", command)

    def test_runner_rejects_artifacts_inside_control_repo(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            workspace = root / "workspace"
            workspace.mkdir()
            (workspace / "TASK.md").write_text("task\n")
            credential = root / "credentials.toml"
            credential.write_text("placeholder\n")
            with self.assertRaises(SystemExit) as raised:
                experiment_002_container.main([
                    "--run-id", "E002-C03-M",
                    "--workspace", str(workspace),
                    "--output-dir", str(ROOT),
                    "--credential-file", str(credential),
                ])
            self.assertIn("artifact directory must be outside", str(raised.exception))

    def test_config_keeps_control_and_host_credential_mounts_false(self):
        config = json.loads(
            (ROOT / "manifests" / "experiment-002-config.json").read_text()
        )
        agent = config["agent"]
        self.assertFalse(agent["control_repository_mount"])
        self.assertFalse(agent["host_home_mount"])
        self.assertFalse(agent["docker_socket_mount"])
        self.assertFalse(agent["privileged"])
        self.assertEqual(agent["permission_mode"], "dangerous")
        self.assertEqual(agent["effective_permission_mode"], "Bypass")
        self.assertEqual(set(agent["network"]["allowlist"]), ALLOWED_HOSTS)


if __name__ == "__main__":
    unittest.main()
