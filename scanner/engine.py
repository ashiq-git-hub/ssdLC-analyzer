"""
Scan engine orchestrator.

Central engine for running SSDLC security assessments. Discovers project
characteristics, runs applicable checks, normalizes results, and generates
comprehensive scan reports.
"""

import os
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Optional
from scanner.models import SecurityFinding, ScanResult
from scanner import scoring
from scanner.checks import requirements, architecture, implementation, testing

try:
    from scanner.checks import supply_chain
except ImportError:
    supply_chain = None

try:
    from scanner.checks import lifecycle
except ImportError:
    lifecycle = None


class ScanEngine:
    """Central orchestrator for SSDLC security assessments."""

    def __init__(self, repo_path: str):
        """
        Initialize scan engine.

        Args:
            repo_path: Absolute path to repository to scan
        """
        self.repo_path = os.path.abspath(repo_path)
        self.project_name = os.path.basename(self.repo_path)
        self.scan_id = f"scan_{uuid.uuid4().hex[:12]}"
        self.findings: List[SecurityFinding] = []
        self.started_at: Optional[str] = None
        self.completed_at: Optional[str] = None

    def detect_technologies(self) -> List[str]:
        """
        Detect programming languages and frameworks used in the project.

        Returns:
            List of detected technology identifiers
        """
        technologies = []

        # Python
        if any(os.path.exists(os.path.join(self.repo_path, f)) for f in
               ["requirements.txt", "setup.py", "pyproject.toml", "Pipfile"]):
            technologies.append("Python")

        # JavaScript/TypeScript
        if os.path.exists(os.path.join(self.repo_path, "package.json")):
            technologies.append("JavaScript")

        # TypeScript
        if os.path.exists(os.path.join(self.repo_path, "tsconfig.json")):
            technologies.append("TypeScript")

        # Java
        if any(os.path.exists(os.path.join(self.repo_path, f)) for f in
               ["pom.xml", "build.gradle", "build.gradle.kts"]):
            technologies.append("Java")

        # Go
        if os.path.exists(os.path.join(self.repo_path, "go.mod")):
            technologies.append("Go")

        # Rust
        if os.path.exists(os.path.join(self.repo_path, "Cargo.toml")):
            technologies.append("Rust")

        # C#/.NET
        for root, _, files in os.walk(self.repo_path):
            if any(f.endswith((".csproj", ".fsproj", ".sln")) for f in files):
                technologies.append(".NET")
                break

        # Ruby
        if any(os.path.exists(os.path.join(self.repo_path, f)) for f in
               ["Gemfile", "Rakefile"]):
            technologies.append("Ruby")

        # PHP
        if os.path.exists(os.path.join(self.repo_path, "composer.json")):
            technologies.append("PHP")

        return technologies

    def run_domain_checks(self, domain: str, check_module) -> None:
        """
        Run all checks for a specific domain with error isolation.

        Args:
            domain: Domain name (for logging)
            check_module: Module containing run_all() function
        """
        try:
            results = check_module.run_all(self.repo_path)
            self.findings.extend(results)
        except Exception as error:
            # Domain failure should not crash entire scan
            self.findings.append(SecurityFinding.create_error(
                id=f"ERR-{domain[:3].upper()}",
                domain=domain,
                category="Scan Error",
                name=f"{domain} Check Failed",
                error=str(error),
            ))

    def run_scan(self) -> ScanResult:
        """
        Execute complete SSDLC security assessment.

        Returns:
            ScanResult with all findings and metadata
        """
        self.started_at = datetime.now(timezone.utc).isoformat()

        # Detect project characteristics
        technologies = self.detect_technologies()

        # Run all domain checks with error isolation
        self.run_domain_checks("Requirements", requirements)
        self.run_domain_checks("Architecture", architecture)
        self.run_domain_checks("Implementation", implementation)
        self.run_domain_checks("Testing", testing)

        if supply_chain is not None:
            self.run_domain_checks("Supply Chain", supply_chain)

        if lifecycle is not None:
            self.run_domain_checks("Lifecycle", lifecycle)

        self.completed_at = datetime.now(timezone.utc).isoformat()

        # Calculate scores and summary
        summary = scoring.calculate_summary(self.findings)
        domain_scores = scoring.calculate_domain_scores(self.findings)

        # Build result
        result = ScanResult(
            scan_id=self.scan_id,
            project=self.project_name,
            started_at=self.started_at,
            completed_at=self.completed_at,
            status="completed",
            summary=summary,
            domains=domain_scores,
            findings=self.findings,
            metadata={
                "technologies": technologies,
                "repo_path": self.repo_path,
            },
        )

        return result


def scan_repository(repo_path: str) -> ScanResult:
    """
    Convenience function to run a complete scan.

    Args:
        repo_path: Path to repository

    Returns:
        ScanResult object
    """
    engine = ScanEngine(repo_path)
    return engine.run_scan()


def scan_repository_legacy(repo_path: str) -> List[dict]:
    """
    Legacy scan function for backward compatibility.

    Args:
        repo_path: Path to repository

    Returns:
        List of finding dictionaries in legacy format
    """
    result = scan_repository(repo_path)
    return [finding.to_dict() for finding in result.findings]
