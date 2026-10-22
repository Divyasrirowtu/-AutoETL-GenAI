from app.configuration import load_settings


def main() -> None:
    """Start the AutoETL GenAI application."""
    settings = load_settings()
    application = settings["application"]
    data = settings["data"]
    pipeline = settings["pipeline"]

    print("=" * 48)
    print(application["name"])
    print(f"Version: {application['version']}")
    print(f"Environment: {application['environment']}")
    print(f"Input directory: {data['input_dir']}")
    print(f"Output directory: {data['output_dir']}")
    print(f"Supported formats: {', '.join(data['supported_formats'])}")
    print(f"Maximum retries: {pipeline['max_retries']}")
    print(f"Dry run: {pipeline['dry_run']}")
    print("Configuration loaded and validated successfully.")
    print("=" * 48)


if __name__ == "__main__":
    main()