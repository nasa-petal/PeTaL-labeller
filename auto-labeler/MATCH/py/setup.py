'''
    setup.py

    Run MATCH with PeTaL data.
    Last modified on 14 July 2021.

    Authors: Eric Kong (eric.l.kong@nasa.gov, erickongl@gmail.com)
'''

import click
import os
import gdown
import logging

@click.command()
@click.option('--cnf', type=click.Path(exists=True), help='Path of configure yaml.')
@click.option('--verbose', '-v', type=click.BOOL, is_flag=True, default=False, help='Verbose output.')

def main(cnf, verbose):
    """
        Download our modified MATCH repository using gdown.

    Args:
        cnf (str): Path to configure yaml file.
        verbose (bool): Verbose output.
    """
    setup(cnf, verbose)


def setup(cnf, verbose):
    """
        Download our modified MATCH repository using gdown.

    Args:
        cnf (str): Path to configure yaml file.
        verbose (bool): Verbose output.
    """
    logging.basicConfig(
        level=logging.DEBUG,
        format="[%(asctime)s:%(name)s] %(message)s"
    )
    logger = logging.getLogger("setup") 

    if not os.path.exists('MATCH/'):
        if verbose:
            logger.info("Downloading our modified MATCH repository.")  
        url = "https://drive.google.com/uc?id=1Ly--Y2w9ZQWZ_v9Kb6o742DTWokR7Rbi" # MATCH_20210716
        # url = "https://drive.google.com/uc?id=1iUwxS7HsP-T9kBkPR3ZMn_bGnn80ydTv" # MATCH_20210714
        output = "MATCH.tar.gz"
        gdown.download(url, output, quiet=not verbose)
        os.system("tar -xvf MATCH.tar.gz")
    else:
        if verbose:
            logger.info("You have already downloaded our modified MATCH repository.")
    

if __name__ == "__main__":
    main()