# SSDLC Analyzer Architecture

## Overview

SSDLC Analyzer is a security assessment tool that analyzes a software
repository against Secure Software Development Lifecycle practices.

The system is divided into four major layers:

1. User Interface
2. FastAPI Backend
3. SSDLC Scanner Engine
4. Security Tooling

## System Flow

User
  |
  v
Frontend
  |
  v
FastAPI Backend
  |
  v
Scanner Engine
  |
  +--> Requirements Checks
  |
  +--> Architecture Checks
  |
  +--> Implementation Checks
  |       |
  |       +--> Semgrep
  |       +--> Gitleaks
  |
  +--> Testing Checks
  |
  +--> Supply Chain Checks
  |       |
  |       +--> Syft
  |       +--> Grype
  |
  +--> Lifecycle Checks
  |
  v
Security Report
  |
  v
Score + Findings

## Components

### Frontend

Provides a user interface where a developer can submit a software project
for security analysis and view the resulting SSDLC report.

### Backend

The FastAPI backend receives the submitted project, validates it, invokes
the scanner engine, and returns structured results.

### Scanner Engine

The scanner engine executes security checks across six SSDLC domains:

- Requirements
- Architecture
- Implementation
- Testing
- Supply Chain
- Lifecycle Management

### Security Tooling

External security tools provide automated analysis:

- Semgrep — Static Application Security Testing
- Gitleaks — Secret detection
- Syft — Software Bill of Materials generation
- Grype — Dependency vulnerability scanning

## Output

Each check produces:

- Domain
- Check name
- PASS/FAIL status
- Detailed result

The final maturity score is calculated from the percentage of passed checks.