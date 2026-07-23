import json
from pathlib import Path
from typing import Any

from legacy_pipeline_converter.api import convert_pipeline
from legacy_pipeline_converter.io import (
    read_pipeline_json,
    write_dbt_artifacts,
    write_report,
    write_sql_models,
)
from legacy_pipeline_converter.models import (
    ConversionResult,
    DbtGenerationConfig,
    SourceMapping,
)


def test_convert_pipeline_v2_returns_models_artifacts_and_warnings(
    example_pipeline_data: dict,
) -> None:
    result = convert_pipeline(
        example_pipeline_data,
        mappings=(
            SourceMapping(
                source_id="orders_source",
                relation="orders",
                database="analytics",
                schema="raw",
            ),
        ),
        dbt_config=DbtGenerationConfig(default_materialization="table"),
    )

    assert isinstance(result, ConversionResult)
    assert result.ordered_pipeline is not None
    assert result.report.status == "success"
    assert len(result.models) == 4
    assert [artifact.filename for artifact in result.artifacts] == [
        "sources.yml",
        "schema.yml",
    ]
    assert "analytics.raw.orders" in result.models[0].sql
    assert "materialized: table" in result.artifacts[1].content
    assert [warning.code for warning in result.report.warnings] == [
        "missing_source_mapping",
    ]
    assert result.report.warnings[0].step_id == "customers_source"


def test_convert_pipeline_v2_preserves_v1_json_compatibility(
    example_pipeline_data: dict,
) -> None:
    result = convert_pipeline(example_pipeline_data)

    assert result.ordered_pipeline is not None
    assert result.ordered_pipeline.execution_order == (
        "orders_source",
        "valid_orders",
        "orders_with_revenue",
        "customers_source",
        "enriched_orders",
        "final_output",
    )
    assert len(result.models) == 4
    assert result.report.status == "success"
    assert result.report.errors == ()


def test_convert_pipeline_invalid_input_returns_failed_report() -> None:
    data = {
        "name": "invalid_pipeline",
        "steps": [
            {
                "id": "valid_orders",
                "type": "filter",
                "input": "missing_source",
                "condition": "status != 'cancelled'",
            },
            {
                "id": "final_output",
                "type": "output",
                "input": "valid_orders",
                "table": "fct_orders",
            },
        ],
    }

    result = convert_pipeline(data)

    assert result.ordered_pipeline is None
    assert result.models == ()
    assert result.artifacts == ()

    assert result.report.status == "failed"
    assert len(result.report.errors) == 1
    assert "missing_source" in result.report.errors[0]


def test_convert_pipeline_uses_supplied_adapter(
    example_pipeline_data: dict,
) -> None:
    class RecordingAdapter:
        def __init__(self) -> None:
            self.received_source: object | None = None

        def normalize(self, source: object) -> dict[str, Any]:
            self.received_source = source
            return example_pipeline_data

    source = object()
    adapter = RecordingAdapter()

    result = convert_pipeline(source, adapter=adapter)

    assert adapter.received_source is source
    assert result.ordered_pipeline is not None
    assert len(result.models) == 4
    assert result.report.status == "success"


def test_convert_pipeline_v2_conflicting_mapping_returns_failed_report(
    example_pipeline_data: dict,
) -> None:
    result = convert_pipeline(
        example_pipeline_data,
        mappings=(
            SourceMapping(
                source_id="orders_source",
                relation="orders",
                schema="raw",
            ),
            SourceMapping(
                source_id="orders_source",
                relation="orders",
                schema="staging",
            ),
        ),
    )

    assert result.ordered_pipeline is None
    assert result.models == ()
    assert result.artifacts == ()
    assert result.report.status == "failed"
    assert len(result.report.errors) == 1
    assert "conflicting mappings" in result.report.errors[0]


def test_convert_pipeline_v2_is_deterministic(
    example_pipeline_data: dict,
) -> None:
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

    first = convert_pipeline(example_pipeline_data, mappings=mappings)
    second = convert_pipeline(example_pipeline_data, mappings=mappings)

    assert first == second


def test_end_to_end_file_round_trip(tmp_path: Path) -> None:
    data = read_pipeline_json(
        Path("data/legacy_pipeline.json")
    )

    result = convert_pipeline(data)

    assert result.ordered_pipeline is not None

    write_sql_models(tmp_path, result.models)
    write_dbt_artifacts(tmp_path, result.artifacts)
    write_report(tmp_path / "report.json", result.report)

    assert len(list(tmp_path.glob("*.sql"))) == 4
    assert (tmp_path / "sources.yml").exists()
    assert (tmp_path / "schema.yml").exists()
    assert (tmp_path / "report.json").exists()

    report_data = json.loads(
        (tmp_path / "report.json").read_text(
            encoding="utf-8"
        )
    )

    assert report_data["status"] == "success"
    assert len(report_data["models_generated"]) == 4
