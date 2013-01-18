import os
import sys
import re
import subprocess
import csv
from subprocess import call
from numpy import median
from itertools import izip
import json

javaExtension = re.compile('.*\.java$', re.IGNORECASE)
cExtension = re.compile('.*\.c[p]$', re.IGNORECASE)
issueKey = re.compile('[a-zA-Z0-9]+\-[0-9]+', re.IGNORECASE)
issueKeys = {}

# constant for fileInfo
PACKAGE_NAME = 0
LOC = 1
MESSAGE = 2
COMMIT_HASH = 3

def getAffectedVersion(issue):
	affected_versions = []
	for v in issue['fields']['versions']:
		affected_versions.append(v['name'])
	affected_versions.sort()
	return affected_versions

def getAllIssues(affectedVersion, project):
	query =	'curl -s -d- -X GET -H "Content-Type: application/json" https://issues.apache.org/jira/rest/api/latest/search?jql=project='+ project + '%20AND%20affectedVersion=\\"'+affectedVersion+'\\"'	
	query_result = subprocess.Popen(query, stdout=subprocess.PIPE, shell=True).communicate()[0]
	json_data = json.loads(query_result)
	if 'issues' not in json_data:
		return
	for issue in json_data['issues']:
		affected_versions = getAffectedVersion(issue)
		issueKeys[issue['key']] = [issue['fields']['issuetype']['name'], issue['fields']['priority']['name'], affected_versions]



def getFileInfo(rootDir):
	result = {}
	info = {}
	for root, subFolder, files in os.walk(rootDir):
		for fileName in files:
			if (re.match(javaExtension, fileName) or re.match(cExtension,
				fileName)):
					#command = "wc -l " + os.path.abspath(os.path.join(root, fileName))
					#fileSize = subprocess.check_output(command, shell=True)

					fileSize = len(open(os.path.abspath(os.path.join(root,
						fileName))).read().splitlines())

					#print fileSize, root, fileSize, " 1234"

					# file name; package name; file size
					#result.append(fileName + ";;" + root + ";;" + str(fileSize))
					result["/".join(os.path.join(root,
						fileName).split("/")[2:])] = [fileName, root,
								str(fileSize)]
					info["/".join(os.path.join(root, fileName).split("/")[2:])] = [root, fileSize]
					#print "/".join(os.path.join(root, fileName).split("/")[2:])

	return (result, info)


def copySourceFiles(srcDir, destDir):
	for root, subFolder, files in os.walk(srcDir):
		for fileName in files:
			if (re.match(javaExtension, fileName) or re.match(cExtension,
				fileName)):
				src = os.path.abspath(os.path.join(root, fileName))
				#print src, destDir
				subprocess.call("cp " + src + " " + destDir, shell=True)
				#call(["cp", src , os.path.join(folder, version_num+"#"+filename)], shell=True)


def iterateAllCommitLogs(logs, fileInfoMap):
	for log in logs:
		try:
			log = log.replace("\"", "")
			splittedLog = log.split(";;")
			message = splittedLog[MESSAGE].strip()
			commitHash = splittedLog[COMMIT_HASH].strip()
			# show the files that are committed by this commit
			""" this line sometimes throws exceptioni: /bin/sh: 1:
				fe281a90f24550b1276c2771f4ecdcbfa4c5a54a: not found """
			command = "git show --pretty=\"format:\" --name-only "+commitHash
			
			files = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True).communicate()[0]	
			files = files.split("\n")
			for f in files:
				try:
					# if this file is in the list of source code files that
					# we get from the git 
					if f in fileInfoMap:
						#print "innnnnn"
						if len(fileInfoMap[f]) <= MESSAGE:
							fileInfoMap[f].append([])
						fileInfoMap[f][MESSAGE].append((message, commitHash))
							
				except KeyError:
					print "key error"

		# end of the commit logs, which produces an empty message line
		except IndexError:
			print "indexError -- 1"
			pass
	return fileInfoMap

def iterateVersion(absRootDir, rootDir, tag, projectName, v1, v2):
	os.chdir(os.path.abspath(absRootDir))
	#print os.getcwd(), " cur dir"
	subprocess.call("git checkout "+tag, shell=True)

	# create a directory that store the files in that particular tag
	#subprocess.call("mkdir ../" + tag+"-"+projectName, shell=True)
	#copySourceFiles(".", "../"+tag+"-"+projectName)
	# since we change cwd, we need to go one directory above
	# then we get the file names, package names,and LOC
	(bugdata, fileInfoMap) = getFileInfo("../"+rootDir)

	command = "git log " +v1+".."+v2+ " --format=\"%an;;%cn;;%s;;%H\""
	logs = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True).communicate()[0]
	logs = logs.split("\n")

	fileInfoMap = iterateAllCommitLogs(logs, fileInfoMap)
	return (bugdata, fileInfoMap)

