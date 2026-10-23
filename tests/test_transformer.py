import pandas as pd
import pytest

from app.execution.transformer import apply_transformations


def test_drop_duplicates():
    dataframe = pd.DataFrame({
        "id": [1, 1, 2],
        "name": ["Asha", "Asha", "Ravi"],
    })

    result = apply_transformations(
        dataframe,
        [{"operation": "drop_duplicates"}],
    )

    assert len(result) == 2


def test_trim_strings():
    dataframe = pd.DataFrame({"name": [" Asha ", " Ravi "]})

    result = apply_transformations(
        dataframe,
        [{"operation": "trim_strings"}],
    )

    assert result["name"].tolist() == ["Asha", "Ravi"]


def test_standardize_column_names():
    dataframe = pd.DataFrame({"Customer Name": ["Asha"], "City-Name": ["Guntur"]})

    result = apply_transformations(
        dataframe,
        [{"operation": "standardize_column_names"}],
    )

    assert result.columns.tolist() == ["customer_name", "city_name"]


def test_filter_numeric_minimum():
    dataframe = pd.DataFrame({"age": [16, 18, 25]})

    result = apply_transformations(
        dataframe,
        [{"operation": "filter_numeric_min", "column": "age", "value": 18}],
    )

    assert result["age"].tolist() == [18, 25]


def test_unknown_operation_is_rejected():
    dataframe = pd.DataFrame({"id": [1]})

    with pytest.raises(ValueError, match="Unsupported"):
        apply_transformations(dataframe, [{"operation": "run_arbitrary_code"}])


def test_original_dataframe_is_not_modified():
    dataframe = pd.DataFrame({"name": [" Asha "]})

    apply_transformations(dataframe, [{"operation": "trim_strings"}])

    assert dataframe.iloc[0]["name"] == " Asha "


def test_standardized_duplicate_column_names_are_rejected():
    dataframe = pd.DataFrame([[1, 2]], columns=["City Name", "City-Name"])

    with pytest.raises(ValueError, match="duplicate names"):
        apply_transformations(
            dataframe,
            [{"operation": "standardize_column_names"}],
        )