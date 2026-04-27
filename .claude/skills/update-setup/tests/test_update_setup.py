import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "update_setup.py"
spec = importlib.util.spec_from_file_location("update_setup", SCRIPT_PATH)
update_setup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(update_setup)


class UpdateSetupTests(unittest.TestCase):
    def test_scoped_files_skip_runtime_and_local_config(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for relative in [
                ".claude/skills/demo/SKILL.md",
                ".claude/agents/demo.md",
                ".claude/hooks/guards/demo.sh",
                ".claude/hooks/logs/commands.jsonl",
                ".claude/hooks/logs/.gitkeep",
                ".claude/settings.json",
                ".claude/settings.local.json",
                "CLAUDE.md",
            ]:
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("x", encoding="utf-8")

            files = update_setup.upstream_files(root)

            self.assertEqual(
                files,
                [
                    "agents/demo.md",
                    "hooks/guards/demo.sh",
                    "skills/demo/SKILL.md",
                ],
            )

    def test_scan_categorizes_new_disabled_modified_placeholder_and_conflict(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            upstream = base / "upstream"
            local = base / "local"
            manifest = local / ".claude/skills/update-setup/claudops-upstream.lock.json"

            self.write(upstream, ".claude/skills/new/SKILL.md", "new")
            self.write(upstream, ".claude/skills/disabled/SKILL.md", "disabled")
            self.write(upstream, ".claude/skills/modified/SKILL.md", "upstream v2")
            self.write(upstream, ".claude/skills/placeholder/SKILL.md", "Project: {{PROJECT_NAME}}\n")
            self.write(upstream, ".claude/skills/conflict/SKILL.md", "conflict upstream v2")

            self.write(local, ".claude/skills/disabled/SKILL.md.disabled", "old disabled")
            self.write(local, ".claude/skills/modified/SKILL.md", "local old")
            self.write(local, ".claude/skills/placeholder/SKILL.md", "Project: Acme\n")
            self.write(local, ".claude/skills/conflict/SKILL.md", "local customization")

            self.write_json(
                manifest,
                {
                    "upstream": {"commit": "old"},
                    "files": {
                        "skills/conflict/SKILL.md": {
                            "source_hash": update_setup.sha256_text("conflict upstream v1"),
                            "target_hash": update_setup.sha256_text("conflict old adopted"),
                            "status": "adopted",
                        },
                        "skills/removed/SKILL.md": {
                            "source_hash": "removed-source",
                            "target_hash": "removed-target",
                            "status": "adopted",
                        },
                    },
                },
            )

            report = update_setup.build_report(upstream, local, "abc123", manifest)
            statuses = {item["path"]: item["status"] for item in report["items"]}

            self.assertEqual(statuses["skills/new/SKILL.md"], "new")
            self.assertEqual(statuses["skills/disabled/SKILL.md"], "disabled")
            self.assertEqual(statuses["skills/modified/SKILL.md"], "modified")
            self.assertEqual(statuses["skills/placeholder/SKILL.md"], "placeholder_only")
            self.assertEqual(statuses["skills/conflict/SKILL.md"], "conflicting")
            self.assertEqual(statuses["skills/removed/SKILL.md"], "removed")

    def test_apply_selection_updates_files_disabled_and_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            upstream = base / "upstream"
            local = base / "local"
            manifest = local / ".claude/skills/update-setup/claudops-upstream.lock.json"
            selection = base / "selection.json"

            self.write(upstream, ".claude/skills/new/SKILL.md", "new")
            self.write(upstream, ".claude/skills/disabled/SKILL.md", "disabled v2")
            self.write(local, ".claude/skills/disabled/SKILL.md.disabled", "disabled v1")
            report = update_setup.build_report(upstream, local, "abc123", manifest)
            self.write_json(
                selection,
                {
                    "update": ["skills/new/SKILL.md"],
                    "refresh_disabled": ["skills/disabled/SKILL.md"],
                    "delete": [],
                },
            )

            result = update_setup.apply_selection(report, selection, local, manifest)

            self.assertEqual(result["updated"], 1)
            self.assertEqual(result["disabled_refreshed"], 1)
            self.assertEqual(
                (local / ".claude/skills/new/SKILL.md").read_text(encoding="utf-8"),
                "new",
            )
            self.assertEqual(
                (local / ".claude/skills/disabled/SKILL.md.disabled").read_text(encoding="utf-8"),
                "disabled v2",
            )
            lock = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertEqual(lock["upstream"]["commit"], "abc123")
            self.assertEqual(lock["files"]["skills/new/SKILL.md"]["status"], "adopted")

    def test_verify_detects_manifest_hash_drift(self):
        with tempfile.TemporaryDirectory() as tmp:
            local = Path(tmp)
            manifest = local / ".claude/skills/update-setup/claudops-upstream.lock.json"
            self.write(local, ".claude/skills/demo/SKILL.md", "changed")
            self.write_json(
                manifest,
                {
                    "files": {
                        "skills/demo/SKILL.md": {
                            "target_hash": update_setup.sha256_text("original"),
                            "status": "adopted",
                        }
                    }
                },
            )

            result = update_setup.verify(local, manifest)

            self.assertEqual(len(result["errors"]), 1)
            self.assertIn("hash mismatch", result["errors"][0])

    def write(self, root, relative, content):
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def write_json(self, path, data):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
