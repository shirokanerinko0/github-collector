/**
 * 测试接口
 */
interface TestInterface {
    /**
     * 执行操作
     * @param value 操作值
     * @return 操作结果
     */
    int execute(int value);

    /**
     * 获取状态
     * @return 状态
     */
    String getStatus();
}

/**
 * 接口实现类
 */
class InterfaceImpl implements TestInterface {
    private int count;
    private String status;

    /**
     * 构造方法
     */
    public InterfaceImpl() {
        this.count = 0;
        this.status = "INITIALIZED";
    }

    /**
     * 执行操作
     * @param value 操作值
     * @return 操作结果
     */
    @Override
    public int execute(int value) {
        int result = processValue(value);
        updateStatus("EXECUTED");
        logOperation("execute", value, result);
        return result;
    }

    /**
     * 获取状态
     * @return 状态
     */
    @Override
    public String getStatus() {
        return status;
    }

    /**
     * 处理值
     * @param value 输入值
     * @return 处理结果
     */
    private int processValue(int value) {
        count += value;
        validateCount(count);
        return count;
    }

    /**
     * 验证计数
     * @param count 计数
     */
    private void validateCount(int count) {
        if (count < 0) {
            throw new IllegalStateException("Count cannot be negative");
        }
    }

    /**
     * 更新状态
     * @param newStatus 新状态
     */
    private void updateStatus(String newStatus) {
        this.status = newStatus;
    }

    /**
     * 记录操作
     * @param operation 操作类型
     * @param input 输入值
     * @param output 输出值
     */
    private void logOperation(String operation, int input, int output) {
        System.out.println("Operation: " + operation + ", Input: " + input + ", Output: " + output);
    }
}

/**
 * 测试主类
 */
public class InterfaceTest {
    /**
     * 主方法
     * @param args 命令行参数
     */
    public static void main(String[] args) {
        TestInterface test = new InterfaceImpl();
        int result1 = test.execute(5);
        int result2 = test.execute(10);
        System.out.println("Final result: " + result2);
        System.out.println("Status: " + test.getStatus());
    }
}
