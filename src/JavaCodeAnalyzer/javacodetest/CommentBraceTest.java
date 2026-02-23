public class CommentBraceTest {
    public void test() {
        String s = "Here's a brace } and another { that shouldn't end";
        char c = '}';
        // This } shouldn't end the method either
        if (true) {
            System.out.println("Inner");
        }
    }
}