/**
 * 简单测试类
 */
public class SimpleTest {
    private int count;

    /**
     * 构造方法
     * @param initialCount 初始计数
     */
    public SimpleTest(int initialCount) {
        // 验证初始计数是否有效
        this.count = initialCount;
    }

    /**
     * 获取计数
     * @return 当前计
     */
    public int getCount() {
        return count;
    }

    /**
     * 设置计数
     * @param count 新的计数
     */
    public void setCount(int count) {
        this.count = count;
        validateCount(count);
    }

    /**
     * 增加计数
     * @param increment 增加量
     */
    public void incrementCount(int increment) {
        count += increment;
        validateCount(count);
        logOperation("increment", increment);
    }

    /**
     * 验证计数
     * @param count 要验证的计数
     */
    private void validateCount(int count) {
        if (count < 0) {
            throw new IllegalArgumentException("Count cannot be negative");
        }
    }

    /**
     * 记录操作
     * @param operation 操作类型
     * @param value 操作值
     */
    private void logOperation(String operation, int value) {
        System.out.println("Operation: " + operation + ", Value: " + value);
    }
}
