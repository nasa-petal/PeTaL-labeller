'''
    perf_plots.py

    Run MATCH with PeTaL data.
    Last modified on 10 August 2021.

    USAGE

        python3 perf_plots.py -r ../experiment_data/results -p ../plots --verbose

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
    columns = extract_data(table_path)
    size = columns['Train set size']
    p1 = columns['P@1=nDCG@1']
    p3 = columns['P@3']
    p5 = columns['P@5']
    n3 = columns['nDCG@3']
    n5 = columns['nDCG@5']

    plt.grid()
    plt.title(f'Effect of training set size on MATCH performance')
    plt.plot(size, p1, linestyle='-', marker='o', label='P@1')
    plt.plot(size, p3, linestyle='-', marker='o', label='P@3')
    plt.plot(size, p5, linestyle='-', marker='o', label='P@5')
    plt.plot(size, n3, linestyle=':', marker='o', label='nDCG@3')
    plt.plot(size, n5, linestyle=':', marker='o', label='nDCG@5')
    plt.xlabel('Training set size')
    plt.xlim(0, 1004)
    plt.ylabel('Metrics')
    plt.ylim(0, 1)
    plt.legend()

    PLOT_PATH = os.path.join(PLOTS_PATH, f'size_test.png')
    plt.savefig(fname=PLOT_PATH, facecolor='w', transparent=False)
    perfLogger.info(f"A plot is saved as {PLOT_PATH}")

    plt.clf()

    ########################################
    # BATCH SIZE TESTING
    ########################################

    table_path = os.path.join(results_path, 'batch_size_test.txt')
    columns = extract_data(table_path)
    size = columns['Training batch size']
    p1 = columns['P@1=nDCG@1']
    p3 = columns['P@3']
    p5 = columns['P@5']
    n3 = columns['nDCG@3']
    n5 = columns['nDCG@5']

    plt.grid()
    plt.title(f'Effect of training batch size on MATCH performance')
    plt.plot(size, p1, linestyle='-', marker='o', label='P@1')
    plt.plot(size, p3, linestyle='-', marker='o', label='P@3')
    plt.plot(size, p5, linestyle='-', marker='o', label='P@5')
    plt.plot(size, n3, linestyle=':', marker='o', label='nDCG@3')
    plt.plot(size, n5, linestyle=':', marker='o', label='nDCG@5')
    plt.xlabel('Training batch size')
    plt.xlim(1, 1024)
    plt.xticks(size)
    plt.xscale('log')
    plt.ylabel('Metrics')
    plt.ylim(0, 1)
    plt.legend()

    PLOT_PATH = os.path.join(PLOTS_PATH, f'batch_size_test.png')
    plt.savefig(fname=PLOT_PATH, facecolor='w', transparent=False)
    perfLogger.info(f"A plot is saved as {PLOT_PATH}")

    plt.clf()    

    ########################################
    # AUGMENT TESTING
    ########################################

    table_path = os.path.join(results_path, 'augment.txt')
    columns = extract_data(table_path)
    aug_factors = columns['Train set augmentation factor']
    p1 = columns['P@1=nDCG@1']
    p3 = columns['P@3']
    p5 = columns['P@5']
    n3 = columns['nDCG@3']
    n5 = columns['nDCG@5']

    plt.grid()
    plt.title(f'Effect of training set augmentation on MATCH performance')
    plt.plot(aug_factors, p1, linestyle='-', marker='o', label='P@1')
    plt.plot(aug_factors, p3, linestyle='-', marker='o', label='P@3')
    plt.plot(aug_factors, p5, linestyle='-', marker='o', label='P@5')
    plt.plot(aug_factors, n3, linestyle=':', marker='o', label='nDCG@3')
    plt.plot(aug_factors, n5, linestyle=':', marker='o', label='nDCG@5')
    plt.xlabel('Training set augmentation factor')
    plt.xlim(0, 6)
    plt.ylabel('Metrics')
    plt.ylim(0, 1)
    plt.legend()

    PLOT_PATH = os.path.join(PLOTS_PATH, f'augment.png')
    plt.savefig(fname=PLOT_PATH, facecolor='w', transparent=False)
    perfLogger.info(f"A plot is saved as {PLOT_PATH}")

    plt.clf()

    ########################################
    # ABLATIONS FROM FULL
    ########################################

    table_path = os.path.join(results_path, 'ablations_from_full.txt')
    columns = extract_data(table_path)

    opts = columns['Train set options']
    p1 = columns['P@1=nDCG@1']

    plt.grid(axis='y')
    plt.title(f'Effect of removing metadata separately on MATCH performance')
    plt.bar(opts, p1, label='P@1')  
    plt.xlabel('Train set options')
    plt.ylabel('Precision at top 1')
    plt.ylim(0, 1)
    # plt.legend()

    PLOT_PATH = os.path.join(PLOTS_PATH, f'ablations_from_full.png')
    plt.savefig(fname=PLOT_PATH, facecolor='w', transparent=False)
    perfLogger.info(f"A plot is saved as {PLOT_PATH}")

    plt.clf()

    ########################################
    # ABLATIONS FROM NONE
    ########################################

    table_path = os.path.join(results_path, 'ablations_from_none.txt')
    columns = extract_data(table_path)

    opts = columns['Train set options']
    p1 = columns['P@1=nDCG@1']

    plt.grid(axis='y')
    plt.title(f'Effect of adding metadata separately on MATCH performance')
    plt.bar(opts, p1, label='P@1')  
    plt.xlabel('Train set options')
    plt.ylabel('Precision at top 1')
    plt.ylim(0, 1)
    # plt.legend()

    PLOT_PATH = os.path.join(PLOTS_PATH, f'ablations_from_none.png')
    plt.savefig(fname=PLOT_PATH, facecolor='w', transparent=False)
    perfLogger.info(f"A plot is saved as {PLOT_PATH}")

    plt.clf()

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
        for idx, line in enumerate(fin):
            items = [x.strip() for x in line.strip('| \n').split('|')]
            if idx == 0:
                column_names = items
                for column_name in column_names:
                    columns[column_name] = []
            elif idx == 1:
                continue
            else:
                cleaned_items = [x.split('±')[0].strip() for x in items]
                for idx, item in enumerate(cleaned_items):
                    if is_num(item):
                        item = float(item)
                    columns[column_names[idx]].append(item)
    return columns

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