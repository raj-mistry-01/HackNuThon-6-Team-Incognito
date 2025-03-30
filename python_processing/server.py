import requests

# ✅ GitLab Settings
GITLAB_URL = "https://gitlab.com"
PROJECT_ID = "68486861"                      # Your GitLab project ID
TOKEN = "glpat-qV4SRr45PxyJHSrJU9KD"         # GitLab token for API access
BRANCH = "main"                              # Target branch for pipeline execution

# ✅ Server IP for fetching test cases and Selenium script
SERVER_IP = "YOUR_SERVER_IP"                  # Replace with your Flask server IP



# 1️⃣ Fetch the .gitlab-ci.yml file
def fetch_ci_file():
    url = f"{GITLAB_URL}/api/v4/projects/{PROJECT_ID}/repository/files/.gitlab-ci.yml/raw?ref={BRANCH}"
    headers = {"PRIVATE-TOKEN": TOKEN}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        print("✅ Successfully fetched the .gitlab-ci.yml file.\n")
        
        # ✅ Print the fetched .gitlab-ci.yml content
        print("🔥 Fetched .gitlab-ci.yml content:")
        print("-" * 40)
        print(response.text)
        print("-" * 40)
        
        return response.text
    else:
        print(f"❌ Failed to fetch file: {response.status_code}")
        return None


# 2️⃣ Push the updated .gitlab-ci.yml file with Selenium config
def push_updated_ci_file():
    # 🔥 Your final GitLab CI/CD configuration with dynamic test execution
    new_content = f"""
image: ruby:3.1  # Keep using your current Docker image

stages:
  - test

test_execution:
  stage: test
  before_script:
    - apt-get update && apt-get install -y jq curl  # Install jq and curl
  script:
    - echo "🔥 Checking test status from the server..."
    - |
      response=$(curl -s   https://4dd0-202-131-110-12.ngrok-free.app/test-status)
      echo "Server Response: $response"

      # ✅ Extract the 'status' field from the response
      status=$(echo "$response" | jq -r '.status')

      # ✅ Proper multi-line block with correct YAML syntax
      if [ "$status" == "true" ]; then
        echo "✅ All tests passed!"
        exit 0  # Success
      else
        echo "❌ Some tests failed!"
        exit 1  # Fail the pipeline
      fi
  allow_failure: false
"""

    # ✅ API call to push the updated .gitlab-ci.yml
    url = f"{GITLAB_URL}/api/v4/projects/{PROJECT_ID}/repository/commits"
    
    data = {
        "branch": BRANCH,
        "commit_message": "🔥 Add Selenium tests with dynamic execution",
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
    else:
        print(f"\n❌ Failed to push changes: {response.status_code}")
        print(response.text)


# 3️⃣ Trigger the pipeline
def trigger_pipeline():
    trigger_url = f"{GITLAB_URL}/api/v4/projects/{PROJECT_ID}/pipeline"
    
    trigger_data = {
        "ref": BRANCH
    }

    # Use the Personal Access Token with API permissions
    headers = {
        "PRIVATE-TOKEN": TOKEN  # Use PAT instead of the trigger token
    }

    response = requests.post(trigger_url, json=trigger_data, headers=headers)

    if response.status_code == 201:
        print("🚀 Pipeline triggered successfully!")
    else:
        print(f"❌ Failed to trigger pipeline: {response.status_code}")
        print(response.text)


# ✅ Execution Flow
print("\n🔥 Starting CI/CD Process...")

# Step 1: Fetch the current .gitlab-ci.yml
original_content = fetch_ci_file()

if original_content:
    # Step 2: Push the new CI/CD configuration
    push_updated_ci_file()
    
    # Step 3: Trigger the pipeline
    trigger_pipeline()

print("\n🚀 All steps completed successfully!")
