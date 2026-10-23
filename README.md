
# AutoETL GenAI
## Intelligent Data Pipeline Generation and Automated Failure Recovery

AutoETL GenAI is a data engineering project designed to automate important parts of an ETL (Extract, Transform, Load) workflow. It loads CSV and JSON files, profiles their schemas, checks data quality, applies approved transformations, and records pipeline execution results.

The project also includes an AI-assisted transformation code generator that uses the OpenAI API to propose Pandas transformation code based on a user's instruction and the input schema.

## Problem Statement

Data engineers often spend time writing repetitive data transformation code, identifying data quality issues, debugging pipeline failures, and maintaining execution records. These tasks can become difficult to manage when datasets have inconsistent schemas or unexpected values.

AutoETL GenAI provides a modular foundation for automating data ingestion, profiling, validation, transformation, and execution monitoring.

## Objectives

- Load data from CSV and JSON files.
- Detect column types and profile datasets.
- Validate required columns, missing values, duplicates, and numeric constraints.
- Generate transformation-code suggestions using an AI model.
- Execute a predefined set of approved transformations.
- Save transformed datasets to an output directory.
- Log pipeline activity and record execution history.
- Summarize successful and failed runs.

## Features

### 1. Data Ingestion
- Loads CSV files using Pandas.
- Loads JSON objects and arrays of records.
- Rejects unsupported formats and invalid input structures.

### 2. Schema Detection and Profiling
- Reports the number of rows and columns.
- Detects basic data types.
- Reports missing values and duplicate rows.
- Provides numeric-column statistics.

### 3. Data Quality Validation
- Checks required columns.
- Checks required non-null fields.
- Detects duplicate rows according to configured rules.
- Validates numeric minimum and maximum limits.
- Reports validation errors and warnings.

### 4. AI-Assisted Transformation Generation
- Accepts a transformation instruction and input schema.
- Uses the configured OpenAI model to generate suggested Pandas code.
- Saves generated code for inspection.
- Does not automatically execute AI-generated Python code.

**Security note:** Generated code must be reviewed and tested before use. The pipeline executor uses a predefined list of approved transformations instead of executing arbitrary AI-generated code.

### 5. Pipeline Execution
The pipeline validates the input, profiles it, applies approved transformations, validates the transformed data, and writes the output.

The currently supported transformation operations include:
- `drop_duplicates`
- `trim_strings`
- `standardize_column_names`
- `filter_numeric_min`
- `filter_numeric_max`
- `drop_missing_rows`

Check `app/execution/transformer.py` for the exact parameters and validation behavior of each operation.

### 6. Logging and Execution History
- Writes timestamped log messages.
- Records successful and failed pipeline runs.
- Stores execution details in JSON format.
- Reports execution totals, success rate, processed rows, and retry attempts.

## Technology Stack

- Python
- Pandas
- PyYAML
- python-dotenv
- OpenAI Python SDK
- Pytest
- Git and GitHub

## Project Structure

```text
AutoETL-GenAI/
├── app/
│   ├── ingestion/
│   │   └── file_loader.py
│   ├── profiling/
│   │   └── profiler.py
│   ├── validation/
│   │   └── validator.py
│   ├── generation/
│   │   ├── code_generator.py
│   │   └── generate.py
│   ├── execution/
│   │   ├── transformer.py
│   │   ├── pipeline.py
│   │   └── run_pipeline.py
│   ├── logging/
│   │   ├── logger.py
│   │   ├── history.py
│   │   └── show_statistics.py
│   ├── configuration.py
│   └── main.py
├── config/
│   └── settings.yaml
├── data/
│   ├── input/
│   │   ├── customers.csv
│   │   └── products.json
│   └── output/
├── logs/
├── tests/
├── docs/
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

This tree describes the expected main files. Keep any additional files that already exist in your repository.

## Prerequisites

- Python 3.10 or a compatible version supported by the installed dependencies.
- Git.
- VS Code or another Python editor.
- An OpenAI API key only for live AI transformation generation.

## Installation on Windows

### 1. Clone the repository

Replace the URL below with your actual GitHub repository URL.

```powershell
git clone YOUR_GITHUB_REPOSITORY_URL
cd AutoETL-GenAI
```

If you already have the project locally, open its folder instead.

### 2. Create a virtual environment

```powershell
python -m venv .venv
```

### 3. Activate it in PowerShell

```powershell
.\.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Configuration

Copy the example environment file:

```powershell
Copy-Item .env.example .env
```

Edit `.env` only if you need AI code generation. Set your API key locally:

```text
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4.1-mini
APP_ENV=development
LOG_LEVEL=INFO
```

Replace the placeholder with your own API key. Do not commit `.env` or expose your API key.

Application paths, validation rules, logging settings, and retry configuration are defined in `config/settings.yaml`.

## Running the Project

Run these commands from the project root.

### Run ingestion, profiling, and validation

```powershell
python -m app.main
```

### Run the CSV pipeline

```powershell
python -m app.execution.run_pipeline --file customers.csv
```

### Run the JSON pipeline

```powershell
python -m app.execution.run_pipeline --file products.json
```

### Run a custom approved transformation

The following example keeps customers whose age is at least 18:

```powershell
python -m app.execution.run_pipeline --file customers.csv --operations '[{"operation":"filter_numeric_min","column":"age","value":18}]'
```

Custom operations must use the supported operation names and parameters defined in `app/execution/transformer.py`. Input validation rules still apply after transformation.

### Generate AI-assisted transformation code

Example:

```powershell
python -m app.generation.generate --file customers.csv --instruction "Remove duplicate customer records"
```

This command requires a valid API key in `.env`. It generates code for review and does not automatically execute the generated Python file.

### View execution statistics

```powershell
python -m app.logging.show_statistics
```

## Output and Logs

- Transformed CSV and JSON files are saved in `data/output/`.
- Application logs are written to `logs/autoetl.log`.
- Execution records are stored in `logs/execution_history.json`.

These files are generated at runtime. Their presence depends on whether the corresponding commands have been run successfully.

Review `.gitignore` before pushing generated logs or data to GitHub. Do not publish private or sensitive data.

## Testing

Run the test suite:

```powershell
python -m pytest tests -v
```

Check Python syntax:

```powershell
python -m compileall -q app tests
```

The tests cover configuration, validation, transformation operations, execution history, and integration behavior where corresponding test files are present.

## Failure Handling and Limitations

- Invalid input formats and data-quality failures are reported.
- Output writing uses a configurable retry limit.
- Pipeline errors are logged and recorded where possible.
- AI-generated transformation code is not executed automatically.
- This implementation is a modular project foundation, not yet a distributed, production-scale ETL platform.
- Automatic recovery is currently limited; output-write retries do not guarantee recovery from every type of pipeline failure.
- For production use, add stronger isolation, access controls, secret management, monitoring, and more extensive recovery tests.

## Future Enhancements

- Support databases and cloud storage.
- Add scheduled and incremental pipelines.
- Add schema-drift detection.
- Add safer transformation execution in an isolated environment.
- Add richer failure classification and recovery strategies.
- Add a dashboard for pipeline runs and data quality.
- Benchmark throughput and reliability on larger datasets.

## Author

Developed as a data engineering and Generative AI project.

## License

Choose and add an appropriate open-source license before distributing the project publicly.
