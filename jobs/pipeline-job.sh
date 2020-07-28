#!/bin/bash

SCRIPT_NAME="pipeline"
COHORT="adni"
DATASET="mri"
CLUSTER_METHOD="nearest_neighbors"
N_CLUSTERS=$1
N_ITERATIONS="5"
DO_DEBUG="" # "" is false and "--do-debug" is true
DO_CONTINUE="" # "" is false and "--do-continue" is true
JOB_NAME=${SCRIPT_NAME}-${COHORT}-${DATASET}-${CLUSTER_METHOD}-${N_CLUSTERS}

sbatch -J $JOB_NAME \
    --time=03-00:00:00 \
    --nodes=1 \
    --ntasks=1 \
    --mem=512G \
    -o ${JOB_NAME}.out \
    -e ${JOB_NAME}.err \
    jobs/${SCRIPT_NAME}.sh ${COHORT} ${DATASET} ${CLUSTER_METHOD} ${N_CLUSTERS} ${N_ITERATIONS} ${DO_DEBUG} ${DO_CONTINUE}
