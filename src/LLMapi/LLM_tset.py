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
            max_tokens=2048,
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
    prompt =f'''
## Task
Process GitHub issue for code traceability (vector similarity search).

## Classification
BUG | FR | NFR | DOCS | CHORE | QUESTION | INVALID
- BUG: Crashes, errors, unexpected behavior
- FR: New features, new methods, new APIs
- NFR: Performance, thread-safety, security, refactoring

## Critical Rules (Vector Retrieval)
1. **KEEP ALL Technical Entities**:
   - Class names: ImmutableSet, Maps, Throwables
   - Method names: builderWithLoadFactor, fromProperties, propagateIf
   - Package names: com.google.common.collect
   - Parameters: float, int, customLoadFactor
   - Exceptions: NullPointerException, ConcurrentModificationException
   - Values: 0.7, 0.35, HashSet, load factor

2. **DO NOT Over-Abstract**:
   - WRONG: "Add theme switching support"
   - RIGHT: "Add dark theme option - ImmutableSet.builderWithLoadFactor(0.2f)"
   
3. **Format** (code-comment style):
   "[Verb] [ClassName].[methodName] - [Preserve original API names and parameters]"

## Output (JSON only)
{{
"reason": "Brief analysis.",
"category": "BUG|FR|NFR|DOCS|CHORE|QUESTION|INVALID",
"cleaned_summary": "Keep all technical entities, use code-comment style."
}}

Issue Title: """{title}"""
Issue Body: """{body}"""
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
            max_tokens=2048,
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
    print("测试2: process_requirement_text_llm")
    print("=" * 60)
    title2 = "Add generics with Maps. fromProperties()."
    body2 = "Add generics with Maps. fromProperties().\r\n\r\nIt can use like this:\r\n```java\r\nMap<Integer, Integer> maps = fromProperties(prop, (k)->Integer.valueOf(k), (v)->Integer.valueOf(v));\r\n```\r\nIt's very useful when we use it to convert properties to a generics map.\r\n\r\nAnd in other way, we can implement with BiFunction<T, U, R> to expand this method."
    result2 = process_requirement_text_llm(title2, body2)
    print("LLM Output:")
    print(result2)
    
    print("\n" + "=" * 60)
    print("测试3: process_requirement_text_llm")
    print("=" * 60)
    title3 = "Add Throwables.propagateIf"
    body3 = "In a normal application is common to throw an exception after eval an expression like\r\n\r\n```\r\nif (balance < amount) {\r\n   throw new InsufficientFundsException();\r\n}\r\n```\r\n\r\n```\r\nif (!optional.isPresent()) {\r\n  throw new NotFoundException();\r\n}\r\n```\r\n\r\nThis PR aims to get rid of those boilerplate code with propagateIf\r\n\r\n```\r\nThrowables.propagateIf(balance < amount, () -> new InsufficientFundsException());\r\nThrowables.propagateIf(!optional.isPresent(), () -> new NotFoundException());\r\n```\r\n\r\n"
    result3 = process_requirement_text_llm(title3, body3)
    print("LLM Output:")
    print(result3)
    
    print("\n" + "=" * 60)
    print("测试4: process_requirement_text_llm")
    print("=" * 60)
    title4 = "Making the BloomFilter thread-safe & lock-free"
    body4 = "Previously, the BloomFilter wasn't thread-safe and required external locking to ensure safety. Now, it's thread-safe and lock-free through the use of atomics and compare-and-swap.\r\n\r\nThis PR introduces **no** API changes beyond an extra `@ThreadSafe` annotation on the BloomFilter class. It should also be entirely backwards (and forwards) compatible with the serialization format because that too isn't being changed. \r\n\r\nPlease extend extra scrutiny to the `LockFreeBitArray.putAll()` method because it's not present in our internal fork of the BloomFilter class and has thus not gone through our integ tests or has seen prod (I wrote it for this PR).\r\n\r\nFixes #2748."
    result4 = process_requirement_text_llm(title4, body4)
    print("LLM Output:")
    print(result4)
