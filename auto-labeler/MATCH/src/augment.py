'''
    augment.py

    Run MATCH with PeTaL data.
    Last modified on 18 August 2021.

    DESCRIPTION

        augment.py performs _data augmentation_ on train.json. It takes
    
        - MATCH/
          - PeTaL/
        	- train.json
        
        and produces

        - MATCH/
          - PeTaL/
        	- train.json (MODIFIED)

        To perform data augmentation, augment.py takes each paper and 
        _augments_ it by a factor N. That is, it produces N - 1 copies
        of the paper and _perturbs_ them slightly by replacing random
        words in the title and the abstract by synonyms (based on the
        WordNet graph).

        If you are feeling adventurous you can turn on _balance-aware_
        data augmentation, which changes N for each paper based on how
        common or rare the paper's labels are. See the rareness_score
        function for how this calculation would happen.

    OPTIONS

        -d, --dataset-path
            Path to training set.
        -f, --factor
            Factor by which to augment training set size.
            Default: 2.
        -b, --balance-aware
            Use balance-aware data augmentation.
            Default: False
        --alpha
            alpha parameter in balance-aware data augmentation.
            Default: 0.7
        --beta
            beta parameter in balance-aware data augmentation.
            Default: 1
        -v, --verbose
            Enable verbose output.
            Default: False

    USAGE

        python3 augment.py --dataset-path MATCH/PeTaL/train.json

    NOTES

        Called by preprocess.py, which is called by run_MATCH_with_PeTaL.py.
        Does not run if INFERENCE MODE is on in run_MATCH_with_PeTaL_data.py.

        We found that dataset augmentation (and balance-aware dataset augmentation)
        preliminary does not help. In config.yaml, we have set augmentation factor
        to 1, which basically tells augment.py to skip.

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
@click.option('--alpha', type=click.FLOAT, default=0.7, help='Alpha parameter in balance-aware data augmentation.')
@click.option('--beta', type=click.FLOAT, default=1, help='Beta parameter in balance-aware data augmentation.')
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, default=False, required=False, help='Verbose output.')

def main(data_json,
        factor=2,
        balance_aware=False,
        alpha=0.7,
        beta=1,
        verbose=False):
    """Augments a dataset in place using nlpaug.

    Args:
        dataset (string): Path to training set.
        factor (int): Factor by which to augment training set size.
        balance_aware (bool): Whether to use balance-aware data augmentation (not fully tested yet).
        alpha (float): Alpha parameter in balance-aware data augmentation.
        beta (float): Beta parameter in balance-aware data augmentation.
        verbose (bool, optional): Verbose output. Defaults to False.
    """

    augment(data_json, factor, balance_aware, alpha, beta, verbose)

########################################
#
# NOTE
#   main just calls augment
#   main is for Click to transform this file into a command-line program
#   augment is for other files to import if they need
#
########################################

def augment(data_json,
        factor,
        balance_aware=False,
        alpha=0.7,
        beta=1,
        verbose=False):
    """Augments a dataset in place using nlpaug.

    Args:
        dataset (string): Path to training set.
        factor (int): Factor by which to augment training set size.
        balance_aware (bool): Whether to use balance-aware data augmentation (not fully tested yet).
        alpha (float): Alpha parameter in balance-aware data augmentation.
        beta (float): Beta parameter in balance-aware data augmentation.
        verbose (bool, optional): Verbose output. Defaults to False.
    """

    logging.basicConfig(
        level=logging.DEBUG,
        format="[%(asctime)s:%(name)s] %(message)s"
    )
    logger = logging.getLogger("augment")

    if not os.path.exists(data_json):
        if verbose:
            logger.info(f'Skipping training set augmentation, for {data_json} not found.')
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
    with open(data_json) as fin:
        for line in fin:
            data = json.loads(line)
            golden.append(data)
    
    label_count = get_label_count(golden)

    if balance_aware:
        min_rareness, max_rareness, spread_factor = analyze_for_balance_awareness(golden, alpha, beta)
        if verbose:
            logger.info(f"Analyzing papers in {data_json} for balance-aware data augmentation.")
            logger.info(f"Minimum rareness score is {min_rareness}.")
            logger.info(f"Maximum rareness score is {max_rareness}.")
            logger.info(f"This allows a spread factor of {spread_factor}.")

        if verbose:
            logger.info(f"Augmenting dataset at {data_json} with {len(golden)} examples.")

    with open(data_json, 'w') as fout:
        for epoch in (tqdm(range(factor), desc='Full augmentation progress') if verbose else range(factor)):
            for js in (tqdm(golden, desc='Per epoch progress', leave=False) if verbose else golden):
                if epoch == 0:
                    fout.write(json.dumps(js)+'\n')
                else:
                    if balance_aware:
                        relative_rareness = floor(rareness_score(js, label_count, alpha, beta) / min_rareness)
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


def rareness_score(paper, label_count, alpha, beta):
    '''
        Computes a rareness score for a json paper.

                 / sum_{label in paper_labels} (1 / count(label)) ^ ALPHA \ ^ BETA
        Score =  | ------------------------------------------------------ |
                 \                 number of labels in paper              /

    Args:
        paper (dict): a json dictionary, a paper from the golden dataset (or formatted as such)
        label_count (dict(str)): Labels mapped to the amount of times they occur in the dataset.
        alpha (float): Alpha parameter in balance-aware data augmentation.
        beta (float): Beta parameter in balance-aware data augmentation.
    Returns:
        score (float): computed rareness score

    '''
    paper_labels = extract_labels(paper)
    if not paper_labels:
        return 0.0
    score = 0.0
    for paper_label in paper_labels:
        score += (1 / label_count[paper_label]) ** alpha
    return (score / len(paper_labels)) ** beta


def get_label_count(dataset):
    """Computes the label count dictionary: labels to their occurrence counts
    inside the dataset.

    Args:
        dataset (list(dict(str))): A dataset, i.e., a list of json objects fitting
            the Golden Dataset Schema.
        alpha (float): Alpha parameter in balance-aware data augmentation.
        beta (float): Beta parameter in balance-aware data augmentation.

    Returns:
        dict(str): Labels mapped to the amount of times they occur in the dataset.
    """
    label_count = defaultdict(int)
    for label_list in [extract_labels(js) for js in dataset]:
        for label in label_list:
            label_count[label] += 1
    
    return label_count


def analyze_for_balance_awareness(dataset, alpha, beta):
    """Computes minimum rareness score, maximum rareness score,
    and spread factor (the second divided by the first).
    The spread factor is the most copies by which a paper can be augmented.

    Args:
        dataset (list(dict(str))): A dataset, i.e., a list of json objects fitting
            the Golden Dataset Schema.
        

    Returns:
        tuple(min_rareness, max_rareness, spread_factor): Those three quantities.
    """
    label_count = get_label_count(dataset)
    rarenesses = [rareness_score(paper, label_count, alpha, beta) for paper in dataset]
    filtered_rarenesses = [x for x in rarenesses if x > 0]
    min_rareness = min(filtered_rarenesses)
    max_rareness = max(filtered_rarenesses)
    spread_factor = max_rareness / min_rareness
    return min_rareness, max_rareness, spread_factor


if __name__ == "__main__":
    main()

