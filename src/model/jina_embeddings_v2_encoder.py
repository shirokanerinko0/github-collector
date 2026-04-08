import numpy as np
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.model.base_encoder import BaseEncoder
import src.model.model_manager as model_manager
from src.utils.utils import load_config
CONFIG = load_config()



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
        batch_size = CONFIG.get("batch_size", 2)
        return self.model.encode(texts, batch_size=batch_size, convert_to_tensor=True,show_progress_bar=False)
    
    def encode_query(self, texts):
        """
        将查询文本编码为向量
        
        Args:
            query (str): 查询文本
            
        Returns:
            numpy.ndarray: 编码后的向量，形状为 (embedding_dim,)
        """
        batch_size = CONFIG.get("batch_size", 2)
        result = self.model.encode(
            texts, 
            batch_size=batch_size, 
            convert_to_tensor=True,
            show_progress_bar=False,
            prompt_name="nl2code_query"
        )
        return result

    def encode_document(self, texts):
        """
        将代码片段编码为向量
        
        Args:
            document (str): 代码片段
            
        Returns:
            numpy.ndarray: 编码后的向量，形状为 (embedding_dim,)
        """
        batch_size = CONFIG.get("batch_size", 2)
        result = self.model.encode(
            texts, 
            batch_size=batch_size, 
            convert_to_tensor=True,
            show_progress_bar=False,
            prompt_name="nl2code_document"
        )
        return result

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


if __name__ == "__main__":
    jina_embeddings_v2_encoder = JinaEmbeddingsV2Encoder()
    encode = jina_embeddings_v2_encoder.encode_document(["cout << \"hello world\" << endl;", "print \"hello world\""])
    encode2 = jina_embeddings_v2_encoder.encode_query(["print \"hello world\""])
    print(encode.shape)
    print(encode)
    sim = F.cosine_similarity(encode, encode2)
    print(sim.item()) # .item() 会自动把结果转成 Python 数值