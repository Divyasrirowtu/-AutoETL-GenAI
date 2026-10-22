import pandas as pd

from app.validation.validator import validate_data


RULES = {
    "fail_on_missing_required_columns": True,
    "allow_duplicate_rows": False,
    "required_columns": {
        "customers.csv": ["customer_id", "name", "age"],
    },
    "required_non_null_columns": {
        "customers.csv": ["customer_id", "name"],
    },
    "numeric_rules": {
        "customers.csv": {
            "age": {"min": 0, "max": 120},
        },
    },
}


def test_valid_data_passes():
    dataframe = pd.DataFrame({
        "customer_id": [1, 2],
        "name": ["Asha", "Ravi"],
        "age": [24, 27],
    })

    report = validate_data(dataframe, RULES, "customers.csv")

    assert report["valid"] is True
    assert report["error_count"] == 0


def test_missing_required_column_fails():
    dataframe = pd.DataFrame({
        "customer_id": [1],
        "name": ["Asha"],
    })

    report = validate_data(dataframe, RULES, "customers.csv")

    assert report["valid"] is False
    assert any("Missing required columns" in error for error in report["errors"])


def test_missing_required_value_fails():
    dataframe = pd.DataFrame({
        "customer_id": [1],
        "name": [None],
        "age": [24],
    })

    report = validate_data(dataframe, RULES, "customers.csv")

    assert report["valid"] is False
    assert any("missing value" in error for error in report["errors"])


def test_duplicate_rows_fail_when_not_allowed():
    dataframe = pd.DataFrame({
        "customer_id": [1, 1],
        "name": ["Asha", "Asha"],
        "age": [24, 24],
    })

    report = validate_data(dataframe, RULES, "customers.csv")

    assert report["valid"] is False
    assert any("duplicate row" in error for error in report["errors"])


def test_numeric_limits_are_checked():
    dataframe = pd.DataFrame({
        "customer_id": [1, 2],
        "name": ["Asha", "Ravi"],
        "age": [24, 150],
    })

    report = validate_data(dataframe, RULES, "customers.csv")

    assert report["valid"] is False
    assert any("above maximum" in error for error in report["errors"])


def test_non_numeric_values_fail():
    dataframe = pd.DataFrame({
        "customer_id": [1],
        "name": ["Asha"],
        "age": ["unknown"],
    })

    report = validate_data(dataframe, RULES, "customers.csv")

    assert report["valid"] is False
    assert any("non-numeric" in error for error in report["errors"])