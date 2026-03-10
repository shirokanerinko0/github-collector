import torch
import torch.nn.functional as F
import os,sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))


import src.model.model_manager as model_manager
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
    # 测试数据 - 加密解密相关
    issue_text = "Implement a data encryption and decryption mechanism using AES algorithm. The system should support generating secure keys, encrypting sensitive data with proper padding, and decrypting ciphertext back to original plaintext. It should handle both string and binary data."

    code1 = """
public class AesEncryptionService {
    
    private static final String ALGORITHM = "AES";
    private static final String TRANSFORMATION = "AES/CBC/PKCS5Padding";
    private static final int KEY_SIZE = 256;
    private static final int IV_SIZE = 16;
    
    public SecretKey generateKey() throws NoSuchAlgorithmException {
        KeyGenerator keyGenerator = KeyGenerator.getInstance(ALGORITHM);
        keyGenerator.init(KEY_SIZE, new SecureRandom());
        return keyGenerator.generateKey();
    }
    
    public byte[] generateIV() {
        byte[] iv = new byte[IV_SIZE];
        new SecureRandom().nextBytes(iv);
        return iv;
    }
    
    public byte[] encrypt(String plaintext, SecretKey key, byte[] iv) throws Exception {
        Cipher cipher = Cipher.getInstance(TRANSFORMATION);
        IvParameterSpec ivSpec = new IvParameterSpec(iv);
        cipher.init(Cipher.ENCRYPT_MODE, key, ivSpec);
        return cipher.doFinal(plaintext.getBytes(StandardCharsets.UTF_8));
    }
    
    public String decrypt(byte[] ciphertext, SecretKey key, byte[] iv) throws Exception {
        Cipher cipher = Cipher.getInstance(TRANSFORMATION);
        IvParameterSpec ivSpec = new IvParameterSpec(iv);
        cipher.init(Cipher.DECRYPT_MODE, key, ivSpec);
        byte[] decrypted = cipher.doFinal(ciphertext);
        return new String(decrypted, StandardCharsets.UTF_8);
    }
}
"""

    code2 = """
public class SimpleCryptoManager {
    
    public String encrypt(String data, String secretKey) throws Exception {
        byte[] key = secretKey.getBytes(StandardCharsets.UTF_8);
        MessageDigest sha = MessageDigest.getInstance("SHA-256");
        key = sha.digest(key);
        key = Arrays.copyOf(key, 16);
        
        SecretKeySpec secretKeySpec = new SecretKeySpec(key, "AES");
        Cipher cipher = Cipher.getInstance("AES/ECB/PKCS5Padding");
        cipher.init(Cipher.ENCRYPT_MODE, secretKeySpec);
        
        byte[] encrypted = cipher.doFinal(data.getBytes(StandardCharsets.UTF_8));
        return Base64.getEncoder().encodeToString(encrypted);
    }
    
    public String decrypt(String encryptedData, String secretKey) throws Exception {
        byte[] key = secretKey.getBytes(StandardCharsets.UTF_8);
        MessageDigest sha = MessageDigest.getInstance("SHA-256");
        key = sha.digest(key);
        key = Arrays.copyOf(key, 16);
        
        SecretKeySpec secretKeySpec = new SecretKeySpec(key, "AES");
        Cipher cipher = Cipher.getInstance("AES/ECB/PKCS5Padding");
        cipher.init(Cipher.DECRYPT_MODE, secretKeySpec);
        
        byte[] decrypted = cipher.doFinal(Base64.getDecoder().decode(encryptedData));
        return new String(decrypted, StandardCharsets.UTF_8);
    }
}
"""

    code3 = """
public class Base64EncoderDecoder {
    
    public String encode(String plaintext) {
        byte[] bytes = plaintext.getBytes(StandardCharsets.UTF_8);
        return Base64.getEncoder().encodeToString(bytes);
    }
    
    public String decode(String encodedString) {
        byte[] decodedBytes = Base64.getDecoder().decode(encodedString);
        return new String(decodedBytes, StandardCharsets.UTF_8);
    }
}
"""

    code4 = """
public class HashCalculator {
    
    public String computeSHA256(String input) throws NoSuchAlgorithmException {
        MessageDigest digest = MessageDigest.getInstance("SHA-256");
        byte[] hash = digest.digest(input.getBytes(StandardCharsets.UTF_8));
        return bytesToHex(hash);
    }
    
    public boolean verifyHash(String input, String expectedHash) throws NoSuchAlgorithmException {
        String actualHash = computeSHA256(input);
        return MessageDigest.isEqual(actualHash.getBytes(), expectedHash.getBytes());
    }
    
    private String bytesToHex(byte[] bytes) {
        StringBuilder hexString = new StringBuilder();
        for (byte b : bytes) {
            String hex = Integer.toHexString(0xff & b);
            if (hex.length() == 1) {
                hexString.append('0');
            }
            hexString.append(hex);
        }
        return hexString.toString();
    }
}
"""

    code5 = """
public class DigitalSignatureManager {
    
    public byte[] signData(byte[] data, PrivateKey privateKey) throws Exception {
        Signature signature = Signature.getInstance("SHA256withRSA");
        signature.initSign(privateKey);
        signature.update(data);
        return signature.sign();
    }
    
    public boolean verifySignature(byte[] data, byte[] signatureBytes, PublicKey publicKey) throws Exception {
        Signature signature = Signature.getInstance("SHA256withRSA");
        signature.initVerify(publicKey);
        signature.update(data);
        return signature.verify(signatureBytes);
    }
}
"""

    code6 = """
public class FileArchiver {
    
    public void compressFiles(List<File> files, String outputPath) throws IOException {
        try (FileOutputStream fos = new FileOutputStream(outputPath);
             ZipOutputStream zos = new ZipOutputStream(fos)) {
            
            for (File file : files) {
                if (file.isFile()) {
                    ZipEntry zipEntry = new ZipEntry(file.getName());
                    zos.putNextEntry(zipEntry);
                    
                    try (FileInputStream fis = new FileInputStream(file)) {
                        byte[] buffer = new byte[1024];
                        int len;
                        while ((len = fis.read(buffer)) > 0) {
                            zos.write(buffer, 0, len);
                        }
                    }
                    zos.closeEntry();
                }
            }
        }
    }
}
"""

    # 计算相似度
    score1 = calculate_nl_code_similarity(issue_text, code1)
    score2 = calculate_nl_code_similarity(issue_text, code2)
    score3 = calculate_nl_code_similarity(issue_text, code3)
    score4 = calculate_nl_code_similarity(issue_text, code4)
    score5 = calculate_nl_code_similarity(issue_text, code5)
    score6 = calculate_nl_code_similarity(issue_text, code6)
    
    print("=" * 60)
    print("加密解密相关 - UniXcoder模型测试:")
    print("=" * 60)
    print(f"1. 与AES加密服务 (AesEncryptionService) 的相似度:  {score1:.4f}")
    print(f"2. 与简单加密管理器 (SimpleCryptoManager) 的相似度:   {score2:.4f}")
    print(f"3. 与Base64编解码 (Base64EncoderDecoder) 的相似度:      {score3:.4f}")
    print(f"4. 与哈希计算器 (HashCalculator) 的相似度:              {score4:.4f}")
    print(f"5. 与数字签名管理器 (DigitalSignatureManager) 的相似度: {score5:.4f}")
    print(f"6. 与文件归档工具 (FileArchiver) 的相似度:             {score6:.4f}")
    print("=" * 60)
    print("\n分析:")
    print("- 前两个是真正的AES加密解密代码")
    print("- 后四个容易混淆（Base64、哈希、签名、压缩）")
    print("- 最后一个完全不相关")