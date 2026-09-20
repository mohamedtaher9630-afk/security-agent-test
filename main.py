import os
import sys
import ast
import json
import subprocess
from github import Github
import google.generativeai as genai

# 1. Environment Setup & Configuration
GEMINI_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
REPO_NAME = os.getenv("GITHUB_REPOSITORY")

if not GEMINI_KEY or not GITHUB_TOKEN or not REPO_NAME:
    print("Error: Missing required environment variables.")
    sys.exit(1)

genai.configure(api_key=GEMINI_KEY)

# Dynamic Model Selection - Choose available active model automatically
try:
    available_models = [
        m.name for m in genai.list_models() 
        if 'generateContent' in m.supported_generation_methods
    ]
    flash_model = next((m for m in available_models if 'flash' in m), None)
    chosen_model = flash_model if flash_model else (available_models[0] if available_models else 'gemini-pro')
    model = genai.GenerativeModel(chosen_model)
    print(f"Info: Using model -> {chosen_model}")
except Exception as e:
    print(f"Warning: Falling back to default model due to: {e}")
    model = genai.GenerativeModel('gemini-pro')

# 2. Diff-Based File Detection
def get_changed_files():
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD~1", "HEAD"],
            capture_output=True, text=True, check=True
        )
        files = [f.strip() for f in result.stdout.split("\n") if f.strip().endswith(".py")]
        return [f for f in files if not f.startswith("tests/") and "venv" not in f and f != "main.py"]
    except Exception as e:
        print(f"Warning: Could not fetch git diff, scanning app.py: {e}")
        return ["app.py"] if os.path.exists("app.py") else []

# 3. AST Syntax Validator
def validate_python_code(code_str):
    try:
        ast.parse(code_str)
        return True, ""
    except SyntaxError as e:
        return False, str(e)

# 4. System Instructions
SYSTEM_INSTRUCTION = """
You are a Principal DevSecOps & Application Security Engineer.
Analyze the provided source code for vulnerabilities.
Tasks:
1. Identify true security vulnerabilities and ignore false positives.
2. Assign severity levels: CRITICAL, HIGH, or MEDIUM.
3. Patch the code WITHOUT breaking or altering the underlying business logic.
4. Output STRICTLY a valid JSON object with the following schema:
   {
     "report": "A detailed Markdown report explaining issues found and patches applied.",
     "patched_code": "The complete patched source code as plain text. Do NOT wrap in markdown triple backticks."
   }
"""

def analyze_and_fix(file_path, code_content):
    prompt = f"{SYSTEM_INSTRUCTION}\n\nFile Path: {file_path}\nCode Content:\n{code_content}"
    response = model.generate_content(prompt)
    
    raw_text = response.text.strip()
    if "```json" in raw_text:
        raw_text = raw_text.split("```json")[1].split("```")[0].strip()
    elif "```" in raw_text:
        raw_text = raw_text.split("```")[1].split("```")[0].strip()
        
    try:
        data = json.loads(raw_text)
        report = data.get("report", "No security report provided.")
        patched_code = data.get("patched_code", code_content)
        
        is_valid, error = validate_python_code(patched_code)
        if not is_valid:
            print(f"Warning: AI generated invalid syntax for {file_path}: {error}. Reverting to original.")
            return report, code_content
            
        return report, patched_code
    except Exception as e:
        print(f"Warning: Failed to parse AI JSON response: {e}")
        return "No critical vulnerabilities found or failed parsing.", code_content

# 5. Core Execution & GitHub Automation
def main():
    files_to_scan = get_changed_files()
    if not files_to_scan:
        print("Success: No modified Python files to scan.")
        sys.exit(0)

    gh = Github(GITHUB_TOKEN)
    repo = gh.get_repo(REPO_NAME)
    
    full_report = "## 🛡️ Enterprise AI DevSecOps Audit Report\n\n"
    has_fixes = False
    branch_name = "ai-security-patch-pro"

    main_branch = repo.get_branch("main")
    
    try:
        ref = repo.get_git_ref(f"heads/{branch_name}")
        ref.edit(main_branch.commit.sha, force=True)
    except Exception:
        repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=main_branch.commit.sha)

    for file_path in files_to_scan:
        if not os.path.exists(file_path):
            continue
        print(f"Scanning {file_path}...")
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        report, patched_code = analyze_and_fix(file_path, content)
        
        if patched_code != content:
            has_fixes = True
            full_report += f"### 📄 `{file_path}`\n{report}\n\n---\n"
            
            try:
                file_obj = repo.get_contents(file_path, ref=branch_name)
                repo.update_file(
                    path=file_path,
                    message=f"security: enterprise auto-patch for {file_path}",
                    content=patched_code,
                    sha=file_obj.sha,
                    branch=branch_name
                )
            except Exception as e:
                print(f"Error updating file on branch: {e}")

    if has_fixes:
        pr_title = "🔒 Enterprise Security Patch: Automated AI Vulnerability Remediation"
        prs = repo.get_pulls(state="open", head=f"{repo.owner.login}:{branch_name}")
        if prs.totalCount == 0:
            repo.create_pull(
                title=pr_title,
                body=full_report,
                head=branch_name,
                base="main"
            )
            print("Success: Enterprise Pull Request created successfully!")
        else:
            print("Info: Pull Request updated successfully.")
    else:
        print("Success: Code passed all enterprise security checks cleanly!")

if __name__ == "__main__":
    main()
