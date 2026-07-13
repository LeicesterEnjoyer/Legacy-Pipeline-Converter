from collections import deque

from legacy_pipeline_converter.errors import CyclicDependencyError
from legacy_pipeline_converter.models import (
    CalculatedColumnStep,
    FilterStep,
    JoinStep,
    OutputStep,
    Pipeline,
    OrderedPipeline,
)


def order_steps(pipeline: Pipeline) -> OrderedPipeline:
    step_lookup = {step.id: step for step in pipeline.steps}
    step_positions = {step.id: index for index, step in enumerate(pipeline.steps)}
    incoming = {step.id: 0 for step in pipeline.steps}
    dependents: dict[str, list[str]] = {step.id: [] for step in pipeline.steps}

    for step in pipeline.steps:
        if isinstance(step, (FilterStep, CalculatedColumnStep, OutputStep)):
            if step.input in step_lookup:
                incoming[step.id] += 1
                dependents[step.input].append(step.id)

        elif isinstance(step, JoinStep):
            if step.left in step_lookup:
                incoming[step.id] += 1
                dependents[step.left].append(step.id)
            if step.right in step_lookup:
                incoming[step.id] += 1
                dependents[step.right].append(step.id)

    ready = deque(sorted((step_id for step_id, count in incoming.items() if count == 0), key=lambda item: step_positions[item]))
    ordered_ids: list[str] = []

    while ready:
        current = ready.popleft()
        ordered_ids.append(current)

        for dependent in sorted(dependents[current], key=lambda item: step_positions[item]):
            incoming[dependent] -= 1

            if incoming[dependent] == 0:
                ready.append(dependent)
        
        ready = deque(sorted(ready, key=lambda item: step_positions[item]))

    if len(ordered_ids) != len(pipeline.steps):
        cycle_step = next((step_id for step_id in incoming if incoming[step_id] > 0), pipeline.steps[0].id)

        raise CyclicDependencyError(
            step_id=cycle_step,
            field="input",
            message=f"Cycle detected involving step {cycle_step!r}.",
        )

    return OrderedPipeline(pipeline=pipeline, execution_order=tuple(ordered_ids))
