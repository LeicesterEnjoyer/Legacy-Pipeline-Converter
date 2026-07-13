import pytest

from legacy_pipeline_converter.errors import CyclicDependencyError
from legacy_pipeline_converter.models import (
    CalculatedColumnStep,
    FilterStep,
    JoinStep,
    OutputStep,
    Pipeline,
    SourceStep,
)
from legacy_pipeline_converter.ordering import order_steps


def test_order_example_pipeline_returns_dependency_order() -> None:
    pipeline = Pipeline(
        name="order_revenue_pipeline",
        steps=(
            SourceStep(id="orders_source", path="orders.csv"),
            FilterStep(id="valid_orders", input="orders_source", condition="status != 'cancelled'"),
            CalculatedColumnStep(
                id="orders_with_revenue",
                input="valid_orders",
                column="revenue",
                expression="price * quantity",
            ),
            SourceStep(id="customers_source", path="customers.csv"),
            JoinStep(
                id="enriched_orders",
                left="orders_with_revenue",
                right="customers_source",
                left_key="customer_id",
                right_key="id",
                join_type="left",
            ),
            OutputStep(id="final_output", input="enriched_orders", table="fct_orders"),
        ),
    )

    ordered = order_steps(pipeline)

    assert ordered.pipeline is pipeline
    assert ordered.execution_order == (
        "orders_source",
        "valid_orders",
        "orders_with_revenue",
        "customers_source",
        "enriched_orders",
        "final_output",
    )


def test_order_independent_steps_follow_json_declaration_order() -> None:
    pipeline = Pipeline(
        name="independent_sources",
        steps=(
            SourceStep(id="source_a", path="a.csv"),
            SourceStep(id="source_b", path="b.csv"),
            JoinStep(
                id="joined",
                left="source_a",
                right="source_b",
                left_key="id",
                right_key="id",
                join_type="inner",
            ),
            OutputStep(id="final_output", input="joined", table="fct_joined"),
        ),
    )

    ordered = order_steps(pipeline)

    assert ordered.execution_order == ("source_a", "source_b", "joined", "final_output")


def test_order_cycle_raises_clear_error() -> None:
    pipeline = Pipeline(
        name="cyclic_pipeline",
        steps=(
            FilterStep(id="a", input="b", condition="true"),
            FilterStep(id="b", input="a", condition="true"),
        ),
    )

    with pytest.raises(CyclicDependencyError) as exc_info:
        order_steps(pipeline)

    error = exc_info.value
    assert error.step_id in {"a", "b"}
    assert error.field == "input"
    assert "cycle" in error.message.lower()


def test_order_is_deterministic() -> None:
    pipeline = Pipeline(
        name="deterministic_pipeline",
        steps=(
            SourceStep(id="source_a", path="a.csv"),
            SourceStep(id="source_b", path="b.csv"),
            JoinStep(
                id="joined",
                left="source_a",
                right="source_b",
                left_key="id",
                right_key="id",
                join_type="inner",
            ),
            OutputStep(id="final_output", input="joined", table="fct_joined"),
        ),
    )

    first = order_steps(pipeline)
    second = order_steps(pipeline)

    assert first.execution_order == second.execution_order
