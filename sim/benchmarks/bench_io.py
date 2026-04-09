"""
sim/benchmarks/io.py
====================
Uberbrain Benchmark — I/O and Artifact Management

Handles run directory creation, config/metrics/summary persistence,
and environment capture for full reproducibility.

License: CC0 — Public Domain
"""

from __future__ import annotations

import csv
import json
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


def make_run_dir(base_dir: str, run_id: str) -> str:
    """
    Create the output directory for a benchmark run.
    Returns the absolute path as a string.
    """
    path = Path(base_dir) / run_id
    path.mkdir(parents=True, exist_ok=True)
    return str(path)


def save_config(path: str, config: Dict[str, Any]) -> None:
    """
    Save the run config as JSON to path/config.json.
    Adds a timestamp and Python version for reproducibility.
    """
    out = {
        "saved_at": datetime.now(timezone.utc).isoformat(),
        "python": sys.version,
        "platform": platform.platform(),
        **config,
    }
    dest = Path(path) / "config.json"
    with open(dest, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, default=str)


def save_metrics_csv(path: str, rows: list[dict]) -> None:
    """
    Save a list of metric dicts as CSV to path/metrics.csv.
    All rows must have the same keys (first row defines fieldnames).
    """
    if not rows:
        return
    dest = Path(path) / "metrics.csv"
    fieldnames = list(rows[0].keys())
    with open(dest, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def save_summary_json(path: str, summary: Dict[str, Any]) -> None:
    """
    Save the benchmark summary as JSON to path/summary.json.
    This is the machine-readable pass/fail artifact.
    """
    dest = Path(path) / "summary.json"
    with open(dest, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, default=str)


def capture_environment(path: str) -> None:
    """
    Capture the full Python environment to path/environment.txt.
    Includes pip freeze, Python version, platform, and git SHA.
    """
    lines = [
        f"Captured: {datetime.now(timezone.utc).isoformat()}",
        f"Python: {sys.version}",
        f"Platform: {platform.platform()}",
        "",
        "=== pip freeze ===",
    ]

    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "freeze"],
            capture_output=True, text=True, timeout=30
        )
        lines.append(result.stdout)
    except Exception as e:
        lines.append(f"pip freeze failed: {e}")

    lines += ["", "=== git log ==="]
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", "-5"],
            capture_output=True, text=True, timeout=10
        )
        lines.append(result.stdout)
    except Exception as e:
        lines.append(f"git log failed: {e}")

    dest = Path(path) / "environment.txt"
    with open(dest, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def get_git_sha() -> str:
    """Return short git SHA, or 'unknown' if not in a git repo."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, timeout=10
        )
        return result.stdout.strip() or "unknown"
    except Exception:
        return "unknown"


def make_run_id(prefix: str = "") -> str:
    """Generate a timestamped run ID with git SHA."""
    date_str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    sha      = get_git_sha()
    parts    = [p for p in [prefix, date_str, sha] if p]
    return "_".join(parts)


def check_required_artifacts(run_dir: str) -> dict[str, bool]:
    """
    Verify all required artifact files exist after a run.
    Returns dict of filename → exists.
    """
    required = ["config.json", "metrics.csv", "summary.json", "environment.txt"]
    path     = Path(run_dir)
    return {f: (path / f).exists() for f in required}
