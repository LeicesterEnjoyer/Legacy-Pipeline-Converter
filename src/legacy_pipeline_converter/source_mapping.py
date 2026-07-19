from pathlib import PurePath
from typing import Sequence

from .errors import ConflictingSourceMappingError
from .models import (
    Pipeline,
    ResolvedSource,
    SourceMapping,
    SourceResolution,
    SourceStep,
    WarningInfo,
)


def resolve_source_mappings(
    pipeline: Pipeline,
    mappings: Sequence[SourceMapping],
) -> SourceResolution:
    mappings_by_source: dict[str, list[SourceMapping]] = {}

    for mapping in mappings:
        mappings_by_source.setdefault(mapping.source_id, []).append(mapping)

    resolved_sources: list[ResolvedSource] = []
    warnings: list[WarningInfo] = []

    for step in pipeline.steps:
        if not isinstance(step, SourceStep):
            continue

        matching = mappings_by_source.get(step.id, [])

        if not matching:
            fallback = PurePath(step.path).stem

            resolved_sources.append(
                ResolvedSource(
                    source_id=step.id,
                    relation_name=fallback,
                    used_fallback=True,
                )
            )

            warnings.append(
                WarningInfo(
                    code="missing_source_mapping",
                    message=(
                        f"Source {step.id!r} has no explicit mapping; "
                        f"using fallback relation {fallback!r}."
                    ),
                    step_id=step.id,
                    field="path",
                )
            )

            continue

        unique_mappings = {
            (mapping.database, mapping.schema, mapping.relation)
            for mapping in matching
        }

        if len(unique_mappings) > 1:
            raise ConflictingSourceMappingError(
                step_id=step.id,
                field="source_id",
                message=(
                    f"Source {step.id!r} has conflicting mappings: "
                    f"{sorted(unique_mappings, key=str)}"
                ),
            )

        mapping = matching[0]

        if mapping.database is not None and mapping.schema is not None:
            relation_name = (
                f"{mapping.database}.{mapping.schema}.{mapping.relation}"
            )
        elif mapping.schema is not None:
            relation_name = f"{mapping.schema}.{mapping.relation}"
        else:
            relation_name = mapping.relation

        resolved_sources.append(
            ResolvedSource(
                source_id=step.id,
                relation_name=relation_name,
                used_fallback=False,
            )
        )

    return SourceResolution(sources=tuple(resolved_sources), warnings=tuple(warnings))