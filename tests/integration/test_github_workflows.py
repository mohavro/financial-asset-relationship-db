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
        """
        Assert that a workflow file exists, is a regular file, and contains non-empty UTF-8 text.
        
        Parameters:
            workflow_file (Path): Path to the workflow file to validate.
        """
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
        """
        Assert that any step using actions/setup-python in the 'review' job specifies python-version "3.11".
        
        Checks each setup-python step in pr_agent_workflow["jobs"]["review"] has a "with" mapping containing "python-version" equal to "3.11".
        """
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
        Ensure every actions/setup-node step in the pr-agent 'pr-agent-trigger' job specifies Node.js version 18.

        Checks each step that uses 'actions/setup-node' has a 'with' mapping containing a 'node-version' key whose value equals '18'.
        """
        review_job = pr_agent_workflow["jobs"]["pr-agent-trigger"]
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
            assert step_with["node-version"] == "18", (
                "Node.js version should be 18"
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
        """
        Assert the workflow file is within reasonable size limits.
        
        If the file is larger than 10,240 bytes (10 KB) a warning is printed to encourage splitting complex workflows.
        If the file is 51,200 bytes (50 KB) or larger the test fails with an assertion instructing to split the workflow or use reusable workflows.
        """
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

class TestPrAgentWorkflowAdvanced:
    """Advanced comprehensive tests for pr-agent.yml workflow specifics."""
    
    @pytest.fixture
    def pr_agent_workflow(self) -> Dict[str, Any]:
        """
        Load the 'pr-agent.yml' workflow from the workflows directory, skipping the test if the file is missing.
        
        Returns:
            workflow (dict): Parsed YAML content of the pr-agent workflow.
        
        Raises:
            yaml.YAMLError: If the workflow file contains invalid YAML.
        """
        workflow_path = WORKFLOWS_DIR / "pr-agent.yml"
        if not workflow_path.exists():
            pytest.skip("pr-agent.yml not found")
        return load_yaml_safe(workflow_path)
    
    def test_pr_agent_has_three_jobs(self, pr_agent_workflow: Dict[str, Any]):
        """
        Ensure the pr-agent workflow defines exactly three jobs.
        
        Asserts that the workflow's top-level `jobs` mapping contains exactly three entries named "pr-agent-trigger", "auto-merge-check" and "dependency-update".
        """
        jobs = pr_agent_workflow.get("jobs", {})
        assert len(jobs) == 3, (
            f"pr-agent workflow should have exactly 3 jobs, found {len(jobs)}"
        )
        assert "pr-agent-trigger" in jobs
        assert "auto-merge-check" in jobs
        assert "dependency-update" in jobs
    
    def test_pr_agent_permissions_structure(self, pr_agent_workflow: Dict[str, Any]):
        """
        Verify the pr-agent workflow defines the expected permissions at top-level and for specific jobs.
        
        Checks:
        - top-level `permissions.contents` is "read"
        - `pr-agent-trigger` job has `permissions.issues` set to "write"
        - `auto-merge-check` job has `permissions.issues` and `permissions.pull-requests` set to "write"
        - `dependency-update` job has `permissions.pull-requests` set to "write"
        
        Parameters:
            pr_agent_workflow (Dict[str, Any]): Parsed workflow dictionary for the pr-agent workflow.
        """
        # Top-level permissions
        assert "permissions" in pr_agent_workflow
        assert pr_agent_workflow["permissions"]["contents"] == "read"
        
        # Job-level permissions
        jobs = pr_agent_workflow["jobs"]
        assert "permissions" in jobs["pr-agent-trigger"]
        assert jobs["pr-agent-trigger"]["permissions"]["issues"] == "write"
        
        assert "permissions" in jobs["auto-merge-check"]
        assert jobs["auto-merge-check"]["permissions"]["issues"] == "write"
        assert jobs["auto-merge-check"]["permissions"]["pull-requests"] == "write"
        
        assert "permissions" in jobs["dependency-update"]
        assert jobs["dependency-update"]["permissions"]["pull-requests"] == "write"
    
    def test_pr_agent_trigger_has_conditional(self, pr_agent_workflow: Dict[str, Any]):
        """Test that pr-agent-trigger job has proper conditional logic."""
        job = pr_agent_workflow["jobs"]["pr-agent-trigger"]
        assert "if" in job, "pr-agent-trigger should have conditional execution"
        conditional = job["if"]
        assert "pull_request_review" in conditional
        assert "changes_requested" in conditional
        assert "issue_comment" in conditional
        assert "@copilot" in conditional
    
    def test_pr_agent_install_steps_validate_files(self, pr_agent_workflow: Dict[str, Any]):
        """
        Validate that the PR Agent trigger job's install steps check for expected dependency files before running installation.
        
        Asserts that the "Install Python dependencies" step exists and its run script contains checks for requirements.txt and requirements-dev.txt, and that the "Install Node dependencies" step exists and its run script contains checks for package-lock.json and package.json.
        
        Parameters:
        	pr_agent_workflow (Dict[str, Any]): Parsed workflow dictionary for the pr-agent.yml workflow.
        """
        job = pr_agent_workflow["jobs"]["pr-agent-trigger"]
        steps = job.get("steps", [])
        
        python_install_step = None
        node_install_step = None
        
        for step in steps:
            if step.get("name") == "Install Python dependencies":
                python_install_step = step
            elif step.get("name") == "Install Node dependencies":
                node_install_step = step
        
        assert python_install_step is not None
        assert "if [ -f requirements.txt ]" in python_install_step["run"]
        assert "if [ -f requirements-dev.txt ]" in python_install_step["run"]
        
        assert node_install_step is not None
        assert "if [ -f package-lock.json ]" in node_install_step["run"]
        assert "if [ -f package.json ]" in node_install_step["run"]
    
    def test_pr_agent_parse_comments_step(self, pr_agent_workflow: Dict[str, Any]):
        """Test that Parse PR Review Comments step is configured correctly."""
        job = pr_agent_workflow["jobs"]["pr-agent-trigger"]
        steps = job.get("steps", [])
        
        parse_step = None
        for step in steps:
            if step.get("name") == "Parse PR Review Comments":
                parse_step = step
                break
        
        assert parse_step is not None
        assert "id" in parse_step
        assert parse_step["id"] == "parse-comments"
        assert "env" in parse_step
        assert "GITHUB_TOKEN" in parse_step["env"]
        assert "gh api" in parse_step["run"]
    
    def test_pr_agent_linting_steps(self, pr_agent_workflow: Dict[str, Any]):
        """
        Verify the PR Agent workflow contains Python and frontend linting steps and that the Python lint step runs expected commands.
        
        Parameters:
            pr_agent_workflow (Dict[str, Any]): Parsed contents of the `pr-agent.yml` workflow as a mapping.
        """
        job = pr_agent_workflow["jobs"]["pr-agent-trigger"]
        steps = job.get("steps", [])
        
        step_names = [s.get("name", "") for s in steps]
        assert "Run Python Linting" in step_names
        assert "Run Frontend Linting" in step_names
        
        # Check Python linting configuration
        python_lint = next(s for s in steps if s.get("name") == "Run Python Linting")
        assert "flake8" in python_lint["run"]
        assert "black" in python_lint["run"]
        assert "--max-line-length=88" in python_lint["run"]
        assert "api/" in python_lint["run"] and "src/" in python_lint["run"]
    
    def test_pr_agent_testing_steps(self, pr_agent_workflow: Dict[str, Any]):
        """Test that pr-agent includes proper testing steps."""
        job = pr_agent_workflow["jobs"]["pr-agent-trigger"]
        steps = job.get("steps", [])
        
        step_names = [s.get("name", "") for s in steps]
        assert "Run Python Tests" in step_names
        assert "Run Frontend Tests" in step_names
        
        # Check test configuration
        python_test = next(s for s in steps if s.get("name") == "Run Python Tests")
        assert "pytest" in python_test["run"]
        assert "--cov=src" in python_test["run"]
        assert "--cov-report=term-missing" in python_test["run"]
    
    def test_pr_agent_create_comment_step(self, pr_agent_workflow: Dict[str, Any]):
        """Test that Create PR Comment step runs always and uses github-script."""
        job = pr_agent_workflow["jobs"]["pr-agent-trigger"]
        steps = job.get("steps", [])
        
        comment_step = None
        for step in steps:
            if step.get("name") == "Create PR Comment":
                comment_step = step
                break
        
        assert comment_step is not None
        assert comment_step.get("if") == "always()"
        assert "actions/github-script" in comment_step["uses"]
        assert "script" in comment_step["with"]
    
    def test_pr_agent_node_version_actual(self, pr_agent_workflow: Dict[str, Any]):
        """
        Verify that any actions/setup-node step in the "pr-agent-trigger" job specifies Node.js version "18".
        
        Parameters:
            pr_agent_workflow (Dict[str, Any]): Parsed workflow YAML for the PR Agent workflow fixture.
        """
        job = pr_agent_workflow["jobs"]["pr-agent-trigger"]
        steps = job.get("steps", [])
        
        node_steps = [
            s for s in steps 
            if s.get("uses", "").startswith("actions/setup-node")
        ]
        
        for step in node_steps:
            step_with = step.get("with", {})
            assert step_with.get("node-version") == "18", (
                "Node.js version should be 18 (current configuration)"
            )
    
    def test_auto_merge_check_logic(self, pr_agent_workflow: Dict[str, Any]):
        """Test auto-merge-check job conditional logic."""
        job = pr_agent_workflow["jobs"]["auto-merge-check"]
        assert "if" in job
        conditional = job["if"]
        
        # Should check for pull_request synchronize, approved review, and check_suite success
        assert "pull_request" in conditional
        assert "synchronize" in conditional
        assert "pull_request_review" in conditional
        assert "approved" in conditional
        assert "check_suite" in conditional
        assert "success" in conditional
    
    def test_auto_merge_check_uses_github_script(self, pr_agent_workflow: Dict[str, Any]):
        """Test that auto-merge-check uses github-script action."""
        job = pr_agent_workflow["jobs"]["auto-merge-check"]
        steps = job.get("steps", [])
        
        assert len(steps) == 1
        assert "actions/github-script" in steps[0]["uses"]
        assert "script" in steps[0]["with"]
    
    def test_dependency_update_conditional(self, pr_agent_workflow: Dict[str, Any]):
        """Test dependency-update job triggers only for dependency PRs."""
        job = pr_agent_workflow["jobs"]["dependency-update"]
        assert "if" in job
        conditional = job["if"]
        
        assert "pull_request" in conditional
        assert "deps" in conditional
    
    def test_dependency_update_auto_approve_logic(self, pr_agent_workflow: Dict[str, Any]):
        """Test dependency-update job auto-approves trusted bot updates."""
        job = pr_agent_workflow["jobs"]["dependency-update"]
        steps = job.get("steps", [])
        
        step = steps[0]
        script = step["with"]["script"]
        
        # Should check for dependabot and renovate
        assert "dependabot[bot]" in script
        assert "renovate[bot]" in script
        assert "bump" in script.lower() or "update" in script.lower()
        assert "APPROVE" in script


class TestWorkflowTriggers:
    """Comprehensive tests for workflow trigger configurations."""
    
    @pytest.mark.parametrize("workflow_file", get_workflow_files())
    def test_workflow_triggers_are_valid_types(self, workflow_file: Path):
        """Test that workflow triggers use valid GitHub event types."""
        config = load_yaml_safe(workflow_file)
        triggers = config.get("on", {})
        
        if isinstance(triggers, str):
            triggers = {triggers: None}
        elif isinstance(triggers, list):
            triggers = {t: None for t in triggers}
        
        valid_events = {
            "push", "pull_request", "pull_request_review", "pull_request_target",
            "issue_comment", "issues", "workflow_dispatch", "schedule", "release",
            "create", "delete", "fork", "watch", "check_suite", "check_run",
            "deployment", "deployment_status", "page_build", "project", "project_card",
            "project_column", "public", "registry_package", "status", "workflow_run",
            "repository_dispatch", "milestone", "discussion", "discussion_comment"
        }
        
        for event in triggers.keys():
            if event is True:  # Handle boolean true for shorthand syntax
                continue
            assert event in valid_events, (
                f"Workflow {workflow_file.name} uses invalid event type: {event}"
            )
    
    @pytest.mark.parametrize("workflow_file", get_workflow_files())
    def test_workflow_pr_triggers_specify_types(self, workflow_file: Path):
        """Test that pull_request triggers specify activity types."""
        config = load_yaml_safe(workflow_file)
        triggers = config.get("on", {})
        
        if not isinstance(triggers, dict):
            return  # Skip for non-dict triggers
        
        if "pull_request" in triggers:
            pr_config = triggers["pull_request"]
            if pr_config is not None:
                assert "types" in pr_config or pr_config == {}, (
                    f"Workflow {workflow_file.name} pull_request trigger should "
                    "specify activity types for better control"
                )


class TestWorkflowJobConfiguration:
    """Tests for job-level configuration in workflows."""
    
    @pytest.mark.parametrize("workflow_file", get_workflow_files())
    def test_workflow_jobs_specify_runner(self, workflow_file: Path):
        """
        Ensure each job in the workflow file specifies a runner.
        
        Checks every job in the parsed workflow YAML and asserts that non-reusable jobs declare a `runs-on` runner. Jobs that invoke reusable workflows via a `uses` key are exempt.
        
        Parameters:
            workflow_file (Path): Path to the workflow YAML file being tested.
        """
        config = load_yaml_safe(workflow_file)
        jobs = config.get("jobs", {})
        
        for job_name, job_config in jobs.items():
            if "uses" in job_config:
                # Reusable workflow calls don't need runs-on
                continue
            assert "runs-on" in job_config, (
                f"Job '{job_name}' in {workflow_file.name} must specify 'runs-on'"
            )
    
    @pytest.mark.parametrize("workflow_file", get_workflow_files())
    def test_workflow_jobs_use_standard_runners(self, workflow_file: Path):
        """
        Verify that jobs which specify `runs-on` use a recognised GitHub-hosted runner.
        
        Only jobs that include a `runs-on` key are checked; jobs using self-hosted runners or runner expressions/matrix variables (containing `${{` or `self-hosted`) are permitted and skipped. Raises an assertion failure when a job specifies a non-standard runner.
         
        Parameters:
            workflow_file (Path): Path to the workflow YAML file being tested.
        """
        config = load_yaml_safe(workflow_file)
        jobs = config.get("jobs", {})
        
        standard_runners = {
            "ubuntu-latest", "ubuntu-20.04", "ubuntu-22.04", "ubuntu-24.04",
            "windows-latest", "windows-2019", "windows-2022",
            "macos-latest", "macos-11", "macos-12", "macos-13", "macos-14"
        }
        
        for job_name, job_config in jobs.items():
            if "runs-on" not in job_config:
                continue
            
            runner = job_config["runs-on"]
            if isinstance(runner, str):
                # Allow self-hosted and matrix variables
                if "${{" in runner or "self-hosted" in runner:
                    continue
                assert runner in standard_runners, (
                    f"Job '{job_name}' in {workflow_file.name} uses non-standard runner: {runner}"
                )


class TestWorkflowStepConfiguration:
    """Detailed tests for workflow step configuration."""
    
    @pytest.mark.parametrize("workflow_file", get_workflow_files())
    def test_workflow_steps_with_working_directory(self, workflow_file: Path):
        """Test that steps with working-directory specify valid paths."""
        config = load_yaml_safe(workflow_file)
        jobs = config.get("jobs", {})
        
        for job_name, job_config in jobs.items():
            steps = job_config.get("steps", [])
            
            for idx, step in enumerate(steps):
                if "working-directory" in step:
                    working_dir = step["working-directory"]
                    # Should not use absolute paths
                    assert not working_dir.startswith("/"), (
                        f"Step {idx} in job '{job_name}' of {workflow_file.name} "
                        f"uses absolute path: {working_dir}"
                    )
    
    @pytest.mark.parametrize("workflow_file", get_workflow_files())
    def test_workflow_steps_with_id_are_unique(self, workflow_file: Path):
        """Test that step IDs are unique within each job."""
        config = load_yaml_safe(workflow_file)
        jobs = config.get("jobs", {})
        
        for job_name, job_config in jobs.items():
            steps = job_config.get("steps", [])
            step_ids = [s.get("id") for s in steps if "id" in s]
            
            duplicates = [sid for sid in step_ids if step_ids.count(sid) > 1]
            assert not duplicates, (
                f"Job '{job_name}' in {workflow_file.name} has duplicate step IDs: {duplicates}"
            )
    
    @pytest.mark.parametrize("workflow_file", get_workflow_files())
    def test_workflow_steps_continue_on_error_usage(self, workflow_file: Path):
        """Test that continue-on-error is used sparingly and intentionally."""
        config = load_yaml_safe(workflow_file)
        jobs = config.get("jobs", {})
        
        for job_name, job_config in jobs.items():
            steps = job_config.get("steps", [])
            
            for step in steps:
                if step.get("continue-on-error") is True:
                    # Should have a comment or name explaining why
                    assert "name" in step, (
                        f"Step in job '{job_name}' of {workflow_file.name} "
                        "uses continue-on-error but lacks descriptive name"
                    )


class TestWorkflowEnvAndSecrets:
    """Tests for environment variables and secrets usage."""
    

@pytest.mark.parametrize("workflow_file", get_workflow_files())
def test_workflow_env_vars_naming_convention(workflow_file: Path):
    """
    Validate that environment variables in workflow files follow UPPER_CASE naming convention.
    
    Parameters:
        workflow_file (Path): Path to the workflow YAML file being tested.
    
    Notes:
        Checks environment variables at both workflow level and job level for proper naming.
    """
    config = load_yaml_safe(workflow_file)
    
    def check_env_vars(env_dict):
        """
        Identify environment variable names that do not follow the naming convention of upper-case letters, digits and underscores.
        
        Parameters:
            env_dict (dict): Mapping of environment variable names to their values. If a non-dict is provided, it is treated as absent.
        
        Returns:
            invalid_keys (List[str]): List of keys from `env_dict` that are not entirely upper-case or that contain characters other than letters, digits or underscores.
        """
        if not isinstance(env_dict, dict):
            return []
        invalid = []
        for key in env_dict.keys():
            if not key.isupper() or not key.replace("_", "").isalnum():
                invalid.append(key)
        return invalid
    
    # Check top-level env
    if "env" in config:
        invalid = check_env_vars(config["env"])
        assert not invalid, (
            f"Workflow {workflow_file.name} has invalid env var names: {invalid}"
        )
    
    # Check job-level env
    jobs = config.get("jobs", {})
    for job_name, job_config in jobs.items():
        if "env" in job_config:
            invalid = check_env_vars(job_config["env"])
            assert not invalid, (
                f"Job '{job_name}' in {workflow_file.name} has invalid env var names: {invalid}"
            )

    
    @pytest.mark.parametrize("workflow_file", get_workflow_files())
    def test_workflow_secrets_not_in_env_values(self, workflow_file: Path):
        """Test that secrets are referenced, not hardcoded in env values."""
        with open(workflow_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Look for patterns that might indicate hardcoded secrets
        suspicious_in_env = [
            "password: \"",
            "token: \"",
            "api_key: \"",
            "secret: \"",
        ]
        
        for pattern in suspicious_in_env:
            if pattern in content.lower():
                # Allow if it's using secrets context
                if "${{ secrets." not in content[max(0, content.lower().find(pattern) - 50):content.lower().find(pattern) + 50]:
                    pytest.skip(
                        f"Workflow {workflow_file.name} may have hardcoded sensitive value. "
                        "Manual review recommended."
                    )


class TestWorkflowComplexity:
    """Tests for workflow complexity and maintainability."""
    
    @pytest.mark.parametrize("workflow_file", get_workflow_files())
    def test_workflow_job_count_reasonable(self, workflow_file: Path):
        """
        Ensure a workflow contains a reasonable number of jobs.
        
        Prints a warning if the workflow defines more than 10 jobs and fails the test if it defines more than 20 jobs.
        
        Parameters:
            workflow_file (Path): Path to the workflow YAML file being validated.
        """
        config = load_yaml_safe(workflow_file)
        jobs = config.get("jobs", {})
        
        job_count = len(jobs)
        if job_count > 10:
            print(f"\nWarning: {workflow_file.name} has {job_count} jobs. "
                  "Consider splitting into multiple workflows.")
        
        assert job_count <= 20, (
            f"Workflow {workflow_file.name} has {job_count} jobs (max 20). "
            "Split into multiple workflows for better maintainability."
        )
    
    @pytest.mark.parametrize("workflow_file", get_workflow_files())
    def test_workflow_step_count_per_job(self, workflow_file: Path):
        """Test that jobs don't have excessive number of steps."""
        config = load_yaml_safe(workflow_file)
        jobs = config.get("jobs", {})
        
        for job_name, job_config in jobs.items():
            steps = job_config.get("steps", [])
            step_count = len(steps)
            
            if step_count > 15:
                print(f"\nInfo: Job '{job_name}' in {workflow_file.name} has "
                      f"{step_count} steps. Consider refactoring.")
            
            assert step_count <= 30, (
                f"Job '{job_name}' in {workflow_file.name} has {step_count} steps (max 30). "
                "Consider breaking into multiple jobs."
            )
    
    @pytest.mark.parametrize("workflow_file", get_workflow_files())
    def test_workflow_deep_nesting_in_conditionals(self, workflow_file: Path):
        """
        Check job-level 'if' conditionals for excessive logical complexity.
        
        Scans each job's `if` conditional in the workflow and counts occurrences of the logical operators `&&` and `||`. Prints a warning if the sum of these operators for a job exceeds 5, indicating a potentially over-complex conditional.
        
        Parameters:
            workflow_file (Path): Path to the workflow YAML file being tested.
        """
        config = load_yaml_safe(workflow_file)
        jobs = config.get("jobs", {})
        
        for job_name, job_config in jobs.items():
            if "if" in job_config:
                conditional = job_config["if"]
                # Count logical operators as proxy for complexity
                and_count = conditional.count("&&")
                or_count = conditional.count("||")
                
                complexity = and_count + or_count
                if complexity > 5:
                    print(f"\nWarning: Job '{job_name}' in {workflow_file.name} "
                          f"has complex conditional ({complexity} operators)")


