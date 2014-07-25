"""
This file crawl all the JIRA issues of the specified project in apache,
and recored the issue's key, created date, updated date, resolved date, 
resolution, affected versions, and fixversions.
"""

import sys
import re
import json
import subprocess
import csv
from subprocess import call

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
    # magic number is for going through all issues
    for i in range(1, 210):
        query = 'curl -s -d- -X GET -H "Content-Type: application/json" https://issues.apache.org/jira/rest/api/latest/search?jql=project='+project+'%20AND%20type=bug%20AND%20key\>='+project+'-'+str(i*100-99)+'%20AND%20key\<'+project+'-'+str(i*100)+"\&maxResults=100"
        queryResult = subprocess.Popen(query, stdout=subprocess.PIPE, shell=True).communicate()[0]
        try: 
            jsonData = json.loads(queryResult)
        except ValueError:
            # exception occur: end of issues, print out result (redirect to a file)
	    sys.stderr.write(str(queryResult)+"\n")
            print ";".join(["key", "createddate", "updateddate", "resolveddate", "resolution", "affectedversions", "fixversions", "assignedDate"])
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
            createdDate = fields['created']#.replace('.000+0000', '')
            updatedDate = fields['updated']#.replace('.000+0000', '')
            if fields['resolution'] == None:
                resolution = "None"
                resolvedDate = "None"
            else:
                resolution = fields['resolution']['name']
                resolvedDate = fields['resolutiondate'].replace('.000+0000', '')
            changelog = issue['changelog']['histories']

            assignedDate = "None"
            for log in changelog:
                # the bug is assigned
                if log['items']['field'] == "assignee":
                    assignedDate = log['items']['created']
            
            issueKeys[issue['key']] = [createdDate, updatedDate, resolvedDate, resolution, affectedVersions, fixedVersions, assignedDate]
            #print issueKeys[issue['key']]

    #w = csv.writer(open("output.csv", "w"))
    #w.writerow(["key", "createdDate", "updatedDate", "resolvedDate", "resolution", "affectedVersions", "fixVersions"])
    print ";".join(["key", "createdDate", "updatedDate", "resolvedDate", "resolution", "affectedVersions", "fixVersions"])
    for key, val in issueKeys.items():
        val = [str(v) for v in val]

        #w.writerow([key] + val)
        print ";".join([key] + val)



getAllIssues(sys.argv[1])

