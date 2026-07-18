from legacy_pipeline_converter.diagnostics import collect_pipeline_warnings
from legacy_pipeline_converter.models import (
    FilterStep,
    OutputStep,
    Pipeline,
    SourceStep,
)


def test_collect_warnings_returns_no_orphan_warning_for_fully_used_pipeline() -> None:
    pipeline = Pipeline(
        name="demo",
        steps=(
            SourceStep(id="orders_source", path="orders.csv"),
            FilterStep(
                id="valid_orders",
                input="orders_source",
                condition="status != 'cancelled'",
            ),
            OutputStep(
                id="final_output",
                input="valid_orders",
                table="fct_orders",
            ),
        ),
    )

    warnings = collect_pipeline_warnings(pipeline)

    assert warnings == ()


def test_collect_warnings_emits_orphan_warning() -> None:
    pipeline = Pipeline(
        name="demo",
        steps=(
            SourceStep(id="orders_source", path="orders.csv"),
            FilterStep(
                id="valid_orders",
                input="orders_source",
                condition="status != 'cancelled'",
            ),
            OutputStep(
                id="final_output",
                input="valid_orders",
                table="fct_orders",
            ),
            SourceStep(id="orphan_source", path="customers.csv"),
        ),
    )

    warnings = collect_pipeline_warnings(pipeline)

    assert len(warnings) == 1
    assert warnings[0].code == "orphan_step"
    assert warnings[0].step_id == "orphan_source"
    assert warnings[0].field == "steps"
    assert "not reachable" in warnings[0].message


def test_orphan_warnings_follow_declaration_order() -> None:
    pipeline = Pipeline(
        name="demo",
        steps=(
            SourceStep(id="used_source", path="orders.csv"),
            OutputStep(
                id="final_output",
                input="used_source",
                table="fct_orders",
            ),
            SourceStep(id="first_orphan", path="first.csv"),
            SourceStep(id="second_orphan", path="second.csv"),
        ),
    )

    warnings = collect_pipeline_warnings(pipeline)

    assert tuple(warning.step_id for warning in warnings) == (
        "first_orphan",
        "second_orphan",
    )