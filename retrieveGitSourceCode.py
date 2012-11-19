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
	commitHist = subprocess.Popen("git log -p --stat " + filePath,
			stdout=subprocess.PIPE, shell=True).communicate()[0]
	insert = re.findall('[0-9]+\sinsertions', commitHist)
	delete = re.findall('[0-9]+\sdeletions', commitHist)

	numInsert = 0
	numDelete = 0

	if len(insert) > 0:
		numInsert = insert[0].split(" ")[0]

	if len(delete) > 0:
		numDelete = delete[0].split(" ")[0]

	return (numInsert, numDelete)

def iterateGitTags(rootDir):
	os.chdir(os.path.abspath(rootDir))
	print os.getcwd(), " cur dir"
	tags = subprocess.Popen(['git', 'tag'], stdout=subprocess.PIPE).communicate()[0]
	tags = tags.strip()
	tags = "dummy\nv1.5.3\nv1.5.4"
	prevTag = None
	# checkout each tag (version) and iterate each version
	for (i, t) in enumerate(tags.split("\n")):
		if i == 0:
			continue
		print t
		# need to fix this line
		subprocess.call("git checkout " + t, shell=True)

		# create a directory that store the files in that particular tag
		subprocess.call("mkdir ../" + t, shell=True)
		copySourceFiles(".", "../"+t)

		# since we change cwd, we need to go one directory above
		# then we get the file names, package names,and LOC
		(bugdata, fileInfoMap) = getFileInfo("../"+rootDir)

		# command for getting commit logs
		# author;;commiters;;commit message;;commit hash
		command = "git log --format=\"%an;;%cn;;%s;;%H\""
		logs = subprocess.Popen(command.split(), stdout=subprocess.PIPE).communicate()[0]
		#print logs
		logs = logs.split("\n")


		# iterate through each commit
		try:
			for log in logs:
				log = log.replace("\"", "")
				splittedLog = log.split(";;")
				message = splittedLog[MESSAGE].strip()
				commitHash = splittedLog[COMMIT_HASH].strip()
				command = "git show --pretty=\"format:\" --name-only "+commitHash

				# files that are associated with the commit
				files = subprocess.Popen(command,
						stdout=subprocess.PIPE, shell=True).communicate()[0]	
				#print files
				files = files.split("\n")
				for f in files:
					try:
						# if this file is in the list of source code files that
						# we get from the git 
						if f in fileInfoMap:
							#print fileInfoMap[f]
							if len(fileInfoMap[f]) <= MESSAGE:
								fileInfoMap[f].append([])

							fileInfoMap[f][MESSAGE].append((message, commitHash))
							#print fileInfoMap[f]
							#exit(0)
							#print fileInfoMap
							
					except KeyError:
						print "key error"
						exit(0)
			# end of the commit logs, which produces an empty message line
		except IndexError:
			pass
			#print splittedLog
			#continue
		# iterate through every file
		for fileName, fileInfo in fileInfoMap.items():
			#print "*************************begin****************************"
			numCommits = 0
			# for each commit message that the file has
			try:
				bugCount = 0
				for msg in fileInfo[MESSAGE]:
					#print "----------------- ", msg, " ------------------"
					numCommits = numCommits + 1
					# first vision - no bug data avail
					if prevTag == None:
						continue
					for matchedKey in re.findall(issueKey, msg[0]):
						matchedKey = matchedKey.strip()
						
						# guery the JIRA repo
						os.chdir("../src/")
						print os.getcwd(), " cur dir"
						print matchedKey
						queryResult = subprocess.Popen("java -cp .:../google-gson-2.2.2-release/google-gson-2.2.2/gson-2.2.2.jar Jira_main " + matchedKey, stdout=subprocess.PIPE, shell=True).communicate()[0]	
						print queryResult
						if queryResult.split(";")[1].strip() == "Bug":
							bugCount = bugCount + 1
						os.chdir("../"+rootDir)
						print os.getcwd(), " cur dir"
				try:
					# make sure this is not the first version
					if prevTag != None:
						#print(bugdataOld[fileName])
						bugdataOld[fileName].append(bugCount)
						
				except KeyError:
					sys.stderr.write("no such file: "+ fileName+ " version: "+
							t+"\n")
				bugdata[fileName].append(numCommits)
				numInsert, numDelete = getCodeChurn(os.path.abspath(fileName))
				bugdata[fileName].append(numInsert)
				bugdata[fileName].append(numDelete)
				#print "*************************end****************************"
			except IndexError:
				print "index error: ", t

		"""
		bugOutputFile = csv.writer(open("../"+t+'.csv', 'wb'), delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
		bugOutputFile.writerow(["fileName", "project", "LOC", "numCommits", "numInsertions", "numDeletions"])
		for k,v in bugdata.items():
			bugOutputFile.writerow(v)
		"""
		# generate bugdata
		if prevTag != None:	
			bugOutputFile = csv.writer(open("../"+prevTag+'.csv', 'wb'), delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
			bugOutputFile.writerow(["fileName", "project", "LOC", "numCommits",
				"numInsertions", "numDeletions", "bugs"])
			for k,v in bugdataOld.items():
				bugOutputFile.writerow(v)
		
		prevTag = t
		bugdataOld = bugdata
			 
	

def main():
	root = sys.argv[1]
	bugdata = iterateGitTags(root)
	#result = getSourceCodeFiles(root)

	#for r in result:
	#	print r
	
if __name__ == "__main__":
	main()
