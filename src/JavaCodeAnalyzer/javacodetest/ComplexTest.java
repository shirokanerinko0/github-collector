/**
 * Complex test class
 */
public class ComplexTest {
    private String[] names;
    private static final int MAX_SIZE = 100;

    /**
     * Constructor
     * @param size Array size
     */
    public ComplexTest(int size) {
        if (size > MAX_SIZE) {
            size = MAX_SIZE;
        }
        names = new String[size];
    }

    /**
     * Add name
     * @param index Index
     * @param name Name
     * @return Whether added successfully
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
     * Get name
     * @param index Index
     * @return Name
     */
    public String getName(int index) {
        if (validateIndex(index)) {
            return names[index];
        }
        return null;
    }

    /**
     * Validate index
     * @param index Index
     * @return Whether valid
     */
    private boolean validateIndex(int index) {
        return index >= 0 && index < names.length;
    }

    /**
     * Validate name
     * @param name Name
     * @return Whether valid
     */
    private boolean validateName(String name) {
        return name != null && !name.isEmpty();
    }

    /**
     * Log operation
     * @param operation Operation type
     * @param detail Detail information
     */
    private void logOperation(String operation, String detail) {
        System.out.println("Operation: " + operation + ", Detail: " + detail);
    }

    /**
     * Static method: Get maximum value
     * @param numbers Number array
     * @return Maximum value
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
     * Get array size
     * @return Array size
     */
    public int getSize() {
        return names.length;
    }

    /**
     * Clear array
     */
    public void clear() {
        for (int i = 0; i < names.length; i++) {
            names[i] = null;
        }
        logOperation("clear", "all");
    }
}
