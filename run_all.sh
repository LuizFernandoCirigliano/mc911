#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "<html><body>" > index.html
for filename in examples/*.lya; do
    echo "##### Running $filename ######"
    python3 run.py $filename
    echo "#######################"
    echo

    echo "<a href=\"file:///$DIR/$filename.ast.html\">$filename</a><br>" >> index.html

done

echo "</body></html>" >> index.html

#if [ "$(uname)" == "Darwin" ]; then
#    open index.html
#else
#    xdg-open index.html
#fi
