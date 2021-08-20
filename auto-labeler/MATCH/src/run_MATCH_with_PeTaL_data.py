'''
    run_MATCH_with_PeTaL_data.py

    Run MATCH with PeTaL data.
    Last modified on 18 August 2021.

    DESCRIPTION

        preprocess.py runs the entire preprocessing, training, and testing
        pipeline:
        - preprocess.py, which runs
            - Split.py
            - augment.py
            - transform_data_golden.py
        - train.py
        - eval.py

        It begins with

        - MATCH/
          - PeTaL/
            - filtered.json
            - PeTaL.joint.emb
            - taxonomy.txt

        and ends up with a lot. The model and results are in these directories:

        - MATCH/
          - PeTaL/
            - models/ (NEW)
              - MATCH-PeTaL (NEW)
            - results/ (NEW)
              - MATCH-PeTaL-labels.npy (NEW)
              - MATCH-PeTaL-scores.npy (NEW)

    OPTIONS

        -c, --cnf
            Path of configure yaml.
        -v, --verbose
            Enable verbose output.
            Defaults to False.
        -s/-S, --split/--no-split
            Perform train-dev-test split. (i.e., Split.py)
            Defaults to True (-s, --split).
        -a/-A, --augment/--no-augment
            Augment training set. (i.e., augment.py)
            Defaults to True (-a, --augment).
        -t/-T, --transform/--no-transform
            Perform transformation from json to text (i.e., transform.py)
            Defaults to True (-t, --transform).
        -p/-P, --preprocess/--no-preprocess
            Perform preprocessing (i.e., MATCH/preprocessing.py)
            Defaults to True (-p, --preprocess)
        -r/-R, --train/--no-train
            Performs training (i.e., train.py)
            Defaults to True.
        -e/-E, --eval/--no-eval
            Performs model evaluation (i.e., eval.py)
            Defaults to True.
        -i, --infer-mode
            Enable inference mode.
            Defaults to False.
        --remake-vocab-file
            Force vocab.npy and emb_init.npy to be recomputed.
            Occasionally this is necessary, especially if you have changed the dataset.
            Defaults to False.

    USAGE

        preprocess.py --cnf config.yaml [--verbose]

    NOTES

        config.yaml holds options for all of the scripts that this script calls.

    Authors: Eric Kong (eric.l.kong@nasa.gov, erickongl@gmail.com)
'''

import click
import logging
from ruamel.yaml import YAML
from pathlib import Path

from preprocess import preprocess
from train import run_train
from eval import run_eval

@click.command()
@click.option('--cnf', '-c', 'cnf_path', type=click.Path(exists=True), help='Path of configure yaml.')
@click.option('--verbose', '-v', type=click.BOOL, is_flag=True, default=False, help='Verbose output.')
@click.option('--split/--no-split', '-s/-S', 'do_split', default=True, help='Perform train-dev-test split.')
@click.option('--augment/--no-augment', '-a/-A', 'do_augment', default=True, help='Augment training set.')
@click.option('--transform/--no-transform', '-t/-T', 'do_transform', default=True, help='Perform transformation from json to text.')
@click.option('--preprocess/--no-preprocess', '-p/-P', 'do_preprocess', default=True, help='Perform preprocessing.')
@click.option('--train/--no-train', '-r/-R', 'do_train', default=True, help='Do training.')
@click.option('--eval/--no-eval', '-e/-E', 'do_eval', default=True, help='Do inference/evaluation.')
@click.option('--infer-mode', '-i', type=click.BOOL, is_flag=True, default=False, help='Inference mode.')
@click.option('--remake-vocab-file', type=click.BOOL, is_flag=True, default=False, help='Force vocab.npy and emb_init.npy to be recomputed.')

def main(cnf_path,
        verbose=False,
        do_split=True,
        do_augment=True,
        do_transform=True,
        do_preprocess=True,
        do_train=True,
        do_eval=True,
        infer_mode=False,
        remake_vocab_file=False):
    """Command-line entry function - runs MATCH on PeTaL data.

    Args:
        cnf_path (str): Path to configure yaml file.
        verbose (bool): Verbose output.
        do_split (bool): Whether to perform train-dev-test split.
        do_augment (bool): Whether to perform data augmentation on the training set.
        do_transform (bool): Whether to transform json to txt.
        do_preprocess (bool): Whether to preprocess txt into npy.
        do_train (bool): Whether to do training.
        do_eval (bool): Whether to do inference/evaluation.
        infer_mode (bool): Whether to run in inference mode.
        remake_vocab_file (bool): Whether to force vocab.npy and emb_init.npy to be recomputed.
    """

    yaml = YAML(typ='safe')
    cnf = yaml.load(Path(cnf_path))

    run_MATCH_with_PeTaL_data(cnf, verbose, do_split, do_augment, do_transform, do_preprocess, do_train, do_eval, infer_mode, remake_vocab_file)

########################################
#
# NOTE
#   main just calls run_MATCH_with_PeTaL_data
#   main is for Click to transform this file into a command-line program
#   run_MATCH_with_PeTaL_data is for other files to import if they need
#
########################################

def run_MATCH_with_PeTaL_data(cnf,
        verbose=False,
        do_split=True,
        do_augment=True,
        do_transform=True,
        do_preprocess=True,
        do_train=True,
        do_eval=True,
        infer_mode=False,
        remake_vocab_file=False):
    """Runs MATCH on PeTaL data.

    Args:
        cnf (Dict): Python dictionary whose structure adheres to our config.yaml file.
        verbose (bool): Verbose output.
        do_split (bool): Whether to perform train-dev-test split.
        do_augment (bool): Whether to perform data augmentation on the training set.
        do_transform (bool): Whether to transform json to txt.
        do_preprocess (bool): Whether to preprocess txt into npy.
        do_train (bool): Whether to do training.
        do_eval (bool): Whether to do inference/evaluation.
        infer_mode (bool): Whether to run in inference mode.
        remake_vocab_file (bool): Whether to force vocab.npy and emb_init.npy to be recomputed.
    """
    logging.basicConfig(
        level=logging.DEBUG,
        format="[%(asctime)s:%(name)s] %(message)s"
    )
    logger = logging.getLogger("main")

    if verbose:
        if infer_mode:
            logger.info("Begin run_MATCH_with_PeTaL_data pipeline in inference mode.")
        else:
            logger.info("Begin run_MATCH_with_PeTaL_data pipeline.")

    '''
        Preprocessing: Perform train-dev-test split,
        transform json to txt, and preprocess txt into npy
        in preprocess.py.
    '''
    preprocess(cnf, verbose, do_split, do_augment, do_transform, do_preprocess, infer_mode, remake_vocab_file)

    '''
        Training: Run training in train.py.
    '''
    if do_train:
        run_train(cnf, infer_mode, verbose)

    '''
        Evaluation: Run testing/inference/evaluation in eval.py.   
    '''
    if do_eval:
        run_eval(cnf, infer_mode, verbose)

    if verbose:
        logger.info("End run_MATCH_with_PeTaL_data pipeline.")


if __name__ == '__main__':
    main()

########################################
#
#   FOR HISTORICAL REFERENCE
#
#   (nothing yet for run_MATCH_with_PeTaL_data.py)
#
########################################