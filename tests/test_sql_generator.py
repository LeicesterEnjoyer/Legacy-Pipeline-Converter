import pytest

from legacy_pipeline_converter.models import (
    CalculatedColumnStep,
    FilterStep,
    JoinStep,
    OrderedPipeline,
    OutputStep,
    Pipeline,
    SourceStep,
)
from legacy_pipeline_converter.ordering import order_steps
from legacy_pipeline_converter.sql_generator import generate_models, source_relation_name


@pytest.fixture
def ordered_pipeline() -> OrderedPipeline:
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
    return order_steps(pipeline)


def test_generate_source_step_produces_no_model(ordered_pipeline: OrderedPipeline) -> None:
    models = generate_models(ordered_pipeline)

    assert [model.step_id for model in models] == [
        "valid_orders",
        "orders_with_revenue",
        "enriched_orders",
        "final_output",
    ]


def test_generate_filter_step_sql(ordered_pipeline: OrderedPipeline) -> None:
    models = generate_models(ordered_pipeline)
    filter_model = next(model for model in models if model.step_id == "valid_orders")

    assert "SELECT * FROM orders" in filter_model.sql
    assert "WHERE status != 'cancelled'" in filter_model.sql


def test_generate_calculated_column_step_sql(ordered_pipeline: OrderedPipeline) -> None:
    models = generate_models(ordered_pipeline)
    revenue_model = next(model for model in models if model.step_id == "orders_with_revenue")

    assert "SELECT *, price * quantity AS revenue" in revenue_model.sql
    assert "FROM {{ ref('valid_orders') }}" in revenue_model.sql


@pytest.mark.parametrize("join_type", ["inner", "left", "right", "full"])
def test_generate_join_step_sql(join_type: str) -> None:
    pipeline = Pipeline(
        name="join_types",
        steps=(
            SourceStep(id="left_source", path="left.csv"),
            SourceStep(id="right_source", path="right.csv"),
            JoinStep(
                id="joined",
                left="left_source",
                right="right_source",
                left_key="id",
                right_key="id",
                join_type=join_type,
            ),
            OutputStep(id="out", input="joined", table="out"),
        ),
    )

    models = generate_models(order_steps(pipeline))
    join_model = next(model for model in models if model.step_id == "joined")

    assert f"{join_type.upper()} JOIN" in join_model.sql
    assert "ON id = id" in join_model.sql


def test_generate_output_step_sql(ordered_pipeline: OrderedPipeline) -> None:
    models = generate_models(ordered_pipeline)
    output_model = next(model for model in models if model.step_id == "final_output")

    assert "SELECT * FROM {{ ref('enriched_orders') }}" in output_model.sql


def test_generate_uses_ref_for_transformed_upstream(ordered_pipeline: OrderedPipeline) -> None:
    models = generate_models(ordered_pipeline)
    revenue_model = next(model for model in models if model.step_id == "orders_with_revenue")

    assert "{{ ref('valid_orders') }}" in revenue_model.sql


def test_generate_uses_source_relation_name_for_source_upstream(ordered_pipeline: OrderedPipeline) -> None:
    models = generate_models(ordered_pipeline)
    filter_model = next(model for model in models if model.step_id == "valid_orders")

    assert "FROM orders" in filter_model.sql
    assert "{{ ref('" not in filter_model.sql


def test_source_relation_name_strips_nested_path_and_extension() -> None:
    assert source_relation_name("data/products.parquet") == "products"


def test_generate_filename_is_step_id_dot_sql(ordered_pipeline: OrderedPipeline) -> None:
    models = generate_models(ordered_pipeline)

    assert [model.filename for model in models] == [
        "valid_orders.sql",
        "orders_with_revenue.sql",
        "enriched_orders.sql",
        "final_output.sql",
    ]


def test_generate_does_not_include_config_blocks(ordered_pipeline: OrderedPipeline) -> None:
    models = generate_models(ordered_pipeline)

    assert all("{{ config(" not in model.sql for model in models)
    assert all("config(" not in model.sql for model in models)


def test_generate_example_pipeline_models(ordered_pipeline: OrderedPipeline) -> None:
    models = generate_models(ordered_pipeline)

    assert len(models) == 4
    assert [model.step_id for model in models] == [
        "valid_orders",
        "orders_with_revenue",
        "enriched_orders",
        "final_output",
    ]
    assert any("orders" in model.sql and "FROM orders" in model.sql for model in models)
    assert any("{{ ref('valid_orders') }}" in model.sql for model in models)
    assert any("{{ ref('enriched_orders') }}" in model.sql for model in models)


def test_generate_is_deterministic(ordered_pipeline: OrderedPipeline) -> None:
    first = generate_models(ordered_pipeline)
    second = generate_models(ordered_pipeline)

    assert first == second
    