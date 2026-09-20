"""
Requirements security checks.

Inspects repository documentation for security requirements, policies,
and architectural assumptions.
"""

import os
import re
from typing import List, Optional
from scanner.models import SecurityFinding, Severity, Status, Confidence


def _find_doc_files(repo_path: str) -> List[str]:
    """Find all documentation files in the repository."""
    doc_extensions = (".md", ".txt", ".rst", ".adoc")
    doc_files = []

    for root, _, files in os.walk(repo_path):
        # Skip hidden and dependency dirs
        if any(part.startswith((".", "node_modules", "vendor")) for part in root.split(os.sep)):
            continue

        for filename in files:
            if filename.lower().endswith(doc_extensions):
                doc_files.append(os.path.join(root, filename))

    return doc_files


def _search_content(doc_files: List[str], patterns: List[str]) -> Optional[tuple]:
    """
    Search doc files for patterns.

    Returns:
        Tuple of (filepath, matched_text) or None
    """
    compiled_patterns = [re.compile(p, re.IGNORECASE) for p in patterns]

    for filepath in doc_files:
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            for pattern in compiled_patterns:
                match = pattern.search(content)
                if match:
                    # Extract surrounding context
                    start = max(0, match.start() - 50)
                    end = min(len(content), match.end() + 100)
                    context = content[start:end].strip()
                    return filepath, context

        except OSError:
            continue

    return None


def check_security_file(repo_path: str) -> SecurityFinding:
    """Check if SECURITY.md or security policy exists."""
    candidates = ["SECURITY.md", "SECURITY.txt", "security.md", "security.txt"]
    found = None

    for root, _, files in os.walk(repo_path):
        for candidate in candidates:
            if candidate in files:
                found = os.path.join(root, candidate)
                break
        if found:
            break

    if found:
        rel_path = os.path.relpath(found, repo_path)
        return SecurityFinding.create_pass(
            id="REQ-001",
            domain="Requirements",
            category="Security Policy",
            name="Security Policy Exists",
            description="Repository contains a SECURITY.md or security policy document",
            detail=f"Security policy found at {rel_path}",
            evidence=f"File: {rel_path}",
            files=[rel_path],
        )

    return SecurityFinding.create_fail(
        id="REQ-001",
        domain="Requirements",
        category="Security Policy",
        name="Security Policy Exists",
        severity=Severity.MEDIUM,
        description="Repository is missing a security policy (SECURITY.md)",
        detail="No SECURITY.md or equivalent security policy file found in repository",
        remediation="Create a SECURITY.md file detailing vulnerability reporting procedures, supported versions, and security contact info.",
        references=["https://docs.github.com/en/code-security/getting-started/adding-a-security-policy-to-your-repository"],
    )


def check_auth_requirements(repo_path: str) -> SecurityFinding:
    """Check if authentication requirements are documented."""
    doc_files = _find_doc_files(repo_path)

    patterns = [
        r"authentication\s+requirement",
        r"user\s+authentication",
        r"auth\s+flow",
        r"password\s+policy",
        r"session\s+management",
        r"token\s+validation",
        r"oauth",
        r"jwt\s+authentication",
    ]

    result = _search_content(doc_files, patterns)

    if result:
        filepath, context = result
        rel_path = os.path.relpath(filepath, repo_path)
        return SecurityFinding.create_pass(
            id="REQ-002",
            domain="Requirements",
            category="Authentication",
            name="Authentication Requirements Documented",
            description="Authentication requirements or mechanisms are documented",
            detail=f"Authentication requirements documented in {rel_path}",
            evidence=f"Matched in {rel_path}: {context[:120]}...",
            files=[rel_path],
        )

    return SecurityFinding.create_fail(
        id="REQ-002",
        domain="Requirements",
        category="Authentication",
        name="Authentication Requirements Documented",
        severity=Severity.HIGH,
        description="No documented authentication requirements or mechanism specifications found",
        detail="Authentication mechanisms, password policies, and session management are not formally documented",
        remediation="Document authentication requirements including auth methods, token lifecycles, password complexity, and session invalidation rules.",
        confidence=Confidence.MEDIUM,
    )


