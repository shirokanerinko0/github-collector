#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试脚本，用于测试GitHubCollector的各项功能
"""

from github_collector import GitHubCollector
import json

# 从配置文件加载配置
def load_config(config_file="config.json"):
    """
    从配置文件加载配置信息
    :param config_file: 配置文件路径
    :return: 配置字典
    """
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except Exception as e:
        print(f"加载配置文件失败: {str(e)}")
        return None

# 加载配置
config = load_config()
if not config:
    print("无法加载配置文件，请检查config.json文件是否存在且格式正确")
    exit(1)

# 从配置中获取信息
access_token = config.get("token")
repo_owner = config.get("owner")
repo_name = config.get("repo")

# 验证配置信息
if not all([access_token, repo_owner, repo_name]):
    print("配置信息不完整，请检查config.json文件中的token、owner和repo字段")
    exit(1)

print(f"从配置文件加载测试信息成功: {repo_owner}/{repo_name}")

def test_collector():
    """
    测试GitHubCollector的各项功能
    """
    print("开始测试GitHubCollector...")
    
    # 初始化GitHubCollector实例
    collector = GitHubCollector(access_token)
    print("✓ 初始化GitHubCollector成功")
    
    # 测试获取仓库
    repo = collector.get_repo(repo_owner, repo_name)
    if repo:
        print(f"✓ 获取仓库成功: {repo.name}")
    else:
        print("✗ 获取仓库失败")
        return
    
    # 测试获取Issues（限制数量以加快测试速度）
    print("\n测试获取Issues...")
    issues = collector.get_issues(repo, state="open")
    if issues:
        print(f"✓ 获取Issues成功，共 {len(issues)} 个")
        print(f"  示例Issue: #{issues[0]['number']} - {issues[0]['title']}")
    else:
        print("✗ 获取Issues失败")
    
    # 测试预处理Issues
    if issues:
        processed_issues = collector.preprocess_issues(issues)
        print(f"✓ 预处理Issues成功，共 {len(processed_issues)} 个")
        print(f"  预处理后示例Issue标题: {processed_issues[0]['title']}")
    
    # 测试获取Commits（限制数量以加快测试速度）
    print("\n测试获取Commits...")
    commits = collector.get_commits(repo)
    if commits:
        print(f"✓ 获取Commits成功，共 {len(commits)} 个")
        print(f"  示例Commit: {commits[0]['sha'][:7]} - {commits[0]['message'][:50]}...")
    else:
        print("✗ 获取Commits失败")
    
    # 测试预处理Commits
    if commits:
        processed_commits = collector.preprocess_commits(commits)
        print(f"✓ 预处理Commits成功，共 {len(processed_commits)} 个")
        print(f"  预处理后示例Commit消息: {processed_commits[0]['message'][:50]}...")
    
    # 测试获取Pull Requests（限制数量以加快测试速度）
    print("\n测试获取Pull Requests...")
    prs = collector.get_pull_requests(repo, state="open")
    if prs:
        print(f"✓ 获取Pull Requests成功，共 {len(prs)} 个")
        print(f"  示例PR: #{prs[0]['number']} - {prs[0]['title']}")
    else:
        print("✗ 获取Pull Requests失败")
    
    # 测试预处理Pull Requests
    if prs:
        processed_prs = collector.preprocess_pull_requests(prs)
        print(f"✓ 预处理Pull Requests成功，共 {len(processed_prs)} 个")
        print(f"  预处理后示例PR标题: {processed_prs[0]['title']}")
    
    # 测试获取文件（限制深度以加快测试速度）
    print("\n测试获取文件...")
    files = collector.get_files(repo, path=".github")  # 选择一个较小的目录
    if files:
        print(f"✓ 获取文件成功，共 {len(files)} 个")
        print(f"  示例文件: {files[0]['path']}")
    else:
        print("✗ 获取文件失败")
    
    # 测试过滤源代码文件
    if files:
        source_files = collector.filter_source_files(files)
        print(f"✓ 过滤源代码文件成功，共 {len(source_files)} 个")
        if source_files:
            print(f"  示例源代码文件: {source_files[0]['path']}")
    
    # 测试检查文件类型
    print("\n测试检查文件类型...")
    test_files = ["README.md", "main.py", "package.json", "image.jpg"]
    for file_path in test_files:
        is_source = collector.is_source_file(file_path)
        status = "✓" if is_source else "✗"
        print(f"  {status} {file_path}: {'源代码文件' if is_source else '非源代码文件'}")
    
    print("\n测试完成！")

if __name__ == "__main__":
    test_collector()
