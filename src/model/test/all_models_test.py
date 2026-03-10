from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import torch
import torch.nn.functional as F
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

import src.model.model_manager as model_manager

# 加载 UniXcoder 模型
print("正在加载 UniXcoder 模型...")
tokenizer = model_manager.get_unixcoder_tokenizer()
unixcoder_model = model_manager.get_unixcoder_model()
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("UniXcoder 模型加载完成\n")

# 加载 Jina 模型
print("正在加载 Jina 模型...")
jina1 = SentenceTransformer(
    'jinaai/jina-code-embeddings-0.5b',
    trust_remote_code=True
)
jina2 = SentenceTransformer(
    'jinaai/jina-embeddings-v2-base-code',
    trust_remote_code=True
)
print("Jina 模型加载完成\n")

# UniXcoder 的 embedding 函数
def get_unixcoder_embeddings(text_list):
    inputs = tokenizer(text_list, padding=True, truncation=True, max_length=512, return_tensors="pt").to(device)
    
    with torch.no_grad():
        outputs = unixcoder_model(**inputs)
        embeddings = outputs.last_hidden_state[:, 0, :]
        embeddings = torch.nn.functional.normalize(embeddings, p=2, dim=1)
        
    return embeddings

def calculate_unixcoder_similarity(nl, code):
    vec_nl = get_unixcoder_embeddings([nl])
    vec_code = get_unixcoder_embeddings([code])
    similarity = F.cosine_similarity(vec_nl, vec_code)
    return similarity.item()

# 测试数据 - 更难的事务管理场景
issue_text = "Implement a database transaction management system that supports ACID properties, provides methods to begin, commit, and rollback transactions, manages transaction savepoints, handles transaction isolation levels, and ensures data consistency across multiple database operations."

code1 = """
public class TransactionManager {
    private Connection connection;
    private boolean transactionActive;
    private List<Savepoint> savepoints;
    private int isolationLevel;
    
    public TransactionManager(Connection connection) {
        this.connection = connection;
        this.transactionActive = false;
        this.savepoints = new ArrayList<>();
        this.isolationLevel = Connection.TRANSACTION_READ_COMMITTED;
    }
    
    public void beginTransaction() throws SQLException {
        if (transactionActive) {
            throw new IllegalStateException("Transaction already active");
        }
        connection.setAutoCommit(false);
        connection.setTransactionIsolation(isolationLevel);
        transactionActive = true;
        savepoints.clear();
    }
    
    public void commit() throws SQLException {
        if (!transactionActive) {
            throw new IllegalStateException("No active transaction");
        }
        try {
            connection.commit();
            savepoints.clear();
        } catch (SQLException e) {
            connection.rollback();
            throw e;
        } finally {
            transactionActive = false;
            connection.setAutoCommit(true);
        }
    }
    
    public void rollback() throws SQLException {
        if (!transactionActive) {
            throw new IllegalStateException("No active transaction");
        }
        try {
            connection.rollback();
            savepoints.clear();
        } finally {
            transactionActive = false;
            connection.setAutoCommit(true);
        }
    }
    
    public void setSavepoint(String name) throws SQLException {
        if (!transactionActive) {
            throw new IllegalStateException("No active transaction");
        }
        Savepoint sp = connection.setSavepoint(name);
        savepoints.add(sp);
    }
    
    public void rollbackToSavepoint(String name) throws SQLException {
        if (!transactionActive) {
            throw new IllegalStateException("No active transaction");
        }
        Savepoint target = savepoints.stream()
            .filter(sp -> {
                try {
                    return sp.getSavepointName().equals(name);
                } catch (SQLException e) {
                    return false;
                }
            })
            .findFirst()
            .orElseThrow(() -> new IllegalArgumentException("Savepoint not found: " + name));
        
        connection.rollback(target);
        int index = savepoints.indexOf(target);
        savepoints.subList(index + 1, savepoints.size()).clear();
    }
    
    public void setIsolationLevel(int level) throws SQLException {
        if (transactionActive) {
            throw new IllegalStateException("Cannot change isolation level during transaction");
        }
        this.isolationLevel = level;
    }
    
    public boolean isTransactionActive() {
        return transactionActive;
    }
    
    public List<String> getSavepointNames() {
        return savepoints.stream()
            .map(sp -> {
                try {
                    return sp.getSavepointName();
                } catch (SQLException e) {
                    return null;
                }
            })
            .filter(Objects::nonNull)
            .collect(Collectors.toList());
    }
}
"""