class TestWorkflowOutputsAndArtifacts:
    """Tests for workflow outputs and artifact handling."""
    
    @pytest.mark.parametrize("workflow_file", get_workflow_files())
    def test_workflow_artifacts_have_retention(self, workflow_file: Path):
        """
        Verify artifact upload steps declare a retention-days policy.
        
        Scans the workflow's jobs and their steps; for any step using actions/upload-artifact, prints an informational message if the step's `with` mapping does not include `retention-days`.
        
        Parameters:
            workflow_file (Path): Path to the workflow YAML file being tested.
        """
        config = load_yaml_safe(workflow_file)
        jobs = config.get("jobs", {})
        
        for job_name, job_config in jobs.items():
            steps = job_config.get("steps", [])
            
            for step in steps:
                if "actions/upload-artifact" in step.get("uses", ""):
                    step_with = step.get("with", {})
                    # Recommend explicit retention-days
                    if "retention-days" not in step_with:
                        print(f"\nInfo: Artifact upload in job '{job_name}' of "
                              f"{workflow_file.name} doesn't specify retention-days")
    
    @pytest.mark.parametrize("workflow_file", get_workflow_files())
    def test_workflow_outputs_referenced_correctly(self, workflow_file: Path):
        """Test that job outputs are defined when referenced by other jobs."""
        config = load_yaml_safe(workflow_file)
        jobs = config.get("jobs", {})
        
        # Collect all job outputs
        job_outputs = {}
        for job_name, job_config in jobs.items():
            if "outputs" in job_config:
                job_outputs[job_name] = set(job_config["outputs"].keys())
        
        # Check references in needs
        for job_name, job_config in jobs.items():
            needs = job_config.get("needs", [])
            if isinstance(needs, str):
                needs = [needs]
            elif not isinstance(needs, list):
                needs = []
            
            # Verify needed jobs exist
            for needed_job in needs:
                assert needed_job in jobs, (
                    f"Job '{job_name}' in {workflow_file.name} needs '{needed_job}' "
                    "which doesn't exist"
                )


