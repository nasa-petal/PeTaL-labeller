'''
    preprocess.py

    Run MATCH with PeTaL data.
    Last modified on 26 July 2021.

    Authors: Eric Kong (eric.l.kong@nasa.gov, erickongl@gmail.com)
'''

import click
import sys
import os
import logging
from ruamel.yaml import YAML
from pathlib import Path

from Split import split
from transform_data_golden import transform_data

@click.command()
@click.option('--cnf', '-c', 'cnf_path', type=click.Path(exists=True), help='Path of configure yaml.')
@click.option('--verbose', '-v', type=click.BOOL, is_flag=True, default=False, help='Verbose output.')
@click.option('--split/--no-split', '-s/-S', 'do_split', default=True, help='Perform train-dev-test split.')
@click.option('--transform/--no-transform', '-t/-T', 'do_transform', default=True, help='Perform transformation from json to text.')
@click.option('--preprocess/--no-preprocess', '-p/-P', 'do_preprocess', default=True, help='Perform preprocessing.')

def main(cnf_path,
        verbose=False,
        do_split=True,
        do_transform=True,
        do_preprocess=True):
    """
        Command-line entry function -- perform train-dev-test split,
        transform json to txt, and preprocess txt into npy.

    Args:
        cnf (str): Path to configure yaml file.
        verbose (bool): Verbose output.
        do_split (bool): Whether to perform train-dev-test split.
        do_transform (bool): Whether to transform json to txt.
        do_preprocess (bool): Whether to preprocess txt into npy.
    """

    yaml = YAML(typ='safe')
    cnf = yaml.load(Path(cnf_path))

    preprocess(cnf, verbose, do_split, do_transform, do_preprocess)

def preprocess(cnf,
        verbose=False,
        do_split=True,
        do_transform=True,
        do_preprocess=True):
    """
        Perform train-dev-test split, transform json to txt, and preprocess txt into npy.

    Args:
        cnf (Dict): Python dictionary whose structure adheres to our config.yaml file.
        verbose (bool): Verbose output.
        do_split (bool): Whether to perform train-dev-test split.
        do_transform (bool): Whether to transform json to txt.
        do_preprocess (bool): Whether to preprocess txt into npy.
    """
    logging.basicConfig(
        level=logging.DEBUG,
        format="[%(asctime)s:%(name)s] %(message)s"
    )
    logger = logging.getLogger("preprocess")

    if verbose:
        logger.info("Begin preprocessing.")
    
    sys.path.insert(1, os.path.join(os.getcwd(), 'MATCH'))

    DATASET = cnf['dataset']

    '''
        Train-test split.

        Notebook code that this accounts for:
        %cd PeTaL/
        !python3 Split.py \
            --train {config['train_proportion']} \
            --dev {config['dev_proportion']} \
            --skip {config['skip']}
        %cd ..
        !wc PeTaL/train.json
    '''
    if do_split:
        split_cnf = cnf['split']
        split(
            prefix=split_cnf['prefix'],
            dataset=split_cnf['dataset'],
            train=float(split_cnf['train']),
            dev=float(split_cnf['dev']),
            skip=int(split_cnf['skip']),
            tot=int(split_cnf['tot']),
            verbose=verbose
        )
    
    '''
        Transform data from json objects into txt sequences of tokens.

        Notebook code that this accounts for:
        !python3 transform_data_golden.py --dataset {DATASET} \
        {get_transform_arg_string(config)}
    '''
    if do_transform:
        transform_cnf = cnf['transform']
        transform_data(
            prefix=transform_cnf['prefix'],
            dataset=transform_cnf['dataset'],
            no_mag=not transform_cnf['use_mag'],
            no_mesh=not transform_cnf['use_mesh'],
            no_venue=not transform_cnf['use_venue'],
            no_author=not transform_cnf['use_author'],
            no_reference=not transform_cnf['use_reference'],
            no_text=not transform_cnf['use_text'],
            verbose=verbose
        )

    '''
        Preprocess training and test data.

        Note: Because this is calling MATCH's preprocess.py,
        we need to os.chdir into the MATCH directory,
        otherwise its imports will not work.

        You can access the original function that a Click command
        CLI-izes using .callback()

        Notebook code that this accounts for:
        !python preprocess.py \
        --text-path {DATASET}/train_texts.txt \
        --label-path {DATASET}/train_labels.txt \
        --vocab-path {DATASET}/vocab.npy \
        --emb-path {DATASET}/emb_init.npy \
        --w2v-model {DATASET}/{DATASET}.joint.emb \

        !python preprocess.py \
        --text-path {DATASET}/test_texts.txt \
        --label-path {DATASET}/test_labels.txt \
        --vocab-path {DATASET}/vocab.npy \
    '''
    if do_preprocess:
        preprocess_cnf = cnf['preprocess']
        os.chdir(preprocess_cnf['prefix'])

        from MATCH.preprocess import main as preprocess_main

        preprocess_main.callback(
            text_path=f"{DATASET}/train_texts.txt",
            label_path=f"{DATASET}/train_labels.txt",
            vocab_path=f"{DATASET}/vocab.npy",
            emb_path=f"{DATASET}/emb_init.npy",
            w2v_model=f"{DATASET}/{DATASET}.joint.emb",
            vocab_size=int(preprocess_cnf['vocab_size']),
            max_len=int(preprocess_cnf['max_len']),
        )

        preprocess_main.callback(
            text_path=f"{DATASET}/test_texts.txt",
            label_path=f"{DATASET}/test_labels.txt",
            vocab_path=f"{DATASET}/vocab.npy",
            emb_path=None,
            w2v_model=None,
            vocab_size=int(preprocess_cnf['vocab_size']),
            max_len=int(preprocess_cnf['max_len']),
        )
        os.chdir("..")

    if verbose:
        logger.info('End preprocessing.')

