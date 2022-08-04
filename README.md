# Bitbucket Server Pull Request Conflict Checker
An application to integrate with Bitbucket Server Webhook service to do the following:
1. Receiving Pull Request events and Repository/Push events (Learn more about Bitbucket event payloads [here](https://confluence.atlassian.com/bitbucketserver/event-payload-938025882.html))
1. With the current pull request, check if:
  1. There is any other OPENED pull request pointing to the same target branch.
  1. There is any potential conflict file with the current pull request.

## Use cases
* You are maintaining multiple OPEN release branches that are branched from master and would like to be notified on any potential conflict caused by same files being changed accross release branches.

## Supported events
| Category | Event | Event Key |
| :--- | :--- | :--- |
| Repository | Push | repo:refs_changed |
| Pull Request | All Events | pr:* |

## [Docker](https://hub.docker.com/r/donkeystudio/bb-server-pr-conflicter)
Supported architectures: `linux/arm/v7`, `linux/arm64`, `linux/amd64`

## Startup Configuration
```
python3 main.py --help
```

```
usage: main.py [-h] [-conf CONFIG_FILE] [-p PORT] [-log LOG_FILE] [-d DEBUG_LEVEL]

optional arguments:
  -h,                   --help                          show this help message and exit
  -conf CONFIG_FILE,    --config_file   CONFIG_FILE     Location of the application config file (default: ./config.properties)
  -p    PORT,           --port          PORT            Port (default: 8080)
  -log  LOG_FILE,       --log_file      LOG_FILE        Location of the log file. Default is system log (default: None)
  -d    DEBUG_LEVEL,    --debug_level   DEBUG_LEVEL     Debug Level CRITICAL/ERROR/WARNING/INFO. Default is WARNING (default: WARNING)
```

### Config file
Config file consists of 2 sections
```
[HMAC]
HMAC_KEY={Optional. Secret key to authenticate with Bitbucket. In Base64 encoded format}
HMAC_SHA={Optional. HMACSHA Algorithm. Default is SHA256}

[BB-API]
BB_URL={Required. Bitbucket URL, e.g. http://localhost:7990}
USERNAME={Required. Username to authenticate with Bitbucket to access its REST API. In Base64 encoded format.}
PASSWORD={Required. Password to authenticate with Bitbucket to access its REST API. In Base64 encoded format.}
```

## API End-points
### General response example
```json
{"status": 200, "message": "Nothing to do here"}
```

### check_dependency/by_pr/comment
```http
POST /check_dependency/by_pr/comment?target=master|any(default)
```
Check and make a comment into the current Pull Request a list of PR Dependencies. The check is done on all open PRs targeting to the same branch (e.g. master) as the current Pull Request.

**Request Options**

| Parameter | Type | Description |
| :--- | :--- | :--- |
| target | string | (optional, default to **ANY**). Only process the request if the current PR is targetting to this branch. Either **MASTER** or **ANY** |

**Sample Response**
```json
{
    "status": 200,
    "comment": "_This is an auto generated message_ \n> * **Event Type:** pr:opened  \n> * **Event Date:** 2022-08-04T06:24:47+0000  \n\nExcluding the current pull request, there are in total `1` other active pull requests. Please check the following information for any potential conflicts:  \n## [Release/release1](http://localhost:7990/projects/POC/repos/repo1/pull-requests/9) \n* **ID:** 9 \n* **From:** `release/release1` (Repository:[repo1](http://localhost:7990/projects/POC/repos/repo1/browse), Project:[POC](http://localhost:7990/projects/POC)) \n* **To:** `master` (Repository:[repo1](http://localhost:7990/projects/POC/repos/repo1/browse), Project:[POC](http://localhost:7990/projects/POC)) \n* **Created Date:** 2022-08-04 06:24:31.922000 \n* **Last Updated:** 2022-08-04 06:24:31.922000 \n* **Author:** [Thor](http://localhost:7990/users/thunder.god) \n* **Potential Conflict(s):** `1` file(s) \n  * File `file1.txt`, full path at `/file1.txt`. \n"
}
```

### check_dependency/by_commit/comment
```http
POST /check_dependency/by_commit/comment?target=master|any(default)
```
Check and make a comment into Pull Request of the current commit a list of PR Dependencies. The check is done on all open PRs targeting to the same branch (e.g. master) as the Pull Request of the current commit.

**Request Options**

| Parameter | Type | Description |
| :--- | :--- | :--- |
| target | string | (optional, default to **ANY**). Only process the request if the current PR is targetting to this branch. Either **MASTER** or **ANY** |

**Sample Resposne**
```json
{
    "status": 200,
    "comment": [
        "_This is an auto generated message_ \n> * **Event Type:** repo:refs_changed  \n> * **Event Date:** 2022-08-04T06:33:23+0000  \n\nExcluding the current pull request, there are in total `1` other active pull requests. Please check the following information for any potential conflicts:  \n## [Release/release1](http://localhost:7990/projects/POC/repos/repo1/pull-requests/9) \n* **ID:** 9 \n* **From:** `release/release1` (Repository:[repo1](http://localhost:7990/projects/POC/repos/repo1/browse), Project:[POC](http://localhost:7990/projects/POC)) \n* **To:** `master` (Repository:[repo1](http://localhost:7990/projects/POC/repos/repo1/browse), Project:[POC](http://localhost:7990/projects/POC)) \n* **Created Date:** 2022-08-04 06:24:31.922000 \n* **Last Updated:** 2022-08-04 06:24:31.922000 \n* **Author:** [Iron Man](http://localhost:7990/users/tony.stark) \n* **Potential Conflict(s):** `1` file(s) \n  * File `file1.txt`, full path at `/file1.txt`. \n"
    ]
}
```