'''
    transform_data_PeTaL.py

    Run MATCH with PeTaL data.
    Last modified on 14 July 2021.

    Authors: Eric Kong (eric.l.kong@nasa.gov, erickongl@gmail.com)
'''

import json
# import argparse
import click
import os
import logging

# parser = argparse.ArgumentParser(description='main', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
# parser.add_argument('--prefix', default='MATCH')
# parser.add_argument('--dataset', default='PeTaL', choices=['MAG', 'MeSH', 'PeTaL'])
# parser.add_argument('--no-mag', action='store_true', required=False)
# parser.add_argument('--no-mesh', action='store_true', required=False)
# parser.add_argument('--no-venue', action='store_true', required=False)
# parser.add_argument('--no-author', action='store_true', required=False)
# parser.add_argument('--no-reference', action='store_true', required=False)
# parser.add_argument('--no-text', action='store_true', required=False)
# parser.add_argument('-v', '--verbose', action='store_true', required=False)

# args = parser.parse_args()
# prog = parser.prog
# prefix = args.prefix
# folder = args.dataset
# no_mag = args.no_mag
# no_mesh = args.no_mesh
# no_venue = args.no_venue
# no_author = args.no_author
# no_reference = args.no_reference
# no_text = args.no_text
# verbose = args.verbose

@click.command()
@click.option('--prefix', default='MATCH')
@click.option('--dataset', default='PeTaL', type=click.Choice(['MAG', 'MeSH', 'PeTaL']))
@click.option('--no-mag', type=click.BOOL, is_flag=True, default=False, required=False)
@click.option('--no-mesh', type=click.BOOL, is_flag=True, default=False, required=False)
@click.option('--no-venue', type=click.BOOL, is_flag=True, default=False, required=False)
@click.option('--no-author', type=click.BOOL, is_flag=True, default=False, required=False)
@click.option('--no-reference', type=click.BOOL, is_flag=True, default=False, required=False)
@click.option('--no-text', type=click.BOOL, is_flag=True, default=False, required=False)
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, default=False, required=False, help='Verbose output.')

def main(prefix,
        dataset,
        no_mag=False,
        no_mesh=False,
        no_venue=False,
        no_author=False,
        no_reference=False,
        no_text=False,
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
        verbose (bool, optional): Verbose output. Defaults to False.
    """

    transform_data(prefix, dataset, no_mag, no_mesh, no_venue, no_author, no_reference, no_text, verbose)


def transform_data(prefix,
        dataset,
        no_mag=False,
        no_mesh=False,
        no_venue=False,
        no_author=False,
        no_reference=False,
        no_text=False,
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
        verbose (bool, optional): Verbose output. Defaults to False.
    """

    logging.basicConfig(
        level=logging.DEBUG,
        format="[%(asctime)s:%(name)s] %(message)s"
    )
    logger = logging.getLogger("transform_data_PeTaL")    

    for src_json, dst_txt, file_mode in zip(
            ['train', 'dev', 'test'],
            ['train', 'train', 'test'],
            ['w', 'a', 'w']):
        dataset_path = os.path.join(prefix, dataset, f"{src_json}.json")
        texts_path = os.path.join(prefix, dataset, f"{dst_txt}_texts.txt")
        labels_path = os.path.join(prefix, dataset, f"{dst_txt}_labels.txt")
        if verbose:
            logger.info(f"Transforming from {dataset_path} into {texts_path} and {labels_path}.")

        with open(dataset_path) as fin, open(texts_path, file_mode) as fou1, open(labels_path, file_mode) as fou2:
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

if __name__ == "__main__":
    main()

# with open(folder+'/train.json') as fin, open(folder+'/train_texts.txt', 'w') as fou1, open(folder+'/train_labels.txt', 'w') as fou2:
#     for line in fin:
#         data = json.loads(line)
        
#         text = ''
#         if not no_mag:
#             mag = ' '.join(['MAG_'+x for x in data['mag']])
#             text += mag + ' '
#         if not no_mesh:
#             mesh = ' '.join(['MESH_'+x for x in data['mesh']])
#             text += mesh + ' '
#         # text = venue + ' ' + author + ' ' + reference + ' ' + data['text']
#         if not no_venue:
#             venue = 'VENUE_'+data['venue'].replace(' ', '_')
#             text += venue + ' '
#         if not no_author:
#             author = ' '.join(['AUTHOR_'+x for x in data['author']])
#             text += author + ' '
#         if not no_reference:
#             reference = ' '.join(['REFP_'+x for x in data['reference']])
#             text += reference + ' '
#         if not no_text:
#             text += data['text']
#         label = ' '.join(data['label'])

#         fou1.write(text+'\n')
#         fou2.write(label+'\n')

# with open(folder+'/dev.json') as fin, open(folder+'/train_texts.txt', 'a') as fou1, open(folder+'/train_labels.txt', 'a') as fou2:
#     for line in fin:
#         data = json.loads(line)
        
#         text = ''
#         if not no_mag:
#             mag = ' '.join(['MAG_'+x for x in data['mag']])
#             text += mag + ' '
#         if not no_mesh:
#             mesh = ' '.join(['MESH_'+x for x in data['mesh']])
#             text += mesh + ' '
#         # text = venue + ' ' + author + ' ' + reference + ' ' + data['text']
#         if not no_venue:
#             venue = 'VENUE_'+data['venue'].replace(' ', '_')
#             text += venue + ' '
#         if not no_author:
#             author = ' '.join(['AUTHOR_'+x for x in data['author']])
#             text += author + ' '
#         if not no_reference:
#             reference = ' '.join(['REFP_'+x for x in data['reference']])
#             text += reference + ' '
#         if not no_text:
#             text += data['text']
#         label = ' '.join(data['label'])

#         fou1.write(text+'\n')
#         fou2.write(label+'\n')

# with open(folder+'/test.json') as fin, open(folder+'/test_texts.txt', 'w') as fou1, open(folder+'/test_labels.txt', 'w') as fou2:
#     for line in fin:
#         data = json.loads(line)
        
#         text = ''
#         if not no_mag:
#             mag = ' '.join(['MAG_'+x for x in data['mag']])
#             text += mag + ' '
#         if not no_mesh:
#             mesh = ' '.join(['MESH_'+x for x in data['mesh']])
#             text += mesh + ' '
#         # text = venue + ' ' + author + ' ' + reference + ' ' + data['text']
#         if not no_venue:
#             venue = 'VENUE_'+data['venue'].replace(' ', '_')
#             text += venue + ' '
#         if not no_author:
#             author = ' '.join(['AUTHOR_'+x for x in data['author']])
#             text += author + ' '
#         if not no_reference:
#             reference = ' '.join(['REFP_'+x for x in data['reference']])
#             text += reference + ' '
#         if not no_text:
#             text += data['text']
#         label = ' '.join(data['label'])

#         fou1.write(text+'\n')
#         fou2.write(label+'\n')