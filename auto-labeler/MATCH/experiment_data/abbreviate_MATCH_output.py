'''
    abbreviate_MATCH_output.py

    Run MATCH with PeTaL data.
    Last modified on 16 July 2021.

    USAGE

        python3 abbreviate_MATCH_output.py -i LOG_FILE_NAME -o ABBR_LOG_FILE_NAME

    or in context:

        python3 abbreviate_MATCH_output.py -i LOG_FILE_NAME -o ABBR_LOG_FILE_NAME
        python3 analyse_MATCH_output.py -f ABBR_LOG_FILE_NAME

    Authors: Eric Kong (eric.l.kong@nasa.gov, erickongl@gmail.com)
'''

from collections import namedtuple
import numpy as np
import argparse

parser = argparse.ArgumentParser(description='main', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-i', '--infile')
parser.add_argument('-o', '--outfile')

args = parser.parse_args()
inpath = args.infile
outpath = args.outfile

def main():
    with open(inpath, 'r') as infile, open(outpath, 'w') as outfile:
        data_file = infile.read()
        logs = data_file.split("```")[1::2]
        abbrev_logs = [abbreviate_log(log) for log in logs]
        outfile.write('\n\n'.join(abbrev_logs))
        

def abbreviate_log(log):
    triple_backtick = '```'
    lines = log.split('\n')
    option = lines[1]
    ps, nDCGs = lines[-3], lines[-2]
    return '\n'.join([triple_backtick, option, '...', ps, nDCGs, triple_backtick])

if __name__ == "__main__":
    main()