"""
Normalized security finding models for SSDLC Analyzer.

This module defines the standardized data structures for security findings
across all assessment domains.
"""

from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any
from enum import Enum


class Severity(str, Enum):
    """Security finding severity levels."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class Status(str, Enum):
    """Check execution status."""
    PASS = "PASS"
    FAIL = "FAIL"
    WARN = "WARN"
    ERROR = "ERROR"
    SKIPPED = "SKIPPED"


class Confidence(str, Enum):
    """Confidence level in the finding."""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


@dataclass
class SecurityFinding:
    """
    Normalized security finding model.

    Represents a single security check result, whether passed or failed,
    with complete context, evidence, and remediation guidance.
    """

    # Core identification
    id: str
    domain: str
    category: str
    name: str

    # Status and severity
    status: Status
    severity: Optional[Severity] = None
    confidence: Optional[Confidence] = None

    # Descriptions
    description: str = ""
    detail: str = ""
    remediation: str = ""
    evidence: str = ""

    # Location information
    files: List[str] = field(default_factory=list)
    line: Optional[int] = None

    # Tool information
    tool: str = "native"
    rule_id: Optional[str] = None

    # Additional context
    references: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def passed(self) -> bool:
        """Backward compatibility property."""
        return self.status == Status.PASS

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        data = asdict(self)
        # Convert enums to strings
        if self.status:
            data['status'] = self.status.value
        if self.severity:
            data['severity'] = self.severity.value
        if self.confidence:
            data['confidence'] = self.confidence.value
        # Add backward compatibility
        data['passed'] = self.passed
        return data

    @classmethod
    def create_pass(
        cls,
        id: str,
        domain: str,
        category: str,
        name: str,
        description: str = "",
        detail: str = "",
        evidence: str = "",
        tool: str = "native",
        **kwargs
    ) -> "SecurityFinding":
        """Create a passing check result."""
        return cls(
            id=id,
            domain=domain,
            category=category,
            name=name,
            status=Status.PASS,
            description=description,
            detail=detail,
            evidence=evidence,
            tool=tool,
            **kwargs
        )

    @classmethod
    def create_fail(
        cls,
        id: str,
        domain: str,
        category: str,
        name: str,
        severity: Severity,
        description: str = "",
        detail: str = "",
        remediation: str = "",
        evidence: str = "",
        confidence: Confidence = Confidence.HIGH,
        tool: str = "native",
        **kwargs
    ) -> "SecurityFinding":
        """Create a failing check result."""
        return cls(
            id=id,
            domain=domain,
            category=category,
            name=name,
            status=Status.FAIL,
            severity=severity,
            confidence=confidence,
            description=description,
            detail=detail,
            remediation=remediation,
            evidence=evidence,
            tool=tool,
            **kwargs
        )

    @classmethod
    def create_skipped(
        cls,
        id: str,
        domain: str,
        category: str,
        name: str,
        reason: str,
        tool: str = "native",
        **kwargs
    ) -> "SecurityFinding":
        """Create a skipped check result."""
        return cls(
            id=id,
            domain=domain,
            category=category,
            name=name,
            status=Status.SKIPPED,
            detail=reason,
            tool=tool,
            **kwargs
        )

    @classmethod
    def create_error(
        cls,
        id: str,
        domain: str,
        category: str,
        name: str,
        error: str,
        tool: str = "native",
        **kwargs
    ) -> "SecurityFinding":
        """Create an error result."""
        return cls(
            id=id,
            domain=domain,
            category=category,
            name=name,
            status=Status.ERROR,
            detail=f"Check failed to execute: {error}",
            tool=tool,
            **kwargs
        )


@dataclass
class ScanSummary:
    """Summary statistics for a completed scan."""

    score: float
    risk_level: str

    total_checks: int
    passed: int
    failed: int
    warnings: int
    errors: int
    skipped: int

    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0
    info: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return asdict(self)


@dataclass
class DomainScore:
    """Score for a specific SSDLC domain."""

    domain: str
    score: float
    weight: float

    total: int
    passed: int
    failed: int
    warnings: int
    errors: int
    skipped: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return asdict(self)


@dataclass
class ScanResult:
    """Complete scan result with all findings and metadata."""

    scan_id: str
    project: str
    started_at: str
    completed_at: Optional[str] = None
    status: str = "completed"

    summary: Optional[ScanSummary] = None
    domains: List[DomainScore] = field(default_factory=list)
    findings: List[SecurityFinding] = field(default_factory=list)

    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "scan_id": self.scan_id,
            "project": self.project,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "status": self.status,
            "summary": self.summary.to_dict() if self.summary else None,
            "domains": [d.to_dict() for d in self.domains],
            "findings": [f.to_dict() for f in self.findings],
            "metadata": self.metadata,
        }


def legacy_format(finding: SecurityFinding) -> Dict[str, Any]:
    """
    Convert SecurityFinding to legacy format for backward compatibility.

    Args:
        finding: SecurityFinding instance

    Returns:
        Dictionary in legacy format
    """
    return {
        "domain": finding.domain,
        "name": finding.name,
        "passed": finding.passed,
        "detail": finding.detail or finding.description,
    }
