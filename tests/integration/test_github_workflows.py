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
    """
    Return all workflow YAML files located in the .github/workflows directory.
    
    Returns:
        List[Path]: Paths to files with `.yml` or `.yaml` extension found in the workflows directory.
                    Returns an empty list if the directory does not exist or no matching files are present.
    """
    if not WORKFLOWS_DIR.exists():
        return []
    return list(WORKFLOWS_DIR.glob("*.yml")) + list(WORKFLOWS_DIR.glob("*.yaml"))


def load_yaml_safe(file_path: Path) -> Dict[str, Any]:
    """
    Load and parse a YAML file.
    
    Parameters:
        file_path (Path): Path to the YAML file to load.
    
    Returns:
        dict: Parsed YAML content as a mapping.
    
    Raises:
        yaml.YAMLError: If the file contains invalid YAML.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def check_duplicate_keys(file_path: Path) -> List[str]:
    """
    Detect duplicate mapping keys in a YAML file.
    
    Parameters:
        file_path (Path): Path to the YAML file to inspect.
    
    Returns:
        List of duplicate key names found, or an empty list if none are present.
    """
    duplicates = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Parse with a custom constructor that detects duplicates
    class DuplicateKeySafeLoader(yaml.SafeLoader):
        pass
    
    def constructor_with_dup_check(loader, node):
        """
        Construct a Python dict from a YAML mapping node and record any duplicate keys.
        
        Parameters:
            loader: YAML loader used to construct key and value objects from nodes.
            node: YAML mapping node whose key/value pairs will be converted into a dict.
        
        Returns:
            mapping (dict): A dictionary of keys to constructed values from the mapping node.
        
        Notes:
            Any duplicate mapping keys encountered are appended to the surrounding `duplicates` list.
        """
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
        """
        Ensure the workflow YAML defines a non-empty string in the top-level "name" field.
        
        Asserts that the top-level "name" key exists, its value is not empty, and the value is a string. Failure messages include the workflow filename for context.
        """
        config = load_yaml_safe(workflow_file)
        assert "name" in config, f"Workflow {workflow_file.name} missing 'name' field"
        assert config["name"], f"Workflow {workflow_file.name} has empty 'name' field"
        assert isinstance(config["name"], str), (
            f"Workflow {workflow_file.name} 'name' must be a string"
        )
    
    @pytest.mark.parametrize("workflow_file", get_workflow_files())
    def test_workflow_has_triggers(self, workflow_file: Path):
        """
        Ensure the workflow defines at least one trigger by including an "on" field.
        
        Fails the test if the parsed workflow configuration does not contain a top-level 'on' key.
        """
        config = load_yaml_safe(workflow_file)
        assert "on" in config or True in config, (
            f"Workflow {workflow_file.name} missing trigger configuration ('on' field)"
        )
    
    @pytest.mark.parametrize("workflow_file", get_workflow_files())
    def test_workflow_has_jobs(self, workflow_file: Path):
        """
        Assert that a GitHub Actions workflow defines at least one job.
        
        Checks that the top-level "jobs" key exists in the parsed workflow, that its value is a mapping (dictionary) and that it contains at least one job entry.
        
        Parameters:
            workflow_file (Path): Path to the workflow YAML file under test.
        """
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
        """
        Verify each job in the workflow defines either 'steps' or 'uses', and that any 'steps' entry is a non-empty list.
        
        If a job has a 'steps' key it must be a list with at least one element.
        """
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
        """
        Ensure every step in each job defines at least one of: 'name', 'uses' or 'run'.
        
        Parameters:
            workflow_file (Path): Path to the workflow YAML file to validate.
        """
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
        """
        Fixture that loads the pr-agent workflow YAML and provides its parsed mapping.
        
        If the file .github/workflows/pr-agent.yml does not exist, the fixture skips the invoking test.
        Returns:
            workflow (Dict[str, Any]): Parsed YAML content of the pr-agent workflow as a mapping.
        """
        workflow_path = WORKFLOWS_DIR / "pr-agent.yml"
        if not workflow_path.exists():
            pytest.skip("pr-agent.yml not found")
        return load_yaml_safe(workflow_path)
    
    def test_pr_agent_name(self, pr_agent_workflow: Dict[str, Any]):
        """
        Verify the pr-agent workflow is named "PR Agent".
        
        Parameters:
            pr_agent_workflow (Dict[str, Any]): Parsed YAML mapping for the pr-agent workflow (fixture providing the workflow content).
        """
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
        """
        Ensure every actions/checkout step in the review job provides a `token` in its `with` mapping.
        
        Fails the test if any checkout step omits the `token` key.
        """
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
        """
        Ensure every actions/setup-node step in the pr-agent 'review' job specifies Node.js version 20.x.
        
        Checks each step that uses 'actions/setup-node' has a 'with' mapping containing a 'node-version' key whose value equals '20.x'.
        """
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
        """
        Validate fetch-depth values for actions/checkout steps in the PR Agent review job.
        
        For each checkout step in the review job, if a `fetch-depth` key is present assert it is an integer or equal to 0.
        """
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
        """
        Ensure sensitive fields in step 'with' blocks use the GitHub secrets context.
        
        Scans each job's steps for keys containing "token", "password", "key" or "secret". If a matching key has a string value, assert that the value either starts with "${{" (secrets context) or is empty.
        """
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
        """
        Check that steps within each job of a workflow have descriptive names and warn when they do not.
        
        Scans the workflow YAML at `workflow_file` and for each job examines its `steps`. If a step uses an action and lacks a `name`, a warning is printed unless the action is one of a small set of common actions exempted from naming (for example `actions/checkout` and `actions/setup-*`).
        
        Parameters:
            workflow_file (Path): Path to the workflow YAML file being checked.
        """
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
        """
        Verify that a workflow file uses the .yml or .yaml extension.
        
        Parameters:
        	workflow_file (Path): Path to the workflow file being tested.
        """
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
        """
        Ensure the workflow YAML file does not contain tab characters.
        
        Fails the test if any tab character is present in the file, because YAML indentation must use spaces.
        """
        with open(workflow_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert "\t" not in content, (
            f"Workflow {workflow_file.name} contains tab characters. "
            "YAML files should use spaces for indentation, not tabs."
        )
    
    @pytest.mark.parametrize("workflow_file", get_workflow_files())
    def test_workflow_consistent_indentation(self, workflow_file: Path):
        """
        Verify that non-empty, non-comment lines in the workflow file use consistent 2-space indentation.
        
        Reads the file and collects leading-space counts for all non-empty, non-comment lines; the test fails if any indentation level is not a multiple of 2.
        """
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
        """
        Check whether the workflow uses caching and report if none is detected.
        
        Scans the workflow's jobs and steps for common caching indicators (for example an `actions/cache` action or a `cache` key in a step's `with` block). Prints an informational message when no caching is found; this check is advisory and does not cause the test to fail.
        """
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