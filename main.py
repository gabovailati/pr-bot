import time
from github import Github
from datetime import datetime, timedelta
import requests
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Replace with the repository owner and name
REPO_OWNER = "gabovailati"
REPO_NAME = "credit-card-tokenisation-simulator"

# Initialize the GitHub client
g = Github(GITHUB_TOKEN)
repo = g.get_repo(f"{REPO_OWNER}/{REPO_NAME}")

# Set the initial last checked time to 24 hours ago
last_checked = datetime.now() - timedelta(days=1)


def prepare_review_prompt(files):
    """
    Prepare the prompt for the Groq AI code review.
    This is a placeholder function, you should customize it based on your needs.
    """
    prompt = "Please review the following code changes and provide feedback:\n\n"
    for file in files:
        filename = file.filename
        patch = file.patch
        prompt += f"File: {filename}\n{patch}\n\n"
    prompt += "Your review comments:"
    return prompt

def perform_code_review(files):
    """
    Perform code review using Groq AI.
    """
    review_prompt = prepare_review_prompt(files)

    # Send the prompt to Groq AI and get the response
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GROQ_API_KEY}",
    }
    data = {"prompt": review_prompt}
    response = requests.post("https://api.groq.ai/v1/complete", headers=headers, json=data)

    # Check if the request was successful
    if response.status_code == 200:
        # Extract the review comments from the response
        review_comments = response.json()["result"]

        # Parse and organize the review comments
        # This is a placeholder, you should implement your own parsing logic
        review_comments = review_comments.split("\n")

        return review_comments
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return []

def main():
    global last_checked

    while True:
        try:
            # Get open pull requests sorted by updated time
            open_prs = repo.get_pulls(state="open", sort="updated")

            for pr in open_prs:
                # Check if the PR is new or updated since the last check
                if pr.updated_at > last_checked:
                    print(f"Reviewing PR #{pr.number}: {pr.title}")

                    # Get the changed files in the PR
                    files = pr.get_files()

                    # Perform code review
                    review_comments = perform_code_review(files)

                    # Post a review comment on the PR
                    if review_comments:
                        review_body = "\n".join(review_comments)
                        pr.create_review(body=review_body, event="COMMENT")
                        print(f"Posted review comments on PR #{pr.number}")
                    else:
                        print(f"No issues found in PR #{pr.number}")

                    # Update the last checked time
                    last_checked = datetime.now()

            # Sleep for 5 minutes before checking for new PRs again
            time.sleep(300)

        except Exception as e:
            print(f"An error occurred: {e}")
            # You can add error handling and logging here

if __name__ == "__main__":
    main()