/**
 * 内部类测试
 */
public class InnerClassTest {
    private int outerValue;
    private InnerClass inner;

    /**
     * 构造方法
     */
    public InnerClassTest() {
        this.outerValue = 0;
        this.inner = new InnerClass();
    }

    /**
     * 设置外部值
     * @param value 外部值
     */
    public void setOuterValue(int value) {
        this.outerValue = value;
        inner.updateInnerValue(value);
    }

    /**
     * 获取内部值
     * @return 内部值
     */
    public int getInnerValue() {
        return inner.getInnerValue();
    }

    /**
     * 执行操作
     * @param value 操作值
     * @return 操作结果
     */
    public int executeOperation(int value) {
        int result = inner.processValue(value);
        logOperation("execute", value, result);
        return result;
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

    /**
     * 内部类
     */
    private class InnerClass {
        private int innerValue;

        /**
         * 构造方法
         */
        public InnerClass() {
            this.innerValue = 0;
        }

        /**
         * 更新内部值
         * @param value 新值
         */
        public void updateInnerValue(int value) {
            this.innerValue = value;
            validateValue(innerValue);
        }

        /**
         * 获取内部值
         * @return 内部值
         */
        public int getInnerValue() {
            return innerValue;
        }

        /**
         * 处理值
         * @param value 输入值
         * @return 处理结果
         */
        public int processValue(int value) {
            innerValue += value;
            validateValue(innerValue);
            return innerValue;
        }

        /**
         * 验证值
         * @param value 要验证的值
         */
        private void validateValue(int value) {
            if (value < 0) {
                throw new IllegalArgumentException("Value cannot be negative");
            }
        }
    }

    /**
     * 静态内部类
     */
    public static class StaticInnerClass {
        private static int staticValue;

        /**
         * 设置静态值
         * @param value 静态值
         */
        public static void setStaticValue(int value) {
            staticValue = value;
        }

        /**
         * 获取静态值
         * @return 静态值
         */
        public static int getStaticValue() {
            return staticValue;
        }

        /**
         * 执行静态操作
         * @param value 操作值
         * @return 操作结果
         */
        public static int executeStaticOperation(int value) {
            return staticValue + value;
        }
    }
}
