from pathlib import Path

import pytest

from legacy_pipeline_converter.errors import ExecutionError
from legacy_pipeline_converter.execution import (
    execute_models,
    render_ref_for_execution,
)
from legacy_pipeline_converter.models import (
    CalculatedColumnStep,
    ExecutionRequest,
    FilterStep,
    OutputStep,
    Pipeline,
    ResolvedSource,
    SourceDataFile,
    SourceResolution,
    SourceStep,
)
from legacy_pipeline_converter.ordering import order_steps
from legacy_pipeline_converter.sql_generator import generate_models


def _source_resolution() -> SourceResolution:
    return SourceResolution(
        sources=(
            ResolvedSource(
                source_id="orders_source",
                relation_name="analytics.raw.orders",
                used_fallback=False,
            ),
        ),
        warnings=(),
    )


def _write_orders_csv(path: Path) -> None:
    path.write_text(
        "id,status,price,quantity\n"
        "1,complete,10,2\n"
        "2,cancelled,5,3\n",
        encoding="utf-8",
    )


def test_render_ref_for_execution_replaces_generated_ref() -> None:
    sql = (
        "SELECT *\n"
        "FROM {{ ref('valid_orders') }}\n"
        "WHERE status = 'complete'\n"
    )

    rendered = render_ref_for_execution(sql)

    assert rendered == (
        "SELECT *\n"
        "FROM valid_orders\n"
        "WHERE status = 'complete'\n"
    )


def test_register_csv_sources_in_duckdb(tmp_path: Path) -> None:
    pipeline = Pipeline(
        name="source_execution",
        steps=(
            SourceStep(id="orders_source", path="orders.csv"),
            OutputStep(
                id="final_output",
                input="orders_source",
                table="orders",
            ),
        ),
    )
    ordered = order_steps(pipeline)
    resolution = _source_resolution()
    models = generate_models(ordered, resolution)
    source_path = tmp_path / "orders.csv"
    _write_orders_csv(source_path)

    executed = execute_models(
        ordered,
        models,
        resolution,
        ExecutionRequest(
            source_files=(
                SourceDataFile(
                    source_id="orders_source",
                    path=str(source_path),
                ),
            ),
            output_step_id="final_output",
        ),
    )

    assert executed.row_count == 2


def test_execute_models_runs_in_dependency_order(tmp_path: Path) -> None:
    pipeline = Pipeline(
        name="ordered_execution",
        steps=(
            SourceStep(id="orders_source", path="orders.csv"),
            FilterStep(
                id="valid_orders",
                input="orders_source",
                condition="status != 'cancelled'",
            ),
            CalculatedColumnStep(
                id="orders_with_revenue",
                input="valid_orders",
                column="revenue",
                expression="price * quantity",
            ),
            OutputStep(
                id="final_output",
                input="orders_with_revenue",
                table="orders",
            ),
        ),
    )
    ordered = order_steps(pipeline)
    resolution = _source_resolution()
    models = tuple(reversed(generate_models(ordered, resolution)))
    source_path = tmp_path / "orders.csv"
    _write_orders_csv(source_path)

    executed = execute_models(
        ordered,
        models,
        resolution,
        ExecutionRequest(
            source_files=(
                SourceDataFile(
                    source_id="orders_source",
                    path=str(source_path),
                ),
            ),
            output_step_id="final_output",
        ),
    )

    assert executed.row_count == 1


def test_execute_models_returns_selected_output_relation(
    tmp_path: Path,
) -> None:
    pipeline = Pipeline(
        name="multiple_outputs",
        steps=(
            SourceStep(id="orders_source", path="orders.csv"),
            FilterStep(
                id="valid_orders",
                input="orders_source",
                condition="status != 'cancelled'",
            ),
            OutputStep(
                id="all_orders_output",
                input="orders_source",
                table="all_orders",
            ),
            OutputStep(
                id="valid_orders_output",
                input="valid_orders",
                table="valid_orders",
            ),
        ),
    )
    ordered = order_steps(pipeline)
    resolution = _source_resolution()
    models = generate_models(ordered, resolution)
    source_path = tmp_path / "orders.csv"
    _write_orders_csv(source_path)

    executed = execute_models(
        ordered,
        models,
        resolution,
        ExecutionRequest(
            source_files=(
                SourceDataFile(
                    source_id="orders_source",
                    path=str(source_path),
                ),
            ),
            output_step_id="valid_orders_output",
        ),
    )

    assert executed.output_step_id == "valid_orders_output"
    assert executed.output_relation == "valid_orders_output"
    assert executed.row_count == 1


def test_missing_source_file_raises_clear_execution_error(
    tmp_path: Path,
) -> None:
    pipeline = Pipeline(
        name="missing_source_file",
        steps=(
            SourceStep(id="orders_source", path="orders.csv"),
            OutputStep(
                id="final_output",
                input="orders_source",
                table="orders",
            ),
        ),
    )
    ordered = order_steps(pipeline)
    resolution = _source_resolution()
    models = generate_models(ordered, resolution)
    missing_path = tmp_path / "missing.csv"

    with pytest.raises(ExecutionError) as exc_info:
        execute_models(
            ordered,
            models,
            resolution,
            ExecutionRequest(
                source_files=(
                    SourceDataFile(
                        source_id="orders_source",
                        path=str(missing_path),
                    ),
                ),
                output_step_id="final_output",
            ),
        )

    error = exc_info.value
    assert error.step_id == "orders_source"
    assert error.field == "path"
    assert str(missing_path) in error.message
