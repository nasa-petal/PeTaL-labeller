'''
    setup.py

    Run MATCH with PeTaL data.
    Last modified on 18 August 2021.

    DESCRIPTION

        setup.py downloads the PeTaL dataset as a tar file, currently from

            https://drive.google.com/uc?id=1MbmyMzUkd-ke4Tnl-scTuspPmnWcRb6x
        
        Then it untars the tar file and situates it under src/MATCH, so as to
        end up with this file structure:

        - src/
          - MATCH/
            - PeTaL/
              - golden.json
              - filtered.json
              - taxonomy.txt
              - PeTaL.joint.emb
        
        If you wish to update the dataset, put at least golden.json, taxonomy.txt,
        and PeTaL.joint.emb in a PeTaL/ directory (filtered.json is not necessary)
        and then run
        
            tar -cvf PeTaL_YYYYMMDD.tar.gz PeTaL/

        Upload PeTaL_YYYYMMDD.tar.gz to an online hosting service where you can get
        a public link for it, and replace the existing link with the new one.

    OPTIONS

        -v, --verbose
            Enable verbose output

    USAGE

        python3 setup.py [--verbose]

    NOTES

        If src/MATCH/PeTaL already exists, setup.py will not download it again.

        filtered.json is not necessary because it can be generated using

            cd src

            python3 filter.py -i MATCH/PeTaL/golden.json -o MATCH/PeTaL/filtered.json

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

########################################
#
# NOTE
#   main just calls setup
#   main is for Click to transform this file into a command-line program
#   setup is for other files to import if they need
#
########################################

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

######################################## PREVIOUS LINKS
#       url = "https://drive.google.com/uc?id=1yYHYpmwsgQMI1-5HfY-QVOxRi8JQQ4v4" # PeTaL_20210720
#       url = "https://drive.google.com/uc?id=1dTA7h0KAf1bBU40Anpfjg_VMJ_I4JXUQ" # PeTaL_golden_20210723
########################################

        url = "https://drive.google.com/uc?id=1MbmyMzUkd-ke4Tnl-scTuspPmnWcRb6x" # PeTaL_20210817
        output = "PeTaL.tar.gz"
        gdown.download(url, output, quiet=not verbose)
        os.system("tar -xvf PeTaL.tar.gz -C src/MATCH")
    else:
        if verbose:
            logger.info("You have already downloaded the PeTaL dataset.")
    

if __name__ == "__main__":
    main()