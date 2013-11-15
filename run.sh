#!/bin/bash
while true
do
    python tourplanner.py

    if [ $? -lt 2 ]
    then
        break
    fi
done

