'''
	Split.py

    Run MATCH with PeTaL data.
    Last modified on 9 August 2021.

	Authors: Eric Kong (eric.l.kong@nasa.gov, erickongl@gmail.com)
'''

import json
import click
import os
import logging

from utils import extract_labels

@click.command()
@click.option('--prefix', default='MATCH/PeTaL', help='Path from current working directory to directory containing dataset.')
@click.option('--dataset', default='golden.json', help='Filename of newline-delimited json dataset.')
@click.option('--train', default=0.8, type=click.FLOAT, help='Proportion, from 0.0 to 1.0, of dataset used for training.')
@click.option('--dev', default=0.1, type=click.FLOAT, help='Proportion, from 0.0 to 1.0, of dataset used for validation.')
@click.option('--skip', default=0, type=click.INT, help='Number of training examples by which to rotate the dataset (e.g., for cross-validation).')
@click.option('--tot', default=0, type=click.INT, help='Total number of examples to use (defaults to whole dataset).')
@click.option('--infer-mode', '-i', type=click.BOOL, is_flag=True, default=False, help='Inference mode.')
@click.option('--verbose', '-v', type=click.BOOL, is_flag=True, default=False, help='Verbose output.')

def main(prefix='MATCH/PeTaL',
		dataset='golden.json',
		train=0.8,
		dev=0.1,
		skip=0,
		tot=0,
		infer_mode=False,
		verbose=False):
	"""Performs train-test split on newline-delimited json file.	

	Args:
		prefix (string): Path from current working directory to directory containing dataset.
		dataset (string): Filename of newline-delimited json dataset.
		train (float): Proportion, from 0.0 to 1.0, of dataset used for training.
		dev (float): Proportion, from 0.0 to 1.0, of dataset used for validation.
		skip (int): Number of training examples by which to rotate the dataset (e.g., for cross-validation).
		tot (int): Total number of training examples.
        infer_mode (bool): Whether to run in inference mode.
		verbose (bool): Verbose output.
	"""	
	split(prefix, dataset, train, dev, skip, tot, infer_mode, verbose)

