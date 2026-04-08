from sentence_transformers import SentenceTransformer
import torch
# Load the model (choose 0.5b or 1.5b)
# model = SentenceTransformer(
#     "jinaai/jina-code-embeddings-0.5b",
#     model_kwargs={"torch_dtype": "bfloat16"},
#     tokenizer_kwargs={"padding_side": "left"}
# )
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = SentenceTransformer(
    "jinaai/jina-code-embeddings-0.5b", 
    trust_remote_code=True,
    model_kwargs={"torch_dtype": "bfloat16"},
    tokenizer_kwargs={"padding_side": "left"},
    device=device
)
# Natural language to code
queries = ["print hello world in python", "initialize array of 5 zeros in c++"]
documents = ["print('Hello World!')", "int arr[5] = {0, 0, 0, 0, 0};"]

# Generate embeddings with task-specific prefixes
query_embeddings = model.encode(queries, prompt_name="nl2code_query")
document_embeddings = model.encode(documents, prompt_name="nl2code_document")

# Compute similarity

# 计算余弦值
cosine_values = model.similarity(query_embeddings, document_embeddings)
print(cosine_values)
