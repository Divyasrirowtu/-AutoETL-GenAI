
import json
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from uuid import uuid4

from app.configuration import PROJECT_ROOT

HISTORY_FILE = PROJECT_ROOT / "logs" / "execution_history.json"
_HISTORY_LOCK = Lock()


def record_execution(
    *,
    input_file: str,
    status: str,
    stage: str,
    rows_before: int = 0,
    rows_after: int = 0,
    attempts: int = 0,
    errors: list[str] | None = None,
    output_file: str | None = None,
) -> dict:
    """Append one pipeline execution record to the JSON history file."""
    if status not in {"success", "failed"}:
        raise ValueError("status must be 'success' or 'failed'.")

    record = {
        "execution_id": str(uuid4()),
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "input_file": input_file,
        "status": status,
        "stage": stage,
        "rows_before": int(rows_before),
        "rows_after": int(rows_after),
        "attempts": int(attempts),
        "output_file": output_file,
        "errors": errors or [],
    }

    with _HISTORY_LOCK:
        HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)

        if HISTORY_FILE.exists():
            try:
                existing = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError) as error:
                raise RuntimeError(
                    f"Cannot read execution history {HISTORY_FILE}: {error}"
                ) from error

            if not isinstance(existing, list):
                raise ValueError("Execution history must contain a JSON list.")
        else:
            existing = []

        existing.append(record)

        temporary_file = HISTORY_FILE.with_suffix(".tmp")
        temporary_file.write_text(
            json.dumps(existing, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        temporary_file.replace(HISTORY_FILE)

    return record


def get_execution_statistics() -> dict:
    """Summarize recorded pipeline runs."""
    if not HISTORY_FILE.exists():
        return {
            "total_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "success_rate_percent": 0.0,
            "total_rows_processed": 0,
            "total_retry_attempts": 0,
        }

    try:
        records = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as error:
        raise RuntimeError(
            f"Cannot read execution history {HISTORY_FILE}: {error}"
        ) from error

    if not isinstance(records, list):
        raise ValueError("Execution history must contain a JSON list.")

    successful = [item for item in records if item.get("status") == "success"]
    failed = [item for item in records if item.get("status") == "failed"]
    total = len(records)

    return {
        "total_executions": total,
        "successful_executions": len(successful),
        "failed_executions": len(failed),
        "success_rate_percent": round(len(successful) / total * 100, 2)
        if total else 0.0,
        "total_rows_processed": sum(
            int(item.get("rows_after", 0)) for item in successful
        ),
        "total_retry_attempts": sum(
            max(0, int(item.get("attempts", 0)) - 1) for item in records
        ),
    }
