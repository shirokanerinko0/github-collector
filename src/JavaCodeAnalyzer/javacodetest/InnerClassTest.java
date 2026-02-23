/**
 * Inner class test
 */
public class InnerClassTest {
    private int outerValue;
    private InnerClass inner;

    /**
     * Constructor
     */
    public InnerClassTest() {
        this.outerValue = 0;
        this.inner = new InnerClass();
    }

    /**
     * Set outer value
     * @param value Outer value
     */
    public void setOuterValue(int value) {
        this.outerValue = value;
        inner.updateInnerValue(value);
    }

    /**
     * Get inner value
     * @return Inner value
     */
    public int getInnerValue() {
        return inner.getInnerValue();
    }

    /**
     * Execute operation
     * @param value Operation value
     * @return Operation result
     */
    public int executeOperation(int value) {
        int result = inner.processValue(value);
        logOperation("execute", value, result);
        return result;
    }

    /**
     * Log operation
     * @param operation Operation type
     * @param input Input value
     * @param output Output value
     */
    private void logOperation(String operation, int input, int output) {
        System.out.println("Operation: " + operation + ", Input: " + input + ", Output: " + output);
    }

    /**
     * Inner class
     */
    private class InnerClass {
        private int innerValue;

        /**
         * Constructor
         */
        public InnerClass() {
            this.innerValue = 0;
        }

        /**
         * Update inner value
         * @param value New value
         */
        public void updateInnerValue(int value) {
            this.innerValue = value;
            validateValue(innerValue);
        }

        /**
         * Get inner value
         * @return Inner value
         */
        public int getInnerValue() {
            return innerValue;
        }

        /**
         * Process value
         * @param value Input value
         * @return Processing result
         */
        public int processValue(int value) {
            innerValue += value;
            validateValue(innerValue);
            return innerValue;
        }

        /**
         * Validate value
         * @param value Value to validate
         */
        private void validateValue(int value) {
            if (value < 0) {
                throw new IllegalArgumentException("Value cannot be negative");
            }
        }
    }

    /**
     * Static inner class
     */
    public static class StaticInnerClass {
        private static int staticValue;

        /**
         * Set static value
         * @param value Static value
         */
        public static void setStaticValue(int value) {
            staticValue = value;
        }

        /**
         * Get static value
         * @return Static value
         */
        public static int getStaticValue() {
            return staticValue;
        }

        /**
         * Execute static operation
         * @param value Operation value
         * @return Operation result
         */
        public static int executeStaticOperation(int value) {
            return staticValue + value;
        }
    }
}
