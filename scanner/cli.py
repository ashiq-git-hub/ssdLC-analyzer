"""
Command-line interface for SSDLC Analyzer.

Provides a CLI for running security assessments and generating reports.
"""

import sys
import os
import argparse
from scanner.engine import scan_repository
from scanner.models import Severity, Status


def print_report(result):
    """Print scan results to console in human-readable format."""
    print()
    print("=" * 70)
    print(f"  SSDLC Analyzer Report: {result.project}")
    print("=" * 70)
    print()

    # Overall score
    summary = result.summary
    print(f"Security Maturity Score: {summary.score}/100")
    print(f"Risk Level: {summary.risk_level}")
    print()

    # Summary statistics
    print(f"Total Checks: {summary.total_checks}")
    print(f"  ✓ Passed: {summary.passed}")
    print(f"  ✗ Failed: {summary.failed}")
    print(f"  ⚠ Warnings: {summary.warnings}")
    print(f"  ⊘ Skipped: {summary.skipped}")
    print(f"  ⊗ Errors: {summary.errors}")
    print()

    # Severity breakdown
    if summary.critical > 0 or summary.high > 0 or summary.medium > 0:
        print("Severity Breakdown:")
        if summary.critical > 0:
            print(f"  CRITICAL: {summary.critical}")
        if summary.high > 0:
            print(f"  HIGH: {summary.high}")
        if summary.medium > 0:
            print(f"  MEDIUM: {summary.medium}")
        if summary.low > 0:
            print(f"  LOW: {summary.low}")
        print()

    # Domain scores
    print("Domain Scores:")
    for domain in result.domains:
        bar_length = int(domain.score / 5)
        bar = "█" * bar_length + "░" * (20 - bar_length)
        print(f"  {domain.domain:20} [{bar}] {domain.score:5.1f}% ({domain.passed}/{domain.total})")
    print()

    # Detailed findings
    print("Findings:")
    print("-" * 70)

    for finding in result.findings:
        status_symbol = {
            Status.PASS: "✓",
            Status.FAIL: "✗",
            Status.WARN: "⚠",
            Status.SKIPPED: "⊘",
            Status.ERROR: "⊗",
        }.get(finding.status, "?")

        severity_label = f"[{finding.severity.value}]" if finding.severity else ""

        print(f"{status_symbol} [{finding.domain}] {finding.name} {severity_label}")
        print(f"  {finding.detail}")

        if finding.evidence:
            print(f"  Evidence: {finding.evidence}")

        if finding.status == Status.FAIL and finding.remediation:
            print(f"  → {finding.remediation}")

        print()

    print("=" * 70)
    print()


def export_json(result, output_path):
    """Export scan results as JSON."""
    import json
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result.to_dict(), f, indent=2)
    print(f"JSON report saved to: {output_path}")


def export_markdown(result, output_path):
    """Export scan results as Markdown."""
    summary = result.summary

    md = []
    md.append(f"# SSDLC Security Assessment Report")
    md.append(f"")
    md.append(f"**Project:** {result.project}  ")
    md.append(f"**Scan ID:** {result.scan_id}  ")
    md.append(f"**Date:** {result.started_at}  ")
    md.append(f"")
    md.append(f"## Overall Security Score")
    md.append(f"")
    md.append(f"- **Maturity Score:** {summary.score}/100")
    md.append(f"- **Risk Level:** {summary.risk_level}")
    md.append(f"")
    md.append(f"## Summary Statistics")
    md.append(f"")
    md.append(f"- Total Checks: {summary.total_checks}")
    md.append(f"- Passed: {summary.passed}")
    md.append(f"- Failed: {summary.failed}")
    md.append(f"- Warnings: {summary.warnings}")
    md.append(f"- Skipped: {summary.skipped}")
    md.append(f"- Errors: {summary.errors}")
    md.append(f"")

    if summary.critical > 0 or summary.high > 0:
        md.append(f"## Security Findings by Severity")
        md.append(f"")
        if summary.critical > 0:
            md.append(f"- **CRITICAL:** {summary.critical}")
        if summary.high > 0:
            md.append(f"- **HIGH:** {summary.high}")
        if summary.medium > 0:
            md.append(f"- **MEDIUM:** {summary.medium}")
        if summary.low > 0:
            md.append(f"- **LOW:** {summary.low}")
        md.append(f"")

    md.append(f"## Domain Scores")
    md.append(f"")
    for domain in result.domains:
        md.append(f"### {domain.domain}")
        md.append(f"")
        md.append(f"- Score: {domain.score}/100")
        md.append(f"- Passed: {domain.passed}/{domain.total}")
        md.append(f"")

    md.append(f"## Detailed Findings")
    md.append(f"")

    for finding in result.findings:
        status_emoji = {
            Status.PASS: "✅",
            Status.FAIL: "❌",
            Status.WARN: "⚠️",
            Status.SKIPPED: "⏭️",
            Status.ERROR: "🔴",
        }.get(finding.status, "❓")

        md.append(f"### {status_emoji} {finding.name}")
        md.append(f"")
        md.append(f"**Domain:** {finding.domain}  ")
        md.append(f"**Status:** {finding.status.value}  ")
        if finding.severity:
            md.append(f"**Severity:** {finding.severity.value}  ")
        md.append(f"")
        md.append(f"{finding.detail}")
        md.append(f"")

        if finding.evidence:
            md.append(f"**Evidence:** {finding.evidence}")
            md.append(f"")

        if finding.status == Status.FAIL and finding.remediation:
            md.append(f"**Remediation:** {finding.remediation}")
            md.append(f"")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md))
    print(f"Markdown report saved to: {output_path}")


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="SSDLC Analyzer - Secure Software Development Lifecycle Assessment Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "repository",
        help="Path to repository to analyze",
    )

    parser.add_argument(
        "--json",
        metavar="FILE",
        help="Export results as JSON to specified file",
    )

    parser.add_argument(
        "--markdown",
        metavar="FILE",
        help="Export results as Markdown to specified file",
    )

    parser.add_argument(
        "--fail-on",
        choices=["critical", "high", "medium", "low"],
        help="Fail with exit code 1 if findings of specified severity or higher are present",
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output",
    )

    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress console output (useful with --json or --markdown)",
    )

    args = parser.parse_args()

    # Validate repository path
    repo_path = os.path.abspath(args.repository)
    if not os.path.isdir(repo_path):
        print(f"Error: Repository path does not exist: {repo_path}", file=sys.stderr)
        sys.exit(2)

    # Run scan
    if args.verbose:
        print(f"Scanning repository: {repo_path}")

    try:
        result = scan_repository(repo_path)
    except Exception as error:
        print(f"Error: Scan failed: {error}", file=sys.stderr)
        sys.exit(2)

    # Print console report
    if not args.quiet:
        print_report(result)

    # Export JSON
    if args.json:
        export_json(result, args.json)

    # Export Markdown
    if args.markdown:
        export_markdown(result, args.markdown)

    # Check fail-on threshold
    if args.fail_on:
        severity_order = ["critical", "high", "medium", "low"]
        threshold_index = severity_order.index(args.fail_on)

        failed_findings = [f for f in result.findings if f.status == Status.FAIL and f.severity]

        for finding in failed_findings:
            finding_severity = finding.severity.value.lower()
            if finding_severity in severity_order:
                finding_index = severity_order.index(finding_severity)
                if finding_index <= threshold_index:
                    print(f"Exiting with code 1: Found {finding_severity.upper()} severity finding", file=sys.stderr)
                    sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
