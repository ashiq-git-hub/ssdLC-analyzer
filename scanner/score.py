def calculate_score(results):
    if not results:
        return 0

    passed = sum(1 for result in results if result["passed"])
    total = len(results)

    return round((passed / total) * 100, 1)
