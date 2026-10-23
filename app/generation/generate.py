import argparse
from pathlib import Path

from app.configuration import load_settings
from app.generation.code_generator import generate_transformation
from app.ingestion.file_loader import load_file
from app.profiling.profiler import profile_data


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate Pandas transformation code using GenAI."
    )
    parser.add_argument(
        "--file",
        required=True,
        help="Input filename inside the configured input directory.",
    )
    parser.add_argument(
        "--instruction",
        required=True,
        help="Describe the data transformation you want.",
    )
    args = parser.parse_args()

    settings = load_settings()
    project_root = Path(__file__).resolve().parents[2]

    input_dir = (project_root / settings["data"]["input_dir"]).resolve()
    output_dir = (project_root / settings["data"]["output_dir"]).resolve()

    input_path = (input_dir / args.file).resolve()

    if input_path.parent != input_dir or not input_path.is_file():
        raise FileNotFoundError(
            "Choose an existing input file directly inside data/input."
        )

    output_dir.mkdir(parents=True, exist_ok=True)

    dataframe = load_file(input_path)
    profile = profile_data(dataframe)

    generated_code = generate_transformation(
        schema=profile["schema"],
        instruction=args.instruction,
    )

    output_path = output_dir / "generated_transform.py"
    output_path.write_text(generated_code + "\n", encoding="utf-8")

    print(f"Input file: {input_path.name}")
    print(f"Input rows: {len(dataframe)}")
    print(f"Generated code saved to: {output_path}")
    print("The generated code has NOT been executed.")


if __name__ == "__main__":
    main()