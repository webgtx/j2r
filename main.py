import requests
import json
from os import environ

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
        started_at = jira_worklog["started"]
        time_spent_seconds = jira_worklog["timeSpentSeconds"]
        try:
            comments = jira_worklog["comment"]
        except:
            print(f"Invalid comment value, check issue {issue_id}")
        
        # Convert the time spent in seconds to hours
        time_spent_hours = time_spent_seconds / 3600
        
        print(issue_id, author, started_at, time_spent_hours, comments)

        continue
        # Construct the payload for the Redmine API request
        payload = {
            "time_entry": {
                "project_id": redmine_project_id,
                "issue_id": redmine_issue_id,
                "user_id": redmine_user_id,
                "activity_id": redmine_activity_id,
                "spent_on": started_at,
                "hours": time_spent_hours,
                "comments": comments
            }
        }
        
        # Make the request to the Redmine API to create the worklog
        redmine_response = requests.post(
            redmine_url,
            auth=(redmine_username, redmine_password),
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload)
        )
        
        # Check the status code of the response
        if redmine_response.status_code != 201:
            print(f"Error creating worklog in Redmine: {redmine_response.text}")
        else:
            print(f"Successfully migrated worklog from Jira to Redmine for issue {issue_id}")
