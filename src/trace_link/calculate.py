import os,sys,json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from src.utils.utils import load_config
config = load_config()
def calculate_recall(links, change_files):
    """
    计算召回情况
    
    Args:
        links (list): 预测的链接列表，每个元素包含 'file_path' 字段
        change_files (list): 实际变更的文件列表，每个元素可以是字符串或包含 'file_path' 字段的字典
    
    Returns:
        dict: 包含召回统计信息的字典
            - total_change_files: 变更文件总数
            - hit_count: 命中的变更文件数
            - recall: 召回率 (hit_count / total_change_files)
            - hit_files: 命中的文件列表
            - missed_files: 未命中的文件列表
    """
    # 提取实际变更的文件路径集合（标准化路径）
    actual_file_set = set()
    for cf in change_files:
        if isinstance(cf, str):
            file_path = cf
        elif isinstance(cf, dict) and 'file_path' in cf:
            file_path = cf['file_path']
        else:
            continue
        # 标准化路径分隔符
        normalized_path = os.path.normpath(file_path)
        actual_file_set.add(normalized_path)
    
    # 提取预测链接的文件路径集合（标准化路径）
    predicted_file_set = set()
    for link in links:
        if 'file_path' in link:
            normalized_path = os.path.normpath(link['file_path'])
            predicted_file_set.add(normalized_path)
    
    # 计算命中
    hit_files = actual_file_set & predicted_file_set
    missed_files = actual_file_set - predicted_file_set
    
    total_change_files = len(actual_file_set)
    hit_count = len(hit_files)
    recall = hit_count / total_change_files if total_change_files > 0 else 0.0
    
    return {
        'total_change_files': total_change_files,
        'hit_count': hit_count,
        'recall': recall,
        'hit_files': list(hit_files),
        'missed_files': list(missed_files)
    }