code2 = """
public class ConnectionPoolManager {
    private DataSource dataSource;
    private Queue<PooledConnection> availableConnections;
    private Set<PooledConnection> activeConnections;
    private int maxPoolSize;
    private long connectionTimeout;
    
    public ConnectionPoolManager(DataSource dataSource, int maxPoolSize, long connectionTimeout) {
        this.dataSource = dataSource;
        this.maxPoolSize = maxPoolSize;
        this.connectionTimeout = connectionTimeout;
        this.availableConnections = new ConcurrentLinkedQueue<>();
        this.activeConnections = ConcurrentHashMap.newKeySet();
    }
    
    public Connection getConnection() throws SQLException {
        PooledConnection pooledConn = availableConnections.poll();
        
        if (pooledConn == null) {
            if (activeConnections.size() >= maxPoolSize) {
                throw new SQLException("Connection pool exhausted");
            }
            Connection conn = dataSource.getConnection();
            pooledConn = new PooledConnection(conn, System.currentTimeMillis());
        }
        
        if (isConnectionExpired(pooledConn)) {
            closeConnection(pooledConn);
            return getConnection();
        }
        
        activeConnections.add(pooledConn);
        return pooledConn.getConnection();
    }
    
    public void releaseConnection(Connection conn) {
        PooledConnection pooledConn = findPooledConnection(conn);
        if (pooledConn != null) {
            activeConnections.remove(pooledConn);
            pooledConn.setLastUsedTime(System.currentTimeMillis());
            availableConnections.offer(pooledConn);
        }
    }
    
    public void beginTransaction(Connection conn) throws SQLException {
        conn.setAutoCommit(false);
    }
    
    public void commitTransaction(Connection conn) throws SQLException {
        conn.commit();
        conn.setAutoCommit(true);
    }
    
    public void rollbackTransaction(Connection conn) throws SQLException {
        conn.rollback();
        conn.setAutoCommit(true);
    }
    
    private boolean isConnectionExpired(PooledConnection conn) {
        return System.currentTimeMillis() - conn.getLastUsedTime() > connectionTimeout;
    }
    
    private PooledConnection findPooledConnection(Connection conn) {
        return activeConnections.stream()
            .filter(pc -> pc.getConnection() == conn)
            .findFirst()
            .orElse(null);
    }
    
    private void closeConnection(PooledConnection conn) {
        try {
            conn.getConnection().close();
        } catch (SQLException e) {
            // Log error
        }
    }
    
    public int getActiveConnectionsCount() {
        return activeConnections.size();
    }
    
    public int getAvailableConnectionsCount() {
        return availableConnections.size();
    }
    
    private static class PooledConnection {
        private Connection connection;
        private long lastUsedTime;
        
        public PooledConnection(Connection connection, long lastUsedTime) {
            this.connection = connection;
            this.lastUsedTime = lastUsedTime;
        }
        
        public Connection getConnection() { return connection; }
        public long getLastUsedTime() { return lastUsedTime; }
        public void setLastUsedTime(long time) { this.lastUsedTime = time; }
    }
}
"""

