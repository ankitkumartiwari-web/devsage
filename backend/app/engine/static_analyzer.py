import re


def analyze_code(code: str) -> dict:
    try:
        if not code:
            return default_result()

        lines = code.splitlines()
        line_count = len(lines)

        # Count loops (language-agnostic keywords)
        loop_pattern = r"\b(for|while)\b"
        loop_count = len(re.findall(loop_pattern, code))

        # --- Nested depth detection (indentation-aware) ---
        nested_depth = 0
        current_depth = 0
        indent_stack = []

        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue

            indent = len(line) - len(line.lstrip())

            # Adjust stack
            while indent_stack and indent < indent_stack[-1]:
                indent_stack.pop()
                current_depth -= 1

            if re.search(loop_pattern, stripped):
                indent_stack.append(indent)
                current_depth += 1
                nested_depth = max(nested_depth, current_depth)

        # Recursion detection
        recursion_detected = False
        function_pattern = r"\bdef\s+(\w+)"
        matches = re.findall(function_pattern, code)

        for func in matches:
            occurrences = code.count(f"{func}(")
            if occurrences > 1:
                recursion_detected = True

        long_functions = 1 if line_count > 40 else 0
        large_file = line_count > 300

        return {
            "line_count": line_count,
            "loop_count": loop_count,
            "nested_depth": nested_depth,
            "recursion_detected": recursion_detected,
            "long_functions": long_functions,
            "large_file": large_file
        }

    except Exception as e:
        return {
            "line_count": 0,
            "loop_count": 0,
            "nested_depth": 0,
            "recursion_detected": False,
            "long_functions": 0,
            "large_file": False,
            "error": f"Static analysis failed: {str(e)}"
        }


def default_result():
    return {
        "line_count": 0,
        "loop_count": 0,
        "nested_depth": 0,
        "recursion_detected": False,
        "long_functions": 0,
        "large_file": False
    }