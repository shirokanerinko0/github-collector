from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

model1 = SentenceTransformer(
    'jinaai/jina-code-embeddings-0.5b',
    trust_remote_code=True
)
model2 = SentenceTransformer(
    'jinaai/jina-embeddings-v2-base-code',
    trust_remote_code=True
)

issue_text = "Implement a database connection pool management system that efficiently manages database connections. The pool should support configurable minimum and maximum connections, connection validation, idle connection cleanup, and proper resource release. It should ensure thread safety and prevent connection leaks."

code1 = """
public class DatabaseConnectionPool {
    
    private DataSource dataSource;
    private int maxPoolSize;
    private int minPoolSize;
    private long maxIdleTime;
    private long validationTimeout;
    
    private List<PooledConnection> availableConnections;
    private List<PooledConnection> inUseConnections;
    private ReentrantLock lock = new ReentrantLock();
    private Condition connectionAvailable = lock.newCondition();
    
    public DatabaseConnectionPool(DataSource dataSource, int minPoolSize, int maxPoolSize, long maxIdleTime) {
        this.dataSource = dataSource;
        this.minPoolSize = minPoolSize;
        this.maxPoolSize = maxPoolSize;
        this.maxIdleTime = maxIdleTime;
        this.availableConnections = new ArrayList<>();
        this.inUseConnections = new ArrayList<>();
        initializePool();
        startIdleConnectionCleaner();
    }
    
    private void initializePool() {
        try {
            for (int i = 0; i < minPoolSize; i++) {
                availableConnections.add(createNewConnection());
            }
        } catch (SQLException e) {
            throw new RuntimeException("Failed to initialize connection pool", e);
        }
    }
    
    private PooledConnection createNewConnection() throws SQLException {
        Connection connection = dataSource.getConnection();
        return new PooledConnection(connection, System.currentTimeMillis());
    }
    
    public Connection getConnection() throws SQLException {
        lock.lock();
        try {
            while (availableConnections.isEmpty() && inUseConnections.size() >= maxPoolSize) {
                try {
                    connectionAvailable.await(validationTimeout, TimeUnit.MILLISECONDS);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                    throw new SQLException("Interrupted while waiting for connection", e);
                }
            }
            
            if (!availableConnections.isEmpty()) {
                PooledConnection pooledConn = availableConnections.remove(availableConnections.size() - 1);
                if (isConnectionValid(pooledConn.getConnection())) {
                    pooledConn.setLastUsedTime(System.currentTimeMillis());
                    inUseConnections.add(pooledConn);
                    return pooledConn.getConnection();
                } else {
                    closeConnection(pooledConn);
                }
            }
            
            PooledConnection newConn = createNewConnection();
            inUseConnections.add(newConn);
            return newConn.getConnection();
        } finally {
            lock.unlock();
        }
    }
    
    public void releaseConnection(Connection connection) {
        lock.lock();
        try {
            Iterator<PooledConnection> iterator = inUseConnections.iterator();
            while (iterator.hasNext()) {
                PooledConnection pooledConn = iterator.next();
                if (pooledConn.getConnection() == connection) {
                    iterator.remove();
                    pooledConn.setLastUsedTime(System.currentTimeMillis());
                    availableConnections.add(pooledConn);
                    connectionAvailable.signal();
                    return;
                }
            }
        } finally {
            lock.unlock();
        }
    }
    
    private boolean isConnectionValid(Connection connection) {
        try {
            return connection != null && !connection.isClosed() && connection.isValid(5);
        } catch (SQLException e) {
            return false;
        }
    }
    
    private void closeConnection(PooledConnection pooledConn) {
        try {
            if (pooledConn.getConnection() != null && !pooledConn.getConnection().isClosed()) {
                pooledConn.getConnection().close();
            }
        } catch (SQLException e) {
            e.printStackTrace();
        }
    }
    
    private void startIdleConnectionCleaner() {
        Thread cleanerThread = new Thread(() -> {
            while (true) {
                try {
                    Thread.sleep(maxIdleTime / 2);
                    cleanupIdleConnections();
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                    break;
                }
            }
        });
        cleanerThread.setDaemon(true);
        cleanerThread.start();
    }
    
    private void cleanupIdleConnections() {
        lock.lock();
        try {
            long now = System.currentTimeMillis();
            Iterator<PooledConnection> iterator = availableConnections.iterator();
            while (iterator.hasNext()) {
                PooledConnection pooledConn = iterator.next();
                if (availableConnections.size() > minPoolSize && 
                    (now - pooledConn.getLastUsedTime()) > maxIdleTime) {
                    closeConnection(pooledConn);
                    iterator.remove();
                }
            }
        } finally {
            lock.unlock();
        }
    }
    
    public void shutdown() {
        lock.lock();
        try {
            for (PooledConnection conn : availableConnections) {
                closeConnection(conn);
            }
            for (PooledConnection conn : inUseConnections) {
                closeConnection(conn);
            }
            availableConnections.clear();
            inUseConnections.clear();
        } finally {
            lock.unlock();
        }
    }
    
    private static class PooledConnection {
        private Connection connection;
        private long lastUsedTime;
        
        public PooledConnection(Connection connection, long lastUsedTime) {
            this.connection = connection;
            this.lastUsedTime = lastUsedTime;
        }
        
        public Connection getConnection() {
            return connection;
        }
        
        public long getLastUsedTime() {
            return lastUsedTime;
        }
        
        public void setLastUsedTime(long lastUsedTime) {
            this.lastUsedTime = lastUsedTime;
        }
    }
}
"""

