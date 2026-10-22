import json
from pathlib import Path

import pandas as pd


SUPPORTED_FORMATS = {".csv", ".json"}


def load_file(file_path: str | Path) -> pd.DataFrame:
    """Load a CSV or JSON file into a Pandas DataFrame."""
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")

    if not path.is_file():
        raise ValueError(f"Input path is not a file: {path}")

    suffix = path.suffix.lower()

    if suffix not in SUPPORTED_FORMATS:
        raise ValueError(
            f"Unsupported file format: {suffix}. Supported formats: CSV, JSON."
        )

    if suffix == ".csv":
        return pd.read_csv(path)

    with path.open("r", encoding="utf-8-sig") as file:
        records = json.load(file)

    if isinstance(records, list):
        if not all(isinstance(record, dict) for record in records):
            raise ValueError("JSON arrays must contain objects (records).")
        return pd.DataFrame(records)

    if isinstance(records, dict):
        if "data" in records and isinstance(records["data"], list):
            if not all(isinstance(record, dict) for record in records["data"]):
                raise ValueError("The JSON 'data' array must contain objects.")
            return pd.DataFrame(records["data"])

        return pd.DataFrame([records])

    raise ValueError("JSON must contain an object or an array of objects.")