import os
import json
import requests

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


def call_openrouter(messages: list[dict], raw: bool = False):

    if not OPENROUTER_API_KEY:
        print("❌ OPENROUTER_API_KEY missing")
        return _fallback(raw, "Missing API key")

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://devsage-9qlh.onrender.com",
        "X-Title": "DevSage"
    }

    try:
        response = requests.post(
            OPENROUTER_URL,
            headers=headers,
            json={
                "model": "openai/gpt-4o-mini",
                "messages": messages,
                "temperature": 0.2,
                max_tokens": 800,
            },
            timeout=30,
        )

        print("OPENROUTER STATUS:", response.status_code)

        if response.status_code != 200:
            print("OPENROUTER BODY:", response.text)
            return _fallback(raw, f"Status {response.status_code}")

        data = response.json()
        content = data["choices"][0]["message"]["content"]

        if raw:
            return content.strip()

        try:
            parsed = json.loads(content)
            return {
                "summary": parsed.get("summary", ""),
                "bugs": parsed.get("bugs", []),
                "security": parsed.get("security", []),
                "optimization": parsed.get("optimization", []),
                "mentor_questions": parsed.get("mentor_questions", []),
                "hints": parsed.get("hints", []),
                "exercise": parsed.get("exercise", ""),
                "emotional_feedback": parsed.get("emotional_feedback", ""),
            }
        except:
            return _fallback(raw, "AI returned non-JSON response")

    except Exception as e:
        print("❌ OpenRouter exception:", str(e))
        return _fallback(raw, str(e))


def _fallback(raw: bool, message: str):
    if raw:
        return "AI request failed."

    return {
        "summary": message,
        "bugs": [],
        "security": [],
        "optimization": [],
        "mentor_questions": [],
        "hints": [],
        "exercise": "",
        "emotional_feedback": message,
    }