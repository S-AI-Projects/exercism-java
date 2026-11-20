import java.util.ArrayList;
import java.util.List;

public class SplitSecondStopwatch {

    private enum State {
        READY,
        RUNNING,
        STOPPED
    }

    private State state;
    private int currentLapSeconds;
    private int totalLapSeconds;
    private final List<Integer> previousLapDurations;

    public SplitSecondStopwatch() {
        this.state = State.READY;
        this.currentLapSeconds = 0;
        this.totalLapSeconds = 0;
        this.previousLapDurations = new ArrayList<>();
    }

    public void start() {
        if (state == State.RUNNING) {
            throw new IllegalStateException("cannot start an already running stopwatch");
        }
        state = State.RUNNING;
    }

    public void stop() {
        if (state != State.RUNNING) {
            throw new IllegalStateException("cannot stop a stopwatch that is not running");
        }
        state = State.STOPPED;
    }

    public void reset() {
        if (state != State.STOPPED) {
            throw new IllegalStateException("cannot reset a stopwatch that is not stopped");
        }
        state = State.READY;
        currentLapSeconds = 0;
        totalLapSeconds = 0;
        previousLapDurations.clear();
    }

    public void lap() {
        if (state != State.RUNNING) {
            throw new IllegalStateException("cannot lap a stopwatch that is not running");
        }
        previousLapDurations.add(currentLapSeconds);
        totalLapSeconds += currentLapSeconds;
        currentLapSeconds = 0;
    }

    public String state() {
        return state.name().toLowerCase();
    }

    public String currentLap() {
        return formatSeconds(currentLapSeconds);
    }

    public String total() {
        return formatSeconds(totalLapSeconds + currentLapSeconds);
    }

    public List<String> previousLaps() {
        List<String> formatted = new ArrayList<>(previousLapDurations.size());
        for (int duration : previousLapDurations) {
            formatted.add(formatSeconds(duration));
        }
        return formatted;
    }

    public void advanceTime(String timeString) {
        if (state == State.RUNNING) {
            currentLapSeconds += parseToSeconds(timeString);
        }
    }

    private static int parseToSeconds(String timeString) {
        String[] parts = timeString.split(":");
        int hours = Integer.parseInt(parts[0]);
        int minutes = Integer.parseInt(parts[1]);
        int seconds = Integer.parseInt(parts[2]);
        return hours * 3600 + minutes * 60 + seconds;
    }

    private static String formatSeconds(int totalSeconds) {
        int hours = totalSeconds / 3600;
        int minutes = (totalSeconds % 3600) / 60;
        int seconds = totalSeconds % 60;
        return String.format("%02d:%02d:%02d", hours, minutes, seconds);
    }
}
