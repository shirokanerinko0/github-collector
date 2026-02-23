import fasttext
import fasttext.util
import numpy as np
import json
import os
import re
import sys

# 加载配置
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from src.utils.utils import load_config
CONFIG = load_config()

class CodeIdentifierProcessor:
    def __init__(self):
        """
        初始化代码标识符处理器
        """
        self.model = None
        self._load_word_vector_model()
    
    def _load_word_vector_model(self):
        """
        加载 fastText 词向量模型
        """
        try:
            model_path = CONFIG["fastText"]["model_path"]
            if os.path.exists(model_path):
                self.model = fasttext.load_model(model_path)
                print(f"成功加载 fastText 模型: {model_path}")
            else:
                print(f"警告: fastText 模型文件不存在: {model_path}")
                print("请先运行 fastText_test.py 下载模型")
        except Exception as e:
            print(f"加载 fastText 模型时出错: {e}")
    
    def tokenize_identifier(self, identifier):
        """
        对代码标识符进行分词
        
        Args:
            identifier (str): 代码标识符（类名、方法名等）
            
        Returns:
            list: 分词结果
        """
        if not identifier:
            return []
        
        # 1. 处理下划线命名
        if '_' in identifier:
            tokens = identifier.lower().split('_')
            return [token for token in tokens if token]
        
        # 2. 处理驼峰命名
        # 使用正则表达式分割驼峰命名
        # 规则：大写字母前加空格，然后转换为小写
        tokens = re.sub('([a-z0-9]|(?=[A-Z]))([A-Z])', r'\1 \2', identifier).split()
        tokens = [token.lower() for token in tokens if token]
        
        return tokens
    
    def process_comments(self, comments):
        """
        处理注释内容，提取词语
        
        Args:
            comments (str): 注释内容
            
        Returns:
            list: 处理后的词语列表
        """
        if not comments:
            return []
        
        # 1. 提取注释内容
        extracted_content = []
        
        # 提取 /* */ 注释中的内容
        block_comments = re.findall(r'/\*([\s\S]*?)\*/', comments)
        for block in block_comments:
            extracted_content.append(block)
        
        # 提取 // 注释中的内容
        line_comments = re.findall(r'//(.*)', comments)
        for line in line_comments:
            extracted_content.append(line)
        
        # 合并提取的内容
        cleaned = ' '.join(extracted_content)
        
        # 2. 清洗内容
        # 去除 @param、@return 等标记
        cleaned = re.sub(r'@\w+\s+', '', cleaned)
        # 去除标点符号
        cleaned = re.sub(r'[^a-zA-Z0-9\s\u4e00-\u9fff]', ' ', cleaned)
        # 去除多余的空白字符
        cleaned = ' '.join(cleaned.split())
        
        if not cleaned:
            return []
        
        # 3. 分词
        # 对于中文注释，按字符分词
        # 对于英文注释，按空格分词
        tokens = []
        
        # 检测是否包含中文
        if any('\u4e00' <= char <= '\u9fff' for char in cleaned):
            # 中文按字符分词
            for char in cleaned:
                if char.isalnum() or '\u4e00' <= char <= '\u9fff':
                    tokens.append(char)
        else:
            # 英文按空格分词
            words = cleaned.lower().split()
            for word in words:
                if word:
                    tokens.append(word)
        
        # 4. 停用词过滤
        stop_words = {'the', 'is', 'at', 'which', 'on', 'and', 'in', 'to', 'a', 'for', 'of', 'with', 'as'}
        tokens = [token for token in tokens if token not in stop_words]
        
        # 5. 去除重复词语，保留顺序
        seen = set()
        unique_tokens = []
        for token in tokens:
            if token not in seen:
                seen.add(token)
                unique_tokens.append(token)
        
        return unique_tokens
    
    def get_embeddings(self, tokens):
        """
        获取词语的词向量
        
        Args:
            tokens (list): 词语列表
            
        Returns:
            list: 词向量列表
        """
        if not self.model or not tokens:
            return []
        
        embeddings = []
        for token in tokens:
            try:
                vector = self.model.get_word_vector(token)
                # 归一化向量
                norm = np.linalg.norm(vector)
                if norm > 0:
                    vector = vector / norm
                embeddings.append(vector.tolist())
            except Exception as e:
                print(f"获取词语 '{token}' 的词向量时出错: {e}")
                # 对于无法获取词向量的词语，跳过
                pass
        
        return embeddings
    
    def calculate_boe(self, identifier_tokens, comment_tokens):
        """
        计算 Bag-of-Embeddings
        
        Args:
            identifier_tokens (list): 标识符分词结果
            comment_tokens (list): 注释处理结果
            
        Returns:
            list: 合并后的词向量列表
        """
        # 合并标识符和注释的词向量
        all_tokens = identifier_tokens + comment_tokens
        # 去重，保留顺序
        seen = set()
        unique_tokens = []
        for token in all_tokens:
            if token not in seen:
                seen.add(token)
                unique_tokens.append(token)
        
        # 获取词向量
        embeddings = self.get_embeddings(unique_tokens)
        
        return embeddings
    
    def enhance_json_with_vectors(self, json_data):
        """
        增强 JSON 数据，添加分词和词向量信息
        
        Args:
            json_data (dict): 原始 JSON 数据
            
        Returns:
            dict: 增强后的 JSON 数据
        """
        if not json_data or 'classes' not in json_data:
            return json_data
        
        # 处理每个类
        for class_info in json_data['classes']:
            # 1. 处理类标识符
            class_name = class_info.get('name', '')
            class_tokens = self.tokenize_identifier(class_name)
            
            # 2. 处理类注释
            class_comments = class_info.get('comments', '')
            class_comment_tokens = self.process_comments(class_comments)
            
            # 3. 获取词向量
            class_identifier_embeddings = self.get_embeddings(class_tokens)
            class_comment_embeddings = self.get_embeddings(class_comment_tokens)
            
            # 4. 计算 BoE
            class_boe = self.calculate_boe(class_tokens, class_comment_tokens)
            
            # 5. 添加到类信息中
            class_info['identifier_tokens'] = class_tokens
            class_info['comment_tokens'] = class_comment_tokens
            class_info['identifier_embeddings'] = class_identifier_embeddings
            class_info['comment_embeddings'] = class_comment_embeddings
            class_info['boe_embeddings'] = class_boe
            
            # 6. 处理每个方法
            if 'methods' in class_info:
                for method_info in class_info['methods']:
                    # 处理方法标识符
                    method_name = method_info.get('name', '')
                    method_tokens = self.tokenize_identifier(method_name)
                    
                    # 处理方法注释
                    method_comments = method_info.get('comments', '')
                    method_comment_tokens = self.process_comments(method_comments)
                    
                    # 获取词向量
                    method_identifier_embeddings = self.get_embeddings(method_tokens)
                    method_comment_embeddings = self.get_embeddings(method_comment_tokens)
                    
                    # 计算 BoE
                    method_boe = self.calculate_boe(method_tokens, method_comment_tokens)
                    
                    # 添加到方法信息中
                    method_info['identifier_tokens'] = method_tokens
                    method_info['comment_tokens'] = method_comment_tokens
                    method_info['identifier_embeddings'] = method_identifier_embeddings
                    method_info['comment_embeddings'] = method_comment_embeddings
                    method_info['boe_embeddings'] = method_boe
        
        return json_data
    
    def process_json_file(self, input_file, output_file=None):
        """
        处理单个 JSON 文件
        
        Args:
            input_file (str): 输入 JSON 文件路径
            output_file (str, optional): 输出 JSON 文件路径
            
        Returns:
            bool: 处理是否成功
        """
        try:
            # 读取输入文件
            with open(input_file, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            
            # 增强数据
            enhanced_data = self.enhance_json_with_vectors(json_data)
            
            # 确定输出文件路径
            if not output_file:
                # 默认输出到同一目录，添加 _enhanced 后缀
                base_name = os.path.basename(input_file)
                name_without_ext = os.path.splitext(base_name)[0]
                output_file = os.path.join(os.path.dirname(input_file), f"{name_without_ext}_enhanced.json")
            
            # 保存输出文件
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(enhanced_data, f, indent=2, ensure_ascii=False)
            
            print(f"成功处理文件: {input_file}")
            print(f"增强结果保存到: {output_file}")
            return True
        except Exception as e:
            print(f"处理文件 {input_file} 时出错: {e}")
            return False

# 测试代码
if __name__ == "__main__":
    processor = CodeIdentifierProcessor()
    
    # 测试标识符分词
    test_identifiers = ["InterfaceImpl", "executeOperation", "user_id", "getHTMLContent"]
    print("\n=== 测试标识符分词 ===")
    for identifier in test_identifiers:
        tokens = processor.tokenize_identifier(identifier)
        print(f"{identifier} -> {tokens}")
    
    # 测试注释处理
    test_comments = "/**\n     * Execute operation\n     * @param value Operation value\n     * @return Operation result\n     */"
    print("\n=== 测试注释 ===")
    comment_tokens = processor.process_comments(test_comments)
    print(f"原始注释: {test_comments}")
    print(f"处理结果: {comment_tokens}")
    
    # 测试词向量获取
    if processor.model:
        print("\n=== 测试词向量获取 ===")
        test_tokens = ["execute", "operation", "value"]
        embeddings = processor.get_embeddings(test_tokens)
        print(f"测试词语: {test_tokens}")
        print(f"词向量数量: {len(embeddings)}")
        if embeddings:
            print(f"词向量维度: {len(embeddings[0])}")
            print(f"第一个词向量前10维: {embeddings[0][:10]}")
