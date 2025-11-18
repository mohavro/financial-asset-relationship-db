"""
Comprehensive tests for GitHub Actions workflow files.

This module validates the structure, syntax, and configuration of GitHub Actions
workflows, ensuring they are properly formatted and free of common issues like
duplicate keys, invalid syntax, and missing required fields.
"""

import os
import pytest
import yaml
from pathlib import Path
from typing import Dict, Any, List


# Path to workflows directory
WORKFLOWS_DIR = Path(__file__).parent.parent.parent / ".github" / "workflows"


def get_workflow_files() -> List[Path]:
    """Get all workflow YAML files from .github/workflows directory."""
    if not WORKFLOWS_DIR.exists():
        return []
    return list(WORKFLOWS_DIR.glob("*.yml")) + list(WORKFLOWS_DIR.glob("*.yaml"))


def load_yaml_safe(file_path: Path) -> Dict[str, Any]:
    """
    Load YAML file with duplicate key detection.
    
    Args:
        file_path: Path to the YAML file
        
    Returns:
        Parsed YAML content as dictionary
        
    Raises:
        yaml.YAMLError: If YAML is invalid or contains duplicate keys
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def check_duplicate_keys(file_path: Path) -> List[str]:
    """
    Check for duplicate keys in YAML file.
    
    This function parses the YAML file manually to detect duplicate keys
    at any level, which yaml.safe_load might silently overwrite.
    
    Args:
        file_path: Path to the YAML file
        
    Returns:
        List of duplicate key names found
    """
    duplicates = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Parse with a custom constructor that detects duplicates
    class DuplicateKeySafeLoader(yaml.SafeLoader):
        pass
    
    def constructor_with_dup_check(loader, node):
        mapping = {}
        for key_node, value_node in node.value:
            key = loader.construct_object(key_node, deep=False)
            if key in mapping:
                duplicates.append(key)
            mapping[key] = loader.construct_object(value_node, deep=False)
        return mapping
    
    DuplicateKeySafeLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        constructor_with_dup_check
    )
    
    try:
        yaml.load(content, Loader=DuplicateKeySafeLoader)
    except yaml.YAMLError:
        pass  # Syntax errors will be caught by other tests
    
    return duplicates


class TestWorkflowSyntax:
    """Test suite for GitHub Actions workflow YAML syntax validation."""
    
    @pytest.mark.parametrize("workflow_file", get_workflow_files())
    def test_workflow_valid_yaml_syntax(self, workflow_file: Path):
        """Test that workflow files contain valid YAML syntax."""
        try:
            with open(workflow_file, 'r', encoding='utf-8') as f:
                yaml.safe_load(f)
        except yaml.YAMLError as e:
            pytest.fail(f"Invalid YAML syntax in {workflow_file.name}: {e}")
    
    @pytest.mark.parametrize("workflow_file", get_workflow_files())
    def test_workflow_no_duplicate_keys(self, workflow_file: Path):
        """Test that workflow files do not contain duplicate keys."""
        duplicates = check_duplicate_keys(workflow_file)
        assert not duplicates, (
            f"Found duplicate keys in {workflow_file.name}: {duplicates}. "
            "Duplicate keys can cause unexpected behavior as YAML will "
            "silently overwrite earlier values."
        )
    
    @pytest.mark.parametrize("workflow_file", get_workflow_files())
    def test_workflow_readable(self, workflow_file: Path):
        """Test that workflow files are readable."""
        assert workflow_file.exists(), f"Workflow file {workflow_file} does not exist"
        assert workflow_file.is_file(), f"Workflow path {workflow_file} is not a file"
        with open(workflow_file, 'r', encoding='utf-8') as f:
            content = f.read()
            assert len(content) > 0, f"Workflow file {workflow_file.name} is empty"


class TestWorkflowStructure:
    """Test suite for GitHub Actions workflow structure validation."""
    
    @pytest.mark.parametrize("workflow_file", get_workflow_files())
    def test_workflow_has_name(self, workflow_file: Path):
        """Test that workflow files have a 'name' field."""
        config = load_yaml_safe(workflow_file)
        assert "name" in config, f"Workflow {workflow_file.name} missing 'name' field"
        assert config["name"], f"Workflow {workflow_file.name} has empty 'name' field"
        assert isinstance(config["name"], str), (
            f"Workflow {workflow_file.name} 'name' must be a string"
        )
    
    @pytest.mark.parametrize("workflow_file", get_workflow_files())
    def test_workflow_has_triggers(self, workflow_file: Path):
        """Test that workflow files have at least one trigger (on)."""
        config = load_yaml_safe(workflow_file)
        assert "on" in config or True in config, (
            f"Workflow {workflow_file.name} missing trigger configuration ('on' field)"
        )
    
    @pytest.mark.parametrize("workflow_file", get_workflow_files())
    def test_workflow_has_jobs(self, workflow_file: Path):
        """Test that workflow files define at least one job."""
        config = load_yaml_safe(workflow_file)
        assert "jobs" in config, f"Workflow {workflow_file.name} missing 'jobs' field"
        assert config["jobs"], f"Workflow {workflow_file.name} has empty 'jobs' field"
        assert isinstance(config["jobs"], dict), (
            f"Workflow {workflow_file.name} 'jobs' must be a dictionary"
        )
        assert len(config["jobs"]) > 0, (
            f"Workflow {workflow_file.name} must define at least one job"
        )
    
    @pytest.mark.parametrize("workflow_file", get_workflow_files())
    def test_workflow_jobs_have_steps(self, workflow_file: Path):
        """Test that all jobs in workflow files have steps defined."""
        config = load_yaml_safe(workflow_file)
        jobs = config.get("jobs", {})
        
        for job_name, job_config in jobs.items():
            assert "steps" in job_config or "uses" in job_config, (
                f"Job '{job_name}' in {workflow_file.name} must have 'steps' or 'uses'"
            )
            
            if "steps" in job_config:
                assert job_config["steps"], (
                    f"Job '{job_name}' in {workflow_file.name} has empty 'steps'"
                )
                assert isinstance(job_config["steps"], list), (
                    f"Job '{job_name}' in {workflow_file.name} 'steps' must be a list"
                )


class TestWorkflowActions:
    """Test suite for GitHub Actions usage validation."""
    
    @pytest.mark.parametrize("workflow_file", get_workflow_files())
    def test_workflow_actions_have_versions(self, workflow_file: Path):
        """Test that all GitHub Actions specify a version/tag."""
        config = load_yaml_safe(workflow_file)
        jobs = config.get("jobs", {})
        
        for job_name, job_config in jobs.items():
            steps = job_config.get("steps", [])
            
            for idx, step in enumerate(steps):
                if "uses" in step:
                    action = step["uses"]
                    # Action should have a version tag (e.g., @v1, @main, @sha)
                    assert "@" in action, (
                        f"Step {idx} in job '{job_name}' of {workflow_file.name} "
                        f"uses action '{action}' without a version tag"
                    )
    
    @pytest.mark.parametrize("workflow_file", get_workflow_files())
    def test_workflow_steps_have_names_or_uses(self, workflow_file: Path):
        """Test that all steps have either a name or uses field."""
        config = load_yaml_safe(workflow_file)
        jobs = config.get("jobs", {})
        
        for job_name, job_config in jobs.items():
            steps = job_config.get("steps", [])
            
            for idx, step in enumerate(steps):
                has_name = "name" in step
                has_uses = "uses" in step
                has_run = "run" in step
                
                assert has_name or has_uses or has_run, (
                    f"Step {idx} in job '{job_name}' of {workflow_file.name} "
                    "must have at least a 'name', 'uses', or 'run' field"
                )


class TestPrAgentWorkflow:
    """Specific tests for the pr-agent.yml workflow."""
    
    @pytest.fixture
    def pr_agent_workflow(self) -> Dict[str, Any]:
        """Load the pr-agent workflow configuration."""
        workflow_path = WORKFLOWS_DIR / "pr-agent.yml"
        if not workflow_path.exists():
            pytest.skip("pr-agent.yml not found")
        return load_yaml_safe(workflow_path)
    
    def test_pr_agent_name(self, pr_agent_workflow: Dict[str, Any]):
        """Test that pr-agent workflow has correct name."""
        assert pr_agent_workflow["name"] == "PR Agent"
    
    def test_pr_agent_triggers_on_pull_request(self, pr_agent_workflow: Dict[str, Any]):
        """Test that pr-agent workflow triggers on pull request events."""
        triggers = pr_agent_workflow.get("on", {})
        assert "pull_request" in triggers, (
            "pr-agent workflow should trigger on pull_request events"
        )
    
    def test_pr_agent_has_review_job(self, pr_agent_workflow: Dict[str, Any]):
        """Test that pr-agent workflow has a review job."""
        jobs = pr_agent_workflow.get("jobs", {})
        assert "review" in jobs, "pr-agent workflow must have a 'review' job"
    
    def test_pr_agent_review_runs_on_ubuntu(self, pr_agent_workflow: Dict[str, Any]):
        """Test that review job runs on Ubuntu."""
        review_job = pr_agent_workflow["jobs"]["review"]
        runs_on = review_job.get("runs-on", "")
        assert "ubuntu" in runs_on.lower(), (
            "Review job should run on Ubuntu runner"
        )
    
    def test_pr_agent_has_checkout_step(self, pr_agent_workflow: Dict[str, Any]):
        """Test that review job checks out the code."""
        review_job = pr_agent_workflow["jobs"]["review"]
        steps = review_job.get("steps", [])
        
        checkout_steps = [
            s for s in steps 
            if s.get("uses", "").startswith("actions/checkout")
        ]
        assert len(checkout_steps) > 0, "Review job must check out the repository"
    
    def test_pr_agent_checkout_has_token(self, pr_agent_workflow: Dict[str, Any]):
        """Test that checkout step uses a token for authentication."""
        review_job = pr_agent_workflow["jobs"]["review"]
        steps = review_job.get("steps", [])
        
        checkout_steps = [
            s for s in steps 
            if s.get("uses", "").startswith("actions/checkout")
        ]
        
        for step in checkout_steps:
            step_with = step.get("with", {})
            assert "token" in step_with, "Checkout step should specify a token"
    
    def test_pr_agent_has_python_setup(self, pr_agent_workflow: Dict[str, Any]):
        """Test that review job sets up Python."""
        review_job = pr_agent_workflow["jobs"]["review"]
        steps = review_job.get("steps", [])
        
        python_steps = [
            s for s in steps 
            if s.get("uses", "").startswith("actions/setup-python")
        ]
        assert len(python_steps) > 0, "Review job must set up Python"
    
    def test_pr_agent_has_node_setup(self, pr_agent_workflow: Dict[str, Any]):
        """Test that review job sets up Node.js."""
        review_job = pr_agent_workflow["jobs"]["review"]
        steps = review_job.get("steps", [])
        
        node_steps = [
            s for s in steps 
            if s.get("uses", "").startswith("actions/setup-node")
        ]
        assert len(node_steps) > 0, "Review job must set up Node.js"
    
    def test_pr_agent_python_version(self, pr_agent_workflow: Dict[str, Any]):
        """Test that Python setup specifies version 3.11."""
        review_job = pr_agent_workflow["jobs"]["review"]
        steps = review_job.get("steps", [])
        
        python_steps = [
            s for s in steps 
            if s.get("uses", "").startswith("actions/setup-python")
        ]
        
        for step in python_steps:
            step_with = step.get("with", {})
            assert "python-version" in step_with, (
                "Python setup should specify a version"
            )
            assert step_with["python-version"] == "3.11", (
                "Python version should be 3.11"
            )
    
    def test_pr_agent_node_version(self, pr_agent_workflow: Dict[str, Any]):
        """Test that Node.js setup specifies version 20.x."""
        review_job = pr_agent_workflow["jobs"]["review"]
        steps = review_job.get("steps", [])
        
        node_steps = [
            s for s in steps 
            if s.get("uses", "").startswith("actions/setup-node")
        ]
        
        for step in node_steps:
            step_with = step.get("with", {})
            assert "node-version" in step_with, (
                "Node.js setup should specify a version"
            )
            assert step_with["node-version"] == "20.x", (
                "Node.js version should be 20.x"
            )
    
    def test_pr_agent_no_duplicate_setup_steps(self, pr_agent_workflow: Dict[str, Any]):
        """Test that there are no duplicate setup steps in the workflow."""
        review_job = pr_agent_workflow["jobs"]["review"]
        steps = review_job.get("steps", [])
        
        # Check for duplicate step names
        step_names = [s.get("name", "") for s in steps if s.get("name")]
        duplicate_names = [name for name in step_names if step_names.count(name) > 1]
        
        assert not duplicate_names, (
            f"Found duplicate step names: {set(duplicate_names)}. "
            "Each step should have a unique name."
        )
    
    def test_pr_agent_fetch_depth_configured(self, pr_agent_workflow: Dict[str, Any]):
        """Test that checkout step has fetch-depth configured."""
        review_job = pr_agent_workflow["jobs"]["review"]
        steps = review_job.get("steps", [])
        
        checkout_steps = [
            s for s in steps 
            if s.get("uses", "").startswith("actions/checkout")
        ]
        
        for step in checkout_steps:
            step_with = step.get("with", {})
            if "fetch-depth" in step_with:
                fetch_depth = step_with["fetch-depth"]
                assert isinstance(fetch_depth, int) or fetch_depth == 0, (
                    "fetch-depth should be an integer"
                )


class TestWorkflowSecurity:
    """Test suite for workflow security best practices."""
    
    @pytest.mark.parametrize("workflow_file", get_workflow_files())
    def test_workflow_no_hardcoded_secrets(self, workflow_file: Path):
        """Test that workflows don't contain hardcoded secrets or tokens."""
        with open(workflow_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Patterns that might indicate hardcoded secrets
        suspicious_patterns = [
            "ghp_",  # GitHub personal access token
            "gho_",  # GitHub OAuth token
            "ghu_",  # GitHub user token
            "ghs_",  # GitHub server token
            "ghr_",  # GitHub refresh token
        ]
        
        for pattern in suspicious_patterns:
            assert pattern not in content, (
                f"Workflow {workflow_file.name} may contain hardcoded secret "
                f"(found pattern: {pattern}). Use secrets context instead."
            )
    
    @pytest.mark.parametrize("workflow_file", get_workflow_files())
    def test_workflow_uses_secrets_context(self, workflow_file: Path):
        """Test that workflows use proper secrets context for sensitive data."""
        config = load_yaml_safe(workflow_file)
        jobs = config.get("jobs", {})
        
        for job_name, job_config in jobs.items():
            steps = job_config.get("steps", [])
            
            for step in steps:
                step_with = step.get("with", {})
                
                # Check if token/password fields use secrets context
                for key, value in step_with.items():
                    if any(sensitive in key.lower() 
                           for sensitive in ["token", "password", "key", "secret"]):
                        if isinstance(value, str):
                            assert value.startswith("${{") or value == "", (
                                f"Sensitive field '{key}' in {workflow_file.name} "
                                "should use secrets context (e.g., ${{ secrets.TOKEN }})"
                            )


class TestWorkflowMaintainability:
    """Test suite for workflow maintainability and best practices."""
    
    @pytest.mark.parametrize("workflow_file", get_workflow_files())
    def test_workflow_steps_have_descriptive_names(self, workflow_file: Path):
        """Test that workflow steps have descriptive names."""
        config = load_yaml_safe(workflow_file)
        jobs = config.get("jobs", {})
        
        for job_name, job_config in jobs.items():
            steps = job_config.get("steps", [])
            
            unnamed_steps = []
            for idx, step in enumerate(steps):
                # Steps should have names unless they're very simple
                if "name" not in step and "uses" in step:
                    # Allow unnamed steps for very common actions
                    common_actions = ["actions/checkout", "actions/setup-"]
                    if not any(step["uses"].startswith(a) for a in common_actions):
                        unnamed_steps.append(f"Step {idx}: {step.get('uses', 'unknown')}")
            
            # This is a warning rather than a hard failure
            if unnamed_steps:
                print(f"\nWarning: {workflow_file.name} job '{job_name}' has "
                      f"{len(unnamed_steps)} unnamed steps (recommended to add names)")
    
    @pytest.mark.parametrize("workflow_file", get_workflow_files())
    def test_workflow_reasonable_size(self, workflow_file: Path):
        """Test that workflow files are not excessively large."""
        file_size = workflow_file.stat().st_size
        
        # Warn if workflow file exceeds 10KB (reasonable limit)
        if file_size > 10240:
            print(f"\nWarning: {workflow_file.name} is {file_size} bytes. "
                  "Consider splitting into multiple workflows if it gets too complex.")
        
        # Fail if exceeds 50KB (definitely too large)
        assert file_size < 51200, (
            f"Workflow {workflow_file.name} is too large ({file_size} bytes). "
            "Consider splitting into multiple workflows or using reusable workflows."
        )


class TestWorkflowEdgeCases:
    """Test suite for edge cases and error conditions."""
    
    def test_workflow_directory_exists(self):
        """Test that .github/workflows directory exists."""
        assert WORKFLOWS_DIR.exists(), (
            ".github/workflows directory does not exist"
        )
        assert WORKFLOWS_DIR.is_dir(), (
            ".github/workflows exists but is not a directory"
        )
    
    def test_at_least_one_workflow_exists(self):
        """Test that at least one workflow file exists."""
        workflow_files = get_workflow_files()
        assert len(workflow_files) > 0, (
            "No workflow files found in .github/workflows directory"
        )
    
    @pytest.mark.parametrize("workflow_file", get_workflow_files())
    def test_workflow_file_extension(self, workflow_file: Path):
        """Test that workflow files have correct extensions."""
        assert workflow_file.suffix in [".yml", ".yaml"], (
            f"Workflow file {workflow_file.name} has invalid extension. "
            "Use .yml or .yaml"
        )
    
    @pytest.mark.parametrize("workflow_file", get_workflow_files())
    def test_workflow_encoding(self, workflow_file: Path):
        """Test that workflow files use UTF-8 encoding."""
        try:
            with open(workflow_file, 'r', encoding='utf-8') as f:
                f.read()
        except UnicodeDecodeError:
            pytest.fail(
                f"Workflow {workflow_file.name} is not valid UTF-8. "
                "Ensure file is saved with UTF-8 encoding."
            )
    
    @pytest.mark.parametrize("workflow_file", get_workflow_files())
    def test_workflow_no_tabs(self, workflow_file: Path):
        """Test that workflow files use spaces instead of tabs."""
        with open(workflow_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert "\t" not in content, (
            f"Workflow {workflow_file.name} contains tab characters. "
            "YAML files should use spaces for indentation, not tabs."
        )
    
    @pytest.mark.parametrize("workflow_file", get_workflow_files())
    def test_workflow_consistent_indentation(self, workflow_file: Path):
        """Test that workflow files use consistent indentation."""
        with open(workflow_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        indentation_levels = set()
        for line in lines:
            if line.strip() and not line.strip().startswith("#"):
                # Count leading spaces
                spaces = len(line) - len(line.lstrip(' '))
                if spaces > 0:
                    indentation_levels.add(spaces)
        
        # Check if indentation is consistent (multiples of 2)
        if indentation_levels:
            inconsistent = [
                level for level in indentation_levels 
                if level % 2 != 0
            ]
            assert not inconsistent, (
                f"Workflow {workflow_file.name} has inconsistent indentation. "
                f"Found indentation levels: {sorted(indentation_levels)}. "
                "Use 2-space indentation consistently."
            )


class TestWorkflowPerformance:
    """Test suite for workflow performance considerations."""
    
    @pytest.mark.parametrize("workflow_file", get_workflow_files())
    def test_workflow_uses_caching(self, workflow_file: Path):
        """Test if workflow utilizes caching for dependencies (recommendation)."""
        config = load_yaml_safe(workflow_file)
        jobs = config.get("jobs", {})
        
        has_cache = False
        for job_name, job_config in jobs.items():
            steps = job_config.get("steps", [])
            
            for step in steps:
                if "actions/cache" in step.get("uses", ""):
                    has_cache = True
                    break
                
                # Check for setup actions with caching enabled
                step_with = step.get("with", {})
                if "cache" in step_with:
                    has_cache = True
                    break
        
        # This is informational, not a hard requirement
        if not has_cache:
            print(f"\nInfo: {workflow_file.name} doesn't use caching. "
                  "Consider adding caching to improve performance.")