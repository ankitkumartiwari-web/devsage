def calculate_score(static_result: dict, ai_result: dict, issues: list) -> int:
    score = 100

    # Static penalties
    if static_result.get("nested_depth", 0) >= 2:
        score -= 15

    if static_result.get("recursion_detected", False):
        score -= 20

    if static_result.get("long_functions", 0) > 0:
        score -= 10

    if static_result.get("large_file", False):
        score -= 10

    # AI bug penalties
    score -= min(len(ai_result.get("bugs", [])) * 2, 10)

    # Security / Dependency penalties
    for issue in issues or []:
        severity = issue.get("severity", "low").lower()

        if severity == "critical":
            score -= 20
        elif severity == "high":
            score -= 10
        elif severity == "medium":
            score -= 5
        elif severity == "low":
            score -= 2

    return max(score, 0)


def calculate_risk_score(issues: list) -> int:
    risk = 0

    for issue in issues or []:
        severity = issue.get("severity", "low").lower()

        if severity == "critical":
            risk += 15
        elif severity == "high":
            risk += 7
        elif severity == "medium":
            risk += 3
        elif severity == "low":
            risk += 1

    return risk


def merge_results(static_result, complexity, issues, ai_result):
    ai_result = ai_result or {}
    issues = issues or []

    final_time = complexity.get("time_complexity", "O(1)")
    final_space = complexity.get("space_complexity", "O(1)")

    score = calculate_score(static_result, ai_result, issues)
    risk_score = calculate_risk_score(issues)

    return {
        "summary": ai_result.get("summary", "Hybrid analysis completed."),
        "bugs": ai_result.get("bugs", []),
        "security": issues,
        "optimization": ai_result.get("optimization", []),
        "time_complexity": final_time,
        "space_complexity": final_space,
        "score": score,
        "risk_score": risk_score,
        "mentor_questions": ai_result.get("mentor_questions", []),
        "hints": ai_result.get("hints", []),
        "exercise": ai_result.get("exercise", []),
        "emotional_feedback": ai_result.get("emotional_feedback", "")
    }