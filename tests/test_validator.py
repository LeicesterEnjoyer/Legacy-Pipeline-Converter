import pytest

from legacy_pipeline_converter.errors import (
    DuplicateStepIdError,
    InvalidJoinTypeError,
    MissingReferenceError,
    NoOutputStepError,
)
from legacy_pipeline_converter.models import (
    CalculatedColumnStep,
    FilterStep,
    JoinStep,
    OutputStep,
    Pipeline,
    SourceStep,
)
from legacy_pipeline_converter.parser import parse_pipeline
from legacy_pipeline_converter.validator import validate_pipeline


def test_validate_duplicate_step_id_raises_clear_error() -> None:
    pipeline = Pipeline(
        name="duplicate_ids",
        steps=(
            SourceStep(id="orders_source", path="orders.csv"),
            SourceStep(id="orders_source", path="customers.csv"),
            OutputStep(
                id="final_output",
                input="orders_source",
                table="fct_orders",
            ),
        ),
    )

    with pytest.raises(DuplicateStepIdError) as exc_info:
        validate_pipeline(pipeline)

    error = exc_info.value
    assert error.step_id == "orders_source"
    assert error.field == "id"
    assert "duplicate" in error.message.lower()


def test_validate_missing_input_reference_raises_clear_error() -> None:
    pipeline = Pipeline(
        name="missing_dependency",
        steps=(
            FilterStep(
                id="valid_orders",
                input="missing_step",
                condition="status != 'cancelled'",
            ),
            OutputStep(
                id="final_output",
                input="valid_orders",
                table="fct_orders",
            ),
        ),
    )

    with pytest.raises(MissingReferenceError) as exc_info:
        validate_pipeline(pipeline)

    error = exc_info.value
    assert error.step_id == "valid_orders"
    assert error.field == "input"
    assert "missing_step" in error.message


def test_validate_join_missing_left_reference_raises_clear_error() -> None:
    pipeline = Pipeline(
        name="missing_join_left_reference",
        steps=(
            SourceStep(id="right_source", path="customers.csv"),
            JoinStep(
                id="enriched_orders",
                left="missing_left",
                right="right_source",
                left_key="customer_id",
                right_key="id",
                join_type="inner",
            ),
            OutputStep(
                id="final_output",
                input="enriched_orders",
                table="fct_orders",
            ),
        ),
    )

    with pytest.raises(MissingReferenceError) as exc_info:
        validate_pipeline(pipeline)

    error = exc_info.value
    assert error.step_id == "enriched_orders"
    assert error.field == "left"
    assert "missing_left" in error.message


def test_validate_join_missing_right_reference_raises_clear_error() -> None:
    pipeline = Pipeline(
        name="missing_join_right_reference",
        steps=(
            SourceStep(id="left_source", path="orders.csv"),
            JoinStep(
                id="enriched_orders",
                left="left_source",
                right="missing_right",
                left_key="customer_id",
                right_key="id",
                join_type="inner",
            ),
            OutputStep(
                id="final_output",
                input="enriched_orders",
                table="fct_orders",
            ),
        ),
    )

    with pytest.raises(MissingReferenceError) as exc_info:
        validate_pipeline(pipeline)

    error = exc_info.value
    assert error.step_id == "enriched_orders"
    assert error.field == "right"
    assert "missing_right" in error.message


def test_validate_invalid_join_type_raises_clear_error() -> None:
    pipeline = Pipeline(
        name="invalid_join_type",
        steps=(
            SourceStep(id="left_source", path="orders.csv"),
            SourceStep(id="right_source", path="customers.csv"),
            JoinStep(
                id="joined_orders",
                left="left_source",
                right="right_source",
                left_key="customer_id",
                right_key="id",
                join_type="cross",
            ),
            OutputStep(
                id="final_output",
                input="joined_orders",
                table="fct_orders",
            ),
        ),
    )

    with pytest.raises(InvalidJoinTypeError) as exc_info:
        validate_pipeline(pipeline)

    error = exc_info.value
    assert error.step_id == "joined_orders"
    assert error.field == "join_type"
    assert "cross" in error.message


@pytest.mark.parametrize("join_type", ["inner", "left", "right", "full"])
def test_validate_all_supported_join_types_pass(join_type: str) -> None:
    pipeline = Pipeline(
        name=f"{join_type}_join",
        steps=(
            SourceStep(id="left_source", path="orders.csv"),
            SourceStep(id="right_source", path="customers.csv"),
            JoinStep(
                id="joined_orders",
                left="left_source",
                right="right_source",
                left_key="customer_id",
                right_key="id",
                join_type=join_type,
            ),
            OutputStep(
                id="final_output",
                input="joined_orders",
                table="fct_orders",
            ),
        ),
    )

    validate_pipeline(pipeline)


def test_validate_zero_output_steps_raises_clear_error() -> None:
    pipeline = Pipeline(
        name="no_output",
        steps=(
            SourceStep(id="orders_source", path="orders.csv"),
            FilterStep(
                id="valid_orders",
                input="orders_source",
                condition="status != 'cancelled'",
            ),
        ),
    )

    with pytest.raises(NoOutputStepError) as exc_info:
        validate_pipeline(pipeline)

    error = exc_info.value
    assert error.step_id is None
    assert error.field == "steps"
    assert "output" in error.message.lower()


def test_validate_multiple_output_steps_allowed() -> None:
    pipeline = Pipeline(
        name="multiple_outputs",
        steps=(
            SourceStep(id="orders_source", path="orders.csv"),
            OutputStep(
                id="out_a",
                input="orders_source",
                table="out_a",
            ),
            OutputStep(
                id="out_b",
                input="orders_source",
                table="out_b",
            ),
        ),
    )

    validated = validate_pipeline(pipeline)

    assert validated is pipeline
    assert validated.name == "multiple_outputs"
    assert len(validated.steps) == 3


def test_validate_orphan_steps_do_not_fail() -> None:
    pipeline = Pipeline(
        name="orphan_step",
        steps=(
            SourceStep(id="orders_source", path="orders.csv"),
            FilterStep(
                id="valid_orders",
                input="orders_source",
                condition="status != 'cancelled'",
            ),
            OutputStep(
                id="final_output",
                input="orders_source",
                table="fct_orders",
            ),
            CalculatedColumnStep(
                id="orphan_metric",
                input="orders_source",
                column="revenue",
                expression="price * quantity",
            ),
        ),
    )

    validated = validate_pipeline(pipeline)

    assert validated is pipeline
    assert validated.name == "orphan_step"
    assert [step.id for step in validated.steps] == [
        "orders_source",
        "valid_orders",
        "final_output",
        "orphan_metric",
    ]


def test_validate_example_pipeline_passes(
    example_pipeline_data: dict,
) -> None:
    pipeline = parse_pipeline(example_pipeline_data)

    validated = validate_pipeline(pipeline)

    assert validated is pipeline
    assert validated.name == "order_revenue_pipeline"