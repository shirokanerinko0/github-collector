import os
import json
import torch
import sys
import numpy as np

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.utils.utils import load_config
from src.model.encoder_factory import EncoderFactory
config = load_config()
##排除的目录路径
exclude_dirs = config['exclude_dirs']

def process_analysis_files(directory):
    """
    处理指定目录下的所有_analysis.json文件，计算方法向量并保存
    """
    # 获取配置的模型名称
    encode_model_name = config.get("encode_model_name", "unixcoder")
    
    # 根据模型名称生成pt文件名
    pt_file_name = f"{encode_model_name}_code_vectors.pt"
    pt_file_path = os.path.join(os.path.dirname(directory), pt_file_name)
    
    # 如果存在.pt文件则直接加载，不重复计算
    if os.path.exists(pt_file_path):
        print(f"目录 {directory} 已存在代码向量 ({pt_file_name})，跳过处理")
        return
    
    # 创建编码器
    print(f"正在加载编码器: {encode_model_name}")
    encoder = EncoderFactory.create_encoder(encode_model_name)
    embedding_dim = encoder.get_embedding_dim()
    print(f"编码器加载完成，嵌入维度: {embedding_dim}")
    # 初始化数据结构
    data = {
        "embeddings": [],
        "file_paths": [],
        "method_names": [],
        "class_names": [],
        "original_code": [],
        "model_name": encode_model_name,
        "dimension": embedding_dim
    }
    
    print(f"正在处理目录: {directory}")
    print("=" * 60)
    
    # 遍历目录及其子目录
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('_analysis.json'):
                file_path = os.path.join(root, file)
                # 排除指定目录中的文件
                if any(exclude_dir in file_path for exclude_dir in exclude_dirs):
                    continue
                
                print(f"处理文件: {file_path}")
                
                try:
                    # 读取分析文件
                    with open(file_path, 'r', encoding='utf-8') as f:
                        analysis_data = json.load(f)
                    # 处理每个类
                    if analysis_data.get("classes"):
                        for cls in analysis_data["classes"]:
                            class_name = cls.get("name", "")
                            class_code = cls.get("original_code", "")

                            # 计算相对于origin_src的路径并转换为Java文件路径
                            src_dir = os.path.join('data', config['repo'], 'origin_src')
                            relative_path = os.path.relpath(file_path, src_dir).replace('_analysis.json', '.java')
                            
                            # 添加类信息到数据结构
                            if class_code:
                                # 计算类向量
                                class_embedding = encoder.encode([class_code])[0]
                                class_embedding = torch.tensor(class_embedding)
                                
                                # 添加到数据结构
                                data["embeddings"].append(class_embedding)
                                data["file_paths"].append(relative_path)
                                data["method_names"].append("")  # 类的method_names为空
                                data["class_names"].append(class_name)
                                data["original_code"].append(class_code)
                            
                            # 处理每个方法
                            for method in cls.get("methods", []):
                                method_name = method.get("name", "")
                                original_code = method.get("original_code", "")
                                
                                if original_code:
                                    # 计算方法向量
                                    embedding = encoder.encode([original_code])[0]
                                    embedding = torch.tensor(embedding)
                                    
                                    # 添加到数据结构
                                    data["embeddings"].append(embedding)
                                    data["file_paths"].append(relative_path)
                                    data["method_names"].append(method_name)
                                    data["class_names"].append(class_name)
                                    data["original_code"].append(original_code)
                    
                except Exception as e:
                    print(f"处理文件 {file_path} 时出错: {e}")
    
    # 转换为张量
    if data["embeddings"]:
        data["embeddings"] = torch.stack(data["embeddings"])
        print(f"\n共处理 {len(data['embeddings'])} 个类和方法")
        
        # 保存为pt文件，与directory同一级
        output_path = os.path.join(os.path.dirname(directory), pt_file_name)
        torch.save(data, output_path)
        print(f"向量文件保存到: {output_path}")
    else:
        print("未找到方法代码")
    
    print("=" * 60)
    print("处理完成！")

if __name__ == "__main__":
    # 测试目录
    test_directory = f"data\\{config['repo']}\\origin_src"
    
    if os.path.exists(test_directory):
        process_analysis_files(test_directory)
    else:
        print(f"目录 {test_directory} 不存在")
