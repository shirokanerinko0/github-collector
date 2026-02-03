public class CommentBraceTest {
    public void test() {
        String s = "这里有个大括号 } 还有个 { 不应该结束";
        char c = '}';
        // 这里的 } 也不应该结束方法
        if (true) {
            System.out.println("Inner");
        }
    }
}