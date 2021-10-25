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
    print(f"{url}/api/v1/repos/migrate")
    res = requests.post(
        f"{url}/api/v1/repos/migrate",
        json={
            "clone_addr": repository["url"].replace(
                "https://bitbucket.org",
                f"https://{bitbucket_username}:{bitbucket_password}@bitbucket.org",
            ),
            "mirror": True,
            "private": True,
            "issues": True,
            "labels": True,
            "milestones": True,
            "pull_requests": True,
            "repo_owner": orgname_or_username,
            "releases": True,
            "wiki": True,
            "description": repository["description"],
            "repo_name": repository["name"],
        },
        headers={"Authorization": f"token {token}"},
        timeout=120,
    )

    if res.status_code == 201:
        logging.info(f'Created {repository["name"]} successfully')
    else:
        logging.error(
            f'Failed to create {repository["name"]}, got status code {res.status_code} and error :\n{res.text}'
        )


def main():
    load_dotenv()

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
