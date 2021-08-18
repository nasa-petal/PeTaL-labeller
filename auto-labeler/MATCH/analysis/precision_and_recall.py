'''
    precision_and_recall.py

    Run MATCH with PeTaL data.
    Last modified on 10 August 2021.

    DESCRIPTION

        precision_and_recall.py produces three plots from results in MATCH/PeTaL.
        These three plots appear in plots/YYYYMMDD_precision_recall and are
        as follows:

        - HHMMSS_labels_MATCH_PeTaL.png, which varies threshold and plots number
        of labels predicted. Higher threshold means fewer labels get past the threshold.
        - HHMMSS_prc_MATCH_PeTaL.png, which plots a precision-recall curve by varying
        the threshold. As threshold decreases from 1 to 0, precision goes down but recall
        goes up (because more labels get past the threshold).
        - HHMMSS_prf1_MATCH_PeTaL.png, which plots how precision, recall, and F1 score
        vary as threshold varies from 0 to 1.

    OPTIONS

        -m, --match PATH/TO/MATCH
            Path of MATCH folder.
        -p, --plots PATH/TO/plots
            Path of plots folder.
        -d, --dataset PeTaL
            Name of dataset, e.g., "PeTaL".
        -v, --verbose
            Enable verbosity.

    USAGE

        python3 precision_and_recall.py -m ../src/MATCH -p ../plots --verbose

    Authors: Eric Kong (eric.l.kong@nasa.gov, erickongl@gmail.com)
'''

import click
import os
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from datetime import datetime
import logging

from collections import namedtuple
from tqdm import tqdm

Stats = namedtuple("Stats", "threshold topk precision recall f1")

@click.command()
@click.option('--match', '-m', 'match_path', type=click.Path(exists=True), help='Path of MATCH folder.')
@click.option('--plots', '-p', 'plots_path', type=click.Path(exists=True), help='Path of plots folder.')
@click.option('--dataset', '-m', 'dataset', default='PeTaL', help='Name of dataset, e.g., "PeTaL".')
@click.option('--verbose', '-v', type=click.BOOL, is_flag=True, default=False, required=False, help='Verbose output.')

