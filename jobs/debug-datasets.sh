#!/bin/sh

COHORT=$1
DATA_NAME=$2

source ../env/bin/activate
python3 main.py debug-datasets --cohort $COHORT --data-name $DATA_NAME
