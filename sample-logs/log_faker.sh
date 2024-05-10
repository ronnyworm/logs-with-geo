#!/bin/bash

input_file="$1"
output_file="$2"
lines_per_append=5

while IFS= read -r line; do
    echo "$line" >> "$output_file"
    lines_appended=$((lines_appended + 1))

    if [ "$lines_appended" -eq "$lines_per_append" ]; then
        lines_appended=0

        # Close the file before sleeping
        exec 3>&-

        # Generate a random sleep time between 10 to 40 seconds
        # sleep_time=$((RANDOM % 31 + 10))
        # Generate a random sleep time between 1 to 10 seconds
        sleep_time=$((RANDOM % 11 + 1))
        echo sleep "$sleep_time"
        sleep "$sleep_time"

        # Reopen the file for appending
        exec 3>> "$output_file"
    fi
done < "$input_file"
