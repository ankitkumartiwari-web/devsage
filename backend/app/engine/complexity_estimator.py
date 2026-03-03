# app/engine/complexity_estimator.py

class ComplexityEstimator:

    @staticmethod
    def estimate_complexity(static_result: dict) -> dict:
        try:
            nested_depth = static_result.get("nested_depth", 0)
            recursion_detected = static_result.get("recursion_detected", False)
            loop_count = static_result.get("loop_count", 0)
            large_file = static_result.get("large_file", False)

            # Time complexity
            if nested_depth >= 3:
                time_complexity = "O(n^3)"
            elif nested_depth >= 2:
                time_complexity = "O(n^2)"
            elif recursion_detected:
                time_complexity = "O(2^n)"
            elif loop_count == 1:
                time_complexity = "O(n)"
            else:
                time_complexity = "O(1)"

            # Space complexity
            if large_file:
                space_complexity = "O(n)"
            else:
                space_complexity = "O(1)"

            return {
                "time_complexity": time_complexity,
                "space_complexity": space_complexity,
            }

        except Exception as e:
            return {
                "time_complexity": "O(1)",
                "space_complexity": "O(1)",
                "error": f"Complexity estimation failed: {str(e)}"
            }