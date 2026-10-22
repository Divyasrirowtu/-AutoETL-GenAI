import pandas as pd


def detect_schema(dataframe: pd.DataFrame) -> dict:
    """Detect column names, data types, and nullability."""
    schema = {}

    for column in dataframe.columns:
        series = dataframe[column]

        if pd.api.types.is_bool_dtype(series):
            data_type = "boolean"
        elif pd.api.types.is_integer_dtype(series):
            data_type = "integer"
        elif pd.api.types.is_float_dtype(series):
            data_type = "float"
        elif pd.api.types.is_datetime64_any_dtype(series):
            data_type = "datetime"
        else:
            data_type = "string" if series.dtype == object else str(series.dtype)

        schema[str(column)] = {
            "data_type": data_type,
            "nullable": bool(series.isna().any()),
            "missing_values": int(series.isna().sum()),
        }

    return schema


def profile_data(dataframe: pd.DataFrame) -> dict:
    """Generate a data-quality and statistical profile."""
    if not isinstance(dataframe, pd.DataFrame):
        raise TypeError("profile_data expects a Pandas DataFrame.")

    if len(dataframe.columns) == 0:
        raise ValueError("Cannot profile a DataFrame with no columns.")

    numeric_columns = dataframe.select_dtypes(include="number")
    numeric_statistics = {}

    for column in numeric_columns.columns:
        values = dataframe[column].dropna()

        numeric_statistics[str(column)] = {
            "min": None if values.empty else float(values.min()),
            "max": None if values.empty else float(values.max()),
            "mean": None if values.empty else float(values.mean()),
        }

    return {
        "row_count": int(len(dataframe)),
        "column_count": int(len(dataframe.columns)),
        "columns": [str(column) for column in dataframe.columns],
        "schema": detect_schema(dataframe),
        "missing_values": {
            str(column): int(count)
            for column, count in dataframe.isna().sum().items()
        },
        "duplicate_rows": int(dataframe.duplicated().sum()),
        "numeric_statistics": numeric_statistics,
    }