def check_authorization_requirements(repo_path: str) -> SecurityFinding:
    """Check if authorization/access control requirements are documented."""
    doc_files = _find_doc_files(repo_path)

    patterns = [
        r"authorization\s+requirement",
        r"role-based\s+access",
        r"rbac",
        r"permission\s+model",
        r"access\s+control",
        r"privilege\s+level",
    ]

    result = _search_content(doc_files, patterns)

    if result:
        filepath, context = result
        rel_path = os.path.relpath(filepath, repo_path)
        return SecurityFinding.create_pass(
            id="REQ-003",
            domain="Requirements",
            category="Authorization",
            name="Authorization Requirements Documented",
            description="Access control or authorization models are documented",
            detail=f"Authorization model documented in {rel_path}",
            evidence=f"Matched in {rel_path}: {context[:120]}...",
            files=[rel_path],
        )

    return SecurityFinding.create_fail(
        id="REQ-003",
        domain="Requirements",
        category="Authorization",
        name="Authorization Requirements Documented",
        severity=Severity.HIGH,
        description="No documented authorization or access control model found",
        detail="Access control policies, roles, and permission models are not documented in repository docs",
        remediation="Document the access control model (e.g., RBAC, ABAC), role definitions, privilege boundaries, and access enforcement points.",
        confidence=Confidence.MEDIUM,
    )


def check_input_validation_requirements(repo_path: str) -> SecurityFinding:
    """Check if input validation requirements are documented."""
    doc_files = _find_doc_files(repo_path)

    patterns = [
        r"input\s+validation",
        r"data\s+sanitization",
        r"request\s+validation",
        r"schema\s+validation",
        r"parameter\s+validation",
    ]

    result = _search_content(doc_files, patterns)

    if result:
        filepath, context = result
        rel_path = os.path.relpath(filepath, repo_path)
        return SecurityFinding.create_pass(
            id="REQ-004",
            domain="Requirements",
            category="Input Validation",
            name="Input Validation Requirements Documented",
            description="Input validation and data sanitization rules are documented",
            detail=f"Input validation specifications found in {rel_path}",
            evidence=f"Matched in {rel_path}: {context[:120]}...",
            files=[rel_path],
        )

    return SecurityFinding.create_fail(
        id="REQ-004",
        domain="Requirements",
        category="Input Validation",
        name="Input Validation Requirements Documented",
        severity=Severity.MEDIUM,
        description="Input validation requirements not documented",
        detail="No documentation specifying input validation strategies, boundaries, or sanitization rules",
        remediation="Document input validation rules for all public APIs and entry points, specifying allowed types, lengths, formats, and rejection handling.",
        confidence=Confidence.LOW,
    )


def check_data_protection_requirements(repo_path: str) -> SecurityFinding:
    """Check if data protection and encryption requirements are documented."""
    doc_files = _find_doc_files(repo_path)

    patterns = [
        r"data\s+protection",
        r"encryption\s+at\s+rest",
        r"encryption\s+in\s+transit",
        r"pii\s+protection",
        r"privacy\s+policy",
        r"data\s+retention",
        r"tls\s+1\.[23]",
    ]

    result = _search_content(doc_files, patterns)

    if result:
        filepath, context = result
        rel_path = os.path.relpath(filepath, repo_path)
        return SecurityFinding.create_pass(
            id="REQ-005",
            domain="Requirements",
            category="Data Protection",
            name="Data Protection Requirements Documented",
            description="Data protection and privacy requirements are documented",
            detail=f"Data protection requirements found in {rel_path}",
            evidence=f"Matched in {rel_path}: {context[:120]}...",
            files=[rel_path],
        )

    return SecurityFinding.create_fail(
        id="REQ-005",
        domain="Requirements",
        category="Data Protection",
        name="Data Protection Requirements Documented",
        severity=Severity.MEDIUM,
        description="Data protection and encryption requirements not documented",
        detail="No documentation specifying sensitive data handling, encryption standards, or privacy controls",
        remediation="Document data classification, encryption requirements (at rest and in transit), PII handling, and retention policies.",
        confidence=Confidence.LOW,
    )


def run_all(repo_path: str) -> List[SecurityFinding]:
    """
    Run all requirements checks.

    Args:
        repo_path: Path to target repository

    Returns:
        List of SecurityFinding objects
    """
    return [
        check_security_file(repo_path),
        check_auth_requirements(repo_path),
        check_authorization_requirements(repo_path),
        check_input_validation_requirements(repo_path),
        check_data_protection_requirements(repo_path),
    ]
