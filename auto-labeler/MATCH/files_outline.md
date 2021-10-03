# Files Outline

What are all these files? How is MATCH structured? This markdown file attempts to diagram all that.

## How is MATCH structured?

In `PeTaL-Labeller/auto-labeler/MATCH` we find the following file structure:

- analysis
  - analysis scripts
- experiment_data
  - xval_test
    - logs from cross-validation runs
  - results
    - markdown-formatted tables for analysis/perf_plots.py
  - abbr_output_* (earlier logs)
- notebooks
  - Notebooks (from Google Colab development, mostly obsolete)
- plots
  - YYYYMMDD_* (directories of plots)
- reports
  - figures
  - results_up_to_* (previous results writeups)
- src (main directory of development)
  - MATCH (the authors' MATCH repository)
    - configure (configuration files from the MATCH authors)
      - datasets
        - PeTaL.yaml (and others)
      - models
        - MATCH-PeTaL.yaml (and others)
    - deepxml
      - python files for the model that the authors adapted from somewhere else (CorNet)
    - joint
      - bin
      - eigen-3.3.3 (you'll need to download if you want to run embedding pretraining)
      - gsl (you'll need to download if you want to run embedding pretraining)
      - src
        - C++ files for building the context graph for embedding pretraining
      - Makefile
      - run.sh
      - Preprocess_golden.py
    - PeTaL (THE DIRECTORY WITH OUR DATASET - you'll download using setup.py)
      - models
        - MATCH-PeTaL (the model weights)
      - results (generated when you run src/eval.py)
        - MATCH-PeTaL-labels.npy (labels for each paper in test set)
        - MATCH-PeTaL-scores.npy (scores for each label)
      - {dev|train|test}.json (result of running src/Split.py)
      - emb_init.npy, vocab.npy, labels_binarizer (result of running src/preprocess.py)
      - filtered.json (result of running src/filter.py)
      - golden.json 
      - PeTaL.joint.emb (result of running src/MATCH/joint/run.sh)
      - taxonomy.txt
      - {train|test}_{texts|labels}.txt (result of running src/transform_data_golden.py)
      - {train|test}_{texts|labels}.npy (result of running src/preprocess.py)
  - augment.py
  - config.yaml
  - eval.py
  - filter.py
  - infer_config.yaml
  - preprocess.py
  - run_inference.sh
  - run_MATCH_with_PeTaL_data.py
  - Split.py
  - train.py
  - transform_data_golden.py
  - utils.py
  - xval_test.py

# What files are generated at each step?

All files get generated in `src/MATCH/PeTaL`

- setup.py
  - filtered.json
  - golden.json
  - PeTaL.joint.emb
  - taxonomy.txt

- Split.py
  - train.json
  - dev.json
  - test.json

- augment.py
  - (just modifies train.json)

- transform_data_golden.py
  - train_labels.txt
  - train_texts.txt
  - test_labels.txt
  - test_texts.txt

- preprocess.py
  - train_labels.npy
  - train_texts.npy
  - test_labels.npy
  - test_texts.npy
  - emb_init.npy
  - labels_binarizer
  - vocab.npy

- train.py
  - models

- eval.py
  - results


    





