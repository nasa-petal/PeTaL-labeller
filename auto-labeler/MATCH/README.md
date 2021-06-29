# MATCH on PeTaL Data

## What is this?

This directory contains work done for investigating the use of the MATCH (https://github.com/yuzhimanhua/MATCH) algorithm to classify Lens output data according to the PeTaL taxonomy.

This README was last updated on 28 June 2021.

## What are all these files?

- `experiment_data/` contains raw experiment logs for various sets of trials.
- `PeTaL` contains the Lens output dataset, including `cleaned_lens_output.json`, `taxonomy.txt`, and `Split.py`. Additionally, `emb_init.npy`, `labels_binarizer`, and `PeTaL.joint.emb` are the result of re-running embedding pre-training on the PeTaL data. The rest of the files are generated in the course of running the Jupyter notebooks, particularly `run_MATCH_with_PeTaL_data.ipynb`.
- `MATCH-PeTaL.yaml` is the model configuration file for training MATCH on PeTaL data.
- `PeTaL.yaml` is the dataset configuration file for training MATCH on PeTaL data.
- `prediction_metrics.ipynb`, in progress, is an attempt to compute various classification metrics (precision, recall, F1 score, confusion matrix) for MATCH run on the MAG-CS dataset.
- `README.md` is this (self-referential) document.
- `run_MATCH_with_PeTaL_data.ipynb` is a Jupyter notebook evaluating the performance of MATCH on PeTaL data.
- `run_MATCH.ipynb` is an earlier attempt to reproduce the MATCH algorithm's results in its Quick Start section.
- `transform_data_PeTaL.py` is a version of MATCH's `transform_data.py`, modified to use the PeTaL dataset instead.

## How do I reproduce your results?

- Step through `run_MATCH_with_PeTaL_data.ipynb`.

## Summary of results

In short, what I've found so far seems to indicate that:
- for the scale of our data in `PeTaL/cleaned_lens_output.json` (up to 1000 papers), dataset size matters a lot. This is encouraging.
- appending MAG fields of study and MeSH terms to text may help (at least does not hurt) accuracy.

Raw experiment logs for various sets of trials are found in `experiment_data`.

### Effect of training dataset size on MATCH precision.

Here are the results from my trials:

| Train set size | P@1=nDCG@1 | P@3 | P@5 | nDCG@3 | nDCG@5 |
| --- | --- | --- | --- | --- | --- |
| 200 | 0.324 | 0.249 | 0.203 | 0.269 | 0.274 |
| 300 | 0.424 | 0.337 | 0.275 | 0.362 | 0.364 |
| 400 | 0.441 | 0.344 | 0.278 | 0.373 | 0.373 |
| 500 | 0.547 | 0.419 | 0.328 | 0.454 | 0.447 |
| 600 | 0.534 | 0.433 | 0.345 | 0.464 | 0.463 |
| 700 | 0.555 | 0.434 | 0.342 | 0.466 | 0.472 |
| 800 | 0.627 | 0.509 | 0.390 | 0.542 | 0.543 |

Each training set size was run for 3 trials, whose statistics are averaged in the table above. All trials used 100 papers for validation and the rest of the papers for testing.

This is encouraging for our project, at least because it indicates that we can keep improving precision for roughly linear increase in training dataset size, and that we have not hit a plateau yet. 

### Effect of adding MAG fields of study and MeSH terms to text

I performed ablation studies to determine the effect of appending Microsoft Academic Graph (MAG) fields of study or Medical Subject Headings (MeSH) terms to the text. Here are the results from my first trials on June 23:

| Test set P@1 | without MeSH | with MeSH |
| --- | --- | --- |
| without MAG | 0.64 | 0.63 |
| with MAG | 0.61 | 0.67 |

Repeated with 10-fold cross-validation on June 28:

| Train set options | P@1=nDCG@1 | P@3 | P@5 | nDCG@3 | nDCG@5 |
| --- | --- | --- | --- | --- | --- |
| with_mag, with_mesh | 0.590 ± 0.040 | 0.457 ± 0.030 | 0.369 ± 0.025 | 0.495 ± 0.032 | 0.493 ± 0.035 |
| with_mag, no_mesh | 0.583 ± 0.032 | 0.477 ± 0.035 | 0.378 ± 0.029 | 0.508 ± 0.033 | 0.506 ± 0.036 |
| no_mag, with_mesh | 0.573 ± 0.056 | 0.455 ± 0.029 | 0.362 ± 0.034 | 0.488 ± 0.034 | 0.485 ± 0.040 |
| no_mag, no_mesh | 0.569 ± 0.036 | 0.475 ± 0.028 | 0.373 ± 0.026 | 0.504 ± 0.029 | 0.498 ± 0.030 |

Results are **inconclusive**, and I suspect the differences between these trials may not be statistically significant, but adding MeSH terms and MAG fields does not hurt accuracy, nor does it hurt performance (i.e., speed). All trials took roughly 12 minutes to run 1000 epochs on the dataset of 1000 papers (800 training, 100 validation, 100 test).

## Future work

- Write Makefile to streamline instructions for reproducing this work.
  - Add CLI options for `PeTaL/Split.py`, `transform_data_PeTaL.py`
- Migrate code from Jupyter notebooks to python source files.
- Integrate this work with the rest of the PeTaL pipeline.
- Look into relevancy threshold vs. top k for labelling (https://github.com/nasa-petal/PeTaL-labeller/issues/55)
- Compare to auto-sklearn (https://github.com/nasa-petal/PeTaL-labeller/issues/56)