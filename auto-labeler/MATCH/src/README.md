# MATCH/src

This directory contains the source files for running MATCH on PeTaL data.

This README was last updated on 21 July 2021.

## What are all these files?

In `auto-labeler/MATCH/src` you will find:
- `MATCH/`, our slightly modified version of the MATCH repository (https://github.com/yuzhimanhua/MATCH).
- `config.yaml`, a one-stop shop for all configuration variables in running MATCH with PeTaL.
- `README.md`, this self-referential document.
- `preprocess.py`, for running splitting (`Split.py`), transforming (`transform_data_PeTaL.py`), and MATCH preprocessing (`MATCH/preprocess.py.`).
- `Split.py`, for performing the train-dev-test split on the original dataset (e.g., `cleaned_lens_output.json`).
- `transform_data_PeTaL.py`, for transforming the training and testing `json` files into `txt` files of sequences of tokens.
- `train.py`, for training MATCH on the PeTaL training set (uses `MATCH/main.py`).
- `eval.py`, for evaluating MATCH's performance on the PeTaL testing set (uses `MATCH/main.py` and `MATCH/eval.py`).
- `run_MATCH_with_PeTaL_data`, for running the whole pipeline (or portions of it): `setup.py`, `preprocess.py`, `train.py`, `eval.py`.

## How do I reproduce your results?

It is recommended that you run this project in a conda environment (`venv`), set up as described in `../README.md`.

Run MATCH on PeTAL data with configuration options in `config.yaml`:

```
python run_MATCH_with_PeTaL_data.py --cnf config.yaml [--verbose]
```
with optional arguments for toggling on/off different phases:
- `--setup` or `-b` vs. `--no-setup` or `-B` for whether to do `setup.py` (i.e., download our version of MATCH using `gdown`). Defaults to true.
- `--split` or `-s` vs. `--no-split` or `-S` for whether to do `Split.py` (i.e., perform train-development-test split). Defaults to true.
- `--transform` or `-t` vs. `--no-transform` or `-T` for whether to do `transform_data_PeTaL.py` (i.e., transform `json` datasets into text (sequences of tokens) and label `txt` files). Defaults to true.
- `--preprocess` or `-p` vs. `--no-preprocess` or `-P` for whether to do `MATCH/preprocess.py` (i.e., tokenize and otherwise process the `txt` files into `npy` data). Defaults to true.
- `--train` or `-r` vs. `--no-train` or `-R` for whether to do `train.py` (i.e., run MATCH training on the PeTaL training set. Generally the longest-running task). Defaults to true.
- `--eval` or `-e` vs. `--no-eval` or `-E` for whether to do `eval.py` (i.e., run MATCH inference on the PeTaL testing set, and generate precision and nDCG scores on that test set). Defaults to true.
- `--verbose` or `-v` on whether to see logging output. Defaults to false.

If you want to tweak a config variable (e.g., train-dev-test split, or whether to use MAG/MeSH terms or not), you can find all of those options in `config.yaml`. Note that you can also use `-c` in place of `--cnf`.

### If you want to run certain steps individually.

Run train-dev-test split by itself:

```
python Split.py --prefix MATCH/PeTaL --dataset cleaned_lens_output.json [--train 0.8] [--dev 0.1] [--skip 0] [--verbose]
```

Run `transform_data_PeTaL` by itself to transform `json` into `txt`:

```
python transform_data.py --prefix MATCH --dataset PeTaL [--no-mag] [--no-mesh] [--no-venue] [--no-author] [--no-reference] [--no-text] [--verbose]
```

Run all preprocessing steps:

```
python preprocess.py --cnf config.yaml [--verbose]
```
with optional arguments for toggling on/off different phases:
- `--split` or `-s` vs. `--no-split` or `-S`- for doing `Split.py`
- `--transform` or `-t` vs. `--no-transform` or `-T` for doing `transform_data_PeTaL.py`.
- `--preprocess` or `-p` vs. `--no-preprocess` or `-P` for doing `MATCH/preprocess.py`.
Note that you can also use `-c` in place of `--cnf`.

Run training:

```
python train.py --cnf config.yaml [--verbose]
```
Note that you can also use `-c` in place of `--cnf`.

Run testing:

```
python eval.py --cnf config.yaml [--verbose]
```
Note that you can also use `-c` in place of `--cnf`.

## Current issues

- `wandb` usage is always on. I may turn this off sometime.

## Dependencies

- `click` for command-line magic. There may be a bit of `argparse` left in some files, but mostly we've moved to `click`.
- `wandb` for logging metrics on the Weights and Biases servers.
- `logging` for other logging.
- `gdown` for downloading from Google Drive.
- `json` for json data interpretation.
- `ruamel.yaml` for YAML config file interpretation.
- `os`, `sys`, `pathlib`, and other Python system-wrangling modules.

## Contact

For questions contact Eric Kong (eric.l.kong@nasa.gov, erickongl@gmail.com).
