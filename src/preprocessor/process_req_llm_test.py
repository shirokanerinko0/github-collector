#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""
测试 preprocess_requirements 功能测试脚本
"""

import sys
import os
import json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from src.utils.utils import save_data


from src.utils.utils import load_config
from src.preprocessor.data_preprocessor import DataPreprocessor

def main():
    """测试 preprocess_requirements 功能"""
    print("=" * 60)
    print("开始测试 preprocess_requirements 功能")
    print("=" * 60)
    
    # 加载配置
    CONFIG = load_config()
    use_llm_processing = CONFIG["requirement_processing"]["use_llm_processing"]
    print(f"\n配置: use_llm_processing = {use_llm_processing}")
    
    # 初始化预处理器
    preprocessor = DataPreprocessor()
    
    # 从文件读取测试需求数据
    test_data_file = f"data\\{CONFIG['repo']}\\requirements_raw.json"
    print(f"\n从文件读取测试数据: {test_data_file}")
    
    try:
        with open(test_data_file, 'r', encoding='utf-8') as f:
            test_requirements = json.load(f)
    except Exception as e:
        print(f"读取测试数据失败: {e}")
        return
    
    print(f"\n测试需求数量: {len(test_requirements)}")
    
    # 预处理需求
    print("\n开始预处理需求...")
    processed_requirements = preprocessor.preprocess_requirements(test_requirements)
    req_file_path = f"data\\{CONFIG['repo']}\\requirements_processed{'_llm' if use_llm_processing else ''}.json"
    save_data(processed_requirements, req_file_path)
    print(f"\n预处理完成，剩余需求数量: {len(processed_requirements)}")
    
    # 打印处理结果
    print("\n" + "=" * 60)
    print("预处理结果详情:")
    print("=" * 60)
    
    for i, req in enumerate(processed_requirements):
        print(f"\n需求 {i + 1}:")
        print(f"  req_id: {req.get('req_id')}")
        print(f"  title: {req.get('title')}")
        
        if use_llm_processing:
            print(f"  llm_category: {req.get('llm_category')}")
            print(f"  cleaned_summary: {req.get('cleaned_summary')}")
            print(f"  llm_reason: {req.get('llm_reason')}")
    
    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)

if __name__ == "__main__":
    main()
