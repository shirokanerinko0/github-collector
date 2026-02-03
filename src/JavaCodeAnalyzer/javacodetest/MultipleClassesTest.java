public class MultipleClassesTest {
    private String name;
    private int value;
    
    /**
     * 构造方法
     * @param name 名称
     * @param value 值
     */
    public MultipleClassesTest(String name, int value) {
        this.name = name;
        this.value = value;
    }
    
    /**
     * 获取名称
     * @return 名称
     */
    public String getName() {
        return name;
    }
    
    /**
     * 设置值
     * @param value 新值
     */
    public void setValue(int value) {
        this.value = value;
    }
    
    /**
     * 执行操作
     * @param factor 因子
     * @return 操作结果
     */
    public int executeOperation(int factor) {
        return value * factor;
    }
}

class HelperClass {
    /**
     * 辅助方法：计算最大值
     * @param a 第一个值
     * @param b 第二个值
     * @return 最大值
     */
    public static int getMax(int a, int b) {
        return a > b ? a : b;
    }
    
    /**
     * 辅助方法：检查是否为空
     * @param str 字符串
     * @return 是否为空
     */
    public static boolean isEmpty(String str) {
        return str == null || str.isEmpty();
    }
}

class UtilityClass {
    private static final String DEFAULT_PREFIX = "UTIL_";
    
    /**
     * 生成带前缀的字符串
     * @param input 输入字符串
     * @return 带前缀的字符串
     */
    public static String addPrefix(String input) {
        return DEFAULT_PREFIX + input;
    }
    
    /**
     * 计算平方
     * @param number 数字
     * @return 平方值
     */
    public static int square(int number) {
        return number * number;
    }
}
