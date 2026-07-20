# Legacy ETL to ELT Modernisation Prototype

## Goal

Build a Python application that reads a simplified legacy ETL pipeline definition,
converts it into an immutable internal representation, validates and orders its
transformations, and generates deterministic ELT-oriented artifacts.

The application should also support optional local execution and result validation
without making execution a requirement for ordinary conversion.

## Version 1 scope

Version 1 supports:

1. Reading a legacy pipeline from JSON.
2. Parsing source, filter, calculated-column, join, and output steps.
3. Validating pipeline structure and references.
4. Ordering transformations based on dependencies.
5. Generating deterministic dbt-style SQL models.
6. Generating a JSON conversion report.
7. Reading and writing conversion artifacts.
8. Running automated tests for all supported behaviour.

## Version 2.0 scope

Version 2.0 adds:

1. Structured warnings and deterministic warning propagation.
2. Orphan-step diagnostics.
3. Configurable source-to-relation mappings.
4. Deterministic fallback source relations.
5. Conflict detection for source mappings.
6. Deterministic SQL aliases and qualified join predicates.
7. Canonical SQL formatting.
8. Deterministic `sources.yml` and `schema.yml` generation.
9. A default JSON adapter.
10. An adapter extension contract for future vendor-specific inputs.
11. End-to-end warning and source-mapping support.

## Version 2.1 scope

Version 2.1 adds optional:

1. Rendering generated dbt-style references for local execution.
2. Source registration in DuckDB.
3. Execution of generated models in dependency order.
4. Comparison of generated outputs with expected datasets.
5. Validation summaries in conversion reports.

## Out of scope

- Complete Informatica, SSIS, Talend, or IICS parsers.
- Remote warehouse execution.
- Warehouse-specific SQL dialects beyond the supported prototype SQL.
- Full dbt project generation.
- `dbt_project.yml` generation.
- dbt packages, macros, snapshots, seeds, exposures, or semantic models.
- Lineage visualisation.
- Incremental dbt models.
- Production deployment or scheduling.
- Fuzzy or probabilistic result matching.
- GUI or IDE extension support.
- Direct LLM API integration.

## Acceptance criteria

### Version 1

- A valid example pipeline is parsed successfully.
- Unsupported transformation types produce a clear error.
- Invalid or missing dependencies produce a clear error.
- Transformations are returned in deterministic dependency order.
- Generated SQL is deterministic.
- Generated files follow a predictable naming convention.
- A JSON conversion report is created.
- Unit tests cover every supported transformation type.
- The complete Version 1 test suite passes.

### Version 2.0

- Warnings are structured, deterministic, serialized, and propagated.
- Orphan steps emit warnings without failing conversion.
- Explicit source mappings are supported.
- Missing mappings use deterministic fallbacks with warnings.
- Conflicting mappings fail clearly.
- Core Version 1 step models remain unchanged.
- Join SQL uses deterministic aliases and qualified predicates.
- SQL generation is byte-deterministic.
- `sources.yml` and `schema.yml` are generated deterministically.
- The JSON adapter preserves the existing input format.
- The high-level API returns the approved Version 2 result model.
- All Version 1 and Version 2.0 tests pass.

### Version 2.1

- Generated references can be rendered for DuckDB execution.
- CSV sources can be registered and queried locally.
- Generated models execute in dependency order.
- A requested output can be compared with an expected dataset.
- Comparison detects column, row-count, duplicate, and value mismatches.
- Validation results are included in the conversion report.
- Execution remains optional and produces no warning when not requested.
- All Version 1, Version 2.0, and Version 2.1 tests pass.