'''
    ideal_MCM.py

    Run MATCH with PeTaL data.
    Last modified on 23 July 2021.

    DESCRIPTION

        ideal_MCM.py produces the "idealized" multilabel confusion matrix
        for a dataset. This is the multilabel confusion matrix for a classifier
        which predicts perfectly every label in the training set in
        MATCH/PeTaL/results.

        In a multilabel confusion matrix, the rows correspond to 
        ground-truth labels $l_{true}$ and the columns correspond to 
        predicted labels $l_{pred}$. Each cell sports a colour representing 
        the average confidence score MATCH predicts for the label $l_{pred}$ 
        across all papers bearing the actual label $l_{true}$. This colour 
        is brighter for averages closer to 1, and darker for averages closer
        to 0.

        In an ideal classifier, there would be a bright line streaking
        across the diagonal from the top left to the bottom right. Cells on
        the diagonal represent correct predictions; most cells off the
        diagonal represent mispredictions.

        Labels are sorted by their frequency of occurrence in the dataset;
        labels at the top and left are more common; labels at the bottom and
        right are rarer.

    OPTIONS

        -m, --match PATH/TO/MATCH
            Path of MATCH folder.
        -p, --plots PATH/TO/plots
            Path of plots folder.
        --leaf-only
            Only include leaf labels in the matrix. Defualts to false.
        -v, --verbose
            Enables verbose output.

    USAGE

        python3 ideal_MCM.py -m ../src/MATCH -p ../plots --verbose

    NOTES

        Not a necessary file by any means.

    Authors: Eric Kong (eric.l.kong@nasa.gov, erickongl@gmail.com)
'''

import click
import os
import numpy as np
from matplotlib import pyplot as plt, rc
from datetime import datetime
import logging
import json

@click.command()
@click.option('--match', '-m', 'match_path', type=click.Path(exists=True), help='Path of MATCH folder.')
@click.option('--plots', '-p', 'plots_path', type=click.Path(exists=True), help='Path of plots folder.')
@click.option('--leaf-only', type=click.BOOL, is_flag=True, default=False, required=False, help='Leaf labels only.')
@click.option('--verbose', '-v', type=click.BOOL, is_flag=True, default=False, required=False, help='Verbose output.')

def main(match_path, plots_path, leaf_only, verbose):
    """Plots ideal multilabel confusion matrix.

    Args:
        match_path (str): Path of MATCH folder.
        plots_path (str): Path of plots folder.
        leaf_only (bool): Leaf labels only.
        threshold (float, optional): 'Logits threshold for a positive prediction. Between 0 and 1.'
        verbose (bool): Verbose output.
    """

    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s:%(name)s] %(message)s"
    )
    MCMlogger = logging.getLogger("MCM")  

    DATASET = 'PeTaL'
    MODEL = 'MATCH'

    with open(f"{match_path}/{DATASET}/golden.json") as all_file:
        all_js = json.loads(all_file.read())
        all_labels = np.array([extract_labels(js) for js in all_js])

    parent_labels = set()
    with open(f'{match_path}/{DATASET}/taxonomy.txt', 'r') as tax_file:
        for line in tax_file:
            parent_label = line.split()[0]
            parent_labels.add(parent_label)

    label_list = np.array(list(set(label for label_list in all_labels for label in label_list)))

    label_count = dict()
    for label in label_list:
        label_count[label] = 0

    for label_list_ in all_labels:
        for label in label_list_:
            label_count[label] += 1

    ONLY_LEAF_LABELS = leaf_only
    # labels = None
    # if ONLY_LEAF_LABELS:
    #     labels = np.array(sorted(filter(lambda lbl: not lbl in parent_labels,
    #                             list(set(label for label_list in all_labels for label in label_list))
    #                         ), 
    #                         key=lambda lbl: label_count[lbl],
    #                         reverse=True))
    # else:
    #     labels = np.array(sorted(list(set(label for label_list in all_labels for label in label_list)), 
    #                         key=lambda lbl: label_count[lbl],
    #                         reverse=True))
    if ONLY_LEAF_LABELS:
        label_list = filter(lambda lbl: not lbl in parent_labels, label_list)
        
    labels = np.array(sorted(label_list,
                        key=lambda lbl: label_count[lbl],
                        reverse=True))

    label2idx = {label: idx for idx, label in enumerate(labels)}
    idx2label = {idx: label for idx, label in enumerate(labels)}

    print(label2idx)

    preds_for_test_label = dict()
    test_label_count = dict()

    for test_label in label2idx:
        test_label_count[test_label] = 0

    for test_label in label2idx:
        preds_for_test_label[test_label] = dict()
        for res_label in label2idx:
            preds_for_test_label[test_label][res_label] = 0

    for test_label_list, res_label_list in zip(all_labels, all_labels):
        for test_label in test_label_list:
            if test_label in test_label_count:
                test_label_count[test_label] += 1
                for res_label in res_label_list:
                    if res_label in label2idx:
                        preds_for_test_label[test_label][res_label] += 1 if res_label in test_label_list else 0

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
    comment = f"ideal_MCM"
    PLOTS_PATH = os.path.join(ALL_PLOTS_PATH, f"{time_str}_{comment}")

    if not os.path.exists(PLOTS_PATH):
        os.mkdir(PLOTS_PATH)
        if verbose:
            MCMlogger.info(f"New plots directory at {PLOTS_PATH}")
    else:
        if verbose:
            MCMlogger.info(f"You already have a plots directory at {PLOTS_PATH}")

    rc('xtick', labelsize=12)
    rc('ytick', labelsize=12)
    rc('font', size=20)

    ################################################################################
    # COMMENT/UNCOMMENT THIS CODE TO FILTER OUT EVERYTHING BUT THE TOP label_limit LABELS
    label_limit = 25
    conf_matrix = conf_matrix[:label_limit, :label_limit]
    num_labels = label_limit
    ################################################################################

    row_labels = [idx2label[i] for i in range(num_labels)]
    col_labels = [idx2label[i] for i in range(num_labels)]

    plt.rcParams["figure.figsize"] = (15, 15)
    fig, ax = plt.subplots()
    plt.matshow(conf_matrix, fignum=0)
    ax.set_title(f'Ideal Multilabel Confusion Matrix for MATCH on golden.json\nTop {label_limit} of {"Leaf" if ONLY_LEAF_LABELS else "All"} Labels Sorted by Frequency', y=1.5, pad=0)
    ax.set_xlabel('Predicted labels')
    ax.set_ylabel('Ground truth labels')
    ax.xaxis.set_label_position('top')
    ax.xaxis.tick_top()
    plt.xticks(range(num_labels), col_labels, rotation='vertical')
    plt.yticks(range(num_labels), row_labels)
    plt.colorbar()
    # plt.rcParams["axes.titley"] = 1.0
    # plt.rcParams["axes.titlepad"] = 15
    PLOT_PATH = os.path.join(PLOTS_PATH, f'ideal_mcm_{time_str}')
    plt.savefig(fname=PLOT_PATH, facecolor='w', transparent=False, bbox_inches='tight')
    plt.clf()


def extract_labels(js):
    """Extracts list of labels from a JSON object representing a paper.

    Args:
        js (dict): JSON object representing a paper in the PeTaL golden dataset.

    Returns:
        List(str): all of its labels concatenated into a single list
    """
    
    level1labels = js['level1'] if js['level1'] else []
    level2labels = js['level2'] if js['level2'] else []
    level3labels = js['level3'] if js['level3'] else []    
    return level1labels + level2labels + level3labels


if __name__ == '__main__':
    main()