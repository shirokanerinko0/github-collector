/**
 * Test class inheritance and interface implementation relationships
 */
public class InheritanceTest {
    public static void main(String[] args) {
        // Test code
    }
}

/**
 * Base parent class
 */
class BaseClass {
    protected int value;
    
    public void setValue(int value) {
        this.value = value;
    }
    
    public int getValue() {
        return value;
    }
}

/**
 * Extend base parent class
 */
class ExtendedClass extends BaseClass {
    private String name;
    
    public void setName(String name) {
        this.name = name;
    }
    
    public String getName() {
        return name;
    }
}

/**
 * Interface
 */
interface MyInterface {
    void doSomething();
    int getResult();
}

/**
 * Another interface
 */
interface AnotherInterface {
    void doAnotherThing();
}

/**
 * Implement single interface
 */
class InterfaceImpl implements MyInterface {
    @Override
    public void doSomething() {
        System.out.println("Doing something");
    }
    
    @Override
    public int getResult() {
        return 42;
    }
}

/**
 * Implement multiple interfaces
 */
class MultipleInterfaceImpl implements MyInterface, AnotherInterface {
    @Override
    public void doSomething() {
        System.out.println("Doing something");
    }
    
    @Override
    public int getResult() {
        return 42;
    }
    
    @Override
    public void doAnotherThing() {
        System.out.println("Doing another thing");
    }
}

/**
 * Inherit and implement interface
 */
class ExtendedAndInterfaceImpl extends BaseClass implements MyInterface {
    @Override
    public void doSomething() {
        System.out.println("Doing something");
    }
    
    @Override
    public int getResult() {
        return value;
    }
}
