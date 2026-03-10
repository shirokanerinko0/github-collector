import os,sys,json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from src.utils.utils import load_config
from src.JavaCodeAnalyzer.tree_sitter_java_analyzer import JavaCodeAnalyzer
from src.JavaCodeAnalyzer.code_identifier_processor import CodeIdentifierProcessor
from src.model.wmd_calculator import WMDCalculator
from src.LLMapi.LLM_tset import check_requirement_code_relation
from src.model.encoder_factory import EncoderFactory

CONFIG = load_config()
analyzer = JavaCodeAnalyzer()
code_processor = CodeIdentifierProcessor()
wmd_calculator = WMDCalculator()

def load_requirements():
    """加载处理后的需求数据"""
    # 直接使用 repo 目录，因为文件结构是 data/{repo}/requirements_processed.json
    req_file = os.path.join('data', CONFIG['repo'], 'requirements_processed.json')
    if os.path.exists(req_file):
        with open(req_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def get_source_file_path(file_path):
    """获取源代码文件的完整路径"""
    # 从 change_files 中的相对路径转换为绝对路径
    src_dir = os.path.join('data', CONFIG['repo'], 'origin_src')
    return os.path.join(src_dir, file_path)

def calculate_similarity(req_tokens, code_tokens):
    """计算需求与代码的相似度"""
    if not req_tokens or not code_tokens:
        return 0.0
    try:
        similarity = wmd_calculator.calculate_similarity(req_tokens, code_tokens)
        return similarity if similarity is not None else 0.0
    except Exception as e:
        print(f"计算相似度时出错: {e}")
        return 0.0



def check_requirement_code_relation_llm(req, file_path):
    """使用LLM判断需求和代码文件是否语义相关
    Args:
        req: 需求对象
        file_path: 代码文件路径
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

    import torch
    import numpy as np

    links = []

    # 获取配置的模型名称
    encode_model_name = CONFIG.get("encode_model_name", "unixcoder")
    
    # 根据模型名称生成pt文件名
    pt_file_name = f"{encode_model_name}_code_vectors.pt"
    pt_file_path = os.path.join('data', CONFIG['repo'], pt_file_name)
    
    if not os.path.exists(pt_file_path):
        print(f"文件不存在: {pt_file_path}")
        return links

    data = torch.load(pt_file_path)

    # 构建需求文本
    requirement_text = f"{req.get('title','')}\n{req.get('description','')}"

    # 创建编码器并计算需求向量
    print(f"正在使用编码器: {encode_model_name}")
    encoder = EncoderFactory.create_encoder(encode_model_name)
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

    k = min(5, embeddings.shape[0])
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
    
    for req in requirements:
        req_id = req.get('req_id')
        req_title = req.get('title')
        req_description = req.get('description')
        req_tokens = req.get('tokens', [])
        change_files = req.get('change_files', [])
        print(f"\n处理需求: {req_id} - {req_title}")
        
        # 处理文件并计算相似度
        links = process_files_with_encoder(req, change_files)
        if(CONFIG['trace_link']['use_llm']):
            for link in links:
                file_path = link['file_path']
                # 使用LLM判断关系
                llm_result = check_requirement_code_relation_llm(req, file_path)
                link['llm_result'] = llm_result
            #根据LLM结果排序，related为true且confidence高的排在前面
            links.sort(key=lambda x: (not x['llm_result']['related'], -x['llm_result']['confidence']))
        # 添加到结果
        results.append({
            'req_id': req_id,
            'req_title': req_title,
            'req_description': req_description,
            'req_url': req.get('url', ''),
            'req_tokens': req_tokens,
            'links': links
        })
    
    # 保存结果
    output_file = os.path.join('data', CONFIG['repo'],'trace_link'+
                            ('_llm' if CONFIG['trace_link']['use_llm'] else '')+
                            ('_scan_all_files' if CONFIG['trace_link']['scan_all_files_when_no_change_files'] else '')+'.json')
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False, separators=(',', ': '))
    
    print(f"\n追踪链接结果已保存到: {output_file}")
    
    # 打印结果摘要
    for result in results:
        print(f"\n需求 {result['req_id']}: {result['req_title']}")
        for link in result['links'][:3]:  # 只显示前3个最相似的链接
            print(f"  - 文件: {link['file_path']}, 类: {link['class_name']}, 相似度: {link['similarity']:.4f}")

if __name__ == "__main__":
    trace_links()


