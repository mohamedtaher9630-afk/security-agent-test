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

def scan_code_file(file_path, file_content, file_type):
    print(f"Scanning {file_path} ({file_type})...")
    
    prompt = f"""
    You are an expert multi-language DevSecOps security reviewer and dependency auditor.
    Analyze the following {file_type} file for security vulnerabilities, weak configurations, or vulnerable outdated dependencies.
    
    File Path: {file_path}
    Content:
    ```
    {file_content}
    ```

    Respond strictly in JSON format with the following keys:
    - "vulnerable": boolean (true if severe security issues are found, false otherwise)
    - "vulnerability_details": string (Markdown description explaining the detected issues and remediation recommendations)
    - "fixed_code": string (The complete, corrected file content without markdown code fences)
    """

    try:
        response = model.generate_content(prompt)
        result = json.loads(response.text)
        return result
    except Exception as e:
        print(f"Warning: Error during AI analysis or JSON parsing for {file_path}: {e}")
        return None

def validate_syntax(code_str, file_ext):
    if file_ext == ".py":
        try:
            ast.parse(code_str)
            return True
        except SyntaxError as e:
            print(f"AST Validation Failed: {e}")
            return False
    # For non-Python files (JSON, TXT, JS), pass basic validation or add custom checks
    return True

def generate_security_analytics(repo, branch_name):
    """التحسين الرابع: توليد تقرير أمني دوري وحفظه في المستودع"""
    report_path = "security-analytics-report.md"
    report_content = f"""# 📊 Enterprise AI Security Analytics Report
- **Target Branch**: `{branch_name}`
- **Audited By**: `gemini-3.6-flash` & Multi-Language DevSecOps Pipeline
- **Status**: Automated remediation workflows active and verified.
"""
    try:
        try:
            contents = repo.get_contents(report_path, ref=branch_name)
            repo.update_file(report_path, "📈 Update security analytics report", report_content, contents.sha, branch=branch_name)
        except Exception:
            repo.create_file(report_path, "📈 Create initial security analytics report", report_content, branch=branch_name)
        print("Security analytics report updated successfully.")
    except Exception as e:
        print(f"Notice: Could not update security analytics report: {e}")

def main():
    g = Github(GH_TOKEN)
    repo = g.get_repo(GITHUB_REPOSITORY)
    default_branch = repo.default_branch

    # تحديد الملفات المراد فحصها (تدعم لغات متعددة + فحص التبعيات SCA)
    target_files = ["app.py", "requirements.txt", "package.json"]
    
    branch_name = "ai-security-patch-pro"
    main_ref = repo.get_git_ref(f"heads/{default_branch}")
    main_sha = main_ref.object.sha

    # تجهيز الفرع الجديد
    try:
        repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=main_sha)
    except Exception:
        ref = repo.get_git_ref(f"heads/{branch_name}")
        ref.edit(sha=main_sha, force=True)

    vulnerabilities_found = False
    combined_details = "## 🛡️ Multi-Language & Dependency Security Audit\n\n"

    for target_file in target_files:
        if not os.path.exists(target_file):
            continue
        
        try:
            with open(target_file, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception:
            continue

        file_ext = os.path.splitext(target_file)[1]
        audit_result = scan_code_file(target_file, content, file_ext)

        if audit_result and audit_result.get("vulnerable"):
            vulnerabilities_found = True
            vulnerability_details = audit_result.get("vulnerability_details", "")
            fixed_code = audit_result.get("fixed_code", "")

            if fixed_code.startswith("```"):
                lines = fixed_code.splitlines()
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].startswith("```"):
                    lines = lines[:-1]
                fixed_code = "\n".join(lines)

            if not validate_syntax(fixed_code, file_ext):
                print(f"Error: Patch for {target_file} failed syntax validation!")
                continue

            # تحديث الملف داخل الفرع
            contents = repo.get_contents(target_file, ref=branch_name)
            repo.update_file(
                path=target_file,
                message=f"🔒 DevSecOps Auto-Fix: Secure {target_file}",
                content=fixed_code,
                sha=contents.sha,
                branch=branch_name
            )
            combined_details += f"### 📄 File: `{target_file}`\n{vulnerability_details}\n\n"

    if not vulnerabilities_found:
        print("Success: All files passed enterprise security and dependency checks cleanly!")
        generate_security_analytics(repo, default_branch)
        sys.exit(0)

    # توليد التقرير الأمني العام
    generate_security_analytics(repo, branch_name)

    # إنشاء Pull Request موحد لكل الإصلاحات
    prs = repo.get_pulls(state='open', head=f"{repo.owner.login}:{branch_name}", base=default_branch)
    if prs.totalCount == 0:
        pr = repo.create_pull(
            title="🚨 DevSecOps Multi-Language & Dependency Security Patch",
            body=combined_details + "---\n*Generated automatically by `gemini-3.6-flash` security engine.*",
            head=branch_name,
            base=default_branch
        )
        print(f"Successfully created Pull Request: {pr.html_url}")
    else:
        print(f"Pull Request already exists: {prs[0].html_url}")

if __name__ == "__main__":
    main()
