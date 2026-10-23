import json
import time
from pathlib import Path

import pandas as pd

from app.configuration import load_settings
from app.execution.transformer import apply_transformations
from app.ingestion.file_loader import load_file
from app.profiling.profiler import profile_data
from app.validation.validator import validate_data


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def run_pipeline(
    input_filename: str,
    operations: list[dict],
) -> dict:
    """Run ingestion, validation, transformation, and output saving."""
    settings = load_settings()
    data_settings = settings["data"]
    validation_rules = settings["validation"]
    max_retries = settings["pipeline"]["max_retries"]

    input_dir = (PROJECT_ROOT / data_settings["input_dir"]).resolve()
    output_dir = (PROJECT_ROOT / data_settings["output_dir"]).resolve()

    # Only accept a filename located directly inside data/input.
    input_path = (input_dir / input_filename).resolve()

    if input_path.parent != input_dir or not input_path.is_file():
        raise FileNotFoundError(
            "Provide an existing input filename directly inside data/input."
        )

    suffix = input_path.suffix.lower()
    if suffix not in {".csv", ".json"}:
        raise ValueError("Only CSV and JSON inputs are supported.")

    # Initial validation happens before transformations.
    dataframe = load_file(input_path)
    initial_validation = validate_data(
        dataframe, validation_rules, input_path.name
    )

    if not initial_validation["valid"]:
        return {
            "status": "failed",
            "stage": "initial_validation",
            "errors": initial_validation["errors"],
            "attempts": 0,
        }

    profile_before = profile_data(dataframe)
    transformed = apply_transformations(dataframe, operations)

    # Validate the transformed data against the same configured rules.
    final_validation = validate_data(
        transformed, validation_rules, input_path.name
    )

    if not final_validation["valid"]:
        return {
            "status": "failed",
            "stage": "post_transformation_validation",
            "errors": final_validation["errors"],
            "attempts": 0,
        }

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = (output_dir / f"{input_path.stem}_transformed{suffix}").resolve()

    if output_path.parent != output_dir:
        raise ValueError("Invalid output path.")

    # Retry only transient file-system errors, not validation or code errors.
    attempts = 0
    while True:
        attempts += 1
        try:
            if suffix == ".csv":
                transformed.to_csv(output_path, index=False)
            else:
                output_path.write_text(
                    json.dumps(
                        transformed.to_dict(orient="records"),
                        indent=2,
                        ensure_ascii=False,
                        allow_nan=False,
                    ),
                    encoding="utf-8",
                )
            break
        except OSError:
            if attempts > max_retries:
                raise
            time.sleep(min(0.5 * attempts, 2.0))

    return {
        "status": "success",
        "input_file": input_path.name,
        "output_file": str(output_path.relative_to(PROJECT_ROOT)),
        "rows_before": profile_before["row_count"],
        "rows_after": int(len(transformed)),
        "attempts": attempts,
        "validation": "passed",
    }