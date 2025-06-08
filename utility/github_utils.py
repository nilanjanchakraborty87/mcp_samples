import requests

def get_repo_list():
    return ["spring-akka-actor-demo", "dsa-in-java", "azure-function-sams-poc", "ErlangChat", "MiniKVStore", "java-tutorials"]

def get_headers(token):
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }

def get_branches(repo, repo_owner, token):
    headers = get_headers(token)
    #print(headers)
    url = f"https://api.github.com/repos/{repo_owner}/{repo}/branches"
    response = requests.get(url, headers = headers)
    response.raise_for_status()  # Optional: raises an error for bad responses
    
    branch_dict = {}
    for branch in response.json():
        #print(f"Branch Name: {branch['name']}")
        branch_details = get_branch_details(repo, repo_owner, branch, token)
        #print(branch_details)
        branch_dict[branch['name']] = branch_details
    return branch_dict


def get_branch_details(repo, repo_owner, branch, token):

    headers = get_headers(token);
    branch_name = branch['name']
    
    # Get commit info
    commit_resp = requests.get(branch['commit']['url'], headers=headers).json()
    last_committer = commit_resp["commit"]["author"]["name"]
    last_committer_email = commit_resp["commit"]["author"]["email"]
    commit_date_str = commit_resp["commit"]["author"]["date"] 
    commit_date = None
    if commit_date_str:
        commit_date = commit_date_str.split("T")[0]  # Gets 'YYYY-MM-DD'
    

    # Get PRs for this branch
    prs_url = f"https://api.github.com/repos/{repo_owner}/{repo}/pulls?state=open&head={branch_name}"
    prs_resp = requests.get(prs_url, headers=headers).json()

    pr_dict = {}
    for pr in prs_resp:
        created_date = None
        if pr["created_at"]:
            created_date = pr["created_at"].split("T")[0]

        updated_date = None
        if pr["updated_at"]:
            updated_date = pr["updated_at"].split("T")[0]
            
        pr_dict[pr["number"]] = {
            "updated_at": updated_date,
            "created_at": created_date,
            "raised_by": pr["user"]["login"],
            "reviewers": pr["requested_reviewers"],
        }

    return {
        "name": branch_name,
        "last_commit_date": commit_date,
        "committer": { 
            "name": last_committer,
            "email": last_committer_email
        },
        "opened_prs": pr_dict
    }



        