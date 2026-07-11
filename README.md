# Legacy ETL to ELT Modernisation Prototype

A Python prototype that converts simplified legacy ETL pipeline definitions into modern ELT-style transformations and generates deterministic dbt-style SQL models.

This project focuses on:

- Legacy ETL to modern ELT migration
- Dependency analysis and transformation ordering
- Deterministic SQL generation
- Specification-driven development
- Test-driven development (TDD)
- AI-assisted software engineering with full human ownership

---

## Goals

The application should:

1. Read a legacy pipeline definition from JSON.
2. Parse supported transformation types.
3. Validate pipeline definitions.
4. Build a dependency graph and determine transformation order.
5. Generate deterministic dbt-style SQL models.
6. Generate a conversion report.
7. Eventually execute transformations and validate results.

---

## Current Scope (v1)

### Supported transformation types

- `source`
- `filter`
- `calculated_column`
- `join`
- `output`

### Features

- Parse pipeline definitions from JSON.
- Validate:

  - unique step IDs;
  - missing dependencies;
  - supported join types;
  - at least one output step.
- Build a dependency graph and topological ordering.
- Generate deterministic dbt-style SQL files.
- Generate a JSON conversion report.
- Automated tests for parsing and conversion logic.

---

## Out of Scope (v1)

- Real Informatica, SSIS, Talend, or IICS formats
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
├── SPEC.md                            # Requirements and acceptance criteria.
├── AGENTS.md                          # AI development workflow.
├── AGENT_FAILURES.md                  # Lessons learned.
├── PROJECT_STATE.md                   # Current implementation status.
├── pyproject.toml                     # Project metadata and dependencies.
├── .gitignore                         # Git exclusions.
├── data/
│   └── legacy_pipeline.json           # Example pipeline.
├── docs/
│   └── clarifications-v1.md           # Resolved ambiguities.
├── generated/                         # Generated artifacts.
├── src/
│   └── legacy_pipeline_converter/
│       ├── __init__.py                # Package initialization.
│       ├── errors.py                  # Custom exceptions.
│       ├── models.py                  # Domain models.
│       └── parser.py                  # JSON parser.
├── tests/
│   ├── conftest.py                    # Shared test fixtures.
│   ├── test_parser.py                 # Parser tests.
│   └── fixtures/
│       └── legacy_pipeline.json       # Example fixture.
└── .venv/                             # Local environment.
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

See:

- `PROJECT_STATE.md`
- `docs/clarifications-v1.md`

for implementation progress and design decisions.

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

- DuckDB execution engine
- Result validation and data comparison
- Additional transformation types
- Real ETL formats (Informatica, SSIS, Talend, IICS)
- IDE extension
- Improved reporting and diagnostics
