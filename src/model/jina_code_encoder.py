import numpy as np
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.model.base_encoder import BaseEncoder
import src.model.model_manager as model_manager
import torch
print(torch.__version__)
print(torch.cuda.is_available())
print(torch.cuda.device_count())
print(torch.cuda.get_device_name(0))
class JinaCodeEncoder(BaseEncoder):
    """
    Jina Code Embeddings 编码器类 (jinaai/jina-code-embeddings-0.5b)
    """
    
    def __init__(self):
        """
        初始化 Jina Code Embeddings 编码器
        """
        self.model = model_manager.get_jina_code_model()
        self._embedding_dim = None
    
    def encode(self, texts):
        """
        将文本列表编码为向量
        
        Args:
            texts (list[str]): 文本列表
            
        Returns:
            numpy.ndarray: 编码后的向量数组，形状为 (len(texts), embedding_dim)
        """
        return self.model.encode(texts, convert_to_tensor=True,show_progress_bar=False)
    
    def get_embedding_dim(self):
        """
        获取嵌入向量的维度
        
        Returns:
            int: 嵌入向量维度
        """
        if self._embedding_dim is None:
            test_emb = self.encode(["test"])
            self._embedding_dim = test_emb.shape[1]
        return self._embedding_dim
