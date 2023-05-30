"""
Python Script to fetch weekly git pull request status for any public repository
and print the details in email format
"""
import datetime
import requests

# GitHub repository details
# To add new repository, please add <Repo Owner> & <Repo name> as key-value pair
git_details = {"username": "repo_name"}

# Configure email details
SENDER_EMAIL = 'sender_email@example.com'
RECIPIENT_EMAIL = 'recipient_email@example.com'

# Get the date range for the past week
today = datetime.datetime.now().date()
last_week = today - datetime.timedelta(days=7)


def fetch_details(url, owner):
    """
    Function to fetch all the pull requests and create an email template
    For each repository.
    """
    # Make a request to the GitHub API
    email_content = f"Pull Request Summary for {owner}/{git_details[owner]} in the last week:\n"
    response = requests.get(url, params={'state': 'all', 'sort': 'created', 'direction': 'desc',
                                         'since': last_week.isoformat()}, timeout=5)
    pull_requests = response.json()
    if pull_requests:
        try:
            if pull_requests['message'] == "Not Found":
                email_content += "STATUS: Repository not Found. Please check\n\n"
        except:
            # Prepare the email content
            for pr in pull_requests:
                pr_state = pr['state']
                pr_title = pr['title']
                pr_url = pr['html_url']
                pr_created_at = pr['created_at']
                pr_closed_at = pr['closed_at']
                pr_draft = pr['draft']
                pr_requester = pr['user']['login']
                pr_approver = pr['requested_reviewers'][0]['login'] if pr['requested_reviewers'] else "None"

                email_content += f"Title: {pr_title}\n"
                email_content += f"URL: {pr_url}\n"
                email_content += f"State: {pr_state}\n"
                email_content += f"Created At: {pr_created_at}\n"
                if pr_closed_at:
                    email_content += f"Closed At: {pr_closed_at}\n"
                if pr_draft:
                    email_content += "Status: Draft\n"
                email_content += f"Requester: {pr_requester}\n"
                email_content += f"Approver: {pr_approver}\n"
                email_content += "\n"

    else:
        email_content += "STATUS: No pull requests have been raised.\n\n"
    return email_content


if __name__ == '__main__':
    for owners in git_details:
        API_URL = f"https://api.github.com/repos/{owners}/{git_details[owners]}/pulls"
        mail_body = fetch_details(API_URL, owners)
        print("FROM: " + SENDER_EMAIL + "\nTO: " + RECIPIENT_EMAIL +
              f"\nSUBJECT: Weekly Pull Request Summary for {owners}/{git_details[owners]} " +
              "\n\n" + mail_body)
