import os
import sys
import re
import subprocess
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
	result = []
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
					result.append(fileName + ";;" + root + ";;" + str(fileSize))
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

def iterateGitTags(rootDir):
	os.chdir(os.path.abspath(rootDir))
	print os.getcwd(), " cur dir"
	tags = subprocess.Popen(['git', 'tag'], stdout=subprocess.PIPE).communicate()[0]
	tags = tags.strip()
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
		(info, fileInfoMap) = getFileInfo("../"+rootDir)

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
							#print "innnnnnnnnnnnnnn"
							fileInfoMap[f].append(message)
							fileInfoMap[f].append(commitHash)
							#print fileInfoMap[f]
							#print fileInfoMap
					except KeyError:
						print "key error"
						exit(0)
			# end of the commit logs, which produces an empty message line
		except IndexError:
			pass
			#print splittedLog
			#continue

		for fileName, fileInfo in fileInfoMap.items():
			msg = fileInfo[MESSAGE]
			for matchedKey in re.findall(issueKey, msg):
				print fileName, msg, matchedKey
				print fileInfo
		

def main():
	root = sys.argv[1]
	iterateGitTags(root)
	#result = getSourceCodeFiles(root)

	#for r in result:
	#	print r
	
if __name__ == "__main__":
	main()
