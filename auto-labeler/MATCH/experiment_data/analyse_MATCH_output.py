'''
    analyse_MATCH_output.py

    Run MATCH with PeTaL data.
    Last modified on 16 July 2021.

    USAGE

        python3 analyse_MATCH_output.py -f LOG_FILE_NAME

    or in context, if you want to strip out the boring bits of the log file
    before you save it (you don't have to do this)

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