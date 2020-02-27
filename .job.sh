#!/bin/bash

JOB_NAME="data_clean"

sbatch -J $JOB_NAME \
    --time=00-00:30:00 \
    --nodes=1 \
    --ntasks=3 \
    --mem=4G \
    -o .${JOB_NAME}.out \
    -e .${JOB_NAME}.err \
    .${JOB_NAME}.sh
