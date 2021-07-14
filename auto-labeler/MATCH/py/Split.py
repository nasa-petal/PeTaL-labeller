'''
	split.py
'''

import json
# import argparse
# import sys
import click
import os
import logging

# parser = argparse.ArgumentParser(description='main', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
# parser.add_argument('--prefix', default='MATCH/PeTaL', help='Path from current working directory to directory containing dataset.')
# parser.add_argument('--dataset', default='cleaned_lens_output.json', help='Filename of newline-delimited json dataset.')
# parser.add_argument('--train', default=0.8, type=float, help='Proportion, from 0.0 to 1.0, of dataset used for training.')
# parser.add_argument('--dev', default=0.1, type=float, help='Proportion, from 0.0 to 1.0, of dataset used for validation.')
# parser.add_argument('--skip', default=0, type=int, help='Number of training examples by which to rotate the dataset (e.g., for cross-validation).')
# parser.add_argument()

# args = parser.parse_args()
# prefix = args.prefix
# dataset = args.dataset
# train_proportion = args.train
# dev_proportion = args.dev
# skip = args.skip

# labelled = 1000 # 409



@click.command()
@click.option('--prefix', default='MATCH/PeTaL', help='Path from current working directory to directory containing dataset.')
@click.option('--dataset', default='cleaned_lens_output.json', help='Filename of newline-delimited json dataset.')
@click.option('--train', default=0.8, type=click.FLOAT, help='Proportion, from 0.0 to 1.0, of dataset used for training.')
@click.option('--dev', default=0.1, type=click.FLOAT, help='Proportion, from 0.0 to 1.0, of dataset used for validation.')
@click.option('--skip', default=0, type=click.INT, help='Number of training examples by which to rotate the dataset (e.g., for cross-validation).')
@click.option('--verbose', '-v', type=click.BOOL, is_flag=True, default=False, help='Verbose output.')

def main(prefix,
		dataset,
		train=0.8,
		dev=0.1,
		skip=0,
		verbose=False):
	"""Performs train-test split on newline-delimited json file.	

	Args:
		prefix (string): Path from current working directory to directory containing dataset.
		dataset (string): Filename of newline-delimited json dataset.
		train (float): Proportion, from 0.0 to 1.0, of dataset used for training.
		dev (float): Proportion, from 0.0 to 1.0, of dataset used for validation.
		skip (int): Number of training examples by which to rotate the dataset (e.g., for cross-validation).
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
	train_path = os.path.join(prefix, 'train.json')
	dev_path = os.path.join(prefix, 'dev.json')
	test_path = os.path.join(prefix, 'test.json')

	logger.info(f"Transforming from {dataset_path} to {train_path}, {dev_path}, and {test_path}.")

	train_proportion, dev_proportion = train, dev
	train_labels = set()
	with open(dataset_path) as fin:
		tot = sum(1 for _ in fin)
	if verbose:
		logger.info(f"{tot} total examples in dataset.")

	with open(dataset_path) as fin, open(train_path, 'w') as fou1, open(dev_path, 'w') as fou2, open(test_path, 'w') as fou3:
		for idx, line in enumerate(fin):
			if idx < skip:
				continue
			js = json.loads(line)

			if (idx - skip) % tot < tot * train_proportion:
				for l in js['label']:
					train_labels.add(l)
				fou1.write(json.dumps(js)+'\n')
			
			else:
				label_new = []
				for l in js['label']:
					if l in train_labels:
						label_new.append(l)
				if len(label_new) == 0:
					continue

				js['label'] = label_new
				if (idx - skip) % tot < tot * (train_proportion + dev_proportion):
					fou2.write(json.dumps(js)+'\n')
				else:
					fou3.write(json.dumps(js)+'\n')
		
		fin.seek(0)

		for idx, line in enumerate(fin):
			if idx >= skip:
				break
			js = json.loads(line)

			if (idx - skip) % tot < tot * train_proportion:
				for l in js['label']:
					train_labels.add(l)
				fou1.write(json.dumps(js)+'\n')
			
			else:
				label_new = []
				for l in js['label']:
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

	# with open('cleaned_lens_output.json') as fin, open('train.json', 'w') as fou1, open('dev.json', 'w') as fou2, open('test.json', 'w') as fou3:
	# 	labelled_so_far = 0
	# 	for idx, line in enumerate(fin):
	# 		js = json.loads(line)
			
	# 		if js['label']:
	# 			if labelled_so_far < labelled * 0.8:
	# 				for l in js['label']:
	# 					train_labels.add(l)
	# 				fou1.write(json.dumps(js) + '\n')
	# 			else:
	# 				label_new = []
	# 				for l in js['label']:
	# 					if l in train_labels:
	# 						label_new.append(l)
	# 				if len(label_new) == 0:
	# 					continue

	# 				js['label'] = label_new
	# 				fou2.write(json.dumps(js)+'\n')
	# 			labelled_so_far += 1
	# 	fin.seek(0)
	# 	for idx, line in enumerate(fin):
	# 		js = json.loads(line)
	# 		if not js['label']:
	# 			fou3.write(json.dumps(js)+'\n')

	# print(len(train_labels))

if __name__ == "__main__":
	main()