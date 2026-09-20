"""
Architecture and design security checks.

Inspects repository for threat models, architecture diagrams,
data flow diagrams, and trust boundary documentation.
"""

import os
from typing import List, Optional, Tuple
from scanner.models import SecurityFinding, Severity, Status, Confidence


def check_threat_model(repo_path: str) -> SecurityFinding:
    """Check if threat model artifact exists and contains meaningful content."""
    candidates = [
        "threat-model.json",
        "threat_model.json",
        "threatmodel.json",
        "stride.md",
        "stride.json",
        "threat-model.md",
        "threat_model.md",
        "threatmodel.md",
        "threats.md",
        "threat-modeling.md",
    ]

    found_file = None
    file_size = 0

    for root, _, files in os.walk(repo_path):
        # Skip node_modules and dot directories
        if any(part.startswith((".", "node_modules")) for part in root.split(os.sep)):
            continue

        for filename in files:
            if filename.lower() in candidates:
                full_path = os.path.join(root, filename)
                found_file = full_path
                file_size = os.path.getsize(full_path)
                break
        if found_file:
            break

    if found_file:
        rel_path = os.path.relpath(found_file, repo_path)

        # Check for empty/placeholder threat model
        if file_size < 100:
            return SecurityFinding.create_fail(
                id="ARC-001",
                domain="Architecture",
                category="Threat Modeling",
                name="Threat Model Artifact Exists",
                severity=Severity.LOW,
                description="Threat model file exists but appears to be empty or minimal",
                detail=f"Threat model artifact at {rel_path} is only {file_size} bytes",
                remediation="Expand the threat model to document system assets, threats (STRIDE), attack vectors, and mitigations.",
                evidence=f"File: {rel_path} (size: {file_size}B)",
                files=[rel_path],
            )

        return SecurityFinding.create_pass(
            id="ARC-001",
            domain="Architecture",
            category="Threat Modeling",
            name="Threat Model Artifact Exists",
            description="Repository contains a documented threat model",
            detail=f"Threat model artifact found at {rel_path}",
            evidence=f"File: {rel_path} ({file_size} bytes)",
            files=[rel_path],
        )

    return SecurityFinding.create_fail(
        id="ARC-001",
        domain="Architecture",
        category="Threat Modeling",
        name="Threat Model Artifact Exists",
        severity=Severity.HIGH,
        description="No threat model artifact found in the repository",
        detail="Missing structured threat model documenting assets, threats, trust boundaries, and mitigations",
        remediation="Create a threat model (e.g., docs/threat-model.md) analyzing system components using STRIDE or PASTA methodology.",
        references=["https://owasp.org/www-community/Threat_Modeling"],
    )


def check_architecture_diagram(repo_path: str) -> SecurityFinding:
    """Check if architecture or system design diagram exists."""
    extensions = (".drawio", ".png", ".svg", ".jpg", ".jpeg", ".puml", ".mermaid")
    keywords = ("architecture", "diagram", "system-design", "component-diagram", "c4")

    found_files = []

    for root, _, files in os.walk(repo_path):
        if any(part.startswith((".", "node_modules")) for part in root.split(os.sep)):
            continue

        for filename in files:
            lower = filename.lower()
            if lower.endswith(extensions) and any(kw in lower for kw in keywords):
                found_files.append(os.path.join(root, filename))

    if found_files:
        rel_paths = [os.path.relpath(f, repo_path) for f in found_files]
        return SecurityFinding.create_pass(
            id="ARC-002",
            domain="Architecture",
            category="System Design",
            name="Architecture Diagram Exists",
            description="Repository contains architecture or component design diagrams",
            detail=f"Found {len(found_files)} architecture diagram(s): {', '.join(rel_paths[:3])}",
            evidence=f"Diagrams: {', '.join(rel_paths)}",
            files=rel_paths,
        )

    return SecurityFinding.create_fail(
        id="ARC-002",
        domain="Architecture",
        category="System Design",
        name="Architecture Diagram Exists",
        severity=Severity.MEDIUM,
        description="No architecture or system design diagrams found",
        detail="Visual representation of system architecture, components, and communication channels is missing",
        remediation="Add an architecture diagram (e.g., docs/architecture.drawio, docs/architecture.png) documenting components and interactions.",
    )


