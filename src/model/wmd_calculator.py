#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Word Mover's Distance (WMD) 计算模块
用于计算两个tokens列表之间的语义距离
"""

import numpy as np
import os
import sys
from scipy.optimize import linprog

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from src.utils.utils import load_config
from src.model.model_manager import get_fasttext_model

class WMDCalculator:
    """
    WMD 计算器类
    用于计算两个tokens列表之间的语义距离
    """
    
    def __init__(self):
        """
        初始化 WMD 计算器
        """
        # 加载配置
        self.config = load_config()
        
        # 加载 fastText 模型
        self.model = get_fasttext_model()
    
    def get_word_vector(self, word):
        """
        获取词向量
        :param word: 词语
        :return: 词向量，如果词语不在词典中返回None
        """
        if not self.model:
            return None
        
        try:
            return self.model.get_word_vector(word)
        except Exception as e:
            print(f"获取词向量失败: {str(e)}")
            return None
    
    def calculate_wmd(self, tokens1, tokens2):
        """
        计算两个tokens列表之间的 Word Mover's Distance
        词权相同
        
        :param tokens1: 第一个tokens列表
        :param tokens2: 第二个tokens列表
        :return: WMD值，如果计算失败返回None
        """
        if not self.model:
            print("错误: fastText 模型未加载")
            return None
        
        if not tokens1 or not tokens2:
            print("错误: tokens列表不能为空")
            return None
        
        try:
            # 获取两个列表的词向量
            vectors1 = []
            valid_tokens1 = []
            for token in tokens1:
                vec = self.get_word_vector(token)
                if vec is not None:
                    vectors1.append(vec)
                    valid_tokens1.append(token)
            
            vectors2 = []
            valid_tokens2 = []
            for token in tokens2:
                vec = self.get_word_vector(token)
                if vec is not None:
                    vectors2.append(vec)
                    valid_tokens2.append(token)
            
            if not vectors1 or not vectors2:
                print("警告: 无法获取有效的词向量")
                return None
            
            # 计算词权（相同权重）- 确保权重之和为1
            weights1 = np.ones(len(vectors1)) / len(vectors1)
            weights2 = np.ones(len(vectors2)) / len(vectors2)
            
            # 计算距离矩阵
            distance_matrix = np.zeros((len(vectors1), len(vectors2)))
            for i, vec1 in enumerate(vectors1):
                for j, vec2 in enumerate(vectors2):
                    # 计算欧氏距离
                    distance_matrix[i, j] = np.linalg.norm(vec1 - vec2)
            
            # 构建线性规划问题
            # 变量是传输矩阵的扁平化
            num_vars = len(vectors1) * len(vectors2)
            
            # 目标函数：最小化总传输成本
            c = distance_matrix.flatten()
            
            # 约束条件1：从第一个文档的每个词出发的总传输量等于该词的权重
            A_eq = []
            b_eq = []
            
            # 行约束（每个词的出流量等于其权重）
            for i in range(len(vectors1)):
                row = np.zeros(num_vars)
                for j in range(len(vectors2)):
                    row[i * len(vectors2) + j] = 1
                A_eq.append(row)
                b_eq.append(weights1[i])
            
            # 列约束（每个词的入流量等于其权重）
            for j in range(len(vectors2)):
                col = np.zeros(num_vars)
                for i in range(len(vectors1)):
                    col[i * len(vectors2) + j] = 1
                A_eq.append(col)
                b_eq.append(weights2[j])
            
            # 变量非负约束
            bounds = [(0, None)] * num_vars
            
            # 求解线性规划
            res = linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
            
            if res.success:
                # 计算总传输成本
                total_distance = res.fun
                return total_distance
            else:
                print(f"线性规划求解失败: {res.message}")
                return None
            
        except Exception as e:
            print(f"计算 WMD 失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def calculate_similarity(self, tokens1, tokens2):
        """
        计算两个tokens列表之间的相似度（基于WMD）
        相似度 = 1 / (1 + WMD)
        
        :param tokens1: 第一个tokens列表
        :param tokens2: 第二个tokens列表
        :return: 相似度值，如果计算失败返回None
        """
        wmd = self.calculate_wmd(tokens1, tokens2)
        if wmd is not None:
            return 1.0 / (1.0 + wmd)
        return None
    


if __name__ == "__main__":
    """
    测试 WMD 计算器
    """
    calculator = WMDCalculator()
    
    # 测试示例1：基础测试
    tokens1 = ["animal", "cat", "pet", "canine"]
    tokens2 = ["dog", "canine"]
    tokens3 = ["cat", "pet", "animal"]
    
    print("测试 WMD 计算:")
    print(f"tokens1: {tokens1}")
    print(f"tokens2: {tokens2}")
    print(f"tokens3: {tokens3}")
    
    wmd12 = calculator.calculate_wmd(tokens1, tokens2)
    wmd13 = calculator.calculate_wmd(tokens1, tokens3)
    wmd11 = calculator.calculate_wmd(tokens1, tokens1)  # 相同词的距离应为0
    
    print(f"WMD(tokens1, tokens2): {wmd12}")
    print(f"WMD(tokens1, tokens3): {wmd13}")
    print(f"WMD(tokens1, tokens1): {wmd11}")
    