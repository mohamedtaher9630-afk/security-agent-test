import os
import sys
import json
import ast
import google.generativeai as genai
from github import Github

# 1. Verification of environment setup
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GH_TOKEN = os.getenv("GH_TOKEN")
GITHUB_REPOSITORY = os.getenv("GITHUB_REPOSITORY")

if not GEMINI_API_KEY or not GH_TOKEN or not GITHUB_REPOSITORY:
    print("Error: Missing required environment variables.")
    sys.exit(1)

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)

# Force Gemini to return strictly valid JSON
generation_config = {
    "response_mime_type": "application/json",
    "temperature": 0.2
}

model = genai.GenerativeModel(
    model_name='gemini-3.6-flash',
    generation_config=generation_config
)

def scan_file(file_path):
    print(f"Scanning {file_path}...")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            code_content = f.read()
    except Exception as e:
        print(f"Failed to read {file_path}: {e}")
        return None

    prompt = f"""
    You are an expert DevSecOps security reviewer.
    Analyze the following Python code for security vulnerabilities (e.g., SQL Injection, Hardcoded Secrets, XSS, Remote Code Execution).
    
    Code to audit:
    ```python
    {code_content}
    ```

    Respond strictly in JSON format with the following keys:
    - "vulnerable": boolean (true if severe vulnerabilities are found, false otherwise)
    - "vulnerability_details": string (Markdown description explaining the detected vulnerabilities and recommendations)
    - "fixed_code": string (The complete, corrected Python code without any markdown code fences like ```python)
    """

    try:
        response = model.generate_content(prompt)
        # Parse strict JSON output
        result = json.loads(response.text)
        return result
    except Exception as e:
        print(f"Warning: Error during AI analysis or JSON parsing: {e}")
        return None

def validate_ast(code_str):
    try:
        ast.parse(code_str)
        return True
    except SyntaxError as e:
        print(f"AST Validation Failed: {e}")
        return False

def main():
    target_file = "app.py"
    if not os.path.exists(target_file):
        print(f"Target file {target_file} not found.")
        sys.exit(0)

    audit_result = scan_file(target_file)

    if not audit_result or not audit_result.get("vulnerable"):
        print("Success: Code passed all enterprise security checks cleanly!")
        sys.exit(0)

    print("Security vulnerability detected by Gemini!")
    vulnerability_details = audit_result.get("vulnerability_details", "Vulnerability detected.")
    fixed_code = audit_result.get("fixed_code", "")

    # Clean up any accidental markdown blocks in fixed code
    if fixed_code.startswith("```python"):
        fixed_code = fixed_code.replace("```python", "").rstrip("```").strip()

    # Validate AST of the generated patch
    if not validate_ast(fixed_code):
        print("Error: AI-generated code patch failed AST syntax validation!")
        sys.exit(1)

    print("AST Validation successful. Proceeding to create Pull Request...")

    # GitHub API Integration
    g = Github(GH_TOKEN)
    repo = g.get_repo(GITHUB_REPOSITORY)

    branch_name = "ai-security-patch-pro"
    default_branch = repo.default_branch

    # Get reference of main branch
    main_ref = repo.get_git_ref(f"heads/{default_branch}")
    main_sha = main_ref.object.sha

    # Create new branch for patch if it doesn't exist
    try:
        repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=main_sha)
        print(f"Created branch: {branch_name}")
    except Exception:
        print(f"Branch {branch_name} already exists. Updating reference...")
        ref = repo.get_git_ref(f"heads/{branch_name}")
        ref.edit(sha=main_sha, force=True)

    # Commit patched code to the new branch
    contents = repo.get_contents(target_file, ref=branch_name)
    repo.update_file(
        path=target_file,
        message="🔒 DevSecOps Auto-Fix: Patch security vulnerabilities",
        content=fixed_code,
        sha=contents.sha,
        branch=branch_name
    )

    # Create Pull Request
    pr_body = f"## 🛡️ Automated DevSecOps AI Security Audit\n\n{vulnerability_details}\n\n---\n*Patched automatically using `gemini-3.6-flash` and validated via Python AST parser.*"
    
    # Check if PR already exists
    prs = repo.get_pulls(state='open', head=f"{repo.owner.login}:{branch_name}", base=default_branch)
    if prs.totalCount == 0:
        pr = repo.create_pull(
            title="🚨 DevSecOps Patch: Fix Identified Security Vulnerabilities",
            body=pr_body,
            head=branch_name,
            base=default_branch
        )
        print(f"Successfully created Pull Request: {pr.html_url}")
    else:
        print(f"Pull Request already exists: {prs[0].html_url}")

if __name__ == "__main__":
    main()
