'''
    transform_data_golden.py

    Run MATCH with PeTaL data.
    Last modified on 18 August 2021.

    DESCRIPTION

        transform_data_golden.py transforms the files that Split.py
        produced, that is:

        - MATCH/
          - PeTaL/
			- train.json
			- dev.json
			- test.json

        into token sequence text files and label files:

        - MATCH/
          - PeTaL/
        	- train.json
			- dev.json
			- test.json
			- train_texts.txt (NEW)
            - train_labels.txt (NEW)
			- test_texts.txt (NEW)
			- test_labels.txt (NEW)

        train.json and dev.json go into train_texts.txt, while test.json
        goes into test_texts.txt.

        train_texts.txt and test_text.txt are text files whose lines are each
        sequences of tokens, beginning with metadata tokens (MAG, VENUE, AUTHOR, REFP)
        and then continuing with title and abstract text tokens.

            MAG_bubble_nest ... REFP_1794681095 building home foam tungara frog ...
            MAG_sunset ... REFP_2040802987 nocturnal mammal greater mouse eared bat ...
        
        train_labels.txt and test_labels.txt are text files whose lines are each
        a space-separated list of biomimicry functions:

            physically_assemble/disassemble protect_from_harm ...
            sense_send_or_process_information sense_signals/environmental_cues ...

    USAGE

        python3 transform_data_golden.py [--prefix MATCH] [--dataset PeTaL] [--verbose]

    OPTIONS

        --prefix
            Path from current working directory to MATCH directory.
            Default: MATCH
        --dataset
            Name of dataset (the directory within MATCH/).
            Default: PeTaL
        --no-mag
            Whether to omit MAG field of study metadata.
            Default: False
        --no-mesh
            Whether to omit MeSH term metadata.
            Default: False
        --no-venue
            Whether to omit venue metadata.
            Default: False
        --no-author
            Whether to omit author metadata.
            Default: False
        --no-reference
            Whether to omit references metadata.
            Default: False
        --no-text
            Whether to omit text.
            Default: False
        --no-title
            Whether to omit title.
            Default: False
        --no-abstract
            Whether to omit abstract.
            Default: False
        --no-level1
            Whether to omit level 1 labels.
            Default: False
        --no-level2
            Whether to omit level 2 labels.
            Default: False
        --no-level3
            Whether to omit level 3 labels.
            Default: False
        --include-labels-in-features
            Whether to include labels in the text.
            The only reason you might want to do this is to see if MATCH can learn
            an identity function, copying input over to output. It can, to a certain extent.
            Default: False
        --infer_mode
            Enable inference mode.
            Without this, transform_data_golden.json considers train.json, dev.json, and test.json
            With this, transfomr_data_golden.json considers only test.json.
            Default: False
        --verbose
            Enable verbose output. 
            Default: False

    NOTES
    
        There may also be another file, transform_data_PeTaL.py, in this directory.
        This script strictly supersedes that one.


    Authors: Eric Kong (eric.l.kong@nasa.gov, erickongl@gmail.com)
'''

import json
import click
import os
import logging

@click.command()
@click.option('--prefix', default='MATCH')
@click.option('--dataset', default='PeTaL', type=click.Choice(['MAG', 'MeSH', 'PeTaL']))
@click.option('--no-mag', type=click.BOOL, is_flag=True, default=False, required=False)
@click.option('--no-mesh', type=click.BOOL, is_flag=True, default=False, required=False)
@click.option('--no-venue', type=click.BOOL, is_flag=True, default=False, required=False)
@click.option('--no-author', type=click.BOOL, is_flag=True, default=False, required=False)
@click.option('--no-reference', type=click.BOOL, is_flag=True, default=False, required=False)
@click.option('--no-text', type=click.BOOL, is_flag=True, default=False, required=False)
@click.option('--no-title', type=click.BOOL, is_flag=True, default=False, required=False)
@click.option('--no-abstract', type=click.BOOL, is_flag=True, default=False, required=False)
@click.option('--no-level1', type=click.BOOL, is_flag=True, default=False, help='Do not include level 1 labels.')
@click.option('--no-level2', type=click.BOOL, is_flag=True, default=False, help='Do not include level 2 labels.')
@click.option('--no-level3', type=click.BOOL, is_flag=True, default=False, help='Do not include level 3 labels.')
@click.option('--include-labels-in-features', type=click.BOOL, is_flag=True, default=False, help='Include labels in train_texts.txt and test_texts.txt.')
@click.option('--infer-mode', '-i', type=click.BOOL, is_flag=True, default=False, help='Inference mode.')
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, default=False, required=False, help='Verbose output.')

