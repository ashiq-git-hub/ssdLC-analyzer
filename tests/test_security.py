"""
Comprehensive test suite for SSDLC Analyzer.

Tests all components: models, scoring, archive security, checks, engine, and API.
"""

import os
import tempfile
import zipfile
import pytest
from scanner.models import (
    SecurityFinding,
    Severity,
    Status,
    ScanResult,
    ScanSummary,
    DomainScore,
)
from scanner import scoring
from scanner.utils.archive import (
    safe_extract_zip,
    validate_zip_path,
    ArchiveSecurityError,
    ArchiveConfig,
)
from scanner.checks import requirements, architecture, testing
from scanner.engine import scan_repository


# ==============================================================================
# Model Tests
# ==============================================================================

def test_security_finding_create_pass():
    """Test creating a passing finding."""
    finding = SecurityFinding.create_pass(
        id="REQ-001",
        domain="Requirements",
        category="Policy",
        name="Security Policy Exists",
        detail="Found SECURITY.md",
    )

    assert finding.id == "REQ-001"
    assert finding.status == Status.PASS
    assert finding.passed is True
    assert finding.severity is None


def test_security_finding_create_fail():
    """Test creating a failing finding."""
    finding = SecurityFinding.create_fail(
        id="IMP-001",
        domain="Implementation",
        category="SAST",
        name="SQL Injection",
        severity=Severity.HIGH,
        detail="Unsanitized user input in query",
    )

    assert finding.id == "IMP-001"
    assert finding.status == Status.FAIL
    assert finding.passed is False
    assert finding.severity == Severity.HIGH


def test_security_finding_to_dict():
    """Test converting finding to dictionary."""
    finding = SecurityFinding.create_fail(
        id="TEST-001",
        domain="Testing",
        category="Unit",
        name="Tests Missing",
        severity=Severity.MEDIUM,
    )

    data = finding.to_dict()
    assert data["id"] == "TEST-001"
    assert data["status"] == "FAIL"
    assert data["severity"] == "MEDIUM"
    assert data["passed"] is False


# ==============================================================================
# Scoring Tests
# ==============================================================================

def test_calculate_domain_score():
    """Test domain score calculation."""
    findings = [
        SecurityFinding.create_pass("1", "Req", "Cat", "Check 1"),
        SecurityFinding.create_pass("2", "Req", "Cat", "Check 2"),
        SecurityFinding.create_fail("3", "Req", "Cat", "Check 3", Severity.LOW),
        SecurityFinding.create_skipped("4", "Req", "Cat", "Check 4", "Skipped"),
    ]

    # 2 passed out of 3 applicable (skipped ignored) = 66.7%
    score = scoring.calculate_domain_score(findings)
    assert score == 66.7


def test_calculate_overall_score():
    """Test weighted overall score calculation."""
    findings = [
        # Requirements (15%): 100%
        SecurityFinding.create_pass("1", "Requirements", "Cat", "Check 1"),
        # Architecture (20%): 50%
        SecurityFinding.create_pass("2", "Architecture", "Cat", "Check 2"),
        SecurityFinding.create_fail("3", "Architecture", "Cat", "Check 3", Severity.LOW),
    ]

    score = scoring.calculate_overall_score(findings)
    # Normalized: (100 * 0.15 + 50 * 0.20) / (0.15 + 0.20) = (15 + 10) / 0.35 = 71.4%
    assert score == 71.4


def test_calculate_risk_level_critical():
    """Test risk level calculation with critical finding."""
    findings = [
        SecurityFinding.create_fail("1", "Imp", "Secrets", "Hardcoded Key", Severity.CRITICAL),
    ]
    assert scoring.calculate_risk_level(findings, 90.0) == "CRITICAL"


def test_calculate_risk_level_high():
    """Test risk level calculation with high findings."""
    findings = [
        SecurityFinding.create_fail("1", "Imp", "SAST", "SQLi", Severity.HIGH),
        SecurityFinding.create_fail("2", "Imp", "SAST", "XSS", Severity.HIGH),
        SecurityFinding.create_fail("3", "Imp", "SAST", "RCE", Severity.HIGH),
    ]
    assert scoring.calculate_risk_level(findings, 50.0) == "HIGH"


