import sys
import json
import subprocess
import argparse

#curl -s -d- -X GET -H "Content-Type: application/json" https://issues.apache.org/jira/rest/api/latest/issue/COCOON-833

query = 'curl -s -d- -X GET -H "Content-Type: application/json" https://issues.apache.org/jira/rest/api/latest/issue/%s'

parser = argparse.ArgumentParser(description="Input parameters for separating the log")

parser.add_argument('--out', help='output file name', type=str, required=True)
parser.add_argument('--dat', help='input dormant bug file name', type=str, required=True)

args = parser.parse_args()

KEY = 0
DORMANT = 13
RESOLUTION = 4



def sendQuery(key):
	queryResult = subprocess.Popen(query % (key), stdout=subprocess.PIPE, shell=True).communicate()[0]

	try:
		jsonData = json.loads(queryResult)
	except ValueError:
		print 'error', key
	
	data = jsonData['fields']
	description = ""
	comments = ""

	if 'description' in data:
		if data['description'] != None:
			description += data['description']

	if 'comment' in data:
		commentData = data['comment']
		if 'comments' in commentData:
			for c in commentData['comments']:
				comments += c['body']
				#if 'body' in commentData:
				#	print c['body']
	comments = comments.replace('\n', ' ')
	description = description.replace('\n', ' ')
	return (comments, description)
	
dormant = open(args.out+'.dormant' , 'wb')
nondormant = open(args.out+'.nondormant' , 'wb')
for line in open(args.dat, 'r'):
	line = line.strip()
	issueInfo = line.split(';')
	if issueInfo[DORMANT] == '?':
		continue
	if issueInfo[RESOLUTION] != 'Fixed':
		continue

	(comments, description) = sendQuery(issueInfo[KEY])

	result = issueInfo[KEY] + "|||||" + issueInfo[DORMANT] + "|||||" + description.encode('utf-8').strip() + "|||||" + comments.encode('utf-8').strip()
	if issueInfo[DORMANT] == 'True':
		dormant.write(result+'\n')
	else:
		nondormant.write(result+'\n')

#sendQuery("COCOON-883")
