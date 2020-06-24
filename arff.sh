#!/bin/bash

if [ -z "$1" ]
then
    COMMAND=python3
else
    COMMAND=pudb3
fi

source env/bin/activate
$COMMAND main.py arff --data-path raw-data/raw-data-set.csv --data-types-path raw-data/col-types.csv
