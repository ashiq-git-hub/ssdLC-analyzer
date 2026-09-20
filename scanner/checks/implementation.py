"""
Implementation security checks.

Runs static analysis (Semgrep), secret detection (Gitleaks), and code quality checks.
"""

import json
import os
import shutil
import subprocess
from typing import List, Optional
from scanner.models import SecurityFinding, Severity, Status, Confidence


def map_semgrep_severity(semgrep_severity: str) -> Severity:
    """Map Semgrep severity to normalized Severity enum."""
    mapping = {
        "ERROR": Severity.HIGH,
        "WARNING": Severity.MEDIUM,
        "INFO": Severity.LOW,
    }
    return mapping.get(semgrep_severity.upper(), Severity.MEDIUM)


def check_semgrep(repo_path: str) -> List[SecurityFinding]:
    """
    Run Semgrep SAST scan and normalize findings.

    Returns:
        List of SecurityFinding objects
    """
    semgrep = shutil.which("semgrep")

    if not semgrep:
        return [SecurityFinding.create_skipped(
            id="IMP-001",
            domain="Implementation",
            category="SAST",
            name="Semgrep Static Analysis",
            reason="Semgrep is not installed on this system",
            tool="semgrep",
        )]

    command = [
        semgrep,
        "scan",
        "--config", "auto",
        "--json",
        "--exclude", ".venv",
        "--exclude", ".venv-1",
        "--exclude", ".git",
        "--exclude", "sbom.json",
        "--exclude", "test-sbom.json",
        "--exclude", "__pycache__",
        "--exclude", "node_modules",
        "--exclude", "*.zip",
        "--exclude", "build",
        "--exclude", "dist",
        repo_path,
    ]

    try:
        result = subprocess.run(
            command,
            cwd=repo_path,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=180,
        )

        try:
            data = json.loads(result.stdout)
        except json.JSONDecodeError:
            return [SecurityFinding.create_error(
                id="IMP-001",
                domain="Implementation",
                category="SAST",
                name="Semgrep Static Analysis",
                error="Semgrep returned invalid JSON output",
                tool="semgrep",
            )]

        findings_data = data.get("results", [])

        if not findings_data:
            return [SecurityFinding.create_pass(
                id="IMP-001",
                domain="Implementation",
                category="SAST",
                name="Semgrep Static Analysis",
                description="Static analysis tool scan completed successfully",
                detail="No security issues detected by Semgrep",
                evidence="Semgrep scan completed with 0 findings",
                tool="semgrep",
            )]

        # Normalize Semgrep findings
        normalized = []
        for idx, finding in enumerate(findings_data[:50]):  # Limit to 50 findings
            check_id = finding.get("check_id", "unknown")
            message = finding.get("extra", {}).get("message", finding.get("message", ""))
            severity = finding.get("extra", {}).get("severity", "WARNING")
            path = finding.get("path", "")
            start_line = finding.get("start", {}).get("line")

            rel_path = os.path.relpath(path, repo_path) if os.path.isabs(path) else path

            normalized.append(SecurityFinding.create_fail(
                id=f"IMP-SAST-{idx+1:03d}",
                domain="Implementation",
                category="Code Security",
                name=check_id.split(".")[-1].replace("-", " ").title(),
                severity=map_semgrep_severity(severity),
                description=message[:200],
                detail=message,
                remediation="Review the finding and apply recommended fixes. Consult Semgrep documentation for details.",
                evidence=f"Detected by Semgrep rule: {check_id}",
                files=[rel_path],
                line=start_line,
                tool="semgrep",
                rule_id=check_id,
                confidence=Confidence.HIGH,
            ))

        return normalized

    except subprocess.TimeoutExpired:
        return [SecurityFinding.create_error(
            id="IMP-001",
            domain="Implementation",
            category="SAST",
            name="Semgrep Static Analysis",
            error="Semgrep scan exceeded timeout limit (180s)",
            tool="semgrep",
        )]

    except Exception as error:
        return [SecurityFinding.create_error(
            id="IMP-001",
            domain="Implementation",
            category="SAST",
            name="Semgrep Static Analysis",
            error=str(error),
            tool="semgrep",
        )]


