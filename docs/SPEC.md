# Legacy ETL to ELT Modernisation Prototype

## Goal

Build a Python application that reads a simplified legacy ETL pipeline definition,
converts it into an internal representation, generates dbt-style SQL models,
and validates that the generated transformation produces the expected result.

## Initial scope

The first version must support:

1. Reading a legacy pipeline from JSON.
2. Parsing source, filter, calculated-column, join, and output steps.
3. Validating references between pipeline steps.
4. Ordering transformations based on their dependencies.
5. Generating dbt-style SQL files.
6. Generating a conversion report in JSON.
7. Running automated tests for parsing and conversion logic.

## Out of scope

- Parsing real Informatica, SSIS, Talend, or IICS files.
- Deploying to Snowflake or another cloud warehouse.
- Building a production-ready frontend.
- Converting arbitrary SQL.
- Integrating directly with an LLM API.
- Supporting every possible transformation type.

## Acceptance criteria

- A valid example pipeline is parsed successfully.
- Unsupported transformation types produce a clear error.
- Invalid or missing dependencies produce a clear error.
- Transformations are returned in dependency order.
- Generated SQL is deterministic.
- Generated files follow a predictable naming convention.
- A JSON conversion report is created.
- Unit tests cover every supported transformation type.
- The complete test suite passes before changes are merged.
