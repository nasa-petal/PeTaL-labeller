'''
    eval.py

    Run MATCH with PeTaL data.
    Last modified on 18 August 2021.

    DESCRIPTION

        eval.py runs the model evaluation portion of MATCH,
        mostly adapting MATCH/main.py --mode eval
        prepared by the MATCH authors.

        It begins with

        - MATCH/
          - PeTaL/
            - models/ (NEW)
              - MATCH-PeTaL (NEW)
            - test_texts.npy
            - test_labels.npy 
            - emb_init.npy
            - vocab.npy
            - labels_binarizer

        and ends up with

        - MATCH/
          - PeTaL/
            - models/
              - MATCH-PeTaL
            - results/ (NEW)
              - MATCH-PeTaL-labels.npy (NEW)
              - MATCH-PeTaL-scores.npy (NEW)
            - test_texts.npy
            - test_labels.npy 
            - emb_init.npy
            - vocab.npy
            - labels_binarizer

        The exciting addition is the results directory, which contains
        MATCH-PeTaL-labels.npy
            which holds the top 100 labels predicted by MATCH for each token sequence
        MATCH-PeTaL-scores.npy
            which holds the "confidence scores" associated with those top 100 labels
        Both are numpy arrays and can be read with numpy.load(PATH, allow_pickle=True)

        eval.py also prints out, for a few test samples:
        - its first few text tokens
        - the ground-truth labels associated with it
        - the top labels MATCH predicted for it, and their confidence scores
        The amount of test samples, text tokens, and predicted labels can be configured
        in config.yaml.

        You can either choose to see the top k predictions
            (in config.yaml:) criterion: top_k
        Or to see the predictions whose confidences exceed a threshold
            (in config.yaml:) criterion: threshold

        It also calls MATCH/evaluation.py to obtain the average precision and 
        normalized discounted cumulative gain scores. These scores can be
        collected and further analyzed.

    OPTIONS

        -c, --cnf
            Path of configure yaml.
        -i, --infer-mode
            Enable inference mode.
            Defaults to False.
        -v, --verbose
            Enable verbose output.
            Defaults to False.

    USAGE

        eval.py --cnf config.yaml [--verbose]

    NOTES

        config.yaml holds eval.py configuration settings.

    Authors: Eric Kong (eric.l.kong@nasa.gov, erickongl@gmail.com)
'''

import click
import sys
import os
import logging

import numpy as np

from ruamel.yaml import YAML
from pathlib import Path

@click.command()
@click.option('--cnf', '-c', 'cnf_path', type=click.Path(exists=True), help='Path of configure yaml.')
@click.option('--infer-mode', '-i', type=click.BOOL, is_flag=True, default=False, help='Inference mode.')
@click.option('--verbose', '-v', type=click.BOOL, is_flag=True, default=False, help='Verbose output.')

def main(cnf_path, infer_mode, verbose):
    """
        Command-line entry function - runs testing.

    Args:
        cnf (str): Path to configure yaml file.
        infer_mode (bool): Whether to run in inference mode.
        verbose (bool): Verbose output.
    """

    yaml = YAML(typ='safe')
    cnf = yaml.load(Path(cnf_path))

    run_eval(cnf, infer_mode, verbose)

########################################
#
# NOTE
#   main just calls run_eval
#   main is for Click to transform this file into a command-line program
#   run_Eval is for other files to import if they need
#
########################################

