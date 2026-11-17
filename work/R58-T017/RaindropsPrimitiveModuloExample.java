public class RaindropsPrimitiveModuloExample {
    public static void main(String[] args) {
        int number = 15;
        boolean divisibleByThree = number % 3 == 0;
        boolean incorrectDivisionCheck = number / 3 == 0;
        System.out.println(divisibleByThree);
        System.out.println(incorrectDivisionCheck);
    }
}
