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

[ Code Commit / PR ]
│
▼
[ GitHub Actions Runner ]
│
├──► Fetch Git Diff
│
├──► Send Code to Gemini API (gemini-3.6-flash)
│
├──► Validate Patch with Python AST Parser
│
▼
[ Open Auto-Fix Pull Request & Enforce Branch Protection ]


---

## 🚀 Tech Stack

* **Language**: Python 3.10+
* **AI Model**: Google Gemini API (`google-generativeai`)
* **CI/CD Platform**: GitHub Actions
* **GitHub Integration**: PyGithub
* **Code Parsing**: Python Abstract Syntax Tree (`ast`)

---

## 🛠️ Setup & Configuration

### 1. Environment Secrets
Configure the following secrets in your repository settings (**Settings > Secrets and variables > Actions**):

| Secret Name | Description |
| :--- | :--- |
| `GEMINI_API_KEY` | Google Gemini API Key |
| `GH_TOKEN` | GitHub Personal Access Token (with repo scope) |

### 2. Workflow Trigger (`.github/workflows/security-scan.yml`)
The action monitors changes to `.py` files on push and pull request events, executing the `main.py` pipeline orchestration script.

---

## 📜 License
