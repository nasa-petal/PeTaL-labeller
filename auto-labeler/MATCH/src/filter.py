'''
	filter.py

    Run MATCH with PeTaL data.
    Last modified on 18 August 2021.

    DESCRIPTION

        filter.py filters out biomimicry papers from an input dataset
        (e.g., golden.json) to produce a smaller output dataset
        (e.g., filtered.json).

        Currently the filter only allows papers which
        - are biomimicry papers
        - have labels.

        To change the filter, modify the code indicated by the comment
        # TO CHANGE THE FILTER

    OPTIONS

        -i, --input-path
            Path to input json dataset (e.g., golden.json.)
            Required, and must exist.
        -o, --output-path
            Path to output json dataest (e.g., filtered.json.)
            Required
        --verbose
            Enable verbose output.
            Default: False.

    USAGE

        python filter.py -i MATCH/PeTaL/golden.json -o MATCH/PeTaL/filtered.json

    NOTES

	Authors: Eric Kong (eric.l.kong@nasa.gov, erickongl@gmail.com)
'''

import os
import json
import click
import logging

@click.command()
@click.option('-i', '--input-path', type=click.Path(exists=True), required=True, help='Path to input json dataset.')
@click.option('-o', '--output-path', type=click.Path(), required=True, help='Path to output json dataset.')
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, default=False, required=False, help='Verbose output.')

def main(input_path, output_path, verbose=False):
    """Filters out a subset of the golden dataset.

    Args:
        input_path (str): Input json dataset (e.g., golden.json).
        output_path (str): Output json dataset (e.g., filtered.json).
        verbose (bool, optional): Enable verbose output.
    """

    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s:%(name)s] %(message)s"
    )
    logger = logging.getLogger("filter")

    if verbose:
        logger.info(f"Begin filtering dataset.")   

    with open(input_path) as fin, open(output_path, 'w') as fout:
        in_set = json.loads(fin.read())
        if verbose:
            logger.info(f"Read {len(in_set)} papers from dataset at {input_path}.")

        out_set = []
        for js in in_set:
            ########################################
            # TO CHANGE THE FILTER
            #
            # Currently filters out all non-biomimicry papers
            # and all papers without labels.
            #
            # Modify this if-statement if you want a different filter.
            ########################################
            if js['isBiomimicry'] == 'Y' and js['level1']:
                out_set.append(js)

        if verbose:
            logger.info(f"Writing {len(out_set)} papers from dataset at {output_path}.")

        fout.write(json.dumps(out_set))

    if verbose:
        logger.info(f"Finish filtering dataset.") 


if __name__ == '__main__':
    main()