import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.model.base_encoder import BaseEncoder
from src.model.unixcoder_encoder import UniXcoderEncoder
from src.model.jina_code_encoder import JinaCodeEncoder
from src.model.jina_embeddings_v2_encoder import JinaEmbeddingsV2Encoder


class EncoderFactory:
    """
    编码器工厂类，用于创建不同类型的编码器
    """
    
    ENCODER_TYPES = {
        'unixcoder': UniXcoderEncoder,
        'jina_code': JinaCodeEncoder,
        'jina_embeddings_v2': JinaEmbeddingsV2Encoder,
    }
    
    @classmethod
    def create_encoder(cls, encoder_type):
        """
        创建编码器实例
        
        Args:
            encoder_type (str): 编码器类型，可选值: 'unixcoder', 'jina_code', 'jina_embeddings_v2'
            
        Returns:
            BaseEncoder: 编码器实例
            
        Raises:
            ValueError: 如果encoder_type不支持
        """
        encoder_class = cls.ENCODER_TYPES.get(encoder_type.lower())
        if encoder_class is None:
            raise ValueError(
                f"不支持的编码器类型: {encoder_type}. "
                f"支持的类型: {list(cls.ENCODER_TYPES.keys())}"
            )
        return encoder_class()
    
    @classmethod
    def get_supported_encoders(cls):
        """
        获取所有支持的编码器类型
        
        Returns:
            list[str]: 支持的编码器类型列表
        """
        return list(cls.ENCODER_TYPES.keys())
