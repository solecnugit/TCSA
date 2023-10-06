#!/bin/bash

# Setting parameters
# Adjust the parameters of sampling according to specific needs
# for example:
# start_time=$(date -d "today 03:00" +%s)
# end_time=$(date -d "today 04:00" +%s)

# Note that when using `crontab -e` to set a timed task, 
# we only need to modify `end_time` to determine the 
# total time period for collecting performance data.
start_time=$(date +%s)
end_time=$(date -d '+1 hour' +%s)
sampling_rate=999Hz
sampling_time=300
interval=300  

# Check if the parameter settings are empty
if [[ -z $start_time || -z $end_time || -z $sampling_rate || -z $sampling_time || -z $interval ]]; then
    echo "Please set the parameters."
    exit 1
fi

# Counter for naming the output file
count=1


# while [ $(date +%s) -le $end_time ]; do
    # current_time=$(date +%s)
    # output_file="perf${count}.data"

# Performs perf record cyclic sampling for a specified period of time.
while [ $(date +%s) -ge $start_time ] && [ $(date +%s) -le $end_time ]; do
    current_time=$(date +%s)
    output_file="perf${count}.data"

    # echo "run perf record，sampling period：$sampling_time s，output：$output_file"
    perf record -F $sampling_rate -a -g -o $output_file -- sleep $sampling_time

    ((count++))

    # You can set the overlap time or not, and if sampling at intervals, set interval to be the same as sampling_time.
    sleep $interval
done

echo "done"
