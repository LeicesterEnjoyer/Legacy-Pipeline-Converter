from legacy_pipeline_converter.errors import (
    DuplicateStepIdError,
    InvalidJoinTypeError,
    MissingReferenceError,
    NoOutputStepError,
)
from legacy_pipeline_converter.models import (
    FilterStep,
    JoinStep,
    OutputStep,
    Pipeline,
)

SUPPORTED_JOIN_TYPES = frozenset({"inner", "left", "right", "full"})


def validate_pipeline(pipeline: Pipeline) -> Pipeline:
    step_lookup = {step.id: step for step in pipeline.steps}
    seen_ids: set[str] = set()

    for step in pipeline.steps:
        if step.id in seen_ids:
            raise DuplicateStepIdError(
                step_id=step.id,
                field="id",
                message=f"Duplicate step id {step.id!r}.",
            )
        seen_ids.add(step.id)

    for step in pipeline.steps:
        if isinstance(step, (FilterStep, OutputStep)):
            if step.input not in step_lookup:
                raise MissingReferenceError(
                    step_id=step.id,
                    field="input",
                    message=f"Step {step.id!r} references unknown step {step.input!r}.",
                )

        elif isinstance(step, JoinStep):
            if step.left not in step_lookup:
                raise MissingReferenceError(
                    step_id=step.id,
                    field="left",
                    message=f"Step {step.id!r} references unknown step {step.left!r}.",
                )

            if step.right not in step_lookup:
                raise MissingReferenceError(
                    step_id=step.id,
                    field="right",
                    message=f"Step {step.id!r} references unknown step {step.right!r}.",
                )

        if isinstance(step, JoinStep):
            if step.join_type not in SUPPORTED_JOIN_TYPES:
                raise InvalidJoinTypeError(
                    step_id=step.id,
                    field="join_type",
                    message=f"Step {step.id!r} has unsupported join type {step.join_type!r}.",
                )

    if not any(isinstance(step, OutputStep) for step in pipeline.steps):
        raise NoOutputStepError(
            step_id=None,
            field="steps",
            message="Pipeline must contain at least one output step.",
        )

    return pipeline