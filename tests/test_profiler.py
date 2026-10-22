import pandas as pd
import pytest

from app.profiling.profiler import detect_schema, profile_data


def test_profile_counts_rows_columns_and_duplicates():
    dataframe = pd.DataFrame({
        "id": [1, 2, 2],
        "amount": [100.0, 200.0, 200.0],
    })

    report = profile_data(dataframe)

    assert report["row_count"] == 3
    assert report["column_count"] == 2
    assert report["duplicate_rows"] == 1


def test_profile_detects_missing_values():
    dataframe = pd.DataFrame({
        "name": ["Asha", None, "Ravi"],
        "age": [20, 21, None],
    })

    report = profile_data(dataframe)

    assert report["missing_values"]["name"] == 1
    assert report["missing_values"]["age"] == 1
    assert report["schema"]["name"]["nullable"] is True


def test_detect_schema_identifies_numeric_types():
    dataframe = pd.DataFrame({
        "count": [1, 2, 3],
        "price": [10.5, 20.5, 30.5],
        "name": ["Asha", "Ravi", "Meena"],
    })

    schema = detect_schema(dataframe)

    assert schema["count"]["data_type"] == "integer"
    assert schema["price"]["data_type"] == "float"
    assert schema["name"]["data_type"] == "string"


def test_profile_calculates_numeric_statistics():
    dataframe = pd.DataFrame({"score": [10, 20, 30]})

    report = profile_data(dataframe)

    assert report["numeric_statistics"]["score"]["min"] == 10.0
    assert report["numeric_statistics"]["score"]["max"] == 30.0
    assert report["numeric_statistics"]["score"]["mean"] == 20.0


def test_profile_rejects_empty_column_structure():
    dataframe = pd.DataFrame()

    with pytest.raises(ValueError, match="no columns"):
        profile_data(dataframe)