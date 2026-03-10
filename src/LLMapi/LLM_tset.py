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


def process_requirement_text(title, body):
    """
    处理原始Issue文本，去噪提取和需求分类
    
    Args:
        title: Issue标题
        body: Issue内容
        
    Returns:
        JSON格式的处理结果
    """
    prompt = f'''You are a senior software engineering requirements analyst. Your task is to read the raw Issue text scraped from GitHub/Jira and complete the following two tasks:

1. [Denoising and Extraction]: Filter out irrelevant noise such as error stacks (Stacktrace), code snippets, environment configurations, acknowledgments, etc., and summarize the core诉求 of this text in clear natural language.

2. [Requirement Classification]: Determine which software engineering requirement type this Issue belongs to.

You can only choose one of the following four types:
- "BUG": Defect report (system error, behavior does not meet expectations).
- "FR": Functional requirement (Feature Request, requires adding new features or extending logic).
- "NFR": Non-functional requirement (such as performance optimization, code refactoring, security enhancement, dependency upgrade).
- "INVALID": Invalid requirement (such as pure user questions, modifying Markdown documents, meaningless nonsense).

[Strict Requirements]: You must only output valid JSON format, do not include any additional explanations or Markdown code block markers (such as ```json).
JSON must include the following three fields:
{{
"category": "BUG | FR | NFR | INVALID",
"cleaned_summary": "The clean requirement summary you extracted and rewritten (can be in English or Chinese, keep the original meaning)",
"reason": "Briefly explain why it is classified into this category"
}}
All in English.

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
    print("测试2: process_requirement_text - BUG类型")
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
    result2 = process_requirement_text(bug_title, bug_body)
    print("LLM Output:")
    print(result2)
    
    print("\n" + "=" * 60)
    print("测试3: process_requirement_text - FR类型")
    print("=" * 60)
    fr_title = "Feature Request: Add dark mode support"
    fr_body = """
It would be great to have a dark mode option for the application.
Many users prefer dark themes for better readability at night.
Thanks!
"""
    result3 = process_requirement_text(fr_title, fr_body)
    print("LLM Output:")
    print(result3)
    
    print("\n" + "=" * 60)
    print("测试4: process_requirement_text - NFR类型")
    print("=" * 60)
    nfr_title = "Performance: Optimize database queries"
    nfr_body = """
The current database queries are taking too long to execute.
We need to optimize the queries and add proper indexing to improve performance.
Also, consider upgrading to the latest version of MySQL.
"""
    result4 = process_requirement_text(nfr_title, nfr_body)
    print("LLM Output:")
    print(result4)
    
    print("\n" + "=" * 60)
    print("测试5: process_requirement_text - INVALID类型")
    print("=" * 60)
    invalid_title = "How to use this library?"
    invalid_body = """
I'm new to this library. Can someone please explain how to use it?
Thanks in advance!
"""
    result5 = process_requirement_text(invalid_title, invalid_body)
    print("LLM Output:")
    print(result5)
