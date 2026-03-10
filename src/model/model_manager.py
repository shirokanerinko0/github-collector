import fasttext
import os
import sys
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModel
import torch
# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.utils.utils import load_config
config = load_config()

fasttext_model = None   # 全局缓存
sbert_model = None      # 全局缓存
unixcoder_model = None  # 全局缓存
unixcoder_tokenizer = None  # 全局缓存
jina_code_model = None  # 全局缓存
jina_embeddings_v2_model = None  # 全局缓存

def get_unixcoder_model():
    global unixcoder_model
    if unixcoder_model is None:
        model_name = config.get("unixcoder", {}).get("model_name", "microsoft/unixcoder-base")
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print("正在加载 UniXcoder 模型...")
        unixcoder_model = AutoModel.from_pretrained(model_name).to(device)
        print("UniXcoder 模型加载完成")

    return unixcoder_model

def get_unixcoder_tokenizer():
    global unixcoder_tokenizer
    if unixcoder_tokenizer is None:
        model_name = config.get("unixcoder", {}).get("model_name", "microsoft/unixcoder-base")
        print("正在加载 UniXcoder 分词器...")
        unixcoder_tokenizer = AutoTokenizer.from_pretrained(model_name)
        print("UniXcoder 分词器加载完成")
    
    return unixcoder_tokenizer

def get_fasttext_model():
    global fasttext_model
    
    if fasttext_model is None:
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
        model_name = config.get("SBERT", {}).get("model_name", "all-MiniLM-L6-v2")

        print("正在加载 SBERT 模型...")
        sbert_model = SentenceTransformer(model_name)
        print("SBERT 模型加载完成")

    return sbert_model


def get_jina_code_model():
    global jina_code_model
    
    if jina_code_model is None:
        model_name = config.get("jina_code", {}).get("model_name", "jinaai/jina-code-embeddings-0.5b")
        
        print("正在加载 Jina Code Embeddings 模型...")
        jina_code_model = SentenceTransformer(model_name, trust_remote_code=True)
        print("Jina Code Embeddings 模型加载完成")
    
    return jina_code_model


def get_jina_embeddings_v2_model():
    global jina_embeddings_v2_model
    
    if jina_embeddings_v2_model is None:
        model_name = config.get("jina_embeddings_v2", {}).get("model_name", "jinaai/jina-embeddings-v2-base-code")
        
        print("正在加载 Jina Embeddings V2 模型...")
        jina_embeddings_v2_model = SentenceTransformer(model_name, trust_remote_code=True)
        print("Jina Embeddings V2 模型加载完成")
    
    return jina_embeddings_v2_model