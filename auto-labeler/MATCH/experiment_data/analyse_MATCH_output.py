'''
    analyse_MATCH_output.py
'''

from collections import namedtuple
import numpy as np
import argparse

parser = argparse.ArgumentParser(description='main', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-f', '--file')

args = parser.parse_args()
file_name = args.file

def main():
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
    main()