def split(prefix='MATCH/PeTaL',
		dataset='cleaned_lens_output.json',
		train=0.8,
		dev=0.1,
		skip=0,
		tot=0,
		infer_mode=False,
		verbose=False):
	"""Performs train-test split on newline-delimited json file.	

	Args:
		prefix (string): Path from current working directory to directory containing dataset.
		dataset (string): Filename of newline-delimited json dataset.
		train (float): Proportion, from 0.0 to 1.0, of dataset used for training.
		dev (float): Proportion, from 0.0 to 1.0, of dataset used for validation.
		skip (int): Number of training examples by which to rotate the dataset (e.g., for cross-validation).
		tot (int): Total number of training examples.
        infer_mode (bool): Whether to run in inference mode.
		verbose (bool): Verbose output.
	"""	

	logging.basicConfig(
		level=logging.DEBUG,
		format="[%(asctime)s:%(name)s] %(message)s"
	)
	logger = logging.getLogger("Split")

	dataset_path = os.path.join(prefix, dataset)
	if not os.path.exists(dataset_path):
		logger.error(f"ERROR: Unable to find dataset json file {os.path.join(os.getcwd(), dataset_path)}.")
		return

	if infer_mode:
		infer_path = os.path.join(prefix, 'test.json')
		
		if verbose:
			logger.info(f"Copying from {dataset_path} to {infer_path} for inference mode.")

		with open(dataset_path) as fin, open(infer_path, 'w') as fout:
			golden = json.loads(fin.read())
			for js in golden:
				fout.write(json.dumps(js)+'\n')
	
	else:
		train_path = os.path.join(prefix, 'train.json')
		dev_path = os.path.join(prefix, 'dev.json')
		test_path = os.path.join(prefix, 'test.json')

		if verbose:
			logger.info(f"Transforming from {dataset_path} to {train_path}, {dev_path}, and {test_path}.")

		train_proportion, dev_proportion = train, dev
		train_labels = set()

		# If the default value 0 was passed in as tot,
		# count the number of examples in the dataset
		# and use that as the total number of examples.
		# Otherwise stick with the passed-in total argument,
		# unless that exceeds the actual number of examples in the dataset.
		with open(dataset_path) as fin:
			num_examples = sum(1 for _ in json.loads(fin.read()))
			if tot == 0 or tot > num_examples:
				tot = num_examples
		if verbose:
			logger.info(f"{tot} total examples in dataset.")

		with open(dataset_path) as fin, open(train_path, 'w') as fou1, open(dev_path, 'w') as fou2, open(test_path, 'w') as fou3:
			golden = json.loads(fin.read())
			# for idx, line in enumerate(fin):
			for idx, js in enumerate(golden):
				if idx < skip or idx >= tot:
					continue
				# js = json.loads(line)
			
				# level1Labels = js['level1'] if js['level1'] else []
				# level2Labels = js['level2'] if js['level2'] else []
				# level3Labels = js['level3'] if js['level3'] else []
				# all_labels = level1Labels + level2Labels + level3Labels

				all_labels = extract_labels(js)

				if (idx - skip) % tot < tot * train_proportion:
					for l in all_labels:
						train_labels.add(l)

					js['label'] = all_labels
					fou1.write(json.dumps(js)+'\n')
				
				else:
					label_new = []
					for l in all_labels:
						if l in train_labels:
							label_new.append(l)
					if len(label_new) == 0:
						continue

					js['label'] = label_new
					# print(js['label'])
					# print([x for x in js.keys()])
					if (idx - skip) % tot < tot * (train_proportion + dev_proportion):
						fou2.write(json.dumps(js)+'\n')
					else:
						fou3.write(json.dumps(js)+'\n')
			
			# fin.seek(0)

			# for idx, line in enumerate(fin):
			for idx, js in enumerate(golden):
				if idx >= skip:
					break
				# js = json.loads(line)
			
				# level1Labels = js['level1'] if js['level1'] else []
				# level2Labels = js['level2'] if js['level2'] else []
				# level3Labels = js['level3'] if js['level3'] else []
				# all_labels = level1Labels + level2Labels + level3Labels

				all_labels = extract_labels(js)

				if (idx - skip) % tot < tot * train_proportion:
					for l in all_labels:
						train_labels.add(l)

					js['label'] = all_labels
					fou1.write(json.dumps(js)+'\n')
				
				else:
					label_new = []
					for l in all_labels:
						if l in train_labels:
							label_new.append(l)
					if len(label_new) == 0:
						continue

					js['label'] = label_new
					if (idx - skip) % tot < tot * (train_proportion + dev_proportion):
						fou2.write(json.dumps(js)+'\n')
					else:
						fou3.write(json.dumps(js)+'\n')   

		if verbose:			
			logger.info(f"Number of train labels: {len(train_labels)}")

		'''
			Original non-rotated version (for reference purposes):

		with open('cleaned_lens_output.json') as fin, open('train.json', 'w') as fou1, open('dev.json', 'w') as fou2, open('test.json', 'w') as fou3:
			labelled_so_far = 0
			for idx, line in enumerate(fin):
				js = json.loads(line)
				
				if js['label']:
					if labelled_so_far < labelled * 0.8:
						for l in js['label']:
							train_labels.add(l)
						fou1.write(json.dumps(js) + '\n')
					else:
						label_new = []
						for l in js['label']:
							if l in train_labels:
								label_new.append(l)
						if len(label_new) == 0:
							continue

						js['label'] = label_new
						fou2.write(json.dumps(js)+'\n')
					labelled_so_far += 1
			fin.seek(0)
			for idx, line in enumerate(fin):
				js = json.loads(line)
				if not js['label']:
					fou3.write(json.dumps(js)+'\n')

		print(len(train_labels))
		'''

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
	parser.add_argument('--prefix', default='MATCH/PeTaL', help='Path from current working directory to directory containing dataset.')
	parser.add_argument('--dataset', default='cleaned_lens_output.json', help='Filename of newline-delimited json dataset.')
	parser.add_argument('--train', default=0.8, type=float, help='Proportion, from 0.0 to 1.0, of dataset used for training.')
	parser.add_argument('--dev', default=0.1, type=float, help='Proportion, from 0.0 to 1.0, of dataset used for validation.')
	parser.add_argument('--skip', default=0, type=int, help='Number of training examples by which to rotate the dataset (e.g., for cross-validation).')
	parser.add_argument()

	args = parser.parse_args()
	prefix = args.prefix
	dataset = args.dataset
	train_proportion = args.train
	dev_proportion = args.dev
	skip = args.skip

	labelled = 1000 # 409
'''