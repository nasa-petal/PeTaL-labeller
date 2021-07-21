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
@click.option('--verbose', '-v', type=click.BOOL, is_flag=True, default=False, help='Verbose output.')

def main(verbose):
    """
        Download our modified MATCH repository using gdown.

    Args:
        cnf (str): Path to configure yaml file.
        verbose (bool): Verbose output.
    """
    setup(verbose)


def setup(verbose):
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

    if not os.path.exists('src/MATCH/PeTaL'):
        if verbose:
            logger.info("Downloading the PeTaL dataset with pretrained embeddings.") 
        url = "https://drive.google.com/uc?id=1yYHYpmwsgQMI1-5HfY-QVOxRi8JQQ4v4" # PeTaL_20210720
        # url = "https://drive.google.com/uc?id=1Ly--Y2w9ZQWZ_v9Kb6o742DTWokR7Rbi" # MATCH_20210716
        output = "PeTaL.tar.gz"
        gdown.download(url, output, quiet=not verbose)
        os.system("tar -xvf PeTaL.tar.gz -C src/MATCH")
    else:
        if verbose:
            logger.info("You have already downloaded the PeTaL dataset.")
    

if __name__ == "__main__":
    main()