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


if __name__ == "__main__":
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
    save_data(issues_list, "issues_test.json")
    """

    result = check_requirement_code_relation(requirement, code)
    print("LLM Output:")
    print(result)