code3 = """
public class MessageTransactionManager {
    private MessageProducer producer;
    private Session session;
    private boolean transactionActive;
    private List<Message> pendingMessages;
    private List<MessageAcknowledgement> pendingAcknowledgements;
    
    public MessageTransactionManager(Connection connection) throws JMSException {
        this.session = connection.createSession(true, Session.SESSION_TRANSACTED);
        this.producer = session.createProducer(null);
        this.transactionActive = false;
        this.pendingMessages = new ArrayList<>();
        this.pendingAcknowledgements = new ArrayList<>();
    }
    
    public void beginTransaction() throws JMSException {
        if (transactionActive) {
            throw new IllegalStateException("Transaction already active");
        }
        transactionActive = true;
        pendingMessages.clear();
        pendingAcknowledgements.clear();
    }
    
    public void sendMessage(Destination destination, Message message) throws JMSException {
        if (!transactionActive) {
            throw new IllegalStateException("No active transaction");
        }
        producer.send(destination, message);
        pendingMessages.add(message);
    }
    
    public void acknowledgeMessage(Message message) throws JMSException {
        if (!transactionActive) {
            throw new IllegalStateException("No active transaction");
        }
        message.acknowledge();
        pendingAcknowledgements.add(new MessageAcknowledgement(message, System.currentTimeMillis()));
    }
    
    public void commit() throws JMSException {
        if (!transactionActive) {
            throw new IllegalStateException("No active transaction");
        }
        try {
            session.commit();
            pendingMessages.clear();
            pendingAcknowledgements.clear();
        } catch (JMSException e) {
            session.rollback();
            throw e;
        } finally {
            transactionActive = false;
        }
    }
    
    public void rollback() throws JMSException {
        if (!transactionActive) {
            throw new IllegalStateException("No active transaction");
        }
        try {
            session.rollback();
            pendingMessages.clear();
            pendingAcknowledgements.clear();
        } finally {
            transactionActive = false;
        }
    }
    
    public void setTransactionTimeout(int seconds) throws JMSException {
        // Implementation depends on JMS provider
    }
    
    public boolean isTransactionActive() {
        return transactionActive;
    }
    
    public int getPendingMessageCount() {
        return pendingMessages.size();
    }
    
    public int getPendingAcknowledgementCount() {
        return pendingAcknowledgements.size();
    }
    
    public void close() throws JMSException {
        if (transactionActive) {
            rollback();
        }
        producer.close();
        session.close();
    }
    
    private static class MessageAcknowledgement {
        private Message message;
        private long timestamp;
        
        public MessageAcknowledgement(Message message, long timestamp) {
            this.message = message;
            this.timestamp = timestamp;
        }
        
        public Message getMessage() { return message; }
        public long getTimestamp() { return timestamp; }
    }
}
"""

code4 = """
public class CacheTransactionManager {
    private Cache<String, Object> cache;
    private Map<String, CacheEntry> transactionalCache;
    private Set<String> deletedKeys;
    private boolean transactionActive;
    
    public CacheTransactionManager(Cache<String, Object> cache) {
        this.cache = cache;
        this.transactionalCache = new ConcurrentHashMap<>();
        this.deletedKeys = ConcurrentHashMap.newKeySet();
        this.transactionActive = false;
    }
    
    public void beginTransaction() {
        if (transactionActive) {
            throw new IllegalStateException("Transaction already active");
        }
        transactionActive = true;
        transactionalCache.clear();
        deletedKeys.clear();
    }
    
    public void put(String key, Object value) {
        if (!transactionActive) {
            throw new IllegalStateException("No active transaction");
        }
        transactionalCache.put(key, new CacheEntry(value, System.currentTimeMillis()));
        deletedKeys.remove(key);
    }
    
    public Object get(String key) {
        if (!transactionActive) {
            throw new IllegalStateException("No active transaction");
        }
        if (deletedKeys.contains(key)) {
            return null;
        }
        CacheEntry entry = transactionalCache.get(key);
        if (entry != null) {
            return entry.getValue();
        }
        return cache.get(key);
    }
    
    public void remove(String key) {
        if (!transactionActive) {
            throw new IllegalStateException("No active transaction");
        }
        deletedKeys.add(key);
        transactionalCache.remove(key);
    }
    
    public boolean containsKey(String key) {
        if (!transactionActive) {
            throw new IllegalStateException("No active transaction");
        }
        if (deletedKeys.contains(key)) {
            return false;
        }
        if (transactionalCache.containsKey(key)) {
            return true;
        }
        return cache.containsKey(key);
    }
    
    public void commit() {
        if (!transactionActive) {
            throw new IllegalStateException("No active transaction");
        }
        try {
            for (String key : deletedKeys) {
                cache.remove(key);
            }
            for (Map.Entry<String, CacheEntry> entry : transactionalCache.entrySet()) {
                cache.put(entry.getKey(), entry.getValue().getValue());
            }
            transactionalCache.clear();
            deletedKeys.clear();
        } finally {
            transactionActive = false;
        }
    }
    
    public void rollback() {
        if (!transactionActive) {
            throw new IllegalStateException("No active transaction");
        }
        transactionalCache.clear();
        deletedKeys.clear();
        transactionActive = false;
    }
    
    public void setSavepoint(String name) {
        // Savepoint implementation
    }
    
    public void rollbackToSavepoint(String name) {
        // Rollback to savepoint implementation
    }
    
    public boolean isTransactionActive() {
        return transactionActive;
    }
    
    public int getModifiedCount() {
        return transactionalCache.size() + deletedKeys.size();
    }
    
    private static class CacheEntry {
        private Object value;
        private long timestamp;
        
        public CacheEntry(Object value, long timestamp) {
            this.value = value;
            this.timestamp = timestamp;
        }
        
        public Object getValue() { return value; }
        public long getTimestamp() { return timestamp; }
    }
}
"""

