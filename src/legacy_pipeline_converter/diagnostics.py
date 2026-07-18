from collections import deque

from .models import (
    CalculatedColumnStep,
    FilterStep,
    JoinStep,
    OutputStep,
    Pipeline,
    WarningInfo,
)


def collect_pipeline_warnings(pipeline: Pipeline) -> tuple[WarningInfo, ...]:
    step_lookup = {step.id: step for step in pipeline.steps}
    reachable_steps: set[str] = set()
    pending: deque[str] = deque()

    for step in pipeline.steps:
        if isinstance(step, OutputStep):
            pending.append(step.id)

    while pending:
        step_id = pending.popleft()
        if step_id in reachable_steps:
            continue

        reachable_steps.add(step_id)
        step = step_lookup.get(step_id)

        if isinstance(step, (FilterStep, CalculatedColumnStep, OutputStep)):
            pending.append(step.input)
        elif isinstance(step, JoinStep):
            pending.append(step.left)
            pending.append(step.right)

    warnings: list[WarningInfo] = []
    for step in pipeline.steps:
        if step.id not in reachable_steps:
            warnings.append(
                WarningInfo(
                    code="orphan_step",
                    message=(
                        f"Step {step.id!r} is not reachable from any output step."
                    ),
                    step_id=step.id,
                    field="steps",
                )
            )

    return tuple(warnings)
