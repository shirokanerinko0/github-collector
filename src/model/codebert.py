import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModel

# 1. 加载模型
# CodeBERT 是双模态模型（NL + PL），它可以同时理解自然语言和编程语言
checkpoint = "microsoft/codebert-base"
tokenizer = AutoTokenizer.from_pretrained(checkpoint)
model = AutoModel.from_pretrained(checkpoint)

# 2. 准备数据
# 模拟一条需求（GitHub Issue）
requirement_text = "user login with valid credentials."

# 模拟两段代码（一段是相关的，一段是不相关的）
code_candidate_1 = """
public class AuthController {
    public void login(String username, String password) {
        // Authenticate user logic
        if (isValid(username, password)) {
            session.create();
        }
    }
}
"""

code_candidate_2 = """
public class ImageUtils {
    public void resizeImage(File file, int width, int height) {
        // Image processing logic
        System.out.println("Resizing image...");
    }
}
"""

# 3. 定义向量化函数
def get_embedding(text, is_code=False):
    # CodeBERT 的一个小技巧：如果是代码，通常会截断得长一点；如果是文本，短一点
    # 但为了简单，这里统一处理
    if is_code:
        # 代码太长需要截断，CodeBERT最大支持512
        inputs = tokenizer(text, return_tensors="pt", max_length=512, truncation=True, padding=True)
    else:
        inputs = tokenizer(text, return_tensors="pt", max_length=128, truncation=True, padding=True)
    
    with torch.no_grad():
        outputs = model(**inputs)
        # 取 [CLS] token 的向量作为这句话/这段代码的语义表示
        embedding = outputs.last_hidden_state[:, 0, :]
    return embedding

# 4. 计算向量
vec_req = get_embedding(requirement_text, is_code=False)
vec_code1 = get_embedding(code_candidate_1, is_code=True)
vec_code2 = get_embedding(code_candidate_2, is_code=True)

# 5. 计算相似度 (余弦相似度)
score_1 = F.cosine_similarity(vec_req, vec_code1)
score_2 = F.cosine_similarity(vec_req, vec_code2)

print(f"需求与 Code1 (登录逻辑) 的相似度: {score_1.item():.4f}")
print(f"需求与 Code2 (图片处理) 的相似度: {score_2.item():.4f}")

# 预期结果：Code1 的分数应该明显高于 Code2