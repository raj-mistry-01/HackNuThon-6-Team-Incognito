import requests
import json

def get_figma_json(access_token: str, file_id: str, output_file: str = "figma_file.json"):
    figma_api_url = f"https://api.figma.com/v1/files/{file_id}"
    headers = {"X-Figma-Token": access_token}
    response = requests.get(figma_api_url, headers=headers)
    if response.status_code == 200:
        file_data = response.json()
        print("✅ File details retrieved successfully!")
        with open(output_file, "w", encoding="utf-8") as json_file:
            json.dump(file_data, json_file, indent=4)
    else:
        print(f"❌ Failed to fetch data: {response.status_code}")
        print(response.text)
# Example usage
# get_figma_json("your_access_token", "your_file_id")
FIGMA_ACCESS_TOKEN = "figd_uVoIukrCAalpz9okHu4CEcG9nHcXCD1YzXHutjcR"
FILE_ID = "zMlGokdmscjtOPXlwzk4Fi"