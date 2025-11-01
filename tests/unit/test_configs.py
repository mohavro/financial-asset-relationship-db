"""Unit tests for validating configuration files."""

import json
import json
import json


def test_vercel_json_valid():
    """Test that vercel.json is valid JSON."""
    with open("vercel.json") as f:
        config = json.load(f)
    assert "builds" in config
    assert "routes" in config


def test_package_json_valid():
    """Test that package.json is valid JSON."""
    with open("frontend/package.json") as f:
        config = json.load(f)
    assert "dependencies" in config
    assert "next" in config["dependencies"]


def test_tsconfig_json_valid():
    """Test that tsconfig.json is valid JSON."""
    with open("frontend/tsconfig.json") as f:
        config = json.load(f)
    assert "compilerOptions" in config