import java.lang.annotation.*;

/**
 * Java class for testing annotation extraction functionality
 */
@Deprecated
@SuppressWarnings("unused")
public class AnnotationTest {
    private int value;

    /**
     * Constructor
     * @param value Initial value
     */
    @Override
    public AnnotationTest(int value) {
        this.value = value;
    }

    /**
     * Get value
     * @return Current value
     */
    @Override
    @SuppressWarnings("unchecked")
    public int getValue() {
        return value;
    }

    /**
     * Set value
     * @param value New value
     */
    @Deprecated
    @SuppressWarnings({"unchecked", "rawtypes"})
    public void setValue(int value) {
        this.value = value;
    }

    /**
     * Custom annotation test
     */
    @MyAnnotation(name = "test", value = 100)
    public void testCustomAnnotation() {
        System.out.println("Custom annotation test");
    }

    /**
     * Static method test
     */
    @SuppressWarnings("static-access")
    public static void staticMethod() {
        AnnotationTest test = new AnnotationTest(0);
        System.out.println(test.value);
    }
}

/**
 * Custom annotation
 */
@Retention(RetentionPolicy.RUNTIME)
@Target({ElementType.METHOD, ElementType.TYPE})
@interface MyAnnotation {
    String name();
    int value();
}
