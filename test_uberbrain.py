"""Convenience runner for beginners.

Usage:
  python test_uberbrain.py

This invokes pytest on tests/test_simulations.py so you don't need
pytest CLI syntax memorized.
"""

from __future__ import annotations

import sys


def main() -> int:
    try:
        import pytest
    except ModuleNotFoundError:
        print("pytest is not installed. Install it with: python -m pip install pytest")
        return 1

    return int(pytest.main(["-q", "tests/test_simulations.py"]))


if __name__ == "__main__":
    raise SystemExit(main())