code5 = """
public class FileTransactionManager {
    private Path baseDirectory;
    private Map<Path, FileOperation> pendingOperations;
    private List<Path> backupFiles;
    private boolean transactionActive;
    
    public FileTransactionManager(Path baseDirectory) {
        this.baseDirectory = baseDirectory;
        this.pendingOperations = new LinkedHashMap<>();
        this.backupFiles = new ArrayList<>();
        this.transactionActive = false;
    }
    
    public void beginTransaction() throws IOException {
        if (transactionActive) {
            throw new IllegalStateException("Transaction already active");
        }
        if (!Files.exists(baseDirectory)) {
            Files.createDirectories(baseDirectory);
        }
        transactionActive = true;
        pendingOperations.clear();
        backupFiles.clear();
    }
    
    public void writeFile(Path relativePath, String content) throws IOException {
        if (!transactionActive) {
            throw new IllegalStateException("No active transaction");
        }
        Path fullPath = baseDirectory.resolve(relativePath);
        createBackupIfNeeded(fullPath);
        pendingOperations.put(relativePath, new WriteOperation(fullPath, content));
    }
    
    public void deleteFile(Path relativePath) throws IOException {
        if (!transactionActive) {
            throw new IllegalStateException("No active transaction");
        }
        Path fullPath = baseDirectory.resolve(relativePath);
        createBackupIfNeeded(fullPath);
        pendingOperations.put(relativePath, new DeleteOperation(fullPath));
    }
    
    public void moveFile(Path sourcePath, Path targetPath) throws IOException {
        if (!transactionActive) {
            throw new IllegalStateException("No active transaction");
        }
        Path fullSource = baseDirectory.resolve(sourcePath);
        Path fullTarget = baseDirectory.resolve(targetPath);
        createBackupIfNeeded(fullSource);
        createBackupIfNeeded(fullTarget);
        pendingOperations.put(sourcePath, new MoveOperation(fullSource, fullTarget));
    }
    
    public void commit() throws IOException {
        if (!transactionActive) {
            throw new IllegalStateException("No active transaction");
        }
        try {
            for (FileOperation op : pendingOperations.values()) {
                op.execute();
            }
            cleanupBackups();
            pendingOperations.clear();
        } catch (IOException e) {
            rollback();
            throw e;
        } finally {
            transactionActive = false;
        }
    }
    
    public void rollback() throws IOException {
        if (!transactionActive) {
            throw new IllegalStateException("No active transaction");
        }
        try {
            restoreBackups();
        } finally {
            cleanupBackups();
            pendingOperations.clear();
            transactionActive = false;
        }
    }
    
    private void createBackupIfNeeded(Path path) throws IOException {
        if (Files.exists(path)) {
            Path backupPath = Paths.get(path.toString() + ".bak." + System.currentTimeMillis());
            Files.copy(path, backupPath);
            backupFiles.add(backupPath);
        }
    }
    
    private void restoreBackups() throws IOException {
        for (Path backup : backupFiles) {
            String originalPath = backup.toString().replaceAll("\\.bak\\.\\d+$", "");
            Path original = Paths.get(originalPath);
            if (Files.exists(backup)) {
                Files.move(backup, original, StandardCopyOption.REPLACE_EXISTING);
            }
        }
    }
    
    private void cleanupBackups() {
        for (Path backup : backupFiles) {
            try {
                Files.deleteIfExists(backup);
            } catch (IOException e) {
                // Log error
            }
        }
        backupFiles.clear();
    }
    
    public boolean isTransactionActive() {
        return transactionActive;
    }
    
    public int getPendingOperationsCount() {
        return pendingOperations.size();
    }
    
    private interface FileOperation {
        void execute() throws IOException;
    }
    
    private static class WriteOperation implements FileOperation {
        private Path path;
        private String content;
        
        public WriteOperation(Path path, String content) {
            this.path = path;
            this.content = content;
        }
        
        public void execute() throws IOException {
            Files.write(path, content.getBytes());
        }
    }
    
    private static class DeleteOperation implements FileOperation {
        private Path path;
        
        public DeleteOperation(Path path) {
            this.path = path;
        }
        
        public void execute() throws IOException {
            Files.deleteIfExists(path);
        }
    }
    
    private static class MoveOperation implements FileOperation {
        private Path source;
        private Path target;
        
        public MoveOperation(Path source, Path target) {
            this.source = source;
            this.target = target;
        }
        
        public void execute() throws IOException {
            Files.move(source, target, StandardCopyOption.REPLACE_EXISTING);
        }
    }
}
"""

