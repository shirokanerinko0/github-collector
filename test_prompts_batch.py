#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量测试多个提示词的脚本
"""

import subprocess
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '')))
from src.utils.utils import load_config

# 要测试的提示词列表
prompts_to_test = ['prompt9_varH', 'prompt9_varI', 'prompt9_varJ', 'prompt9_varK']

# 加载配置
config = load_config()

def update_config(prompt_name):
    """更新配置文件中的提示词"""
    config_path = 'config.json'
    with open(config_path, 'r', encoding='utf-8') as f:
        config_data = json.load(f)
    
    config_data['requirement_processing']['prompt_name'] = prompt_name
    
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*60}")
    print(f"测试提示词: {prompt_name}")
    print(f"{'='*60}")

def run_command(cmd, description):
    """运行命令并打印结果"""
    print(f"\n>>> {description}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"错误: {result.stderr}")
    return result.returncode == 0

def extract_statistics():
    """从结果文件中提取统计信息"""
    result_file = 'data/guava/trace_link_jina_code_top5.json'
    if not os.path.exists(result_file):
        return None
    
    with open(result_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    stats = data.get('statistics', {})
    return {
        'total_requirements': stats.get('total_requirements', 0),
        'requirements_with_change_files': stats.get('requirements_with_change_files', 0),
        'requirements_with_at_least_one_hit': stats.get('requirements_with_at_least_one_hit', 0),
        'total_change_files': stats.get('total_change_files', 0),
        'total_hit_files': stats.get('total_hit_files', 0),
        'top_k': stats.get('top_k', 5),
        'overall_recall': stats.get('overall_recall', 0.0)
    }

def update_prompt_statistics(prompt_name, statistics):
    """更新提示词文件中的统计信息"""
    prompt_file = f'src/LLMapi/prompt/process_req/{prompt_name}.json'
    if not os.path.exists(prompt_file):
        print(f"提示词文件不存在: {prompt_file}")
        return
    
    with open(prompt_file, 'r', encoding='utf-8') as f:
        prompt_data = json.load(f)
    
    prompt_data['statistics'] = statistics
    
    with open(prompt_file, 'w', encoding='utf-8') as f:
        json.dump(prompt_data, f, indent=2, ensure_ascii=False)
    
    print(f"已更新 {prompt_name} 的统计信息")

def main():
    """主函数"""
    print("开始批量测试提示词...")
    
    results = []
    
    for prompt_name in prompts_to_test:
        # 更新配置
        update_config(prompt_name)
        
        # 运行预处理
        if not run_command(
            'D:\\conda_envs\\thesis_nlp\\python.exe src/preprocessor/process_req_llm_test.py',
            f"预处理需求 ({prompt_name})"
        ):
            print(f"预处理失败，跳过 {prompt_name}")
            continue
        
        # 运行追溯链接
        if not run_command(
            'D:\\conda_envs\\thesis_nlp\\python.exe src/trace_link/main.py',
            f"生成追溯链接 ({prompt_name})"
        ):
            print(f"追溯链接失败，跳过 {prompt_name}")
            continue
        
        # 提取统计信息
        stats = extract_statistics()
        if stats:
            print(f"\n结果: 召回率 = {stats['overall_recall']:.4f}, 命中文件数 = {stats['total_hit_files']}")
            
            # 更新提示词文件
            update_prompt_statistics(prompt_name, stats)
            
            results.append({
                'prompt_name': prompt_name,
                'recall': stats['overall_recall'],
                'hit_files': stats['total_hit_files']
            })
    
    # 打印汇总
    print(f"\n{'='*60}")
    print("测试结果汇总:")
    print(f"{'='*60}")
    for r in results:
        print(f"{r['prompt_name']}: 召回率 = {r['recall']:.4f}, 命中文件数 = {r['hit_files']}")

if __name__ == '__main__':
    main()
