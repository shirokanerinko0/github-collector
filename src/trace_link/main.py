import os,sys,json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from src.utils.utils import load_config
from src.JavaCodeAnalyzer.tree_sitter_java_analyzer import JavaCodeAnalyzer
from src.JavaCodeAnalyzer.code_identifier_processor import CodeIdentifierProcessor
from src.model.unixcoder import calculate_nl_code_similarity
from src.model.wmd_calculator import WMDCalculator
from src.LLMapi.LLM_tset import check_requirement_code_relation

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

def analyze_code_file(file_path):
    """分析代码文件并返回类信息"""
    try:
        return analyzer.analyze_file(file_path)
    except Exception as e:
        print(f"分析文件 {file_path} 时出错: {e}")
        return {"classes": []}

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

def process_code_file(req, file_path):
    """处理单个代码文件并计算与需求的相似度
    
    Args:
        req: 需求的字典，包含 'tokens' 键
        file_path: 代码文件路径
        
    Returns:
        包含文件链接信息的列表
    """
    links = []
    
    # 获取完整文件路径
    full_path = get_source_file_path(file_path)
    if not os.path.exists(full_path):
        print(f"文件不存在: {full_path}")
        return links
    
    print(f"分析文件: {file_path}")
    
    # 分析代码文件
    code_analysis = analyze_code_file(full_path)
    
    # 处理每个类
    for class_info in code_analysis.get('classes', []):
        class_name = class_info.get('name')
        if not class_name:
            continue
        # 分词类名
        class_tokens = code_processor.tokenize_identifier(class_name)
        # 计算相似度（只计算类名标识符相似度）
        similarity = calculate_similarity(req.get('tokens', []), class_tokens)
        
        original_code = class_info.get("original_code", "")
        # 添加链接信息
        links.append({
            'file_path': file_path,
            'class_name': class_name,
            'class_tokens': class_tokens,
            'similarity': similarity,
            'original_code': original_code
        })
    
    return links

def process_files(req, change_files):
    """处理文件并计算与需求的相似度
    
    Args:
        req: 需求的字典，包含 'tokens' 键
        change_files: 变更文件列表
        
    Returns:
        包含文件链接信息的列表，按相似度排序，最多返回前5个
    """
    links = []
    set_files = set()
    # 处理每个变更文件
    for change_file in change_files:
        file_path = change_file.get('file_path')
        if file_path in set_files:
            continue
        if not file_path:
            continue
        set_files.add(file_path)
        
        # 使用 process_code_file 函数处理文件
        file_links = process_code_file(req, file_path)
        links.extend(file_links)
    
    # 当 change_files 为空且配置为 true 时，遍历所有源代码文件
    scan_all_files = CONFIG.get('trace_link', {}).get('scan_all_files_when_no_change_files', False)
    if not change_files and scan_all_files:
        print("change_files 为空，遍历所有源代码文件...")
        src_dir = os.path.join('data', CONFIG['repo'], 'origin_src')
        
        # 遍历所有 Java 文件
        for root, dirs, files in os.walk(src_dir):
            for file in files:
                # 计算相对路径
                file_path = os.path.relpath(os.path.join(root, file), src_dir)
                # 使用 process_code_file 函数处理文件
                file_links = process_code_file(req, file_path)
                links.extend(file_links)
    # 按相似度排序
    links.sort(key=lambda x: x['similarity'], reverse=True)
    # 只保留前5个最相似的链接
    return links[:5]

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


def process_files_unixcoder(req, change_files):

    import torch
    from src.model.unixcoder import get_embeddings

    links = []

    pt_file_path = os.path.join('data', CONFIG['repo'], 'unixcoder_code_vectors.pt')
    if not os.path.exists(pt_file_path):
        print(f"文件不存在: {pt_file_path}")
        return links

    data = torch.load(pt_file_path)

    # 构建需求文本
    requirement_text = f"{req.get('title','')}\n{req.get('description','')}"

    # 计算需求向量
    req_embedding = get_embeddings([requirement_text])[0]

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
        links = process_files_unixcoder(req, change_files)
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


