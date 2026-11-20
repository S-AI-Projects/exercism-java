import java.util.List;

/**
 * Reference implementation for the 0/1 Knapsack exercise.
 *
 * Computational Complexity:
 * - Time Complexity: O(N * W), where N is the number of item records and W is maximumWeight.
 *   The algorithm fills a 2D dynamic programming grid of size (N + 1) * (W + 1) across two
 *   nested loops, executing constant-time state updates in each cell.
 * - Space Complexity: O(N * W), allocating an int[N + 1][W + 1] memoization table.
 */
class Knapsack {

    int maximumValue(int maximumWeight, List<Item> items) {
        return maximumValueHelperBottomUp(maximumWeight, items);
    }

    private int maximumValueHelperBottomUp(
        int maximumWeight, List<Item> items) {
        int[][] knapsack = new int[items.size() + 1][maximumWeight + 1]; 
        for (int item = 0; item <= items.size(); item++) {
            for (int weight = 0; weight <= maximumWeight; weight++) {
                knapsack[item][weight] = 0; // Return 0 if not filled
            }
        }
        for (int item = 0; item <= items.size(); item++) {
            for (int weight = 0; weight <= maximumWeight; weight++) {
                if (item == 0 || weight == 0) {
                    knapsack[item][weight] = 0;    
                } else if (items.get(item - 1).weight > weight) {
                    knapsack[item][weight] = knapsack[item - 1][weight];
                } else {
                    int itemValue  = items.get(item - 1).value;
                    int itemWeight  = items.get(item - 1).weight;
                    knapsack[item][weight] = 
                        Math.max(
                            itemValue + knapsack[item - 1][weight - itemWeight],
                            knapsack[item - 1][weight]
                        );
                }
            }
        }
        return knapsack[items.size()][maximumWeight];
    }

}
