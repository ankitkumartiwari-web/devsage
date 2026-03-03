import os
import json
import re


RISKY_JS_PACKAGES = {
    "vm2",
    "crypto-js",
    "child_process"
}

DEPRECATED_PY_PACKAGES = {
    "urllib2",
    "imp"
}


def scan_dependencies(project_path: str) -> list[dict]:
    findings = []

    if not project_path:
        return findings

    # ---------------------------
    # package.json
    # ---------------------------
    package_json_path = os.path.join(project_path, "package.json")

    if os.path.exists(package_json_path):
        try:
            with open(package_json_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            dependencies = data.get("dependencies", {})
            dependencies.update(data.get("devDependencies", {}))

            for pkg, version in dependencies.items():

                if version.startswith("^") or version.startswith("*"):
                    findings.append({
                        "type": "Unpinned Dependency",
                        "package": pkg,
                        "version": version,
                        "severity": "medium",
                        "recommendation": "Pin exact version instead of using ^ or *.",
                        "fix_version": version.lstrip("^*")
                    })

                if pkg in RISKY_JS_PACKAGES:
                    findings.append({
                        "type": "Risky Package",
                        "package": pkg,
                        "version": version,
                        "severity": "high",
                        "recommendation": "Review necessity and security implications."
                    })

        except Exception:
            pass

    # ---------------------------
    # requirements.txt
    # ---------------------------
    requirements_path = os.path.join(project_path, "requirements.txt")

    if os.path.exists(requirements_path):
        try:
            with open(requirements_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            for line in lines:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                if "==" not in line:
                    findings.append({
                        "type": "Unpinned Python Dependency",
                        "package": line,
                        "version": "unspecified",
                        "severity": "medium",
                        "recommendation": "Pin version using == for reproducibility."
                    })

                pkg_name = re.split(r"[=<>!]", line)[0]

                if pkg_name in DEPRECATED_PY_PACKAGES:
                    findings.append({
                        "type": "Deprecated Python Package",
                        "package": pkg_name,
                        "version": "unknown",
                        "severity": "high",
                        "recommendation": "Replace deprecated package."
                    })

        except Exception:
            pass

    return findings