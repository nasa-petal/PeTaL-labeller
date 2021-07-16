# MATCH/experiment_data

## What is this?

This directory contains raw results from investigating the use of the MATCH (https://github.com/yuzhimanhua/MATCH) algorithm to classify PeTaL data according to the PeTaL taxonomy.

This README was last updated on 16 July 2021.

## What are all these files?

- `abbr_output_*.md` contains abbreviated experiment logs for various sets of trials.
- `abbreviate_MATCH_output.py` takes a raw experiment output and abbreviates it.
- `analyse_MATCH_output.py` takes an experiment output (raw or abbreviated) and returns a markdown table of statistics.
- `README.md` is this (self-referential) document.

A few other files in nonstandard formats from previous logging (by hand) are also here.

## How do I summarise a log?

Suppose you have a log, `ablations_20210716.md`. Then you may run

```
python3 analyse_MATCH_output.py -f ablations_20210716.md
```

Alternatively, in order to abbreviate it before running, you can use

```
python3 abbreviate_MATCH_output.py -i ablations_20210716.md -o abbr_output_20210716.md
python3 analyse_MATCH_output.py -f abbr_output_20210716.md
```

You should get a table in ssstandard output, which, when rendered in markdown, looks like this.

| Train set options | P@1=nDCG@1 | P@3 | P@5 | nDCG@3 | nDCG@5 |
| --- | --- | --- | --- | --- | --- |
| with_mag, with_mesh | 0.590 ± 0.040 | 0.457 ± 0.030 | 0.369 ± 0.025 | 0.495 ± 0.032 | 0.493 ± 0.035 |
| with_mag, no_mesh | 0.583 ± 0.032 | 0.477 ± 0.035 | 0.378 ± 0.029 | 0.508 ± 0.033 | 0.506 ± 0.036 |
| no_mag, with_mesh | 0.573 ± 0.056 | 0.455 ± 0.029 | 0.362 ± 0.034 | 0.488 ± 0.034 | 0.485 ± 0.040 |
| no_mag, no_mesh | 0.569 ± 0.036 | 0.475 ± 0.028 | 0.373 ± 0.026 | 0.504 ± 0.029 | 0.498 ± 0.030 |

For reasons of space, only the abbreviated versions should be saved in this repository. To access the original versions, see the Contact section below.

## Future work

- Standardise data formats.

## Contact

For questions contact Eric Kong (eric.l.kong@nasa.gov, erickongl@gmail.com).