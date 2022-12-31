import requests
from os import environ

try:
    # Jira API credentials
    jira_origin = environ["JIRA_ORIGIN"] 
    jira_username = environ["JIRA_USERNAME"] 
    jira_apikey = environ["JIRA_APIKEY"] 
except:
    print("You must execute enviroment variable setter script")
    exit(1)

issue_id = "10842"

# Jira API endpoint for worklogs
jira_worklogs_url = f"https://{jira_origin}/rest/api/2/issue/{issue_id}/worklog"

# Jira API key
jira_apikey = "ZMCiH84BrPF3VywlTVIJBA3C"

# Get worklogs for a specific issue
response = requests.get(
    jira_worklogs_url.format(issue_id=issue_id),
    auth=(jira_username, jira_apikey)
)

# Check the status code of the response
if response.status_code != 200:
    print(f"Error getting worklogs: {response.text}")
else:
    worklogs = response.json()["worklogs"]
    print(f"Successfully retrieved worklogs for issue {issue_id}: {worklogs}")
