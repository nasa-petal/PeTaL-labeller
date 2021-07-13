'''
    run_MATCH_with_PeTaL_data.py
    
'''

import click
import os
import gdown
from ruamel.yaml import YAML
from pathlib import Path

@click.command()
@click.option('--cnf', type=click.Path(exists=True), help='Path of configure yaml.')
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, default=False)

def main(cnf, verbose):
    '''
        Run MATCH on PeTaL data.
    '''
    yaml = YAML(typ='safe')
    cnf = yaml.load(Path(cnf))

    '''
        Download our modified MATCH repository using gdown.
    '''
    if not os.path.exists('MATCH/'):
        if verbose:
            print("Downloading our modified MATCH repository.")
        url = "https://drive.google.com/uc?id=100yel9kxjy4VW4VpaAUjjUr0JhxS3fDH"
        output = "MATCH.tar.gz"
        gdown.download(url, output, quiet=not verbose)
        os.system("tar -xvf MATCH.tar.gz")
    else:
        if verbose:
            print("You have already downloaded our modified MATCH repository.")

    DATASET = cnf['dataset']
    MODEL = cnf['model']

    if verbose:
        print(f"Running model {MODEL} on dataset {DATASET}.")


if __name__ == '__main__':
    main()
