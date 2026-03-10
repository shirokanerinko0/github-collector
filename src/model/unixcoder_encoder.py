import torch
import numpy as np
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.model.base_encoder import BaseEncoder
import src.model.model_manager as model_manager


class UniXcoderEncoder(BaseEncoder):
    """
    UniXcoder 编码器类
    """
    
    def __init__(self):
        """
        初始化 UniXcoder 编码器
        """
        self.tokenizer = model_manager.get_unixcoder_tokenizer()
        self.model = model_manager.get_unixcoder_model()
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self._embedding_dim = None
    
    def encode(self, texts):
        """
        将文本列表编码为向量
        
        Args:
            texts (list[str]): 文本列表
            
        Returns:
            numpy.ndarray: 编码后的向量数组，形状为 (len(texts), embedding_dim)
        """
        inputs = self.tokenizer(texts, padding=True, truncation=True, max_length=512, return_tensors="pt").to(self.device)
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            embeddings = outputs.last_hidden_state[:, 0, :]
            embeddings = torch.nn.functional.normalize(embeddings, p=2, dim=1)
        
        return embeddings.cpu().numpy()
    
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
