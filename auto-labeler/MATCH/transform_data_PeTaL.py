import json
import argparse

parser = argparse.ArgumentParser(description='main', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('--dataset', default='PeTaL', choices=['MAG', 'MeSH', 'PeTaL'])
parser.add_argument('--no-mag', action='store_true', required=False)
parser.add_argument('--no-mesh', action='store_true', required=False)

args = parser.parse_args()
folder = args.dataset
no_mag = args.no_mag
no_mesh = args.no_mesh

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
        venue = 'VENUE_'+data['venue'].replace(' ', '_')
        author = ' '.join(['AUTHOR_'+x for x in data['author']])
        reference = ' '.join(['REFP_'+x for x in data['reference']])
        text += venue + ' ' + author + ' ' + reference + ' ' + data['text']
        # text = venue + ' ' + author + ' ' + reference + ' ' + data['text']
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
        venue = 'VENUE_'+data['venue'].replace(' ', '_')
        author = ' '.join(['AUTHOR_'+x for x in data['author']])
        reference = ' '.join(['REFP_'+x for x in data['reference']])
        text += venue + ' ' + author + ' ' + reference + ' ' + data['text']
        # text = venue + ' ' + author + ' ' + reference + ' ' + data['text']
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
        venue = 'VENUE_'+data['venue'].replace(' ', '_')
        author = ' '.join(['AUTHOR_'+x for x in data['author']])
        reference = ' '.join(['REFP_'+x for x in data['reference']])
        text += venue + ' ' + author + ' ' + reference + ' ' + data['text']
        # text = venue + ' ' + author + ' ' + reference + ' ' + data['text']
        label = ' '.join(data['label'])

        fou1.write(text+'\n')
        fou2.write(label+'\n')