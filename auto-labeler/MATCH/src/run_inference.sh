#!/usr/bin/env bash

########################################
# 
# ./run_inference.sh
#   takes one argument
#   and that is a path of the dataset on which to run inference.
#   This path must conform to the golden dataset schema.
#
#   For example, you would run the following command in bash
#
#       ./run_inference MATCH/PeTaL/golden.json
#
#   The predictions, as well as their confidence scores
#   are to be found in
#     $MODEL/$DATASET/results/$MODEL-$DATASET-labels.npy
#     $MODEL/$DATASET/results/$MODEL-$DATASET-scores.npy
#   that is to say,
#     MATCH/PeTaL/results/MATCH-PeTaL-labels.npy
#     MATCH/PeTaL/results/MATCH-PeTaL-scores.npy
#
########################################

DATASET=PeTaL
MODEL=MATCH

echo "run_inference.sh: Copying $1 to $MODEL/$DATASET/infer.json"
cp $1 infer.json
mv infer.json $MODEL/$DATASET

echo "run_inference.sh: Running MATCH in inference mode on $MODEL/$DATASET/infer.json"
PYTHONFAULTHANDLER=1 python3 run_MATCH_with_PeTaL_data.py --infer-mode --cnf infer_config.yaml --verbose