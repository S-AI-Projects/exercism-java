import java.util.Arrays;

class DigitMinimumExample {
    public static void main(String[] args) {
        int[] digits = {1, 0, 1};
        int smallestDigit = Arrays.stream(digits).min().getAsInt();
        System.out.println(smallestDigit);

        int[] noDigits = {};
        if (noDigits.length == 0) {
            System.out.println("no digits to check");
        } else {
            System.out.println(Arrays.stream(noDigits).min().getAsInt());
        }
    }
}