def main(prefix,
        dataset,
        no_mag=False,
        no_mesh=False,
        no_venue=False,
        no_author=False,
        no_reference=False,
        no_text=False,
        no_title=False,
        no_abstract=False,
        no_level1=False,
        no_level2=False,
        no_level3=False,
        include_labels_in_features=False,
        infer_mode=False,
        verbose=False):
    """Transforms newline-delimited json files into MATCH-compatible text files.

    Args:
        prefix (string): Path from current working directory to directory containing dataset.
        dataset (string): Name of dataset (in fact, directory containing data)
        no_mag (bool, optional): Whether to omit MAG field of study metadata. Defaults to False.
        no_mesh (bool, optional): Whether to omit MeSH term metadata. Defaults to False.
        no_venue (bool, optional): Whether to omit venue metadata. Defaults to False.
        no_author (bool, optional): Whether to omit author metadata. Defaults to False.
        no_reference (bool, optional): Whether to omit references metadata. Defaults to False.
        no_text (bool, optional): Whether to omit text. Defaults to False.
        no_title (bool, optional): Whether to omit title. Defaults to False.
        no_abstract (bool, optional): Whether to omit abstract. Defaults to False.
        no_level1 (bool, optional): Whether to omit level 1 labels. Defaults to False.
        no_level2 (bool, optional): Whether to omit level 2 labels. Defaults to False.
        no_level3 (bool, optional): Whether to omit level 3 labels. Defaults to False.     
        include_labels_in_features (bool, optional): Whether to include labels in the text.
            The only reason you might want to do this is to see if MATCH can learn
            an identity function, copying input over to output. It can. Defaults to False. 
        infer_mode (bool): Whether to run in inference mode. 
        verbose (bool, optional): Verbose output. Defaults to False.
    """

    transform_data(prefix, dataset, no_mag, no_mesh, no_venue, no_author, no_reference, no_text,
        no_title, no_abstract, no_level1, no_level2, no_level3, include_labels_in_features, infer_mode, verbose)

########################################
#
# NOTE
#   main just calls transform_data
#   main is for Click to transform this file into a command-line program
#   transform_data is for other files to import if they need
#
########################################

