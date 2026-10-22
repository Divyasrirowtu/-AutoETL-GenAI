import json

import pandas as pd
import pytest

from app.ingestion.file_loader import load_file


def test_load_csv_file(tmp_path):
    csv_file = tmp_path / "customers.csv"
    csv_file.write_text(
        "customer_id,name\n1,Asha\n2,Ravi\n",
        encoding="utf-8",
    )

    dataframe = load_file(csv_file)

    assert isinstance(dataframe, pd.DataFrame)
    assert len(dataframe) == 2
    assert list(dataframe.columns) == ["customer_id", "name"]
    assert dataframe.iloc[0]["name"] == "Asha"


def test_load_json_file(tmp_path):
    json_file = tmp_path / "products.json"
    json_file.write_text(
        json.dumps([
            {"product_id": 101, "product_name": "Laptop"},
            {"product_id": 102, "product_name": "Mouse"},
        ]),
        encoding="utf-8",
    )

    dataframe = load_file(json_file)

    assert len(dataframe) == 2
    assert "product_name" in dataframe.columns
    assert dataframe.iloc[0]["product_name"] == "Laptop"


def test_missing_file_raises_error(tmp_path):
    missing_file = tmp_path / "missing.csv"

    with pytest.raises(FileNotFoundError):
        load_file(missing_file)


def test_unsupported_format_raises_error(tmp_path):
    text_file = tmp_path / "data.txt"
    text_file.write_text("sample data", encoding="utf-8")

    with pytest.raises(ValueError, match="Unsupported file format"):
        load_file(text_file)


def test_json_object_is_loaded_as_one_row(tmp_path):
    json_file = tmp_path / "single.json"
    json_file.write_text(
        json.dumps({"product_id": 101, "product_name": "Laptop"}),
        encoding="utf-8",
    )

    dataframe = load_file(json_file)

    assert len(dataframe) == 1
    assert dataframe.iloc[0]["product_name"] == "Laptop"