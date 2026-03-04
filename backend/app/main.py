from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import threading

from app.engine.static_analyzer import analyze_code
from app.engine.complexity_estimator import ComplexityEstimator
from app.engine.security_scanner import scan_security
from app.engine.dependency_scanner import scan_dependencies
from app.engine.prompt_builder import PromptBuilder
from app.engine.openrouter_client import call_openrouter
from app.engine.merger import merge_results

app = FastAPI()

# ============================================================
# REQUEST LOCK (prevents multiple AI requests)
# ============================================================

request_lock = threading.Lock()


# ============================================================
# REQUEST MODELS
# ============================================================

class AnalyzeRequest(BaseModel):
    code: str
    language: str
    mode: str
    project_path: Optional[str] = None


class FixRequest(BaseModel):
    code: str
    language: str
    issue: str


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health():
    return {"status": "ok"}


# ============================================================
# ANALYZE ENDPOINT
# ============================================================

@app.post("/analyze")
def analyze(request: AnalyzeRequest):

    # ---------------------------
    # LOCK CHECK
    # ---------------------------
    if not request_lock.acquire(blocking=False):
        return {
            "summary": "Server busy. Please try again shortly.",
            "bugs": [],
            "security": [],
            "optimization": [],
            "mentor_questions": [],
            "hints": [],
            "exercise": "",
            "emotional_feedback": ""
        }

    try:
        print("MODE:", request.mode)

        static_result = analyze_code(request.code)
        complexity = ComplexityEstimator.estimate_complexity(static_result)
        security = scan_security(request.code, request.language)

        dependencies = []
        if request.project_path:
            dependencies = scan_dependencies(request.project_path)

        # ---------------------------
        # WORKSPACE MODE (NO AI)
        # ---------------------------
        if request.mode == "workspace":
            merged = merge_results(
                static_result,
                complexity,
                security + dependencies,
                {}
            )

            merged["summary"] = "Workspace security scan completed."
            return merged

        # ---------------------------
        # REVIEW MODE (WITH AI)
        # ---------------------------
        messages = PromptBuilder.build_prompt(
            code=request.code,
            language=request.language,
            mode=request.mode,
            static_data=static_result,
            complexity_data=complexity,
            security_data=security,
            dependency_data=dependencies,
        )

        print("OPENROUTER CALLED")

        ai_result = call_openrouter(messages)

        # Safety guard
        if not isinstance(ai_result, dict):
            ai_result = {
                "summary": str(ai_result),
                "bugs": [],
                "optimization": [],
                "mentor_questions": [],
                "hints": [],
                "exercise": "",
                "emotional_feedback": ""
            }

        return merge_results(
            static_result,
            complexity,
            security + dependencies,
            ai_result,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "message": "DevSage backend failure",
                "error": str(e)
            }
        )

    finally:
        request_lock.release()


# ============================================================
# AI FIX ENDPOINT
# ============================================================

@app.post("/fix")
def ai_fix(request: FixRequest):

    if not request_lock.acquire(blocking=False):
        return {
            "fixed_code": "",
            "message": "Server busy. Try again shortly."
        }

    try:
        prompt = [
            {
                "role": "system",
                "content": "You are a strict code fixer. Return ONLY corrected code. No explanations."
            },
            {
                "role": "user",
                "content": f"""
Language: {request.language}

Issue:
{request.issue}

Code:
{request.code}

Return ONLY corrected code.
"""
            }
        ]

        print("AI FIX CALLED")

        ai_response = call_openrouter(prompt, raw=True)

        if isinstance(ai_response, str):
            fixed_code = ai_response.strip()
        else:
            fixed_code = str(ai_response).strip()

        if not fixed_code:
            raise ValueError("AI returned empty fix.")

        return {
            "fixed_code": fixed_code
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "message": "DevSage fix failure",
                "error": str(e)
            }
        )

    finally:
        request_lock.release()