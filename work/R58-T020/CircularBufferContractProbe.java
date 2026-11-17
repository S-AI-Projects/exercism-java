public class CircularBufferContractProbe {
    private static void check(boolean condition, String message) {
        if (!condition) throw new AssertionError(message);
    }

    private static void expectBufferError(RunnableWithBufferException action, String message) throws Exception {
        try {
            action.run();
            throw new AssertionError("Expected BufferIOException: " + message);
        } catch (BufferIOException error) {
            check(message.equals(error.getMessage()), "Unexpected exception message: " + error.getMessage());
        }
    }

    @FunctionalInterface
    interface RunnableWithBufferException {
        void run() throws Exception;
    }

    public static void main(String[] args) throws Exception {
        CircularBuffer<Integer> empty = new CircularBuffer<>(1);
        expectBufferError(empty::read, "Tried to read from empty buffer");

        CircularBuffer<Integer> notFull = new CircularBuffer<>(2);
        notFull.write(1);
        notFull.overwrite(2);
        check(notFull.read() == 1 && notFull.read() == 2,
                "overwrite on a non-full buffer must append like write");

        CircularBuffer<Integer> full = new CircularBuffer<>(2);
        full.write(1); full.write(2); full.overwrite(3);
        check(full.read() == 2 && full.read() == 3,
                "overwrite on a full buffer must discard the oldest unread item");

        CircularBuffer<Integer> afterRead = new CircularBuffer<>(3);
        afterRead.write(1); afterRead.write(2); afterRead.write(3);
        check(afterRead.read() == 1, "first read should return oldest item");
        afterRead.write(4); afterRead.overwrite(5);
        check(afterRead.read() == 3 && afterRead.read() == 4 && afterRead.read() == 5,
                "overwrite must discard the oldest item still unread, not an item already read");

        CircularBuffer<Integer> afterClear = new CircularBuffer<>(2);
        afterClear.clear();
        afterClear.write(1); afterClear.write(2);
        afterClear.overwrite(3); afterClear.overwrite(4);
        check(afterClear.read() == 3 && afterClear.read() == 4,
                "clear on an empty buffer must not break subsequent wrap-around behavior");
        expectBufferError(afterClear::read, "Tried to read from empty buffer");

        CircularBuffer<Integer> fullWrite = new CircularBuffer<>(1);
        fullWrite.write(7);
        expectBufferError(() -> fullWrite.write(8), "Tried to write to full buffer");

        System.out.println("PASS: six circular-buffer contract checks.");
    }
}
