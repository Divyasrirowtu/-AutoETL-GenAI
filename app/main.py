from pathlib import Path

import pandas as pd

from app.configuration import load_settings
from app.ingestion.file_loader import load_file
from app.profiling.profiler import profile_data


def main() -> None:
    """Load input files and display their data profiles."""
    settings = load_settings()

    app = settings["application"]
    data_settings = settings["data"]

    project_root = Path(__file__).resolve().parent.parent
    input_dir = project_root / data_settings["input_dir"]

    print("=" * 55)
    print(app["name"])
    print(f"Version: {app['version']}")
    print("Step 4: Schema Detection and Data Profiling")
    print("=" * 55)

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

    if not input_files:
        print("No supported input files found.")

    for file_path in input_files:
        try:
            dataframe = load_file(file_path)
            report = profile_data(dataframe)

            print(f"\nFile: {file_path.name}")
            print(f"Rows: {report['row_count']}")
            print(f"Columns: {report['column_count']}")
            print(f"Duplicate rows: {report['duplicate_rows']}")

            print("\nDetected schema:")
            for column, details in report["schema"].items():
                print(
                    f"  {column}: {details['data_type']}, "
                    f"missing={details['missing_values']}"
                )

            print("\nNumeric statistics:")
            if report["numeric_statistics"]:
                for column, stats in report["numeric_statistics"].items():
                    print(
                        f"  {column}: min={stats['min']}, "
                        f"max={stats['max']}, mean={stats['mean']}"
                    )
            else:
                print("  No numeric columns found.")

        except (ValueError, OSError, pd.errors.ParserError) as error:
            print(f"Could not profile {file_path.name}: {error}")

    print("\nStep 4: Data profiling completed.")
    print("=" * 55)


if __name__ == "__main__":
    main()