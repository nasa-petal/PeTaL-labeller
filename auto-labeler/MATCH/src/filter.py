'''
	filter.py

    Run MATCH with PeTaL data.
    Last modified on 12 August 2021.

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
            if js['isBiomimicry'] == 'Y' and js['level1']:
                out_set.append(js)

        if verbose:
            logger.info(f"Writing {len(out_set)} papers from dataset at {output_path}.")

        fout.write(json.dumps(out_set))

    if verbose:
        logger.info(f"Finish filtering dataset.") 


if __name__ == '__main__':
    main()