#!/usr/bin/env python3
"""Read-only allocated-space inventory of every immediate directory child."""

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys


def measure(path, du_command):
    """Do not follow links or cross mounted filesystems. Keep partial errors."""
    try:
        result = subprocess.run(
            [du_command, "-s", "-k", "-P", "-x", str(path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            errors="replace",
            env=dict(os.environ, LC_ALL="C"),
        )
    except OSError as error:
        return {"allocated_kib": None, "status": "unavailable", "error": str(error)}
    match = re.match(r"\s*(\d+)\s", result.stdout)
    kib = int(match.group(1)) if match else None
    status = "complete" if result.returncode == 0 and kib is not None else "unavailable"
    if result.returncode != 0 and kib is not None:
        status = "partial"
    return {
        "allocated_kib": kib,
        "status": status,
        "error": result.stderr.strip() or ("No size returned by du" if kib is None else None),
    }


def file_kind(mode):
    if stat.S_ISLNK(mode):
        return "symlink"
    if stat.S_ISDIR(mode):
        return "directory"
    if stat.S_ISREG(mode):
        return "file"
    return "special"


def inventory(root, du_command=None):
    root = Path(root).expanduser().resolve(strict=True)
    if not root.is_dir():
        raise ValueError("Target must be a directory")
    if root == Path(root.anchor):
        raise ValueError("Select a specific folder, not the filesystem root")
    du_command = du_command or shutil.which("du")
    if not du_command:
        raise ValueError("du is unavailable; use native file tools to measure disk usage")
    root_device = root.stat().st_dev
    # List first, so a failure does not silently become an empty inventory.
    with os.scandir(root) as listing:
        paths = sorted((Path(entry.path) for entry in listing), key=lambda path: path.name)
    entries = []
    for path in paths:
        row = {"path": str(path)}
        try:
            info = path.lstat()
            kind = file_kind(info.st_mode)
            row.update(
                kind=kind,
                logical_bytes=info.st_size if kind == "file" else None,
                hardlink_count=info.st_nlink if kind == "file" else None,
                identity={"device": info.st_dev, "inode": info.st_ino, "mtime_ns": info.st_mtime_ns},
            )
            if kind == "symlink":
                row["link_target"] = os.readlink(path)
            if info.st_dev != root_device:
                row.update(allocated_kib=None, status="skipped_mount", error="Different filesystem")
            else:
                row.update(measure(path, du_command))
        except OSError as error:
            row.update(kind="unknown", allocated_kib=None, status="unavailable", error=str(error))
        entries.append(row)
    entries.sort(key=lambda row: (row["allocated_kib"] is None, -(row["allocated_kib"] or 0), row["path"]))
    usage = shutil.disk_usage(root)
    return {
        "root": str(root),
        "root_usage": measure(root, du_command),
        "volume_free_bytes": usage.free,
        "entry_count": len(entries),
        "entries": entries,
        "notes": [
            "Read-only; includes hidden entries; directory sizes include descendants.",
            "Symlink targets and mounted filesystems are not traversed.",
            "allocated_kib is du's allocated-space estimate rounded to KiB, not logical file length.",
            "Child measurements can double-count hard links across entries; use root_usage for the root total.",
            "Clones, snapshots, compression, and concurrent writes prevent exact reclamation estimates.",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Folder to inventory (default: current directory)")
    args = parser.parse_args()
    try:
        report = inventory(args.root)
    except (OSError, ValueError) as error:
        json.dump({"status": "failed", "error": str(error)}, sys.stdout)
        sys.stdout.write("\n")
        return 1
    json.dump(report, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