code2 = """
public class SimpleConnectionManager {
    
    private String jdbcUrl;
    private String username;
    private String password;
    private int maxConnections;
    
    private List<Connection> availableConnections;
    private List<Connection> usedConnections;
    private Object lock = new Object();
    
    public SimpleConnectionManager(String jdbcUrl, String username, String password, int maxConnections) {
        this.jdbcUrl = jdbcUrl;
        this.username = username;
        this.password = password;
        this.maxConnections = maxConnections;
        this.availableConnections = new ArrayList<>();
        this.usedConnections = new ArrayList<>();
    }
    
    public Connection getConnection() throws SQLException {
        synchronized (lock) {
            if (!availableConnections.isEmpty()) {
                Connection conn = availableConnections.remove(availableConnections.size() - 1);
                if (isValid(conn)) {
                    usedConnections.add(conn);
                    return conn;
                }
            }
            
            if (usedConnections.size() < maxConnections) {
                Connection conn = createConnection();
                usedConnections.add(conn);
                return conn;
            }
            
            throw new SQLException("No available connections in pool");
        }
    }
    
    public void releaseConnection(Connection conn) {
        synchronized (lock) {
            usedConnections.remove(conn);
            if (isValid(conn)) {
                availableConnections.add(conn);
            }
        }
    }
    
    private Connection createConnection() throws SQLException {
        return DriverManager.getConnection(jdbcUrl, username, password);
    }
    
    private boolean isValid(Connection conn) {
        try {
            return conn != null && !conn.isClosed();
        } catch (SQLException e) {
            return false;
        }
    }
    
    public void closeAll() {
        synchronized (lock) {
            closeConnections(availableConnections);
            closeConnections(usedConnections);
        }
    }
    
    private void closeConnections(List<Connection> connections) {
        for (Connection conn : connections) {
            try {
                if (conn != null && !conn.isClosed()) {
                    conn.close();
                }
            } catch (SQLException e) {
                e.printStackTrace();
            }
        }
        connections.clear();
    }
}
"""

code3 = """
public class ThreadPoolExecutor {
    
    private int corePoolSize;
    private int maximumPoolSize;
    private long keepAliveTime;
    private BlockingQueue<Runnable> workQueue;
    
    private List<WorkerThread> workerThreads;
    private ReentrantLock mainLock = new ReentrantLock();
    private volatile boolean isShutdown = false;
    
    public ThreadPoolExecutor(int corePoolSize, int maximumPoolSize, long keepAliveTime, BlockingQueue<Runnable> workQueue) {
        this.corePoolSize = corePoolSize;
        this.maximumPoolSize = maximumPoolSize;
        this.keepAliveTime = keepAliveTime;
        this.workQueue = workQueue;
        this.workerThreads = new ArrayList<>();
        
        for (int i = 0; i < corePoolSize; i++) {
            addWorker();
        }
    }
    
    private void addWorker() {
        WorkerThread worker = new WorkerThread();
        workerThreads.add(worker);
        worker.start();
    }
    
    public void execute(Runnable task) {
        if (isShutdown) {
            throw new IllegalStateException("Executor is shutdown");
        }
        
        mainLock.lock();
        try {
            if (workerThreads.size() < maximumPoolSize) {
                addWorker();
            }
            workQueue.offer(task);
        } finally {
            mainLock.unlock();
        }
    }
    
    public void shutdown() {
        isShutdown = true;
        for (WorkerThread worker : workerThreads) {
            worker.interrupt();
        }
    }
    
    private class WorkerThread extends Thread {
        @Override
        public void run() {
            while (!isShutdown || !workQueue.isEmpty()) {
                try {
                    Runnable task = workQueue.poll(keepAliveTime, TimeUnit.MILLISECONDS);
                    if (task != null) {
                        task.run();
                    } else {
                        mainLock.lock();
                        try {
                            if (workerThreads.size() > corePoolSize) {
                                workerThreads.remove(this);
                                break;
                            }
                        } finally {
                            mainLock.unlock();
                        }
                    }
                } catch (InterruptedException e) {
                    if (isShutdown) break;
                }
            }
        }
    }
}
"""

