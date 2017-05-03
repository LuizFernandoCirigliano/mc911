#!/bin/bash
for filename in examples/*.lya; do
    echo "##### Running $filename ######"
    python3 run.py $filename
    echo "#######################"
    echo
done