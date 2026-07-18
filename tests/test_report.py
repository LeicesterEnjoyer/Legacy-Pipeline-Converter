from dataclasses import asdict

from legacy_pipeline_converter.models import ConversionReport, WarningInfo
from legacy_pipeline_converter.report import build_report


def test_build_report_success_schema() -> None:
    report = build_report(
        pipeline_name="demo",
        status="success",
        models_generated=["valid_orders.sql", "final_output.sql"],
        errors=[],
        warnings=[],
    )

    assert isinstance(report, ConversionReport)

    report_data = asdict(report)

    assert set(report_data) == {
        "pipeline_name",
        "status",
        "models_generated",
        "errors",
        "warnings",
    }

    assert report_data["pipeline_name"] == "demo"
    assert report_data["status"] == "success"
    assert report_data["models_generated"] == (
        "valid_orders.sql",
        "final_output.sql",
    )
    assert report_data["errors"] == ()
    assert report_data["warnings"] == ()


def test_build_report_success_populates_models_generated() -> None:
    report = build_report(
        pipeline_name="demo",
        status="success",
        models_generated=["valid_orders.sql", "final_output.sql"],
        errors=[],
        warnings=[],
    )

    assert report.status == "success"
    assert report.models_generated == (
        "valid_orders.sql",
        "final_output.sql",
    )
    assert report.errors == ()
    assert report.warnings == ()


def test_build_report_failure_populates_errors() -> None:
    error_message = (
        "Step 'valid_orders' references unknown step "
        "'missing_step'. (step: 'valid_orders', field: input)"
    )

    report = build_report(
        pipeline_name="demo",
        status="failed",
        models_generated=[],
        errors=[error_message],
        warnings=[],
    )

    assert report.status == "failed"
    assert report.models_generated == ()
    assert report.errors == (error_message,)
    assert report.warnings == ()


def test_build_report_populates_structured_warnings() -> None:
    warning = WarningInfo(
        code="orphan_step",
        message="Step 'orphan' is not reachable from any output step.",
        step_id="orphan",
        field="steps",
    )

    report = build_report(
        pipeline_name="demo",
        status="success",
        models_generated=["valid_orders.sql"],
        errors=[],
        warnings=[warning],
    )

    assert report.warnings == (warning,)


def test_warning_serializes_to_expected_json_object() -> None:
    warning = WarningInfo(
        code="orphan_step",
        message="Step 'orphan' is not reachable from any output step.",
        step_id="orphan",
        field="steps",
    )

    report = build_report(
        pipeline_name="demo",
        status="success",
        models_generated=[],
        errors=[],
        warnings=[warning],
    )

    report_data = asdict(report)

    assert report_data["warnings"] == (
        {
            "code": "orphan_step",
            "message": (
                "Step 'orphan' is not reachable from any output step."
            ),
            "step_id": "orphan",
            "field": "steps",
        },
    )