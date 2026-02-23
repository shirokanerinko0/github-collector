public class NestedInnerClassTest {
    private int outerValue;
    
    /**
     * Outer class constructor
     * @param value Initial value
     */
    public NestedInnerClassTest(int value) {
        this.outerValue = value;
    }
    
    /**
     * Get outer value
     * @return Outer value
     */
    public int getOuterValue() {
        return outerValue;
    }
    
    /**
     * First level inner class
     */
    public class FirstLevelInner {
        private int firstLevelValue;
        
        /**
         * First level inner class constructor
         * @param value Initial value
         */
        public FirstLevelInner(int value) {
            this.firstLevelValue = value;
        }
        
        /**
         * Get first level inner value
         * @return First level inner value
         */
        public int getFirstLevelValue() {
            return firstLevelValue;
        }
        
        /**
         * Get outer value (via outer class reference)
         * @return Outer value
         */
        public int getOuterValueFromInner() {
            return NestedInnerClassTest.this.outerValue;
        }
        
        /**
         * Second level inner class
         */
        public class SecondLevelInner {
            private int secondLevelValue;
            
            /**
             * Second level inner class constructor
             * @param value Initial value
             */
            public SecondLevelInner(int value) {
                this.secondLevelValue = value;
            }
            
            /**
             * Get second level inner value
             * @return Second level inner value
             */
            public int getSecondLevelValue() {
                return secondLevelValue;
            }
            
            /**
             * Get first level inner value
             * @return First level inner value
             */
            public int getFirstLevelValueFromInner() {
                return FirstLevelInner.this.firstLevelValue;
            }
            
            /**
             * Get outer value
             * @return Outer value
             */
            public int getOuterValueFromDeepInner() {
                return NestedInnerClassTest.this.outerValue;
            }
            
            /**
             * Third level inner class
             */
            public class ThirdLevelInner {
                private int thirdLevelValue;
                
                /**
                 * Third level inner class constructor
                 * @param value Initial value
                 */
                public ThirdLevelInner(int value) {
                    this.thirdLevelValue = value;
                }
                
                /**
                 * Get third level inner value
                 * @return Third level inner value
                 */
                public int getThirdLevelValue() {
                    return thirdLevelValue;
                }
                
                /**
                 * Get all levels values
                 * @return String representation of values
                 */
                public String getAllLevelsValues() {
                    return "Outer: " + NestedInnerClassTest.this.outerValue + 
                           ", First: " + FirstLevelInner.this.firstLevelValue + 
                           ", Second: " + SecondLevelInner.this.secondLevelValue + 
                           ", Third: " + this.thirdLevelValue;
                }
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
         * @param value New value
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
         * Static inner class within static inner class
         */
        public static class NestedStaticInner {
            private static int nestedStaticValue;
            
            /**
             * Set nested static value
             * @param value New value
             */
            public static void setNestedStaticValue(int value) {
                nestedStaticValue = value;
            }
            
            /**
             * Get nested static value
             * @return Nested static value
             */
            public static int getNestedStaticValue() {
                return nestedStaticValue;
            }
        }
    }
}
