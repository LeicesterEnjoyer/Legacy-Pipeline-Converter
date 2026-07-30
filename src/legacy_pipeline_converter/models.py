from dataclasses import dataclass
from typing import Any, Literal


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
class SourceDataFile:
    source_id: str
    path: str


@dataclass(frozen=True)
class ExecutionRequest:
    source_files: tuple[SourceDataFile, ...]
    output_step_id: str
    expected_file: str | None = None


@dataclass(frozen=True)
class ExecutedPipeline:
    output_step_id: str
    output_relation: str
    columns: tuple[str, ...]
    rows: tuple[tuple[Any, ...], ...]
    row_count: int


@dataclass(frozen=True)
class DifferenceDetail:
    kind: Literal[
        "row_count",
        "column_names",
        "column_types",
        "row_values",
    ]
    message: str


@dataclass(frozen=True)
class ValidationSummary:
    executed: bool
    passed: bool | None
    output_step_id: str | None = None
    actual_row_count: int | None = None
    expected_row_count: int | None = None
    differences: tuple[DifferenceDetail, ...] = ()


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
    status: Literal["success", "failed"]
    models_generated: tuple[str, ...]
    errors: tuple[str, ...]
    warnings: tuple[WarningInfo, ...]
    validation: ValidationSummary | None = None


@dataclass(frozen=True)
class ConversionResult:
    ordered_pipeline: OrderedPipeline | None
    models: tuple[GeneratedModel, ...]
    artifacts: tuple[GeneratedArtifact, ...]
    report: ConversionReport
