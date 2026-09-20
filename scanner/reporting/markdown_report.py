"""Markdown report generator."""

from typing import Dict, Any


def generate_markdown_report(scan_data: Dict[str, Any]) -> str:
    """Generate professional Markdown report."""
    summary = scan_data.get("summary", {})
    domains = scan_data.get("domains", [])
    findings = scan_data.get("findings", [])

    md = []
    md.append(f"# SSDLC Security Assessment Report")
    md.append(f"")
    md.append(f"**Project:** {scan_data.get('project', 'Unknown')}  ")
    md.append(f"**Scan ID:** `{scan_data.get('scan_id', 'N/A')}`  ")
    md.append(f"**Date:** {scan_data.get('started_at', 'N/A')}  ")
    md.append(f"")
    md.append(f"---")
    md.append(f"")
    md.append(f"## Executive Summary")
    md.append(f"")
    md.append(f"This report presents the findings of a Secure Software Development Lifecycle (SSDLC) assessment. The assessment evaluates the repository's security posture across multiple domains including Requirements, Architecture, Implementation, Testing, Supply Chain, and Lifecycle controls.")
    md.append(f"")
    md.append(f"### Key Metrics")
    md.append(f"")
    md.append(f"| Metric | Value |")
    md.append(f"| :--- | :--- |")
    md.append(f"| **Overall Maturity Score** | **{summary.get('score', 0)}/100** |")
    md.append(f"| **Security Risk Level** | **{summary.get('risk_level', 'UNKNOWN')}** |")
    md.append(f"| Total Checks Evaluated | {summary.get('total_checks', 0)} |")
    md.append(f"| Checks Passed | {summary.get('passed', 0)} |")
    md.append(f"| Checks Failed | {summary.get('failed', 0)} |")
    md.append(f"| Warnings | {summary.get('warnings', 0)} |")
    md.append(f"| Skipped / Unavailable | {summary.get('skipped', 0)} |")
    md.append(f"")

    # Severity distribution
    critical = summary.get("critical", 0)
    high = summary.get("high", 0)
    medium = summary.get("medium", 0)
    low = summary.get("low", 0)

    if critical > 0 or high > 0 or medium > 0:
        md.append(f"### Finding Severity Distribution")
        md.append(f"")
        md.append(f"| Severity | Count |")
        md.append(f"| :--- | :--- |")
        if critical > 0:
            md.append(f"| 🔴 CRITICAL | {critical} |")
        if high > 0:
            md.append(f"| 🟠 HIGH | {high} |")
        if medium > 0:
            md.append(f"| 🟡 MEDIUM | {medium} |")
        if low > 0:
            md.append(f"| 🔵 LOW | {low} |")
        md.append(f"")

    md.append(f"---")
    md.append(f"")
    md.append(f"## Domain Performance")
    md.append(f"")
    md.append(f"| Domain | Score | Passed | Failed | Status |")
    md.append(f"| :--- | :--- | :--- | :--- | :--- |")

    for domain in domains:
        score = domain.get("score", 0)
        status_badge = "✅ Strong" if score >= 80 else ("⚠️ Needs Review" if score >= 50 else "❌ Weak")
        md.append(f"| {domain.get('domain')} | {score}% | {domain.get('passed')}/{domain.get('total')} | {domain.get('failed')} | {status_badge} |")

    md.append(f"")
    md.append(f"---")
    md.append(f"")
    md.append(f"## Detailed Findings")
    md.append(f"")

    for finding in findings:
        status = finding.get("status")
        status_icon = {
            "PASS": "✅",
            "FAIL": "❌",
            "WARN": "⚠️",
            "SKIPPED": "⏭️",
            "ERROR": "🔴",
        }.get(status, "❓")

        severity = finding.get("severity")
        severity_str = f" `[{severity}]`" if severity else ""

        md.append(f"### {status_icon} {finding.get('name')}{severity_str}")
        md.append(f"")
        md.append(f"- **ID:** `{finding.get('id')}`")
        md.append(f"- **Domain:** {finding.get('domain')}")
        md.append(f"- **Category:** {finding.get('category')}")
        md.append(f"- **Status:** {status}")
        if severity:
            md.append(f"- **Severity:** {severity}")
        if finding.get("tool"):
            md.append(f"- **Tool:** {finding.get('tool')}")
        md.append(f"")
        md.append(f"**Description:**  ")
        md.append(f"{finding.get('detail') or finding.get('description')}")
        md.append(f"")

        if finding.get("evidence"):
            md.append(f"**Evidence:**  ")
            md.append(f"```")
            md.append(f"{finding.get('evidence')}")
            md.append(f"```")
            md.append(f"")

        if finding.get("files"):
            files_str = ", ".join([f"`{f}`" for f in finding.get("files")])
            md.append(f"**Affected Files:** {files_str}")
            if finding.get("line"):
                md.append(f" (Line: {finding.get('line')})")
            md.append(f"")

        if status == "FAIL" and finding.get("remediation"):
            md.append(f"**Remediation Guidance:**  ")
            md.append(f"{finding.get('remediation')}")
            md.append(f"")

        if finding.get("references"):
            md.append(f"**References:**")
            for ref in finding.get("references"):
                md.append(f"- [{ref}]({ref})")
            md.append(f"")

        md.append(f"---")
        md.append(f"")

    # Limitations & Disclaimer
    md.append(f"## Assessment Limitations & Disclaimer")
    md.append(f"")
    md.append(f"- **Static Analysis Limitations:** Static analysis provides a snapshot of detectable security patterns and practices. A clean scan does not guarantee the absence of security vulnerabilities.")
    md.append(f"- **Tool Availability:** Some checks depend on external tools (Semgrep, Gitleaks, Syft, Grype). Unavailable tools will result in skipped checks, reducing overall assessment coverage.")
    md.append(f"- **Scope:** This assessment evaluates SSDLC process maturity, architectural artifacts, and static code patterns. It does not perform dynamic analysis, penetration testing, or runtime security monitoring.")
    md.append(f"")
    md.append(f"---")
    md.append(f"")
    md.append(f"*Generated by SSDLC Analyzer v2.0.0*")

    return "\n".join(md)
