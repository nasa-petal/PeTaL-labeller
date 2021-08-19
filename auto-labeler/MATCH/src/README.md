# MATCH/src

## Links

- [What is this?](#intro)
- [What are all these files?](#files)
- [How do I reproduce your results?](#results)
- [How do I tweak hyperparameters and other configurables?](#config)
- [Current issues](#issues)
- [Dependencies](#dependencies)
- [Contact](#contact)

## <a name='intro'></a> What is this?

This directory contains the source files for running MATCH on PeTaL data.

This README was last updated on 9 August 2021.

## <a name='files'></a> What are all these files?

In `auto-labeler/MATCH/src` you will find:
- `MATCH/`, our slightly modified version of the MATCH repository (https://github.com/yuzhimanhua/MATCH).
- `config.yaml`, a one-stop shop for all configuration variables in running MATCH with PeTaL.
- `README.md`, this self-referential document.
- `preprocess.py`, for running splitting (`Split.py`), transforming (`transform_data_golden.py`), and MATCH preprocessing (`MATCH/preprocess.py.`).
- `Split.py`, for performing the train-dev-test split on the original dataset (e.g., `cleaned_lens_output.json`).
- `augment.py`, for performing data augmentation on the training dataset (e.g., `MATCH/PeTaL/train.json`).
- `transform_data_golden.py`, for transforming the training and testing `json` files into `txt` files of sequences of tokens.
- `transform_data_PeTaL.py`, now obsolete, retired in favour of `transform_data_golden.py`.
- `train.py`, for training MATCH on the PeTaL training set (uses `MATCH/main.py`).
- `eval.py`, for evaluating MATCH's performance on the PeTaL testing set (uses `MATCH/main.py` and `MATCH/eval.py`).
- `run_MATCH_with_PeTaL_data`, for running the whole pipeline (or portions of it): `setup.py`, `preprocess.py`, `train.py`, `eval.py`.
- `utils.py`, for common functions that the other `*.py` files share.
- `xval_test.py` for running the whole pipeline multiple times with different folds for cross-validation.

**Every source file includes detailed instructions on what its code does and how to run it. Additionally, we describe all existing `config.yaml` options [here].**

## <a name='results'></a> How do I reproduce your results?

It is recommended that you run this project in a conda environment (`venv`), set up as described in `../README.md`.

Run MATCH on PeTAL data with configuration options in `config.yaml`:

```
python run_MATCH_with_PeTaL_data.py --cnf config.yaml [--infer-mode] [--verbose]
```
with optional arguments for toggling on/off different phases:
- `--split` or `-s` vs. `--no-split` or `-S` for whether to do `Split.py` (i.e., perform train-development-test split). Defaults to true.
- `--transform` or `-t` vs. `--no-transform` or `-T` for whether to do `transform_data_PeTaL.py` (i.e., transform `json` datasets into text (sequences of tokens) and label `txt` files). Defaults to true.
- `--augment` or `-a` vs. `--no-augment` or `-A` for whether to do `augment.py` (i.e., perform data augmentation on the training dataset). Defaults to true.
- `--preprocess` or `-p` vs. `--no-preprocess` or `-P` for whether to do `MATCH/preprocess.py` (i.e., tokenize and otherwise process the `txt` files into `npy` data). Defaults to true.
- `--train` or `-r` vs. `--no-train` or `-R` for whether to do `train.py` (i.e., run MATCH training on the PeTaL training set. Generally the longest-running task). Defaults to true.
- `--eval` or `-e` vs. `--no-eval` or `-E` for whether to do `eval.py` (i.e., run MATCH inference on the PeTaL testing set, and generate precision and nDCG scores on that test set). Defaults to true.
- `--verbose` or `-v` on whether to see logging output. Defaults to false.
- `--remake-vocab-file` forces the vocabulary and initial embedding files `vocab.npy` and `emb_init.npy` to be deleted and recomputed. This is a helpful option if you are adding or removing vocabulary or classes of metadata to the dataset. Defaults to false.

If you want to tweak a config variable (e.g., train-dev-test split, or whether to use MAG/MeSH terms or not), you can find all of those options in `config.yaml`. Note that you can also use `-c` in place of `--cnf`. Flag `-i` or `--infer-mode` specifies that _inference mode_ should be used (which produces only `test_*` files, no `train_*` files and does not run training, only evaluation).

### If you want to run certain steps individually.

Run train-dev-test split by itself:

```
python Split.py --prefix MATCH/PeTaL --dataset cleaned_lens_output.json [--train 0.8] [--dev 0.1] [--skip 0] [--infer-mode] [--verbose]
```

Run data augmentation by itself:

```
python3 augment.py --dataset-path MATCH/PeTaL/train.json [--factor 5] [--balance-aware] [--verbose]
```

Run `transform_data_golden` by itself to transform `json` into `txt`:

```
python transform_data_golden.py --prefix MATCH --dataset PeTaL [--no-mag] [--no-mesh] [--no-venue] [--no-author] [--no-reference] [--no-text] [--no-title] [--no-abstract] [--no-level1] [--no-level2] [--no-level3] [--include-labels-in-features] [--infer-mode] [--verbose]
```

Run all preprocessing steps:

```
python preprocess.py --cnf config.yaml [--infer-mode] [--verbose]
```
with optional arguments for toggling on/off different phases:
- `--split` or `-s` vs. `--no-split` or `-S`- for doing `Split.py`
- `--transform` or `-t` vs. `--no-transform` or `-T` for doing `transform_data_PeTaL.py`.
- `--augment` or `-a` vs. `--no-augment` or `-A` for whether to do `augment.py`.
- `--preprocess` or `-p` vs. `--no-preprocess` or `-P` for doing `MATCH/preprocess.py`.
- `--remake-vocab-file` forces the vocabulary and initial embedding files `vocab.npy` and `emb_init.npy` to be deleted and recomputed. This is a helpful option if you are adding or removing vocabulary or classes of metadata to the dataset. Defaults to false.
- Option `-c` or `--cnf` identifies the configuration file, by default `config.yaml`.
- Flag `-i` or `--infer-mode` specifies that _inference mode_ should be used (which produces only `test_*` files, no `train_*` files).

Run training:

```
python train.py --cnf config.yaml [--infer-mode] [--verbose]
```
- Option `-c` or `--cnf` identifies the configuration file, by default `config.yaml`.
- Flag `-i` or `--infer-mode` specifies that _inference mode_ should be used (skipping this training step).

Run testing:

```
python eval.py --cnf config.yaml [--infer-mode] [--verbose]
```
- Option `-c` or `--cnf` identifies the configuration file, by default `config.yaml`.
- Flag `-i` or `--infer-mode` specifies that _inference mode_ should be used (no effect on eval.py).

Run multiple trials for cross-validation:

```
python xval_test.py --cnf config.yaml -k N --study STUDY_NAME [--mode MODE] [--verbose]
```
- Option `k` is the *k* in *k*-fold cross-validation -- how many folds to split the dataset into for validation and testing purposes.
- Option `-s` or `--study` is the study name -- the string that identifies this set of runs in the output of `../analysis/analyse_MATCH_output.py`.
- Option `-c` or `--cnf` identifies the configuration file, by default `config.yaml`.
- Option `-m` or `--mode` indicates the type of analysis to perform. Choices are `none`, `ablation` for testing the effect of removing various metadata, `size` for testing the effect of training set size, and `augment` for testing the effect of data augmentation. Defaults to `none`.

You can redirect output to a file that `../analysis/analyse_MATCH_output.py` can read by appending `| tee -a experiment_data/xval_test/[FILENAME.py]` to your command.

## <a name='config'></a> How do I tweak hyperparameters and other configurables?

The main configurations file is `config.yaml`. You may either modify it directly, or create a copy, e.g., `new_config.yaml`, and run

```
python3 run_MATCH_with_PeTaL_data.py --cnf new_config.yaml [--verbose]
```

Also note that `infer_config.yaml` is a slightly modified version of `config.yaml` used for inference mode.

Other tweakable hyperparameters, those to do with the internals of MATCH itself, may be found in `MATCH/configure/datasets/PeTaL.yaml` and `MATCH/configure/models/MATCH-PeTaL.yaml`.

The following are parameters which may be tweaked:

- `model` name of model (`MATCH`)
- `dataset` name of dataset (`PeTaL`)
- `split`
  - `prefix` file path prefix where `Split.py` will be working with files (`MATCH/PeTaL`)
  - `dataset` name of dataset json file
  - `train` proportion, between 0 and 1, of papers in the dataset used for training
  - `dev` proportion, between 0 and 1, of papers in the dataset used for validation
  - `skip` number of papers by which to rotate the dataset, to allow slicing into different folds for cross-validation
  - `tot` total number of papers in dataset to consider. If `0`, use all of the papers; if `N` for `N > 0`, use the first `N` papers.
- `augment`
  - `prefix` file path prefix where `augment.py` will be working with files (`MATCH/PeTaL`)
  - `factor` augmentation factor `N` such that each paper in the dataset has `N - 1` perturbed copies added to the dataset. `1` to ignore data augmentation.
  - `balance_aware` whether to augment papers more or less depending on how rare their labels are
  - `alpha` free-standing parameter in balance-aware data augmentation
  - `beta` free-standing parameter in balance-aware data augmentation
- `transform`
  - `prefix` file path prefix where `transform_data_golden.py` will be working with files (`MATCH`)
  - `dataset` name of dataset (`PeTaL`)
  - `use_mag` whether to include MAG field of study tokens in token sequences
  - `use_mesh` whether to include MeSH term tokens in token sequences
  - `use_venue` whether to include venue tokens in token sequences
  - `use_author` whether to include author tokens in token sequences
  - `use_reference` whether to include reference tokens (other paper IDs) in token sequences
  - `use_text` whether to include text tokens (title and abstract) in token sequences
  - `use_title` whether to include title tokens in token sequences
  - `use_abstract` whether to include abstract tokens in token sequences
  - `use_level1` whether to include Level 1 labels in target
  - `use_level2` whether to include Level 2 labels in target
  - `use_level3` whether to include Level 3 labels in target
  - `include_labels_in_features` whether to include the labels themselves in the token sequences. Generally only for sanity-checking purposes
- `preprocess`
  - `prefix` file path prefix where `preprocess.py` will be working with files (`MATCH`)
  - `vocab_size` maximum size of vocabulary
  - `max_len` maximum length of a sequence in tokens
- `train`
  - `prefix` file path prefix where `train.py` will be working with files (`MATCH`)
  - `sample` whether to print a sample of texts to standard output before training
  - `num_samples` how many papers to print out
  - `hypernymy_regularization` whether to add hypernymy regularization terms to the loss function (generally a good idea if your taxonomy is a hierarchy)
  - `leaf_labels_only` whether to train on leaf labels only (generally not)
  - `notes` any notes for wandb (generally no)
- `eval`
  - `prefix` file path prefix where `eval.py` will be working with files (`MATCH`)
  - `sample` whether to print a sample of texts and their predictions during evaluation
  - `num_samples` how many papers to print out
  - `criterion` whether to print, for each paper, the top *k* predictions (`top_k`) or the predictions whose confidence scores exceed a threshold (`threshold`)
  - `top_k` the *k* for criterion `top_k`
  - `threshold` the threshold for criterion `threshold`
  - `num_text_tokens` how many text tokens by which to identify the paper
- `wandb`
  - `project` name of project for wandb logging purposes
  - `group` name of experiment group for wandb logging purposes

## <a name='issues'></a> Current issues

- `wandb` usage is always on. I may turn this off sometime.

## <a name='dependencies'></a> Dependencies

- `click` for command-line magic. There may be a bit of `argparse` left in some files, but mostly we've moved to `click`.
- `wandb` for logging metrics on the Weights and Biases servers.
- `logging` for other logging.
- `gdown` for downloading from Google Drive.
- `json` for json data interpretation.
- `ruamel.yaml` for YAML config file interpretation.
- `nlpaug` and `nltk` for text data augmentation.
- `os`, `sys`, `pathlib`, and other Python system-wrangling modules.

## <a name='contact'></a> Contact

For questions contact Eric Kong (eric.l.kong@nasa.gov, erickongl@gmail.com).
