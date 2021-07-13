'''
    run_MATCH_with_PeTaL_data.py
    
'''

import click
import os
import gdown

@click.command()
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, default=False)

def main(verbose):
    '''
        Download our modified MATCH repository using gdown.
    '''
    if not os.path.exists('MATCH/'):
        url = "https://drive.google.com/uc?id=100yel9kxjy4VW4VpaAUjjUr0JhxS3fDH"
        output = "MATCH.tar.gz"
        gdown.download(url, output, quiet=verbose)
        os.system("tar -xvf MATCH.tar.gz")
    else:
        if verbose:
            print("You have already downloaded our modified MATCH repository.")
    

if __name__ == '__main__':
    main()
