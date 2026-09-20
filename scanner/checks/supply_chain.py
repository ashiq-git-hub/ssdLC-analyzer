"""
Supply chain security checks.

Analyzes dependency management, SBOM generation, and vulnerability scanning.
"""

import os
import json
import shutil
import subprocess
from typing import List, Dict, Optional
from scanner.models import SecurityFinding, Severity, Status


def detect_package_ecosystem(repo_path: str) -> List[Dict[str, str]]:
    """
    Detect package ecosystems present in the repository.

    Returns:
        List of dicts with 'ecosystem' and 'manifest' keys
    """
    ecosystems = []

    # Python
    if os.path.exists(os.path.join(repo_path, "requirements.txt")):
        ecosystems.append({"ecosystem": "Python", "manifest": "requirements.txt"})
    if os.path.exists(os.path.join(repo_path, "pyproject.toml")):
        ecosystems.append({"ecosystem": "Python", "manifest": "pyproject.toml"})
    if os.path.exists(os.path.join(repo_path, "Pipfile")):
        ecosystems.append({"ecosystem": "Python", "manifest": "Pipfile"})

    # JavaScript/Node
    if os.path.exists(os.path.join(repo_path, "package.json")):
        ecosystems.append({"ecosystem": "JavaScript", "manifest": "package.json"})

    # Java
    if os.path.exists(os.path.join(repo_path, "pom.xml")):
        ecosystems.append({"ecosystem": "Java", "manifest": "pom.xml"})
    if os.path.exists(os.path.join(repo_path, "build.gradle")):
        ecosystems.append({"ecosystem": "Java", "manifest": "build.gradle"})

    # Go
    if os.path.exists(os.path.join(repo_path, "go.mod")):
        ecosystems.append({"ecosystem": "Go", "manifest": "go.mod"})

    # Rust
    if os.path.exists(os.path.join(repo_path, "Cargo.toml")):
        ecosystems.append({"ecosystem": "Rust", "manifest": "Cargo.toml"})

    # Ruby
    if os.path.exists(os.path.join(repo_path, "Gemfile")):
        ecosystems.append({"ecosystem": "Ruby", "manifest": "Gemfile"})

    # .NET
    for root, _, files in os.walk(repo_path):
        for f in files:
            if f.endswith((".csproj", ".fsproj")):
                ecosystems.append({"ecosystem": ".NET", "manifest": f})
                break
        if any(e["ecosystem"] == ".NET" for e in ecosystems):
            break

    return ecosystems


def check_dependency_manifest(repo_path: str) -> SecurityFinding:
    """Check if dependency manifests exist."""
    ecosystems = detect_package_ecosystem(repo_path)

    if ecosystems:
        manifests = ", ".join([e["manifest"] for e in ecosystems])
        return SecurityFinding.create_pass(
            id="SC-001",
            domain="Supply Chain",
            category="Dependency Management",
            name="Dependency Manifest Exists",
            description="Repository declares dependencies through package manifests",
            detail=f"Found {len(ecosystems)} package manifest(s): {manifests}",
            evidence=f"Ecosystems: {', '.join([e['ecosystem'] for e in ecosystems])}",
        )

    return SecurityFinding.create_fail(
        id="SC-001",
        domain="Supply Chain",
        category="Dependency Management",
        name="Dependency Manifest Exists",
        severity=Severity.LOW,
        description="No dependency manifest detected",
        detail="Project does not appear to use a package manager or dependency manifest is missing",
        remediation="If the project has dependencies, declare them in an appropriate manifest (requirements.txt, package.json, etc.).",
    )


def check_lockfile_exists(repo_path: str) -> SecurityFinding:
    """Check if dependency lockfiles exist."""
    lockfiles = []

    lockfile_names = [
        "package-lock.json",
        "yarn.lock",
        "pnpm-lock.yaml",
        "Pipfile.lock",
        "poetry.lock",
        "Gemfile.lock",
        "Cargo.lock",
        "go.sum",
    ]

    for lockfile in lockfile_names:
        if os.path.exists(os.path.join(repo_path, lockfile)):
            lockfiles.append(lockfile)

    if lockfiles:
        return SecurityFinding.create_pass(
            id="SC-002",
            domain="Supply Chain",
            category="Dependency Pinning",
            name="Dependency Lockfile Exists",
            description="Dependencies are pinned via lockfiles for reproducible builds",
            detail=f"Lockfiles found: {', '.join(lockfiles)}",
            evidence=f"Files: {', '.join(lockfiles)}",
        )

    return SecurityFinding.create_fail(
        id="SC-002",
        domain="Supply Chain",
        category="Dependency Pinning",
        name="Dependency Lockfile Exists",
        severity=Severity.MEDIUM,
        description="No dependency lockfile detected",
        detail="Dependencies are not pinned to specific versions, risking inconsistent builds",
        remediation="Generate and commit lockfiles (package-lock.json, Pipfile.lock, etc.) to ensure reproducible dependency resolution.",
    )


