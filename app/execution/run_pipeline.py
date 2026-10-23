import argparse
import json

from app.execution.pipeline import run_pipeline


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the AutoETL GenAI pipeline."
    )
    parser.add_argument(
        "--file",
        required=True,
        help="Input filename located in data/input.",
    )
    parser.add_argument(
        "--operations",
        default='[{"operation":"drop_duplicates"},{"operation":"trim_strings"}]',
        help="JSON list of approved transformation operations.",
    )
    args = parser.parse_args()

    try:
        operations = json.loads(args.operations)
    except json.JSONDecodeError as error:
        parser.error(f"--operations must be valid JSON: {error}")

    if not isinstance(operations, list):
        parser.error("--operations must be a JSON list.")

    report = run_pipeline(args.file, operations)
    print(json.dumps(report, indent=2))

    if report["status"] != "success":
        raise SystemExit(1)


if __name__ == "__main__":
    main()