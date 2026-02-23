/**
 * Test interface
 */
interface TestInterface {
    /**
     * Execute operation
     * @param value Operation value
     * @return Operation result
     */
    int execute(int value);

    /**
     * Get status
     * @return Status
     */
    String getStatus();
}

/**
 * Interface implementation class
 */
class InterfaceImpl implements TestInterface {
    private int count;
    private String status;

    /**
     * Constructor
     */
    public InterfaceImpl() {
        this.count = 0;
        this.status = "INITIALIZED";
    }

    /**
     * Execute operation
     * @param value Operation value
     * @return Operation result
     */
    @Override
    public int execute(int value) {
        int result = processValue(value);
        updateStatus("EXECUTED");
        logOperation("execute", value, result);
        return result;
    }

    /**
     * Get status
     * @return Status
     */
    @Override
    public String getStatus() {
        return status;
    }

    /**
     * Process value
     * @param value Input value
     * @return Processing result
     */
    private int processValue(int value) {
        count += value;
        validateCount(count);
        return count;
    }

    /**
     * Validate count
     * @param count Count
     */
    private void validateCount(int count) {
        if (count < 0) {
            throw new IllegalStateException("Count cannot be negative");
        }
    }

    /**
     * Update status
     * @param newStatus New status
     */
    private void updateStatus(String newStatus) {
        this.status = newStatus;
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
}

/**
 * Test main class
 */
public class InterfaceTest {
    /**
     * Main method
     * @param args Command line arguments
     */
    public static void main(String[] args) {
        TestInterface test = new InterfaceImpl();
        int result1 = test.execute(5);
        int result2 = test.execute(10);
        System.out.println("Final result: " + result2);
        System.out.println("Status: " + test.getStatus());
    }
}
