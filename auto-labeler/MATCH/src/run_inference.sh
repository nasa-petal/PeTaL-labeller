#!/usr/bin/env bash

DATASET=PeTaL
MODEL=MATCH

echo "run_inference.sh: Copying $1 to $MODEL/$DATASET/infer.json"
cp $1 infer.json
mv infer.json $MODEL/$DATASET

echo "run_inference.sh: Running MATCH in inference mode on $MODEL/$DATASET/infer.json"
PYTHONFAULTHANDLER=1 python3 run_MATCH_with_PeTaL_data.py --infer-mode --cnf infer_config.yaml --verbose