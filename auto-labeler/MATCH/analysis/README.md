# MATCH on PeTaL Data - Analysis

## What is this?

This directory contains work done for analysing the performance of the MATCH (https://github.com/yuzhimanhua/MATCH) algorithm to classify PeTaL data according to the PeTaL taxonomy.

This README was last updated on 19 August 2021.

## What are all these files?

- `abbreviate_MATCH_output.py` takes output from several runs of MATCH and abbreviates it.
- `analyse_MATCH_output.py` takes output from several runs of MATCH, each delimited by an opening triple-backtick and a closing triple-backtick and performs statistics on them.
- `count_terms_in_w2v.py` counts the number of unique terms of each type (author, references, etc.) in a w2v file (e.g., `PeTaL.joint.emb`).
- `count_terms.py` counts the number of unique terms of each type (author, references, etc.) in a file.
- `ideal_MCM.py` produces idealized multilabel confusion matrices.
- `multilabel_confusion_matrix.py` produces multilabel confusion matrices.
- `perf_plots.py` produces matplotlib plots from a results folder.
- `precision_and_recall.py` produces plots of precision, recall, and F1 score.
- `README.md` is this (self-referential) document.

## How do I use them?

Note that each script has detailed instructions in its opening comment.

### abbreviate_MATCH_output.py

`abbreviate_MATCH_output.py` takes an input file with `-i` and an output file with `-o`

```
    python3 abbreviate_MATCH_output.py -i LOG_FILE_NAME -o ABBR_LOG_FILE_NAME
```

or in conjunction with `analyse_MATCH_output.py`:

```
    python3 abbreviate_MATCH_output.py -i LOG_FILE_NAME -o ABBR_LOG_FILE_NAME
    python3 analyse_MATCH_output.py -f ABBR_LOG_FILE_NAME
```

### analyse_MATCH_output.py

`analyse_MATCH_output.py` takes an input file with `-f`

```
    python3 analyse_MATCH_output.py -f LOG_FILE_NAME
```

or in context, if you want to strip out the boring bits of the log file before you save it (you don't have to do this)

```
    python3 abbreviate_MATCH_output.py -i LOG_FILE_NAME -o ABBR_LOG_FILE_NAME
    python3 analyse_MATCH_output.py -f ABBR_LOG_FILE_NAME
```

### count_terms_in_w2v.py

`count_terms_in_w2v.py` takes an input file with `-f`

```
    python3 count_terms_in_w2v.py -f PATH/TO/PeTaL.joint.emb
```

### count_terms.py

`count_terms.py` takes an input file with `-f`

```
    python3 count_terms.py -f PATH/TO/TRAIN_TEXTS.txt
```

### ideal_MCM.py

`ideal_MCM.py` takes a path to the MATCH directory with `-m` and outputs plots in a `plots` directory with `-p`.

```
    python3 ideal_MCM.py -m ../src/MATCH -p ../plots [--verbose]
```

### multilabel_confusion_matrix.py

`multilabel_confusion_matrix.py` takes a path to the MATCH directory with `-m` and outputs plots in a `plots` directory with `-p`.

```
    python3 multilabel_confusion_matrix.py -m ../src/MATCH -p ../plots [--verbose] [--threshold 0.1]
```

### perf_plots.py

`perf_plots.py` takes a path to the results directory with `-r` and outputs plots in a `plots` directory with `-p`.

```
    python3 perf_plots.py -r ../experiment_data/results -p ../plots --verbose
```

### precision_and_recall.py

`precision_and_recall.py` takes a path to the MATCH directory with `-m` and outputs plots in a `plots` directory with `-p`.

```
    python3 precision_and_recall.py -m ../src/MATCH -p ../plots [--verbose]
```

## Future work

- Investigate using just the most common subset of labels (https://github.com/nasa-petal/PeTaL-labeller/issues/69, https://github.com/nasa-petal/PeTaL-labeller/issues/70) to see if MATCH does better on that.

## Contact

For questions contact Eric Kong (eric.l.kong@nasa.gov, erickongl@gmail.com).