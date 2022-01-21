# Bitbucket 2 Gitea

## Usage
Create a .env file with the following information:
- `GITEA_URL`
- `GITEA_TOKEN`
- `GITEA_ORGNAME_OR_USERNAME`
- `BITBUCKET_ORGNAME`
- `BITBUCKET_USERNAME`
- `BITBUCKET_PASSWORD`

Optionally, you can specify the following variables to override the way repositories are migrated to Gitea (defaults to `False` if not specified) :
- `GITEA_MIGRATE_CONFIG_MIRROR`
- `GITEA_MIGRATE_CONFIG_PRIVATE`
- `GITEA_MIGRATE_CONFIG_ISSUES`
- `GITEA_MIGRATE_CONFIG_LABELS`
- `GITEA_MIGRATE_CONFIG_MILESTONES`
- `GITEA_MIGRATE_CONFIG_PULL_REQUESTS`
- `GITEA_MIGRATE_CONFIG_RELEASES`
- `GITEA_MIGRATE_CONFIG_WIKI`

And run the following command:
```sh
python3 bitbucket2gitea.py
```

## TODO :
- [ ] Use https://github.com/dblueai/giteapy instead of requests
