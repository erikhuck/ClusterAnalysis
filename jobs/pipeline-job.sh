#!/bin/bash

SCRIPT_NAME="pipeline"
COHORT="adni"
DATASET="combined"
N_CLUSTERS="2"
N_ITERATIONS="4"
JOB_NAME=${SCRIPT_NAME}-${COHORT}-${DATASET}

sbatch -J $JOB_NAME \
    --time=00-18:00:00 \
    --nodes=1 \
    --ntasks=1 \
    --mem=64G \
    -o ${JOB_NAME}.out \
    -e ${JOB_NAME}.err \
    jobs/${SCRIPT_NAME}.sh ${COHORT} ${DATASET} ${N_CLUSTERS} ${N_ITERATIONS}
