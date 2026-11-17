public class RotationalCipherComparison {
    private static void check(String input, int key, String expected) {
        String reference = new RotationalCipher(key).rotate(input);
        String alternative = RotationalCipherAlternative.rotate(input, key);
        if (!expected.equals(reference)) throw new AssertionError("Reference mismatch: " + reference);
        if (!expected.equals(alternative)) throw new AssertionError("Alternative mismatch: " + alternative);
    }
    public static void main(String[] args) {
        check("a", 0, "a");
        check("a", 1, "b");
        check("a", 26, "a");
        check("m", 13, "z");
        check("n", 13, "a");
        check("OMG", 5, "TRL");
        check("O M G", 5, "T R L");
        check("Testing 1 2 3 testing", 4, "Xiwxmrk 1 2 3 xiwxmrk");
        check("Let's eat, Grandma!", 21, "Gzo'n zvo, Bmviyhv!");
        check("Gur dhvpx oebja sbk whzcf bire gur ynml qbt.", 13,
              "The quick brown fox jumps over the lazy dog.");
        System.out.println("PASS: both implementations match all 10 exercise cases.");
    }
}
