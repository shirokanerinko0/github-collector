import os
import json
import torch
import sys
import numpy as np
from tqdm import tqdm
# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.utils.utils import load_config
from src.model.encoder_factory import EncoderFactory
config = load_config()
##排除的目录路径
exclude_dirs = config['exclude_dirs']
DEBUG = True

def get_pt_file_name():
    encode_model_name = config.get("encode_model_name", "unixcoder")
    analyze_by_method = config.get("analyze_by_method", False)
    analyze_full_code = config.get("analyze_full_code", False)
    pt_file_name = f"{encode_model_name}_code_vectors{'_full' if analyze_full_code else ''}{'_method' if analyze_by_method else ''}.pt"
    return pt_file_name

def process_analysis_files(directory):
    """
    处理指定目录下的所有_analysis.json文件，计算方法向量并保存
    """
    # 获取配置
    encode_model_name = config.get("encode_model_name", "unixcoder")
    analyze_by_method = config.get("analyze_by_method", False)
    analyze_full_code = config.get("analyze_full_code", False)
    batch_size = config.get("batch_size", 32) # 建议在config中添加batch_size，默认32或64
    
    pt_file_name = get_pt_file_name()
    pt_file_path = os.path.join(os.path.dirname(directory), pt_file_name)
    
    if os.path.exists(pt_file_path):
        print(f"目录 {directory} 已存在代码向量 ({pt_file_name})，跳过处理")
        return
    
    print(f"正在加载编码器: {encode_model_name}")
    encoder = EncoderFactory.create_encoder(encode_model_name)
    embedding_dim = encoder.get_embedding_dim()
    print(f"编码器加载完成，向量维度: {embedding_dim}")
    
    # 将不变的路径计算移出循环
    src_dir = os.path.join('data', config.get('repo', ''), 'origin_src')
    
    print(f"正在读取与解析目录: {directory}")
    print("=" * 60)
    
    exclude_count = 0
    
    # 临时列表，用于收集所有待编码的数据
    texts_to_encode =[]
    file_paths = []
    method_names = []
    class_names =[]
    original_codes =[]

    # 第一阶段：极速遍历与解析文件（不涉及深度学习计算）
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('_analysis.json'):
                file_path = os.path.join(root, file)
                
                # 排除指定目录
                if any(exclude_dir in file_path for exclude_dir in exclude_dirs):
                    exclude_count += 1
                    continue
                
                relative_path = os.path.relpath(file_path, src_dir).replace('_analysis.json', '.java')
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        analysis_data = json.load(f)
                    source_code = analysis_data.get("source_code", "")    
                    if analyze_full_code:
                        texts_to_encode.append(source_code)
                        file_paths.append(relative_path)
                        method_names.append("")  # 类的method_names为空
                        class_names.append("")  # 类的class_names为空
                        original_codes.append(source_code)
                        
                    if not analysis_data.get("classes"):
                        continue
                        
                    for cls in analysis_data["classes"]:
                        class_name = cls.get("name", "")
                        class_code = cls.get("original_code", "")

                        if class_code:
                            texts_to_encode.append(class_code)
                            file_paths.append(relative_path)
                            method_names.append("")  # 类的method_names为空
                            class_names.append(class_name)
                            original_codes.append(class_code)
                        
                        if analyze_by_method:
                            for method in cls.get("methods",[]):
                                method_name = method.get("name", "")
                                method_code = method.get("original_code", "")
                                
                                if method_code:
                                    texts_to_encode.append(method_code)
                                    file_paths.append(relative_path)
                                    method_names.append(method_name)
                                    class_names.append(class_name)
                                    original_codes.append(method_code)
                                    
                except Exception as e:
                    print(f"解析文件 {file_path} 时出错: {e}")

    # 第二阶段：批量计算向量 (Batch Encoding)
    total_samples = len(texts_to_encode)
    if total_samples == 0:
        print("未找到有效的方法或类代码。")
        return

    print(f"\n共解析到 {total_samples} 个代码片段，过滤了 {exclude_count} 个文件。")
    print(f"开始批量提取向量 (Batch Size: {batch_size})...")
    
    all_embeddings =[]
    
    # 使用 tqdm 分批次进行编码，防止 OOM (显存/内存溢出)
    for i in tqdm(range(0, total_samples, batch_size), desc="编码进度"):
        batch_texts = texts_to_encode[i: i + batch_size]
        
        # 将一个批次的文本传给 encoder (模型内部会并行处理)
        # 注意: 你的 encoder.encode 必须支持传入列表并返回批量向量
        batch_emb = encoder.encode(batch_texts) 
        
        # 转为 tensor
        if not isinstance(batch_emb, torch.Tensor):
            batch_emb = torch.tensor(batch_emb)
            
        all_embeddings.append(batch_emb.cpu())
        torch.cuda.empty_cache()
    # 将所有的批次拼接起来
    final_embeddings = torch.cat(all_embeddings, dim=0)
    
    # 构建最终的数据结构
    data = {
        "embeddings": final_embeddings,
        "file_paths": file_paths,
        "method_names": method_names,
        "class_names": class_names,
        "original_code": original_codes,
        "model_name": encode_model_name,
        "dimension": embedding_dim
    }
    
    # 保存结果
    output_path = os.path.join(os.path.dirname(directory), pt_file_name)
    torch.save(data, output_path)
    
    print("=" * 60)
    print(f"处理完成！向量文件成功保存到: {output_path}")

if __name__ == "__main__":
    # 测试目录
    test_directory = f"data\\{config['repo']}\\origin_src"
    
    if os.path.exists(test_directory):
        process_analysis_files(test_directory)
    else:
        print(f"目录 {test_directory} 不存在")
