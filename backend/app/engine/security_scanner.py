import re
from typing import List, Dict

def scan_security(code: str, language: str) -> List[Dict]:
    if not code or not isinstance(code, str):
        return []
    lines = code.splitlines()
    results = []
    for idx, line in enumerate(lines):
        lnum = idx + 1
        # HIGH severity
        if re.search(r"\beval\s*\(", line):
            results.append({"line": lnum, "type": "Eval Usage", "severity": "high", "message": "Use of eval() is dangerous.", "fix": "Remove or refactor eval usage."})
        if re.search(r"\bexec\s*\(", line):
            results.append({"line": lnum, "type": "Exec Usage", "severity": "high", "message": "Use of exec() is dangerous.", "fix": "Remove or refactor exec usage."})
        if re.search(r"os\.system\s*\(", line):
            results.append({"line": lnum, "type": "OS Command", "severity": "high", "message": "os.system() can lead to command injection.", "fix": "Use subprocess with args, not shell."})
        if re.search(r"subprocess\.run\s*\(.*shell\s*=\s*True", line):
            results.append({"line": lnum, "type": "Subprocess Shell", "severity": "high", "message": "subprocess.run(..., shell=True) is dangerous.", "fix": "Avoid shell=True in subprocess."})
        if re.search(r"system\s*\(", line) and language.lower() in ["c", "cpp", "c++"]:
            results.append({"line": lnum, "type": "System Call", "severity": "high", "message": "system() call in C/C++ is dangerous.", "fix": "Use safer APIs or validate input."})
        if re.search(r"Runtime\.getRuntime\(\)\.exec", line):
            results.append({"line": lnum, "type": "Java Runtime Exec", "severity": "high", "message": "Runtime.getRuntime().exec() is dangerous.", "fix": "Avoid direct exec calls."})
        # MEDIUM severity
        if re.search(r'("SELECT |"INSERT )\s*\+|\+\s*"SELECT |\+\s*"INSERT ', line):
            results.append({"line": lnum, "type": "SQL String Concatenation", "severity": "medium", "message": "SQL query built via string concatenation.", "fix": "Use parameterized queries."})
        if re.search(r'password\s*=\s*"[^"]+"', line, re.IGNORECASE):
            results.append({"line": lnum, "type": "Hardcoded Password", "severity": "medium", "message": "Hardcoded password detected.", "fix": "Remove hardcoded credentials."})
        if re.search(r'(AKIA|AIza|sk_live|ghp_)[0-9A-Za-z]{16,}', line):
            results.append({"line": lnum, "type": "API Key", "severity": "medium", "message": "Possible API key detected.", "fix": "Remove or secure API keys."})
        if re.search(r"pickle\.loads\s*\(", line):
            results.append({"line": lnum, "type": "Pickle Loads", "severity": "medium", "message": "pickle.loads() is unsafe with untrusted data.", "fix": "Avoid pickle.loads on untrusted input."})
        if re.search(r"yaml\.load\s*\(", line) and not re.search(r"SafeLoader", line):
            results.append({"line": lnum, "type": "YAML Load", "severity": "medium", "message": "yaml.load() without SafeLoader is unsafe.", "fix": "Use yaml.safe_load instead."})
        # LOW severity
        if re.search(r"print\s*\(", line) and not re.search(r"__name__\s*==\s*['\"]__main__['\"]", code):
            results.append({"line": lnum, "type": "Debug Print", "severity": "low", "message": "Debug print in production code.", "fix": "Remove or guard debug prints."})
        if re.search(r"except\s*:\s*pass", line):
            results.append({"line": lnum, "type": "Broad Exception", "severity": "low", "message": "Broad exception catch without logging.", "fix": "Log exception details."})
    return results
