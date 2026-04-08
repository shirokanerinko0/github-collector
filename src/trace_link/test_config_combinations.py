#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试不同配置组合的脚本
测试 config.json 中 enrich_* 配置的不同组合
"""

import os
import json
import subprocess
import sys

# 项目根目录
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
CONFIG_FILE = os.path.join(PROJECT_ROOT, 'config.json')
MAIN_SCRIPT = os.path.join(PROJECT_ROOT, 'src', 'trace_link', 'main.py')

# 保存原始配置
def save_original_config():
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

# 恢复原始配置
def restore_original_config(original_config):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(original_config, f, indent=2, ensure_ascii=False)

# 修改配置
def update_config(enrich_method, enrich_context):
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    config['enrich_method_with_docstring'] = enrich_method
    config['enrich_method_with_class_context'] = enrich_context
    
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

# 运行测试
def run_test(enrich_method, enrich_context):
    print(f"\n" + "=" * 80)
    print(f"测试配置: enrich_method={enrich_method}, enrich_context={enrich_context}")
    print("=" * 80)
    
    # 更新配置
    update_config(enrich_method, enrich_context)
    
    # 运行 main.py（实时显示输出）
    print("\n开始运行 main.py...")
    result = subprocess.run(
        [sys.executable, MAIN_SCRIPT],
        cwd=PROJECT_ROOT,
        capture_output=False,  # 实时显示输出
        text=True,
        encoding='utf-8'
    )
    
    print(f"\n返回码: {result.returncode}")
    
    
    

# 主函数
def main():
    # 保存原始配置
    original_config = save_original_config()
    
    try:
        # 生成所有可能的配置组合（只测试两个配置）
        combinations = [
            (False, False),  # 无增强
            (False, True),   # 仅类上下文
            (True, False),   # 仅方法注释
            (True, True)     # 方法注释 + 类上下文
        ]
        
        
        # 运行所有组合
        for i, (enrich_method, enrich_context) in enumerate(combinations, 1):
            print(f"\n开始测试组合 {i}/{len(combinations)}")
            run_test(enrich_method, enrich_context)

            
           
        
        # 打印结果总结
        print("\n" + "=" * 80)
        print("测试结果总结")
        print("=" * 80)
        
    finally:
        # 恢复原始配置
        restore_original_config(original_config)
        print("\n已恢复原始配置")

if __name__ == "__main__":
    main()
