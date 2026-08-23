from pathlib import Path
import os
from urllib.parse import parse_qs, urlparse
import sys

ALLOWED_ACTIONS = {"task", "review"}

LOG_PATH = Path("/tmp/sid-url-handler.log")

BASE_PATH = Path(
    os.environ["CODE_WORKSPACE_BASE"]
)

REPOS = {
    "secchi": {
        "path": BASE_PATH / "secchi",
        "github": "kannandreams/secchi",
    }
}


def emit(message: str) -> None:
    print(message)

    with LOG_PATH.open("a") as f:
        f.write(message + "\n")


def parse_intent(raw_url: str):
    url = urlparse(raw_url)

    if url.scheme != "sid":
        raise ValueError(
            f"unsupported URL scheme: {url.scheme}"
        )

    action = url.netloc

    if action not in ALLOWED_ACTIONS:
        raise ValueError(
            f"unsupported Sid action: {action}"
        )

    params = {
        key: values[0]
        for key, values in parse_qs(url.query).items()
    }

    validate_params(action, params)

    return action, params


def validate_params(action: str, params: dict) -> None:
    if "repo" not in params:
        raise ValueError(
            "missing required parameter: repo"
        )

    if action == "task" and "issue" not in params:
        raise ValueError(
            "task requires an issue parameter"
        )

    if action == "review" and "pr" not in params:
        raise ValueError(
            "review requires a pr parameter"
        )


def resolve_repo(repo_name: str):
    repo = REPOS.get(repo_name)

    if repo is None:
        raise ValueError(
            f"unknown repository: {repo_name}"
        )

    return repo


def main():
    if len(sys.argv) != 2:
        raise SystemExit(
            "usage: python sid.py <sid://...>"
        )

    raw_url = sys.argv[1]

    action, params = parse_intent(raw_url)

    repo_name = params["repo"]
    repo = resolve_repo(repo_name)

    emit("")
    emit("External Sid request")
    emit("--------------------")
    emit(f"URL:         {raw_url}")
    emit(f"Action:      {action}")
    emit(f"Repository:  {repo_name}")
    emit(f"Local path:  {repo['path']}")
    emit(f"GitHub repo: {repo['github']}")

    if action == "task":
        emit(f"Issue:       #{params['issue']}")

    elif action == "review":
        emit(f"PR:          #{params['pr']}")

    emit("")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        emit(f"Error: {exc}")
        raise