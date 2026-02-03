public class NestedInnerClassTest {
    private int outerValue;
    
    /**
     * 外部类构造方法
     * @param value 初始值
     */
    public NestedInnerClassTest(int value) {
        this.outerValue = value;
    }
    
    /**
     * 获取外部值
     * @return 外部值
     */
    public int getOuterValue() {
        return outerValue;
    }
    
    /**
     * 第一层内部类
     */
    public class FirstLevelInner {
        private int firstLevelValue;
        
        /**
         * 第一层内部类构造方法
         * @param value 初始值
         */
        public FirstLevelInner(int value) {
            this.firstLevelValue = value;
        }
        
        /**
         * 获取第一层内部值
         * @return 第一层内部值
         */
        public int getFirstLevelValue() {
            return firstLevelValue;
        }
        
        /**
         * 获取外部值（通过外部类引用）
         * @return 外部值
         */
        public int getOuterValueFromInner() {
            return NestedInnerClassTest.this.outerValue;
        }
        
        /**
         * 第二层内部类
         */
        public class SecondLevelInner {
            private int secondLevelValue;
            
            /**
             * 第二层内部类构造方法
             * @param value 初始值
             */
            public SecondLevelInner(int value) {
                this.secondLevelValue = value;
            }
            
            /**
             * 获取第二层内部值
             * @return 第二层内部值
             */
            public int getSecondLevelValue() {
                return secondLevelValue;
            }
            
            /**
             * 获取第一层内部值
             * @return 第一层内部值
             */
            public int getFirstLevelValueFromInner() {
                return FirstLevelInner.this.firstLevelValue;
            }
            
            /**
             * 获取外部值
             * @return 外部值
             */
            public int getOuterValueFromDeepInner() {
                return NestedInnerClassTest.this.outerValue;
            }
            
            /**
             * 第三层内部类
             */
            public class ThirdLevelInner {
                private int thirdLevelValue;
                
                /**
                 * 第三层内部类构造方法
                 * @param value 初始值
                 */
                public ThirdLevelInner(int value) {
                    this.thirdLevelValue = value;
                }
                
                /**
                 * 获取第三层内部值
                 * @return 第三层内部值
                 */
                public int getThirdLevelValue() {
                    return thirdLevelValue;
                }
                
                /**
                 * 获取所有层级的值
                 * @return 值的字符串表示
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
     * 静态内部类
     */
    public static class StaticInnerClass {
        private static int staticValue;
        
        /**
         * 设置静态值
         * @param value 新值
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
         * 静态内部类中的静态内部类
         */
        public static class NestedStaticInner {
            private static int nestedStaticValue;
            
            /**
             * 设置嵌套静态值
             * @param value 新值
             */
            public static void setNestedStaticValue(int value) {
                nestedStaticValue = value;
            }
            
            /**
             * 获取嵌套静态值
             * @return 嵌套静态值
             */
            public static int getNestedStaticValue() {
                return nestedStaticValue;
            }
        }
    }
}
