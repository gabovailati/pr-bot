import time
from github import Github
from datetime import datetime, timedelta
import requests
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

# Replace with the repository owner and name
REPO_OWNER = "gabovailati"
REPO_NAME = "credit-card-tokenisation-simulator"

# Initialize the GitHub client
g = Github(GITHUB_TOKEN)
repo = g.get_repo(f"{REPO_OWNER}/{REPO_NAME}")

# Set the initial last checked time to 24 hours ago
#last_checked = datetime.now() - timedelta(days=1)

client = Groq(
    api_key=GROQ_API_KEY
)

def prepare_review_prompt(files):
    """
    Prepare the prompt for the Groq AI code review.
    This is a placeholder function, you should customize it based on your needs.
    """
    prompt = "Please perform a code review on the following changes and provide feedback. Below there are the GitHub changes. Be aware that lines starting with + are being added and the ones starting with - are being removed.\n\n---\n\n"
    for file in files:
        filename = file.filename
        patch = file.patch
        prompt += f"File: {filename}\n{patch}\n\n"
    prompt += "---"
    print(prompt)
    return prompt

def perform_code_review(files):
    """
    Perform code review using Groq AI.
    """
    review_prompt = prepare_review_prompt(files)

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": review_prompt,
            }
        ],
        model="llama3-8b-8192",
#        temperature=1,
#        max_tokens=1024,
#        top_p=1,
#        stream=True,
#        stop=None,
    )

    review_comments = chat_completion.choices[0].message.content
    review_comments = review_comments.split("\n")

    print(review_comments)
    return review_comments


def main():
    pr_last_checked = {}  # Dictionary to store the last checked time for each PR

    while True:
        try:
            # Get open pull requests sorted by updated time
            print(f"Looking for new PRs in {REPO_NAME}")            
            open_prs = repo.get_pulls(state="open", sort="updated")

            for pr in open_prs:
                # Check if the PR is new or updated since the last check
                if pr.number not in pr_last_checked or pr.updated_at > pr_last_checked[pr.number]:
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

                    # Update the last checked time for this PR
                    pr_last_checked[pr.number] = pr.updated_at

            # Sleep for 5 minutes before checking for new PRs again
            time.sleep(300)

        except Exception as e:
            print(f"An error occurred: {e}")
            # You can add error handling and logging here

if __name__ == "__main__":
    main()