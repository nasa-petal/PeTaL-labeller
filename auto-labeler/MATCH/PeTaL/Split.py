import json

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
		js = json.loads(line)

		if idx < tot * 0.8:
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
			if idx < tot * 0.9:
				fou2.write(json.dumps(js)+'\n')
			else:
				fou3.write(json.dumps(js)+'\n')
				
print(len(train_labels))