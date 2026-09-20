# 🛡️ Enterprise DevSecOps AI Security Agent

An automated, AI-powered DevSecOps pipeline that integrates Google Gemini with GitHub Actions to perform continuous code auditing, automated vulnerability patching, and safe Abstract Syntax Tree (AST) validation before deployment.

---

## 🌟 Key Features

* **🤖 Autonomous Security Scanning**: Automatically triggers on code modifications to perform real-time security analysis.
* **🧠 Advanced AI Audit**: Powered by `gemini-3.6-flash` to detect true security risks (SQLi, XSS, Hardcoded Secrets) while minimizing false positives.
* **⚡ Automated AST Validation**: Validates generated code patches using Python's `ast` module to ensure fixes contain no syntax errors before applying them.
* **🔀 Auto-PR Generation**: Creates structured Pull Requests with detailed Markdown vulnerability reports and proposed fixes.
* **🔒 Enterprise Gatekeeping**: Integrated with GitHub Branch Protection Rules to enforce status checks prior to merging into `main`.

---

## 🏗️ Architecture & Workflow
