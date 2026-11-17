final class RotationalCipherAlternative {
    private static final String LOWER = "abcdefghijklmnopqrstuvwxyz";
    private static final String UPPER = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";

    static String rotate(String input, int key) {
        int shift = Math.floorMod(key, 26);
        StringBuilder result = new StringBuilder(input.length());
        for (int i = 0; i < input.length(); i++) {
            char current = input.charAt(i);
            int lowerIndex = LOWER.indexOf(current);
            if (lowerIndex >= 0) {
                result.append(LOWER.charAt((lowerIndex + shift) % LOWER.length()));
                continue;
            }
            int upperIndex = UPPER.indexOf(current);
            if (upperIndex >= 0) {
                result.append(UPPER.charAt((upperIndex + shift) % UPPER.length()));
            } else {
                result.append(current);
            }
        }
        return result.toString();
    }
}
