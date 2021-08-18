'''
    abbreviate_MATCH_output.py

    Run MATCH with PeTaL data.
    Last modified on 17 August 2021.

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

        abbreviate_MATCH_output.py strips out all of the (STUFF) in the middle of
        the log so that only the training set option string, skip number,
        precisions, and nDCGs remain in the abbreviated version.

    OPTIONS

        -i, --infile LOG_FILE_NAME
            path to input (uncompressed) log file (must exist)
        -o, --outfile ABBR_LOG_FILE_NAME
            path to output (compressed) log file (need not exist yet)

    USAGE

        python3 abbreviate_MATCH_output.py -i LOG_FILE_NAME -o ABBR_LOG_FILE_NAME

    or in context:

        cd ../src
        python3 xval_test.py -c config.yaml --k 10 -s STUDY_NAME --verbose | tee -a LOG_FILE_NAME
        cd ../analysis

        python3 abbreviate_MATCH_output.py -i LOG_FILE_NAME -o ABBR_LOG_FILE_NAME
        python3 analyse_MATCH_output.py -f ABBR_LOG_FILE_NAME

    Authors: Eric Kong (eric.l.kong@nasa.gov, erickongl@gmail.com)

    NOTES

        Not a necessary step to run, because analyse_MATCH_output.py can also work
        with the uncompressed log files.
'''

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
    # ps, nDCGs = lines[-3], lines[-2]
    ps, nDCGs = "", ""
    for line in lines:
        if line.startswith("Precision@1,3,5: "):
            ps = line
        if line.startswith("nDCG@1,3,5: "):
            nDCGs = line
    return '\n'.join([triple_backtick, option, '...', ps, nDCGs, triple_backtick])

if __name__ == "__main__":
    main()