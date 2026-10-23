
import logging
from pathlib import Path

from app.configuration import PROJECT_ROOT, load_settings


def get_logger(name: str = "autoetl") -> logging.Logger:
    """Create a logger that writes to both the console and a log file."""
    settings = load_settings()
    logging_settings = settings["logging"]

    log_file = PROJECT_ROOT / logging_settings.get(
        "file", "logs/autoetl.log"
    )
    log_file.parent.mkdir(parents=True, exist_ok=True)

    level_name = logging_settings.get("level", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False

    # Avoid adding duplicate handlers when get_logger is called repeatedly.
    if not logger.handlers:
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        )

        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger
