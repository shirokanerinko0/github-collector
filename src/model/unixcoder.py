import torch
import torch.nn.functional as F
import model_manager
tokenizer = model_manager.get_unixcoder_tokenizer()
model = model_manager.get_unixcoder_model()
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# 核心函数：把文本/代码转成向量
def get_embeddings(text_list):
    # UniXcoder 的输入处理
    inputs = tokenizer(text_list, padding=True, truncation=True, max_length=512, return_tensors="pt").to(device)
    
    with torch.no_grad():
        outputs = model(**inputs)
        # 取 [CLS] token 的向量 (last_hidden_state 的第 0 个位置)
        embeddings = outputs.last_hidden_state[:, 0, :]
        
        # 【关键步骤】归一化 (Normalization)
        # 这一步能让余弦相似度计算更准确，虽然 cosine_similarity 函数内部会做，但手动做是个好习惯
        embeddings = torch.nn.functional.normalize(embeddings, p=2, dim=1)
        
    return embeddings

def calculate_nl_code_similarity(natural_language, code_snippet):
    """
    计算自然语言片段和代码片段的相似度
    
    Args:
        natural_language (str): 自然语言片段（如需求描述）
        code_snippet (str): 代码片段
    
    Returns:
        float: 相似度得分，范围 [-1, 1]，越接近 1 表示越相似
    """
    # 获取向量
    vec_nl = get_embeddings([natural_language])
    vec_code = get_embeddings([code_snippet])
    
    # 计算余弦相似度
    similarity = F.cosine_similarity(vec_nl, vec_code)
    
    return similarity.item()

# 示例用法
if __name__ == "__main__":
    # 测试数据
    # Query: 需求描述
    query = "Fix the bug where user cannot login with valid credentials."
    
    # Code 1: 真正相关的代码 (登录逻辑)
    code_match = """
    public void login(String username, String password) {
        if (authService.authenticate(username, password)) {
            session.create(username);
        }
    }
    """
    
    # Code 2: 完全不相关的代码 (图片处理)
    code_mismatch = """
    public void resizeImage(File file, int width, int height) {
        Image img = ImageIO.read(file);
        img.getScaledInstance(width, height, Image.SCALE_SMOOTH);
    }
    """
    
    # 计算相似度
    score_match = calculate_nl_code_similarity(query, code_match)
    score_mismatch = calculate_nl_code_similarity(query, code_mismatch)
    
    print(f"查询语句: {query}\n")
    print(f"匹配代码 (Login) 得分: {score_match:.4f}")
    print(f"无关代码 (Image) 得分: {score_mismatch:.4f}")