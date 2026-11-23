import java.util.List;

class BinarySearchBoxingDemo {
    public static void main(String[] args) {
        Integer target = Integer.valueOf(10);
        Integer middle = List.of(4, 10, 21).get(1);
        System.out.println(target.compareTo(middle) == 0);
        System.out.println((int) middle);
    }
}