def check_sbom_generation(repo_path: str) -> SecurityFinding:
    """Check if SBOM can be generated using Syft."""
    syft = shutil.which("syft")

    if not syft:
        return SecurityFinding.create_skipped(
            id="SC-003",
            domain="Supply Chain",
            category="SBOM",
            name="SBOM Generation",
            reason="Syft is not installed on this system",
            tool="syft",
        )

    ecosystems = detect_package_ecosystem(repo_path)
    if not ecosystems:
        return SecurityFinding.create_skipped(
            id="SC-003",
            domain="Supply Chain",
            category="SBOM",
            name="SBOM Generation",
            reason="No package ecosystems detected",
            tool="syft",
        )

    # Try to generate SBOM
    sbom_path = os.path.join(repo_path, ".ssdlc-sbom.json")
    command = [
        syft,
        repo_path,
        "-o", "json",
        "--file", sbom_path,
    ]

    try:
        result = subprocess.run(
            command,
            cwd=repo_path,
            capture_output=True,
            timeout=60,
        )

        if result.returncode == 0 and os.path.exists(sbom_path):
            try:
                with open(sbom_path, "r", encoding="utf-8") as f:
                    sbom_data = json.load(f)

                component_count = len(sbom_data.get("artifacts", []))

                # Clean up
                os.remove(sbom_path)

                return SecurityFinding.create_pass(
                    id="SC-003",
                    domain="Supply Chain",
                    category="SBOM",
                    name="SBOM Generation",
                    description="Software Bill of Materials (SBOM) can be generated",
                    detail=f"Syft generated SBOM with {component_count} components",
                    evidence=f"SBOM contains {component_count} dependency artifacts",
                    tool="syft",
                )

            except (json.JSONDecodeError, OSError):
                pass

        return SecurityFinding.create_error(
            id="SC-003",
            domain="Supply Chain",
            category="SBOM",
            name="SBOM Generation",
            error="Syft failed to generate SBOM",
            tool="syft",
        )

    except subprocess.TimeoutExpired:
        return SecurityFinding.create_error(
            id="SC-003",
            domain="Supply Chain",
            category="SBOM",
            name="SBOM Generation",
            error="SBOM generation timed out",
            tool="syft",
        )

    except Exception as error:
        return SecurityFinding.create_error(
            id="SC-003",
            domain="Supply Chain",
            category="SBOM",
            name="SBOM Generation",
            error=str(error),
            tool="syft",
        )


def check_vulnerability_scanning(repo_path: str) -> SecurityFinding:
    """Check for dependency vulnerabilities using Grype."""
    grype = shutil.which("grype")

    if not grype:
        return SecurityFinding.create_skipped(
            id="SC-004",
            domain="Supply Chain",
            category="Vulnerability Scanning",
            name="Dependency Vulnerability Scan",
            reason="Grype is not installed on this system",
            tool="grype",
        )

    ecosystems = detect_package_ecosystem(repo_path)
    if not ecosystems:
        return SecurityFinding.create_skipped(
            id="SC-004",
            domain="Supply Chain",
            category="Vulnerability Scanning",
            name="Dependency Vulnerability Scan",
            reason="No package ecosystems detected",
            tool="grype",
        )

    command = [
        grype,
        f"dir:{repo_path}",
        "-o", "json",
    ]

    try:
        result = subprocess.run(
            command,
            cwd=repo_path,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=90,
        )

        try:
            data = json.loads(result.stdout)
        except json.JSONDecodeError:
            return SecurityFinding.create_error(
                id="SC-004",
                domain="Supply Chain",
                category="Vulnerability Scanning",
                name="Dependency Vulnerability Scan",
                error="Grype returned invalid JSON",
                tool="grype",
            )

        matches = data.get("matches", [])

        if not matches:
            return SecurityFinding.create_pass(
                id="SC-004",
                domain="Supply Chain",
                category="Vulnerability Scanning",
                name="Dependency Vulnerability Scan",
                description="No known vulnerabilities found in dependencies",
                detail="Grype scan completed with 0 vulnerability matches",
                evidence="All dependencies passed vulnerability scan",
                tool="grype",
            )

        # Count by severity
        critical = sum(1 for m in matches if m.get("vulnerability", {}).get("severity") == "Critical")
        high = sum(1 for m in matches if m.get("vulnerability", {}).get("severity") == "High")
        medium = sum(1 for m in matches if m.get("vulnerability", {}).get("severity") == "Medium")
        low = sum(1 for m in matches if m.get("vulnerability", {}).get("severity") == "Low")

        severity = Severity.CRITICAL if critical > 0 else (
            Severity.HIGH if high > 0 else (
                Severity.MEDIUM if medium > 0 else Severity.LOW
            )
        )

        return SecurityFinding.create_fail(
            id="SC-004",
            domain="Supply Chain",
            category="Vulnerability Scanning",
            name="Dependency Vulnerability Scan",
            severity=severity,
            description=f"Known vulnerabilities detected in dependencies",
            detail=f"Grype found {len(matches)} vulnerability matches: {critical} critical, {high} high, {medium} medium, {low} low",
            remediation="Update vulnerable dependencies to patched versions. Review Grype output for specific CVEs and affected packages.",
            evidence=f"Vulnerabilities by severity: Critical={critical}, High={high}, Medium={medium}, Low={low}",
            tool="grype",
        )

    except subprocess.TimeoutExpired:
        return SecurityFinding.create_error(
            id="SC-004",
            domain="Supply Chain",
            category="Vulnerability Scanning",
            name="Dependency Vulnerability Scan",
            error="Vulnerability scan timed out",
            tool="grype",
        )

    except Exception as error:
        return SecurityFinding.create_error(
            id="SC-004",
            domain="Supply Chain",
            category="Vulnerability Scanning",
            name="Dependency Vulnerability Scan",
            error=str(error),
            tool="grype",
        )


def run_all(repo_path: str) -> List[SecurityFinding]:
    """
    Run all supply chain security checks.

    Args:
        repo_path: Path to target repository

    Returns:
        List of SecurityFinding objects
    """
    return [
        check_dependency_manifest(repo_path),
        check_lockfile_exists(repo_path),
        check_sbom_generation(repo_path),
        check_vulnerability_scanning(repo_path),
    ]
