import requests
import json
import time

# ✅ GitLab Settings
GITLAB_URL = "https://gitlab.com"
PROJECT_ID = "68486861"                      # Your GitLab project ID
TOKEN = "glpat-qV4SRr45PxyJHSrJU9KD"         # GitLab token for API access
BRANCH = "main"                              # Target branch for pipeline execution


# 1️⃣ Fetch the current .gitlab-ci.yml file
def fetch_ci_file():
    """ Fetch the current .gitlab-ci.yml from GitLab """
    url = f"{GITLAB_URL}/api/v4/projects/{PROJECT_ID}/repository/files/.gitlab-ci.yml/raw?ref={BRANCH}"
    headers = {"PRIVATE-TOKEN": TOKEN}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        print("✅ Successfully fetched the .gitlab-ci.yml file.")
        return response.text
    else:
        print(f"❌ Failed to fetch file: {response.status_code}")
        return None


# 2️⃣ Push the updated .gitlab-ci.yml file based on test status
def push_updated_ci_file(status):
    """ Push different .gitlab-ci.yml files based on test status """
    
    # 🔥 Generate YAML content dynamically based on the test status
    if status:
        print("✅ Pushing SUCCESS YAML")
        new_content = f"""
image: ruby:3.1

stages:
  - test

test_execution:
  stage: test
  script:
    - echo "✅ All tests passed!"
    - exit 0  # Success
  allow_failure: false
"""
    else:
        print("❌ Pushing FAIL YAML")
        new_content = f"""
image: ruby:3.1

stages:
  - test

test_execution:
  stage: test
  script:
    - echo "❌ Some tests failed!"
    - exit 1  # Fail
  allow_failure: false
"""

    url = f"{GITLAB_URL}/api/v4/projects/{PROJECT_ID}/repository/commits"

    data = {
        "branch": BRANCH,
        "commit_message": f"🔥 Add {'SUCCESS' if status else 'FAIL'} pipeline YAML",
        "actions": [
            {
                "action": "update",
                "file_path": ".gitlab-ci.yml",
                "content": new_content
            }
        ]
    }

    headers = {"PRIVATE-TOKEN": TOKEN}

    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 201:
        print("\n✅ Successfully pushed the updated .gitlab-ci.yml file.")
        return True
    else:
        print(f"\n❌ Failed to push changes: {response.status_code}")
        print(response.text)
        return False


# 3️⃣ Trigger the pipeline
def trigger_pipeline():
    """ Trigger GitLab pipeline """
    trigger_url = f"{GITLAB_URL}/api/v4/projects/{PROJECT_ID}/pipeline"

    trigger_data = {
        "ref": BRANCH
    }

    headers = {
        "PRIVATE-TOKEN": TOKEN
    }

    response = requests.post(trigger_url, json=trigger_data, headers=headers)

    if response.status_code == 201:
        print("🚀 Pipeline triggered successfully!")
        return True
    else:
        print(f"❌ Failed to trigger pipeline: {response.status_code}")
        print(response.text)
        return False


# 4️⃣ Wait for the new commit to be applied
def wait_for_commit(commit_message, timeout=30):
    """ Wait until the new commit is visible """
    url = f"{GITLAB_URL}/api/v4/projects/{PROJECT_ID}/repository/commits"
    headers = {"PRIVATE-TOKEN": TOKEN}

    start_time = time.time()

    while time.time() - start_time < timeout:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            commits = response.json()

            # ✅ Check if the latest commit contains our message
            if any(commit['title'] == commit_message for commit in commits):
                print("✅ Commit applied successfully!")
                return True

        print("⏳ Waiting for the commit to be applied...")
        time.sleep(2)

    print("❌ Timeout waiting for commit.")
    return False
