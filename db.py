import base64
import requests
import os
import json
from config import *

def fetch_data_from_db():
    """
    Fetch the raw data from the anime_data.txt file in the GitHub repository.
    """
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{PATH}"
    headers = {
        "Authorization": f"token {GIT_TOKEN}"
    }

    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        # Check if the response is a list or a dictionary
        data = response.json()

        if isinstance(data, list):
            print("Error: Unexpected response format. List received instead of dictionary.")
            return None, None
        
        # Now handle the expected dictionary format
        file_content = data.get('content', None)
        if not file_content:
            print("Error: No content found in the file.")
            return None, None
        
        try:
            # Decode base64 content into the original string
            decoded_content = base64.b64decode(file_content).decode("utf-8")
        except Exception as e:
            print(f"Error decoding base64 content: {e}")
            return None, None

        sha = data.get('sha', None)  # Safely get the sha
        return decoded_content, sha  # Return decoded content and sha
    else:
        print("Error fetching data from GitHub:", response.status_code)
        return None, None

def update_data_in_db(new_json_data):
    """
    Overwrite the existing content of the anime_data.txt file in the GitHub repository with new JSON data.
    """
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{PATH}"
    headers = {
        "Authorization": f"token {GIT_TOKEN}"
    }

    # Step 1: Fetch the current file metadata (to get the 'sha')
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        sha = data.get('sha', None)  # Fetch the current sha

        # Debugging: Print the sha (optional)
        print(f"Current file sha: {sha}")

    else:
        print("Error fetching the existing file:", response.json())
        return False

    # Step 2: Validate the new data is valid JSON
    try:
        json.loads(new_json_data)  # Ensure new data is valid JSON
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON data: {e}")
        return False

    # Step 3: Base64 encode the new content
    encoded_data = base64.b64encode(new_json_data.encode("utf-8")).decode("utf-8")

    # Step 4: Prepare the payload to overwrite the file
    update_payload = {
        "message": "Rewriting content of anime_data.txt",
        "sha": sha,  # Use the current sha to update the file
        "content": encoded_data  # Base64 encoded new content
    }

    # Step 5: Send the PUT request to update the file
    response = requests.put(url, headers=headers, json=update_payload)

    if response.status_code == 200:
        print("Successfully overwrote the content of the GitHub repository.")
        return True
    else:
        print("Error updating the GitHub repository:", response.json())
        return False
