#!/bin/bash
cat c\(k\)_2011.txt |awk '{ print $2 }'|sort|uniq
