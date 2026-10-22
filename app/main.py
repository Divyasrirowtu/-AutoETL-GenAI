from pathlib import Path

import yaml
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = PROJECT_ROOT / "config" / "settings.yaml"


def load_settings() -> dict:
    """Load settings from the YAML configuration."""
    load_dotenv(PROJECT_ROOT / ".env")

    with CONFIG_PATH.open("r", encoding="utf-8-sig") as config_file:
        settings = yaml.safe_load(config_file)

    if not isinstance(settings, dict):
        raise ValueError("Application configuration must be a YAML mapping.")

    return settings


def main() -> None:
    """Start the AutoETL GenAI application."""
    settings = load_settings()
    application = settings.get("application", {})

    print("=" * 48)
    print(application.get("name", "AutoETL GenAI"))
    print(f"Version: {application.get('version', 'unknown')}")
    print(f"Environment: {application.get('environment', 'unknown')}")
    print("Application setup completed successfully.")
    print("ETL and GenAI features will be added in later steps.")
    print("=" * 48)


if __name__ == "__main__":
    main()