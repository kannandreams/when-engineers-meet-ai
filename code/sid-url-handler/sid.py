from urllib.parse import parse_qs, urlparse
import sys


ALLOWED_ACTIONS = {"task", "review"}


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


def validate_params(action: str, params: dict):
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


def main():
    if len(sys.argv) != 2:
        raise SystemExit(
            "usage: python sid.py <sid://...>"
        )

    action, params = parse_intent(sys.argv[1])

    print(f"Action: {action}")

    for key, value in params.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()