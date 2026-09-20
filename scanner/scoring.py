"""
Transparent scoring system for SSDLC maturity assessment.

This module implements a weighted domain-based scoring methodology
that calculates both security maturity scores and risk levels.
"""

from typing import List, Dict, Tuple
from scanner.models import SecurityFinding, Status, Severity, ScanSummary, DomainScore


# Domain weights (must sum to 1.0)
DOMAIN_WEIGHTS = {
    "Requirements": 0.15,
    "Architecture": 0.20,
    "Implementation": 0.30,
    "Testing": 0.15,
    "Supply Chain": 0.10,
    "Lifecycle": 0.10,
}


def calculate_domain_score(findings: List[SecurityFinding]) -> float:
    """
    Calculate score for a single domain.

    Args:
        findings: List of findings for the domain

    Returns:
        Score as percentage (0-100)
    """
    if not findings:
        return 0.0

    # Only count non-skipped checks
    applicable_findings = [
        f for f in findings
        if f.status not in (Status.SKIPPED, Status.ERROR)
    ]

    if not applicable_findings:
        return 0.0

    passed = sum(1 for f in applicable_findings if f.status == Status.PASS)
    total = len(applicable_findings)

    return round((passed / total) * 100, 1)


def calculate_overall_score(findings: List[SecurityFinding]) -> float:
    """
    Calculate weighted overall security maturity score.

    Args:
        findings: All findings from the scan

    Returns:
        Weighted score as percentage (0-100)
    """
    domain_findings: Dict[str, List[SecurityFinding]] = {}

    for finding in findings:
        domain = finding.domain
        if domain not in domain_findings:
            domain_findings[domain] = []
        domain_findings[domain].append(finding)

    weighted_score = 0.0
    total_weight = 0.0

    for domain, domain_list in domain_findings.items():
        weight = DOMAIN_WEIGHTS.get(domain, 0.0)
        if weight > 0:
            score = calculate_domain_score(domain_list)
            weighted_score += score * weight
            total_weight += weight

    # Normalize if not all domains are present
    if total_weight > 0 and total_weight < 1.0:
        weighted_score = weighted_score / total_weight

    return round(weighted_score, 1)


def calculate_risk_level(findings: List[SecurityFinding], score: float) -> str:
    """
    Determine risk level based on findings and score.

    Args:
        findings: All findings from the scan
        score: Overall maturity score

    Returns:
        Risk level: CRITICAL, HIGH, MEDIUM, LOW, or MINIMAL
    """
    # Count critical and high severity findings
    critical_count = sum(
        1 for f in findings
        if f.severity == Severity.CRITICAL and f.status == Status.FAIL
    )
    high_count = sum(
        1 for f in findings
        if f.severity == Severity.HIGH and f.status == Status.FAIL
    )

    # Critical findings always result in high risk
    if critical_count > 0:
        return "CRITICAL"

    if high_count >= 5:
        return "CRITICAL"

    if high_count >= 3 or score < 30:
        return "HIGH"

    if high_count >= 1 or score < 50:
        return "MEDIUM"

    if score < 70:
        return "LOW"

    return "MINIMAL"


def calculate_domain_scores(findings: List[SecurityFinding]) -> List[DomainScore]:
    """
    Calculate scores for each domain.

    Args:
        findings: All findings from the scan

    Returns:
        List of DomainScore objects
    """
    domain_findings: Dict[str, List[SecurityFinding]] = {}

    for finding in findings:
        domain = finding.domain
        if domain not in domain_findings:
            domain_findings[domain] = []
        domain_findings[domain].append(finding)

    domain_scores = []

    for domain, domain_list in domain_findings.items():
        weight = DOMAIN_WEIGHTS.get(domain, 0.0)
        score = calculate_domain_score(domain_list)

        passed = sum(1 for f in domain_list if f.status == Status.PASS)
        failed = sum(1 for f in domain_list if f.status == Status.FAIL)
        warnings = sum(1 for f in domain_list if f.status == Status.WARN)
        errors = sum(1 for f in domain_list if f.status == Status.ERROR)
        skipped = sum(1 for f in domain_list if f.status == Status.SKIPPED)

        domain_scores.append(DomainScore(
            domain=domain,
            score=score,
            weight=weight,
            total=len(domain_list),
            passed=passed,
            failed=failed,
            warnings=warnings,
            errors=errors,
            skipped=skipped,
        ))

    return domain_scores


def calculate_summary(findings: List[SecurityFinding]) -> ScanSummary:
    """
    Calculate complete scan summary with statistics.

    Args:
        findings: All findings from the scan

    Returns:
        ScanSummary object
    """
    score = calculate_overall_score(findings)
    risk_level = calculate_risk_level(findings, score)

    total = len(findings)
    passed = sum(1 for f in findings if f.status == Status.PASS)
    failed = sum(1 for f in findings if f.status == Status.FAIL)
    warnings = sum(1 for f in findings if f.status == Status.WARN)
    errors = sum(1 for f in findings if f.status == Status.ERROR)
    skipped = sum(1 for f in findings if f.status == Status.SKIPPED)

    critical = sum(
        1 for f in findings
        if f.severity == Severity.CRITICAL and f.status == Status.FAIL
    )
    high = sum(
        1 for f in findings
        if f.severity == Severity.HIGH and f.status == Status.FAIL
    )
    medium = sum(
        1 for f in findings
        if f.severity == Severity.MEDIUM and f.status == Status.FAIL
    )
    low = sum(
        1 for f in findings
        if f.severity == Severity.LOW and f.status == Status.FAIL
    )
    info = sum(
        1 for f in findings
        if f.severity == Severity.INFO and f.status == Status.FAIL
    )

    return ScanSummary(
        score=score,
        risk_level=risk_level,
        total_checks=total,
        passed=passed,
        failed=failed,
        warnings=warnings,
        errors=errors,
        skipped=skipped,
        critical=critical,
        high=high,
        medium=medium,
        low=low,
        info=info,
    )


# Legacy function for backward compatibility
def calculate_score(results: List[dict]) -> float:
    """
    Legacy scoring function for backward compatibility.

    Args:
        results: List of result dictionaries with 'passed' field

    Returns:
        Simple percentage score
    """
    if not results:
        return 0.0

    passed = sum(1 for result in results if result.get("passed", False))
    total = len(results)

    return round((passed / total) * 100, 1)
