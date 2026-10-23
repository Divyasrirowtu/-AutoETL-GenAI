
import json
import time
from pathlib import Path

import pandas as pd

from app.configuration import load_settings
from app.execution.transformer import apply_transformations
from app.ingestion.file_loader import load_file
from app.logging.history import record_execution
from app.logging.logger import get_logger
from app.profiling.profiler import profile_data
from app.validation.validator import validate_data

PROJECT_ROOT = Path(__file__).resolve().parents[2]
logger = get_logger("autoetl.pipeline")


def run_pipeline(input_filename: str, operations: list[dict]) -> dict:
    """Run a validated ETL pipeline and record its execution history."""
    rows_before = 0
    rows_after = 0
    attempts = 0
    stage = "configuration"
    output_relative = None

    try:
        settings = load_settings()
        data_settings = settings["data"]
        validation_rules = settings["validation"]
        max_retries = settings["pipeline"]["max_retries"]

        input_dir = (PROJECT_ROOT / data_settings["input_dir"]).resolve()
        output_dir = (PROJECT_ROOT / data_settings["output_dir"]).resolve()
        input_path = (input_dir / input_filename).resolve()

        if input_path.parent != input_dir or not input_path.is_file():
            raise FileNotFoundError(
                "Provide an existing input filename directly inside data/input."
            )

        suffix = input_path.suffix.lower()
        if suffix not in {".csv", ".json"}:
            raise ValueError("Only CSV and JSON inputs are supported.")

        logger.info("Starting pipeline for %s", input_path.name)

        stage = "ingestion"
        dataframe = load_file(input_path)
        rows_before = int(len(dataframe))
        rows_after = rows_before
        logger.info(
            "Loaded %s: %s rows and %s columns",
            input_path.name,
            len(dataframe),
            len(dataframe.columns),
        )

        stage = "initial_validation"
        initial_validation = validate_data(
            dataframe, validation_rules, input_path.name
        )
        if not initial_validation["valid"]:
            errors = initial_validation["errors"]
            logger.error("Initial validation failed for %s: %s", input_path.name, errors)
            report = {
                "status": "failed",
                "stage": stage,
                "errors": errors,
                "attempts": 0,
            }
            record_execution(
                input_file=input_path.name,
                status="failed",
                stage=stage,
                rows_before=rows_before,
                rows_after=rows_after,
                attempts=0,
                errors=errors,
            )
            return report

        stage = "profiling"
        profile_before = profile_data(dataframe)
        logger.info(
            "Profiling complete: %s duplicate rows",
            profile_before["duplicate_rows"],
        )

        stage = "transformation"
        transformed = apply_transformations(dataframe, operations)
        rows_after = int(len(transformed))
        logger.info("Transformations completed: %s rows remain", rows_after)

        stage = "post_transformation_validation"
        final_validation = validate_data(
            transformed, validation_rules, input_path.name
        )
        if not final_validation["valid"]:
            errors = final_validation["errors"]
            logger.error(
                "Post-transformation validation failed for %s: %s",
                input_path.name,
                errors,
            )
            report = {
                "status": "failed",
                "stage": stage,
                "errors": errors,
                "attempts": 0,
            }
            record_execution(
                input_file=input_path.name,
                status="failed",
                stage=stage,
                rows_before=rows_before,
                rows_after=rows_after,
                attempts=0,
                errors=errors,
            )
            return report

        stage = "output"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = (
            output_dir / f"{input_path.stem}_transformed{suffix}"
        ).resolve()

        if output_path.parent != output_dir:
            raise ValueError("Invalid output path.")

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
                logger.exception(
                    "Output write attempt %s failed for %s",
                    attempts,
                    input_path.name,
                )
                if attempts > max_retries:
                    raise
                time.sleep(min(0.5 * attempts, 2.0))

        output_relative = str(output_path.relative_to(PROJECT_ROOT))
        report = {
            "status": "success",
            "input_file": input_path.name,
            "output_file": output_relative,
            "rows_before": rows_before,
            "rows_after": rows_after,
            "attempts": attempts,
            "validation": "passed",
        }

        record_execution(
            input_file=input_path.name,
            status="success",
            stage="completed",
            rows_before=rows_before,
            rows_after=rows_after,
            attempts=attempts,
            output_file=output_relative,
        )
        logger.info(
            "Pipeline succeeded for %s; output=%s; attempts=%s",
            input_path.name,
            output_relative,
            attempts,
        )
        return report

    except Exception as error:
        logger.exception(
            "Pipeline failed for %s during stage %s",
            input_filename,
            stage,
        )
        try:
            record_execution(
                input_file=input_filename,
                status="failed",
                stage=stage,
                rows_before=rows_before,
                rows_after=rows_after,
                attempts=attempts,
                errors=[f"{type(error).__name__}: {error}"],
                output_file=output_relative,
            )
        except Exception:
            logger.exception("Could not save the failure to execution history")
        raise
