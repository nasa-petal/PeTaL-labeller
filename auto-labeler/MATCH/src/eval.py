'''
    eval.py

    Run MATCH with PeTaL data.
    Last modified on 14 July 2021.

    Authors: Eric Kong (eric.l.kong@nasa.gov, erickongl@gmail.com)
'''

import click
import sys
import os
import logging

from ruamel.yaml import YAML
from pathlib import Path

@click.command()
@click.option('--cnf', '-c', 'cnf_path', type=click.Path(exists=True), help='Path of configure yaml.')
@click.option('--verbose', '-v', type=click.BOOL, is_flag=True, default=False, help='Verbose output.')

def main(cnf_path, verbose):
    """
        Command-line entry function - runs testing.

    Args:
        cnf (str): Path to configure yaml file.
        verbose (bool): Verbose output.
    """

    yaml = YAML(typ='safe')
    cnf = yaml.load(Path(cnf_path))

    run_eval(cnf, verbose)

def run_eval(cnf, verbose):
    """
        Run testing.

    Args:
        cnf (Dict): Python dictionary whose structure adheres to our config.yaml file.
        verbose (bool): Verbose output.
    """
    logging.basicConfig(
        level=logging.DEBUG,
        format="[%(asctime)s:%(name)s] %(message)s"
    )
    logger = logging.getLogger("eval")

    if verbose:
        logger.info("Begin evaluation.")

    MODEL = cnf['model']
    DATASET = cnf['dataset']
    train_cnf = cnf['train']

    sys.path.insert(1, os.path.join(os.getcwd(), 'MATCH'))

    os.chdir(train_cnf['prefix'])

    from MATCH.main import main as match_main # main.py
    from MATCH.evaluation import main as evaluation_main # evaluation.py

    match_main.callback(
        data_cnf=f"configure/datasets/{DATASET}.yaml",
        model_cnf=f"configure/models/{MODEL}-{DATASET}.yaml",
        mode="eval",
        reg=0
    )

    evaluation_main.callback(
        results=f"{DATASET}/results/{MODEL}-{DATASET}-labels.npy",
        targets=f"{DATASET}/test_labels.npy",
        train_labels=f"{DATASET}/train_labels.npy"
    )

    os.chdir("..")

    if verbose:
        logger.info("End evaluation.")

if __name__ == '__main__':
    main()

########################################
#
#   FOR HISTORICAL REFERENCE
#
#   (nothing yet for eval.py)
#
########################################