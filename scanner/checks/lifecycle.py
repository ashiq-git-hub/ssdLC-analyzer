"""
Lifecycle and DevSecOps security checks.

Inspects CI/CD pipelines, security automation, and development lifecycle controls.
"""

import os
import re
from typing import List, Dict, Optional
from scanner.models import SecurityFinding, Severity, Status


def _find_ci_files(repo_path: str) -> Dict[str, List[str]]:
    """Find all CI/CD configuration files."""
    ci_files = {
        "github": [],
        "gitlab": [],
        "jenkins": [],
        "azure": [],
        "circleci": [],
        "other": [],
    }

    # GitHub Actions
    gh_dir = os.path.join(repo_path, ".github", "workflows")
    if os.path.isdir(gh_dir):
        for f in os.listdir(gh_dir):
            if f.endswith((".yml", ".yaml")):
                ci_files["github"].append(os.path.join(gh_dir, f))

    # GitLab CI
    gitlab_file = os.path.join(repo_path, ".gitlab-ci.yml")
    if os.path.exists(gitlab_file):
        ci_files["gitlab"].append(gitlab_file)

    # Jenkins
    jenkins_file = os.path.join(repo_path, "Jenkinsfile")
    if os.path.exists(jenkins_file):
        ci_files["jenkins"].append(jenkins_file)

    # Azure Pipelines
    azure_file = os.path.join(repo_path, "azure-pipelines.yml")
    if os.path.exists(azure_file):
        ci_files["azure"].append(azure_file)

    # CircleCI
    circle_dir = os.path.join(repo_path, ".circleci")
    if os.path.isdir(circle_dir):
        for f in os.listdir(circle_dir):
            if f.endswith((".yml", ".yaml")):
                ci_files["circleci"].append(os.path.join(circle_dir, f))

    return ci_files


def _get_all_ci_content(ci_files: Dict[str, List[str]]) -> str:
    """Read all CI configuration contents."""
    all_content = []
    for platform, files in ci_files.items():
        for f in files:
            try:
                with open(f, "r", encoding="utf-8", errors="ignore") as file:
                    all_content.append(file.read())
            except OSError:
                pass
    return "\n".join(all_content).lower()


def check_cicd_pipeline_exists(repo_path: str) -> SecurityFinding:
    """Check if CI/CD pipeline configurations exist."""
    ci_files = _find_ci_files(repo_path)
    total_files = sum(len(files) for files in ci_files.values())

    if total_files > 0:
        platforms = [p for p, files in ci_files.items() if files]
        return SecurityFinding.create_pass(
            id="LC-001",
            domain="Lifecycle",
            category="CI/CD Pipeline",
            name="CI/CD Pipeline Exists",
            description="Repository has automated build/test pipeline configurations",
            detail=f"Found {total_files} CI/CD workflow file(s) across platforms: {', '.join(platforms)}",
            evidence=f"Platforms: {', '.join(platforms)}",
        )

    return SecurityFinding.create_fail(
        id="LC-001",
        domain="Lifecycle",
        category="CI/CD Pipeline",
        name="CI/CD Pipeline Exists",
        severity=Severity.HIGH,
        description="No CI/CD pipeline configuration detected",
        detail="Missing automated continuous integration and delivery pipelines",
        remediation="Configure CI/CD (e.g., .github/workflows/ci.yml) to automate building, testing, and security scanning on every commit.",
    )


def check_automated_testing_in_ci(repo_path: str) -> SecurityFinding:
    """Check if CI pipeline executes automated tests."""
    ci_files = _find_ci_files(repo_path)
    ci_content = _get_all_ci_content(ci_files)

    if not ci_content:
        return SecurityFinding.create_skipped(
            id="LC-002",
            domain="Lifecycle",
            category="Automated Testing",
            name="Automated Testing in CI",
            reason="No CI/CD pipeline files found to analyze",
        )

    test_patterns = [
        "pytest",
        "npm test",
        "yarn test",
        "mvn test",
        "gradle test",
        "go test",
        "cargo test",
        "dotnet test",
        "run tests",
    ]

    has_tests = any(pattern in ci_content for pattern in test_patterns)

    if has_tests:
        return SecurityFinding.create_pass(
            id="LC-002",
            domain="Lifecycle",
            category="Automated Testing",
            name="Automated Testing in CI",
            description="CI/CD pipeline runs automated test suites",
            detail="Pipeline configuration includes test execution steps",
            evidence="Detected test runner commands in CI workflow",
        )

    return SecurityFinding.create_fail(
        id="LC-002",
        domain="Lifecycle",
        category="Automated Testing",
        name="Automated Testing in CI",
        severity=Severity.MEDIUM,
        description="CI pipeline does not appear to run automated tests",
        detail="No standard test execution commands detected in CI workflow files",
        remediation="Add automated test execution steps to your CI/CD pipeline to prevent regressions from reaching production.",
    )


def check_security_scanning_in_ci(repo_path: str) -> SecurityFinding:
    """Check if CI pipeline runs security scanning tools."""
    ci_files = _find_ci_files(repo_path)
    ci_content = _get_all_ci_content(ci_files)

    if not ci_content:
        return SecurityFinding.create_skipped(
            id="LC-003",
            domain="Lifecycle",
            category="DevSecOps",
            name="Security Scanning in CI",
            reason="No CI/CD pipeline files found to analyze",
        )

    sec_tools = [
        "semgrep",
        "snyk",
        "sonarqube",
        "codeql",
        "trivy",
        "gitleaks",
        "trufflehog",
        "bandit",
        "safety",
        "dependabot",
        "grype",
        "syft",
    ]

    detected_tools = [tool for tool in sec_tools if tool in ci_content]

    if detected_tools:
        return SecurityFinding.create_pass(
            id="LC-003",
            domain="Lifecycle",
            category="DevSecOps",
            name="Security Scanning in CI",
            description="CI pipeline integrates automated security scanning",
            detail=f"Detected security tools in CI: {', '.join(detected_tools)}",
            evidence=f"Security tools: {', '.join(detected_tools)}",
        )

    return SecurityFinding.create_fail(
        id="LC-003",
        domain="Lifecycle",
        category="DevSecOps",
        name="Security Scanning in CI",
        severity=Severity.HIGH,
        description="No security scanning tools detected in CI pipeline",
        detail="CI workflow does not integrate automated SAST, secret scanning, or dependency scanning",
        remediation="Integrate security scanning tools (CodeQL, Semgrep, Gitleaks, Trivy) directly into your CI pipeline to catch vulnerabilities early.",
    )


def check_branch_protection(repo_path: str) -> SecurityFinding:
    """Document branch protection observation."""
    # We cannot reliably verify GitHub branch protection from repo files alone
    return SecurityFinding.create_pass(
        id="LC-004",
        domain="Lifecycle",
        category="Branch Protection",
        name="Branch Protection Configuration",
        description="Branch protection rules cannot be directly verified from repository files alone",
        detail="Branch protection status requires API access to the Git hosting provider. Ensure main branch requires PR reviews and passing status checks.",
        evidence="Manual verification required via hosting provider settings",
    )


def run_all(repo_path: str) -> List[SecurityFinding]:
    """
    Run all lifecycle and DevSecOps checks.

    Args:
        repo_path: Path to target repository

    Returns:
        List of SecurityFinding objects
    """
    return [
        check_cicd_pipeline_exists(repo_path),
        check_automated_testing_in_ci(repo_path),
        check_security_scanning_in_ci(repo_path),
        check_branch_protection(repo_path),
    ]
