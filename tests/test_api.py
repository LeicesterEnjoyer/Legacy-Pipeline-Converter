import json
from pathlib import Path

from legacy_pipeline_converter.api import convert_pipeline
from legacy_pipeline_converter.io import (
    read_pipeline_json,
    write_report,
    write_sql_models,
)


def test_convert_pipeline_example_succeeds(example_pipeline_data: dict) -> None:
    ordered, models, report = convert_pipeline(
        example_pipeline_data
    )

    assert ordered is not None
    assert report.status == "success"
    assert len(models) == 4

    assert ordered.execution_order == (
        "orders_source",
        "valid_orders",
        "orders_with_revenue",
        "customers_source",
        "enriched_orders",
        "final_output",
    )

    assert report.errors == ()
    assert report.warnings == ()


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

    ordered, models, report = convert_pipeline(data)

    assert ordered is None
    assert models == ()

    assert report.status == "failed"
    assert len(report.errors) == 1
    assert "missing_source" in report.errors[0]


def test_end_to_end_file_round_trip(tmp_path: Path) -> None:
    data = read_pipeline_json(
        Path("data/legacy_pipeline.json")
    )

    ordered, models, report = convert_pipeline(data)

    assert ordered is not None

    write_sql_models(tmp_path, models)
    write_report(tmp_path / "report.json", report)

    assert len(list(tmp_path.glob("*.sql"))) == 4
    assert (tmp_path / "report.json").exists()

    report_data = json.loads(
        (tmp_path / "report.json").read_text(
            encoding="utf-8"
        )
    )

    assert report_data["status"] == "success"
    assert len(report_data["models_generated"]) == 4