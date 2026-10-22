from pathlib import Path

import pandas as pd

from app.configuration import load_settings
from app.ingestion.file_loader import load_file
from app.profiling.profiler import profile_data
from app.validation.validator import validate_data


def main() -> None:
    """Ingest, profile, and validate supported input files."""
    settings = load_settings()

    app = settings["application"]
    data_settings = settings["data"]
    validation_rules = settings["validation"]

    project_root = Path(__file__).resolve().parent.parent
    input_dir = project_root / data_settings["input_dir"]

    if not input_dir.exists():
        raise FileNotFoundError(f"Input directory not found: {input_dir}")

    supported_formats = {
        f".{fmt.lower().lstrip('.')}"
        for fmt in data_settings["supported_formats"]
    }

    input_files = sorted(
        path
        for path in input_dir.iterdir()
        if path.is_file() and path.suffix.lower() in supported_formats
    )

    print("=" * 55)
    print(app["name"])
    print(f"Version: {app['version']}")
    print("Steps 3–5: Ingestion, Profiling, and Validation")
    print("=" * 55)

    if not input_files:
        print("No supported input files found.")

    for file_path in input_files:
        print(f"\nFile: {file_path.name}")

        try:
            dataframe = load_file(file_path)
            profile = profile_data(dataframe)
            report = validate_data(
                dataframe,
                validation_rules,
                file_name=file_path.name,
            )

            print(f"Rows: {profile['row_count']}")
            print(f"Columns: {profile['column_count']}")
            print(f"Duplicate rows: {profile['duplicate_rows']}")

            print("\nSchema:")
            for column, details in profile["schema"].items():
                print(
                    f"  {column}: {details['data_type']}, "
                    f"missing={details['missing_values']}"
                )

            print("\nValidation:")
            print(f"  Status: {'PASS' if report['valid'] else 'FAIL'}")
            print(f"  Errors: {report['error_count']}")
            print(f"  Warnings: {report['warning_count']}")

            for error in report["errors"]:
                print(f"  ERROR: {error}")

            for warning in report["warnings"]:
                print(f"  WARNING: {warning}")

        except (ValueError, OSError, pd.errors.ParserError) as error:
            print(f"Could not process {file_path.name}: {error}")

    print("\nStep 5: Data quality validation completed.")
    print("=" * 55)


if __name__ == "__main__":
    main()