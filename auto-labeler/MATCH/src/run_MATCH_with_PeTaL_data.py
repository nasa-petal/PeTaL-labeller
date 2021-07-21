'''
    run_MATCH_with_PeTaL_data.py

    Run MATCH with PeTaL data.
    Last modified on 14 July 2021.

    Authors: Eric Kong (eric.l.kong@nasa.gov, erickongl@gmail.com)
'''

import click
import logging

from preprocess import preprocess
from train import run_train
from eval import run_eval

@click.command()
@click.option('--cnf', type=click.Path(exists=True), help='Path of configure yaml.')
@click.option('--verbose', '-v', type=click.BOOL, is_flag=True, default=False, help='Verbose output.')
@click.option('--split/--no-split', '-s/-S', 'do_split', default=True, help='Perform train-dev-test split.')
@click.option('--transform/--no-transform', '-t/-T', 'do_transform', default=True, help='Perform transformation from json to text.')
@click.option('--preprocess/--no-preprocess', '-p/-P', 'do_preprocess', default=True, help='Perform preprocessing.')
@click.option('--train/--no-train', '-r/-R', 'do_train', default=True, help='Do training.')
@click.option('--eval/--no-eval', '-e/-E', 'do_eval', default=True, help='Do inference/evaluation.')

def main(cnf,
        verbose=False,
        do_split=True,
        do_transform=True,
        do_preprocess=True,
        do_train=True,
        do_eval=True):
    """Runs MATCH on PeTaL data.

    Args:
        cnf (str): Path to configure yaml file.
        verbose (bool): Verbose output.
        do_setup (bool): Whether to do preliminary setup (e.g., downloading MATCH).
        do_split (bool): Whether to perform train-dev-test split.
        do_transform (bool): Whether to transform json to txt.
        do_preprocess (bool): Whether to preprocess txt into npy.
        do_train (bool): Whether to do training.
        do_eval (bool): Whether to do inference/evaluation.
    """
    logging.basicConfig(
        level=logging.DEBUG,
        format="[%(asctime)s:%(name)s] %(message)s"
    )
    logger = logging.getLogger("train")

    if verbose:
        logger.info("Begin run_MATCH_with_PeTaL_data pipeline.")

    '''
        Preprocessing: Perform train-dev-test split,
        transform json to txt, and preprocess txt into npy
        in preprocess.py.
    '''
    preprocess(cnf, verbose, do_split, do_transform, do_preprocess)

    '''
        Training: Run training in train.py.
    '''
    if do_train:
        run_train(cnf, verbose)

    '''
        Evaluation: Run testing/inference/evaluation in eval.py.   
    '''
    if do_eval:
        run_eval(cnf, verbose)

    if verbose:
        logger.info("End run_MATCH_with_PeTaL_data pipeline.")


if __name__ == '__main__':
    main()