code4 = """
public class ObjectPool<T> {
    
    private int maxSize;
    private int minSize;
    private List<T> availableObjects;
    private List<T> inUseObjects;
    private ObjectFactory<T> factory;
    private ReentrantLock lock = new ReentrantLock();
    
    public ObjectPool(ObjectFactory<T> factory, int minSize, int maxSize) {
        this.factory = factory;
        this.minSize = minSize;
        this.maxSize = maxSize;
        this.availableObjects = new ArrayList<>();
        this.inUseObjects = new ArrayList<>();
        
        for (int i = 0; i < minSize; i++) {
            availableObjects.add(factory.create());
        }
    }
    
    public T acquire() {
        lock.lock();
        try {
            if (!availableObjects.isEmpty()) {
                T obj = availableObjects.remove(availableObjects.size() - 1);
                if (factory.validate(obj)) {
                    inUseObjects.add(obj);
                    return obj;
                } else {
                    factory.destroy(obj);
                }
            }
            
            if (inUseObjects.size() < maxSize) {
                T obj = factory.create();
                inUseObjects.add(obj);
                return obj;
            }
            
            throw new PoolExhaustedException("Pool is exhausted");
        } finally {
            lock.unlock();
        }
    }
    
    public void release(T obj) {
        lock.lock();
        try {
            inUseObjects.remove(obj);
            if (factory.validate(obj)) {
                availableObjects.add(obj);
            } else {
                factory.destroy(obj);
            }
        } finally {
            lock.unlock();
        }
    }
    
    public void cleanup() {
        lock.lock();
        try {
            Iterator<T> iterator = availableObjects.iterator();
            while (iterator.hasNext() && availableObjects.size() > minSize) {
                T obj = iterator.next();
                factory.destroy(obj);
                iterator.remove();
            }
        } finally {
            lock.unlock();
        }
    }
    
    public interface ObjectFactory<T> {
        T create();
        boolean validate(T obj);
        void destroy(T obj);
    }
    
    public static class PoolExhaustedException extends RuntimeException {
        public PoolExhaustedException(String message) {
            super(message);
        }
    }
}
"""

code5 = """
public class FileResourceManager {
    
    private String basePath;
    private int maxOpenFiles;
    private List<FileHandle> availableHandles;
    private List<FileHandle> inUseHandles;
    private ReentrantLock lock = new ReentrantLock();
    
    public FileResourceManager(String basePath, int maxOpenFiles) {
        this.basePath = basePath;
        this.maxOpenFiles = maxOpenFiles;
        this.availableHandles = new ArrayList<>();
        this.inUseHandles = new ArrayList<>();
    }
    
    public FileHandle openFile(String filename, String mode) throws IOException {
        lock.lock();
        try {
            if (!availableHandles.isEmpty()) {
                for (Iterator<FileHandle> it = availableHandles.iterator(); it.hasNext(); ) {
                    FileHandle handle = it.next();
                    if (handle.getFilename().equals(filename)) {
                        it.remove();
                        inUseHandles.add(handle);
                        return handle;
                    }
                }
            }
            
            if (inUseHandles.size() < maxOpenFiles) {
                FileHandle handle = new FileHandle(filename, new File(basePath, filename), mode);
                inUseHandles.add(handle);
                return handle;
            }
            
            throw new IOException("Too many open files");
        } finally {
            lock.unlock();
        }
    }
    
    public void closeFile(FileHandle handle) {
        lock.lock();
        try {
            inUseHandles.remove(handle);
            if (availableHandles.size() < maxOpenFiles / 2) {
                availableHandles.add(handle);
            } else {
                try {
                    handle.getFileChannel().close();
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
        } finally {
            lock.unlock();
        }
    }
    
    public void closeAll() {
        lock.lock();
        try {
            for (FileHandle handle : availableHandles) {
                try {
                    handle.getFileChannel().close();
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
            for (FileHandle handle : inUseHandles) {
                try {
                    handle.getFileChannel().close();
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
            availableHandles.clear();
            inUseHandles.clear();
        } finally {
            lock.unlock();
        }
    }
    
    public static class FileHandle {
        private String filename;
        private File file;
        private FileChannel fileChannel;
        private String mode;
        
        public FileHandle(String filename, File file, String mode) throws IOException {
            this.filename = filename;
            this.file = file;
            this.mode = mode;
            RandomAccessFile raf = new RandomAccessFile(file, mode);
            this.fileChannel = raf.getChannel();
        }
        
        public String getFilename() { return filename; }
        public File getFile() { return file; }
        public FileChannel getFileChannel() { return fileChannel; }
    }
}
"""