def test_legacy_calculate_score():
    """Test backward-compatible calculate_score function."""
    results = [
        {"passed": True},
        {"passed": True},
        {"passed": False},
        {"passed": False},
    ]
    assert scoring.calculate_score(results) == 50.0


# ==============================================================================
# Archive Security Tests
# ==============================================================================

def test_validate_zip_path_safe():
    """Test path validation with safe relative path."""
    target_dir = os.path.abspath("/tmp/target")
    safe_path = validate_zip_path(target_dir, "src/main.py")
    assert safe_path.startswith(target_dir)


def test_validate_zip_path_traversal():
    """Test path traversal detection."""
    target_dir = os.path.abspath("/tmp/target")
    with pytest.raises(ArchiveSecurityError):
        validate_zip_path(target_dir, "../../../etc/passwd")


def test_safe_extract_zip(tmp_path):
    """Test safe ZIP extraction with valid archive."""
    # Create test zip
    zip_path = tmp_path / "test.zip"
    extract_dir = tmp_path / "extracted"

    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("test.txt", "Hello World")
        zf.writestr("subdir/nested.txt", "Nested content")

    result_dir = safe_extract_zip(str(zip_path), str(extract_dir))

    assert os.path.exists(os.path.join(result_dir, "test.txt"))
    assert os.path.exists(os.path.join(result_dir, "subdir", "nested.txt"))


def test_archive_size_limit(tmp_path):
    """Test archive size limit enforcement."""
    zip_path = tmp_path / "large.zip"
    extract_dir = tmp_path / "extracted"

    # Create dummy large zip
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("large.txt", "A" * 1000)

    config = ArchiveConfig(max_file_size=500)

    with pytest.raises(ArchiveSecurityError):
        safe_extract_zip(str(zip_path), str(extract_dir), config)


# ==============================================================================
# Security Checks Tests
# ==============================================================================

def test_requirements_security_file_exists(tmp_path):
    """Test detection of SECURITY.md."""
    # Create SECURITY.md
    sec_file = tmp_path / "SECURITY.md"
    sec_file.write_text("# Security Policy")

    finding = requirements.check_security_file(str(tmp_path))
    assert finding.status == Status.PASS
    assert finding.passed is True


def test_requirements_security_file_missing(tmp_path):
    """Test detection of missing SECURITY.md."""
    finding = requirements.check_security_file(str(tmp_path))
    assert finding.status == Status.FAIL
    assert finding.passed is False
    assert finding.severity == Severity.MEDIUM


def test_architecture_threat_model_exists(tmp_path):
    """Test detection of threat model artifact."""
    tm_file = tmp_path / "threat-model.md"
    tm_file.write_text("# Threat Model\n\nDetailed STRIDE analysis of the system..." * 10)

    finding = architecture.check_threat_model(str(tmp_path))
    assert finding.status == Status.PASS


def test_architecture_threat_model_empty(tmp_path):
    """Test detection of empty threat model."""
    tm_file = tmp_path / "threat-model.md"
    tm_file.write_text("# Threat Model")  # Very short

    finding = architecture.check_threat_model(str(tmp_path))
    assert finding.status == Status.FAIL
    assert finding.severity == Severity.LOW


def test_testing_suite_exists(tmp_path):
    """Test test suite detection."""
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_app.py").write_text("def test_dummy(): pass")

    finding = testing.check_test_suite_exists(str(tmp_path))
    assert finding.status == Status.PASS


# ==============================================================================
# Scan Engine Integration Test
# ==============================================================================

def test_scan_repository_self(tmp_path):
    """Integration test: scan repository with sample structure."""
    # Create mock repo
    (tmp_path / "SECURITY.md").write_text("# Security Policy")
    (tmp_path / "requirements.txt").write_text("fastapi\nuvicorn")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_security.py").write_text("def test_auth(): pass")

    result = scan_repository(str(tmp_path))

    assert isinstance(result, ScanResult)
    assert result.summary is not None
    assert result.summary.total_checks > 0
    assert len(result.domains) > 0
    assert len(result.findings) > 0
