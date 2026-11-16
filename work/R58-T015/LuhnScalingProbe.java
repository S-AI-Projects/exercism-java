import java.util.Arrays;

public class LuhnScalingProbe {
    private static volatile long sink;
    private static final int CALLS_PER_SAMPLE = 20000;
    private static final int WARMUP_CALLS = 10000;
    private static final int REPETITIONS = 5;

    public static void main(String[] args) {
        String[] candidates = {"059", "055444285", "4539319503436467"};
        LuhnValidator validator = new LuhnValidator();

        for (String candidate : candidates) {
            if (!validator.isValid(candidate)) {
                throw new AssertionError("Benchmark input is not a valid Luhn number: " + candidate);
            }

            long warmupChecksum = 0;
            for (int i = 0; i < WARMUP_CALLS; i++) {
                warmupChecksum += validator.isValid(candidate) ? 1 : 0;
            }
            sink = warmupChecksum;

            long[] samples = new long[REPETITIONS];
            for (int repetition = 0; repetition < REPETITIONS; repetition++) {
                long checksum = 0;
                long start = System.nanoTime();
                for (int i = 0; i < CALLS_PER_SAMPLE; i++) {
                    checksum += validator.isValid(candidate) ? 1 : 0;
                }
                samples[repetition] = (System.nanoTime() - start) / CALLS_PER_SAMPLE;
                sink = checksum;
            }
            Arrays.sort(samples);
            System.out.println("digits=" + candidate.length()
                    + " repetitions=" + REPETITIONS
                    + " calls_per_repetition=" + CALLS_PER_SAMPLE
                    + " median_ns_per_call=" + samples[REPETITIONS / 2]);
        }
    }
}
