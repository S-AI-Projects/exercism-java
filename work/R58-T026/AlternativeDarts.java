class Darts {

    private static final double INNER_RADIUS_SQUARED = 1.0;
    private static final double MIDDLE_RADIUS_SQUARED = 25.0;
    private static final double OUTER_RADIUS_SQUARED = 100.0;

    int score(double x, double y) {
        double distanceSquared = x * x + y * y;

        if (distanceSquared <= INNER_RADIUS_SQUARED) {
            return 10;
        } else if (distanceSquared <= MIDDLE_RADIUS_SQUARED) {
            return 5;
        } else if (distanceSquared <= OUTER_RADIUS_SQUARED) {
            return 1;
        }
        return 0;
    }
}
