import os
import sys
import re
import subprocess
import csv
from subprocess import call

javaExtension = re.compile('.*\.java$', re.IGNORECASE)
cExtension = re.compile('.*\.c[p]$', re.IGNORECASE)
issueKey = re.compile('\s[a-zA-Z0-9]+\-[0-9]+\s', re.IGNORECASE)

# constant for fileInfo
PACKAGE_NAME = 0
LOC = 1
MESSAGE = 2
COMMIT_HASH = 3


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

def getCodeChurn(filePath):
	#commitHist = subprocess.Popen("git log -p --stat " + filePath ,stdout=subprocess.PIPE, shell=True).communicate()[0]
	commitHist = subprocess.Popen("git log --oneline --shortstat " + filePath, stdout=subprocess.PIPE, shell=True).communicate()[0]

	insert = re.findall('[0-9]+\sinsertions', commitHist)
	delete = re.findall('[0-9]+\sdeletions', commitHist)

	numInsert = 0
	numDelete = 0

	if len(insert) > 0:
		for i in insert:
			try:
				numInsert = numInsert + int(i[0].split(" ")[0])
			except ValueError:
				pass
	if len(delete) > 0:
		for d in delete:
			try:
				numDelete = numDelete + int(d[0].split(" ")[0])
			except ValueError:
				pass

	return (numInsert, numDelete)

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

def iterateVersion(absRootDir, rootDir, tag):
	os.chdir(os.path.abspath(absRootDir))
	print os.getcwd(), " cur dir"
	subprocess.call("git checkout "+tag, shell=True)

	# create a directory that store the files in that particular tag
	subprocess.call("mkdir ../" + tag, shell=True)
	copySourceFiles(".", "../"+tag)
	# since we change cwd, we need to go one directory above
	# then we get the file names, package names,and LOC
	(bugdata, fileInfoMap) = getFileInfo("../"+rootDir)

	command = "git log --format=\"%an;;%cn;;%s;;%H\""
	logs = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True).communicate()[0]
	logs = logs.split("\n")

	fileInfoMap = iterateAllCommitLogs(logs, fileInfoMap)
	return (bugdata, fileInfoMap)

def computeCommitMetrics(bugdataOld, fileInfoMap):
	for fileName, fileInfo in fileInfoMap.items():
		#print "*************************begin****************************"
		numCommits = 0
		numUniqueCommitters = 0
		try:
			# get num of commits
			numCommits = len(fileInfo[MESSAGE])
			# get num of unique committers
			committers = subprocess.Popen("git log --pretty=format:\"%an\" " +
					fileName, stdout=subprocess.PIPE, shell=True).communicate()[0]
			uniq = set()
			for c in committers.split("\n"):
				uniq.add(c)
			numUniqueCommitters = len(uniq)
		except IndexError:
			#print "index error: ", fileName
			pass

		bugdataOld[fileName].append(numCommits)
		numInsert, numDelete = getCodeChurn(os.path.abspath(fileName))
		bugdataOld[fileName].append(numInsert)
		bugdataOld[fileName].append(numDelete)
		bugdataOld[fileName].append(numUniqueCommitters)
	return bugdataOld
	
def getIssueKeyInfo(fileInfoMap, rootDir):
	issueKeyInfo = {}
	# iterate through every file
	for fileName, fileInfo in fileInfoMap.items():
		# for each commit message that the file has
		try:
			bugCount = 0
			newFeatureCount = 0
			numImprovement = 0
			numTest = 0
			for msg in fileInfo[MESSAGE]:

				for matchedKey in re.findall(issueKey, msg[0]):
					matchedKey = matchedKey.strip()
						
					# guery the JIRA repo
					os.chdir("../src/")
					queryResult = subprocess.Popen("java -cp .:../google-gson-2.2.2-release/google-gson-2.2.2/gson-2.2.2.jar Jira_main " + matchedKey, stdout=subprocess.PIPE, shell=True).communicate()[0]	
					if queryResult.split(";")[1].strip() == "Bug":
						bugCount = bugCount + 1
						print "bug found!!!!!!!!!!!!!!!!!!!!!!!!!!!"
					if queryResult.split(";")[1].strip() == "New Feature":
						newFeatureCount = newFeatureCount + 1
					if queryResult.split(";")[1].strip() == "Improvement":
						numImprovement = numImprovement + 1
					if queryResult.split(";")[1].strip() == "Test":
						numTest = numTest + 1
					os.chdir("../"+rootDir)
					print matchedKey
					print queryResult
			issueKeyInfo[fileName] = {"bug": bugCount, "feature":
					newFeatureCount, "improvement": numImprovement, "test" : numTest}
			"""
			try:
				# make sure this is not the first version
				bugdataOld[fileName].append(bugCount)
			except KeyError:
				sys.stderr.write("no such file: "+ fileName+"\n")
			"""
		except IndexError:
			print "get bug count index error, no such file: ", fileName
	return issueKeyInfo#bugdataOld 
	

def main():
	root = sys.argv[1]
	v1 = sys.argv[2]
	v2 = sys.argv[3]

	absRootDir = os.path.abspath(root)
	# need to call the following two lines before computing for v2
	print "getting file info..."
	bugdataOld, fileInfoMapV1 = iterateVersion(absRootDir, root, v1)
	print "computing commit metrics..."
	bugdataOld = computeCommitMetrics(bugdataOld, fileInfoMapV1)

	print "getting bug data..."
	bugdataNew, fileInfoMapV2 = iterateVersion(absRootDir, root, v2)
	# update bugdataOld
	#bugdataOld = getBugCounts(fileInfoMapV2, bugdataOld, root)
	issueKeyInfo = getIssueKeyInfo(fileInfoMapV2, root)

	#issueKeyInfo[fileName] = {"bug": bugCount, "feature":
	#	                    newFeatureCount, "improvement": numImprovement,
	#						"test" : numTest}
	for fileName, metrics in bugdataOld.items():
		if fileName in issueKeyInfo:
			bugdataOld[fileName].append(issueKeyInfo[fileName]["feature"])
			bugdataOld[fileName].append(issueKeyInfo[fileName]["improvement"])
			bugdataOld[fileName].append(issueKeyInfo[fileName]["test"])
			bugdataOld[fileName].append(issueKeyInfo[fileName]["bug"])
		# this file does not have any issue key associated with it in commits
		else:
			bugdataOld[fileName].append(0)
			bugdataOld[fileName].append(0)
			bugdataOld[fileName].append(0)
			bugdataOld[fileName].append(0)


	bugOutputFile = csv.writer(open("../"+v1+'.csv', 'wb'), delimiter=';',	quotechar='|', quoting=csv.QUOTE_MINIMAL)
	bugOutputFile.writerow(["fileName", "project", "LOC", "numCommits",
		"numInsertions", "numDeletions", "numUniqueCommitters", "feature",
		"improvement", "test", "bugs"])
	for k,v in bugdataOld.items():
		bugOutputFile.writerow(v)
	
if __name__ == "__main__":
	main()
