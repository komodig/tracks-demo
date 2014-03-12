#!/bin/bash

file_list_cmd="`find * -name '*.py'`"

for f in $file_list_cmd; do
    if [ "$f" == "sed.sh" ]; then
        echo "skipping $f"
        continue
    fi

    [ -f $f ] || continue

    echo "tuuuut: $f"
    sed -i "s/DISPLAY..unite_areas..:/DISPLAY['areas']['unite_info']:/g" $f

#    git checkout $f
done


