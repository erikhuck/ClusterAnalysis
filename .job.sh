#!/bin/bash

JOB_NAME="data_clean"

sbatch -J $JOB_NAME \
    --time=00-05:00:00 \
    --nodes=1 \
    --ntasks=5 \
    --mem=128G \
    -o .${JOB_NAME}.out \
    -e .${JOB_NAME}.err \
    .${JOB_NAME}.sh
