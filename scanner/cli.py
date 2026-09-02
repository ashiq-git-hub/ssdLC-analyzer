import sys
import os

from scanner.score import calculate_score
from scanner.checks import architecture
from scanner.checks import implementation
from scanner.checks import requirements
from scanner.checks import testing

try:
    from scanner.checks import supply_chain
except ImportError:
    supply_chain = None

try:
    from scanner.checks import lifecycle
except ImportError:
    lifecycle = None


def run_scanner(repo_path):
    results = []

    results.extend(requirements.run_all(repo_path))
    results.extend(architecture.run_all(repo_path))
    results.extend(implementation.run_all(repo_path))
    results.extend(testing.run_all(repo_path))

    if supply_chain is not None:
        results.extend(supply_chain.run_all(repo_path))

    if lifecycle is not None:
        results.extend(lifecycle.run_all(repo_path))

    return results


def print_report(results):
    print()
    print("=== SSDLC Analyzer Report ===")
    print()

    for result in results:
        status = "PASS" if result["passed"] else "FAIL"

        print(
            f"[{status}] "
            f"({result['domain']}) "
            f"{result['name']} - "
            f"{result['detail']}"
        )

    score = calculate_score(results)

    print()
    print(f"Score: {sum(1 for r in results if r['passed'])}/{len(results)} ({score}%)")
    print()


def main():
    if len(sys.argv) != 2:
        print("Usage: python -m scanner.cli <repository_path>")
        sys.exit(1)

    repo_path = os.path.abspath(sys.argv[1])

    if not os.path.isdir(repo_path):
        print(f"Error: Repository path does not exist: {repo_path}")
        sys.exit(1)

    results = run_scanner(repo_path)
    print_report(results)


if __name__ == "__main__":
    main()