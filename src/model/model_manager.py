import fasttext
import os
import sys
from sentence_transformers import SentenceTransformer
# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.utils.utils import load_config

fasttext_model = None   # 全局缓存
sbert_model = None      # 全局缓存

def get_fasttext_model():
    global fasttext_model
    
    if fasttext_model is None:
        config = load_config()
        model_path = config.get("fastText", {}).get("model_path")
        
        if not model_path or not os.path.exists(model_path):
            raise FileNotFoundError("fastText 模型路径不存在")
        
        print("正在加载 fastText 模型...")
        fasttext_model = fasttext.load_model(model_path)
        print("fastText 模型加载完成")
    
    return fasttext_model

def get_sbert_model():
    global sbert_model

    if sbert_model is None:
        config = load_config()
        model_name = config.get("SBERT", {}).get("model_name", "all-MiniLM-L6-v2")

        print("正在加载 SBERT 模型...")
        sbert_model = SentenceTransformer(model_name)
        print("SBERT 模型加载完成")

    return sbert_model