def main(match_path, plots_path, dataset, verbose):
    """Plots precision and recall and other statistics on graphs.

    Args:
        match_path (str): Path of MATCH folder.
        plots_path (str): Path of plots folder.
        verbose (bool): Verbose output.
    """

    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s:%(name)s] %(message)s"
    )
    PRlogger = logging.getLogger("P&R")  

    DATASET = dataset
    MODEL = 'MATCH'

    res_labels = np.load(f"{match_path}/{DATASET}/results/{MODEL}-{DATASET}-labels.npy", allow_pickle=True)
    res_scores = np.load(f"{match_path}/{DATASET}/results/{MODEL}-{DATASET}-scores.npy", allow_pickle=True)
    test_labels = np.load(f"{match_path}/{DATASET}/test_labels.npy", allow_pickle=True)
    train_labels = np.load(f"{match_path}/{DATASET}/train_labels.npy", allow_pickle=True)

    if verbose:
        PRlogger.info(f"Computing statistics by varying threshold for {MODEL} on {DATASET}.")

    thresholds = list(x / 10000 for x in range(1, 10)) + \
        list(x / 1000 for x in range(1, 10)) + \
        list(x / 100 for x in range(1, 10)) + \
        list(x / 20 for x in range(2, 19)) + \
        list((90 + x) / 100 for x in range(1, 10)) + \
        list((990 + x) / 1000 for x in range(1, 10)) + \
        list((9990 + x) / 10000 for x in range(1, 10))

    ps = []
    rs = []
    ts = []
    f1s = []
    topks = []
    for threshold in tqdm(thresholds):
        stats = compute_stats(threshold, res_labels, res_scores, test_labels)
        ps.append(stats.precision)
        rs.append(stats.recall)
        ts.append(threshold)
        f1s.append(stats.f1)
        topks.append(stats.topk)

    '''
        Make the following plots to assess the performance of the model.

        Precision-recall curve
        Precision, recall, and F1 score by varying threshold
        Numbers of labels predicted by varying threshold    
    '''

    ALL_PLOTS_PATH = plots_path
    if not os.path.exists(ALL_PLOTS_PATH):
        os.mkdir(ALL_PLOTS_PATH)
    else:
        if verbose:
            PRlogger.info(f"You already have a plots directory at {ALL_PLOTS_PATH}.")

    now = datetime.now()
    date_str = now.strftime("%Y%m%d")
    time_str = now.strftime("%H%M%S")
    comment = f"precision_recall" # "_on_{DATASET}"
    PLOTS_PATH = os.path.join(ALL_PLOTS_PATH, f"{date_str}_{comment}")

    if not os.path.exists(PLOTS_PATH):
        os.mkdir(PLOTS_PATH)
        if verbose:
            PRlogger.info(f"New plots directory at {PLOTS_PATH}")
    else:
        if verbose:
            PRlogger.info(f"You already have a plots directory at {PLOTS_PATH}")

    ########################################
    # PRECISION-RECALL CURVE
    ########################################
    
    plt.grid()
    plt.title(f'Precision-Recall Curve for {MODEL} on {DATASET}, varying threshold')
    plt.plot(ps, rs, linestyle='-')
    plt.xlabel('Recall')
    plt.xlim(0, 1)
    plt.ylabel('Precision')
    plt.ylim(0, 1)

    PLOT_PATH = os.path.join(PLOTS_PATH, f'{time_str}_prc_{MODEL}_{DATASET}.png')
    plt.savefig(fname=PLOT_PATH, facecolor='w', transparent=False)
    PRlogger.info(f"Your plot is saved as {PLOT_PATH}")
    plt.clf()

    ########################################
    # PRECISION, RECALL, AND F1 SCORE BY THRESHOLD
    ########################################

    plt.grid()
    plt.title(f'Precision, Recall, and F1 Score by Threshold for {MODEL} on {DATASET}')
    plt.plot(ts, ps, linestyle='-', label='Precision')
    plt.plot(ts, rs, linestyle='-', label='Recall')
    plt.plot(ts, f1s, linestyle='-', label='F1 score')
    plt.xlabel('Threshold')
    plt.xlim(0, 1)
    plt.ylabel('Metrics')
    plt.ylim(0, 1)
    plt.legend()

    PLOT_PATH = os.path.join(PLOTS_PATH, f'{time_str}_prf1_{MODEL}_{DATASET}.png')
    plt.savefig(fname=PLOT_PATH, facecolor='w', transparent=False)
    PRlogger.info(f"Your plot is saved as {PLOT_PATH}")
    plt.clf()

    ########################################
    # NUMBER OF LABELS PREDICTED BY THRESHOLD
    ########################################

    plt.grid()
    plt.title(f'Number of Labels Predicted by Threshold for {MODEL} on {DATASET}')
    plt.plot(ts, topks, linestyle='-', label='Number of Labels')
    plt.xlabel('Threshold')
    plt.xlim(0, 1)
    plt.ylabel('Labels')
    plt.legend()

    PLOT_PATH = os.path.join(PLOTS_PATH, f'{time_str}_labels_{MODEL}_{DATASET}.png')
    plt.savefig(fname=PLOT_PATH, facecolor='w', transparent=False)
    PRlogger.info(f"Your plot is saved as {PLOT_PATH}")
    plt.clf()

def compute_stats(threshold, res_labels, res_scores, test_labels):
    """
        compute_stats(threshold)

        Parameters:
            threshold: float, 0.0 < threshold < 1.0
            res_labels: numpy array of predicted labels
            res_scores: numpy array of predicted label scores
            test_labels: numpy array of target labels
        
        Returns:
            Stats object containing
                threshold
                topk: average number of labels above threshold
                precision: average precision across examples
                recall: average recall across examples
                f1: average F1 score across examples
        
        Note:
            precision, recall, and F1 scores are macro (averaged across examples, not labels)
    """
    precisions = []
    recalls = []
    topks = []
    f1s = []
    for res_label, res_score, test_label in zip(res_labels, res_scores, test_labels):
        topk = np.argmax(res_score < threshold) # topk becomes the number of labels scoring above the threshold
        precision = 1.0 if topk == 0 else np.mean([1 if x in test_label else 0 for x in res_label[:topk]])
        recall = np.mean([1 if x in res_label[:topk] else 0 for x in test_label])
        f1 = 0 if (precision + recall) == 0 else (2 * precision * recall) / (precision + recall)
        topks.append(topk)
        precisions.append(precision)
        recalls.append(recall)
        f1s.append(f1)
        # print(res_label[:topk], precision, recall)
    return Stats(threshold, np.mean(topks), np.mean(precisions), np.mean(recalls), np.mean(f1s))

if __name__ == '__main__':
    main()