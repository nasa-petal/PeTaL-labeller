'''
    xval_test.py

    Testing using cross-validation and multiple runs of MATCH.

    Run MATCH with PeTaL data.
    Last modified on 26 July 2021.

    Authors: Eric Kong (eric.l.kong@nasa.gov, erickongl@gmail.com)
'''

import click
import logging
from ruamel.yaml import YAML
from pathlib import Path

from run_MATCH_with_PeTaL_data import run_MATCH_with_PeTaL_data

@click.command()
@click.option('--cnf', '-c', 'cnf_path', type=click.Path(exists=True), help='Path of configure yaml.')
@click.option('--verbose', '-v', type=click.BOOL, is_flag=True, default=False, help='Verbose output.')

def main(cnf_path,
        verbose=False):
    """Command-line entry function
        - runs multiple trials of MATCH for cross-validation.

    Args:
        cnf_path (str): Path to configure yaml file.
        verbose (bool): Verbose output.
    """

    yaml = YAML(typ='safe')
    cnf = yaml.load(Path(cnf_path))

    xval_test(cnf, verbose)

def xval_test(cnf,
        verbose=False):
    """Runs multiple trials of MATCH for cross-validation.

    Args:
        cnf (Dict): Python dictionary whose structure adheres to our config.yaml file.
        verbose (bool): Verbose output.
    """
    STUDY_TITLE = "golden_testing"
    for skip in range(0, 1160, 116):
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