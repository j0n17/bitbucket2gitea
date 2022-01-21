import os
import logging
import requests

from typing import List
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(module)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def get_bitbucket_repositories(owner: str, username: str, password: str) -> List:
    """
    Fetches the list of repositories from Bitbucket API
    """
    repositories = []

    page = 1
    while True:
        res = requests.get(
            f"https://api.bitbucket.org/2.0/repositories/{owner}",
            params={"pagelen": 100, "page": page},
            auth=(username, password),
        )
        if res.status_code != 200:
            raise Exception(
                "Failed to fetch the list of repositories", res.status_code, res.text
            )

        data = res.json()

        repositories += data["values"]
        page = data["page"] + 1

        if len(data["values"]) == 0:
            break

    return [
        {
            "url": "https://bitbucket.org/" + r["full_name"],
            "full_name": r["full_name"],
            "name": r["full_name"].split("/")[1],
            "title": r["name"],
            "description": r["description"],
        }
        for r in repositories
    ]


def migrate_repository(
    url,
    token,
    orgname_or_username,
    bitbucket_username,
    bitbucket_password,
    repository,
):
    """
    Send the migration payload to GitTea
    """

    payload = {
        "clone_addr": repository["url"].replace(
            "https://bitbucket.org",
            f"https://{bitbucket_username}:{bitbucket_password}@bitbucket.org",
        ),
        "repo_owner": orgname_or_username,
        "description": repository["description"],
        "repo_name": repository["name"],

        "mirror": (os.getenv("GITEA_MIGRATE_CONFIG_MIRROR", 'False') == 'True'),
        "private": (os.getenv("GITEA_MIGRATE_CONFIG_PRIVATE", 'False') == 'True'),
        "issues": (os.getenv("GITEA_MIGRATE_CONFIG_ISSUES", 'False') == 'True'),
        "labels": (os.getenv("GITEA_MIGRATE_CONFIG_LABELS", 'False') == 'True'),
        "milestones": (os.getenv("GITEA_MIGRATE_CONFIG_MILESTONES", 'False') == 'True'),
        "pull_requests": (os.getenv("GITEA_MIGRATE_CONFIG_PULL_REQUESTS", 'False') == 'True'),
        "releases": (os.getenv("GITEA_MIGRATE_CONFIG_RELEASES", 'False') == 'True'),
        "wiki": (os.getenv("GITEA_MIGRATE_CONFIG_WIKI", 'False') == 'True'),
    }

    logging.info(f'Migrating {repository["name"]} to {url}')
    res = requests.post(
        f"{url}/api/v1/repos/migrate",
        json=payload,
        headers={"Authorization": f"token {token}"},
        timeout=120,
    )

    if res.status_code == 201:
        logging.info(f'Created {repository["name"]} successfully')
    else:
        logging.error(
            f'Failed to create {repository["name"]}, got status code {res.status_code} and error :\n{res.text}'
        )

def validate_environment():
    """
    Validates the required environment variables, raises an exception if some of them are missing
    """

    missing_values = []

    required_keys = [
        "BITBUCKET_ORGNAME",
        "BITBUCKET_USERNAME",
        "BITBUCKET_PASSWORD",
        "GITEA_URL",
        "GITEA_TOKEN",
        "GITEA_ORGNAME_OR_USERNAME",
    ]

    for key in required_keys:
        if key not in os.environ:
            missing_values.append(key)

    if len(missing_values):
        raise Exception(f"The following keys are missing from the environment variables : {', '.join(missing_values)}")


def main():
    load_dotenv()

    validate_environment()

    bitbucket_orgname = os.getenv("BITBUCKET_ORGNAME")
    bitbucket_username = os.getenv("BITBUCKET_USERNAME")
    bitbucket_password = os.getenv("BITBUCKET_PASSWORD")

    gitea_url = os.getenv("GITEA_URL").rstrip("/")
    gitea_token = os.getenv("GITEA_TOKEN")
    gitea_orgname_or_username = os.getenv("GITEA_ORGNAME_OR_USERNAME")

    repositories = get_bitbucket_repositories(
        bitbucket_orgname, bitbucket_username, bitbucket_password
    )

    for repository in repositories:
        migrate_repository(
            gitea_url,
            gitea_token,
            gitea_orgname_or_username,
            bitbucket_username,
            bitbucket_password,
            repository,
        )


if __name__ == "__main__":
    main()
