#!/bin/sh

COHORT=$1
DATASET=$2
CLUSTER_METHOD=$3
N_CLUSTERS=$4
N_ITERATIONS=$5
DO_DEBUG=$6
DO_CONTINUE=$7

source ../env/bin/activate
python3 main.py pipeline --cohort $COHORT --dataset $DATASET --cluster-method $CLUSTER_METHOD --n-clusters $N_CLUSTERS --n-iterations $N_ITERATIONS $DO_DEBUG $DO_CONTINUE
