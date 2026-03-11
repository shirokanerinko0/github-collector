import os,sys,json
import torch
import numpy as np
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from src.model.calculate_code_vectors import get_pt_file_name
from src.utils.utils import load_config
from src.JavaCodeAnalyzer.tree_sitter_java_analyzer import JavaCodeAnalyzer
from src.JavaCodeAnalyzer.code_identifier_processor import CodeIdentifierProcessor
from src.model.wmd_calculator import WMDCalculator
from src.LLMapi.LLM_tset import check_requirement_code_relation
from src.model.encoder_factory import EncoderFactory
from src.trace_link.calculate import calculate_recall

config = load_config()
encoder = None
data = None
use_llm_processing = config["requirement_processing"]["use_llm_processing"]
encode_model_name = config.get("encode_model_name", "unixcoder")
top_k = config.get("top_k", 5)
def load_requirements():
    """加载处理后的需求数据"""
    req_file = os.path.join('data', config['repo'], 'requirements_processed'+('_llm' if use_llm_processing else '')+'.json')
    if os.path.exists(req_file):
        with open(req_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def get_source_file_path(file_path):
    """获取源代码文件的完整路径"""
    # 从 change_files 中的相对路径转换为绝对路径
    src_dir = os.path.join('data', config['repo'], 'origin_src')
    return os.path.join(src_dir, file_path)


def check_requirement_code_relation_llm(req, file_path, code_snippet=""):
    """使用LLM判断需求和代码文件是否语义相关
    Args:
        req: 需求对象
        file_path: 代码文件路径
        code_snippet: 代码片段，默认为空字符串，用于直接传递代码内容
    Returns:
        包含关系信息的字典
    """
    # 获取完整文件路径
    full_path = get_source_file_path(file_path)
    if not os.path.exists(full_path):
        print(f"文件不存在: {full_path}")
        exit(1)
    # 读取代码文件内容
    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            code_content = f.read()
    except Exception as e:
        print(f"读取文件 {full_path} 时出错: {e}")
        exit(1)
    
    # 构建需求文本
    req_title = req.get('title', '')
    req_description = req.get('description', '')
    requirement_text = f"{req_title}\n{req_description}"
    
    # 调用LLM API判断关系
    try:
        result_json = check_requirement_code_relation(requirement_text, code_content)
        # 解析JSON结果
        result = json.loads(result_json)
        return result
    except Exception as e:
        return {
            'related': False,
            'reason': f'LLM调用失败: {str(e)}',
            'confidence': 0.0
        }


def process_files_with_encoder(req, change_files):

    links = []

    # 构建需求文本
    requirement_text = req.get('cleaned_summary', '')

    req_embedding = encoder.encode([requirement_text])[0]
    req_embedding = torch.tensor(req_embedding)

    embeddings = data['embeddings']
    device = req_embedding.device
    embeddings = embeddings.to(device)

    # 归一化（如果当初没做）
    req_embedding = torch.nn.functional.normalize(req_embedding, dim=0)
    embeddings = torch.nn.functional.normalize(embeddings, dim=1)

    # 一次性算相似度
    similarities = torch.matmul(
        req_embedding.unsqueeze(0),
        embeddings.T
    ).squeeze(0)

    k = min(top_k, embeddings.shape[0])
    topk_scores, topk_indices = torch.topk(similarities, k=k)

    for score, idx in zip(topk_scores, topk_indices):
        idx = idx.item()

        links.append({
            'file_path': data['file_paths'][idx],
            'class_name': data['class_names'][idx],
            'method_name': data['method_names'][idx],
            'similarity': score.item(),
            'original_code': data['original_code'][idx]
        })

    return links

def trace_links():
    """实现需求到代码的追踪链接"""
    print("开始实现需求到代码的追踪链接...")
    
    # 加载需求数据
    requirements = load_requirements()
    print(f"加载了 {len(requirements)} 个需求")
    
    results = []
    
    # 整体统计
    overall_stats = {
        'total_requirements': len(requirements),
        'requirements_with_change_files': 0,
        'requirements_with_at_least_one_hit': 0,
        'total_change_files': 0,
        'total_hit_files': 0,
        'top_k': top_k,
    }
    
    for req in requirements:
        req_id = req.get('req_id')
        req_title = req.get('title')
        change_files = req.get('change_files', [])
        has_change_files = len(change_files) > 0
        print(f"\n处理需求: {req_id} - {req_title}")
        
        # 处理文件并计算相似度
        links = process_files_with_encoder(req, change_files)
        if(config['trace_link']['use_llm']):
            for link in links:
                file_path = link['file_path']
                # 使用LLM判断关系
                llm_result = check_requirement_code_relation_llm(req, file_path)
                link['llm_result'] = llm_result
            #根据LLM结果排序，related为true且confidence高的排在前面
            links.sort(key=lambda x: (not x['llm_result']['related'], -x['llm_result']['confidence']))
        
        # 计算召回率（仅当有变更文件时）
        recall_info = None
        if has_change_files:
            recall_info = calculate_recall(links, change_files)
            
            # 更新整体统计
            overall_stats['requirements_with_change_files'] += 1
            overall_stats['total_change_files'] += recall_info['total_change_files']
            overall_stats['total_hit_files'] += recall_info['hit_count']
            if recall_info['hit_count'] > 0:
                overall_stats['requirements_with_at_least_one_hit'] += 1
        
        # 添加到结果
        result_item = {
            'req_id': req_id,
            'req_title': req_title,
            'req_description': req.get('description', ''),
            'req_cleaned_summary': req.get('cleaned_summary', ''),
            'req_url': req.get('url', ''),
            # 'req_tokens': req.get('tokens', []),
            'req_type': req.get('type', 'default'),
            'links': links,
            'change_files': change_files
        }
        
        if has_change_files and recall_info:
            result_item['recall'] = recall_info
        
        results.append(result_item)
    
    # 计算整体召回率
    if overall_stats['total_change_files'] > 0:
        overall_stats['overall_recall'] = overall_stats['total_hit_files'] / overall_stats['total_change_files']
    else:
        overall_stats['overall_recall'] = 0.0
    
    # 准备最终输出
    final_output = {
        'results': results,
        'statistics': overall_stats
    }
    
    # 保存结果
    output_file = os.path.join('data', config['repo'],'trace_link'+
                            ('_llm' if config['trace_link']['use_llm'] else '')+
                            ('_scan_all_files' if config['trace_link']['scan_all_files_when_no_change_files'] else '')+
                            (f'_{encode_model_name}' if encode_model_name else '')+
                            (f'_top{top_k}' if top_k else '')+
                            ('.json'))
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(final_output, f, indent=2, ensure_ascii=False, separators=(',', ': '))
    
    print(f"\n追踪链接结果已保存到: {output_file}")
    
    # 打印结果摘要
    print("\n" + "=" * 60)
    print("整体统计:")
    print(f"  总需求数: {overall_stats['total_requirements']}")
    print(f"  有变更文件的需求数: {overall_stats['requirements_with_change_files']}")
    print(f"  至少命中一个文件的需求数: {overall_stats['requirements_with_at_least_one_hit']}")
    print(f"  总变更文件数: {overall_stats['total_change_files']}")
    print(f"  命中文件数: {overall_stats['total_hit_files']}")
    print(f"  整体召回率: {overall_stats.get('overall_recall', 0):.4f}")
    print("=" * 60)
    
    for result in results:
        print(f"\n需求 {result['req_id']}: {result['req_title']}")
        change_files = result.get('change_files', [])
        if len(change_files) > 0:
            recall = result.get('recall', {})
            print(f"  变更文件: {recall['total_change_files']}, 命中: {recall['hit_count']}, 召回率: {recall['recall']:.4f}")
        for link in result['links'][:3]:  # 只显示前3个最相似的链接
            print(f"  - 文件: {link['file_path']}, 类: {link['class_name']}, 相似度: {link['similarity']:.4f}")


def get_data():
    # 根据模型名称生成pt文件名
    pt_file_name = get_pt_file_name()
    pt_file_path = os.path.join('data', config['repo'], pt_file_name)
    if not os.path.exists(pt_file_path):
        print(f"文件不存在: {pt_file_path}")
        exit(1)
    data_ = torch.load(pt_file_path)
    return data_

def get_encoder():
    # 创建编码器并计算需求向量
    print(f"正在使用编码器: {encode_model_name}")
    encoder_ = EncoderFactory.create_encoder(encode_model_name)
    return encoder_

if __name__ == "__main__":
    data = get_data()
    encoder = get_encoder()
    trace_links()


