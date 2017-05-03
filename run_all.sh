#!/bin/bash
for filename in examples/*.lya; do
    echo "##### Running $filename ######"
    python3 lyaparser.py $filename
    echo "#######################"
    echo
done