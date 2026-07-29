from pathlib import Path

from legacy_pipeline_converter import convert_pipeline
from legacy_pipeline_converter.execution import execute_models
from legacy_pipeline_converter.io import (
    read_pipeline_json,
    write_dbt_artifacts,
    write_report,
    write_sql_models,
)
from legacy_pipeline_converter.models import (
    DbtGenerationConfig,
    ExecutionRequest,
    SourceDataFile,
    SourceMapping,
)
from legacy_pipeline_converter.result_validation import compare_results
from legacy_pipeline_converter.source_mapping import (
    resolve_source_mappings,
)


PROJECT_ROOT = Path(__file__).resolve().parent.parent
INPUT_PATH = PROJECT_ROOT / "data" / "legacy_pipeline.json"
OUTPUT_DIRECTORY = PROJECT_ROOT / "generated"
MODELS_DIRECTORY = OUTPUT_DIRECTORY / "models"

ORDERS_SOURCE_PATH = (
    PROJECT_ROOT / "data" / "sources" / "orders.csv"
)
CUSTOMERS_SOURCE_PATH = (
    PROJECT_ROOT / "data" / "sources" / "customers.csv"
)
EXPECTED_OUTPUT_PATH = (
    PROJECT_ROOT / "data" / "expected" / "final_output.csv"
)


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

    print("\nConversion report:")
    print(f"- {OUTPUT_DIRECTORY / 'report.json'}")

    if result.report.warnings:
        print("\nWarnings:")

        for warning in result.report.warnings:
            print(f"- [{warning.code}] {warning.message}")

    if result.ordered_pipeline is None:
        return

    source_resolution = resolve_source_mappings(
        result.ordered_pipeline.pipeline,
        mappings,
    )

    executed = execute_models(
        result.ordered_pipeline,
        result.models,
        source_resolution,
        ExecutionRequest(
            source_files=(
                SourceDataFile(
                    source_id="orders_source",
                    path=str(ORDERS_SOURCE_PATH),
                ),
                SourceDataFile(
                    source_id="customers_source",
                    path=str(CUSTOMERS_SOURCE_PATH),
                ),
            ),
            output_step_id="final_output",
            expected_file=str(EXPECTED_OUTPUT_PATH),
        ),
    )

    print("\nDuckDB execution result:")
    print(f"- Output step: {executed.output_step_id}")
    print(f"- Output relation: {executed.output_relation}")
    print(f"- Columns: {executed.columns}")
    print(f"- Row count: {executed.row_count}")

    print("\nExecuted rows:")

    for row in executed.rows:
        print(f"- {row}")

    validation = compare_results(
        executed,
        str(EXPECTED_OUTPUT_PATH),
    )

    print("\nResult validation:")
    print(f"- Executed: {validation.executed}")
    print(f"- Passed: {validation.passed}")
    print(f"- Output step: {validation.output_step_id}")
    print(f"- Actual row count: {validation.actual_row_count}")
    print(f"- Expected row count: {validation.expected_row_count}")

    if validation.differences:
        print("\nValidation differences:")

        for difference in validation.differences:
            print(f"- [{difference.kind}] {difference.message}")
    else:
        print("- No differences found.")


if __name__ == "__main__":
    main()