def transform_data(dataset_path:str,
        no_mag:bool=False,
        no_mesh:bool=False,
        no_venue:bool=False,
        no_author:bool=False,
        no_reference:bool=False,
        no_text:bool=False,
        no_title:bool=False,
        no_abstract:bool=False,
        no_level1:bool=False,
        no_level2:bool=False,
        no_level3:bool=False,
        include_labels_in_features:bool=False,
        infer_mode:bool=False,
        verbose:bool=False):
    """Transforms newline-delimited json files into MATCH-compatible text files.

    Args:
        prefix (string): Path from current working directory to directory containing dataset.
        dataset_path (string): Path of dataset (in fact, directory containing data)
        no_mag (bool, optional): Whether to omit MAG field of study metadata. Defaults to False.
        no_mesh (bool, optional): Whether to omit MeSH term metadata. Defaults to False.
        no_venue (bool, optional): Whether to omit venue metadata. Defaults to False.
        no_author (bool, optional): Whether to omit author metadata. Defaults to False.
        no_reference (bool, optional): Whether to omit references metadata. Defaults to False.
        no_text (bool, optional): Whether to omit text (title and abstract). Defaults to False.
        no_title (bool, optional): Whether to omit title. Defaults to False.
        no_abstract (bool, optional): Whether to omit abstract. Defaults to False.
        no_level1 (bool, optional): Whether to omit level 1 labels. Defaults to False.
        no_level2 (bool, optional): Whether to omit level 2 labels. Defaults to False.
        no_level3 (bool, optional): Whether to omit level 3 labels. Defaults to False.     
        include_labels_in_features (bool, optional): Whether to include labels in the text.
            The only reason you might want to do this is to see if MATCH can learn
            an identity function, copying input over to output. It can. Defaults to False.  
        infer_mode (bool): Whether to run in inference mode.
        verbose (bool, optional): Verbose output. Defaults to False.
    """

    logging.basicConfig(
        level=logging.DEBUG,
        format="[%(asctime)s:%(name)s] %(message)s"
    )
    logger = logging.getLogger("transform_data_golden")

    ########################################
    #
    # INFERENCE vs. NOT INFERENCE MODE
    #   In zip_options, each item in each list
    #   represents one file to process.
    #   If in INFERENCE MODE,
    #     only work with test.json
    #   but in NOT INFERENCE MODE
    #     work with train.json, dev.json, and test.json
    #
    ########################################

    zip_options = zip(
        ['test'],
        ['test'],
        ['w']
    ) if infer_mode else zip(
        ['train', 'dev', 'test'],
        ['train', 'train', 'test'],
        ['w', 'a', 'w']
    )

    ########################################
    # Loop through json sources.
    ########################################

    for src_json, dst_txt, file_mode in zip_options:
        src_json_path = os.path.join(dataset_path, f"{src_json}.json")
        texts_path = os.path.join(dataset_path, f"{dst_txt}_texts.txt")
        labels_path = os.path.join(dataset_path, f"{dst_txt}_labels.txt")
        if verbose:
            logger.info(f"Transforming from {src_json_path} into {texts_path} and {labels_path}.")

        with open(src_json_path,'r') as fin, open(texts_path, file_mode) as fou1, open(labels_path, file_mode) as fou2:
            for line in fin:
                data = json.loads(line)

                ########################################
                # Construct the concatenated token sequence.
                ########################################
                
                text = ''
                if 'mag' in data and not no_mag:
                    mag = ' '.join(['MAG_'+x.replace(' ', '_') for x in data['mag']])
                    text += mag + ' '
                if 'mesh' in data and not no_mesh:
                    mesh = ' '.join(['MESH_'+x.replace(' ', '_') for x in data['mesh']])
                    text += mesh + ' '
                # text = venue + ' ' + author + ' ' + reference + ' ' + data['text']
                if 'venue' in data and not no_venue:
                    venue = ' '.join('VENUE_'+x.replace(' ', '_') for x in data['venue'])
                    text += venue + ' '
                    if 'venue_mag' in data:
                        venue_mag = ' '.join('VENUE_'+x.replace(' ', '_') for x in data['venue_mag'])
                        text += venue_mag + ' '
                if 'author' in data and not no_author:
                    author = ' '.join(['AUTHOR_'+str(x) for x in data['author']])
                    text += author + ' '
                if 'reference' in data and not no_reference:
                    reference = ' '.join(['REFP_'+str(x) for x in data['reference']])
                    text += reference + ' '
                if 'title' in data and not (no_text or no_title):
                    title = ' '.join(data['title'])
                    text += title + ' '
                if 'abstract' in data and not (no_text or no_abstract):
                    abstract = ' '.join(data['abstract'])
                    text += abstract + ' '
                # if 'text' in data and not no_text:
                #     text += data['text']
                # label = ' '.join(data['label'])

                ########################################
                # Construct the label list by joining all the labels on all levels.
                ########################################

                labels = (
                    (data['level1'] if data['level1'] and not no_level1 else [])
                    + (data['level2'] if data['level2'] and not no_level2 else [])
                    + (data['level3'] if data['level3'] and not no_level3 else [])
                ) if not 'label' in data else data['label']
                label = ' '.join(labels)

                if include_labels_in_features:
                    text += ' '.join(['LABEL_'+str(x) for x in labels]) + ' '

                fou1.write(text+'\n')
                fou2.write(label+'\n')

if __name__ == "__main__":
    main()

########################################
#
#   FOR HISTORICAL REFERENCE
#
########################################

