import json
from openai import OpenAI
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.utils.utils import load_config


CONFIG = load_config()

# 从配置文件获取API密钥和基础URL
API_KEY = CONFIG["SiliconFlow"]["API_Key"]
BASE_URL = CONFIG["SiliconFlow"]["Base_URL"]  # 使用siliconflow的API地址
MAX_BODY_LEN = 4000

# 创建OpenAI客户端
client = OpenAI(
    api_key=API_KEY,
    base_url=BASE_URL
)

def check_requirement_code_relation(requirement_text, code_snippet):
    prompt = f'''
You are a software analyst.

Task:
Determine whether the following requirement and code snippet are semantically related.

Requirement:
"""{requirement_text}"""

Code Snippet:
"""{code_snippet}"""

Output in JSON format:
{{
  "related": true/false,
  "reason": "...(chinese)",
  "confidence": 0.0-1.0
}}
'''

    try:
        # 使用OpenAI客户端调用API
        response = client.chat.completions.create(
            model=CONFIG["SiliconFlow"]["model"],  # 使用V2.5模型
            messages=[
                {"role": "system", "content": "You are a precise and concise software analysis assistant."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},  # 指定返回JSON格式
            temperature=0.2,
            max_tokens=1024,
        )

        # 获取模型返回的内容
        answer_text = response.choices[0].message.content
        return answer_text
    except Exception as e:
        print(f"API调用失败: {e}")
        return f"{{\"related\": false, \"reason\": \"API调用失败\", \"confidence\": 0.0}}"


def process_requirement_text_llm(title, body):
    body = body[:MAX_BODY_LEN]
    """
    处理原始Issue文本，去噪提取和需求分类
    
    Args:
        title: Issue标题
        body: Issue内容
        
    Returns:
        JSON格式的处理结果
    """
    prompt =f'''You are a senior software engineering requirements analyst. Your task is to read the raw Issue text scraped from GitHub and complete the following tasks:

1. [Denoising and Extraction]: Filter out irrelevant noise (stacktraces, config files, greetings) and extract the core intent of the author.
2. [Requirement Classification]: Determine which software engineering requirement type this Issue belongs to.

### Category Definitions (Strictly choose ONE from the 7 options):
- "BUG": Code Defect. The production code is broken, throws unexpected errors, or logic fails to meet existing design/specifications.
- "FR": Functional Requirement (Feature / Enhancement). Requesting new business logic, new APIs, new features, or modifying existing features to support new use cases.
- "NFR": Non-Functional Requirement. Modifying production code to improve system attributes (e.g., performance optimization, memory leak fixing, security enhancement, code refactoring).
- "DOCS": Documentation. Issues related strictly to creating, updating, fixing typos, or translating READMEs, JavaDocs, tutorials, or official websites. No production code changes.
- "CHORE": Repository Maintenance. Internal engineering tasks that do not affect the end-user product (e.g., CI/CD pipeline updates, GitHub Actions, dependency version bumps, build scripts, linting configurations).
- "QUESTION": User Support. The user is asking for help, reporting confusion, asking "how-to", or inquiring about roadmaps/release dates. The intent is seeking an answer or guidance, not proposing a codebase change.
- "INVALID": Pure noise. Spam, completely empty descriptions, meaningless test strings (e.g., "test", "123"), or completely out-of-scope/unrelated content.

Summarize the following GitHub issue into a concise requirement.

Rules:
- Use a direct requirement statement.
- Do NOT mention the user, issue, request, or discussion.
- Do NOT start with phrases like:
    "The user requests"
    "This issue requests"
    "The author wants"
- Describe only the feature or capability to be added or changed.
- Maximum 25 words.

Bad summaries:
- The user requests adding support for X.
- The issue asks for adding feature Y.

Good summaries:
- Add support for X.
- Implement feature Y.
- Enable X functionality.

### Few-Shot Examples for Clarification:
Example 1:
User: "how to get Set<String> in a collection mapping in xml?"
Analysis: The user is asking for guidance on how to write code using existing features. They are not asking the developers to modify the framework's source code.
Category: QUESTION

Example 2:
User: "when will mybatis add r2dbc feature?"
Analysis: The user is inquiring about the roadmap/release date of a specific feature. This is a question about project management and future plans, not an actionable feature request proposal.
Category: QUESTION

Example 3:
User: "Update GitHub Actions to use Node 20"
Analysis: The user is requesting an update to the CI/CD pipeline. This is an internal repository maintenance task that does not change the core product logic.
Category: CHORE

Example 4:
User: "Typo in the caching documentation page"
Analysis: The user is pointing out a spelling mistake in the official documentation. No production code changes are required.
Category: DOCS

### Output Format (JSON Only):
You must output valid JSON without any markdown wrappers (like ```json). 
CRITICAL: You MUST generate the JSON keys in the EXACT order below (analyze first, classify last). All text must be in English.

{{
"cleaned_summary": "Summarize the core requirement clearly in English. Keep the original meaning but remove noise.",
"reason": "Step 1: What is the user's core intent? Step 2: Does this require developers to change the production code, documentation, or CI/CD? Step 3: Is it just a pure question or meaningless noise? Explain briefly.",
"category": "BUG | FR | NFR | DOCS | CHORE | QUESTION | INVALID"
}}

Issue Title:
"""{title}"""

Issue Body:
"""{body}"""
'''

    try:
        # 使用OpenAI客户端调用API
        response = client.chat.completions.create(
            model=CONFIG["SiliconFlow"]["model"],
            messages=[
                {"role": "system", "content": "You are a precise and concise software requirements analysis assistant."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
            max_tokens=1024,
        )

        # 获取模型返回的内容
        answer_text = response.choices[0].message.content
        return answer_text
    except Exception as e:
        print(f"API调用失败: {e}")
        return f"{{\"category\": \"INVALID\", \"cleaned_summary\": \"\", \"reason\": \"API调用失败\"}}"


if __name__ == "__main__":
    print("=" * 60)
    print("测试1: check_requirement_code_relation")
    print("=" * 60)
    requirement = "The system should return a 500 error if the request body exceeds the maximum size limit."
    code = """
    for issue in issues:
        if count >= max_issues:
            break
        if "pull_request" in issue.raw_data:
            print(f"跳过PR: {issue.html_url}")
            continue
        issues_list.append(issue.raw_data)
        count += 1
        print(f"已处理 {count} 个issue")
    """

    result1 = check_requirement_code_relation(requirement, code)
    print("LLM Output:")
    print(result1)
    
    print("\n" + "=" * 60)
    print("测试2: process_requirement_text_llm - BUG类型")
    print("=" * 60)
    bug_title = "Bug: Login fails with valid credentials"
    bug_body = """
When trying to login with correct username and password, the system returns an error message.
Stack trace:
java.lang.NullPointerException
    at com.example.UserService.login(UserService.java:42)
    at com.example.LoginController.post(LoginController.java:28)
    
Environment:
- Java 11
- Spring Boot 2.5.0
"""
    result2 = process_requirement_text_llm(bug_title, bug_body)
    print("LLM Output:")
    print(result2)
    
    print("\n" + "=" * 60)
    print("测试3: process_requirement_text_llm - FR类型")
    print("=" * 60)
    fr_title = "Feature Request: Add dark mode support"
    fr_body = """
It would be great to have a dark mode option for the application.
Many users prefer dark themes for better readability at night.
Thanks!
"""
    result3 = process_requirement_text_llm(fr_title, fr_body)
    print("LLM Output:")
    print(result3)
    
    print("\n" + "=" * 60)
    print("测试4: process_requirement_text_llm - NFR类型")
    print("=" * 60)
    nfr_title = "Performance: Optimize database queries"
    nfr_body = """
The current database queries are taking too long to execute.
We need to optimize the queries and add proper indexing to improve performance.
Also, consider upgrading to the latest version of MySQL.
"""
    result4 = process_requirement_text_llm(nfr_title, nfr_body)
    print("LLM Output:")
    print(result4)
    
    print("\n" + "=" * 60)
    print("测试5: process_requirement_text_llm - INVALID类型")
    print("=" * 60)
    invalid_title = "How to use this library?"
    invalid_body = """
I'm new to this library. Can someone please explain how to use it?
Thanks in advance!
"""
    result5 = process_requirement_text_llm(invalid_title, invalid_body)
    print("LLM Output:")
    print(result5)
