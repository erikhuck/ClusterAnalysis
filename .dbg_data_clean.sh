#!/bin/bash

source env/bin/activate
pudb3 main.py --data-path raw_data/raw-data-set.csv --data-types-path raw_data/col-types.csv
