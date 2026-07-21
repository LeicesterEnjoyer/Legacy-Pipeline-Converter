from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class SourceStep:
    id: str
    path: str


@dataclass(frozen=True)
class FilterStep:
    id: str
    input: str
    condition: str


@dataclass(frozen=True)
class CalculatedColumnStep:
    id: str
    input: str
    column: str
    expression: str


@dataclass(frozen=True)
class JoinStep:
    id: str
    left: str
    right: str
    left_key: str
    right_key: str
    join_type: str


@dataclass(frozen=True)
class OutputStep:
    id: str
    input: str
    table: str


Step = SourceStep | FilterStep | CalculatedColumnStep | JoinStep | OutputStep


@dataclass(frozen=True)
class Pipeline:
    name: str
    steps: tuple[Step, ...]


@dataclass(frozen=True)
class OrderedPipeline:
    pipeline: Pipeline
    execution_order: tuple[str, ...]


@dataclass(frozen=True)
class GeneratedModel:
    step_id: str
    filename: str
    sql: str


@dataclass(frozen=True)
class GeneratedArtifact:
    filename: str
    content: str
    artifact_type: Literal["sources_yml", "schema_yml"]


@dataclass(frozen=True)
class DbtGenerationConfig:
    default_materialization: Literal["view", "table"] = "view"


@dataclass(frozen=True)
class WarningInfo:
    code: str
    message: str
    step_id: str | None = None
    field: str | None = None


@dataclass(frozen=True)
class SourceMapping:
    source_id: str
    relation: str
    database: str | None = None
    schema: str | None = None


@dataclass(frozen=True)
class ResolvedSource:
    source_id: str
    relation_name: str
    used_fallback: bool


@dataclass(frozen=True)
class SourceResolution:
    sources: tuple[ResolvedSource, ...]
    warnings: tuple[WarningInfo, ...]


@dataclass(frozen=True)
class ConversionReport:
    pipeline_name: str
    status: str
    models_generated: tuple[str, ...]
    errors: tuple[str, ...]
    warnings: tuple[WarningInfo, ...]
