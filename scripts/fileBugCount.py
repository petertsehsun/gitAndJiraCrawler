import os
import sys
import argparse
import subprocess
import re
import ast

parser = argparse.ArgumentParser(description="Input parameters for separating the log")

parser.add_argument('--out', help='output file name', type=str, required=True)
parser.add_argument('--dat', help='input dormant bug file name', type=str, required=True)

args = parser.parse_args()

KEY = 0
DORMANT = 13
RESOLUTION = 4
VERSION = 5

#gitGrep = "git log --all --oneline --grep='%s' | grep %s"
gitGrep = 'git log --all --oneline | grep "%s[^0-9]*"'

fileCount = "git log --oneline --name-status %s -1"

#git show cHash:filePath
fileContent = "git show %s:%s"

writer = open(args.out, 'wb')

#git log --follow --oneline dependencies/i18n/src/main/java/org/apache/abdera/i18n/text/CharUtils.java
commitHistory = "git log --follow --oneline %s"

def countFiles(projectName, issueInfo):
	os.chdir('../projects/%s' % (projectName))

	allCommits = subprocess.Popen(gitGrep % (issueInfo[KEY]), stdout=subprocess.PIPE, shell=True).communicate()[0].strip()	

	totalFileCount = 0
	for c in allCommits.strip().split('\n'):
					cHash = c.split(' ')[0]
					#print c
					commitMsg = ' '.join(c.split(' ')[1:])
					if issueInfo[KEY].lower() in commitMsg.lower():
						fileNames = subprocess.Popen(fileCount % (cHash), stdout=subprocess.PIPE, shell=True).communicate()[0].strip()	
						#print fileNames
						for i, f in enumerate(fileNames.split('\n')):
							if i == 0:
								continue
							if f != "":
								#print f, '<---'
								f = f[1:].strip()
								# get file LOC
								#print '***********1************'
								#print fileContent % (cHash, f)
								LOC = subprocess.Popen(fileContent % (cHash, f), stdout=subprocess.PIPE, shell=True).communicate()[0].strip().count('\n')
								#print '************************'
								#print '***********2************'
								# get total number of prior commit
								#print (commitHistory % (f))
								commits = subprocess.Popen(commitHistory % (f), stdout=subprocess.PIPE, shell=True).communicate()[0].strip()
								#print '************************'

								startCount = False
								commitCount = 0
								for cc in commits.split('\n'):
									if startCount == True:
										commitCount += 1
									if cc.split(' ')[0] == cHash:
										startCount = True
									
								#print '--------------', f+','+str(LOC)+','+str(commitCount)+','+issueInfo[VERSION]
								writer.write(f+','+str(LOC)+','+str(commitCount)+','+ast.literal_eval(issueInfo[VERSION])[0].split('#')[0] + ','+ issueInfo[KEY] + ',' + issueInfo[KEY].split('-')[0]+','+issueInfo[DORMANT]+'\n')

						totalFileCount += fileNames.count('\n')	
						


	#print issueInfo[KEY], totalFileCount, issueInfo[DORMANT]
	os.chdir('../../scripts')
	return totalFileCount




for line in open(args.dat, 'r'):
	line = line.strip()
	issueInfo = line.split(';')
	if issueInfo[DORMANT] == '?':
		continue
	if issueInfo[RESOLUTION] != 'Fixed':
		continue

	projectName = issueInfo[KEY].split('-')[0].lower()

	#print issueInfo[KEY], issueInfo[DORMANT], issueInfo[RESOLUTION]
	totalCount = 0
	if projectName == 'axis':
					totalCount += countFiles('axis1', issueInfo)
					totalCount += countFiles('axis2-c', issueInfo)
					totalCount += countFiles('axis2-java', issueInfo)
					
	else:
					totalCount += countFiles(projectName, issueInfo)

	#print issueInfo[KEY], totalCount, issueInfo[DORMANT]


