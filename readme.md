# TCSA: Efficient Localization of Busy-Wait Synchronization Bugs for Latency-Critical Applications

This repository is the implementation of TCSA. 

# Usage

## Performance Data Collection

We have implemented a performance data collection script in the `collector` folder to automate the collection of performance data by setting parameters for sampling.
The sampling parameters include: start time, end time, sampling frequency, and sampling period of performance data sampling.

There are two ways to realize automated sampling:

(1) Set the above parameters in recorder.bash to execute automated sampling and immediately execute recorder.bash.

(2) Setting a timer (e.g., `cron`) to execute the `recorder.bash` script file at regular intervals.

Let's take `cron` as an example to illustrate (2).

 - First edit the cron task list with `crontab -e`.
 - Then add the timed tasks you want to execute. Example: `0 3 * * * * /path/recorder.bash` means "Execute the recorder.bash script under the `/path` path at 3:00 a.m. every day".

After `recorder.bash` is executed, the performance data is stored in the current directory.

The `converter.bash` script converts all `perfX.data` into `perfX.txt` files.


Of course, it is also possible to perform the performance data collection and conversion process manually.



## Localization with TCSA


We automate the location of busy-wait synchronization performance bugs by executing TCSA as shown below. We need to specify the path to the performance data to be analyzed and specify the path to where the result files of the automated location are stored.

Use the command as follows:

**`python main.py <file_path> <output_path> [direction] [degrees_of_freedom] [threshold]`**


`file_path` : The path of the collected function call stack data, include the file name.

`output_path` : The path to store the output results.

` direction ` : The direction of identification of consecutive identical call stacks. 1 means top-down, 0 means bottom-up.

`degrees_of_freedom` : The depth when judging consecutive identical events for threads. 

` threshold ` : Set the threshold value for the number of durations. The default -1 means use the average value.


# Requirements
The specific environment requirements for python are in the requirements.txt file.

- python3

- Linux perf

# Example


# People 

- System Optimization Lab, East China Normal University (SOLE)


# Contact Information

If you have any questions or suggestions, please contact Ning Li via ningli@stu#DOTecnu#DOTedu.cn.


# Repository Special Description

origin: https://jihulab.com/solecnu/tcsa

mirror: https://github.com/MercuryLc/TCSA