def run_eval(cnf, infer_mode, verbose):
    """
        Run testing.

    Args:
        cnf (Dict): Python dictionary whose structure adheres to our config.yaml file.
        infer_mode (bool): Whether to run in inference mode.
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
    eval_cnf = cnf['eval']

    sys.path.insert(1, os.path.join(os.getcwd(), 'MATCH'))

    os.chdir(eval_cnf['prefix'])

    from MATCH.main import main as match_main # main.py
    from MATCH.evaluation import main as evaluation_main # evaluation.py

    match_main.callback(
        data_cnf=f"configure/datasets/{DATASET}.yaml",
        model_cnf=f"configure/models/{MODEL}-{DATASET}.yaml",
        mode="eval",
        reg=0
    )

    ########################################
    # determine how many papers have labels
    ########################################

    with open(f"{DATASET}/test_labels.txt") as fin:
        test_labels = [line.strip() for line in fin]
        num_papers = len(test_labels)
        num_with_labels = len([label for label in test_labels if label])
        logger.info(f"Of {num_papers} papers, {num_with_labels}, or {100 * num_with_labels / num_papers :2.1f}%, have labels.")

    ########################################
    # Sample some test papers
    # and their predictions and confidences
    # You can either choose to see the top k predictions
    #   (criterion: top_k)
    # Or to see the predictions whose confidences exceed a threshold
    #   (criterion: threshold)
    ########################################

    sample = eval_cnf['sample']

    if sample:
        num_samples = eval_cnf['num_samples']
        num_text_tokens = eval_cnf['num_text_tokens']
        top_k = eval_cnf['top_k']
        threshold = eval_cnf['threshold']
        criterion = eval_cnf['criterion']

        logger.info(f"Sampling predictions and their confidences for _{num_samples}_ test papers.")
        if criterion == 'threshold':
            logger.info(f"Using _threshold_ criterion: showing first _{num_text_tokens}_ text tokens and predicted labels with a confidence exceeding _{threshold}_ for each paper.")
        else:
            logger.info(f"Using _top k_ criterion: showing first _{num_text_tokens}_ text tokens and top _{top_k}_ predicted labels and their confidences for each paper.")
        logger.info("Any of the above properties between _underscores_ is configurable.")
    
        print("--- EVALUATION SAMPLES")
        with open(f"{DATASET}/test_texts.txt") as fin:
            texts = [line for line in fin]
        targets = np.load(f"{DATASET}/test_labels.npy", allow_pickle=True)
        res_labels = np.load(f"{DATASET}/results/{MODEL}-{DATASET}-labels.npy", allow_pickle=True)
        res_scores = np.load(f"{DATASET}/results/{MODEL}-{DATASET}-scores.npy", allow_pickle=True)

        num_targets = int(targets.shape[0])
        sample_idxs = np.random.choice(num_targets, num_samples)
        for idx in sample_idxs:
            METADATA_PREFIXES = ['MAG_', 'MESH_', 'VENUE_', 'AUTHOR_', 'REFP_']
            text_tokens = [token for token in texts[idx].split() if not any(token.startswith(prefix) for prefix in METADATA_PREFIXES)]
            text_tokens_str = ' '.join(text_tokens[:num_text_tokens])
            print(f"TEXT: {text_tokens_str} ")

            actual_labels = targets[idx] 
            if len(actual_labels) == 0:
                print('ACTUAL LABELS: (none)')
            else:
                actual_labels_str = ', '.join(actual_labels)
                print(f"ACTUAL LABELS: {actual_labels_str}")

            if criterion == 'threshold':
                top_k = np.argmax(res_scores[idx] < threshold) # top_k becomes the number of labels scoring above the threshold
            if top_k == 0:
                print(f"PREDICTED LABELS: (none)")
            else:
                pred_label_scores = zip(res_labels[idx, :top_k], res_scores[idx, :top_k])
                pred_label_scores_str = ', '.join([f'{x} {y:.3f}' for x, y in pred_label_scores])
                print(f"PREDICTED LABELS: {pred_label_scores_str}")

            print("---")

        logger.info("End of prediction samples.")

    if num_with_labels == 0:
        logger.info("Because no papers have labels, the following statistics are expected to be zero.")
    elif num_with_labels < num_papers:
        logger.info(f"Because only {100 * num_with_labels / num_papers :2.1f}% of papers have labels, the following statistics may not be reliable.")

    ########################################
    # Call MATCH/evaluation.py to get scores for test set.
    ########################################

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