def getOwnershipMetrics(authors, fileName, v1, v2):
	totalCommits = subprocess.Popen("git log " +v1+".."+v2+ " --oneline " + fileName, stdout=subprocess.PIPE, shell=True).communicate()[0]
	minor = 0
	major = 0
	ownership = 0
	totalCommitLen = len(totalCommits.strip().split("\n"))
	for author in authors:
		authorCommits = subprocess.Popen("git log " +v1+".."+v2+ " --author=\"" + author + "\" --oneline " + fileName, stdout=subprocess.PIPE, shell=True).communicate()[0]
		authorCommitLen = len(authorCommits.strip().split("\n"))
		ownerPercent = float(authorCommitLen)/totalCommitLen 
		if ownerPercent <= 0.05 and authorCommitLen >= 1:
			minor = minor + 1
		else:
			major = major + 1
		if ownerPercent > ownership:
			ownership = ownerPercent
	return (minor, major, ownership)

def getAuthorGeneralExp(authorName, v1, v2):
	#exp = subprocess.Popen("git log " +v1+".."+v2+ " --author=\"" + authorName + "\" --oneline --shortstat", stdout=subprocess.PIPE, shell=True).communicate()[0]
	exp = subprocess.Popen("git log --author=\"" + authorName + "\" --oneline --shortstat", stdout=subprocess.PIPE, shell=True).communicate()[0]
	insert = re.findall('[0-9]+\sinsertions', exp)
	delete = re.findall('[0-9]+\sdeletions', exp)

	numInsert = 0
	numDelete = 0

	if len(insert) > 0:
		for i in insert:
			try:
				numInsert = numInsert + int(i.split(" ")[0])
			except ValueError:
				pass
	if len(delete) > 0:
		for d in delete:
			try:
				numDelete = numDelete + int(d.split(" ")[0])
			except ValueError:
				pass
	return numInsert+numDelete

def getCodeChurn(filePath, v1, v2):
	#commitHist = subprocess.Popen("git log -p --stat " + filePath ,stdout=subprocess.PIPE, shell=True).communicate()[0]
	commitHist = subprocess.Popen("git log " +v1+".."+v2+ " --oneline --shortstat " + filePath, stdout=subprocess.PIPE, shell=True).communicate()[0]

	insert = re.findall('[0-9]+\sinsertions', commitHist)
	delete = re.findall('[0-9]+\sdeletions', commitHist)

	numInsert = 0
	numDelete = 0

	if len(insert) > 0:
		for i in insert:
			try:
				numInsert = numInsert + int(i.split(" ")[0])
			except ValueError:
				pass
	if len(delete) > 0:
		for d in delete:
			try:
				numDelete = numDelete + int(d.split(" ")[0])
			except ValueError:
				pass

	return (numInsert, numDelete)

def allAuthorExp(v1, v2):
	committers = subprocess.Popen("git log " +v1+".."+v2+ " --pretty=format:\"%an\" ", stdout=subprocess.PIPE, shell=True).communicate()[0]
	
	uniq = set()
	for c in committers.split("\n"):
		uniq.add(c)
	authorExp = {}
	for author in uniq:
		authorExp[author] = getAuthorGeneralExp(author, v1, v2)
	return authorExp

