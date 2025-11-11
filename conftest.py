"""Pytest configuration helpers for the repository.

This module removes optional coverage-related command line arguments when the
``pytest-cov`` plugin is not installed. Some environments (for example, local
developer shells or CI configurations) may inject coverage options via
``PYTEST_ADDOPTS``. Without ``pytest-cov`` those options cause pytest to fail
before executing any tests. By trimming the coverage options when the plugin is
missing we allow the default test command to succeed while still preserving
coverage reporting where the dependency is available.
"""

from __future__ import annotations

import importlib.util
from typing import List


def _cov_plugin_available() -> bool:
    """
    Check whether the pytest-cov plugin is importable.
    
    Returns:
        bool: `True` if the `pytest-cov` plugin can be imported, `False` otherwise.
    """

    return importlib.util.find_spec("pytest_cov") is not None


def pytest_load_initial_conftests(args: List[str], early_config, parser) -> None:  # pragma: no cover - exercised via pytest
    """
    Remove pytest-cov related CLI options from the provided args list when the pytest-cov plugin is not installed.
    
    If the pytest-cov plugin is unavailable, this hook filters out coverage flags so pytest can run without the plugin. It removes both combined forms (`--cov=...`, `--cov-report=...`) and separate-option forms (`--cov <path>`, `--cov-report <format>`). The original `args` list is mutated in place.
    
    Parameters:
        args (List[str]): The list of pytest command-line arguments to filter; modified in place.
    """

    if _cov_plugin_available():
        return

    filtered_args: List[str] = []
    skip_next = False

    for arg in args:
        if skip_next:
            skip_next = False
            continue

        if arg in {"--cov", "--cov-report"}:
            skip_next = True
            continue

        if arg.startswith("--cov=") or arg.startswith("--cov-report="):
            continue

        filtered_args.append(arg)

    args[:] = filtered_args