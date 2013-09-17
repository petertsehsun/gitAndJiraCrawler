import os
import sys
import argparse

parser = argparse.ArgumentParser(description="Input parameters for separating the log")

parser.add_argument('--out', help='output file name', type=str, required=True)
parser.add_argument('--dat', help='input dormant bug file name', type=str, required=True)

args = parser.parse_args()

KEY = 0
DORMANT = 13
RESOLUTION = 4


for line in open(args.dat, 'r'):
	line = line.strip()
	issueInfo = line.split(';')
	if issueInfo[DORMANT] == '?':
		continue
	if issueInfo[RESOLUTION] != 'Fixed':
		continue

	projectName = issueInfo[KEY].split('-')[0].lower()

	print issueInfo[KEY], issueInfo[DORMANT], issueInfo[RESOLUTION]


