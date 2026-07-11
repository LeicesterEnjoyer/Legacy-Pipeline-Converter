from typing import Any

from legacy_pipeline_converter.errors import ParseError, UnsupportedStepTypeError
from legacy_pipeline_converter.models import (
    CalculatedColumnStep,
    FilterStep,
    JoinStep,
    OutputStep,
    Pipeline,
    SourceStep,
    Step,
)

SUPPORTED_STEP_TYPES = frozenset(
    {"source", "filter", "calculated_column", "join", "output"}
)

STEP_REQUIRED_FIELDS: dict[str, tuple[str, ...]] = {
    "source": ("id", "type", "path"),
    "filter": ("id", "type", "input", "condition"),
    "calculated_column": ("id", "type", "input", "column", "expression"),
    "join": ("id", "type", "left", "right", "left_key", "right_key", "join_type"),
    "output": ("id", "type", "input", "table"),
}


def parse_pipeline(data: dict[str, Any]) -> Pipeline:
    if "name" not in data:
        raise ParseError(
            step_id=None,
            field="name",
            message="Pipeline is missing required field 'name'.",
        )

    if "steps" not in data:
        raise ParseError(
            step_id=None,
            field="steps",
            message="Pipeline is missing required field 'steps'.",
        )

    steps_data = data["steps"]
    if not isinstance(steps_data, list):
        raise ParseError(
            step_id=None,
            field="steps",
            message="Pipeline field 'steps' must be a list.",
        )

    steps = tuple(
        _parse_step(step_data, index)
        for index, step_data in enumerate(steps_data)
    )

    return Pipeline(name=data["name"], steps=steps)


def _parse_step(step_data: Any, index: int) -> Step:
    if not isinstance(step_data, dict):
        raise ParseError(
            step_id=None,
            field="steps",
            message=f"Invalid step at index {index}: step must be an object.",
        )

    if "id" not in step_data:
        raise ParseError(
            step_id=None,
            field="id",
            message=f"Invalid step at index {index}: field 'id' is required.",
        )

    step_id = step_data.get("id")
    step_type = step_data.get("type")

    if step_type is None:
        raise ParseError(
            step_id=step_id,
            field="type",
            message=f"Step {step_id!r} is missing required field 'type'.",
        )

    if step_type not in SUPPORTED_STEP_TYPES:
        raise UnsupportedStepTypeError(
            step_id=step_id,
            field="type",
            message=(
                f"Step {step_id!r} has unsupported type {step_type!r}."
                if step_id is not None
                else f"Step has unsupported type {step_type!r}."
            ),
        )

    for field in STEP_REQUIRED_FIELDS[step_type]:
        if field not in step_data:
            raise ParseError(
                step_id=step_id,
                field=field,
                message=f"Step {step_id!r} is missing required field {field!r}.",
            )

    if step_type == "source":
        return SourceStep(id=step_data["id"], path=step_data["path"])
    if step_type == "filter":
        return FilterStep(
            id=step_data["id"],
            input=step_data["input"],
            condition=step_data["condition"],
        )
    if step_type == "calculated_column":
        return CalculatedColumnStep(
            id=step_data["id"],
            input=step_data["input"],
            column=step_data["column"],
            expression=step_data["expression"],
        )
    if step_type == "join":
        return JoinStep(
            id=step_data["id"],
            left=step_data["left"],
            right=step_data["right"],
            left_key=step_data["left_key"],
            right_key=step_data["right_key"],
            join_type=step_data["join_type"],
        )

    return OutputStep(
        id=step_data["id"],
        input=step_data["input"],
        table=step_data["table"],
    )
