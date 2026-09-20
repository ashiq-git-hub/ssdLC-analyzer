# SSDLC Analyzer

A professional local-first Secure Software Development Lifecycle (SSDLC) security assessment platform.

## Overview

SSDLC Analyzer evaluates software repositories against security best practices across the complete software development lifecycle. It provides transparent security maturity scoring, detailed finding reports, and actionable remediation guidance.

## Features

- **Comprehensive Assessment**: Analyzes 6 SSDLC domains
  - Requirements (security policies, documentation)
  - Architecture (threat models, design artifacts)
  - Implementation (SAST, secret detection)
  - Testing (test coverage, security tests)
  - Supply Chain (dependency management, vulnerability scanning)
  - Lifecycle (CI/CD, DevSecOps automation)

- **Multiple Security Tools Integration**
  - Semgrep (SAST)
  - Gitleaks (secret detection)
  - Syft (SBOM generation)
  - Grype (dependency vulnerability scanning)

- **Transparent Scoring**
  - Weighted domain-based maturity scoring
  - Risk level calculation (CRITICAL, HIGH, MEDIUM, LOW, MINIMAL)
  - Severity-based finding classification

- **Multiple Interfaces**
  - Web UI (React + FastAPI)
  - Command-line interface
  - REST API

- **Persistent Storage**
  - SQLite-based scan history
  - Scan comparison capabilities

- **Professional Reports**
  - JSON export
  - Markdown export
  - HTML export

- **Security First**
  - Local processing (no data sent externally)
  - Secure ZIP extraction with path traversal protection
  - Archive bomb detection
  - Secret redaction in outputs

## Installation

### Prerequisites

- Python 3.8+
- Node.js 16+ (for frontend)

### Backend Setup

```bash
# Clone repository
cd "SSDLC Analyzer"

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Unix/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Frontend Setup

```bash
cd frontend
npm install
```

### Optional External Tools

For enhanced scanning capabilities, install:

```bash
# Semgrep (SAST)
pip install semgrep

# Gitleaks (secrets)
# Download from: https://github.com/gitleaks/gitleaks/releases

# Syft (SBOM)
# Download from: https://github.com/anchore/syft/releases

# Grype (vulnerabilities)
# Download from: https://github.com/anchore/grype/releases
```

## Usage

### Web Application

1. **Start Backend**:
```bash
python -m uvicorn backend.back:app --reload
# API available at: http://127.0.0.1:8000
```

2. **Start Frontend** (separate terminal):
```bash
cd frontend
npm run dev
# UI available at: http://localhost:5173
```

3. **Use the Web UI**:
   - Navigate to http://localhost:5173
   - Upload a ZIP archive of your repository
   - Click "Start security analysis"
   - View results, findings, and domain scores

### Command Line

```bash
# Basic scan
python -m scanner.cli /path/to/repository

# Export JSON report
python -m scanner.cli /path/to/repository --json report.json

# Export Markdown report
python -m scanner.cli /path/to/repository --markdown report.md

# Fail on HIGH or CRITICAL findings
python -m scanner.cli /path/to/repository --fail-on high

# Quiet mode (only exports)
python -m scanner.cli /path/to/repository --json report.json --quiet
```

### API

```bash
# Health check
curl http://127.0.0.1:8000/health

# Upload and scan repository
curl -X POST http://127.0.0.1:8000/scan \
  -F "file=@repository.zip"

# List scan history
curl http://127.0.0.1:8000/scans

# Get specific scan
curl http://127.0.0.1:8000/scans/{scan_id}

# Delete scan
curl -X DELETE http://127.0.0.1:8000/scans/{scan_id}
```

## Architecture

```
SSDLC Analyzer/
├── backend/
│   └── back.py              # FastAPI application
├── scanner/
│   ├── __init__.py
│   ├── cli.py               # CLI interface
│   ├── engine.py            # Scan orchestration
│   ├── models.py            # Data models
│   ├── scoring.py           # Scoring logic
│   ├── db.py                # SQLite storage
│   ├── checks/              # Security checks
│   │   ├── requirements.py
│   │   ├── architecture.py
│   │   ├── implementation.py
│   │   ├── testing.py
│   │   ├── supply_chain.py
│   │   └── lifecycle.py
│   ├── reporting/           # Report generators
│   │   ├── json_report.py
│   │   ├── markdown_report.py
│   │   └── html_report.py
│   └── utils/
│       └── archive.py       # Secure ZIP handling
├── frontend/
│   └── src/
│       ├── App.jsx          # Main application
│       └── ...
├── tests/                   # Test suite
├── docs/                    # Documentation
└── requirements.txt
```

## Security Checks

### Requirements Domain (Weight: 15%)
- SECURITY.md exists
- Authentication requirements documented
- Authorization requirements documented
- Input validation requirements documented
- Data protection requirements documented

### Architecture Domain (Weight: 20%)
- Threat model artifact exists
- Architecture diagram exists
- Data flow diagram exists
- Trust boundaries documented

### Implementation Domain (Weight: 30%)
- Semgrep SAST scan
- Gitleaks secret detection

### Testing Domain (Weight: 15%)
- Test suite exists
- Security tests exist
- Integration tests exist

### Supply Chain Domain (Weight: 10%)
- Dependency manifest exists
- Lockfile exists
- SBOM generation (Syft)
- Vulnerability scanning (Grype)

### Lifecycle Domain (Weight: 10%)
- CI/CD pipeline exists
- Automated testing in CI
- Security scanning in CI
- Branch protection configuration

## Scoring Methodology

**Overall Score** = Weighted average of domain scores

**Domain Score** = (Passed Checks / Applicable Checks) × 100

**Risk Level** is determined by:
- CRITICAL: Critical findings present OR 5+ high findings
- HIGH: 3+ high findings OR score < 30%
- MEDIUM: 1+ high findings OR score < 50%
- LOW: Score < 70%
- MINIMAL: Score ≥ 70% with no critical/high findings

Skipped checks (unavailable tools) do not count against the score.

## Limitations

- **Static Analysis Only**: Does not perform dynamic testing, penetration testing, or runtime analysis
- **Tool Dependencies**: Full coverage requires external tools (Semgrep, Gitleaks, Syft, Grype)
- **Pattern Matching**: Some checks use keyword matching and may produce false positives/negatives
- **Repository Contents**: Can only verify artifacts present in the repository
- **No Guarantees**: A clean scan does not guarantee absence of vulnerabilities

## Development

### Running Tests

```bash
pytest tests/
```

### Project Structure

The project follows a clean architecture:
- `backend/`: FastAPI REST API
- `scanner/`: Core scanning engine and checks
- `frontend/`: React web interface
- `tests/`: Automated test suite
- `docs/`: Additional documentation

## CI/CD Integration

Example GitHub Actions workflow:

```yaml
name: Security Assessment

on: [push, pull_request]

jobs:
  ssdlc-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install SSDLC Analyzer
        run: |
          pip install -r requirements.txt
      
      - name: Run Security Scan
        run: |
          python -m scanner.cli . --json scan-results.json --fail-on high
      
      - name: Upload Results
        uses: actions/upload-artifact@v3
        with:
          name: security-scan
          path: scan-results.json
```

## Contributing

1. Follow the existing code structure
2. Write tests for new checks
3. Update documentation
4. Ensure the analyzer can scan itself successfully

## License

See LICENSE file for details.

## Version

Current version: 2.0.0

---

**Security Note**: SSDLC Analyzer processes repositories locally. No source code or scan results are transmitted to external services.
