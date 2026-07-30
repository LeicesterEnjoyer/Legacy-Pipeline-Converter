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

---

## Phase 9 execution without expected result data

### Question

How should the conversion report represent a successful execution when
an `ExecutionRequest` is provided without an `expected_file`?

### Clarification

When an `ExecutionRequest` is supplied, the generated pipeline is
executed even if no expected result file is provided.

If execution completes successfully but `expected_file` is `None`, the
conversion report stores:

```python
ValidationSummary(
    executed=True,
    passed=None,
    output_step_id=executed_pipeline.output_step_id,
    actual_row_count=executed_pipeline.row_count,
    expected_row_count=None,
    differences=(),
)
```

In this state:

- `executed=True` means the generated models were successfully executed;
- `passed=None` means result comparison was not requested;
- `actual_row_count` contains the number of rows produced by the selected output;
- `expected_row_count` remains `None`;
- `differences` remains empty because no comparison was performed.

### Comparison behaviour

When `expected_file` is provided, Phase 8 result comparison is performed
and `passed` becomes:

- `True` when the actual and expected results match;
- `False` when the comparison completes and differences are found.

When `expected_file` is not provided, execution still occurs, but no
comparison is performed.

### Rationale

This distinction allows the report to represent three separate states:

```text
Execution not requested:
executed=False
passed=None

Execution completed without comparison:
executed=True
passed=None

Execution completed with comparison:
executed=True
passed=True or False
```

This preserves useful execution metadata without requiring an expected
dataset for every execution request.

### Failure behaviour

If execution cannot be completed, such as because of a missing source
file or invalid generated SQL, the conversion returns a failed report.

If an expected file is supplied but cannot be read, the conversion also
returns a failed report.

A completed comparison that finds data differences does not fail the
conversion itself. It returns a successful conversion report containing:

```python
ValidationSummary(
    executed=True,
    passed=False,
    ...
)
```