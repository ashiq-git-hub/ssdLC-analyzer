import os


def check_security_file_exists(repo_path):
    found = None

    for root, _, files in os.walk(repo_path):
        if "SECURITY.md" in files:
            found = os.path.join(root, "SECURITY.md")
            break

    return {
        "domain": "Requirements",
        "name": "SECURITY.md present",
        "passed": found is not None,
        "detail": f"Found {found}" if found else "No SECURITY.md file found"
    }


def check_auth_requirements(repo_path):
    keywords = [
        "authentication",
        "authorization",
        "login",
        "password",
        "access control",
        "auth"
    ]

    for root, _, files in os.walk(repo_path):
        for filename in files:
            if not filename.lower().endswith((".md", ".txt", ".rst")):
                continue

            path = os.path.join(root, filename)

            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as file:
                    content = file.read().lower()

                if any(keyword in content for keyword in keywords):
                    return {
                        "domain": "Requirements",
                        "name": "Auth requirements documented",
                        "passed": True,
                        "detail": "Found auth-related text in a doc file"
                    }

            except OSError:
                pass

    return {
        "domain": "Requirements",
        "name": "Auth requirements documented",
        "passed": False,
        "detail": "No authentication/authorization requirements found"
    }


def run_all(repo_path):
    return [
        check_security_file_exists(repo_path),
        check_auth_requirements(repo_path)
    ]
