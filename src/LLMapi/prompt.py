import os
import json

# 获取当前文件所在目录
_current_dir = os.path.dirname(os.path.abspath(__file__))
# JSON文件在 prompt/process_req/ 目录下
_prompt_dir = os.path.join(_current_dir, 'prompt', 'process_req')

# 缓存已加载的提示词
_PROMPTS_CACHE = {}

def _load_prompt_files():
    """从 JSON 文件加载所有提示词"""
    global _PROMPTS_CACHE
    if _PROMPTS_CACHE:
        return _PROMPTS_CACHE
    
    prompts = {}
    
    # 如果目录不存在，返回空字典
    if not os.path.exists(_prompt_dir):
        return prompts
    
    # 遍历目录中的所有 JSON 文件
    for filename in os.listdir(_prompt_dir):
        if filename.endswith('.json'):
            filepath = os.path.join(_prompt_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    name = data.get('name')
                    if name:
                        prompts[name] = data
            except Exception as e:
                print(f"加载提示词文件 {filename} 失败: {e}")
    
    _PROMPTS_CACHE = prompts
    return prompts


def _get_prompts():
    """获取所有提示词（兼容属性访问）"""
    return _load_prompt_files()


# 提供类字典的接口
class _PromptsDict:
    """提示词字典代理类，支持延迟加载"""
    
    def __getitem__(self, key):
        prompts = _load_prompt_files()
        if key not in prompts:
            raise KeyError(key)
        return prompts[key]
    
    def __contains__(self, key):
        return key in _load_prompt_files()
    
    def __iter__(self):
        return iter(_load_prompt_files())
    
    def __len__(self):
        return len(_load_prompt_files())
    
    def keys(self):
        return _load_prompt_files().keys()
    
    def values(self):
        return _load_prompt_files().values()
    
    def items(self):
        return _load_prompt_files().items()
    
    def get(self, key, default=None):
        prompts = _load_prompt_files()
        return prompts.get(key, default)


# PROMPTS 对象
PROMPTS = _PromptsDict()


def get_prompt(prompt_name):
    """
    Get prompt by name.
    
    Args:
        prompt_name: Name of the prompt (e.g., "prompt2", "prompt8")
    
    Returns:
        Prompt string or None
    """
    prompts = _load_prompt_files()
    if prompt_name not in prompts:
        available = list(prompts.keys())
        raise ValueError(f"Unknown prompt: {prompt_name}. Available prompts: {available}")
    return prompts[prompt_name].get("prompt")


def get_prompt_full(prompt_name):
    """
    Get full prompt data by name.
    
    Args:
        prompt_name: Name of the prompt
    
    Returns:
        Full prompt data dict or None
    """
    prompts = _load_prompt_files()
    return prompts.get(prompt_name)


def get_all_prompts():
    """Get all prompts."""
    return _load_prompt_files()


def get_prompt_stats(prompt_name):
    """
    Get statistics for a specific prompt.
    
    Args:
        prompt_name: Name of the prompt
    
    Returns:
        Statistics dictionary or None
    """
    prompts = _load_prompt_files()
    if prompt_name not in prompts:
        available = list(prompts.keys())
        raise ValueError(f"Unknown prompt: {prompt_name}. Available prompts: {available}")
    return prompts[prompt_name].get("statistics")


def list_prompts_by_recall():
    """
    List all prompts sorted by recall rate (descending).
    
    Returns:
        List of tuples (prompt_name, description, recall)
    """
    prompts = _load_prompt_files()
    prompt_list = []
    
    for name, data in prompts.items():
        stats = data.get("statistics")
        if stats:
            recall = stats.get("overall_recall", 0)
            desc = data.get("description", "")
            prompt_list.append((name, desc, recall))
    
    return sorted(prompt_list, key=lambda x: x[2], reverse=True)


def get_best_prompt():
    """
    Get the prompt with the highest recall rate.
    
    Returns:
        Tuple of (prompt_name, prompt_string) or (prompt_name, None)
    """
    ranked = list_prompts_by_recall()
    if not ranked:
        return None, None
    
    best = ranked[0]
    prompt_name = best[0]
    prompt_str = get_prompt(prompt_name)
    return prompt_name, prompt_str


def reload_prompts():
    """重新加载提示词（清除缓存）"""
    global _PROMPTS_CACHE
    _PROMPTS_CACHE = {}
    return _load_prompt_files()


def add_prompt(name, prompt_text, description="", statistics=None):
    """
    添加新提示词并保存到文件
    
    Args:
        name: 提示词名称
        prompt_text: 提示词内容
        description: 提示词描述
        statistics: 统计数据字典
    """
    data = {
        "name": name,
        "description": description,
        "prompt": prompt_text,
        "statistics": statistics or {}
    }
    
    filepath = os.path.join(_prompt_dir, f"{name}.json")
    os.makedirs(_prompt_dir, exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    # 清除缓存
    reload_prompts()


if __name__ == "__main__":
    print("=" * 60)
    print("Available Prompts (sorted by recall):")
    print("=" * 60)
    
    for name, desc, recall in list_prompts_by_recall():
        print(f"\n{name}: {desc}")
        print(f"  Recall: {recall:.4f}")
        stats = get_prompt_stats(name)
        if stats:
            print(f"  Hit Files: {stats.get('total_hit_files')}")
    
    print("\n" + "=" * 60)
    ranked = list_prompts_by_recall()
    if ranked:
        print(f"Best Prompt: {ranked[0][0]} (recall: {ranked[0][2]:.4f})")
    print("=" * 60)