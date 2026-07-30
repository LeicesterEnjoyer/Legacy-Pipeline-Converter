# Legacy ETL to ELT Modernisation Prototype

A Python prototype that converts simplified legacy ETL pipeline definitions into modern ELT-style transformations, generates deterministic dbt artifacts, and supports local execution through DuckDB.

This project focuses on:

- Legacy ETL to modern ELT migration
- Dependency analysis and transformation ordering
- Deterministic SQL generation
- Specification-driven development
- Test-driven development (TDD)
- AI-assisted software engineering with full human ownership

The project is developed using AI-assisted software engineering while keeping architecture, specifications, and implementation decisions under explicit human control.

---

## Goals

The application should:

1. Read a legacy pipeline definition from JSON.
2. Parse supported transformation types.
3. Validate pipeline definitions.
4. Build a dependency graph and determine transformation order.
5. Generate deterministic dbt-style SQL models and dbt project artifacts.
6. Produce a unified conversion result containing generated models, dbt artifacts, and a conversion report.
7. Execute generated transformations locally using DuckDB.
8. Validate execution results against expected datasets.

---

## Current Scope (v2.1)

### Supported transformation types

- `source`
- `filter`
- `calculated_column`
- `join`
- `output`

### Features

- Normalize pipeline input through an explicit adapter contract.
- Support the existing JSON dictionary format through the default `JsonPipelineAdapter`.
- Support custom adapter injection for future vendor-specific formats.
- Parse normalized pipeline definitions.
- Validate:
  - unique step IDs;
  - missing dependencies;
  - supported join types;
  - at least one output step.
- Build a dependency graph and deterministic topological ordering.
- Generate deterministic dbt-style SQL models.
- Generate structured conversion warnings.
- Detect orphan pipeline steps.
- Support explicit source-to-relation mappings.
- Resolve warehouse source relations with deterministic fallbacks.
- Generate deterministic dbt artifacts (`sources.yml`, `schema.yml`).
- Support configurable default dbt model materialization.
- Generate a JSON conversion report.
- Provide an automated specification-driven test suite.
- Integrate parsing, validation, diagnostics, source resolution, SQL generation, dbt artifact generation, and reporting through a unified conversion API.
- Execute generated SQL models locally using DuckDB.
- Register CSV source files for local execution.
- Render generated dbt references for execution.
- Return execution metadata for a selected output step.
- Capture immutable execution snapshots containing output columns and rows.
- Compare execution results against expected CSV datasets.
- Report column, row count, and row value differences.
- Support optional execution and result validation through the unified conversion API.

---

## Out of Scope

- Real Informatica, SSIS, Talend, or IICS parsers
- Cloud warehouse deployment
- Frontend or UI
- Arbitrary SQL conversion
- Direct LLM integration
- Support for every transformation type

---

## Program Workflow

The complete workflow is:

```text
Legacy pipeline input
        ↓
Pipeline adapter
        ↓
Parsing into domain models
        ↓
Pipeline validation
        ↓
Warning and orphan-step diagnostics
        ↓
Source mapping resolution
        ↓
Dependency graph and execution ordering
        ↓
dbt SQL model generation
        ↓
dbt YAML artifact generation
        ↓
Optional DuckDB execution
        ↓
Optional expected-result comparison
        ↓
Conversion report
        ↓
Generated SQL, YAML, and JSON artifacts
```

### Workflow steps

1. Input normalization

    The user provides a pipeline definition. The default
    JsonPipelineAdapter accepts the existing dictionary-based JSON format,
    while custom adapters can normalize other formats in the future.

2. Parsing

    The normalized dictionary is converted into immutable domain models such
    as SourceStep, FilterStep, CalculatedColumnStep, JoinStep, and
    OutputStep.

3. Validation

    The pipeline is checked for duplicate step IDs, missing dependencies,
    unsupported join types, and the presence of at least one output step.

4. Diagnostics

    Non-fatal issues, such as orphan steps that are not used by any output,
    are collected as structured warnings.

5. Source resolution

    Source steps are mapped to warehouse relations. Explicit mappings are used
    when provided, otherwise deterministic fallback relation names are
    generated.

6. Dependency ordering

    The pipeline dependency graph is topologically sorted to produce a
    deterministic execution order.

7. SQL generation

    One deterministic dbt-style SQL model is generated for every non-source
    step.

8. dbt artifact generation

    The project generates deterministic sources.yml and schema.yml
    artifacts.

9. Optional execution

    When an ExecutionRequest is provided, source CSV files are registered in
    an in-memory DuckDB database and the generated models are executed in
    dependency order.

10. Optional result validation

    When an expected CSV file is provided, the selected output is compared
    against it using column names, column order, row count, and row values.

11. Reporting

    The final ConversionResult contains the ordered pipeline, generated SQL
    models, generated dbt artifacts, and a conversion report containing
    warnings, errors, and optional validation results.

---

## Example Pipeline

```json
{
  "name": "order_revenue_pipeline",
  "steps": [
    {
      "id": "orders_source",
      "type": "source",
      "path": "orders.csv"
    },
    {
      "id": "valid_orders",
      "type": "filter",
      "input": "orders_source",
      "condition": "status != 'cancelled'"
    },
    {
      "id": "orders_with_revenue",
      "type": "calculated_column",
      "input": "valid_orders",
      "column": "revenue",
      "expression": "price - quantity"
    },
    {
      "id": "customers_source",
      "type": "source",
      "path": "customers.csv"
    },
    {
      "id": "enriched_orders",
      "type": "join",
      "left": "orders_with_revenue",
      "right": "customers_source",
      "left_key": "customer_id",
      "right_key": "id",
      "join_type": "left"
    },
    {
      "id": "final_output",
      "type": "output",
      "input": "enriched_orders",
      "table": "fct_order_revenue"
    }
  ]
}
```

