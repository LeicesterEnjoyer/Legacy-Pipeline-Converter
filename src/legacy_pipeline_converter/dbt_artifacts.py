from collections.abc import Sequence
from typing import Any

import yaml

from .models import (
    DbtGenerationConfig,
    GeneratedArtifact,
    GeneratedModel,
    Pipeline,
    SourceResolution,
    SourceStep,
)


class _IndentedSafeDumper(yaml.SafeDumper):
    def increase_indent(
        self,
        flow: bool = False,
        indentless: bool = False,
    ) -> None:
        super().increase_indent(flow, False)


def _dump_yaml(data: dict[str, Any]) -> str:
    return yaml.dump(
        data,
        Dumper=_IndentedSafeDumper,
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=False,
    )


def _relation_parts(
    relation_name: str,
) -> tuple[str | None, str | None, str]:
    parts = relation_name.split(".")

    if len(parts) == 1:
        return None, None, parts[0]

    if len(parts) == 2:
        return None, parts[0], parts[1]

    return ".".join(parts[:-2]), parts[-2], parts[-1]


def _source_group_name(database: str | None, schema: str | None) -> str:
    if database is not None and schema is not None:
        return f"{database}_{schema}"

    if schema is not None:
        return schema

    return "legacy_sources"


def _sources_document(
    pipeline: Pipeline,
    source_resolution: SourceResolution,
) -> dict[str, Any]:
    resolved_by_id = {
        source.source_id: source
        for source in source_resolution.sources
    }
    groups: dict[tuple[str | None, str | None], dict[str, Any]] = {}

    for step in pipeline.steps:
        if not isinstance(step, SourceStep):
            continue

        resolved = resolved_by_id.get(step.id)
        if resolved is None:
            continue

        database, schema, relation = _relation_parts(resolved.relation_name)
        group_key = (database, schema)

        if group_key not in groups:
            group: dict[str, Any] = {
                "name": _source_group_name(database, schema),
            }

            if database is not None:
                group["database"] = database
            if schema is not None:
                group["schema"] = schema

            group["tables"] = []
            groups[group_key] = group

        groups[group_key]["tables"].append({"name": relation})

    return {
        "version": 2,
        "sources": list(groups.values()),
    }


def _schema_document(
    models: Sequence[GeneratedModel],
    config: DbtGenerationConfig,
) -> dict[str, Any]:
    return {
        "version": 2,
        "models": [
            {
                "name": model.step_id,
                "config": {
                    "materialized": config.default_materialization,
                },
            }
            for model in models
        ],
    }


def generate_dbt_artifacts(
    pipeline: Pipeline,
    models: Sequence[GeneratedModel],
    source_resolution: SourceResolution,
    config: DbtGenerationConfig | None = None,
) -> tuple[GeneratedArtifact, ...]:
    generation_config = config or DbtGenerationConfig()

    return (
        GeneratedArtifact(
            filename="sources.yml",
            content=_dump_yaml(_sources_document(pipeline, source_resolution)),
            artifact_type="sources_yml",
        ),
        GeneratedArtifact(
            filename="schema.yml",
            content=_dump_yaml(_schema_document(models, generation_config)),
            artifact_type="schema_yml",
        ),
    )
