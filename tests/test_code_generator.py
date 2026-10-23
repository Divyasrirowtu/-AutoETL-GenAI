import pytest

from app.generation.code_generator import (
    build_prompt,
    generate_transformation,
)


def test_build_prompt_includes_schema_and_instruction():
    schema = {
        "customer_id": {"data_type": "integer"},
        "city": {"data_type": "string"},
    }
    instruction = "Standardize city names."

    prompt = build_prompt(schema, instruction)

    assert "customer_id" in prompt
    assert "city" in prompt
    assert "Standardize city names." in prompt
    assert "DataFrame named df" in prompt


def test_build_prompt_rejects_empty_schema():
    with pytest.raises(ValueError, match="schema"):
        build_prompt({}, "Remove duplicates")


def test_build_prompt_rejects_empty_instruction():
    with pytest.raises(ValueError, match="instruction"):
        build_prompt({"id": {"data_type": "integer"}}, "   ")


def test_generation_requires_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(RuntimeError, match="OPENAI_API_KEY"):
        generate_transformation(
            {"id": {"data_type": "integer"}},
            "Remove duplicate rows",
        )