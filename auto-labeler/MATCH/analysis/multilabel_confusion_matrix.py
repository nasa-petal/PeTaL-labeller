'''
    multilabel_confusion_matrix.py

    Run MATCH with PeTaL data.
    Last modified on 23 July 2021.

    USAGE

        python3 multilabel_confusion_matrix.py -m ../src/MATCH -p ../plots --verbose

    Authors: Eric Kong (eric.l.kong@nasa.gov, erickongl@gmail.com)
'''

import click
import os
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt, rc
from datetime import datetime
import logging
from collections import namedtuple
from tqdm import tqdm

@click.command()
@click.option('--match', '-m', 'match_path', type=click.Path(exists=True), help='Path of MATCH folder.')
@click.option('--plots', '-p', 'plots_path', type=click.Path(exists=True), help='Path of plots folder.')
@click.option('--verbose', '-v', type=click.BOOL, is_flag=True, default=False, required=False, help='Verbose output.')

def main(match_path, plots_path, verbose):
    """Plots multilabel confusion matrix.

    Args:
        match_path (str): Path of MATCH folder.
        plots_path (str): Path of plots folder.
        verbose (bool): Verbose output.
    """

    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s:%(name)s] %(message)s"
    )
    MCMlogger = logging.getLogger("MCM")  

    DATASET = 'PeTaL'
    MODEL = 'MATCH'

    res_labels = np.load(f"{match_path}/{DATASET}/results/{MODEL}-{DATASET}-labels.npy", allow_pickle=True)
    res_scores = np.load(f"{match_path}/{DATASET}/results/{MODEL}-{DATASET}-scores.npy", allow_pickle=True)
    test_labels = np.load(f"{match_path}/{DATASET}/test_labels.npy", allow_pickle=True)
    train_labels = np.load(f"{match_path}/{DATASET}/train_labels.npy", allow_pickle=True)

    parent_labels = set()
    with open(f'{match_path}/{DATASET}/taxonomy.txt', 'r') as tax_file:
        for line in tax_file:
            parent_label = line.split()[0]
            parent_labels.add(parent_label)
    len(parent_labels)

    all_labels = np.concatenate([train_labels, test_labels], axis=0)

    label_list = np.array(list(set(label for label_list in all_labels for label in label_list)))

    label_count = dict()
    for label in label_list:
        label_count[label] = 0

    for label_list in all_labels:
        for label in label_list:
            label_count[label] += 1

    # print(label_count)
    # print(len(label_count))

    ONLY_LEAF_LABELS = True
    labels = None
    if ONLY_LEAF_LABELS:
        labels = np.array(sorted(filter(lambda lbl: not lbl in parent_labels,
                                list(set(label for label_list in all_labels for label in label_list))
                            ), 
                            key=lambda lbl: label_count[lbl],
                            reverse=True))
    else:
        labels = np.array(sorted(list(set(label for label_list in all_labels for label in label_list)), 
                            key=lambda lbl: label_count[lbl],
                            reverse=True))

    label2idx = {label: idx for idx, label in enumerate(labels)}
    idx2label = {idx: label for idx, label in enumerate(labels)}

    preds_for_test_label = dict()
    test_label_count = dict()

    for test_label in label2idx:
        test_label_count[test_label] = 0

    for test_label in label2idx:
        preds_for_test_label[test_label] = dict()
        for res_label in label2idx:
            preds_for_test_label[test_label][res_label] = 0

    for test_label_list, res_label_list, res_score_list in zip(test_labels, res_labels, res_scores):
        for test_label in test_label_list:
            if test_label in test_label_count:
                test_label_count[test_label] += 1
                for res_label, res_score in zip(res_label_list, res_score_list):
                    if res_label in label2idx:
                        preds_for_test_label[test_label][res_label] += res_score

        # print("test_label_list", test_label_list)
        # print("top_res_label_list", top_res_label_list)

    num_labels = len(label2idx)
    conf_matrix = np.array(
        [
            [
                # i is label2idx[test_label], j is label2idx[res_label]
                preds_for_test_label[idx2label[i]][idx2label[j]] / test_label_count[idx2label[i]] if test_label_count[idx2label[i]] > 0 else 0
                for j in range(num_labels)
            ]
            for i in range(num_labels)
        ] 
    )

    ########################################
    # PLOTTING!
    ########################################

    ALL_PLOTS_PATH = plots_path
    if not os.path.exists(ALL_PLOTS_PATH):
        os.mkdir(ALL_PLOTS_PATH)
    else:
        if verbose:
            MCMlogger.info(f"You already have a plots directory at {ALL_PLOTS_PATH}.")
    
    time_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    comment = f"MCM"
    PLOTS_PATH = os.path.join(ALL_PLOTS_PATH, f"{time_str}_{comment}")

    if not os.path.exists(PLOTS_PATH):
        os.mkdir(PLOTS_PATH)
        if verbose:
            MCMlogger.info(f"New plots directory at {PLOTS_PATH}")
    else:
        if verbose:
            MCMlogger.info(f"You already have a plots directory at {PLOTS_PATH}")

    rc('xtick', labelsize=7)
    rc('ytick', labelsize=7)
    rc('font', size=20)

    # label_limit = 100
    # conf_matrix_small = conf_matrix[:label_limit, :label_limit]
    # num_labels = label_limit
    row_labels = [idx2label[i] for i in range(num_labels)]
    col_labels = [idx2label[i] for i in range(num_labels)]

    plt.rcParams["figure.figsize"] = (10, 10)
    fig, ax = plt.subplots()
    plt.matshow(conf_matrix, fignum=0)
    ax.set_title('Multilabel Confusion Matrix for MATCH on golden.json\nLeaf Labels Sorted by Frequency', y=1.5, pad=0)
    ax.set_xlabel('Predicted labels')
    ax.set_ylabel('Ground truth labels')
    ax.xaxis.set_label_position('top')
    ax.xaxis.tick_top()
    plt.xticks(range(num_labels), col_labels, rotation='vertical')
    plt.yticks(range(num_labels), row_labels)
    plt.colorbar()
    # plt.rcParams["axes.titley"] = 1.0
    # plt.rcParams["axes.titlepad"] = 15
    PLOT_PATH = os.path.join(PLOTS_PATH, f'mcm_{time_str}')
    plt.savefig(fname=PLOT_PATH, facecolor='w', transparent=False, bbox_inches='tight')
    plt.clf()

if __name__ == '__main__':
    main()