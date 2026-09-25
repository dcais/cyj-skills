import json
from pathlib import Path
import subprocess
import sys
import tempfile
import tomllib
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import install as router


class InstallTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="codex router 测试 ")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.home = self.root / "custom home"

    def mapping(self, model="future-model"):
        data = router.load_mapping(router.PACKAGE / "skill/models.json")
        data["tiers"]["standard"]["model"] = model
        path = self.root / "mapping.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        return path

    def test_dry_run_does_not_create_home(self):
        result = router.install(self.home, dry_run=True)
        self.assertEqual(len(result["changed_files"]), 7)
        self.assertFalse(self.home.exists())

    def test_install_custom_mapping_and_repeat(self):
        result = router.install(self.home, self.mapping())
        self.assertEqual(len(result["changed_files"]), 7)
        role = tomllib.loads((self.home / "agents/codex-router-standard.toml").read_text())
        self.assertEqual(role["model"], "future-model")
        self.assertEqual(role["name"], "codex-router-standard")
        self.assertEqual(router.install(self.home)["changed_files"], [])
        installed = router.load_mapping(self.home / "skills/codex-model-router/models.json")
        self.assertEqual(installed["tiers"]["standard"]["model"], "future-model")

    def test_preserves_existing_config_and_backs_up_agents(self):
        self.home.mkdir()
        config = self.home / "config.toml"
        config.write_bytes(b'model = "user-selected-model"\r\n')
        agents = self.home / "AGENTS.md"
        original = b"\xef\xbb\xbf# Personal instructions\r\nKeep this exactly.\r\n"
        agents.write_bytes(original)
        result = router.install(self.home)
        self.assertTrue(agents.read_bytes().startswith(original))
        self.assertEqual((Path(result["backup"]) / "AGENTS.md").read_bytes(), original)
        self.assertEqual(config.read_bytes(), b'model = "user-selected-model"\r\n')
        after = agents.read_bytes()
        self.assertEqual(router.install(self.home)["changed_files"], [])
        self.assertEqual(after, agents.read_bytes())

    def test_explicit_update_backs_up_previous_mapping_and_role(self):
        router.install(self.home)
        role_path = self.home / "agents/codex-router-standard.toml"
        before = role_path.read_bytes()
        result = router.install(self.home, self.mapping())
        self.assertEqual(len(result["changed_files"]), 2)
        self.assertEqual((Path(result["backup"]) / role_path.relative_to(self.home)).read_bytes(), before)
        self.assertEqual(tomllib.loads(role_path.read_text())["model"], "future-model")

    def test_invalid_mapping_and_markers_do_not_write(self):
        invalid = self.mapping('bad"\ninjected = true')
        with self.assertRaises(ValueError):
            router.install(self.home, invalid)
        self.assertFalse(self.home.exists())
        self.home.mkdir()
        agents = self.home / "AGENTS.md"
        original = router.START.encode()
        agents.write_bytes(original)
        with self.assertRaises(ValueError):
            router.install(self.home)
        self.assertEqual(agents.read_bytes(), original)
        self.assertFalse((self.home / "skills").exists())

    def test_existing_block_updates_only_managed_bytes(self):
        original = b"before\r\n" + router.START.encode() + b"\r\nold\r\n" + router.END.encode() + b"\r\nafter\r\n"
        changed = router.update_entry(original, self.home / "skills/codex-model-router/SKILL.md")
        self.assertTrue(changed.startswith(b"before\r\n"))
        self.assertTrue(changed.endswith(b"\r\nafter\r\n"))
        self.assertNotIn(b"\r\nold\r\n", changed)

    def test_write_failure_rolls_back_installed_files(self):
        router.install(self.home)
        skill = self.home / "skills/codex-model-router/SKILL.md"
        skill.write_bytes(b"previous local skill")
        before = {p.relative_to(self.home): p.read_bytes() for p in self.home.rglob("*") if p.is_file()}
        real_write = router.write_atomic
        def fail_once(path, data):
            if path == self.home / "agents/codex-router-standard.toml" and b"future-model" in data:
                raise OSError("simulated disk write failure")
            return real_write(path, data)
        with patch.object(router, "write_atomic", side_effect=fail_once):
            with self.assertRaises(OSError):
                router.install(self.home, self.mapping())
        for relative, contents in before.items():
            self.assertEqual((self.home / relative).read_bytes(), contents)

    def test_linked_target_rejected_without_touching_external_file(self):
        self.home.mkdir()
        external = self.root / "external.md"
        external.write_bytes(b"untouched")
        try:
            (self.home / "AGENTS.md").symlink_to(external)
        except OSError:
            self.skipTest("Creating symlinks is not permitted on this host")
        with self.assertRaises(ValueError):
            router.install(self.home)
        self.assertEqual(external.read_bytes(), b"untouched")

    def test_legacy_install_is_reported_and_preserved(self):
        legacy = self.home / "skills/model-router/SKILL.md"
        legacy.parent.mkdir(parents=True)
        legacy.write_bytes(b"legacy")
        result = router.install(self.home)
        self.assertIn("legacy_notice", result)
        self.assertEqual(legacy.read_bytes(), b"legacy")

    def test_cli_respects_codex_home_and_dry_run(self):
        import os
        env = dict(os.environ, CODEX_HOME=str(self.home))
        result = subprocess.run([sys.executable, str(router.PACKAGE / "install.py"), "--dry-run"],
                                env=env, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(Path(report["codex_home"]), self.home)
        self.assertFalse(self.home.exists())


if __name__ == "__main__":
    unittest.main()