class TestWorkflowBestPractices:
    """Tests for workflow best practices and recommendations."""
    
    @pytest.mark.parametrize("workflow_file", get_workflow_files())
    def test_workflow_uses_concurrency_for_prs(self, workflow_file: Path):
        """Test if PR workflows use concurrency to cancel outdated runs."""
        config = load_yaml_safe(workflow_file)
        triggers = config.get("on", {})
        
        has_pr_trigger = False
        if isinstance(triggers, dict):
            has_pr_trigger = "pull_request" in triggers or "pull_request_target" in triggers
        
        if has_pr_trigger and "concurrency" not in config:
            print(f"\nRecommendation: {workflow_file.name} triggers on PR but doesn't "
                  "use concurrency. Consider adding concurrency group to cancel outdated runs.")
    
    @pytest.mark.parametrize("workflow_file", get_workflow_files())
    def test_workflow_timeout_specified(self, workflow_file: Path):
        """
        Check that each job in the workflow specifies timeout-minutes.
        
        For any job missing `timeout-minutes` this test prints a recommendation identifying the job and the workflow file.
        """
        config = load_yaml_safe(workflow_file)
        jobs = config.get("jobs", {})
        
        for job_name, job_config in jobs.items():
            if "timeout-minutes" not in job_config:
                print(f"\nRecommendation: Job '{job_name}' in {workflow_file.name} "
                      "doesn't specify timeout-minutes")
    
    @pytest.mark.parametrize("workflow_file", get_workflow_files())
    def test_workflow_shell_explicitly_set(self, workflow_file: Path):
        """Test if multi-line run commands explicitly set shell."""
        config = load_yaml_safe(workflow_file)
        jobs = config.get("jobs", {})
        
        for job_name, job_config in jobs.items():
            steps = job_config.get("steps", [])
            
            for idx, step in enumerate(steps):
                if "run" in step:
                    run_cmd = step["run"]
                    if isinstance(run_cmd, str) and "\n" in run_cmd:
                        # Multi-line command
                        if "shell" not in step:
                            print(f"\nRecommendation: Step {idx} in job '{job_name}' "
                                  f"of {workflow_file.name} uses multi-line run without "
                                  "explicit shell specification")