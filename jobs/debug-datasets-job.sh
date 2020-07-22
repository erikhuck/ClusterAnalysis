#!/bin/bash

SCRIPT_NAME="debug-datasets"
COHORT="adni"
DATA_NAME="mri"
JOB_NAME=${SCRIPT_NAME}-${COHORT}-${DATA_NAME}

sbatch -J $JOB_NAME \
    --time=00-12:00:00 \
    --nodes=1 \
    --ntasks=1 \
    --mem=64G \
    -o ${JOB_NAME}.out \
    -e ${JOB_NAME}.err \
    jobs/${SCRIPT_NAME}.sh ${COHORT} ${DATA_NAME}
