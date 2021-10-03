'''
    perf_plots.py

    Run MATCH with PeTaL data.
    Last modified on 10 August 2021.

    DESCRIPTION

        Produces matplotlib plots based on markdown tables in results folder.
        The results folder ought to contain:
        - ablations_from_full.txt
        - ablations_from_none.txt
        - augment.txt
        - batch_size_test.txt
        - learning_rate.txt
        - mesh_size_test.txt
        - old_ablations_from_full.txt
        - old_ablations_from_none.txt
        - size_test.txt
        - weight_decay.txt

    OPTIONS

        -r, --results PATH/TO/results
            Path of results folder.
        -p, --plots PATH/TO/plots
            Path of plots folder.
        -v, --verbose
            Enables verbose output.

    USAGE

        python3 perf_plots.py -r ../experiment_data/results -p ../plots --verbose

    NOTES
        
        Not a very extensible script -- it plots these plots and these plots only
        but it does them well.

    Authors: Eric Kong (eric.l.kong@nasa.gov, erickongl@gmail.com)
'''

import click
import os
import logging
from datetime import datetime

import numpy as np
from matplotlib import pyplot as plt

@click.command()
@click.option('--results', '-r', 'results_path', type=click.Path(exists=True), help='Path of results folder.')
@click.option('--plots', '-p', 'plots_path', type=click.Path(exists=True), help='Path of plots folder.')
@click.option('--verbose', '-v', type=click.BOOL, is_flag=True, default=False, required=False, help='Verbose output.')

