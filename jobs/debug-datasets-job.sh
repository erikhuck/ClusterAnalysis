#!/bin/bash

SCRIPT_NAME="debug-datasets"
COHORT="adni"
DATASET="genotypes"
JOB_NAME=${SCRIPT_NAME}-${COHORT}-${DATASET}

sbatch -J $JOB_NAME \
    --time=00-16:00:00 \
    --nodes=1 \
    --ntasks=1 \
    --mem=256G \
    -o ${JOB_NAME}.out \
    -e ${JOB_NAME}.err \
    jobs/${SCRIPT_NAME}.sh ${COHORT} ${DATASET}
