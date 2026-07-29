import re
from collections.abc import Sequence
from pathlib import Path

import duckdb

from .errors import ExecutionError
from .models import (
    ExecutedPipeline,
    ExecutionRequest,
    GeneratedModel,
    OrderedPipeline,
    OutputStep,
    SourceResolution,
    SourceStep,
)

_REF_PATTERN = re.compile(r"\{\{ ref\('([^']+)'\) \}\}")


def render_ref_for_execution(sql: str) -> str:
    return _REF_PATTERN.sub(r"\1", sql)


def _quote_identifier(identifier: str) -> str:
    escaped_identifier = identifier.replace('"', '""')
    return f'"{escaped_identifier}"'


def _local_relation_name(relation_name: str) -> str:
    return relation_name.rsplit(".", 1)[-1]


def _render_source_relations(
    sql: str,
    source_resolution: SourceResolution,
) -> str:
    rendered = sql

    for source in source_resolution.sources:
        local_name = _local_relation_name(source.relation_name)
        relation_pattern = re.compile(
            rf"(?m)(\b(?:FROM|JOIN)\s+)"
            rf"{re.escape(source.relation_name)}"
            rf"(?=(?:\s+AS\b|\s*$))"
        )
        rendered = relation_pattern.sub(
            lambda match: (
                f"{match.group(1)}"
                f"{_quote_identifier(local_name)}"
            ),
            rendered,
        )

    return rendered


def _register_sources(
    connection: duckdb.DuckDBPyConnection,
    source_resolution: SourceResolution,
    request: ExecutionRequest,
) -> None:
    source_files = {
        source_file.source_id: source_file
        for source_file in request.source_files
    }

    for source in source_resolution.sources:
        source_file = source_files.get(source.source_id)
        if source_file is None:
            raise ExecutionError(
                step_id=source.source_id,
                field="source_files",
                message=f"Source {source.source_id!r} has no execution data file.",
            )

        source_path = Path(source_file.path)
        if not source_path.is_file():
            raise ExecutionError(
                step_id=source.source_id,
                field="path",
                message=f"Source data file does not exist: {source_file.path}",
            )

        local_name = _local_relation_name(source.relation_name)

        try:
            connection.read_csv(str(source_path)).create_view(
                local_name,
                replace=True,
            )
        except duckdb.Error as error:
            raise ExecutionError(
                step_id=source.source_id,
                field="path",
                message=(
                    f"Could not register source data file "
                    f"{source_file.path!r}: {error}"
                ),
            ) from error


def _validate_output_step(
    ordered: OrderedPipeline,
    output_step_id: str,
) -> None:
    step_lookup = {
        step.id: step
        for step in ordered.pipeline.steps
    }
    output_step = step_lookup.get(output_step_id)

    if not isinstance(output_step, OutputStep):
        raise ExecutionError(
            step_id=output_step_id,
            field="output_step_id",
            message=(
                f"Execution output {output_step_id!r} must reference "
                "an output step."
            ),
        )


def execute_models(
    ordered: OrderedPipeline,
    models: Sequence[GeneratedModel],
    source_resolution: SourceResolution,
    request: ExecutionRequest,
) -> ExecutedPipeline:
    _validate_output_step(ordered, request.output_step_id)

    model_lookup = {
        model.step_id: model
        for model in models
    }
    step_lookup = {
        step.id: step
        for step in ordered.pipeline.steps
    }
    connection = duckdb.connect(":memory:")

    try:
        _register_sources(connection, source_resolution, request)

        for step_id in ordered.execution_order:
            if isinstance(step_lookup[step_id], SourceStep):
                continue

            model = model_lookup.get(step_id)
            if model is None:
                raise ExecutionError(
                    step_id=step_id,
                    field="models",
                    message=f"Generated model {step_id!r} is missing.",
                )

            rendered_sql = render_ref_for_execution(model.sql)
            rendered_sql = _render_source_relations(
                rendered_sql,
                source_resolution,
            )

            try:
                connection.execute(
                    f"CREATE OR REPLACE VIEW "
                    f"{_quote_identifier(step_id)} AS\n"
                    f"{rendered_sql}"
                )
            except duckdb.Error as error:
                raise ExecutionError(
                    step_id=step_id,
                    field="sql",
                    message=(
                        f"Could not execute generated model "
                        f"{step_id!r}: {error}"
                    ),
                ) from error

        output_relation = request.output_step_id

        try:
            output_cursor = connection.execute(
                f"SELECT * FROM "
                f"{_quote_identifier(output_relation)}"
            )
            columns = tuple(
                column[0]
                for column in output_cursor.description
            )
            rows = tuple(
                tuple(row)
                for row in output_cursor.fetchall()
            )
        except duckdb.Error as error:
            raise ExecutionError(
                step_id=request.output_step_id,
                field="output_step_id",
                message=(
                    f"Could not query execution output "
                    f"{request.output_step_id!r}: {error}"
                ),
            ) from error

        return ExecutedPipeline(
            output_step_id=request.output_step_id,
            output_relation=output_relation,
            columns=columns,
            rows=rows,
            row_count=len(rows),
        )
    finally:
        connection.close()
