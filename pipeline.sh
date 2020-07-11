#!/bin/sh

COHORT=$1
DATASET=$2
N_CLUSTERS=$3
N_ITERATIONS=$4

source ../env/bin/activate
python3 main.py pipeline --cohort $COHORT --dataset $DATASET --n-clusters $N_CLUSTERS --n-iterations $N_ITERATIONS
