import json
from pathlib import Path

from legacy_pipeline_converter.io import (
    read_pipeline_json,
    write_report,
    write_sql_models,
)
from legacy_pipeline_converter.models import (
    ConversionReport,
    GeneratedModel,
)


def test_read_pipeline_json_loads_example_file() -> None:
    path = Path("data/legacy_pipeline.json")

    data = read_pipeline_json(path)

    assert isinstance(data, dict)
    assert data["name"] == "order_revenue_pipeline"
    assert len(data["steps"]) == 6


def test_write_sql_models_and_report_creates_files(tmp_path: Path) -> None:
    models = (
        GeneratedModel(
            step_id="valid_orders",
            filename="valid_orders.sql",
            sql="SELECT * FROM orders WHERE status != 'cancelled'",
        ),
        GeneratedModel(
            step_id="final_output",
            filename="final_output.sql",
            sql="SELECT * FROM {{ ref('valid_orders') }}",
        ),
    )

    report = ConversionReport(
        pipeline_name="demo",
        status="success",
        models_generated=(
            "valid_orders.sql",
            "final_output.sql",
        ),
        errors=(),
        warnings=(),
    )

    write_sql_models(tmp_path, models)
    write_report(tmp_path / "report.json", report)

    assert (tmp_path / "valid_orders.sql").read_text(
        encoding="utf-8"
    ) == "SELECT * FROM orders WHERE status != 'cancelled'"

    assert (tmp_path / "final_output.sql").read_text(
        encoding="utf-8"
    ) == "SELECT * FROM {{ ref('valid_orders') }}"

    report_data = json.loads(
        (tmp_path / "report.json").read_text(encoding="utf-8")
    )

    assert report_data == {
        "pipeline_name": "demo",
        "status": "success",
        "models_generated": [
            "valid_orders.sql",
            "final_output.sql",
        ],
        "errors": [],
        "warnings": [],
    }