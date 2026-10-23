
import json

from app.logging import history


def test_record_execution_and_statistics(tmp_path, monkeypatch):
    history_file = tmp_path / "execution_history.json"
    monkeypatch.setattr(history, "HISTORY_FILE", history_file)

    history.record_execution(
        input_file="customers.csv",
        status="success",
        stage="completed",
        rows_before=5,
        rows_after=4,
        attempts=2,
        output_file="data/output/customers_transformed.csv",
    )

    history.record_execution(
        input_file="products.json",
        status="failed",
        stage="initial_validation",
        rows_before=3,
        rows_after=3,
        attempts=0,
        errors=["Missing required column"],
    )

    records = json.loads(history_file.read_text(encoding="utf-8"))
    stats = history.get_execution_statistics()

    assert len(records) == 2
    assert records[0]["input_file"] == "customers.csv"
    assert records[1]["status"] == "failed"
    assert stats["total_executions"] == 2
    assert stats["successful_executions"] == 1
    assert stats["failed_executions"] == 1
    assert stats["success_rate_percent"] == 50.0
    assert stats["total_rows_processed"] == 4
    assert stats["total_retry_attempts"] == 1


def test_statistics_when_history_does_not_exist(tmp_path, monkeypatch):
    monkeypatch.setattr(
        history, "HISTORY_FILE", tmp_path / "missing_history.json"
    )

    stats = history.get_execution_statistics()

    assert stats["total_executions"] == 0
    assert stats["successful_executions"] == 0
    assert stats["failed_executions"] == 0
    assert stats["success_rate_percent"] == 0.0
