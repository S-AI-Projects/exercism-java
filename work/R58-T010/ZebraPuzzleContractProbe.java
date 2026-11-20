public class ZebraPuzzleContractProbe {

    private static void check(boolean condition, String message) {
        if (!condition) {
            throw new AssertionError(message);
        }
    }

    public static void main(String[] args) {
        // Contract Check 1: Normal instantiation and water drinker getter
        ZebraPuzzle puzzle1 = new ZebraPuzzle();
        String waterDrinker = puzzle1.getWaterDrinker();
        check(waterDrinker != null, "getWaterDrinker() must not return null");
        check("Norwegian".equals(waterDrinker),
                "Expected water drinker to be 'Norwegian', got: " + waterDrinker);

        // Contract Check 2: Zebra owner getter
        String zebraOwner = puzzle1.getZebraOwner();
        check(zebraOwner != null, "getZebraOwner() must not return null");
        check("Japanese".equals(zebraOwner),
                "Expected zebra owner to be 'Japanese', got: " + zebraOwner);

        // Contract Check 3: Order independence (query zebra owner before water drinker)
        ZebraPuzzle puzzle2 = new ZebraPuzzle();
        String zebraFirst = puzzle2.getZebraOwner();
        String waterSecond = puzzle2.getWaterDrinker();
        check("Japanese".equals(zebraFirst),
                "Expected zebra owner on first call to be 'Japanese', got: " + zebraFirst);
        check("Norwegian".equals(waterSecond),
                "Expected water drinker on second call to be 'Norwegian', got: " + waterSecond);

        // Contract Check 4: Idempotence (repeated calls must return identical results)
        check(puzzle2.getWaterDrinker().equals(waterSecond),
                "getWaterDrinker() must be idempotent on repeated calls");
        check(puzzle2.getZebraOwner().equals(zebraFirst),
                "getZebraOwner() must be idempotent on repeated calls");

        // Contract Check 5: Strict type check
        check(waterDrinker.getClass() == String.class, "getWaterDrinker() return type must be java.lang.String");
        check(zebraOwner.getClass() == String.class, "getZebraOwner() return type must be java.lang.String");

        System.out.println("PASS: ZebraPuzzle contract verified (waterDrinker=Norwegian, zebraOwner=Japanese, order-independent, idempotent).");
    }
}
