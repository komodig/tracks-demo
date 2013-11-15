#!/bin/bash
while true
do
    python tourplanner.py

    if [ $? -eq 0 ]
    then
        break
    fi
done

