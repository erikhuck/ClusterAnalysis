source ../env/bin/activate

DATASET=$1
python3 main.py best-clustering --cohort adni --dataset $DATASET