'''
	Original argparse version of getting CLI arguments (for reference purposes):

    parser = argparse.ArgumentParser(description='main', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--prefix', default='MATCH')
    parser.add_argument('--dataset', default='PeTaL', choices=['MAG', 'MeSH', 'PeTaL'])
    parser.add_argument('--no-mag', action='store_true', required=False)
    parser.add_argument('--no-mesh', action='store_true', required=False)
    parser.add_argument('--no-venue', action='store_true', required=False)
    parser.add_argument('--no-author', action='store_true', required=False)
    parser.add_argument('--no-reference', action='store_true', required=False)
    parser.add_argument('--no-text', action='store_true', required=False)
    parser.add_argument('-v', '--verbose', action='store_true', required=False)

    args = parser.parse_args()
    prog = parser.prog
    prefix = args.prefix
    folder = args.dataset
    no_mag = args.no_mag
    no_mesh = args.no_mesh
    no_venue = args.no_venue
    no_author = args.no_author
    no_reference = args.no_reference
    no_text = args.no_text
    verbose = args.verbose
'''

'''
    Original (bit redundant) code for transformation:

    with open(folder+'/train.json') as fin, open(folder+'/train_texts.txt', 'w') as fou1, open(folder+'/train_labels.txt', 'w') as fou2:
        for line in fin:
            data = json.loads(line)
        
            text = ''
            if not no_mag:
                mag = ' '.join(['MAG_'+x for x in data['mag']])
                text += mag + ' '
            if not no_mesh:
                mesh = ' '.join(['MESH_'+x for x in data['mesh']])
                text += mesh + ' '
            # text = venue + ' ' + author + ' ' + reference + ' ' + data['text']
            if not no_venue:
                venue = 'VENUE_'+data['venue'].replace(' ', '_')
                text += venue + ' '
            if not no_author:
                author = ' '.join(['AUTHOR_'+x for x in data['author']])
                text += author + ' '
            if not no_reference:
                reference = ' '.join(['REFP_'+x for x in data['reference']])
                text += reference + ' '
            if not no_text:
                text += data['text']
            label = ' '.join(data['label'])

            fou1.write(text+'\n')
            fou2.write(label+'\n')

    with open(folder+'/dev.json') as fin, open(folder+'/train_texts.txt', 'a') as fou1, open(folder+'/train_labels.txt', 'a') as fou2:
        for line in fin:
            data = json.loads(line)
        
            text = ''
            if not no_mag:
                mag = ' '.join(['MAG_'+x for x in data['mag']])
                text += mag + ' '
            if not no_mesh:
                mesh = ' '.join(['MESH_'+x for x in data['mesh']])
                text += mesh + ' '
            # text = venue + ' ' + author + ' ' + reference + ' ' + data['text']
            if not no_venue:
                venue = 'VENUE_'+data['venue'].replace(' ', '_')
                text += venue + ' '
            if not no_author:
                author = ' '.join(['AUTHOR_'+x for x in data['author']])
                text += author + ' '
            if not no_reference:
                reference = ' '.join(['REFP_'+x for x in data['reference']])
                text += reference + ' '
            if not no_text:
                text += data['text']
            label = ' '.join(data['label'])

            fou1.write(text+'\n')
            fou2.write(label+'\n')

    with open(folder+'/test.json') as fin, open(folder+'/test_texts.txt', 'w') as fou1, open(folder+'/test_labels.txt', 'w') as fou2:
        for line in fin:
            data = json.loads(line)
        
            text = ''
            if not no_mag:
                mag = ' '.join(['MAG_'+x for x in data['mag']])
                text += mag + ' '
            if not no_mesh:
                mesh = ' '.join(['MESH_'+x for x in data['mesh']])
                text += mesh + ' '
            # text = venue + ' ' + author + ' ' + reference + ' ' + data['text']
            if not no_venue:
                venue = 'VENUE_'+data['venue'].replace(' ', '_')
                text += venue + ' '
            if not no_author:
                author = ' '.join(['AUTHOR_'+x for x in data['author']])
                text += author + ' '
            if not no_reference:
                reference = ' '.join(['REFP_'+x for x in data['reference']])
                text += reference + ' '
            if not no_text:
                text += data['text']
            label = ' '.join(data['label'])

            fou1.write(text+'\n')
            fou2.write(label+'\n')
'''