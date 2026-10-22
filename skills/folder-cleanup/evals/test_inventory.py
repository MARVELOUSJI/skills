"""Filesystem fixtures exercise measurement and scope, never real cleanup."""

import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "inventory.py"
SPEC = importlib.util.spec_from_file_location("folder_inventory", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class InventoryTests(unittest.TestCase):
    def test_all_children_hidden_names_nested_usage_and_read_only(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            names = [".hidden", "spaces and | pipe.txt", "line\nbreak.txt", "-dash.txt", "$(not-a-command).txt"]
            for name in names:
                (root / name).write_bytes(b"x" * 8192)
            (root / "outputs").mkdir()
            (root / "outputs" / "result.bin").write_bytes(b"y" * 32768)
            before = {str(path.relative_to(root)): path.read_bytes() for path in root.rglob("*") if path.is_file()}
            report = MODULE.inventory(root)
            rows = {Path(row["path"]).name: row for row in report["entries"]}
            self.assertEqual(set(rows), set(names + ["outputs"]))
            self.assertEqual(report["entry_count"], 6)
            self.assertTrue(all(Path(row["path"]).is_absolute() for row in report["entries"]))
            self.assertTrue(all(row["status"] == "complete" for row in report["entries"]))
            self.assertGreater(rows["outputs"]["allocated_kib"], rows[".hidden"]["allocated_kib"])
            after = {str(path.relative_to(root)): path.read_bytes() for path in root.rglob("*") if path.is_file()}
            self.assertEqual(before, after)

    def test_links_do_not_charge_or_read_external_targets(self):
        with tempfile.TemporaryDirectory() as folder, tempfile.TemporaryDirectory() as outside:
            root = Path(folder)
            payload = Path(outside) / "keep.bin"
            payload.write_bytes(b"z" * 1048576)
            (root / "external").symlink_to(outside, target_is_directory=True)
            (root / "broken").symlink_to(Path(outside) / "missing")
            report = MODULE.inventory(root)
            self.assertEqual(report["entry_count"], 2)
            for row in report["entries"]:
                self.assertEqual(row["kind"], "symlink")
                self.assertEqual(row["status"], "complete")
                self.assertLess(row["allocated_kib"], 1024)
                self.assertIn("link_target", row)
            self.assertEqual(payload.stat().st_size, 1048576)

    def test_partial_usage_preserves_error_and_is_not_zero(self):
        result = subprocess.CompletedProcess([], 1, "12\t/example\n", "du: Permission denied")
        with patch.object(MODULE.subprocess, "run", return_value=result):
            measurement = MODULE.measure(Path("/example"), "du")
        self.assertEqual(measurement["allocated_kib"], 12)
        self.assertEqual(measurement["status"], "partial")
        self.assertIn("Permission denied", measurement["error"])

    def test_failed_usage_is_unknown(self):
        result = subprocess.CompletedProcess([], 1, "", "du: cannot read")
        with patch.object(MODULE.subprocess, "run", return_value=result):
            measurement = MODULE.measure(Path("/example"), "du")
        self.assertIsNone(measurement["allocated_kib"])
        self.assertEqual(measurement["status"], "unavailable")

    def test_empty_folder_and_invalid_targets(self):
        with tempfile.TemporaryDirectory() as folder:
            report = MODULE.inventory(folder)
            self.assertEqual(report["entries"], [])
            file = Path(folder) / "file.txt"
            file.write_text("keep")
            with self.assertRaises(ValueError):
                MODULE.inventory(file)
        with self.assertRaises(ValueError):
            MODULE.inventory(Path("/"))
        with self.assertRaises(FileNotFoundError):
            MODULE.inventory(Path(folder) / "absent")


if __name__ == "__main__":
    unittest.main()