---

## Repository Structure

```text
legacy-pipeline-converter/
├── README.md                          # Project overview.
├── pyproject.toml                     # Project metadata and dependencies.
├── .gitignore                         # Git exclusions.
├── data/
│   ├── expected/
│   │   └── final_output.csv           # Expected output dataset.
│   ├── sources/
│   │   ├── orders.csv                 # Example orders source data.
│   │   └── customers.csv              # Example customers source data.
│   └── legacy_pipeline.json           # Example pipeline.
│
├── docs/
│   ├── SPEC.md                        # Requirements and acceptance criteria.
│   ├── AGENTS.md                      # AI development workflow.
│   ├── AGENT_FAILURES.md              # Lessons learned from AI-assisted development.
│   ├── PROJECT_STATE.md               # Current implementation status.
│   ├── clarifications-v1.md           # Resolved ambiguities for v1.
│   ├── clarifications-v2.md           # Resolved ambiguities for v2.
│   ├── implementation-plan-v1.md      # Approved architecture and phased test plan.
│   └── implementation-plan-v2.md      # Version 2 implementation plan.
├── generated/                         # Generated SQL, YAML, and report artifacts.
├── scripts/
│   └── run_pipeline.py                # End-to-end example conversion runner.
├── src/
│   └── legacy_pipeline_converter/
│       ├── adapters/
│       │   ├── __init__.py            # Adapter package exports.
│       │   ├── base.py                # Pipeline adapter protocol.
│       │   └── json_adapter.py        # Default JSON dictionary adapter.
│       ├── __init__.py                # Package initialization and public exports.
│       ├── api.py                     # End-to-end conversion orchestration.
│       ├── dbt_artifacts.py           # dbt YAML artifact generation.
│       ├── diagnostics.py             # Structured warning generation.
│       ├── errors.py                  # Custom exceptions.
│       ├── execution.py               # DuckDB execution engine.
│       ├── io.py                      # JSON input and generated file output.
│       ├── models.py                  # Domain and supporting models.
│       ├── ordering.py                # Dependency graph and deterministic ordering.
│       ├── parser.py                  # Dictionary-to-domain parser.
│       ├── report.py                  # Conversion report generation.
│       ├── result_validation.py       # Execution result validation.
│       ├── source_mapping.py          # Source-to-relation resolution.
│       ├── sql_generator.py           # dbt-style SQL model generation.
│       └── validator.py               # Pipeline validation rules.
├── tests/
│   ├── conftest.py                    # Shared test fixtures.
│   ├── test_adapters.py               # Adapter contract and normalization tests.
│   ├── test_api.py                    # End-to-end conversion tests.
│   ├── test_dbt_artifacts.py          # dbt artifact generation tests.
│   ├── test_diagnostics.py            # Structured warning and diagnostics tests.
│   ├── test_execution.py              # DuckDB execution tests.
│   ├── test_io.py                     # File input and output tests.
│   ├── test_ordering.py               # Dependency ordering tests.
│   ├── test_parser.py                 # Parser tests.
│   ├── test_report.py                 # Conversion report tests.
│   ├── test_result_validation.py      # Execution result validation tests.
│   ├── test_source_mapping.py         # Source mapping tests.
│   ├── test_sql_generator.py          # SQL generation tests.
│   ├── test_validator.py              # Validation tests.
│   └── fixtures/
│       └── legacy_pipeline.json       # Example fixture.
└── .venv/                             # Local virtual environment.
```

## Development Principles

- Specification-driven development
- Acceptance criteria → failing tests → implementation
- Small, focused changes
- Composition over inheritance
- Deterministic output
- AI-assisted development with full human ownership

---

## Current Status

Version 1 is complete.

Version 2.0 is complete.

Version 2.1 is complete.

For implementation progress and architecture, see:

- `docs/PROJECT_STATE.md`
- `docs/implementation-plan-v2.md`

---

## Getting Started

### Create a virtual environment

```bash
python -m venv .venv
```

### Activate the virtual environment

#### Windows (PowerShell)

```bash
.\.venv\Scripts\Activate.ps1
```

#### Linux / macOS

```bash
source .venv/bin/activate
```

### Install the project and development dependencies

```bash
python -m pip install -e ".[dev]"
```

### Run the test suite

```bash
pytest
```

### Run the example conversion

The repository contains an example pipeline definition together with sample source data.

Run the end-to-end conversion example:

```bash
python scripts/run_pipeline.py
```

The script:

- reads the example pipeline from `data/legacy_pipeline.json`;
- reads the sample CSV source files from `data/sources/`;
- normalizes and validates the pipeline;
- resolves source mappings;
- generates deterministic dbt SQL models;
- generates `sources.yml` and `schema.yml`;
- executes the generated models locally using DuckDB (optional);
- validates the execution result against the expected dataset when provided;
- includes execution and validation results in the conversion report;
- generates a JSON conversion report;
- writes all generated artifacts to the `generated/` directory.

Generated files:

```text
generated/
├── models/
│   ├── enriched_orders.sql
│   ├── final_output.sql
│   ├── orders_with_revenue.sql
│   └── valid_orders.sql
├── report.json
├── schema.yml
└── sources.yml
```

Example console output:

```text
Conversion status: success

Execution order:
- orders_source
- valid_orders
- orders_with_revenue
- customers_source
- enriched_orders
- final_output

Execution and result validation:
- Executed: True
- Passed: True
- Output step: final_output
- Actual row count: 2
- Expected row count: 2
- No differences found.
```

---

## Planned Future Work

- Vendor-specific adapter implementations
- Additional transformation types
- Real ETL formats (Informatica, SSIS, Talend, IICS)
- IDE extension
