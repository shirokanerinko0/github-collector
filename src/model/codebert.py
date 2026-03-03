import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModel

# 1. 换用 UniXcoder (它专门优化了代码搜索任务)
checkpoint = "microsoft/unixcoder-base"
tokenizer = AutoTokenizer.from_pretrained(checkpoint)
model = AutoModel.from_pretrained(checkpoint)

# 2. 准备数据
requirement_text = "Fix the bug where user cannot login with valid credentials."

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

# 3. 定义向量化函数 (UniXcoder 的官方用法)
def get_embedding(text):
    # UniXcoder 建议把输入变成列表格式
    inputs = tokenizer([text], return_tensors="pt", max_length=512, truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
        # 同样取 [CLS] (最后一层的第一个token)
        embedding = outputs.last_hidden_state[:, 0, :]
    return embedding

# 4. 计算向量
vec_req = get_embedding(requirement_text)
vec_code1 = get_embedding(code_candidate_1)
vec_code2 = get_embedding(code_candidate_2)

# 5. 计算相似度
score_1 = F.cosine_similarity(vec_req, vec_code1)
score_2 = F.cosine_similarity(vec_req, vec_code2)

print("--- 使用 UniXcoder 直接推理 ---")
print(f"需求: {requirement_text}")
print(f"Code1 (登录): {score_1.item():.4f}")
print(f"Code2 (图片): {score_2.item():.4f}")

