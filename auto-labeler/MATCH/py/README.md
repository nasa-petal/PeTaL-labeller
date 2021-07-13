# MATCH/py

This directory contains the source files for running MATCH on PeTaL data.

This README was last updated on 13 July 2021.

## How do I reproduce your results?

It is recommended that you run this project in a python virtual environment ('venv'). We have provided one in `match-env/`.

Install requirements:

```
pip install -r requirements.txt.
```

Run MATCH on PeTAL data with configuration options in `config.yaml`:

```
python run_MATCH_with_PeTaL_data.py --cnf config.yaml
```



