#!/bin/bash

runs=1

# remove not to show same again
rm clients.bin

while true
do
    echo ""
    echo "  beginning run $runs"
    echo ""

    python tourplanner.py
    ret=$?

    echo ""
    echo "================================="
    echo "  finished run $runs  (exit($ret))"
    echo "================================="

    if [ $ret -eq 0 -o $ret -eq 1 -o $ret -eq 7 ]
    then
        break
    fi

    rm clients.bin
    sleep 2
    let runs++
done

