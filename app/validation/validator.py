from pathlib import Path

import pandas as pd


def validate_data(
    dataframe: pd.DataFrame,
    rules: dict,
    file_name: str = "",
) -> dict:
    """Validate a DataFrame against configured data-quality rules."""
    if not isinstance(dataframe, pd.DataFrame):
        raise TypeError("validate_data expects a Pandas DataFrame.")

    if not isinstance(rules, dict):
        raise TypeError("Validation rules must be a dictionary.")

    errors = []
    warnings = []

    file_name = Path(file_name).name if file_name else ""
    required_columns_by_file = rules.get("required_columns", {})
    required_non_null_by_file = rules.get("required_non_null_columns", {})
    numeric_rules_by_file = rules.get("numeric_rules", {})

    required_columns = required_columns_by_file.get(file_name, [])
    required_non_null = required_non_null_by_file.get(file_name, [])
    numeric_rules = numeric_rules_by_file.get(file_name, {})

    fail_on_missing = rules.get("fail_on_missing_required_columns", True)
    allow_duplicates = rules.get("allow_duplicate_rows", False)

    if not isinstance(required_columns, list):
        raise ValueError(f"required_columns for {file_name} must be a list.")

    if not isinstance(required_non_null, list):
        raise ValueError(
            f"required_non_null_columns for {file_name} must be a list."
        )

    if not isinstance(numeric_rules, dict):
        raise ValueError(f"numeric_rules for {file_name} must be a mapping.")

    missing_columns = [
        column for column in required_columns if column not in dataframe.columns
    ]

    if missing_columns:
        message = f"Missing required columns: {missing_columns}"
        if fail_on_missing:
            errors.append(message)
        else:
            warnings.append(message)

    for column in required_non_null:
        if column not in dataframe.columns:
            continue

        missing_count = int(dataframe[column].isna().sum())
        if missing_count:
            errors.append(
                f"Required column '{column}' contains "
                f"{missing_count} missing value(s)."
            )

    duplicate_count = int(dataframe.duplicated().sum())
    if duplicate_count:
        message = f"Found {duplicate_count} duplicate row(s)."
        if allow_duplicates:
            warnings.append(message)
        else:
            errors.append(message)

    for column, limits in numeric_rules.items():
        if column not in dataframe.columns:
            continue

        if not isinstance(limits, dict):
            raise ValueError(f"Numeric rules for '{column}' must be a mapping.")

        numeric_values = pd.to_numeric(dataframe[column], errors="coerce")
        invalid_mask = dataframe[column].notna() & numeric_values.isna()

        invalid_count = int(invalid_mask.sum())
        if invalid_count:
            errors.append(
                f"Column '{column}' contains {invalid_count} non-numeric value(s)."
            )

        if "min" in limits:
            below_min = numeric_values.notna() & (
                numeric_values < limits["min"]
            )
            count = int(below_min.sum())
            if count:
                errors.append(
                    f"Column '{column}' contains {count} value(s) "
                    f"below minimum {limits['min']}."
                )

        if "max" in limits:
            above_max = numeric_values.notna() & (
                numeric_values > limits["max"]
            )
            count = int(above_max.sum())
            if count:
                errors.append(
                    f"Column '{column}' contains {count} value(s) "
                    f"above maximum {limits['max']}."
                )

    return {
        "file_name": file_name,
        "valid": len(errors) == 0,
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
        "row_count": int(len(dataframe)),
    }