
import json

import pandas as pd
import yaml

from app import configuration
from app.execution import pipeline
from app.logging import history


def setup_test_project(tmp_path, monkeypatch, csv_content):
    """Create an isolated project structure for an integration test."""
    input_dir = tmp_path / "data" / "input"
    output_dir = tmp_path / "data" / "output"
    input_dir.mkdir(parents=True)
    output_dir.mkdir(parents=True)

    (input_dir / "customers.csv").write_text(
        csv_content, encoding="utf-8"
    )

    settings = {
        "application": {
            "name": "AutoETL GenAI Test",
            "version": "1.0.0",
            "environment": "test",
        },
        "data": {
            "input_dir": "data/input",
            "output_dir": "data/output",
            "supported_formats": ["csv", "json"],
        },
        "validation": {
            "fail_on_missing_required_columns": True,
            "allow_duplicate_rows": False,
            "required_columns": {
                "customers.csv": ["customer_id", "name"]
            },
            "required_non_null_columns": {
                "customers.csv": ["customer_id", "name"]
            },
            "numeric_rules": {
                "customers.csv": {
                    "customer_id": {"min": 1}
                }
            },
        },
        "logging": {
            "level": "INFO",
            "file": "logs/autoetl.log",
        },
        "pipeline": {
            "max_retries": 1,
            "dry_run": True,
        },
    }

    config_dir = tmp_path / "config"
    config_dir.mkdir()
    config_path = config_dir / "settings.yaml"
    config_path.write_text(
        yaml.safe_dump(settings, sort_keys=False),
        encoding="utf-8",
    )

    monkeypatch.setattr(configuration, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(configuration, "CONFIG_PATH", config_path)
    monkeypatch.setattr(pipeline, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(
        history, "HISTORY_FILE", tmp_path / "logs" / "execution_history.json"
    )

    return output_dir


def test_end_to_end_pipeline_writes_output_and_history(
    tmp_path, monkeypatch
):
    output_dir = setup_test_project(
        tmp_path,
        monkeypatch,
        "customer_id,name\n1, Asha \n2, Ravi \n",
    )

    report = pipeline.run_pipeline(
        "customers.csv",
        [
            {"operation": "drop_duplicates"},
            {"operation": "trim_strings"},
        ],
    )

    assert report["status"] == "success"
    assert report["rows_before"] == 2
    assert report["rows_after"] == 2

    output_file = output_dir / "customers_transformed.csv"
    assert output_file.exists()

    output_df = pd.read_csv(output_file)
    assert output_df["name"].tolist() == ["Asha", "Ravi"]

    records = json.loads(
        history.HISTORY_FILE.read_text(encoding="utf-8")
    )
    assert len(records) == 1
    assert records[0]["status"] == "success"
    assert records[0]["output_file"] == (
        "data/output/customers_transformed.csv"
    )


def test_end_to_end_pipeline_records_validation_failure(
    tmp_path, monkeypatch
):
    setup_test_project(
        tmp_path,
        monkeypatch,
        "customer_id,wrong_column\n1,Asha\n",
    )

    report = pipeline.run_pipeline(
        "customers.csv",
        [{"operation": "trim_strings"}],
    )

    assert report["status"] == "failed"
    assert report["stage"] == "initial_validation"

    records = json.loads(
        history.HISTORY_FILE.read_text(encoding="utf-8")
    )
    assert len(records) == 1
    assert records[0]["status"] == "failed"
    assert records[0]["stage"] == "initial_validation"
    assert records[0]["errors"]
