from dataclasses import dataclass


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