code6 = """
public class MemoryCacheManager {
    
    private int maxEntries;
    private Map<String, CacheEntry> cache;
    private LinkedList<String> accessOrder;
    private ReentrantLock lock = new ReentrantLock();
    
    public MemoryCacheManager(int maxEntries) {
        this.maxEntries = maxEntries;
        this.cache = new HashMap<>();
        this.accessOrder = new LinkedList<>();
    }
    
    public void put(String key, Object value, long ttlMs) {
        lock.lock();
        try {
            if (cache.containsKey(key)) {
                accessOrder.remove(key);
            }
            
            if (cache.size() >= maxEntries && !cache.containsKey(key)) {
                String oldestKey = accessOrder.removeFirst();
                cache.remove(oldestKey);
            }
            
            CacheEntry entry = new CacheEntry(value, System.currentTimeMillis() + ttlMs);
            cache.put(key, entry);
            accessOrder.addLast(key);
        } finally {
            lock.unlock();
        }
    }
    
    public Object get(String key) {
        lock.lock();
        try {
            CacheEntry entry = cache.get(key);
            if (entry == null) {
                return null;
            }
            
            if (System.currentTimeMillis() > entry.getExpirationTime()) {
                cache.remove(key);
                accessOrder.remove(key);
                return null;
            }
            
            accessOrder.remove(key);
            accessOrder.addLast(key);
            return entry.getValue();
        } finally {
            lock.unlock();
        }
    }
    
    public void remove(String key) {
        lock.lock();
        try {
            cache.remove(key);
            accessOrder.remove(key);
        } finally {
            lock.unlock();
        }
    }
    
    public void clear() {
        lock.lock();
        try {
            cache.clear();
            accessOrder.clear();
        } finally {
            lock.unlock();
        }
    }
    
    public void cleanupExpired() {
        lock.lock();
        try {
            long now = System.currentTimeMillis();
            Iterator<Map.Entry<String, CacheEntry>> iterator = cache.entrySet().iterator();
            while (iterator.hasNext()) {
                Map.Entry<String, CacheEntry> entry = iterator.next();
                if (now > entry.getValue().getExpirationTime()) {
                    iterator.remove();
                    accessOrder.remove(entry.getKey());
                }
            }
        } finally {
            lock.unlock();
        }
    }
    
    private static class CacheEntry {
        private Object value;
        private long expirationTime;
        
        public CacheEntry(Object value, long expirationTime) {
            this.value = value;
            this.expirationTime = expirationTime;
        }
        
        public Object getValue() {
            return value;
        }
        
        public long getExpirationTime() {
            return expirationTime;
        }
    }
}
"""

data = [issue_text, code1, code2, code3, code4, code5, code6]

embeddings1 = model1.encode(data)
embeddings2 = model2.encode(data)

issue_embedding1 = embeddings1[0:1]
code_embeddings1 = embeddings1[1:]
similarities1 = cosine_similarity(issue_embedding1, code_embeddings1)

issue_embedding2 = embeddings2[0:1]
code_embeddings2 = embeddings2[1:]
similarities2 = cosine_similarity(issue_embedding2, code_embeddings2)

print("=" * 80)
print("数据库连接池相关 - 两个模型对比测试:")
print("=" * 80)
print(f"{'代码片段':<40} {'jina-code-0.5b':<20} {'jina-embeddings-v2':<20}")
print("-" * 80)
print(f"{'1. 数据库连接池':<40} {similarities1[0][0]:<20.4f} {similarities2[0][0]:<20.4f}")
print(f"{'2. 简单连接管理器':<40} {similarities1[0][1]:<20.4f} {similarities2[0][1]:<20.4f}")
print(f"{'3. 线程池执行器':<40} {similarities1[0][2]:<20.4f} {similarities2[0][2]:<20.4f}")
print(f"{'4. 对象池':<40} {similarities1[0][3]:<20.4f} {similarities2[0][3]:<20.4f}")
print(f"{'5. 文件资源管理器':<40} {similarities1[0][4]:<20.4f} {similarities2[0][4]:<20.4f}")
print(f"{'6. 内存缓存管理器':<40} {similarities1[0][5]:<20.4f} {similarities2[0][5]:<20.4f}")
print("=" * 80)
print("\n分析:")
print("- 前两个是真正的数据库连接池相关代码")
print("- 后四个容易混淆（线程池、对象池、文件管理、缓存）")
print("- 它们都有\"池\"的概念，但用途不同")
print("\n模型对比:")
print("- jina-code-embeddings-0.5b: 专门为代码设计的模型")
print("- jina-embeddings-v2-base-code: 通用代码嵌入模型")