def computeCommitMetrics(bugdataOld, fileInfoMap, v1, v2):
	authorExp = allAuthorExp(v1, v2)
	generalExpCutoff = median(authorExp.values())
	for fileName, fileInfo in fileInfoMap.items():
		#print "*************************begin****************************"
		numCommits = 0
		numUniqueCommitters = 0
		minor = 0
		major = 0
		ownership = 0
		numGeneralExpAuthor = 0
		totalFileExp = 0
		try:
			# get num of commits
			if len(fileInfo) > MESSAGE: 
				numCommits = len(fileInfo[MESSAGE])
			else:
				numCommits = 0
			# get num of unique committers
			committers = subprocess.Popen("git log " +v1+".."+v2+ " --pretty=format:\"%an\" " +
					fileName, stdout=subprocess.PIPE, shell=True).communicate()[0]
			uniq = set()
			for c in committers.strip().split("\n"):
				if c != "":
					uniq.add(c)
			numUniqueCommitters = len(uniq)
			# this metric may be wrong
			try:
				for author in uniq:
					if author in authorExp:
						totalFileExp = totalFileExp + authorExp[author]
						if authorExp[author] > generalExpCutoff:
							numGeneralExpAuthor = numGeneralExpAuthor + 1
			except KeyError:
				print "key error"
			(minor, major, ownership) = getOwnershipMetrics(uniq, fileName, v1, v2)
		except IndexError, e:
			print "index error: ", fileName, e
			exc_type, exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]      
			print(exc_type, fname, exc_tb.tb_lineno)
			pass
		# two more metrics: number of general exp developers
		# and number of specific exp developers
		bugdataOld[fileName].append(numCommits)
		numInsert, numDelete = getCodeChurn(os.path.abspath(fileName), v1, v2)
		bugdataOld[fileName].append(numInsert)
		bugdataOld[fileName].append(numDelete)
		bugdataOld[fileName].append(numUniqueCommitters)
		bugdataOld[fileName].append(totalFileExp)
		bugdataOld[fileName].append(minor)
		bugdataOld[fileName].append(major)
		bugdataOld[fileName].append(ownership)
		bugdataOld[fileName].append(numGeneralExpAuthor)
		#print numCommits, numInsert, numDelete, numUniqueCommitters, totalFileExp, minor, major, ownership, numGeneralExpAuthor
	return bugdataOld
	