def main(results_path, plots_path, verbose):
    """Plots precision and recall and other statistics on graphs.

    Args:
        results_path (str): Path of MATCH folder.
        plots_path (str): Path of plots folder.
        verbose (bool): Verbose output.
    """

    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s:%(name)s] %(message)s"
    )
    perfLogger = logging.getLogger("perf")  

    perfLogger.info("Begin plotting performance plots.")

    ########################################
    # CREATE PLOTTING DIRECTORY
    ########################################

    ALL_PLOTS_PATH = plots_path
    if not os.path.exists(ALL_PLOTS_PATH):
        os.mkdir(ALL_PLOTS_PATH)
    else:
        if verbose:
            perfLogger.info(f"You already have a plots directory at {ALL_PLOTS_PATH}.")
    
    now = datetime.now()
    date_str = now.strftime("%Y%m%d")
    time_str = now.strftime("%H%M%S")
    comment = f"perf"
    PLOTS_PATH = os.path.join(ALL_PLOTS_PATH, f"{date_str}_{comment}")

    if not os.path.exists(PLOTS_PATH):
        os.mkdir(PLOTS_PATH)
        if verbose:
            perfLogger.info(f"New plots directory at {PLOTS_PATH}")
    else:
        if verbose:
            perfLogger.info(f"You already have a plots directory at {PLOTS_PATH}")

    perfLogger.info("Begin plotting performance plots.")

    ########################################
    # SIZE TESTING
    ########################################

    table_path = os.path.join(results_path, 'size_test.txt')
    columns, stds = extract_data(table_path)
    size = columns['Train set size']
    p1 = columns['P@1=nDCG@1']
    p3 = columns['P@3']
    p5 = columns['P@5']
    n3 = columns['nDCG@3']
    n5 = columns['nDCG@5']
    p1err = stds['P@1=nDCG@1']
    p3err = stds['P@3']
    p5err = stds['P@5']
    n3err = stds['nDCG@3']
    n5err = stds['nDCG@5']

    plt.grid()
    # plt.plot(size, p1, linestyle='-', marker='o', label='P@1')
    # plt.plot(size, p3, linestyle='-', marker='o', label='P@3')
    # plt.plot(size, p5, linestyle='-', marker='o', label='P@5')
    # plt.plot(size, n3, linestyle=':', marker='o', label='nDCG@3')
    # plt.plot(size, n5, linestyle=':', marker='o', label='nDCG@5')
    plt.errorbar(size, p1, yerr=p1err, linestyle='-', marker='o', label='P@1')
    plt.errorbar(size, p3, yerr=p3err, linestyle='-', marker='o', label='P@3')
    plt.errorbar(size, p5, yerr=p5err, linestyle='-', marker='o', label='P@5')
    plt.errorbar(size, n3, yerr=n3err, linestyle=':', marker='o', label='nDCG@3')
    plt.errorbar(size, n5, yerr=n5err, linestyle=':', marker='o', label='nDCG@5')
    plt.xlabel('Training set size')
    plt.xlim(0, 1004)
    plt.ylabel('Metrics')
    plt.ylim(0, 1)
    plt.legend()

    NO_TITLE_PLOT_PATH = os.path.join(PLOTS_PATH, f'no_title_size_test.png')
    plt.savefig(fname=NO_TITLE_PLOT_PATH, facecolor='w', transparent=False)
    perfLogger.info(f"A titleless plot is saved as {NO_TITLE_PLOT_PATH}")

    plt.title(f'Effect of training set size on MATCH performance')
    PLOT_PATH = os.path.join(PLOTS_PATH, f'size_test.png')
    plt.savefig(fname=PLOT_PATH, facecolor='w', transparent=False)
    perfLogger.info(f"A plot is saved as {PLOT_PATH}")

    plt.clf()

    ########################################
    # BATCH SIZE TESTING
    ########################################

    table_path = os.path.join(results_path, 'batch_size_test.txt')
    columns, stds = extract_data(table_path)
    size = columns['Training batch size']
    p1 = columns['P@1=nDCG@1']
    p3 = columns['P@3']
    p5 = columns['P@5']
    n3 = columns['nDCG@3']
    n5 = columns['nDCG@5']
    p1err = stds['P@1=nDCG@1']
    p3err = stds['P@3']
    p5err = stds['P@5']
    n3err = stds['nDCG@3']
    n5err = stds['nDCG@5']

    plt.grid()
    plt.errorbar(size, p1, yerr=p1err, linestyle='-', marker='o', label='P@1')
    plt.errorbar(size, p3, yerr=p3err, linestyle='-', marker='o', label='P@3')
    plt.errorbar(size, p5, yerr=p5err, linestyle='-', marker='o', label='P@5')
    plt.errorbar(size, n3, yerr=n3err, linestyle=':', marker='o', label='nDCG@3')
    plt.errorbar(size, n5, yerr=n5err, linestyle=':', marker='o', label='nDCG@5')
    plt.xlabel('Training batch size')
    plt.xlim(1, 1024)
    plt.xticks(size)
    plt.xscale('log')
    plt.ylabel('Metrics')
    plt.ylim(0, 1)
    plt.legend()

    NO_TITLE_PLOT_PATH = os.path.join(PLOTS_PATH, f'no_title_batch_size_test.png')
    plt.savefig(fname=NO_TITLE_PLOT_PATH, facecolor='w', transparent=False)
    perfLogger.info(f"A titleless plot is saved as {NO_TITLE_PLOT_PATH}")

    plt.title(f'Effect of training batch size on MATCH performance')
    PLOT_PATH = os.path.join(PLOTS_PATH, f'batch_size_test.png')
    plt.savefig(fname=PLOT_PATH, facecolor='w', transparent=False)
    perfLogger.info(f"A plot is saved as {PLOT_PATH}")

    plt.clf()    

    ########################################
    # AUGMENT TESTING
    ########################################

    table_path = os.path.join(results_path, 'augment.txt')
    columns, stds = extract_data(table_path)
    aug_factors = columns['Train set augmentation factor']
    p1 = columns['P@1=nDCG@1']
    p3 = columns['P@3']
    p5 = columns['P@5']
    n3 = columns['nDCG@3']
    n5 = columns['nDCG@5']
    p1err = stds['P@1=nDCG@1']
    p3err = stds['P@3']
    p5err = stds['P@5']
    n3err = stds['nDCG@3']
    n5err = stds['nDCG@5']

    plt.grid()
    plt.errorbar(aug_factors, p1, yerr=p1err, linestyle='-', marker='o', label='P@1')
    plt.errorbar(aug_factors, p3, yerr=p3err, linestyle='-', marker='o', label='P@3')
    plt.errorbar(aug_factors, p5, yerr=p5err, linestyle='-', marker='o', label='P@5')
    plt.errorbar(aug_factors, n3, yerr=n3err, linestyle=':', marker='o', label='nDCG@3')
    plt.errorbar(aug_factors, n5, yerr=n5err, linestyle=':', marker='o', label='nDCG@5')
    plt.xlabel('Training set augmentation factor')
    plt.xlim(0, 6)
    plt.ylabel('Metrics')
    plt.ylim(0, 1)
    plt.legend()

    NO_TITLE_PLOT_PATH = os.path.join(PLOTS_PATH, f'no_title_augment.png')
    plt.savefig(fname=NO_TITLE_PLOT_PATH, facecolor='w', transparent=False)
    perfLogger.info(f"A titleless plot is saved as {NO_TITLE_PLOT_PATH}")

    plt.title(f'Effect of training set augmentation on MATCH performance')
    PLOT_PATH = os.path.join(PLOTS_PATH, f'augment.png')
    plt.savefig(fname=PLOT_PATH, facecolor='w', transparent=False)
    perfLogger.info(f"A plot is saved as {PLOT_PATH}")

    plt.clf()

    ########################################
    # ABLATIONS FROM FULL
    ########################################

    table_path = os.path.join(results_path, 'ablations_from_full.txt')
    columns, stds = extract_data(table_path)

    opts = columns['Train set options']
    p1 = columns['P@1=nDCG@1']
    p1err = stds['P@1=nDCG@1']

    plt.grid(axis='y')

    plt.bar(opts, p1, yerr=p1err, label='P@1')  
    plt.xlabel('Train set options')
    plt.ylabel('Precision at top 1')
    plt.ylim(0, 1)
    # plt.legend()

    NO_TITLE_PLOT_PATH = os.path.join(PLOTS_PATH, f'no_title_ablations_from_full.png')
    plt.savefig(fname=NO_TITLE_PLOT_PATH, facecolor='w', transparent=False)
    perfLogger.info(f"A titleless plot is saved as {NO_TITLE_PLOT_PATH}")

    plt.title(f'Effect of removing metadata separately on MATCH performance')
    PLOT_PATH = os.path.join(PLOTS_PATH, f'ablations_from_full.png')
    plt.savefig(fname=PLOT_PATH, facecolor='w', transparent=False)
    perfLogger.info(f"A plot is saved as {PLOT_PATH}")

    plt.clf()

    ########################################
    # ABLATIONS FROM NONE
    ########################################

    table_path = os.path.join(results_path, 'ablations_from_none.txt')
    columns, stds = extract_data(table_path)

    opts = columns['Train set options']
    p1 = columns['P@1=nDCG@1']
    p1err = stds['P@1=nDCG@1']

    plt.grid(axis='y')
    plt.bar(opts, p1, yerr=p1err, label='P@1')  
    plt.xlabel('Train set options')
    plt.ylabel('Precision at top 1')
    plt.ylim(0, 1)
    # plt.legend()

    NO_TITLE_PLOT_PATH = os.path.join(PLOTS_PATH, f'no_title_ablations_from_none.png')
    plt.savefig(fname=NO_TITLE_PLOT_PATH, facecolor='w', transparent=False)
    perfLogger.info(f"A titleless plot is saved as {NO_TITLE_PLOT_PATH}")

    plt.title(f'Effect of adding metadata separately on MATCH performance')
    PLOT_PATH = os.path.join(PLOTS_PATH, f'ablations_from_none.png')
    plt.savefig(fname=PLOT_PATH, facecolor='w', transparent=False)
    perfLogger.info(f"A plot is saved as {PLOT_PATH}")

    plt.clf()

    ########################################
    # OLD ABLATIONS FROM FULL
    ########################################

    table_path = os.path.join(results_path, 'old_ablations_from_full.txt')
    columns, stds = extract_data(table_path)

    opts = columns['Train set options']
    p1 = columns['P@1=nDCG@1']
    p1err = stds['P@1=nDCG@1']

    plt.grid(axis='y')

    plt.bar(opts, p1, yerr=p1err, label='P@1')  
    plt.xlabel('Train set options')
    plt.ylabel('Precision at top 1')
    plt.ylim(0, 1)
    # plt.legend()

    NO_TITLE_PLOT_PATH = os.path.join(PLOTS_PATH, f'no_title_old_ablations_from_full.png')
    plt.savefig(fname=NO_TITLE_PLOT_PATH, facecolor='w', transparent=False)
    perfLogger.info(f"A titleless plot is saved as {NO_TITLE_PLOT_PATH}")

    plt.title(f'Preliminary effect of removing metadata separately on MATCH performance')
    PLOT_PATH = os.path.join(PLOTS_PATH, f'old_ablations_from_full.png')
    plt.savefig(fname=PLOT_PATH, facecolor='w', transparent=False)
    perfLogger.info(f"A plot is saved as {PLOT_PATH}")

    plt.clf()

    ########################################
    # ABLATIONS FROM NONE
    ########################################

    table_path = os.path.join(results_path, 'old_ablations_from_none.txt')
    columns, stds = extract_data(table_path)

    opts = columns['Train set options']
    p1 = columns['P@1=nDCG@1']
    p1err = stds['P@1=nDCG@1']

    plt.grid(axis='y')
    plt.bar(opts, p1, yerr=p1err, label='P@1')  
    plt.xlabel('Train set options')
    plt.ylabel('Precision at top 1')
    plt.ylim(0, 1)
    # plt.legend()

    NO_TITLE_PLOT_PATH = os.path.join(PLOTS_PATH, f'no_title_old_ablations_from_none.png')
    plt.savefig(fname=NO_TITLE_PLOT_PATH, facecolor='w', transparent=False)
    perfLogger.info(f"A titleless plot is saved as {NO_TITLE_PLOT_PATH}")

    plt.title(f'Preliminary effect of adding metadata separately on MATCH performance')
    PLOT_PATH = os.path.join(PLOTS_PATH, f'old_ablations_from_none.png')
    plt.savefig(fname=PLOT_PATH, facecolor='w', transparent=False)
    perfLogger.info(f"A plot is saved as {PLOT_PATH}")

    plt.clf()

    ########################################
    # LEARNING RATE
    ########################################

    table_path = os.path.join(results_path, 'learning_rate.txt')
    columns, stds = extract_data(table_path)
    size = columns['Learning rate']
    p1 = columns['P@1=nDCG@1']
    p3 = columns['P@3']
    p5 = columns['P@5']
    n3 = columns['nDCG@3']
    n5 = columns['nDCG@5']
    p1err = stds['P@1=nDCG@1']
    p3err = stds['P@3']
    p5err = stds['P@5']
    n3err = stds['nDCG@3']
    n5err = stds['nDCG@5']

    plt.grid()
    plt.errorbar(size, p1, yerr=p1err, linestyle='-', marker='o', label='P@1')
    plt.errorbar(size, p3, yerr=p3err, linestyle='-', marker='o', label='P@3')
    plt.errorbar(size, p5, yerr=p5err, linestyle='-', marker='o', label='P@5')
    plt.errorbar(size, n3, yerr=n3err, linestyle=':', marker='o', label='nDCG@3')
    plt.errorbar(size, n5, yerr=n5err, linestyle=':', marker='o', label='nDCG@5')
    plt.xlabel('Adam optimizer learning rate')
    plt.xlim(0, 0.005)
    # plt.xticks(size)
    # plt.xscale('log')
    plt.ylabel('Metrics')
    plt.ylim(0, 1)
    plt.legend()

    NO_TITLE_PLOT_PATH = os.path.join(PLOTS_PATH, f'no_title_learning_rate.png')
    plt.savefig(fname=NO_TITLE_PLOT_PATH, facecolor='w', transparent=False)
    perfLogger.info(f"A titleless plot is saved as {NO_TITLE_PLOT_PATH}")

    plt.title(f'Effect of learning rate on MATCH performance')
    PLOT_PATH = os.path.join(PLOTS_PATH, f'learning_rate.png')
    plt.savefig(fname=PLOT_PATH, facecolor='w', transparent=False)
    perfLogger.info(f"A plot is saved as {PLOT_PATH}")

    plt.clf()

    ########################################
    # WEIGHT DECAY
    ########################################

    table_path = os.path.join(results_path, 'weight_decay.txt')
    columns, stds = extract_data(table_path)
    size = columns['Weight decay']
    p1 = columns['P@1=nDCG@1']
    p3 = columns['P@3']
    p5 = columns['P@5']
    n3 = columns['nDCG@3']
    n5 = columns['nDCG@5']
    p1err = stds['P@1=nDCG@1']
    p3err = stds['P@3']
    p5err = stds['P@5']
    n3err = stds['nDCG@3']
    n5err = stds['nDCG@5']

    plt.grid()
    plt.errorbar(size, p1, yerr=p1err, linestyle='-', marker='o', label='P@1')
    plt.errorbar(size, p3, yerr=p3err, linestyle='-', marker='o', label='P@3')
    plt.errorbar(size, p5, yerr=p5err, linestyle='-', marker='o', label='P@5')
    plt.errorbar(size, n3, yerr=n3err, linestyle=':', marker='o', label='nDCG@3')
    plt.errorbar(size, n5, yerr=n5err, linestyle=':', marker='o', label='nDCG@5')
    plt.xlabel('Adam optimizer weight decay')
    plt.xlim(0, 0.1)
    # plt.xticks(size)
    # plt.xscale('log')
    plt.ylabel('Metrics')
    plt.ylim(0, 1)
    plt.legend()

    NO_TITLE_PLOT_PATH = os.path.join(PLOTS_PATH, f'no_title_weight_decay.png')
    plt.savefig(fname=NO_TITLE_PLOT_PATH, facecolor='w', transparent=False)
    perfLogger.info(f"A titleless plot is saved as {NO_TITLE_PLOT_PATH}")

    plt.title(f'Effect of weight decay on MATCH performance')
    PLOT_PATH = os.path.join(PLOTS_PATH, f'weight_decay.png')
    plt.savefig(fname=PLOT_PATH, facecolor='w', transparent=False)
    perfLogger.info(f"A plot is saved as {PLOT_PATH}")

    plt.clf()

    ########################################
    # MESH SIZE TEST
    ########################################

    table_path = os.path.join(results_path, 'mesh_size_test.txt')
    columns, stds = extract_data(table_path)
    size = columns['Train set size']
    p1 = columns['P@1=nDCG@1']
    p3 = columns['P@3']
    p5 = columns['P@5']
    n3 = columns['nDCG@3']
    n5 = columns['nDCG@5']
    p1err = stds['P@1=nDCG@1']
    p3err = stds['P@3']
    p5err = stds['P@5']
    n3err = stds['nDCG@3']
    n5err = stds['nDCG@5']

    plt.grid()
    plt.errorbar(size, p1, yerr=p1err, linestyle='-', marker='o', label='P@1')
    plt.errorbar(size, p3, yerr=p3err, linestyle='-', marker='o', label='P@3')
    plt.errorbar(size, p5, yerr=p5err, linestyle='-', marker='o', label='P@5')
    plt.errorbar(size, n3, yerr=n3err, linestyle=':', marker='o', label='nDCG@3')
    plt.errorbar(size, n5, yerr=n5err, linestyle=':', marker='o', label='nDCG@5')
    plt.xlabel('Training set size')
    plt.xlim(100, 10000)
    plt.xscale('log')
    plt.ylabel('Metrics')
    plt.ylim(0, 1)
    plt.legend()

    NO_TITLE_PLOT_PATH = os.path.join(PLOTS_PATH, f'no_title_mesh_size_test.png')
    plt.savefig(fname=NO_TITLE_PLOT_PATH, facecolor='w', transparent=False)
    perfLogger.info(f"A titleless plot is saved as {NO_TITLE_PLOT_PATH}")

    plt.title(f'Effect of training set size on MATCH performance on PubMed dataset')
    PLOT_PATH = os.path.join(PLOTS_PATH, f'mesh_size_test.png')
    plt.savefig(fname=PLOT_PATH, facecolor='w', transparent=False)
    perfLogger.info(f"A plot is saved as {PLOT_PATH}")

    plt.clf()

    ########################################
    # THAT'S IT
    ########################################

    perfLogger.info("Finish plotting performance plots.")



