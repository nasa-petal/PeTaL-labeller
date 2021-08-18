'''
    train.py

    Run MATCH with PeTaL data.
    Last modified on 14 July 2021.

    Authors: Eric Kong (eric.l.kong@nasa.gov, erickongl@gmail.com)
'''

import click
import sys
import os
import logging

from ruamel.yaml import YAML
from pathlib import Path
import wandb

@click.command()
@click.option('--cnf', '-c', 'cnf_path', type=click.Path(exists=True), help='Path of configure yaml.')
@click.option('--verbose', '-v', type=click.BOOL, is_flag=True, default=False, help='Verbose output.')

def main(cnf_path, verbose):
    """
        Run training.

    Args:
        cnf_path (str): Path to configure yaml file.
        verbose (bool): Verbose output.
    """

    yaml = YAML(typ='safe')
    cnf = yaml.load(Path(cnf_path))
    
    run_train(cnf, verbose)

def run_train(cnf, verbose):
    """
        Run training.

    Args:
        cnf (Dict): Python dictionary whose structure adheres to our config.yaml file.
        verbose (bool): Verbose output.
    """
    logging.basicConfig(
        level=logging.DEBUG,
        format="[%(asctime)s:%(name)s] %(message)s"
    )
    logger = logging.getLogger("train")

    if verbose:
        logger.info("Begin training.")

    wandb.login()

    MODEL = cnf['model']
    DATASET = cnf['dataset']
    split_cnf = cnf['split']
    transform_cnf = cnf['transform']
    train_cnf = cnf['train']
    wandb_cnf = cnf['wandb']
    # wandb_config is the config information that our wandb project expects
    wandb_config = {
        'train_proportion': split_cnf['train'],
        'dev_proportion': split_cnf['dev'],
        'skip': split_cnf['skip'],
        'use_mag': transform_cnf['use_mag'],
        'use_mesh': transform_cnf['use_mag'],
        'use_author': transform_cnf['use_mag'],
        'use_venue': transform_cnf['use_mag'],
        'use_references': transform_cnf['use_mag'],
        'use_text': transform_cnf['use_mag'],
        'hypernymy_regularization': train_cnf['hypernymy_regularization'],
        'leaf_labels_only': train_cnf['leaf_labels_only'],
        'other_notes': train_cnf['notes'],
    }
    wandb.init(
        project=wandb_cnf['project'],
        group=wandb_cnf['group'],
        config=wandb_config
    )

    sys.path.insert(1, os.path.join(os.getcwd(), 'MATCH'))

    os.chdir(train_cnf['prefix'])

    sample = train_cnf['sample']
    if sample:
        num_samples = train_cnf['num_samples']

        logger.info(f"Sampling _{num_samples}_ texts and their labels.")

        print('--- TRAINING SAMPLES')
        with open(f"{DATASET}/train_texts.txt") as fin1, open(f"{DATASET}/train_labels.txt") as fin2:
            for idx, (text, labels) in enumerate(zip(fin1, fin2)):
                if idx >= num_samples:
                    break
                print(f"FULL TEXT: {text.strip()}")
                print(f"LABELS: {labels.strip()}")
                print('---')

        logger.info(f"End of training samples.")
        

    from MATCH.main import main as match_main # main.py

    match_main.callback(
        data_cnf=f"configure/datasets/{DATASET}.yaml",
        model_cnf=f"configure/models/{MODEL}-{DATASET}.yaml",
        mode="train",
        reg=1 if train_cnf['hypernymy_regularization'] else 0
    )

    '''
        The Google Colab version of this (where I had to construct
        a CLI argument string, blecch) is as follows:

        train_args = ["--data-cnf", f"configure/datasets/{DATASET}.yaml",
            "--model-cnf", f"configure/models/{MODEL}-{DATASET}.yaml",
            "--mode", "train",
            "--reg", "1" if config['hypernymy_regularization'] else "0"]
        match_main(args=train_args, standalone_mode=False)
    '''

    os.chdir("..")

    wandb.finish()

    if verbose:
        logger.info("End training.")

if __name__ == '__main__':
    main()

########################################
#
#   FOR HISTORICAL REFERENCE
#
########################################

'''
    The original Google Colab code, from which I adopted the above, for reference.

    def run_train_test(config, group):
        """Runs training, testing, and evaluation.

        Args:
            config (dict[str]): JSON dictionary of config arguments.
            group (str): experiment group name for wandb logging.
        """
        # Slightly modified run_models.sh

        wandb.init(
            project="MATCH",
            group=group,
            config=config
        )

        # wandb.save(f"configure/datasets/{DATASET}.yaml")
        # wandb.save(f"configure/models/{MODEL}-{DATASET}.yaml")
        %cp configure/datasets/{DATASET}.yaml {wandb.run.dir}
        %cp configure/models/{MODEL}-{DATASET}.yaml {wandb.run.dir}

        train_args = ["--data-cnf", f"configure/datasets/{DATASET}.yaml",
            "--model-cnf", f"configure/models/{MODEL}-{DATASET}.yaml",
            "--mode", "train",
            "--reg", "1" if config['hypernymy_regularization'] else "0"]
        match_main(args=train_args, standalone_mode=False)

        test_args = ["--data-cnf", f"configure/datasets/{DATASET}.yaml",
            "--model-cnf", f"configure/models/{MODEL}-{DATASET}.yaml",
            "--mode", "eval"]
        match_main(args=test_args, standalone_mode=False)

        wandb.finish()

        !python evaluation.py \
        --results {DATASET}/results/{MODEL}-{DATASET}-labels.npy \
        --targets {DATASET}/test_labels.npy \
        --train-labels {DATASET}/train_labels.npy

    def run_trial(config, group):
        """Runs both preprocessing and training-testing. The whole enchilada.

        Args:
            config (dict[str]): JSON dictionary of config arguments.
            group (str): experiment group name for wandb logging.
        """
        run_preprocessing(config)
        run_train_test(config, group)  
'''