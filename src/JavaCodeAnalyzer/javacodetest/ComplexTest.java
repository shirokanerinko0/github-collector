/**
 * 复杂测试类
 */
public class ComplexTest {
    private String[] names;
    private static final int MAX_SIZE = 100;

    /**
     * 构造方法
     * @param size 数组大小
     */
    public ComplexTest(int size) {
        if (size > MAX_SIZE) {
            size = MAX_SIZE;
        }
        names = new String[size];
    }

    /**
     * 添加名称
     * @param index 索引
     * @param name 名称
     * @return 是否添加成功
     */
    public boolean addName(int index, String name) {
        if (validateIndex(index) && validateName(name)) {
            names[index] = name;
            logOperation("add", name);
            return true;
        }
        return false;
    }

    /**
     * 获取名称
     * @param index 索引
     * @return 名称
     */
    public String getName(int index) {
        if (validateIndex(index)) {
            return names[index];
        }
        return null;
    }

    /**
     * 验证索引
     * @param index 索引
     * @return 是否有效
     */
    private boolean validateIndex(int index) {
        return index >= 0 && index < names.length;
    }

    /**
     * 验证名称
     * @param name 名称
     * @return 是否有效
     */
    private boolean validateName(String name) {
        return name != null && !name.isEmpty();
    }

    /**
     * 记录操作
     * @param operation 操作类型
     * @param detail 详细信息
     */
    private void logOperation(String operation, String detail) {
        System.out.println("Operation: " + operation + ", Detail: " + detail);
    }

    /**
     * 静态方法：获取最大值
     * @param numbers 数字数组
     * @return 最大值
     */
    public static int getMaxValue(int[] numbers) {
        if (numbers == null || numbers.length == 0) {
            throw new IllegalArgumentException("Numbers array cannot be empty");
        }
        int max = numbers[0];
        for (int num : numbers) {
            if (num > max) {
                max = num;
            }
        }
        return max;
    }

    /**
     * 获取数组大小
     * @return 数组大小
     */
    public int getSize() {
        return names.length;
    }

    /**
     * 清空数组
     */
    public void clear() {
        for (int i = 0; i < names.length; i++) {
            names[i] = null;
        }
        logOperation("clear", "all");
    }
}
