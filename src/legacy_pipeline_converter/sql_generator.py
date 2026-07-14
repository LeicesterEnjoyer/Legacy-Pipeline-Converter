from pathlib import PurePath

from .models import Step
from .models import (
    CalculatedColumnStep,
    FilterStep,
    GeneratedModel,
    JoinStep,
    OrderedPipeline,
    OutputStep,
    Pipeline,
    SourceStep,
)


def source_relation_name(path: str) -> str:
    return PurePath(path).stem


def _step_lookup(pipeline: Pipeline) -> dict[str, Step]:
    return {step.id: step for step in pipeline.steps}


def _upstream_sql(step_id: str, ordered_pipeline: OrderedPipeline) -> str:
    step_lookup = _step_lookup(ordered_pipeline.pipeline)
    upstream_step = step_lookup[step_id]

    if isinstance(upstream_step, SourceStep):
        return source_relation_name(upstream_step.path)

    return f"{{{{ ref('{upstream_step.id}') }}}}"


def generate_models(ordered_pipeline: OrderedPipeline) -> tuple[GeneratedModel, ...]:
    models: list[GeneratedModel] = []
    step_lookup = _step_lookup(ordered_pipeline.pipeline)

    for step_id in ordered_pipeline.execution_order:
        step = step_lookup[step_id]

        if isinstance(step, SourceStep):
            continue

        if isinstance(step, FilterStep):
            sql = f"SELECT * FROM {_upstream_sql(step.input, ordered_pipeline)}\nWHERE {step.condition}"
        elif isinstance(step, CalculatedColumnStep):
            sql = (
                f"SELECT *, {step.expression} AS {step.column} "
                f"FROM {_upstream_sql(step.input, ordered_pipeline)}"
            )
        elif isinstance(step, JoinStep):
            join_type = step.join_type.upper()
            left_sql = _upstream_sql(step.left, ordered_pipeline)
            right_sql = _upstream_sql(step.right, ordered_pipeline)
            sql = (
                f"SELECT * FROM {left_sql}\n"
                f"{join_type} JOIN {right_sql}\n"
                f"ON {step.left_key} = {step.right_key}"
            )
        elif isinstance(step, OutputStep):
            sql = f"SELECT * FROM {_upstream_sql(step.input, ordered_pipeline)}"
        else:
            continue

        models.append(GeneratedModel(step_id=step.id, filename=f"{step.id}.sql", sql=sql))

    return tuple(models)
