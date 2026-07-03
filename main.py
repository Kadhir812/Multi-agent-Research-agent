import sys

from config import load_env

load_env()

from graph import graph  # noqa: E402


def main() -> None:
    question = sys.argv[1] if len(sys.argv) > 1 else input("Question: ")

    result = graph.invoke({"question": question})

    print(result["final_answer"])


if __name__ == "__main__":
    main()
