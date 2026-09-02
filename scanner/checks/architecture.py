import os


def check_threat_model_exists(repo_path):
    candidates = [
        "threat-model.json",
        "threat_model.json",
        "threatmodel.json",
        "stride.md",
        "threat-model.md"
    ]

    found_file = None

    for root, _, files in os.walk(repo_path):
        for filename in files:
            if filename.lower() in candidates:
                found_file = os.path.join(root, filename)
                break

        if found_file:
            break

    return {
        "domain": "Architecture",
        "name": "Threat model artifact exists",
        "passed": found_file is not None,
        "detail": f"Found: {found_file}" if found_file else "No threat model file found"
    }


def check_architecture_diagram_exists(repo_path):
    extensions = (".drawio", ".png", ".svg")
    keywords = ("architecture", "diagram", "dfd")

    found_file = None

    for root, _, files in os.walk(repo_path):
        for filename in files:
            lower = filename.lower()

            if lower.endswith(extensions) and any(
                keyword in lower for keyword in keywords
            ):
                found_file = os.path.join(root, filename)
                break

        if found_file:
            break

    return {
        "domain": "Architecture",
        "name": "Architecture diagram exists",
        "passed": found_file is not None,
        "detail": f"Found: {found_file}" if found_file else "No architecture diagram found"
    }


def run_all(repo_path):
    return [
        check_threat_model_exists(repo_path),
        check_architecture_diagram_exists(repo_path)
    ]
