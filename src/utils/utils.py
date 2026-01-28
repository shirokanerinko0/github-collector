#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
工具文件，包含配置文件加载和数据保存等功能
"""

import json
import os


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
        import traceback
        traceback.print_exc()
        return None


def save_data(data, file_path):
    """
    保存数据到指定文件
    :param data: 要保存的数据
    :param file_path: 文件路径
    """
    try:
        # 处理路径，确保使用正确的路径分隔符
        file_path = os.path.normpath(file_path)
        
        # 确保目录存在
        dir_path = os.path.dirname(file_path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)
        
        # 保存数据
        with open(file_path, 'w', encoding='utf-8') as f:
            # 自定义序列化函数，处理复杂类型
            def default_serializer(obj):
                if hasattr(obj, '__dict__'):
                    return obj.__dict__
                elif isinstance(obj, (bytes, bytearray)):
                    return obj.decode('utf-8', errors='replace')
                else:
                    return str(obj)
            
            json.dump(data, f, ensure_ascii=False, indent=2, default=default_serializer)
        print(f"数据保存成功: {file_path}")
    except Exception as e:
        print(f"保存数据失败: {str(e)}")
        import traceback
        traceback.print_exc()
