import json
from collections import defaultdict
import argparse

parser = argparse.ArgumentParser(description='main', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('--dataset', default='PeTaL', choices=['MAG', 'MeSH', 'PeTaL'])
parser.add_argument('--json-file', default='filtered.json')

args = parser.parse_args()
dataset = args.dataset
json_file = args.json_file
folder = '../'+dataset+'/'

thrs = 5
left = set()
right = set()

node2cnt = defaultdict(int)
with open(folder+json_file) as fin:
	golden = json.loads(fin.read())
	# for idx, line in enumerate(fin):
	for idx, js in enumerate(golden):
		if idx % 10000 == 0:
			print(idx)
		
		for W in js['title']:
			node2cnt[W] += 1

		for W in js['abstract']:
			node2cnt[W] += 1
		
		for A0 in js['author']:
			A = 'AUTHOR_' + str(A0)
			node2cnt[A] += 1

		for V0 in js['venue'] + js['venue_mag']:
			V = 'VENUE_' + V0.replace(' ', '_')
			node2cnt[V] += 1

with open(folder+json_file) as fin, open('network.dat', 'w') as fout:
	golden = json.loads(fin.read())
	# for idx, line in enumerate(fin):
	for idx, js in enumerate(golden):
		if idx % 10000 == 0:
			print(idx)

		P = 'PAPER_'+str(js['paper'])
		left.add(P)
		
		# P-L
		level1Labels = js['level1'] if js['level1'] else []
		level2Labels = js['level2'] if js['level2'] else []
		level3Labels = js['level3'] if js['level3'] else []
		all_labels = level1Labels + level2Labels + level3Labels
		for L0 in all_labels:
			L = 'LABEL_' + L0
			fout.write(P+' '+L+' 0 1 \n')
			right.add(L)

		# P-A
		for A0 in js['author']:
			A = 'AUTHOR_' + str(A0)
			if node2cnt[A] >= thrs:
				fout.write(P+' '+A+' 1 1 \n')
				right.add(A)

		# P-V
		for V0 in js['venue'] + js['venue_mag']:
			V = 'VENUE_' + V0.replace(' ', '_')
			fout.write(P+' '+V+' 2 1 \n')
			right.add(V)

		# P-R
		for R0 in js['reference']:
			R = 'REFP_'+str(R0)
			fout.write(P+' '+R+' 3 1 \n')
			right.add(R)

		# P-Mag
		for Mag0 in js['mag']:
			Mag = 'MAG_'+Mag0.replace(' ', '_')
			fout.write(P+' '+Mag+' 6 1 \n')
			right.add(Mag)

		# # P-Mesh
		# for Mesh0 in js['mesh']:
		# 	Mesh = 'MESH_'+Mesh0
		# 	fout.write(P+' '+Mesh+' 7 1 \n')
		# 	right.add(Mesh)

		# P-W
		words = [word for word in js['title'] + js['abstract'] if word]
		for W in words:
			if node2cnt[W] >= thrs:
				fout.write(P+' '+W+' 4 1 \n')
				right.add(W)

		# Wc-W
		for i in range(len(words)):
			Wi = words[i]
			if node2cnt[Wi] < thrs:
				continue
			for j in range(i-5, i+6):
				if j < 0 or j >= len(words) or j == i:
					continue
				Wj = words[j]
				if node2cnt[Wj] < thrs:
					continue
				fout.write(Wj+' '+Wi+' 5 1 \n')
				left.add(Wj)
			
with open('left.dat', 'w') as fou1, open('right.dat', 'w') as fou2:
	for x in left:
		fou1.write(x+'\n')
	for x in right:
		fou2.write(x+'\n')