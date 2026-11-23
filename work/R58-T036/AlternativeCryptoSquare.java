import java.util.Locale;

/** Independent direct-index crypto-square implementation used only for comparison. */
class AlternativeCryptoSquare {

    static String encode(String plaintext) {
        String normalized = plaintext.toLowerCase(Locale.ROOT).codePoints()
                .filter(Character::isLetterOrDigit)
                .collect(StringBuilder::new, StringBuilder::appendCodePoint, StringBuilder::append)
                .toString();
        if (normalized.isEmpty()) {
            return "";
        }

        int columns = (int) Math.ceil(Math.sqrt(normalized.length()));
        int rows = (normalized.length() + columns - 1) / columns;
        StringBuilder result = new StringBuilder(normalized.length() + columns - 1);
        for (int column = 0; column < columns; column++) {
            if (column > 0) {
                result.append(' ');
            }
            for (int row = 0; row < rows; row++) {
                int sourceIndex = row * columns + column;
                result.append(sourceIndex < normalized.length() ? normalized.charAt(sourceIndex) : ' ');
            }
        }
        return result.toString();
    }
}