def getIssueKeyInfo(fileInfoMap, rootDir, _vcur, projectName):
	issueKeyInfo = {}

	keysFromJira = set()
	keysFromLogs = set()
	alreadyInIssueKey = set()
	keysFromLogsNoAffectedVersion = set()
	
	getAllIssues(_vcur, projectName) # must be called before issueKeyInfo
	
	# iterate through every file
	for fileName, fileInfo in fileInfoMap.items():
		# for each commit message that the file has
		try:
			# bug types
			bugCount = 0
			numBlocker = 0
			numCritical = 0
			numMajor = 0
			numMinor = 0
			numTrivial = 0
			#
			newFeatureCount = 0
			numImprovement = 0
			numTest = 0
			# avoid sending request to JIRA all the time
			alreadyMatched = {}
			for msg in fileInfo[MESSAGE]:
				m = msg[0].replace(':', '-')
				for matchedKey in re.findall(issueKey, m):
					matchedKey = matchedKey.strip()
					matchedKey = matchedKey.upper()
					# do not double count issue keys
					if matchedKey in issueKeys:
						#print "double count"
						alreadyInIssueKey.add(matchedKey)
						continue	
					#################################
					if matchedKey not in alreadyMatched:
						# guery the JIRA repo
						query =	'curl -s -d- -X GET -H "Content-Type: application/json" https://issues.apache.org/jira/rest/api/latest/issue/'+matchedKey
						query_result = subprocess.Popen(query, stdout=subprocess.PIPE, shell=True).communicate()[0]
						#key; type; resolution; priority; affectedVersions
						json_data = json.loads(query_result)
						try:
							affectedVersion = json_data['fields']['versions']
						except KeyError:
							# no such issue key
							continue
						if affectedVersion == None:
							affectedVersion = "None"
							keysFromLogsNoAffectedVersion.add(json_data['key'])
							#print "affected version is none " + json_data['key']
						else:
							affectedVersion = str(getAffectedVersion(json_data)[0])

					#queryResult = json_data['key'] + ";" + json_data['fields']['issuetype']['name'] + ";" + json_data['fields']['resolution'] + ";" + json_data['fields']['priority']['name'] + ";" + affectedVersion

						queryResult = str(json_data['key']) + ";" + str(json_data['fields']['issuetype']['name']) + ";" + str(json_data['fields']['resolution']['name']) + ";" + str(json_data['fields']['priority']['name']) + ";"
						alreadyMatched[matchedKey] = queryResult
					
					#https://issues.apache.org/jira/rest/api/latest/issue/AXIS2-5470
					if matchedKey in alreadyMatched:
						queryResult = alreadyMatched[matchedKey]
					#################################



					######### affected version is not true #########
					if affectedVersion != _vcur:
						keysFromLogs.add((matchedKey, affectedVersion))
						continue
						#print "previously found"
					#################################
					# is this a bug, improvement, new feature, or test
					if queryResult.split(";")[1].strip() == "Bug":
						bugCount = bugCount + 1
						# is a bug, what is the priority
						if queryResult.split(";")[3].strip() == "Blocker":
							numBlocker = numBlocker + 1
						if queryResult.split(";")[3].strip() == "Critical":
							numCritical = numCritical + 1
						if queryResult.split(";")[3].strip() == "Major":
							numMajor = numMajor + 1
						if queryResult.split(";")[3].strip() == "Minor":
							numMinor = numMinor + 1
						if queryResult.split(";")[3].strip() == "Trivial":
							numMinor = numMinor + 1
						#print "bug found!!!!!!!!!!!!!!!!!!!!!!!!!!!"
					if queryResult.split(";")[1].strip() == "New Feature":
						newFeatureCount = newFeatureCount + 1
					if queryResult.split(";")[1].strip() == "Improvement":
						numImprovement = numImprovement + 1
					if queryResult.split(";")[1].strip() == "Test":
						numTest = numTest + 1
					#print matchedKey
					#print queryResult
			issueKeyInfo[fileName] = {"bug": bugCount, "feature":
					newFeatureCount, "improvement": numImprovement, "test" : numTest, "blocker": numBlocker, "critical": numCritical, "major": numMajor, "minor": numMinor, "trivial": numTrivial}
			"""
			try:
				# make sure this is not the first version
				bugdataOld[fileName].append(bugCount)
			except KeyError:
				sys.stderr.write("no such file: "+ fileName+"\n")
			"""
		except IndexError, e:
			#print "get bug count index error, no such file: ", fileName
			#exc_type, exc_obj, exc_tb = sys.exc_info()
			#fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]      
			#print(exc_type, fname, exc_tb.tb_lineno)
			pass

	print "Now from JIRA to git..."
	# now need to update issueKeyInfo based on the JIRA data
	# get all the commits
	command = 'git rev-list --all  --format="%an;;%cn;;%s;;%H"'
	allCommits = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True).communicate()[0]	
	allCommits = allCommits.split('\n')
	for i, commitInfo in enumerate(allCommits):
		if (i+1) % 2 != 0:
			continue
		# find the files associated with the commit and update
		#print commitInfo
		splittedLog = commitInfo.split(";;")
		message = splittedLog[MESSAGE].strip()
		message = message.replace("\"", "")
		for matchedKey in re.findall(issueKey, message):
			matchedKey = matchedKey.upper()
			matchedKey = matchedKey.strip()
			if matchedKey in issueKeys:
				# first affected version is not the version of interest
				if str(issueKeys[matchedKey][2][0]).lower() != _vcur.lower():
					#print matchedKey + " not in the right version"
					continue # skip
				#print "matched key ", issueKeys[matchedKey]
				keysFromJira.add((matchedKey, issueKeys[matchedKey][2][0]))

				commitHash = splittedLog[COMMIT_HASH].strip()
				# show the files that are committed by this commit
				""" this line sometimes throws exceptioni: /bin/sh: 1:
					fe281a90f24550b1276c2771f4ecdcbfa4c5a54a: not found """
				command = "git show --pretty=\"format:\" --name-only "+commitHash
			
				files = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True).communicate()[0]	
				files = files.split("\n")
				for f in files:
					if f not in issueKeyInfo:
						bugCount = 0
						numBlocker = 0
						numCritical = 0
						numMajor = 0
						numMinor = 0
						numTrivial = 0
			
						newFeatureCount = 0
						numImprovement = 0
						numTest = 0
				#issueKeyInfo[fileName] = {"bug": bugCount, "feature":
			#		newFeatureCount, "improvement": numImprovement, "test" : numTest, "blocker": numBlocker, "critical": numCritical, "major": numMajor, "minor": numMinor, "trivial": numTrivial}
			
					else:
						bugCount = issueKeyInfo[f]["bug"]
						numBlocker = issueKeyInfo[f]["blocker"]
						numCritical = issueKeyInfo[f]["critical"]
						numMajor = issueKeyInfo[f]["major"]
						numMinor = issueKeyInfo[f]["minor"]
						numTrivial = issueKeyInfo[f]["trivial"]
			
						newFeatureCount = issueKeyInfo[f]["feature"]
						numImprovement = issueKeyInfo[f]["improvement"]
						numTest = issueKeyInfo[f]["test"]


					if issueKeys[matchedKey][0] == "Bug":
						bugCount = bugCount + 1
						# is a bug, what is the priority
						if issueKeys[matchedKey][1] == "Blocker":
							numBlocker = numBlocker + 1
						if issueKeys[matchedKey][1] == "Critical":
							numCritical = numCritical + 1
						if issueKeys[matchedKey][1] == "Major":
							numMajor = numMajor + 1
						if issueKeys[matchedKey][1] == "Minor":
							numMinor = numMinor + 1
						if issueKeys[matchedKey][1] == "Trivial":
							numMinor = numMinor + 1
						#print "bug found!!!!!!!!!!!!!!!!!!!!!!!!!!!"

						#print f
					if issueKeys[matchedKey][0] == "New Feature":
						newFeatureCount = newFeatureCount + 1
					if issueKeys[matchedKey][0] == "Improvement":
						numImprovement = numImprovement + 1
					if issueKeys[matchedKey][0] == "Test":
						numTest = numTest + 1
			

					issueKeyInfo[f] = {"bug": bugCount, "feature": newFeatureCount, "improvement": numImprovement, "test" : numTest, "blocker": numBlocker, "critical": numCritical, "major": numMajor, "minor": numMinor, "trivial": numTrivial}

	res = []
	for e in keysFromLogs:
		res.append(str(e))
	print "keys from logs that have affected version"
	res.sort()
	print res	
	
	res = []
	for e in keysFromJira:
		res.append(str(e))
	print
	print "keys from Jira"
	res.sort()
	print res

	res = []
	for e in alreadyInIssueKey:
		res.append(str(e))
	print
	print "overlaps"
	res.sort()
	print res

	res = []
	for e in keysFromLogsNoAffectedVersion:
		res.append(str(e))
	print
	print "no affected version"
	res.sort()
	print res




	return issueKeyInfo#bugdataOld 
	

