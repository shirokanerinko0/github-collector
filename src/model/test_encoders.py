import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.model.encoder_factory import EncoderFactory
from sklearn.metrics.pairwise import cosine_similarity


def test_encoders():
    """
    测试所有编码器是否正常工作
    """
    print("=" * 80)
    print("测试编码器工厂和所有编码器")
    print("=" * 80)
    
    # 测试支持的编码器类型
    supported_encoders = EncoderFactory.get_supported_encoders()
    print(f"\n支持的编码器类型: {supported_encoders}")
    
    # 测试数据
    test_texts = [
        "print hello world",
        "int main() { cout<<\"hello world\";return 0; }",
        "public class Test { public static void main(String[] args) {sys.out.println(\"hello world\");} }"
    ]
    
    print(f"\n测试文本: {test_texts}")
    print()
    
    # 测试每个编码器
    for encoder_type in supported_encoders:
        print("-" * 80)
        print(f"测试编码器: {encoder_type}")
        print("-" * 80)
        
        try:
            # 创建编码器
            encoder = EncoderFactory.create_encoder(encoder_type)
            
            # 编码测试文本
            embeddings = encoder.encode(test_texts)
            
            # 获取嵌入维度
            dim = encoder.get_embedding_dim()
            
            print(f"✓ 编码器创建成功")
            print(f"✓ 嵌入维度: {dim}")
            print(f"✓ 嵌入形状: {embeddings.shape}")
            
            # 计算相似度矩阵
            sim_matrix = cosine_similarity(embeddings)
            print(f"✓ 相似度矩阵计算成功")
            print(f"  相似度矩阵:\n{sim_matrix}")
            
        except Exception as e:
            print(f"✗ 测试失败: {e}")
            import traceback
            traceback.print_exc()
        
        print()
    
    print("=" * 80)
    print("所有测试完成!")
    print("=" * 80)


if __name__ == "__main__":
    test_encoders()
