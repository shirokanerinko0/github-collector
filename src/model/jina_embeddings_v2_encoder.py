import numpy as np
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.model.base_encoder import BaseEncoder
import src.model.model_manager as model_manager


class JinaEmbeddingsV2Encoder(BaseEncoder):
    """
    Jina Embeddings V2 编码器类 (jinaai/jina-embeddings-v2-base-code)
    """
    
    def __init__(self):
        """
        初始化 Jina Embeddings V2 编码器
        """
        self.model = model_manager.get_jina_embeddings_v2_model()
        self._embedding_dim = None
    
    def encode(self, texts):
        """
        将文本列表编码为向量
        
        Args:
            texts (list[str]): 文本列表
            
        Returns:
            numpy.ndarray: 编码后的向量数组，形状为 (len(texts), embedding_dim)
        """
        return self.model.encode(texts)
    
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
