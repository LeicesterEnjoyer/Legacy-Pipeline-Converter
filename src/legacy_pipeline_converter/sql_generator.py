from pathlib import PurePath

from .models import (
    CalculatedColumnStep,
    FilterStep,
    GeneratedModel,
    JoinStep,
    OrderedPipeline,
    OutputStep,
    Pipeline,
    SourceResolution,
    SourceStep,
    Step,
)


def source_relation_name(path: str) -> str:
    return PurePath(path).stem


def _step_lookup(pipeline: Pipeline) -> dict[str, Step]:
    return {step.id: step for step in pipeline.steps}


def _source_relation_lookup(
    source_resolution: SourceResolution | None,
) -> dict[str, str]:
    if source_resolution is None:
        return {}

    return {
        source.source_id: source.relation_name
        for source in source_resolution.sources
    }


def _upstream_relation(
    step_id: str,
    step_lookup: dict[str, Step],
    source_relations: dict[str, str],
) -> str:
    upstream_step = step_lookup[step_id]

    if isinstance(upstream_step, SourceStep):
        return source_relations.get(
            upstream_step.id,
            source_relation_name(upstream_step.path),
        )

    return f"{{{{ ref('{upstream_step.id}') }}}}"


def generate_models(
    ordered_pipeline: OrderedPipeline,
    source_resolution: SourceResolution | None = None,
) -> tuple[GeneratedModel, ...]:
    models: list[GeneratedModel] = []
    step_lookup = _step_lookup(ordered_pipeline.pipeline)
    source_relations = _source_relation_lookup(source_resolution)

    for step_id in ordered_pipeline.execution_order:
        step = step_lookup[step_id]

        if isinstance(step, SourceStep):
            continue

        if isinstance(step, FilterStep):
            sql = (
                "SELECT *\n"
                f"FROM {_upstream_relation(step.input, step_lookup, source_relations)}\n"
                f"WHERE {step.condition}\n"
            )

        elif isinstance(step, CalculatedColumnStep):
            sql = (
                f"SELECT *, {step.expression} AS {step.column}\n"
                f"FROM {_upstream_relation(step.input, step_lookup, source_relations)}\n"
            )

        elif isinstance(step, JoinStep):
            join_type = step.join_type.upper()

            left_relation = _upstream_relation(
                step.left,
                step_lookup,
                source_relations,
            )
            right_relation = _upstream_relation(
                step.right,
                step_lookup,
                source_relations,
            )

            sql = (
                "SELECT *\n"
                f"FROM {left_relation} AS left_relation\n"
                f"{join_type} JOIN {right_relation} AS right_relation\n"
                f"    ON left_relation.{step.left_key} = "
                f"right_relation.{step.right_key}\n"
            )

        elif isinstance(step, OutputStep):
            sql = (
                "SELECT *\n"
                f"FROM {_upstream_relation(step.input, step_lookup, source_relations)}\n"
            )

        else:
            continue

        models.append(
            GeneratedModel(
                step_id=step.id,
                filename=f"{step.id}.sql",
                sql=sql,
            )
        )

    return tuple(models)
