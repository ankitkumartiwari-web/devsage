class PromptBuilder:

    @staticmethod
    def build_prompt(
        code: str,
        language: str,
        mode: str,
        static_data: dict,
        complexity_data: dict,
        security_data: list | None = None,
        dependency_data: list | None = None,
    ):

        security_data = security_data or []
        dependency_data = dependency_data or []

        system_prompt = (
            "You are DevSage, an elite AI coding mentor.\n"
            "Return STRICT JSON with EXACT schema:\n"
            "{\n"
            '  "summary": string,\n'
            '  "bugs": [ { "line": number, "message": string, "fix": string } ],\n'
            '  "security": [ { "line": number, "message": string, "severity": "low|medium|high" } ],\n'
            '  "optimization": [string],\n'
            '  "mentor_questions": [string],\n'
            '  "hints": [string],\n'
            '  "exercise": [string],\n'
            '  "emotional_feedback": string\n'
            "}\n"
            "Rules:\n"
            "- summary must be plain string\n"
            "- line numbers must be 1-based\n"
            "- fix must be full replacement line\n"
            "- Do NOT return static analysis or complexity\n"
        )

        user_prompt = f"""
Language: {language}
Mode: {mode}

Static Analysis:
{static_data}

Complexity:
{complexity_data}

Security Findings:
{security_data}

Dependency Findings:
{dependency_data}

Code:
{code}
"""

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]