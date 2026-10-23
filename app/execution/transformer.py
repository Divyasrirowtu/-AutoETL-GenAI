import re

import pandas as pd


def apply_transformations(
    dataframe: pd.DataFrame,
    operations: list[dict],
) -> pd.DataFrame:
    """Apply only explicitly approved transformation operations."""
    if not isinstance(dataframe, pd.DataFrame):
        raise TypeError("Expected a Pandas DataFrame.")

    if not isinstance(operations, list):
        raise TypeError("Operations must be supplied as a list.")

    result = dataframe.copy()

    for operation in operations:
        if not isinstance(operation, dict):
            raise ValueError("Each transformation must be a dictionary.")

        name = operation.get("operation")

        if name == "drop_duplicates":
            result = result.drop_duplicates().reset_index(drop=True)

        elif name == "trim_strings":
            for column in result.select_dtypes(include=["object", "string"]).columns:
                result[column] = result[column].map(
                    lambda value: value.strip() if isinstance(value, str) else value
                )

        elif name == "standardize_column_names":
            new_columns = [
                re.sub(r"_+", "_", re.sub(r"[^a-zA-Z0-9]+", "_", str(column)))
                .strip("_")
                .lower()
                for column in result.columns
            ]

            if len(new_columns) != len(set(new_columns)):
                raise ValueError(
                    "Standardizing column names would create duplicate names."
                )

            result.columns = new_columns

        elif name in {"filter_numeric_min", "filter_numeric_max"}:
            column = operation.get("column")
            threshold = operation.get("value")

            if column not in result.columns:
                raise ValueError(f"Column not found: {column}")

            if isinstance(threshold, bool) or not isinstance(
                threshold, (int, float)
            ):
                raise ValueError("Filter threshold must be a number.")

            numeric_values = pd.to_numeric(result[column], errors="coerce")

            if numeric_values.isna().any():
                raise ValueError(
                    f"Column '{column}' contains missing or non-numeric values."
                )

            if name == "filter_numeric_min":
                result = result.loc[numeric_values >= threshold].copy()
            else:
                result = result.loc[numeric_values <= threshold].copy()

            result = result.reset_index(drop=True)

        elif name == "drop_missing_rows":
            columns = operation.get("columns")

            if columns is not None:
                if not isinstance(columns, list):
                    raise ValueError("'columns' must be a list.")

                missing = [column for column in columns if column not in result.columns]
                if missing:
                    raise ValueError(f"Columns not found: {missing}")

            result = result.dropna(subset=columns).reset_index(drop=True)

        else:
            raise ValueError(f"Unsupported transformation operation: {name}")

    return result