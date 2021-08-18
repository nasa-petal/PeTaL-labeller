'''
    augment.py

    Run MATCH with PeTaL data.
    Last modified on 18 August 2021.

    Authors: Eric Kong (eric.l.kong@nasa.gov, erickongl@gmail.com)
'''

import os
import json
import click
import logging
import copy
from collections import defaultdict
from math import floor
from tqdm import tqdm

import nlpaug.augmenter.word as naw
import nltk

from utils import extract_labels

@click.command()
@click.option('-d', '--dataset-path', type=click.Path(exists=True), required=True, help='Path to training set.')
@click.option('-f', '--factor', type=click.INT, default=2, help='Factor by which to augment training set size.')
@click.option('-b', '--balance-aware', type=click.BOOL, is_flag=True, default=False, required=False, help='Use balance-aware data augmentation.')
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, default=False, required=False, help='Verbose output.')

def main(dataset_path,
        factor=2,
        balance_aware=False,
        verbose=False):
    """Augments a dataset in place using nlpaug.

    Args:
        dataset (string): Path to training set.
        factor (int): Factor by which to augment training set size.
        balance_aware (bool): Whether to use balance-aware data augmentation (not fully tested yet).
        verbose (bool, optional): Verbose output. Defaults to False.
    """

    augment(dataset_path, factor, balance_aware, verbose)


def augment(dataset_path,
        factor,
        balance_aware=False,
        verbose=False):
    """Augments a dataset in place using nlpaug.

    Args:
        dataset (string): Path to training set.
        factor (int): Factor by which to augment training set size.
        infer_mode (bool): Whether to run in inference mode.
        balance_aware (bool): Whether to use balance-aware data augmentation (not fully tested yet).
        verbose (bool, optional): Verbose output. Defaults to False.
    """

    logging.basicConfig(
        level=logging.DEBUG,
        format="[%(asctime)s:%(name)s] %(message)s"
    )
    logger = logging.getLogger("augment")

    if not os.path.exists(dataset_path):
        if verbose:
            logger.info(f'Skipping training set augmentation, for {dataset_path} not found.')
        return

    if factor < 2:
        if verbose:
            logger.info(f'Skipping training set augmentation, for factor is {factor} < 2.')
        return

    if verbose:
        logger.info(f"Begin training set augmentation.")    

    aug = naw.SynonymAug(aug_src='wordnet')
    nltk.download('averaged_perceptron_tagger')
    nltk.download('wordnet')

    golden = []
    with open(dataset_path) as fin:
        for line in fin:
            data = json.loads(line)
            golden.append(data)
    
    label_count = get_label_count(golden)

    if balance_aware:
        min_rareness, max_rareness, spread_factor = analyze_for_balance_awareness(golden)
        if verbose:
            logger.info(f"Analyzing papers in {dataset_path} for balance-aware data augmentation.")
            logger.info(f"Minimum rareness score is {min_rareness}.")
            logger.info(f"Maximum rareness score is {max_rareness}.")
            logger.info(f"This allows a spread factor of {spread_factor}.")

        if verbose:
            logger.info(f"Augmenting dataset at {dataset_path} with {len(golden)} examples.")

    with open(dataset_path, 'w') as fout:
        for epoch in (tqdm(range(factor), desc='Full augmentation progress') if verbose else range(factor)):
            for js in (tqdm(golden, desc='Per epoch progress', leave=False) if verbose else golden):
                if epoch == 0:
                    fout.write(json.dumps(js)+'\n')
                else:
                    if balance_aware:
                        relative_rareness = floor(rareness_score(js, label_count) / min_rareness)
                        if relative_rareness <= epoch:
                            continue
                    title = ' '.join(js['title'])
                    aug_title = aug.augment(title)
                    abstract = ' '.join(js['abstract'])
                    aug_abstract = aug.augment(abstract)
                    
                    aug_js = copy.deepcopy(js)

                    aug_js['title'] = aug_title.split()
                    aug_js['abstract'] = aug_abstract.split()
                    fout.write(json.dumps(aug_js)+'\n')

    if verbose:
        logger.info(f"Finish training set augmentation.")    


def rareness_score(paper, label_count):
    '''
        Computes a rareness score for a json paper.

                 / sum_{label in paper_labels} (1 / count(label)) ^ ALPHA \ ^ BETA
        Score =  | ------------------------------------------------------ |
                 \                 number of labels in paper              /

    Params:
        paper (Dict): a json dictionary, a paper from the golden dataset (or formatted as such)
    Returns:
        score (float): computed rareness score

    '''
    ALPHA, BETA = 1, 1
    paper_labels = extract_labels(paper)
    if not paper_labels:
        return 0.0
    score = 0.0
    for paper_label in paper_labels:
        score += (1 / label_count[paper_label]) ** ALPHA
    return (score / len(paper_labels)) ** BETA


def get_label_count(dataset):
    label_count = defaultdict(int)
    for label_list in [extract_labels(js) for js in dataset]:
        for label in label_list:
            label_count[label] += 1
    
    return label_count


def analyze_for_balance_awareness(dataset):
    label_count = get_label_count(dataset)
    rarenesses = [rareness_score(paper, label_count) for paper in dataset]
    filtered_rarenesses = [x for x in rarenesses if x > 0]
    min_rareness = min(filtered_rarenesses)
    max_rareness = max(filtered_rarenesses)
    spread_factor = max_rareness / min_rareness
    return min_rareness, max_rareness, spread_factor


if __name__ == "__main__":
    main()

########################################
#
#   FOR HISTORICAL REFERENCE
#
########################################

