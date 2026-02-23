public class MultipleClassesTest {
    private String name;
    private int value;
    
    /**
     * Constructor
     * @param name Name
     * @param value Value
     */
    public MultipleClassesTest(String name, int value) {
        this.name = name;
        this.value = value;
    }
    
    /**
     * Get name
     * @return Name
     */
    public String getName() {
        return name;
    }
    
    /**
     * Set value
     * @param value New value
     */
    public void setValue(int value) {
        this.value = value;
    }
    
    /**
     * Execute operation
     * @param factor Factor
     * @return Operation result
     */
    public int executeOperation(int factor) {
        return value * factor;
    }
}

class HelperClass {
    /**
     * Helper method: Calculate maximum value
     * @param a First value
     * @param b Second value
     * @return Maximum value
     */
    public static int getMax(int a, int b) {
        return a > b ? a : b;
    }
    
    /**
     * Helper method: Check if empty
     * @param str String
     * @return Whether empty
     */
    public static boolean isEmpty(String str) {
        return str == null || str.isEmpty();
    }
}

class UtilityClass {
    private static final String DEFAULT_PREFIX = "UTIL_";
    
    /**
     * Generate prefixed string
     * @param input Input string
     * @return Prefixed string
     */
    public static String addPrefix(String input) {
        return DEFAULT_PREFIX + input;
    }
    
    /**
     * Calculate square
     * @param number Number
     * @return Square value
     */
    public static int square(int number) {
        return number * number;
    }
}
