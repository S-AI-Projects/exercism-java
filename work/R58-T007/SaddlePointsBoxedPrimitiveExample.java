import java.util.Collections;
import java.util.List;

public class SaddlePointsBoxedPrimitiveExample {
    public static void main(String[] args) {
        // Construct used by getRowMax: auto-unboxing Collections.max to primitive int
        List<Integer> row = List.of(128, 64, 32);
        int coordinateValue = row.get(0);
        int rowMax = Collections.max(row);
        boolean primitiveComparison = coordinateValue == rowMax;
        System.out.println(primitiveComparison);

        // Contrasting pitfall: comparing boxed Integer objects using == (outside [-128, 127] cache)
        Integer boxedCoordinate = Integer.valueOf(128);
        Integer boxedRowMax = Integer.valueOf(128);
        boolean boxedReferenceComparison = boxedCoordinate == boxedRowMax;
        System.out.println(boxedReferenceComparison);
    }
}
