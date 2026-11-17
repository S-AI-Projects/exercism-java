/**
 * To solve our exercise, we are going to model our board based on disjoint-set data structure, also called a
 * union-find data structure or merge-find set. We are going to use two sets. One for player O and the other for
 * player X.
 * For additional documentation, check
 * <a href="https://en.wikipedia.org/wiki/Disjoint-set_data_structure">Wikipedia Disjoint-set Data Structure</a>
 * or <a href="https://algs4.cs.princeton.edu/15uf">Section 1.5</a> of
 * <i>Algorithms, 4th Edition, A nice book on DSA</i> by Robert Sedgewick and Kevin Wayne.
 */
class Connect {

    private Board boardO;
    private Board boardX;
    private int boardWidth;
    private int boardHeight;

    public Connect(String[] board) {
        if (board.length == 0) {
            return;
        }

        boardWidth = board[0]
                .replace(" ", "") // remove spaces
                .length();
        boardHeight = board.length;

        // O connects top-to-bottom; X connects left-to-right, so each player tracks a different target direction.
        boardO = new Board(boardWidth, boardHeight, false);
        boardX = new Board(boardWidth, boardHeight, true);

        // Place each stone in the corresponding player's connectivity structure.
        for (int rowIndex = 0; rowIndex < board.length; rowIndex++) {
            String row = board[rowIndex].replace(" ", "");
            for (int columnIndex = 0; columnIndex < row.length(); columnIndex++) {
                if (row.charAt(columnIndex) == 'O') {
                    boardO.placeStone(rowIndex, columnIndex);
                }
                if (row.charAt(columnIndex) == 'X') {
                    boardX.placeStone(rowIndex, columnIndex);
                }
            }
        }
    }

    public Winner computeWinner() {
        if (boardO == null || boardX == null) {
            return Winner.NONE;
        }

        // When a target edge collapses to one cell, that cell must belong to the player for a path to exist.
        boolean playerOCanConnectTopToBottom = boardWidth != 1 || boardO.hasStone(0, 0);
        boolean playerXCanConnectLeftToRight = boardHeight != 1 || boardX.hasStone(0, 0);

        if (playerOCanConnectTopToBottom && boardO.playerWins()) {
            return Winner.PLAYER_O;
        }

        if (playerXCanConnectLeftToRight && boardX.playerWins()) {
            return Winner.PLAYER_X;
        }
        return Winner.NONE;
    }
}
