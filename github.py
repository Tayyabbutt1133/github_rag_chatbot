import os 
import requests
from dotenv import load_dotenv
from langchain_core.documents import Document
 
load_dotenv()

github_token = os.getenv("GITHUB_TOKEN")


# fetching/accessing Github
def fetch_github(owner, repo, endpoint):
    url = f"https://api.github.com/repos/{owner}/{repo}/{endpoint}"
    headers={
        "Authorization" : f"Bearer {github_token}"
    }
    # Sending request to github api endpoint 
    response = requests.get(url, headers)
    
    
    
    # making condition at a time of getting response back
    if response.status_code == 200:
        data = response.json()
    else: 
        print("Failed at Status code:", response.status_code)
        return []
    # returning response getting from github api endpoint
    # print(data)
    return data


# fetching issue's
def fetch_github_issues(owner, repo):
    data = fetch_github(owner, repo, "issues")
    return load_github_issues_doc(data)


# loading retrieve issues in document to make Document-base-external knowledgeBase - RAG PIPELINE
def load_github_issues_doc(issues):
    docs = []
    for entry in issues:
        metadata = {
            "author": entry["user"]["login"],
            "comments": entry["comments"],
            "body": entry["body"],
            "labels": entry["labels"],
            "created_at": entry["created_at"]
        }
        data = entry["title"]
        if entry["body"]:
            # Concatenating body with title
            data += entry["body"]
               # uploading data that we get in response from github will be loaded in documents using langchain to make RAG Pipeline
            doc = Document(page_content=data, metadata=metadata)
            docs.append(doc)
    return docs






