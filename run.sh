#!/bin/bash
while true
do
    python tourplanner.py

    if [ $? -eq 3 ]
    then
        break
    fi
done

