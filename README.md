<div align="center">

<table>
  <tr>
    <td align="right" style="vertical-align: middle;">
      <img width="60"
           src="https://github.com/user-attachments/assets/cbbddb1b-00a0-4022-94ba-bd159611f1c1" />
    </td>
    <td width="20"></td>
    <td align="left" style="vertical-align: middle;">
      <h1 style="margin: 0;">DevSage</h1>
    </td>
  </tr>
</table>

</div>





[![Version](https://img.shields.io/badge/version-0.0.2-blue.svg)](#)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](#)
[![VS Code](https://img.shields.io/badge/vscode-%3E%3D1.70.0-blue.svg)](#)

---

## Overview

DevSage is an AI-powered intelligent code mentor and security scanner for Visual Studio Code. It delivers static analysis, complexity estimation, security vulnerability detection, dependency risk assessment, risk scoring, quick fixes, and workspace-wide analysis—all seamlessly integrated into your editor.

---

## Key Features

- Static code analysis for early bug detection
- Complexity estimation for performance insights
- Security scanning for vulnerability awareness
- Dependency risk detection for safer projects
- Risk scoring to prioritize issues
- Quick Fixes for instant remediation
- Workspace analysis for holistic review

---

## Why DevSage?

Traditional linters highlight errors. DevSage explains risk, prioritizes issues, guides improvement, and encourages learning. It transforms code review from error-spotting to actionable, educational insight—empowering developers to write safer, smarter code.

---

## Installation

Install from VS Code Marketplace

Search for DevSage in the VS Code Marketplace and install.

Install via VSIX

```
code --install-extension devsage-extension-0.1.0.vsix
```

---

## Usage Guide

- Right-click → Review Code
- Scan Workspace for security and quality
- Quick Fix lightbulb for instant remediation
- Export Security Report for compliance

Empty sections are hidden for clarity.
Severity is always normalized (HIGH / MEDIUM / LOW) and issues are sorted by risk score.

---

## Example Output

```
══════════════════════════
🔍 DevSage Code Review
══════════════════════════

📊 Score: 87
🛡 Risk Score: 14

⏱ Time Complexity: O(n)
💾 Space Complexity: O(1)

🐞 Bugs:
	[HIGH - 8.5] Possible null dereference
		 Line: 42
		 Fix: Add null check

🛡 Security Issues:
	[MEDIUM - 5.0] Hardcoded password detected
		 Line: 17
		 OWASP: A2

📦 Dependency Issues:
	[HIGH - 9.0] vm2
		 Type: Risky Package
		 Version: ^3.9.11
		 Recommendation: Review necessity and security implications.

💡 Emotional Feedback:
Great job! Only minor issues found.
```

---

## Security & Scoring Philosophy

- CVSS-inspired risk model
- Deterministic scoring
- Structured findings
- No vague warnings
- Actionable remediation guidance

---

## Roadmap

- CVE/OSV integration
- Dashboard UI
- SaaS tier
- Team analytics
- Multi-language expansion

---

## License & Author

MIT License

**Ankit Kumar Tiwari**

[GitHub](https://github.com/ankitkumartiwari-web/devsage)

[Linkedin](https://www.linkedin.com/in/ankit-kumar-tiwari-565a56257/)


---
