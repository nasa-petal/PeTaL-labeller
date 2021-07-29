'''
    xval_test.py

    Testing using cross-validation and multiple runs of MATCH.

    Run MATCH with PeTaL data.
    Last modified on 26 July 2021.

    Authors: Eric Kong (eric.l.kong@nasa.gov, erickongl@gmail.com)
'''

import click
import numpy as np
from collections import namedtuple
from ruamel.yaml import YAML
from pathlib import Path

from run_MATCH_with_PeTaL_data import run_MATCH_with_PeTaL_data

@click.command()
@click.option('--cnf', '-c', 'cnf_path', type=click.Path(exists=True), help='Path of configure yaml.')
@click.option('-k', type=click.INT, default=10, help='The k in k-fold cross-validation.')
@click.option('--study', '-s', default='golden_testing', help='Name of study, for logging purposes.')
@click.option('--verbose', '-v', type=click.BOOL, is_flag=True, default=False, help='Verbose output.')

def main(cnf_path,
        k=10,
        study='golden_testing',        
        verbose=False):
    """Command-line entry function
        - runs multiple trials of MATCH for cross-validation.

    Args:
        cnf_path (str): Path to configure yaml file.
        k (int): The k in k-fold cross-validation.
        study (str): Name of study, for logging purposes.
        verbose (bool): Verbose output.
    """

    yaml = YAML(typ='safe')
    cnf = yaml.load(Path(cnf_path))

    xval_test(cnf, k, study, verbose)
    # xval_test_ablations(cnf, k, study, verbose)

def xval_test(cnf,
        k=10,
        study='golden_testing',
        verbose=False):
    """Runs multiple trials of MATCH for cross-validation.

    Args:
        cnf (Dict): Python dictionary whose structure adheres to our config.yaml file.
        k (int): The k in k-fold cross-validation.
        study (str): Name of study, for logging purposes.
        verbose (bool): Verbose output.
    """

    # Determine amount of training examples to rotate for each fold.
    tot = cnf['split']['tot'] if 'tot' in cnf['split'] else 1000 # default
    skip_interval = int(tot / k)

    STUDY_TITLE = study
    for skip in range(0, skip_interval * k, skip_interval):
        cnf['split']['skip'] = skip
        print(f"```\n{STUDY_TITLE} skip={skip}\n")
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


def xval_test_ablations(cnf,
        k=10,
        study='golden_testing',
        verbose=False):
    """Runs multiple trials of MATCH for cross-validation.

    Args:
        cnf (Dict): Python dictionary whose structure adheres to our config.yaml file.
        k (int): The k in k-fold cross-validation.
        study (str): Name of study, for logging purposes.
        verbose (bool): Verbose output.
    """

    # Determine amount of training examples to rotate for each fold.
    tot = cnf['split']['tot'] if 'tot' in cnf['split'] else 1000 # default
    skip_interval = int(tot / k)

    AblateOptions = namedtuple("AblateOptions", "study mag mesh venue author reference text")
    ablations = [
        AblateOptions("all", True, True, True, True, True, True),
        AblateOptions("no_mag", False, True, True, True, True, True),
        AblateOptions("no_mesh", True, False, True, True, True, True),
        AblateOptions("no_venue", True, True, False, True, True, True),
        AblateOptions("no_author", True, True, True, False, True, True),
        AblateOptions("no_ref", True, True, True, True, False, True),
        AblateOptions("no_text", True, True, True, True, True, False),
        AblateOptions("only_mag", True, False, False, False, False, False),
        AblateOptions("only_mesh", False, True, False, False, False, False),
        AblateOptions("only_venue", False, False, True, False, False, False),
        AblateOptions("only_author", False, False, False, True, False, False),
        AblateOptions("only_ref", False, False, False, False, True, False),
        AblateOptions("only_text", False, False, False, False, False, True),
        AblateOptions("none", False, False, False, False, False, False),
    ]

    for ablation in ablations:
        STUDY_TITLE = f"{study}_{ablation.study}"
        cnf['transform']['use_mag'] = ablation.mag
        cnf['transform']['use_mesh'] = ablation.mesh
        cnf['transform']['use_venue'] = ablation.venue
        cnf['transform']['use_author'] = ablation.author
        cnf['transform']['use_reference'] = ablation.reference
        cnf['transform']['use_text'] = ablation.text
        for skip in range(0, skip_interval * k, skip_interval):
            cnf['split']['skip'] = skip
            print(f"```\n{STUDY_TITLE} skip={skip}\n")
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


def xval_test_by_size(cnf,
        k=10,
        study='golden_testing',
        verbose=False):
    """Runs multiple trials of MATCH for cross-validation.

    Args:
        cnf (Dict): Python dictionary whose structure adheres to our config.yaml file.
        k (int): The k in k-fold cross-validation.
        study (str): Name of study, for logging purposes.
        verbose (bool): Verbose output.
    """

    # Determine amount of training examples to rotate for each fold.
    tot = cnf['split']['tot'] if 'tot' in cnf['split'] else 1000 # default
    skip_interval = int(tot / k)

    for train_proportion in np.arange(0.2, 0.9, 0.1):
        STUDY_TITLE = f"{study}_{train_proportion:.1f}"
        cnf['split']['train'] = train_proportion
        for skip in range(0, skip_interval * k, skip_interval):
            cnf['split']['skip'] = skip
            print(f"```\n{STUDY_TITLE} skip={skip}\n")
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