import requests
import json
from datetime import date, datetime
from os import environ
import re

from requests.api import request

date_format = '%Y-%m-%dT%H:%M:%S.%f%z'
hours_summury = 0

try:
    # Jira API credentials
    jira_origin = environ["JIRA_ORIGIN"] 
    jira_username = environ["JIRA_USERNAME"] 
    jira_apikey = environ["JIRA_APIKEY"] 

    # Redmine API credentials
    redmine_username = environ["REDMINE_USERNAME"] 
    redmine_password = environ["REDMINE_PASSWORD"] 
    redmine_url = environ["REDMINE_URL"] 
except:
    print("You must execute enviroment variable setter script")
    exit(1)

redmine_issues = requests.get(
        redmine_url + "issues.json",
        auth = (redmine_username, redmine_password),
        params = {"limit": 100}
        )


#try:
#    print(redmine_issues.json())
#except:
#    print(redmine_issues.headers)

def issue_filter(project, mask):
    for issue in redmine_issues.json()["issues"]:
        if issue["project"]["name"] == project:
            subject_pattern = re.search(mask, issue["subject"])
            if subject_pattern:
                return issue["id"]

print(issue_filter("MthMR", "AWS"))
    
    

def count_worklogs():
    global hours_summury

    # Jira API endpoint for searching issues
    jira_search_url = f"https://{jira_origin}/rest/api/2/search"
    
    issue_ids, issues = "", ""
    
    # Query parameters for the search request
    query_params = {
        "jql": "project = SevenPro",
        "fields": "id",
        "maxResults": 1000
    }
    
    # Make the request to the Jira API to search for issues
    response = requests.get(
        jira_search_url,
        auth=(jira_username, jira_apikey),
        params=query_params
    )
    
    # Check the status code of the response
    if response.status_code != 200:
        print(f"Error searching for issues: {response.text}")
    else:
        # Extract the list of issue IDs from the response
        jira_issues = response.json()["issues"]
        jira_issue_ids = [issue["id"] for issue in jira_issues]
        print(f"Successfully retrieved issue IDs for project SevenPro: {jira_issue_ids}")
    
    
    # Iterate through all Jira issues
    for issue_id in jira_issue_ids:
        # Jira API endpoint for worklogs
        jira_worklogs_url = f"https://{jira_origin}/rest/api/2/issue/{issue_id}/worklog"
        jira_issues_url = f"https://{jira_origin}/rest/api/2/issue/"
    
        # Get worklogs for the current issue
        jira_response = requests.get(
            jira_worklogs_url.format(issue_id=issue_id),
            auth=(jira_username, jira_apikey)
        )
        jira_worklogs = jira_response.json()["worklogs"]
        
        # Iterate through the worklogs for the current issue
        for jira_worklog in jira_worklogs:
            # Extract the relevant information from the Jira worklog
            author = jira_worklog["author"]["displayName"]
            started_at = datetime.strptime(jira_worklog["started"], date_format)
            time_spent_seconds = jira_worklog["timeSpentSeconds"]
            try:
                comments = jira_worklog["comment"]
            except:
                comments = f"Invalid comment value, check issue {issue_id}"
            
            # Convert the time spent in seconds to hours
            time_spent_hours = time_spent_seconds / 3600
            
            if started_at.month == 1:
                issue_title = requests.get(
                        jira_issues_url + issue_id,
                        auth=(jira_username, jira_apikey)
                        )
                print("\n",issue_id, author, started_at.month, time_spent_hours, comments, " | ", issue_title.json()["fields"]["summary"])
                print() 

                hours_summury += int(time_spent_hours)
                redmine_issue_id = issue_filter("MthMR", issue_title.json()["fields"]["summary"])
                
                res = requests.post(
                        redmine_url + "time_entries.json",
                        auth = (redmine_username, redmine_password),
                        headers={"Content-Type": "application/json"},
                        data = json.dumps({
                            "time_entry": {
                                    "issue_id": redmine_issue_id,
                                    "spent_on": started_at.strftime("%G-%m-%d"),
                                    "hours": time_spent_hours,
                                    "comments": comments 
                                }
                            } 
                        ))
                
                try:
                    print(res.json(), res.status_code)
                except:
                    print("ERROR", res.headers)
                
count_worklogs()

print("Summury hours = ", hours_summury)
