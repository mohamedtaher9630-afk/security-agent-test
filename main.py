import os
import json
import re
from dotenv import load_dotenv
from github import Github
import google.generativeai as genai

load_dotenv()

GEMINI_KEY = os.getenv("GEMINI_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-3.6-flash')

SUPPORTED_EXTENSIONS = ('.py', '.js', '.ts', '.php', '.html', '.sql', '.java', '.go', '.rb', '.json', '.env.example')

def get_all_repo_files(repo, path=""):
    files_data = []
    contents = repo.get_contents(path)
    for content in contents:
        if content.type == "dir":
            files_data.extend(get_all_repo_files(repo, content.path))
        elif content.path.endswith(SUPPORTED_EXTENSIONS):
            try:
                decoded = content.decoded_content.decode("utf-8")
                files_data.append({"path": content.path, "content": decoded, "sha": content.sha})
            except Exception:
                pass
    return files_data

def create_multi_file_pr(repo_name: str, patched_files: list, summary_report: str):
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(repo_name)
    main_branch = repo.get_branch("main")
    
    branch_name = f"full-security-fix-{os.urandom(3).hex()}"
    repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=main_branch.commit.sha)
    
    for item in patched_files:
        file_path = item["path"]
        new_content = item["patched_code"]
        file_contents = repo.get_contents(file_path, ref=branch_name)
        
        repo.update_file(
            path=file_path,
            message=f"Fix vulnerabilities in {file_path}",
            content=new_content,
            sha=file_contents.sha,
            branch=branch_name
        )
    
    pr = repo.create_pull(
        title="🔒 Security Fix: Auto-patched by AI Agent",
        body=f"## 🤖 Automated DevSecOps Audit Report\n\n{summary_report}",
        head=branch_name,
        base="main"
    )
    return pr.html_url

def analyze_file(file_path: str, code: str):
    prompt = f"""
    You are an expert cybersecurity auditor. Analyze this code for ANY security vulnerabilities (SQLi, XSS, Hardcoded Secrets/Keys, RCE, CSRF, Insecure Deserialization, etc.).
    File: {file_path}
    Code:
    ```
    {code}
    ```
    
    If vulnerabilities exist, fix them completely while preserving original functionality.
    Respond strictly in valid JSON format:
    {{
      "vulnerable": true,
      "issues": ["Issue 1 description", "Issue 2 description"],
      "patched_code": "full corrected file content"
    }}
    """
    
    response = model.generate_content(
        prompt,
        generation_config={"response_mime_type": "application/json"}
    )
    
    try:
        return json.loads(response.text)
    except Exception:
        json_match = re.search(r"\{.*\}", response.text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))
        return {"vulnerable": False, "issues": [], "patched_code": code}

def run_full_security_pipeline(repo_name: str):
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(repo_name)
    
    print("🔍 [1/3] Fetching all project files from GitHub...")
    all_files = get_all_repo_files(repo)
    print(f"📦 Found {len(all_files)} code file(s) to scan.\n")
    
    patched_files = []
    report_details = []
    
    print("🤖 [2/3] Scanning repository for vulnerabilities...")
    for file_info in all_files:
        path = file_info["path"]
        print(f"  ➡️ Scanning: {path} ...")
        
        result = analyze_file(path, file_info["content"])
        
        if result.get("vulnerable") and result.get("patched_code"):
            print(f"     ⚠️ Found {len(result.get('issues', []))} issue(s) in {path}!")
            patched_files.append({
                "path": path,
                "patched_code": result["patched_code"]
            })
            issues_list = "\n".join([f"  - {iss}" for iss in result.get("issues", [])])
            report_details.append(f"### 📄 `{path}`\n**Issues Found:**\n{issues_list}\n")
        else:
            print(f"     ✅ {path} is clean.")
            
    if patched_files:
        print("\n🚀 [3/3] Creating unified Pull Request with all security fixes...")
        summary_report = "\n".join(report_details)
        pr_url = create_multi_file_pr(repo_name, patched_files, summary_report)
        print(f"\n✅ All vulnerabilities fixed! Unified PR created: {pr_url}")
    else:
        print("\n✅ Entire repository is secure. No vulnerabilities found in any file!")

if __name__ == "__main__":
    TARGET_REPO = os.getenv("GITHUB_REPOSITORY", "mohamedtaher9630-afk/security-agent-test")
    run_full_security_pipeline(TARGET_REPO)
