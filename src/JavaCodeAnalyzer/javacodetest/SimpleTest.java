/**
 * Simple test class
 */
public class SimpleTest {
    private int count;

    /**
     * Constructor
     * @param initialCount Initial count
     */
    public SimpleTest(int initialCount) {
        // Validate if initial count is valid
        this.count = initialCount;
    }

    /**
     * Get count
     * @return Current count
     */
    public int getCount() {
        return count;
    }

    /**
     * Set count
     * @param count New count
     */
    public void setCount(int count) {
        this.count = count;
        validateCount(count);
    }

    /**
     * Increment count
     * @param increment Increment amount
     */
    public void incrementCount(int increment) {
        count += increment;
        validateCount(count);
        logOperation("increment", increment);
    }

    /**
     * Validate count
     * @param count Count to validate
     */
    private void validateCount(int count) {
        if (count < 0) {
            throw new IllegalArgumentException("Count cannot be negative");
        }
    }

    /**
     * Log operation
     * @param operation Operation type
     * @param value Operation value
     */
    private void logOperation(String operation, int value) {
        System.out.println("Operation: " + operation + ", Value: " + value);
    }
}
