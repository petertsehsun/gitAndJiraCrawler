import sys
import re
import json
import subprocess
import csv
from subprocess import call

javaExtension = re.compile('.*\.java$', re.IGNORECASE)
cExtension = re.compile('.*\.c[p]$', re.IGNORECASE)
issueKey = re.compile('[a-zA-Z0-9]+\-[0-9]+', re.IGNORECASE)
issueKeys = {}

def getAffectedVersion(issue):
    if issue['fields']['versions'] == None:
        return "None"
    affected_versions = []
    for v in issue['fields']['versions']:
        if 'releaseDate' not in v:
            releaseDate = "None"
        else:
            releaseDate = v['releaseDate']
        affected_versions.append(v['name']+"#"+releaseDate)
    affected_versions.sort()
    return affected_versions

def getFixVersion(issue):
    if issue['fields']['fixVersions'] == None:
        return "None"
    fix_versions = []
    for v in issue['fields']['fixVersions']:
        
        if 'releaseDate' not in v:
            releaseDate="None"
        else:
            releaseDate = v['releaseDate']
        fix_versions.append(v['name']+"#"+releaseDate)
    fix_versions.sort()
    return fix_versions


def getAllIssues(project):
    project = project.upper()
    for i in range(1, 210):
        #print i
        query = 'curl -s -d- -X GET -H "Content-Type: application/json" https://issues.apache.org/jira/rest/api/latest/search?jql=project='+project+'%20AND%20type=bug%20AND%20key\>='+project+'-'+str(i*100-99)+'%20AND%20key\<'+project+'-'+str(i*100)+"\&maxResults=100"
        #print query
        queryResult = subprocess.Popen(query, stdout=subprocess.PIPE, shell=True).communicate()[0]
        #print query_result
        try: 
            jsonData = json.loads(queryResult)
        except ValueError:

	    sys.stderr.write(str(queryResult)+"\n")
            print ";".join(["key", "createddate", "updateddate", "resolveddate", "resolution", "affectedversions", "fixversions"])
            for key, val in issueKeys.items():
                val = [str(v) for v in val]
                print ";".join([key] + val)
            return



        if 'issues' not in jsonData:
	    #print jsonData
	    sys.stderr.write(str(jsonData)+"\n")
            if i == 1:
                query = 'curl -s -d- -X GET -H "Content-Type: application/json" https://issues.apache.org/jira/rest/api/latest/search?jql=project='+project+'%20AND%20type=bug&maxResults=1000'
                queryResult = subprocess.Popen(query, stdout=subprocess.PIPE, shell=True).communicate()[0]
                jsonData = json.loads(queryResult)
	    else:
                #for key, val in issueKeys.items():
                #    val = [str(v) for v in val]
                #    print ";".join([key] + val)
                break 
        for issue in jsonData['issues']:
            affectedVersions = getAffectedVersion(issue)
            fixedVersions = getFixVersion(issue)
            fields = issue['fields']
            createdDate = fields['created'].replace('.000+0000', '')
            updatedDate = fields['updated'].replace('.000+0000', '')
            if fields['resolution'] == None:
                resolution = "None"
                resolvedDate = "None"
            else:
                resolution = fields['resolution']['name']
                resolvedDate = fields['resolutiondate'].replace('.000+0000', '')
            issueKeys[issue['key']] = [createdDate, updatedDate, resolvedDate, resolution, affectedVersions, fixedVersions]
            #print issueKeys[issue['key']]

    #w = csv.writer(open("output.csv", "w"))
    #w.writerow(["key", "createdDate", "updatedDate", "resolvedDate", "resolution", "affectedVersions", "fixVersions"])
    print ";".join(["key", "createddate", "updateddate", "resolveddate", "resolution", "affectedversions", "fixversions"])
    for key, val in issueKeys.items():
        val = [str(v) for v in val]

        #w.writerow([key] + val)
        print ";".join([key] + val)



getAllIssues(sys.argv[1])

