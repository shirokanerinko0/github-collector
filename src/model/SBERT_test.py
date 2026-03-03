from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import model_manager
# 1️⃣ 加载模型
model = model_manager.get_sbert_model()

# 2️⃣ 构建文本
issue_text = "Fix cache expiration bug when loading data"
class_text = "CacheLoader loads and refreshes cached entries,Fix cache expiration bug when loading data"

# 3️⃣ 编码
issue_embedding = model.encode(issue_text, normalize_embeddings=True)
class_embedding = model.encode(class_text, normalize_embeddings=True)
# 4️⃣ 计算相似度
score = cosine_similarity(
    [issue_embedding],
    [class_embedding]
)[0][0]

print("相似度:", score)