def check_gitleaks(repo_path: str) -> List[SecurityFinding]:
    """
    Run Gitleaks secret detection and normalize findings.

    Returns:
        List of SecurityFinding objects
    """
    gitleaks = shutil.which("gitleaks")

    if not gitleaks:
        return [SecurityFinding.create_skipped(
            id="IMP-002",
            domain="Implementation",
            category="Secrets",
            name="Gitleaks Secret Detection",
            reason="Gitleaks is not installed on this system",
            tool="gitleaks",
        )]

    command = [
        gitleaks,
        "detect",
        "--source", repo_path,
        "--no-banner",
        "--redact",
        "--report-format", "json",
        "--report-path", os.path.join(repo_path, ".gitleaks-report.json"),
    ]

    try:
        result = subprocess.run(
            command,
            cwd=repo_path,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=120,
        )

        report_path = os.path.join(repo_path, ".gitleaks-report.json")

        # Gitleaks returns exit code 1 if secrets found, 0 if clean
        if result.returncode == 0:
            # Clean up report
            if os.path.exists(report_path):
                os.remove(report_path)

            return [SecurityFinding.create_pass(
                id="IMP-002",
                domain="Implementation",
                category="Secrets",
                name="Gitleaks Secret Detection",
                description="Secret scanning completed successfully",
                detail="No hardcoded secrets detected by Gitleaks",
                evidence="Gitleaks scan completed with 0 findings",
                tool="gitleaks",
            )]

        # Parse findings
        if os.path.exists(report_path):
            try:
                with open(report_path, "r", encoding="utf-8") as f:
                    findings_data = json.load(f)

                os.remove(report_path)  # Clean up

                if not findings_data:
                    return [SecurityFinding.create_pass(
                        id="IMP-002",
                        domain="Implementation",
                        category="Secrets",
                        name="Gitleaks Secret Detection",
                        description="Secret scanning completed successfully",
                        detail="No hardcoded secrets detected by Gitleaks",
                        evidence="Gitleaks scan completed with 0 findings",
                        tool="gitleaks",
                    )]

                # Normalize findings
                normalized = []
                for idx, finding in enumerate(findings_data[:30]):  # Limit to 30
                    rule_id = finding.get("RuleID", "unknown")
                    description = finding.get("Description", "Potential secret detected")
                    file_path = finding.get("File", "")
                    start_line = finding.get("StartLine")

                    rel_path = os.path.relpath(file_path, repo_path) if os.path.isabs(file_path) else file_path

                    # NEVER include the actual secret
                    normalized.append(SecurityFinding.create_fail(
                        id=f"IMP-SECRET-{idx+1:03d}",
                        domain="Implementation",
                        category="Secrets",
                        name=f"Hardcoded Secret: {rule_id}",
                        severity=Severity.CRITICAL,
                        description=description,
                        detail=f"Potential hardcoded secret detected in {rel_path}",
                        remediation="Remove hardcoded secret immediately. Use environment variables, secrets manager, or encrypted config. Rotate the compromised credential.",
                        evidence=f"Gitleaks rule: {rule_id} (secret redacted for security)",
                        files=[rel_path],
                        line=start_line,
                        tool="gitleaks",
                        rule_id=rule_id,
                        confidence=Confidence.HIGH,
                    ))

                return normalized

            except (json.JSONDecodeError, OSError):
                pass

        # Fallback if we can't parse report
        return [SecurityFinding.create_fail(
            id="IMP-002",
            domain="Implementation",
            category="Secrets",
            name="Gitleaks Secret Detection",
            severity=Severity.HIGH,
            description="Potential secrets detected by Gitleaks",
            detail="Gitleaks detected potential hardcoded secrets but detailed report could not be parsed",
            remediation="Run gitleaks manually to inspect findings: gitleaks detect --source .",
            tool="gitleaks",
        )]

    except subprocess.TimeoutExpired:
        return [SecurityFinding.create_error(
            id="IMP-002",
            domain="Implementation",
            category="Secrets",
            name="Gitleaks Secret Detection",
            error="Gitleaks scan exceeded timeout limit (120s)",
            tool="gitleaks",
        )]

    except Exception as error:
        return [SecurityFinding.create_error(
            id="IMP-002",
            domain="Implementation",
            category="Secrets",
            name="Gitleaks Secret Detection",
            error=str(error),
            tool="gitleaks",
        )]


def run_all(repo_path: str) -> List[SecurityFinding]:
    """
    Run all implementation security checks.

    Args:
        repo_path: Path to target repository

    Returns:
        List of SecurityFinding objects
    """
    findings = []

    findings.extend(check_semgrep(repo_path))
    findings.extend(check_gitleaks(repo_path))

    return findings
