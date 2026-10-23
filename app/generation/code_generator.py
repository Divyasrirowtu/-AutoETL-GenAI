import os

from openai import OpenAI


def build_prompt(schema: dict, instruction: str) -> str:
    """Build a prompt for generating a Pandas transformation."""
    if not isinstance(schema, dict) or not schema:
        raise ValueError("A non-empty data schema is required.")

    if not isinstance(instruction, str) or not instruction.strip():
        raise ValueError("Please provide a transformation instruction.")

    return f"""
You are a data engineering assistant.

Generate Python code for a Pandas DataFrame transformation.

Input schema:
{schema}

User transformation request:
{instruction.strip()}

Requirements:
1. Assume the input DataFrame is named df.
2. Store the transformed result in a DataFrame named result.
3. Do not read or write files.
4. Do not make network requests.
5. Do not use eval, exec, subprocess, or operating-system commands.
6. Do not import modules.
7. Do not modify external files or system settings.
8. Return only Python code, without Markdown code fences.
9. Preserve the original DataFrame by creating a copy before changes.
10. Do not invent columns that are not in the schema unless the user requests them.
""".strip()


def generate_transformation(schema: dict, instruction: str) -> str:
    """Generate transformation code using the configured OpenAI model."""
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini").strip()

    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is missing. Add your API key to the root .env file."
        )

    if not model:
        raise ValueError("OPENAI_MODEL cannot be empty.")

    prompt = build_prompt(schema, instruction)

    client = OpenAI(api_key=api_key)
    response = client.responses.create(
        model=model,
        input=prompt,
    )

    generated_code = response.output_text.strip()

    if not generated_code:
        raise RuntimeError("The AI returned empty transformation code.")

    if generated_code.startswith("```"):
        lines = generated_code.splitlines()

        if lines and lines[0].startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        generated_code = "\n".join(lines).strip()

    if not generated_code:
        raise RuntimeError("No Python code was returned by the AI.")

    return generated_code