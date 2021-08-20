'''
    analyse_MATCH_output.py

    Run MATCH with PeTaL data.
    Last modified on 16 July 2021.

    DESCRIPTION

        MATCH produces an output to stdout of the form

        ```
        TRAIN_SET_OPTIONS skip=N
        ...
        (STUFF)
        ...
        Precision@1,3,5: 0.7413793103448276 0.5718390804597702 0.4396551724137931
        nDCG@1,3,5: 0.7413793103448276 0.6131173000787031 0.6022903445480057
        ```

        analyse_MATCH_output.py takes the TRAIN_SET_OPTIONS string, skip number,
        precisions, and nDCGs, and computes, for each distinct TRAIN_SET_OPTIONS:
        - P@1 mean and standard deviation
        - P@3 mean and standard deviation
        - P@5 mean and standard deviation
        - nDCG@3 mean and standard deviation
        - nDCG@5 mean and standard deviation

        It produces a markdown-formatted table somewhat like the following.

        | Train set options | P@1=nDCG@1 | P@3 | P@5 | nDCG@3 | nDCG@5 |
        | --- | --- | --- | --- | --- | --- |
        | all | 0.689 ± 0.048 | 0.541 ± 0.041 | 0.426 ± 0.026 | 0.581 ± 0.040 | 0.575 ± 0.033 |
        | no_mag | 0.692 ± 0.032 | 0.546 ± 0.039 | 0.423 ± 0.033 | 0.586 ± 0.038 | 0.575 ± 0.042 |
        | no_venue | 0.660 ± 0.088 | 0.508 ± 0.064 | 0.403 ± 0.050 | 0.548 ± 0.070 | 0.542 ± 0.067 |
        | no_author | 0.688 ± 0.045 | 0.541 ± 0.039 | 0.428 ± 0.026 | 0.582 ± 0.039 | 0.577 ± 0.034 |
        | no_ref | 0.696 ± 0.044 | 0.528 ± 0.036 | 0.420 ± 0.021 | 0.573 ± 0.036 | 0.570 ± 0.028 |
        | no_text | 0.659 ± 0.032 | 0.527 ± 0.030 | 0.417 ± 0.023 | 0.563 ± 0.031 | 0.559 ± 0.028 |

        which can then be plotted by perf_plots.py.

    OPTIONS

        -f, --file LOG_FILE_NAME
            path to input log file (must exist)

    USAGE

        python3 analyse_MATCH_output.py -f LOG_FILE_NAME

    or in context, if you want to strip out the boring bits of the log file
    before you save it (you don't have to do this)

        cd ../src
        python3 xval_test.py -c config.yaml --k 10 -s STUDY_NAME --verbose | tee -a LOG_FILE_NAME
        cd ../analysis

        python3 abbreviate_MATCH_output.py -i LOG_FILE_NAME -o ABBR_LOG_FILE_NAME
        python3 analyse_MATCH_output.py -f ABBR_LOG_FILE_NAME

    Authors: Eric Kong (eric.l.kong@nasa.gov, erickongl@gmail.com)
'''

from collections import namedtuple
import numpy as np
import argparse

parser = argparse.ArgumentParser(description='analyse_MATCH_output', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-f', '--file')

args = parser.parse_args()
file_name = args.file

def analyse_MATCH_output():
    """
        analyse_MATCH_output
        Takes output from several runs of MATCH, each delimited by an opening ``` and a closing ```
        and performs statistics on them.

        Format of a run:
        ```
        [name_of_run] [skip_number]
        ...
        Precision@1,3,5: 0.55 0.3933333333333333 0.296
        nDCG@1,3,5: 0.55 0.43140443472026896 0.4260974804656027
        ```

        Args:
            -f, --file: Path to file of run logs.
    """

    Stats = namedtuple("Stats", "p1s p3s p5s nDCG3s nDCG5s")

    print("""
| Train set options | P@1=nDCG@1 | P@3 | P@5 | nDCG@3 | nDCG@5 |
| --- | --- | --- | --- | --- | --- |""")

    with open(file_name, 'r') as f:
        data_file = f.read()
        logs = data_file.split("```")[1::2]
        stats_dict = {}
        for log in logs:
            option, p1, p3, p5, nDCG3, nDCG5 = extract_log_results(log)
            if option not in stats_dict:
                stats_dict[option] = Stats([], [], [], [], [])
            stats_dict[option].p1s.append(p1)
            stats_dict[option].p3s.append(p3)
            stats_dict[option].p5s.append(p5)
            stats_dict[option].nDCG3s.append(nDCG3)
            stats_dict[option].nDCG5s.append(nDCG5)
        for option in stats_dict:
            stats = stats_dict[option]
            print(f"| {option} | \
{np.mean(stats.p1s):.3f} ± {np.std(stats.p1s):.3f} | \
{np.mean(stats.p3s):.3f} ± {np.std(stats.p3s):.3f} | \
{np.mean(stats.p5s):.3f} ± {np.std(stats.p5s):.3f} | \
{np.mean(stats.nDCG3s):.3f} ± {np.std(stats.nDCG3s):.3f} | \
{np.mean(stats.nDCG5s):.3f} ± {np.std(stats.nDCG5s):.3f} |")
            # print(f"| {option} | {sum(stats.p1s) / len(stats.p1s):.3f} | {sum(stats.p3s) / len(stats.p3s):.3f} | {sum(stats.p5s) / len(stats.p5s):.3f} | {sum(stats.nDCG3s) / len(stats.nDCG3s):.3f} | {sum(stats.nDCG5s) / len(stats.nDCG5s):.3f} |")


def extract_log_results(log):
    lines = log.split('\n')
    option = lines[1].split()[0]
    ps, nDCGs = lines[-3].split(' '), lines[-2].split(' ')
    p1, p3, p5 = float(ps[1]), float(ps[2]), float(ps[3])
    nDCG3, nDCG5 = float(nDCGs[2]), float(nDCGs[3])
    return option, p1, p3, p5, nDCG3, nDCG5

if __name__ == "__main__":
    analyse_MATCH_output()