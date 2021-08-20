'''
    xval_test.py

    Testing using cross-validation and multiple runs of MATCH.

    Run MATCH with PeTaL data.
    Last modified on 18 August 2021.

    DESCRIPTION

        xval_test.py performs cross-validation: it runs the entire 
        MATCH-PeTaL pipeline on different folds of the PeTaL dataset.

        At the end it will produce output in stdout
        which you ought to redirect to log files.
        Each of the entries in this output is
        surrounded by triple-backticks like this:

            ```
            TRAIN_SET_OPTIONS skip=N
            ...
            (STUFF)
            ...
            Precision@1,3,5: 0.7413793103448276 0.5718390804597702 0.4396551724137931
            nDCG@1,3,5: 0.7413793103448276 0.6131173000787031 0.6022903445480057
            ```
            

            ```
            TRAIN_SET_OPTIONS skip=N
            ...
            (STUFF)
            ...
            Precision@1,3,5: 0.7105263157894737 0.5847953216374269 0.41228070175438597
            nDCG@1,3,5: 0.7105263157894737 0.6381949983173864 0.606931235522187
            ```        

        These log files can then be analysed for statistics using
        analysis/analyse_MATCH_output.py.

    OPTIONS
    
        -c, --cnf
            Path to configure yaml.
        -k
            The k in k-fold cross-validation. The number of times to run
            the MATCH-PeTaL pipeline, the dataset partitioned differently
            each time.
            Defaults to 10.
        -s, --study
            Name of study, for logging purposes.
            Defaults to golden_testing.
        -v, --verbose
            Enable verbose output.
            Defaults to False.
        -m, --mode
            Special suites of tests to run, hard-coded:
            - size
                Tests which vary the training size.
            - ablation
                Tests which add/remove classes of metadata tokens
                one by one
            - augment
                Tests which vary the augmentation factor.
            - none
                Just run one suite of k trials.
            Defaults to none.

    USAGE

        python3 xval_test.py -c config.yaml --k 10 -s STUDY_NAME --verbose

    or in context, you'll want to save its output to a log file:

        python3 xval_test.py -c config.yaml --k 10 -s STUDY_NAME --verbose | tee -a LOG_FILE_NAME

    after which you can analyze the log file using

        python3 ../analysis/analyse_MATCH_output.py -f LOG_FILE_NAME

    NOTES

        Generally with the current settings, a trial takes 3-6 minutes,
        so xval_test.py may take 30-60 minutes to complete.

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
@click.option('--mode', '-m', type=click.Choice(['none', 'size', 'ablation', 'augment']), default='none', help='Suite of tests to run.')

def main(cnf_path,
        k=10,
        study='golden_testing',        
        verbose=False,
        mode='none'):
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

    if mode == 'size':
        xval_test_by_size(cnf, k, study, verbose)
    elif mode == 'ablation':
        xval_test_ablations(cnf, k, study, verbose)
    elif mode == 'augment':
        xval_test_augment(cnf, k, study, verbose)
    else:
        xval_test(cnf, k, study, verbose)

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

    for train_proportion in np.linspace(0.05, 0.85, 17):
    # for train_proportion in [0.02, 0.04, 0.07, 0.1, 0.2, 0.4, 0.7]: # np.linspace(0.1, 0.8, 8):
        # STUDY_TITLE = f"{study}_{train_proportion:.2f}"
        STUDY_TITLE = f"{study}_{int(train_proportion * tot)}"
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


def xval_test_augment(cnf,
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

    for aug_factor in range(1, 6):
        STUDY_TITLE = f"{study}_{aug_factor}"
        cnf['augment']['num_aug'] = aug_factor
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