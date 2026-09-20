"""
Testing security checks.

Inspects test suites, security test coverage, and testing practices.
"""

import os
from typing import List
from scanner.models import SecurityFinding, Severity, Status


def check_test_suite_exists(repo_path: str) -> SecurityFinding:
    """Check if test directory or test files exist."""
    test_indicators = []

    # Check for test directories
    test_dirs = ["tests", "test", "__tests__", "spec"]
    for test_dir in test_dirs:
        full_path = os.path.join(repo_path, test_dir)
        if os.path.isdir(full_path):
            test_indicators.append(test_dir)

    # Check for test files in root or src
    test_patterns = ["test_", "_test.", ".test.", ".spec."]
    for root, _, files in os.walk(repo_path):
        # Limit depth
        if root.count(os.sep) - repo_path.count(os.sep) > 2:
            continue

        for filename in files:
            if any(pattern in filename.lower() for pattern in test_patterns):
                test_indicators.append(os.path.join(root, filename))
                break
        if len(test_indicators) >= 3:
            break

    if test_indicators:
        evidence = ", ".join(test_indicators[:3])
        return SecurityFinding.create_pass(
            id="TST-001",
            domain="Testing",
            category="Test Coverage",
            name="Test Suite Exists",
            description="Repository contains a test suite",
            detail=f"Test suite detected: {evidence}",
            evidence=f"Found test infrastructure: {evidence}",
        )

    return SecurityFinding.create_fail(
        id="TST-001",
        domain="Testing",
        category="Test Coverage",
        name="Test Suite Exists",
        severity=Severity.MEDIUM,
        description="No test suite detected in the repository",
        detail="No test directory or test files found",
        remediation="Implement automated tests using a testing framework appropriate for the project's language (pytest, jest, junit, etc.).",
    )


def check_security_tests(repo_path: str) -> SecurityFinding:
    """Check if security-focused tests exist."""
    security_patterns = [
        "security",
        "auth",
        "xss",
        "injection",
        "csrf",
        "sanitiz",
        "validation",
        "access_control",
        "permission",
    ]

    found_tests = []

    for root, _, files in os.walk(repo_path):
        # Skip non-test directories
        if not any(test_dir in root.lower() for test_dir in ["test", "spec"]):
            continue

        for filename in files:
            lower_name = filename.lower()
            # Check if it's a test file
            if any(pattern in lower_name for pattern in ["test_", "_test.", ".test.", ".spec."]):
                # Check if it has security-related keywords
                if any(sec_pattern in lower_name for sec_pattern in security_patterns):
                    found_tests.append(os.path.join(root, filename))

                # Also check file content for security test keywords
                elif lower_name.endswith((".py", ".js", ".ts", ".java", ".go")):
                    try:
                        filepath = os.path.join(root, filename)
                        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                            content = f.read(5000).lower()  # First 5000 chars

                        if any(sec_pattern in content for sec_pattern in security_patterns):
                            found_tests.append(filepath)
                    except OSError:
                        pass

        if len(found_tests) >= 5:
            break

    if found_tests:
        rel_paths = [os.path.relpath(f, repo_path) for f in found_tests[:3]]
        return SecurityFinding.create_pass(
            id="TST-002",
            domain="Testing",
            category="Security Testing",
            name="Security Tests Exist",
            description="Repository contains security-focused test cases",
            detail=f"Found {len(found_tests)} security-related test file(s): {', '.join(rel_paths)}",
            evidence=f"Security test files: {', '.join(rel_paths)}",
            files=rel_paths,
        )

    return SecurityFinding.create_fail(
        id="TST-002",
        domain="Testing",
        category="Security Testing",
        name="Security Tests Exist",
        severity=Severity.MEDIUM,
        description="No security-focused tests detected",
        detail="No test files explicitly covering authentication, authorization, input validation, or other security controls",
        remediation="Add security-specific test cases covering authentication, authorization, input validation, XSS prevention, and injection attacks.",
    )


def check_integration_tests(repo_path: str) -> SecurityFinding:
    """Check if integration or E2E tests exist."""
    integration_keywords = [
        "integration",
        "e2e",
        "end-to-end",
        "api_test",
        "functional",
    ]

    found = []

    for root, _, files in os.walk(repo_path):
        if not any(test_dir in root.lower() for test_dir in ["test", "spec"]):
            continue

        for filename in files:
            lower_name = filename.lower()
            if any(kw in lower_name for kw in integration_keywords):
                found.append(os.path.join(root, filename))

        if len(found) >= 3:
            break

    if found:
        rel_paths = [os.path.relpath(f, repo_path) for f in found[:2]]
        return SecurityFinding.create_pass(
            id="TST-003",
            domain="Testing",
            category="Integration Testing",
            name="Integration Tests Exist",
            description="Repository contains integration or end-to-end tests",
            detail=f"Integration tests detected: {', '.join(rel_paths)}",
            evidence=f"Files: {', '.join(rel_paths)}",
            files=rel_paths,
        )

    return SecurityFinding.create_fail(
        id="TST-003",
        domain="Testing",
        category="Integration Testing",
        name="Integration Tests Exist",
        severity=Severity.LOW,
        description="No integration or end-to-end tests detected",
        detail="No tests verifying full system behavior across components",
        remediation="Add integration tests to verify security controls work correctly across component boundaries.",
    )


def run_all(repo_path: str) -> List[SecurityFinding]:
    """
    Run all testing security checks.

    Args:
        repo_path: Path to target repository

    Returns:
        List of SecurityFinding objects
    """
    return [
        check_test_suite_exists(repo_path),
        check_security_tests(repo_path),
        check_integration_tests(repo_path),
    ]
