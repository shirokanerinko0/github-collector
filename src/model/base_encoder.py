from abc import ABC, abstractmethod
import numpy as np


class BaseEncoder(ABC):
    """
    编码器基类，所有编码器都需要实现此接口
    """
    
    @abstractmethod
    def encode(self, texts):
        """
        将文本列表编码为向量
        
        Args:
            texts (list[str]): 文本列表
            
        Returns:
            numpy.ndarray: 编码后的向量数组，形状为 (len(texts), embedding_dim)
        """
        pass
    
    @abstractmethod
    def get_embedding_dim(self):
        """
        获取嵌入向量的维度
        
        Returns:
            int: 嵌入向量维度
        """
        pass
