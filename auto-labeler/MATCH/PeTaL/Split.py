import json
import argparse
import sys

parser = argparse.ArgumentParser(description='main', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('--train', default=0.8, type=float)
parser.add_argument('--dev', default=0.1, type=float)
parser.add_argument('--skip', default=0, type=int)

args = parser.parse_args()
train_proportion = args.train
dev_proportion = args.dev
skip = args.skip

train_labels = set()
# labelled = 1000 # 409
tot = 1000

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

with open('cleaned_lens_output.json') as fin, open('train.json', 'w') as fou1, open('dev.json', 'w') as fou2, open('test.json', 'w') as fou3:
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
				
print(len(train_labels))