def get_transform_arg_string(config, verbose=False):
    """Transforms config arguments into a CLI-option string 
    for transform_data_PeTaL.py.

    Args:
        config (dict[str]): JSON dictionary of config arguments.

    Returns:
        str: CLI-option string
    """
    transform_args = []
    if not config['use_mag']:
        transform_args.append("--no-mag")
    if not config['use_mesh']:
        transform_args.append("--no-mesh")
    if not config['use_author']:
        transform_args.append("--no-author")
    if not config['use_venue']:
        transform_args.append("--no-venue")
    if not config['use_references']:
        transform_args.append("--no-reference")
    if not config['use_text']:
        transform_args.append("--no-text")
    return ' '.join(transform_args)

if __name__ == '__main__':
    main()

########################################
#
#   FOR HISTORICAL REFERENCE
#
########################################

'''
    For historical purposes.
    The original Google Colab notebook function that this somewhat replaces:

def run_preprocessing(config, verbose=False):
    """Runs train-test split and preprocessing scripts

    Args:
        config (dict[str]): JSON dictionary of config arguments.
    """
    # Train-test split
    %cd PeTaL/
    !python3 Split.py \
        --train {config['train_proportion']} \
        --dev {config['dev_proportion']} \
        --skip {config['skip']}
    %cd ..
    !wc PeTaL/train.json

    # Slightly modified preprocess.sh
    !python3 transform_data_PeTaL.py --dataset {DATASET} \
    {get_transform_arg_string(config)}

    !python preprocess.py \
    --text-path {DATASET}/train_texts.txt \
    --label-path {DATASET}/train_labels.txt \
    --vocab-path {DATASET}/vocab.npy \
    --emb-path {DATASET}/emb_init.npy \
    --w2v-model {DATASET}/{DATASET}.joint.emb \

    !python preprocess.py \
    --text-path {DATASET}/test_texts.txt \
    --label-path {DATASET}/test_labels.txt \
    --vocab-path {DATASET}/vocab.npy \
'''