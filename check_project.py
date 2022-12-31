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

# Jira API endpoint for getting all projects
jira_projects_url = f"https://{jira_origin}/rest/api/2/project"
print(jira_projects_url)

# Make the request to the Jira API to get all projects
response = requests.get(
    jira_projects_url,
    auth=(jira_username, jira_apikey)
)
# Check the status code of the response
if response.status_code != 200:
    print(f"Error getting projects: {response.text}")
else:
    # Extract the list of projects from the response
    projects = response.json()
    print(projects, response.headers)
    for project in projects:
        print(f"Project: {project['name']} ({project['key']})")
