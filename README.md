# Legacy ETL to ELT Modernisation Prototype

A Python prototype that converts simplified legacy ETL pipeline definitions into modern ELT-style transformations and generates deterministic dbt-style SQL models and YAML artifacts.

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
6. Generate a conversion report.
7. Extend the conversion pipeline with execution and result validation capabilities.

---

## Current Scope (v2.0)

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

---

## Out of Scope

- Real Informatica, SSIS, Talend, or IICS parsers
- Cloud warehouse deployment
- Frontend or UI
- Arbitrary SQL conversion
- Direct LLM integration
- Support for every transformation type
- Execution and result validation

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
│   └── legacy_pipeline.json           # Example pipeline.
├── docs/
│   ├── SPEC.md                        # Requirements and acceptance criteria.
│   ├── AGENTS.md                      # AI development workflow.
│   ├── AGENT_FAILURES.md              # Lessons learned from AI-assisted development.
│   ├── PROJECT_STATE.md               # Current implementation status.
│   ├── clarifications-v1.md           # Resolved ambiguities for v1.
│   ├── implementation-plan-v1.md      # Approved architecture and phased test plan.
│   └── implementation-plan-v2.md      # Version 2 implementation plan.
├── generated/                         # Generated SQL, YAML, and report artifacts.
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
│       ├── io.py                      # JSON input and generated file output.
│       ├── models.py                  # Domain and supporting models.
│       ├── ordering.py                # Dependency graph and deterministic ordering.
│       ├── parser.py                  # Dictionary-to-domain parser.
│       ├── report.py                  # Conversion report generation.
│       ├── source_mapping.py          # Source-to-relation resolution.
│       ├── sql_generator.py           # dbt-style SQL model generation.
│       └── validator.py               # Pipeline validation rules.
├── tests/
│   ├── conftest.py                    # Shared test fixtures.
│   ├── test_adapters.py               # Adapter contract and normalization tests.
│   ├── test_api.py                    # End-to-end conversion tests.
│   ├── test_dbt_artifacts.py          # dbt artifact generation tests.
│   ├── test_diagnostics.py            # Structured warning and diagnostics tests.
│   ├── test_io.py                     # File input and output tests.
│   ├── test_ordering.py               # Dependency ordering tests.
│   ├── test_parser.py                 # Parser tests.
│   ├── test_report.py                 # Conversion report tests.
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

## Current Status

Version 1 is complete.

Version 2.0 is currently under active development.

Completed Version 2.0 phases:

- Structured warnings and diagnostics
- Source mapping and deterministic fallback resolution
- Improved SQL generation
- dbt artifact generation
- Adapter extension contract and default JSON adapter

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

---

## Planned Future Work

- Version 2.0 end-to-end integration
- DuckDB execution engine
- Result validation and dataset comparison
- Vendor-specific adapter implementations
- Additional transformation types
- Real ETL formats (Informatica, SSIS, Talend, IICS)
- IDE extension
