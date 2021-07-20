'''
    count_terms_in_w2v.py

    Run MATCH with PeTaL data.
    Last modified on 16 July 2021.

    USAGE

        python3 count_terms_in_w2v.py -f PATH/TO/PeTaL.joint.emb

    Authors: Eric Kong (eric.l.kong@nasa.gov, erickongl@gmail.com)
'''

import click
from tqdm import tqdm

@click.command()
@click.option('-f', '--file', type=click.Path(exists=True), help='Path of w2v model file.')

def main(file):
    """Counts types of terms in a w2v model.

    Args:
        file (str): Path of w2v model file.
    """
    count(file)

def count(file):
    """Counts types of terms in a w2v model.

    Args:
        file (str): Path of w2v model file.
    """
    ref_terms = set()
    venue_terms = set()
    author_terms = set()
    MAG_terms = set()
    MESH_terms = set()
    words = set()
    with open(file) as f:
        for line in tqdm(f):
            token = line.split()[0]
            if token.startswith('REFP_'):
                ref_terms.add(token)
            elif token.startswith('VENUE_'):
                venue_terms.add(token)
            elif token.startswith('AUTHOR_'):
                author_terms.add(token)
            elif token.startswith('MAG_'):
                MAG_terms.add(token)
            elif token.startswith('MESH_'):
                MESH_terms.add(token)
            else:
                words.add(token)
    num_refs, num_venues, num_authors, num_MAGs, num_MESHes, num_others = (
        len(ref_terms), len(venue_terms), len(author_terms),
        len(MAG_terms), len(MESH_terms), len(words)
    )
    print(f"Number of unique reference terms: {num_refs}")
    print(f"Number of unique venue terms: {num_venues}")
    print(f"Number of unique author terms: {num_authors}")
    print(f"Number of unique MAG terms: {num_MAGs}")
    print(f"Number of unique MeSH terms: {num_MESHes}")
    print(f"Number of unique other words: {num_others}")
    print(f"Total unique terms: {num_refs + num_venues + num_authors + num_MAGs + num_MESHes + num_others}")

if __name__ == '__main__':
    main()