import json
import os
import shutil
import subprocess


def check_semgrep(repo_path):
    semgrep = shutil.which("semgrep")

    if not semgrep:
        return {
            "domain": "Implementation",
            "name": "Semgrep SAST",
            "passed": False,
            "detail": "Semgrep executable not found",
        }

    command = [
        semgrep,
        "scan",
        "--config",
        "auto",
        "--json",
        "--exclude",
        ".venv",
        "--exclude",
        ".venv-1",
        "--exclude",
        ".git",
        "--exclude",
        "sbom.json",
        "--exclude",
        "test-sbom.json",
        "--exclude",
        "__pycache__",
        "--exclude",
        "*.zip",
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
            timeout=120,
        )

        try:
            data = json.loads(result.stdout)
            findings = data.get("results", [])
        except json.JSONDecodeError:
            return {
                "domain": "Implementation",
                "name": "Semgrep SAST",
                "passed": False,
                "detail": "Semgrep returned invalid JSON output",
            }

        if findings:
            return {
                "domain": "Implementation",
                "name": "Semgrep SAST",
                "passed": False,
                "detail": f"{len(findings)} security finding(s) detected",
            }

        return {
            "domain": "Implementation",
            "name": "Semgrep SAST",
            "passed": True,
            "detail": "No security findings detected by Semgrep",
        }

    except subprocess.TimeoutExpired:
        return {
            "domain": "Implementation",
            "name": "Semgrep SAST",
            "passed": False,
            "detail": "Semgrep scan timed out",
        }

    except Exception as error:
        return {
            "domain": "Implementation",
            "name": "Semgrep SAST",
            "passed": False,
            "detail": f"Semgrep error: {error}",
        }


def check_gitleaks(repo_path):
    gitleaks = shutil.which("gitleaks")

    if not gitleaks:
        return {
            "domain": "Implementation",
            "name": "Gitleaks Secret Detection",
            "passed": False,
            "detail": "Gitleaks executable not found",
        }

    command = [
        gitleaks,
        "detect",
        "--source",
        repo_path,
        "--no-banner",
        "--redact",
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

        if result.returncode == 0:
            return {
                "domain": "Implementation",
                "name": "Gitleaks Secret Detection",
                "passed": True,
                "detail": "No hardcoded secrets detected by Gitleaks",
            }

        return {
            "domain": "Implementation",
            "name": "Gitleaks Secret Detection",
            "passed": False,
            "detail": "Potential hardcoded secrets detected by Gitleaks",
        }

    except subprocess.TimeoutExpired:
        return {
            "domain": "Implementation",
            "name": "Gitleaks Secret Detection",
            "passed": False,
            "detail": "Gitleaks scan timed out",
        }

    except Exception as error:
        return {
            "domain": "Implementation",
            "name": "Gitleaks Secret Detection",
            "passed": False,
            "detail": f"Gitleaks error: {error}",
        }


def run_all(repo_path):
    return [
        check_semgrep(repo_path),
        check_gitleaks(repo_path),
    ]