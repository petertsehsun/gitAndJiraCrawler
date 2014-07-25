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
    isIn = False
    notInCount = 0
    for i in range(1, 130):
        #query = 'curl -s -d- -X GET -H "Content-Type: application/json" https://issues.apache.org/jira/rest/api/latest/search?expand=changelog\&jql=project='+project+'%20AND%20type=bug%20AND%20key\>='+project+'-'+str(i*50-49)+'%20AND%20key\<='+project+'-'+str(i*50)+"\&maxResults=50"
        query = 'curl -s -d- -X GET -H "Content-Type: application/json" https://issues.apache.org/jira/rest/api/latest/search?expand=changelog\&jql=project='+project+'%20AND%20type=bug\&key\>='+project+'-'+str(i*50-49)+'\&key\<='+project+'-'+str(i*50)+"\&maxResults=50"
        print query


        #if i == 19 and not isIn:
        #    print 'final'
        #    query = 'curl -s -d- -X GET -H "Content-Type: application/json" https://issues.apache.org/jira/rest/api/latest/search?expand=changelog\&jql=project='+project+'%20AND%20type=bug\&maxResults=1000'
        queryResult = subprocess.Popen(query, stdout=subprocess.PIPE, shell=True).communicate()[0]
        #print queryResult
        #print query, i 
        
        try: 
            jsonData = json.loads(queryResult)
        except ValueError:
            # exception occur: end of issues, print out result (redirect to a file)
            sys.stderr.write(str(queryResult)+"\n")
            #print ";".join(["key", "createddate", "updateddate", "resolveddate", "resolution", "affectedversions", "fixversions", "assignDate", "numReopen", "numTosses"])
            for key, val in issueKeys.items():
                val = [str(v) for v in val]
                #print ";".join([key] + val)
            break
            #return

        if 'issues' not in jsonData:
            notInCount += 1
            print 'not in'
            print queryResult
            if notInCount > 30:
                break
            """
            f = open(sys.argv[1]+".csv", 'wb')
            w = csv.writer(f, delimiter=';')
            w.writerow(["key", "createdDate", "updatedDate", "resolvedDate", "resolution", "affectedVersions", "fixVersions", "assignDate", "numReopen", "numTosses"])
            for key, val in issueKeys.items():
                val = [str(v) for v in val]

                w.writerow([key] + val)
            """
            continue
        """
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
        """
        allIssues = len(jsonData['issues'])
        issueCount = 0
        print allIssues
        for issue in jsonData['issues']:
            isIn = True
            
            if issueCount % 1000 == 0:
                print issueCount, allIssues
            issueCount+=1


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
                resolvedDate = fields['resolutiondate']#.replace('.000+0000', '')


            assignDate = "None"
            numReopen = 0
            numTosses = -1
            numRelated = 0
            numComments = 0
            changelog = issue['changelog']
            assignees = []
            # get first assign date
            if 'assignee' in fields:
		if fields['assignee'] != None:
                    #assignees.append(fields['assignee']['name'])
                    assignees.append(fields['assignee']['displayName']+"|"+fields['assignee']['name'])
                    assignDate = createdDate
            #if 'assignee' not in fields:
            # get correct first assign date
            for history in changelog['histories']:
                try:
                    for histItem in history['items']:
                        if histItem['field'].lower() == "assignee".lower():
                            try:
                                if histItem['to']+'|'+histItem['toString'] in assignees:
                                    assignDate = history['created']
                                if histItem['toString']+'|'+histItem['to'] in assignees:
                                    assignDate = history['created']
                                break
                            except TypeError:
                                pass
                except IndexError:
                    continue

            if 'comment' in fields:
                print 'comments'
                if 'comments' in fields['comment']:
                    numComments = len(fields['comment']['comments'])


            # get reopen count
            for history in changelog['histories']:
                try:
                    for histItem in history['items']:
                        if histItem['toString'] != None:
                            if histItem['toString'].lower() == "Reopened".lower():
                                numReopen += 1
                            if "This issue is related to".lower() in histItem['toString'].lower():
                                numRelated += 1
                        if histItem['field'] == "assignee":
                            numTosses += 1
                            # add who was assigned
                            if histItem['toString'] != None:
                                assignees.append(histItem['to']+"|"+histItem['toString'])
                except IndexError:
                    continue

            if numTosses == -1:
                numTosses = 0

            issueKeys[issue['key']] = [createdDate, updatedDate, resolvedDate, resolution, affectedVersions, fixedVersions, assignDate, numReopen, numTosses, numRelated, numComments, assignees]
            #print issueKeys[issue['key']]

    #w = csv.writer(open("output.csv", "w"))
    #w.writerow(["key", "createdDate", "updatedDate", "resolvedDate", "resolution", "affectedVersions", "fixVersions"])
    #print ";".join(["key", "createdDate", "updatedDate", "resolvedDate", "resolution", "affectedVersions", "fixVersions"])
    #print ";".join(["key", "createdDate", "updatedDate", "resolvedDate", "resolution", "affectedVersions", "fixVersions", "assignDate", "numReopen", "numTosses"])
    f = open(sys.argv[1]+".csv", 'wb')
    w = csv.writer(f, delimiter=';')
    w.writerow(["key", "createdDate", "updatedDate", "resolvedDate", "resolution", "affectedVersions", "fixVersions", "assignDate", "numReopen", "numTosses", "numRelated", "numComments", "assignees"])
    for key, val in issueKeys.items():
        val = [str(v) for v in val]

        w.writerow([key] + val)
        #print ";".join([key] + val)



getAllIssues(sys.argv[1])

