import os
from pathlib import Path

import yaml
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = PROJECT_ROOT / "config" / "settings.yaml"
ENV_PATH = PROJECT_ROOT / ".env"


def load_settings() -> dict:
    """Load and validate application settings."""
    load_dotenv(ENV_PATH)

    if not CONFIG_PATH.exists():
        raise FileNotFoundError(
            f"Configuration file not found: {CONFIG_PATH}"
        )

    with CONFIG_PATH.open("r", encoding="utf-8-sig") as file:
        settings = yaml.safe_load(file)

    if not isinstance(settings, dict):
        raise ValueError("settings.yaml must contain a YAML mapping.")

    required_sections = [
        "application",
        "data",
        "validation",
        "logging",
        "pipeline",
    ]

    for section in required_sections:
        if not isinstance(settings.get(section), dict):
            raise ValueError(
                f"Missing or invalid configuration section: {section}"
            )

    if not settings["application"].get("name"):
        raise ValueError("Application name is required.")

    data = settings["data"]

    for key in ("input_dir", "output_dir"):
        value = data.get(key)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"data.{key} must be a non-empty path.")

    retries = settings["pipeline"].get("max_retries")

    if (
        not isinstance(retries, int)
        or isinstance(retries, bool)
        or retries < 0
    ):
        raise ValueError(
            "pipeline.max_retries must be a non-negative integer."
        )

    formats = data.get("supported_formats")

    if not isinstance(formats, list) or not formats:
        raise ValueError(
            "data.supported_formats must be a non-empty list."
        )

    supported_formats = {"csv", "json"}

    if any(
        not isinstance(fmt, str)
        or fmt.lower() not in supported_formats
        for fmt in formats
    ):
        raise ValueError("Supported formats must be csv and/or json.")

    settings["application"]["environment"] = os.getenv(
        "APP_ENV",
        settings["application"].get("environment", "development"),
    )

    settings["logging"]["level"] = os.getenv(
        "LOG_LEVEL",
        settings["logging"].get("level", "INFO"),
    ).upper()

    return settings