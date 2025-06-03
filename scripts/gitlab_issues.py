import os
import json
import requests


def create_issue(
    title: str, description: str, gitlab_url: str, project_id: str, token: str
) -> dict:
    """Create a single GitLab issue via the API."""
    api = f"{gitlab_url}/api/v4/projects/{project_id}/issues"
    headers = {"PRIVATE-TOKEN": token}
    payload = {"title": title, "description": description}
    response = requests.post(api, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()


def create_issues_from_tickets(
    tickets_file: str,
    gitlab_url: str | None = None,
    project_id: str | None = None,
    token: str | None = None,
) -> list:
    """Create GitLab issues for each ticket in ``tickets_file``.

    Parameters fall back to environment variables if not provided.
    Returns a list with the created issue JSON objects.
    """
    with open(tickets_file, encoding="utf-8") as f:
        tickets = json.load(f)

    url = gitlab_url or os.getenv("GITLAB_URL", "https://gitlab.com")
    project = project_id or os.environ.get("GITLAB_PROJECT_ID")
    tok = token or os.environ.get("GITLAB_TOKEN")

    if not project or not tok:
        raise ValueError("GitLab project ID und Token erforderlich")

    issues = []
    for ticket in tickets:
        title = ticket.get("title", "Untitled")
        desc = ticket.get("beschreibung", "")
        reqs = ticket.get("anforderungen", "")
        body = f"{desc}\n\n{reqs}" if reqs else desc
        issue = create_issue(title, body, url, project, tok)
        issues.append(issue)
    return issues


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Create GitLab issues from tickets.json"
    )
    parser.add_argument("tickets_file", help="Path to tickets.json")
    parser.add_argument(
        "--gitlab-url",
        dest="gitlab_url",
        default=os.getenv("GITLAB_URL", "https://gitlab.com"),
        help="GitLab URL",
    )
    parser.add_argument(
        "--project-id",
        dest="project_id",
        default=os.getenv("GITLAB_PROJECT_ID"),
        help="GitLab project ID",
    )
    parser.add_argument(
        "--token", dest="token", default=os.getenv("GITLAB_TOKEN"), help="GitLab token"
    )
    args = parser.parse_args()

    create_issues_from_tickets(
        args.tickets_file, args.gitlab_url, args.project_id, args.token
    )
