# Debugging hints

The gigasecond is an exact duration of 1,000,000,000 seconds. Keep the seconds in the duration: dropping or adding even one second changes the expected result. The existing `modernTime` case is a useful diagnostic: for the input date `2011-04-25`, the reference result is `2043-01-01T01:46:40`. A mutant that adds 999,999,999 seconds instead produces `2043-01-01T01:46:39`, so the test catches the off-by-one error.

This example illustrates a duration-boundary mistake; it does not indicate a defect in the maintained reference implementation.
