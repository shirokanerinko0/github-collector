import fasttext
import os
from src.utils.utils import load_config

_model = None   # 全局缓存


def get_fasttext_model():
    global _model
    
    if _model is None:
        config = load_config()
        model_path = config.get("fastText", {}).get("model_path")
        
        if not model_path or not os.path.exists(model_path):
            raise FileNotFoundError("fastText 模型路径不存在")
        
        print("正在加载 fastText 模型...")
        _model = fasttext.load_model(model_path)
        print("fastText 模型加载完成")
    
    return _model