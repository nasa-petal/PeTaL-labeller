#!/bin/sh

dataset=$1
json_file=$2

python Preprocess_golden.py --dataset $dataset --json-file $json_file
# python Preprocess_PeTaL.py --dataset $dataset

# unzip eigen-3.3.3.zip
# make
threads=16 # number of threads for training
negative=5 # number of negative samples
alpha=0.04 # initial learning rate
sample=5000 # number of training samples (Million)
type=7 # number of edge types
dim=100

word_file="left.dat"
node_file="right.dat"
link_file="network.dat"
emb_file="$dataset/petal.joint.emb"
  
./bin/jointemb -words ${word_file} -nodes ${node_file} -hin ${link_file} -output ${emb_file} -binary 0 -type ${type} -size ${dim} -negative ${negative} -samples ${sample} -alpha ${alpha} -threads ${threads}

