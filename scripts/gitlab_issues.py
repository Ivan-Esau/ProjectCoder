import os
import json
import requests


def create_issue(title: str, description: str, gitlab_url: str, project_id: str, token: str) -> dict:
    """Create a single GitLab issue via the API."""
    api = f"{gitlab_url}/api/v4/projects/{project_id}/issues"
    headers = {"PRIVATE-TOKEN": token}
    payload = {"title": title, "description": description}
    response = requests.post(api, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()


def create_issues_from_tickets(tickets_file: str) -> None:
    """Create GitLab issues for each ticket in tickets_file."""
    with open(tickets_file, encoding="utf-8") as f:
        tickets = json.load(f)

    url = os.getenv("GITLAB_URL", "https://gitlab.com")
    project_id = os.environ["GITLAB_PROJECT_ID"]
    token = os.environ["GITLAB_TOKEN"]

    for ticket in tickets:
        title = ticket.get("title", "Untitled")
        desc = ticket.get("beschreibung", "")
        reqs = ticket.get("anforderungen", "")
        body = f"{desc}\n\n{reqs}" if reqs else desc
        issue = create_issue(title, body, url, project_id, token)
        print(f"Created issue #{issue['iid']}: {issue['web_url']}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Create GitLab issues from tickets.json")
    parser.add_argument("tickets_file", help="Path to tickets.json")
    args = parser.parse_args()

    create_issues_from_tickets(args.tickets_file)
