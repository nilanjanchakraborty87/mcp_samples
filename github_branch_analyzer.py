
import dotenv
import os
from fastmcp import FastMCP
from utility.github_utils import get_branches, get_repo_list

dotenv.load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_PAT") # Get the GitHub token from the environment variables
REPO_OWNER = os.getenv("REPO_OWNER")

mcp = FastMCP(name="github_branch_analyzer")

@mcp.resource("data://repos")
def get_repo_list():
    """
    Get the list of github repositories.
    """
    return get_repo_list()

@mcp.tool()
def github_branch_analyzer(repo: str) -> dict:
    """
    Get the branch details for a given repository as a dictionary in the following format:  
    {
        "<REPO_NAME>": {
            "<BRANCH_NAME>": {
                "committer": {
                    "email": "<EMAIL_ID>",
                    "name": "<NAME>"
                },
                "last_commit_date": "date in YYYY-MM-DD format",
                "name": "BRANCH_NAME",
                "opened_prs": {
                    "1": {
                        "created_at": "date in YYYY-MM-DD format",
                        "raised_by": "<GITHUB_USERNAME>",
                        "reviewers": [],
                        "updated_at": "date in YYYY-MM-DD format"
                    }
                }
            }
        }
    }
    """
    return get_branches(repo, REPO_OWNER, GITHUB_TOKEN)

mcp.run(transport="streamable-http", host="0.0.0.0", port=8055, log_level="DEBUG")

