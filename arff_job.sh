#!/bin/bash

JOB_NAME="arff"

sbatch -J $JOB_NAME \
    --time=00-01:30:00 \
    --nodes=1 \
    --ntasks=3 \
    --mem=16G \
    -o ${JOB_NAME}.out \
    -e ${JOB_NAME}.err \
    ${JOB_NAME}.sh
