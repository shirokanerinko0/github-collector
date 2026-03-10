#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from src.model.calculate_code_vectors import process_analysis_files
from src.JavaCodeAnalyzer.tree_sitter_java_analyzer import analyze_directory
from file_operations.download import download_repository_main
"""
主文件，整合各层功能模块
"""
import os
from src.utils.utils import load_config, save_data
from src.api.github_api import GitHubAPI
from src.extractor.data_extractor import DataExtractor
from src.preprocessor.data_preprocessor import DataPreprocessor
from src.trace_link.main import trace_links

# 全局配置变量
config = load_config()

def main():
    """
    主函数，整合各层功能模块
    """
    # 从配置文件加载配置
    config = load_config()
    if not config:
        print("无法加载配置文件，请检查config.json文件是否存在且格式正确")
        return
    
    # 从配置中获取信息
    access_token = config.get("token")
    repo_owner = config.get("owner")
    repo_name = config.get("repo")
    
    # 验证配置信息
    if not all([access_token, repo_owner, repo_name]):
        print("配置信息不完整，请检查config.json文件中的token、owner和repo字段")
        return
    
    print(f"从配置文件加载信息成功: {repo_owner}/{repo_name}")
    
    # 初始化各层实例
    # GitHubAPI会从配置文件中读取debug值
    github_api = GitHubAPI(access_token)
    # DataExtractor会从配置文件中读取limits值
    extractor = DataExtractor()
    preprocessor = DataPreprocessor()
    
    # 获取仓库对象
    repo = github_api.get_repo(repo_owner, repo_name)
    if not repo:
        print("无法获取仓库，请检查输入信息和访问令牌权限")
        return
    
    print(f"成功获取仓库: {repo.name}")
    
    # 数据保存目录
    data_dir = f"data/{repo_name}"
    
    # 1. 采集Issues数据
    print("\n开始采集Issues数据...")
    issues = github_api.get_issues(repo, state=config["issue_state"],labels=config["filter_labels"])
    issues_list = extractor.extract_issues(issues, github_api, repo)
    print(f"采集到 {len(issues_list)} 个Issues")
    
    # 预处理Issues数据
    processed_issues = preprocessor.preprocess_issues(issues_list)
    print(f"预处理完成 {len(processed_issues)} 个Issues")
    
    # 保存Issues数据
    save_data(issues_list, f"{data_dir}/issues_raw.json")
    save_data(processed_issues, f"{data_dir}/issues_processed.json")
    
    
    # 3. 采集Pull Requests数据
    print("\n开始采集Pull Requests数据...")
    prs = github_api.get_pull_requests(repo, state="closed")
    prs_list = extractor.extract_pull_requests(prs, github_api, repo)
    print(f"采集到 {len(prs_list)} 个Pull Requests")
    
    # 预处理Pull Requests数据
    processed_prs = preprocessor.preprocess_pull_requests(prs_list)
    print(f"预处理完成 {len(processed_prs)} 个Pull Requests")
    
    # 保存Pull Requests数据
    save_data(prs_list, f"{data_dir}/pull_requests_raw.json")
    save_data(processed_prs, f"{data_dir}/pull_requests_processed.json")
    
    # 4. 提取和处理需求数据
    print("\n开始提取和处理需求数据...")
    requirements = extractor.extract_requirements(issues_list, prs_list)
    print(f"提取到 {len(requirements)} 个需求")
    # 保存需求数据
    save_data(requirements, f"{data_dir}/requirements_raw.json")
    # 预处理需求数据
    processed_requirements = preprocessor.preprocess_requirements(requirements)
    print(f"预处理完成 {len(processed_requirements)} 个需求")
    
    # 保存需求数据
    use_llm = config["requirement_processing"]["use_llm_processing"]
    llm_suffix = "_llm" if use_llm else ""
    req_file_name = f"requirements_processed{llm_suffix}.json"
    req_file_path = f"{data_dir}/{req_file_name}"
    
    save_data(processed_requirements, req_file_path)
    
    print(f"需求数据已保存到: {req_file_path}")
    
    # 5. 采集文件数据
    download_repository_main()
    print("\n数据采集、预处理和保存完成")

    # 6. 分析代码，保存为_analysis.json
    analyze_code()


def analyze_code():
    """
    分析每个代码，保存为_analysis.json
    将所有方法、类代码编码成向量保存为.pt文件
    """
    analyze_directory(f"data/{config['repo']}/origin_src")
    print("\n代码解析完成")
    process_analysis_files(f"data/{config['repo']}/origin_src")
    print("\n代码向量计算、保存完成")

if __name__ == "__main__":
    main()
