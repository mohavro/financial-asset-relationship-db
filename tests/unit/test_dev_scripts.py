"""Tests for development scripts and configuration files.

This module validates:
- Shell script syntax and structure
- Environment configuration
- Vercel deployment configuration
"""

import pytest
import json
import os


class TestVercelConfiguration:
    """Test Vercel deployment configuration."""
    
    def test_vercel_json_exists(self):
        """Test that vercel.json exists."""
        assert os.path.exists("vercel.json")
    
    def test_vercel_json_valid(self):
        """Test that vercel.json is valid JSON."""
        with open("vercel.json") as f:
            config = json.load(f)
        
        assert "builds" in config
        assert "routes" in config
    
    def test_vercel_builds_configuration(self):
        """Test Vercel builds are properly configured."""
        with open("vercel.json") as f:
            config = json.load(f)
        
        builds = config["builds"]
        assert len(builds) == 2
        
        # Check Python build
        python_build = next(b for b in builds if b["src"] == "api/main.py")
        assert python_build["use"] == "@vercel/python"
        assert "maxLambdaSize" in python_build["config"]
    
    def test_vercel_routes_configuration(self):
        """Test Vercel routes are properly configured."""
        with open("vercel.json") as f:
            config = json.load(f)
        
        routes = config["routes"]
        
        # Check API route
        api_route = next(r for r in routes if r["src"] == "/api/(.*)")
        assert api_route["dest"] == "api/main.py"


class TestEnvironmentConfiguration:
    """Test environment configuration."""
    
    def test_env_example_exists(self):
        """Test that .env.example exists."""
        assert os.path.exists(".env.example")
    
    def test_env_example_has_required_vars(self):
        """Test that .env.example contains required variables."""
        with open(".env.example") as f:
            content = f.read()
        
        assert "NEXT_PUBLIC_API_URL" in content
        assert "ALLOWED_ORIGINS" in content


class TestGitIgnore:
    """Test .gitignore configuration."""
    
    def test_gitignore_excludes_build_artifacts(self):
        """Test that .gitignore excludes build artifacts."""
        with open(".gitignore") as f:
            content = f.read()
        
        # Python artifacts
        assert "__pycache__" in content or "*.pyc" in content
        
        # Node.js artifacts
        assert "node_modules" in content
        assert ".next" in content
        
        # Environment files
        assert ".env.local" in content or ".env" in content
        
        # Vercel
        assert ".vercel" in content


class TestDocumentationFiles:
    """Test that documentation files exist and are properly structured."""
    
    @pytest.mark.parametrize("doc_file", [
        "README.md",
        "DEPLOYMENT.md",
        "INTEGRATION_SUMMARY.md",
        "ARCHITECTURE.md",
        "QUICK_START.md",
        "UI_COMPARISON.md",
        "VERCEL_DEPLOYMENT_CHECKLIST.md"
    ])
    def test_documentation_exists(self, doc_file):
        """Test that key documentation files exist."""
        assert os.path.exists(doc_file), f"Missing documentation: {doc_file}"
    
    def test_readme_has_quick_start(self):
        """Test README contains quick start section."""
        with open("README.md") as f:
            content = f.read()
        
        assert "Quick Start" in content or "Getting Started" in content
        assert "Installation" in content or "Setup" in content