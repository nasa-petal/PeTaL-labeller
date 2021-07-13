# MATCH/py

This directory contains the source files for running MATCH on PeTaL data.

This README was last updated on 13 July 2021.

## How do I reproduce your results?

This project is run in an Anaconda environment, specified in `match-env.yml`. In order to run it, first recreate the environment:

```
conda env create -n match-env -f match-env.yml
```



## Future work

- Migrate code from Jupyter notebooks to python source files.
- Integrate this work with the rest of the PeTaL pipeline.
- Compare to auto-sklearn (https://github.com/nasa-petal/PeTaL-labeller/issues/56)
- Use flat taxonomy and/or taxonomy with labels with less than 10 instances removed (https://github.com/nasa-petal/PeTaL-labeller/issues/60)

