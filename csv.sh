#!/bin/bash

if [ -z "$1" ]
then
    COMMAND=python3
else
    COMMAND=pudb3
fi

source env/bin/activate
$COMMAND main.py csv --arff-path data.arff --kept-feats feat-select/kept-feats-0.2.txt
