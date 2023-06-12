# TCSA: Efficient Localization of Busy-Wait Synchronization Bugs for Latency-Critical Applications

This repository is the implementation of TCSA. 


# Localization with TCSA:

**`python main.py <file_path> <output_path> [direction] [degrees_of_freedom] [threshold]`**


`file_path` : The path of the collected function call stack data, include the file name.

`output_path` : The path to store the output results.

` direction ` : The direction of identification of consecutive identical call stacks. 1 means top-down, 0 means bottom-up.

`degrees_of_freedom` : The depth when judging consecutive identical events for threads. 

` threshold ` : Set the threshold value for the number of durations. The default -1 means use the average value.


# Requirements

- python3

- perf
