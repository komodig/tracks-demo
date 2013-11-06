#!/bin/bash
while true
do
    python tourplanner.py

    if [ $? -gt 0 ] 
    then
        break
    fi
done

