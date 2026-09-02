import os


def check_test_suite_exists(repo_path):
    test_dir = os.path.join(repo_path, "tests")

    passed = os.path.isdir(test_dir)

    return {
        "domain": "Testing",
        "name": "Test Suite Exists",
        "passed": passed,
        "detail": (
            "Test directory found: tests"
            if passed
            else "No tests directory found"
        ),
    }


def check_security_tests_exist(repo_path):
    test_dir = os.path.join(repo_path, "tests")

    if not os.path.isdir(test_dir):
        return {
            "domain": "Testing",
            "name": "Security Tests Exist",
            "passed": False,
            "detail": "No tests directory found",
        }

    for root, _, files in os.walk(test_dir):
        for filename in files:
            lower = filename.lower()

            if (
                lower.startswith("test_")
                and "security" in lower
            ):
                return {
                    "domain": "Testing",
                    "name": "Security Tests Exist",
                    "passed": True,
                    "detail": f"Security-related test found: {filename}",
                }

    return {
        "domain": "Testing",
        "name": "Security Tests Exist",
        "passed": False,
        "detail": "No security-related test found",
    }


def run_all(repo_path):
    return [
        check_test_suite_exists(repo_path),
        check_security_tests_exist(repo_path),
    ]