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
    Determine whether the pytest-cov plugin is importable.
    
    Returns:
        bool: `True` if the `pytest-cov` plugin can be imported, `False` otherwise.
    """

    return importlib.util.find_spec("pytest_cov") is not None


def pytest_load_initial_conftests(args: List[str], early_config, parser) -> None:  # pragma: no cover - exercised via pytest
    """
    Remove coverage-related pytest command-line options from the provided argument list when the `pytest-cov` plugin is not available.
    
    If the `pytest-cov` plugin is present the function returns immediately. Otherwise it mutates `args` in place to remove `--cov` and `--cov-report` options, their following values (e.g. `--cov file`), and inline forms (`--cov=...`, `--cov-report=...`), preserving all other arguments.
     
    Parameters:
        args (List[str]): The initial pytest argument list; mutated in place to remove coverage options.
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