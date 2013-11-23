#!/bin/bash
while true
do
    python tourplanner.py

    if [ $? -eq 0 -o $? -eq 7 ]
    then
        break
    fi
done

