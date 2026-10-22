from pathlib import Path

import pandas as pd

from app.configuration import load_settings
from app.ingestion.file_loader import load_file


def main() -> None:
    """Start AutoETL GenAI and demonstrate file ingestion."""
    settings = load_settings()

    app = settings["application"]
    data_settings = settings["data"]

    project_root = Path(__file__).resolve().parent.parent
    input_dir = project_root / data_settings["input_dir"]

    print("=" * 48)
    print(app["name"])
    print(f"Version: {app['version']}")
    print(f"Environment: {app['environment']}")
    print("=" * 48)

    for file_path in sorted(input_dir.iterdir()):
        if file_path.is_file() and file_path.suffix.lower() in {
            ".csv",
            ".json",
        }:
            try:
                dataframe = load_file(file_path)

                print(f"\nFile: {file_path.name}")
                print(f"Rows: {len(dataframe)}")
                print(f"Columns: {list(dataframe.columns)}")
                print("Preview:")
                print(dataframe.head(3).to_string(index=False))

            except (ValueError, OSError, pd.errors.ParserError) as error:
                print(f"Could not load {file_path.name}: {error}")

    print("\nStep 3: Data ingestion completed.")


if __name__ == "__main__":
    main()