'''
    xval_test.py

    Testing using cross-validation and multiple runs of MATCH.

    Run MATCH with PeTaL data.
    Last modified on 26 July 2021.

    Authors: Eric Kong (eric.l.kong@nasa.gov, erickongl@gmail.com)
'''

import click
import numpy as np
from ruamel.yaml import YAML
from pathlib import Path

from run_MATCH_with_PeTaL_data import run_MATCH_with_PeTaL_data

@click.command()
@click.option('--cnf', '-c', 'cnf_path', type=click.Path(exists=True), help='Path of configure yaml.')
@click.option('--verbose', '-v', type=click.BOOL, is_flag=True, default=False, help='Verbose output.')
@click.option('--study', '-s', default='golden_testing', help='Name of study, for logging purposes.')

def main(cnf_path,
        verbose=False,
        study='golden_testing'):
    """Command-line entry function
        - runs multiple trials of MATCH for cross-validation.

    Args:
        cnf_path (str): Path to configure yaml file.
        verbose (bool): Verbose output.
        study (str): Name of study, for logging purposes.
    """

    yaml = YAML(typ='safe')
    cnf = yaml.load(Path(cnf_path))

    xval_test(cnf, verbose, study)

def xval_test(cnf,
        verbose=False,
        study='golden_testing'):
    """Runs multiple trials of MATCH for cross-validation.

    Args:
        cnf (Dict): Python dictionary whose structure adheres to our config.yaml file.
        verbose (bool): Verbose output.
        study (str): Name of study, for logging purposes.
    """

    # Determine amount of training examples to rotate for each fold.
    tot = cnf['split']['tot'] if 'tot' in cnf['split'] else 1000 # default
    skip_interval = int(tot / 10)

    for train_proportion in np.arange(0.2, 0.9, 0.1):
        STUDY_TITLE = f"{study}_train_{train_proportion:.1f}"
        cnf['split']['train'] = train_proportion
        for skip in range(0, skip_interval * 10, skip_interval):
            print(f"```\n{STUDY_TITLE} skip={skip}\n")
            cnf['split']['skip'] = skip
            run_MATCH_with_PeTaL_data(
                cnf,
                verbose,
                do_split=True,
                do_transform=True,
                do_preprocess=True,
                do_train=True,
                do_eval=True
            )
            print("```\n")


if __name__ == '__main__':
    main()