code6 = """
public class NetworkTransactionManager {
    private Socket socket;
    private ObjectInputStream input;
    private ObjectOutputStream output;
    private boolean transactionActive;
    private List<NetworkRequest> pendingRequests;
    private int transactionTimeout;
    
    public NetworkTransactionManager(Socket socket, int transactionTimeout) throws IOException {
        this.socket = socket;
        this.output = new ObjectOutputStream(socket.getOutputStream());
        this.input = new ObjectInputStream(socket.getInputStream());
        this.transactionTimeout = transactionTimeout;
        this.transactionActive = false;
        this.pendingRequests = new ArrayList<>();
    }
    
    public void beginTransaction() throws IOException {
        if (transactionActive) {
            throw new IllegalStateException("Transaction already active");
        }
        sendCommand(new BeginTransactionCommand(transactionTimeout));
        TransactionResponse response = (TransactionResponse) receiveResponse();
        if (!response.isSuccess()) {
            throw new IOException("Failed to begin transaction: " + response.getErrorMessage());
        }
        transactionActive = true;
        pendingRequests.clear();
    }
    
    public void sendRequest(NetworkRequest request) throws IOException {
        if (!transactionActive) {
            throw new IllegalStateException("No active transaction");
        }
        sendCommand(request);
        RequestResponse response = (RequestResponse) receiveResponse();
        if (!response.isAccepted()) {
            throw new IOException("Request rejected: " + response.getRejectionReason());
        }
        pendingRequests.add(request);
    }
    
    public void commit() throws IOException {
        if (!transactionActive) {
            throw new IllegalStateException("No active transaction");
        }
        try {
            sendCommand(new CommitCommand());
            CommitResponse response = (CommitResponse) receiveResponse();
            if (!response.isSuccess()) {
                throw new IOException("Commit failed: " + response.getErrorMessage());
            }
            pendingRequests.clear();
        } catch (IOException e) {
            rollback();
            throw e;
        } finally {
            transactionActive = false;
        }
    }
    
    public void rollback() throws IOException {
        if (!transactionActive) {
            throw new IllegalStateException("No active transaction");
        }
        try {
            sendCommand(new RollbackCommand());
            RollbackResponse response = (RollbackResponse) receiveResponse();
            if (!response.isSuccess()) {
                // Log but don't throw, we're already rolling back
            }
            pendingRequests.clear();
        } finally {
            transactionActive = false;
        }
    }
    
    public void setSavepoint(String name) throws IOException {
        if (!transactionActive) {
            throw new IllegalStateException("No active transaction");
        }
        sendCommand(new SetSavepointCommand(name));
        SavepointResponse response = (SavepointResponse) receiveResponse();
        if (!response.isSuccess()) {
            throw new IOException("Failed to set savepoint: " + response.getErrorMessage());
        }
    }
    
    public void rollbackToSavepoint(String name) throws IOException {
        if (!transactionActive) {
            throw new IllegalStateException("No active transaction");
        }
        sendCommand(new RollbackToSavepointCommand(name));
        RollbackSavepointResponse response = (RollbackSavepointResponse) receiveResponse();
        if (!response.isSuccess()) {
            throw new IOException("Failed to rollback to savepoint: " + response.getErrorMessage());
        }
    }
    
    private void sendCommand(Object command) throws IOException {
        output.writeObject(command);
        output.flush();
    }
    
    private Object receiveResponse() throws IOException {
        try {
            socket.setSoTimeout(transactionTimeout * 1000);
            return input.readObject();
        } catch (ClassNotFoundException e) {
            throw new IOException("Invalid response type", e);
        } finally {
            socket.setSoTimeout(0);
        }
    }
    
    public boolean isTransactionActive() {
        return transactionActive;
    }
    
    public int getPendingRequestCount() {
        return pendingRequests.size();
    }
    
    public void close() throws IOException {
        if (transactionActive) {
            rollback();
        }
        input.close();
        output.close();
        socket.close();
    }
}
"""

