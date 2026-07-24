from pathlib import Path

from legacy_pipeline_converter import convert_pipeline
from legacy_pipeline_converter.io import (
    read_pipeline_json,
    write_dbt_artifacts,
    write_report,
    write_sql_models,
)
from legacy_pipeline_converter.models import (
    DbtGenerationConfig,
    SourceMapping,
)


PROJECT_ROOT = Path(__file__).resolve().parent.parent
INPUT_PATH = PROJECT_ROOT / "data" / "legacy_pipeline.json"
OUTPUT_DIRECTORY = PROJECT_ROOT / "generated"
MODELS_DIRECTORY = OUTPUT_DIRECTORY / "models"


def main() -> None:
    pipeline_data = read_pipeline_json(INPUT_PATH)

    mappings = (
        SourceMapping(
            source_id="orders_source",
            relation="orders",
            schema="raw",
        ),
        SourceMapping(
            source_id="customers_source",
            relation="customers",
            schema="raw",
        ),
    )

    result = convert_pipeline(
        pipeline_data,
        mappings=mappings,
        dbt_config=DbtGenerationConfig(
            default_materialization="view",
        ),
    )

    print(f"Conversion status: {result.report.status}")

    if result.report.status == "failed":
        print("\nConversion errors:")

        for error in result.report.errors:
            print(f"- {error}")

        return

    write_sql_models(
        MODELS_DIRECTORY,
        result.models,
    )
    write_dbt_artifacts(
        OUTPUT_DIRECTORY,
        result.artifacts,
    )
    write_report(
        OUTPUT_DIRECTORY / "report.json",
        result.report,
    )

    print("\nExecution order:")

    if result.ordered_pipeline is not None:
        for step_id in result.ordered_pipeline.execution_order:
            print(f"- {step_id}")

    print("\nGenerated SQL models:")

    for model in result.models:
        print(f"- {MODELS_DIRECTORY / model.filename}")

    print("\nGenerated dbt artifacts:")

    for artifact in result.artifacts:
        print(f"- {OUTPUT_DIRECTORY / artifact.filename}")

    print(f"\nConversion report:")
    print(f"- {OUTPUT_DIRECTORY / 'report.json'}")

    if result.report.warnings:
        print("\nWarnings:")

        for warning in result.report.warnings:
            print(f"- [{warning.code}] {warning.message}")


if __name__ == "__main__":
    main()