import os
from jira import JIRA

# Production-ready Atlassian Jira Integration
# Requires JIRA_SERVER, JIRA_USER, and JIRA_API_TOKEN.

def ingest_jira_project(project_key: str):
    """
    Connects to Atlassian Jira API, searches for tickets in a project,
    and structures the issue descriptions into text chunks for Qdrant storage.
    """
    server = os.environ.get("JIRA_SERVER", "https://your-domain.atlassian.net")
    user = os.environ.get("JIRA_USER", "admin@company.com")
    token = os.environ.get("JIRA_API_TOKEN", "mock_token")

    options = {"server": server}
    
    try:
        # Authenticate with Jira
        jira = JIRA(options, basic_auth=(user, token))
        
        # JQL query to get all issues in the project
        issues = jira.search_issues(f'project={project_key}')
        
        parsed_chunks = []
        for issue in issues:
            desc = issue.fields.description or ""
            summary = issue.fields.summary or ""
            
            chunk = {
                "source": "jira",
                "ticket_id": issue.key,
                "text": f"Title: {summary}\nDescription: {desc}",
                "status": str(issue.fields.status)
            }
            parsed_chunks.append(chunk)
            
        print(f"Successfully extracted {len(parsed_chunks)} Jira tickets.")
        return parsed_chunks

    except Exception as e:
        print(f"Jira API connection failed: {e}")
        return []

if __name__ == "__main__":
    print("Jira Ingestion Worker Initialized.")