codes = [code1, code2, code3, code4, code5, code6]
code_names = [
    "1. 数据库事务管理 (真正相关)",
    "2. 连接池管理 (容易混淆)",
    "3. 消息事务管理 (容易混淆)",
    "4. 缓存事务管理 (容易混淆)",
    "5. 文件事务管理 (容易混淆)",
    "6. 网络事务管理 (容易混淆)"
]

# 计算三个模型的相似度
print("正在计算相似度...\n")
unixcoder_scores = []
jina1_scores = []
jina2_scores = []

for code in codes:
    # UniXcoder
    unixcoder_scores.append(calculate_unixcoder_similarity(issue_text, code))

# Jina 模型批量处理
data = [issue_text] + codes
embeddings1 = jina1.encode(data)
embeddings2 = jina2.encode(data)

issue_emb1 = embeddings1[0:1]
code_embs1 = embeddings1[1:]
jina1_scores = cosine_similarity(issue_emb1, code_embs1)[0]

issue_emb2 = embeddings2[0:1]
code_embs2 = embeddings2[1:]
jina2_scores = cosine_similarity(issue_emb2, code_embs2)[0]

# 输出对比结果
print("=" * 100)
print("数据库事务管理 - 极其容易混淆场景 - 三个模型对比测试:")
print("=" * 100)
print(f"{'代码片段':<30} {'UniXcoder':<15} {'jina-code-0.5b':<20} {'jina-embeddings-v2':<20}")
print("-" * 100)
for i in range(6):
    print(f"{code_names[i]:<30} {unixcoder_scores[i]:<15.4f} {jina1_scores[i]:<20.4f} {jina2_scores[i]:<20.4f}")
print("=" * 100)
print("\n分析:")
print("- 只有第一个是真正的数据库事务管理代码")
print("- 其他代码都极其容易混淆（都有begin/commit/rollback、savepoint等术语）")
print("- 但分别是：连接池、消息队列、缓存、文件系统、网络的事务管理")
print("- 测试模型在术语高度相似但领域完全不同的场景下的区分能力")
print("\n模型说明:")
print("- UniXcoder: Microsoft的代码-文本统一表示模型")
print("- jina-code-0.5b: Jina的专门代码嵌入模型")
print("- jina-embeddings-v2: Jina的通用代码嵌入模型")