def extract_data(path):
    """Extracts data from a markdown-formatted table.

    Args:
        path (str): Path to file of markdown-formatted table.

    Returns:
        dict(str): Data for each column.
    """

    with open(path) as fin:
        column_names = []
        columns = dict()
        stds = dict()
        for idx, line in enumerate(fin):
            items = [x.strip() for x in line.strip('| \n').split('|')]
            if idx == 0:
                column_names = items
                for column_name in column_names:
                    columns[column_name] = []
                    stds[column_name] = []
            elif idx == 1:
                continue
            else:
                ext_cleaned_items = [x.split('±') for x in items]
                cleaned_items = [x[0].strip() for x in ext_cleaned_items]
                cleaned_stds = [x[1].strip() if len(x) > 1 else None for x in ext_cleaned_items]
                for idx, item in enumerate(cleaned_items):
                    if is_num(item):
                        item = float(item)
                    columns[column_names[idx]].append(item)
                for idx, item in enumerate(cleaned_stds):
                    if item and is_num(item):
                        item = float(item)
                    stds[column_names[idx]].append(item)
    return columns, stds

def is_num(n):
    """is_num utility function.

    Args:
        n (str): Candidate string

    Returns:
        bool: Whether the string represents a float.
    """
    try:
        num = float(n)
    except ValueError:
        return False
    return True


    

if __name__ == '__main__':
    main()