# Clarifications – Version 2

## Purpose

This document records ambiguities discovered during planning and the decisions made for v2.

## How to use this document

- This file overrides ambiguities in `SPEC.md`.
- New decisions should be appended rather than rewriting previous ones.
- If a decision changes in a future version, add a new entry and mark the old one as superseded.
- Unless explicitly superseded, all decisions in this document are authoritative for v2.

---

## Phase 8 execution result access

### Question

How should Phase 8 access the executed output after Phase 7 closes its
in-memory DuckDB connection?

### Clarification

Phase 7 executes all generated models using an in-memory DuckDB
connection and closes the connection before `execute_models()`
returns.

To make the selected output available for Phase 8 result comparison,
`ExecutedPipeline` stores an immutable snapshot of the executed output
before the connection is closed.

The snapshot contains:

- ordered column names;
- all output rows;
- the output row count.

### Updated model

```python
@dataclass(frozen=True)
class ExecutedPipeline:
    output_step_id: str
    output_relation: str
    columns: tuple[str, ...]
    rows: tuple[tuple[Any, ...], ...]
    row_count: int
```

### Comparison API

Phase 8 compares the immutable execution snapshot against the expected
CSV file.

```python
def compare_results(
    executed_pipeline: ExecutedPipeline,
    expected_csv_path: str,
) -> ValidationSummary:
    ...
```

### Rationale

This design:

- preserves deterministic connection cleanup;
- avoids exposing a live DuckDB connection through the public API;
- avoids caller-managed database resources;
- keeps execution results immutable;
- supports Phase 8 and Phase 9 without changing the execution contract.

### Trade-off

The selected output is fully materialized in memory before the DuckDB
connection is closed.

This trade-off is accepted for the prototype because the expected
datasets are small. Streaming comparison and persistent DuckDB
connections remain out of scope.