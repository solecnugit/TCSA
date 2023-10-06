#!/bin/bash

# Get all perf*.data files in the current directory
perf_files=$(ls perf*.data)

# Iterate through each perf file and convert it to a text file
for file in $perf_files; do
    filename=$(basename "$file" .data)
    perf script -i "$file" > "${filename}.txt"
    # echo "Converted $file to ${filename}.txt"
done

echo "done"
