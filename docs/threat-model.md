# SSDLC Analyzer Threat Model

## Scope

This threat model covers the SSDLC Analyzer application, including the
frontend, FastAPI backend, scanner engine, uploaded repositories, and
external security tools.

## Assets

- Uploaded source code
- Security scan results
- Repository metadata
- Generated SBOM
- Vulnerability findings
- Application configuration

## Trust Boundaries

### Boundary 1 — User to Frontend

The user provides an untrusted software repository.

### Boundary 2 — Frontend to Backend

The uploaded project is transferred to the FastAPI backend.

### Boundary 3 — Backend to Scanner

The backend passes repository contents to security analysis tools.

### Boundary 4 — Scanner to External Tools

The scanner invokes tools such as Semgrep, Gitleaks, Syft, and Grype.

## Threats

### Spoofing

An attacker could attempt to impersonate an authorized user if
authentication is implemented incorrectly.

### Tampering

An uploaded repository or scan result could be modified during processing.

### Repudiation

Insufficient logging could make it difficult to determine who initiated a
scan.

### Information Disclosure

Scan results could contain sensitive source-code information or secret
detection findings.

### Denial of Service

A maliciously large or complex repository could consume excessive CPU,
memory, disk space, or execution time.

### Elevation of Privilege

Unsafe execution of uploaded project content could potentially allow
malicious code to execute with backend privileges.

## Mitigations

- Treat uploaded repositories as untrusted input.
- Validate uploaded archive types and sizes.
- Extract archives into isolated temporary directories.
- Prevent path traversal during archive extraction.
- Never execute uploaded application code directly.
- Apply execution timeouts to security tools.
- Exclude generated files and virtual environments where appropriate.
- Do not expose secrets in scan output.
- Limit resource consumption.
- Validate all backend inputs.
- Run security tooling with minimum required privileges.

## STRIDE Summary

| Threat | Example | Mitigation |
|---|---|---|
| Spoofing | Unauthorized scan request | Authentication |
| Tampering | Modified uploaded project | Validation and integrity checks |
| Repudiation | Missing scan records | Logging |
| Information Disclosure | Secrets exposed in results | Redaction |
| Denial of Service | Huge repository | Size/time/resource limits |
| Elevation of Privilege | Malicious uploaded code | Isolation and no execution |