def main():
	root = sys.argv[1]
	vpre = sys.argv[2]
	vcur = sys.argv[3]
	vpost = sys.argv[4]
	projectName = sys.argv[5]
	_vcur = sys.argv[6] # used for making jira query

	# need to double check git tagv1...tagv2
	# how does since and until work
	# should be vcur, vpost, vpostpost to get commits from
	# v1.4 to v1.5, and get the commits from v1.5 to v1.6
	# if we are interested in data in v1.4

	absRootDir = os.path.abspath(root)
	# need to call the following two lines before computing for v2
	#print "getting file info..."
	# bugdataOld contains: file path, package, and file size
	bugdataOld, fileInfoMapV1 = iterateVersion(absRootDir, root, vcur, projectName, vpre, vcur)
	#print "computing commit metrics..."
	# add metrics to bugdataOld
	#bugdataOld = computeCommitMetrics(bugdataOld, fileInfoMapV1, vpre, vcur)

	#print "getting bug data..."
	# bugdataNew is for next version of does not need metrics
	# it is only used for finding commit logs (which is done using fileInfoMapV2)
	bugdataNew, fileInfoMapV2 = iterateVersion(absRootDir, root, vcur, projectName, vcur, vpost)

	issueKeyInfo = getIssueKeyInfo(fileInfoMapV2, root, _vcur, projectName)


	for fileName, metrics in bugdataOld.items():
		if fileName in issueKeyInfo:
			bugdataOld[fileName].append(issueKeyInfo[fileName]["feature"])
			bugdataOld[fileName].append(issueKeyInfo[fileName]["improvement"])
			bugdataOld[fileName].append(issueKeyInfo[fileName]["test"])
			bugdataOld[fileName].append(issueKeyInfo[fileName]["bug"])
			bugdataOld[fileName].append(issueKeyInfo[fileName]["blocker"])
			bugdataOld[fileName].append(issueKeyInfo[fileName]["critical"])
			bugdataOld[fileName].append(issueKeyInfo[fileName]["major"])
			bugdataOld[fileName].append(issueKeyInfo[fileName]["minor"])
			bugdataOld[fileName].append(issueKeyInfo[fileName]["trivial"])
		# this file does not have any issue key associated with it in commits
		else:
			bugdataOld[fileName].append(0)
			bugdataOld[fileName].append(0)
			bugdataOld[fileName].append(0)
			bugdataOld[fileName].append(0)
			bugdataOld[fileName].append(0)
			bugdataOld[fileName].append(0)
			bugdataOld[fileName].append(0)
			bugdataOld[fileName].append(0)
			bugdataOld[fileName].append(0)


	bugOutputFile = csv.writer(open("../"+vcur+"-"+projectName+'.csv', 'wb'), delimiter=';',	quotechar='|', quoting=csv.QUOTE_MINIMAL)
	bugOutputFile.writerow(["fileName", "project", "LOC", "numCommits",
		"numInsertions", "numDeletions", "numUniqueCommitters", "fileExp", "minor", "major", "ownership", "numGeneralExp", "feature",	"improvement", "test", "bugs", "blocker", "critical", "major", "minor", "trivial"])
	for k,v in bugdataOld.items():
		bugOutputFile.writerow(v)
	
if __name__ == "__main__":
	main()
