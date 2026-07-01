from pathlib import Path

import tiktoken


ENCODING = tiktoken.get_encoding("o200k_base")


def analyse(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")

    lines = len(text.splitlines())
    chars = len(text)
    words = len(text.split())
    tokens = len(ENCODING.encode(text))

    return {
        "File": path.name,
        "Lines": lines,
        "Characters": chars,
        "Words": words,
        "LLM Tokens": tokens,
    }


def print_table(results: list[dict]) -> None:
    headers = ["File", "Lines", "Characters", "Words", "LLM Tokens"]

    widths = {
        h: max(len(h), *(len(str(r[h])) for r in results))
        for h in headers
    }

    header = " | ".join(f"{h:<{widths[h]}}" for h in headers)
    divider = "-+-".join("-" * widths[h] for h in headers)

    print(header)
    print(divider)

    for row in results:
        print(
            " | ".join(
                f"{str(row[h]):<{widths[h]}}"
                for h in headers
            )
        )


def main():
    folder = Path("examples")

    extensions = {".py", ".rs"}

    files = sorted(
        f
        for f in folder.iterdir()
        if f.suffix in extensions
    )

    results = [analyse(f) for f in files]

    print_table(results)


if __name__ == "__main__":
    main()