def check_data_flow_diagram(repo_path: str) -> SecurityFinding:
    """Check if Data Flow Diagram (DFD) exists."""
    extensions = (".drawio", ".png", ".svg", ".puml", ".mermaid")
    keywords = ("dfd", "data-flow", "dataflow", "data_flow", "sequence")

    found_files = []

    for root, _, files in os.walk(repo_path):
        if any(part.startswith((".", "node_modules")) for part in root.split(os.sep)):
            continue

        for filename in files:
            lower = filename.lower()
            if lower.endswith(extensions) and any(kw in lower for kw in keywords):
                found_files.append(os.path.join(root, filename))

    if found_files:
        rel_paths = [os.path.relpath(f, repo_path) for f in found_files]
        return SecurityFinding.create_pass(
            id="ARC-003",
            domain="Architecture",
            category="Data Flow",
            name="Data Flow Diagram Exists",
            description="Repository contains data flow diagrams or sequence diagrams",
            detail=f"Data flow diagrams found: {', '.join(rel_paths[:2])}",
            evidence=f"Files: {', '.join(rel_paths)}",
            files=rel_paths,
        )

    return SecurityFinding.create_fail(
        id="ARC-003",
        domain="Architecture",
        category="Data Flow",
        name="Data Flow Diagram Exists",
        severity=Severity.LOW,
        description="No Data Flow Diagram (DFD) detected",
        detail="Data movement across trust boundaries and storage points is not visually documented",
        remediation="Create a Data Flow Diagram illustrating data ingress, processing, storage, and egress paths across trust boundaries.",
    )


def check_trust_boundaries(repo_path: str) -> SecurityFinding:
    """Check if trust boundaries and external integrations are documented."""
    doc_extensions = (".md", ".txt", ".rst")
    keywords = [
        "trust boundary",
        "trust boundaries",
        "external integration",
        "third-party service",
        "api boundary",
        "network zone",
        "security zone",
    ]

    for root, _, files in os.walk(repo_path):
        if any(part.startswith((".", "node_modules")) for part in root.split(os.sep)):
            continue

        for filename in files:
            if filename.lower().endswith(doc_extensions):
                filepath = os.path.join(root, filename)
                try:
                    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read().lower()

                    for kw in keywords:
                        if kw in content:
                            rel_path = os.path.relpath(filepath, repo_path)
                            return SecurityFinding.create_pass(
                                id="ARC-004",
                                domain="Architecture",
                                category="Trust Boundaries",
                                name="Trust Boundaries Documented",
                                description="Trust boundaries and external integration security are documented",
                                detail=f"Trust boundary documentation found in {rel_path}",
                                evidence=f"Matched '{kw}' in {rel_path}",
                                files=[rel_path],
                            )
                except OSError:
                    continue

    return SecurityFinding.create_fail(
        id="ARC-004",
        domain="Architecture",
        category="Trust Boundaries",
        name="Trust Boundaries Documented",
        severity=Severity.MEDIUM,
        description="Trust boundaries and external integrations are not documented",
        detail="No explicit documentation defining system trust boundaries, perimeter controls, or external dependency risks",
        remediation="Document all trust boundaries where data crosses privilege domains, and define validation/sanitization at each boundary.",
    )


def run_all(repo_path: str) -> List[SecurityFinding]:
    """
    Run all architecture security checks.

    Args:
        repo_path: Path to target repository

    Returns:
        List of SecurityFinding objects
    """
    return [
        check_threat_model(repo_path),
        check_architecture_diagram(repo_path),
        check_data_flow_diagram(repo_path),
        check_trust_boundaries(repo_path),
    ]
