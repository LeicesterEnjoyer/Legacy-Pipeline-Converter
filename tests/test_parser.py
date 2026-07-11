import pytest

from legacy_pipeline_converter.errors import ParseError, UnsupportedStepTypeError
from legacy_pipeline_converter.models import (
    CalculatedColumnStep,
    FilterStep,
    JoinStep,
    OutputStep,
    Pipeline,
    SourceStep,
)
from legacy_pipeline_converter.parser import parse_pipeline


def test_parse_example_pipeline_succeeds(example_pipeline_data: dict) -> None:
    pipeline = parse_pipeline(example_pipeline_data)

    assert isinstance(pipeline, Pipeline)
    assert pipeline.name == "order_revenue_pipeline"
    assert len(pipeline.steps) == 6
    assert [step.id for step in pipeline.steps] == [
        "orders_source",
        "valid_orders",
        "orders_with_revenue",
        "customers_source",
        "enriched_orders",
        "final_output",
    ]
    assert isinstance(pipeline.steps[0], SourceStep)
    assert isinstance(pipeline.steps[1], FilterStep)
    assert isinstance(pipeline.steps[2], CalculatedColumnStep)
    assert isinstance(pipeline.steps[3], SourceStep)
    assert isinstance(pipeline.steps[4], JoinStep)
    assert isinstance(pipeline.steps[5], OutputStep)


def test_parse_source_step_fields() -> None:
    pipeline = parse_pipeline(
        {
            "name": "source_only",
            "steps": [{"id": "orders_source", "type": "source", "path": "orders.csv"}],
        }
    )

    step = pipeline.steps[0]
    assert isinstance(step, SourceStep)
    assert step.id == "orders_source"
    assert step.path == "orders.csv"


def test_parse_filter_step_fields() -> None:
    pipeline = parse_pipeline(
        {
            "name": "filter_only",
            "steps": [
                {
                    "id": "valid_orders",
                    "type": "filter",
                    "input": "orders_source",
                    "condition": "status != 'cancelled'",
                }
            ],
        }
    )

    step = pipeline.steps[0]
    assert isinstance(step, FilterStep)
    assert step.id == "valid_orders"
    assert step.input == "orders_source"
    assert step.condition == "status != 'cancelled'"


def test_parse_calculated_column_step_fields() -> None:
    pipeline = parse_pipeline(
        {
            "name": "calculated_only",
            "steps": [
                {
                    "id": "orders_with_revenue",
                    "type": "calculated_column",
                    "input": "valid_orders",
                    "column": "revenue",
                    "expression": "price * quantity",
                }
            ],
        }
    )

    step = pipeline.steps[0]
    assert isinstance(step, CalculatedColumnStep)
    assert step.id == "orders_with_revenue"
    assert step.input == "valid_orders"
    assert step.column == "revenue"
    assert step.expression == "price * quantity"


def test_parse_join_step_fields() -> None:
    pipeline = parse_pipeline(
        {
            "name": "join_only",
            "steps": [
                {
                    "id": "enriched_orders",
                    "type": "join",
                    "left": "orders_with_revenue",
                    "right": "customers_source",
                    "left_key": "customer_id",
                    "right_key": "id",
                    "join_type": "left",
                }
            ],
        }
    )

    step = pipeline.steps[0]
    assert isinstance(step, JoinStep)
    assert step.id == "enriched_orders"
    assert step.left == "orders_with_revenue"
    assert step.right == "customers_source"
    assert step.left_key == "customer_id"
    assert step.right_key == "id"
    assert step.join_type == "left"


def test_parse_output_step_fields() -> None:
    pipeline = parse_pipeline(
        {
            "name": "output_only",
            "steps": [
                {
                    "id": "final_output",
                    "type": "output",
                    "input": "enriched_orders",
                    "table": "fct_order_revenue",
                }
            ],
        }
    )

    step = pipeline.steps[0]
    assert isinstance(step, OutputStep)
    assert step.id == "final_output"
    assert step.input == "enriched_orders"
    assert step.table == "fct_order_revenue"


def test_parse_unsupported_step_type_raises_clear_error() -> None:
    with pytest.raises(UnsupportedStepTypeError) as exc_info:
        parse_pipeline(
            {
                "name": "unsupported",
                "steps": [{"id": "bad_step", "type": "aggregate", "input": "orders"}],
            }
        )

    error = exc_info.value
    assert error.step_id == "bad_step"
    assert error.field == "type"
    assert "aggregate" in error.message
    assert "bad_step" in str(error)


def test_parse_missing_required_field_raises_clear_error() -> None:
    with pytest.raises(ParseError) as exc_info:
        parse_pipeline(
            {
                "name": "missing_field",
                "steps": [{"id": "valid_orders", "type": "filter", "input": "orders_source"}],
            }
        )

    error = exc_info.value
    assert error.step_id == "valid_orders"
    assert error.field == "condition"
    assert "condition" in error.message
    assert "valid_orders" in str(error)


def test_parse_ignores_extra_fields() -> None:
    pipeline = parse_pipeline(
        {
            "name": "extra_fields",
            "steps": [
                {
                    "id": "orders_source",
                    "type": "source",
                    "path": "orders.csv",
                    "legacy_metadata": "ignored",
                }
            ],
        }
    )

    step = pipeline.steps[0]
    assert isinstance(step, SourceStep)
    assert not hasattr(step, "legacy_metadata")


def test_parse_missing_pipeline_name_raises_clear_error() -> None:
    with pytest.raises(ParseError) as exc_info:
        parse_pipeline({"steps": []})

    error = exc_info.value
    assert error.step_id is None
    assert error.field == "name"
    assert "name" in error.message


def test_parse_empty_steps_list_succeeds() -> None:
    pipeline = parse_pipeline({"name": "empty_pipeline", "steps": []})

    assert pipeline.name == "empty_pipeline"
    assert pipeline.steps == ()
