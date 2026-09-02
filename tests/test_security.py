from scanner.score import calculate_score


def test_score_with_all_passed():
    results = [
        {"passed": True},
        {"passed": True},
        {"passed": True},
    ]

    assert calculate_score(results) == 100.0


def test_score_with_half_passed():
    results = [
        {"passed": True},
        {"passed": False},
    ]

    assert calculate_score(results) == 50.0


def test_score_with_no_results():
    assert calculate_score([]) == 0


def test_score_with_no_passed_checks():
    results = [
        {"passed": False},
        {"passed": False},
    ]

    assert calculate_score(results) == 0.0