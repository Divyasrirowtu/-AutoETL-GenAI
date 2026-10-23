
import json

from app.logging.history import get_execution_statistics, HISTORY_FILE
from app.logging.logger import get_logger


def main() -> None:
    """Display summary statistics for recorded pipeline runs."""
    logger = get_logger("autoetl.statistics")
    try:
        statistics = get_execution_statistics()
        print("\n=== AutoETL GenAI Execution Statistics ===")
        print(json.dumps(statistics, indent=2))
        print(f"\nHistory file: {HISTORY_FILE}")
    except (OSError, RuntimeError, ValueError) as error:
        logger.exception("Could not read execution statistics")
        raise SystemExit(f"Unable to show statistics: {error}") from error


if __name__ == "__main__":
    main()
