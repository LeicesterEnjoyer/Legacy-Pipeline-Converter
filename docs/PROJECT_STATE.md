# Project State

## Current Phase

Version 2.1 – Phase 7: DuckDB Rendering and Execution.

---

## Completed

### Project setup

- Created repository structure.
- Added `README.md`.
- Added project documentation under `docs/`.
- Configured `pyproject.toml`.
- Added `.gitignore`.
- Set up a local virtual environment.

### Architecture and planning

- Defined the approved v1 architecture in `docs/implementation-plan-v1.md`.
- Defined module responsibilities and public APIs.
- Defined the phased implementation plan and ordered test plan.
- Documented the TDD workflow and agent handoff process.

### Domain model

- Implemented immutable domain models:
  - `SourceStep`
  - `FilterStep`
  - `CalculatedColumnStep`
  - `JoinStep`
  - `OutputStep`
  - `Pipeline`
  - `OrderedPipeline`
  - `GeneratedModel`
  - `ConversionReport`

### Error handling

- Implemented `ConversionError`.
- Implemented `ParseError`.
- Implemented `UnsupportedStepTypeError`.
- Implemented validation-specific errors:
  - `ValidationError`
  - `DuplicateStepIdError`
  - `MissingReferenceError`
  - `InvalidJoinTypeError`
  - `NoOutputStepError`
- Implemented ordering-specific errors:
  - `CyclicDependencyError`

### Parser

- Implemented JSON-to-domain-model parsing.
- Supports all v1 transformation types.
- Ignores unknown fields.
- Keeps parsing and validation responsibilities separate.
- Provides clear parse errors, including invalid step indexes.

### Parser test coverage

- Valid example pipeline.
- All supported transformation types.
- Unsupported step types.
- Missing required fields.
- Missing pipeline name.
- Missing `steps`.
- Non-list `steps`.
- Non-object step entries.
- Missing step `id`.
- Missing step `type`.
- Ignored extra fields.
- Empty pipeline parsing.

**Status:** All parser test cases are passing (`20 passed`).

### Validation

- Implemented pipeline validation for:
  - unique step IDs;
  - valid dependencies for filter, calculated-column, and output steps;
  - valid left and right dependencies for join steps;
  - supported join types;
  - at least one output step;
  - multiple output steps allowed;
  - orphan steps allowed.

### Validation test coverage

- Duplicate step IDs.
- Missing input dependencies.
- Missing calculated-column dependencies.
- Missing join references.
- Invalid join types.
- All supported join types.
- Zero output steps.
- Multiple output steps.
- Orphan steps.
- Canonical example pipeline.

**Status:** All validation test cases are passing (`14 passed`).

### Dependency ordering

- Implemented dependency graph construction.
- Implemented deterministic topological ordering using Kahn's algorithm.
- Preserves JSON declaration order when multiple steps are ready.
- Supports dependencies for:
  - filter steps;
  - calculated-column steps;
  - join steps;
  - output steps.
- Implemented cyclic dependency detection.
- Returns an immutable `OrderedPipeline`.

### Dependency ordering test coverage

- Canonical example pipeline dependency order.
- Declaration-order tie-breaking for independent steps.
- Cyclic dependency errors.
- Deterministic ordering across repeated calls.

**Status:** All dependency ordering test cases are passing (`4 passed`).

### SQL generation

- Implemented deterministic SQL model generation.
- Generates one `GeneratedModel` for every non-source step.
- Skips SQL generation for source steps.
- Generates SQL for:
  - filter steps;
  - calculated-column steps;
  - join steps;
  - output steps.
- Uses `{{ ref('step_id') }}` for transformed upstream steps.
- Uses relation names derived from source file paths.
- Generates filenames using `<step_id>.sql`.
- Generates models in dependency order.
- Excludes dbt `config()` blocks.
- Uses deterministic `left_relation` and `right_relation` aliases for joins.
- Qualifies join predicates with their generated aliases.
- Uses canonical clause-per-line formatting with one trailing newline.
- Returns generated models as an immutable tuple.

### SQL generation test coverage

- Source steps generate no SQL model.
- Filter-step SQL.
- Calculated-column SQL.
- Join-step SQL.
- All supported join types.
- Output-step SQL.
- dbt `ref()` references for transformed upstream steps.
- Existing relation names for source upstream steps.
- Nested source path and extension removal.
- Deterministic model filenames.
- Absence of dbt `config()` blocks.
- Canonical example pipeline models.
- Deterministic SQL generation, including byte-identical canonical formatting.

**Status:** All SQL generation test cases are passing (`20 passed`).

### Conversion report

- Implemented immutable `ConversionReport`.
- Uses immutable tuples for:
  - generated model filenames;
  - errors;
  - warnings.
- Implemented report generation for successful conversions.
- Implemented report generation for failed conversions.
- Populates generated model filenames in dependency order.
- Stores formatted conversion errors.
- Keeps warnings empty in v1.
- Produces a JSON-serializable report structure.

### Conversion report test coverage

- Successful report schema.
- Successful report model population.
- Failed report error population.
- Empty warnings in v1.

**Status:** All conversion report test cases are passing (`4 passed`).

### End-to-end conversion

- Implemented `convert_pipeline` orchestration.
- Composes:
  - parsing;
  - validation;
  - dependency ordering;
  - SQL generation;
  - conversion reporting.
- Returns generated models and a success report for valid pipelines.
- Returns a failed report for expected conversion errors.
- Implemented JSON pipeline file reading.
- Implemented generated SQL file writing.
- Implemented conversion report JSON writing.
- Exposed the approved public API from the package root.

### End-to-end and file I/O test coverage

- Successful conversion of the canonical example pipeline.
- Failed conversion report for invalid input.
- Reading the canonical JSON pipeline from disk.
- Writing generated SQL models and the conversion report.
- Complete file-based conversion round trip.

**Status:** All Version 1 end-to-end and file I/O tests are passing (`5 passed`).

---

### Structured warnings and diagnostics

- Implemented immutable `WarningInfo`.
- Implemented deterministic orphan-step diagnostics.
- Implemented `collect_pipeline_warnings()`.
- Detects unreachable (orphan) pipeline steps.
- Preserves pipeline declaration order for warnings.
- Integrated structured warnings into `ConversionReport`.
- Propagates warnings through `convert_pipeline`.
- Produces JSON-serializable structured warning objects.

### Structured warnings and diagnostics test coverage

- Structured warning population in `ConversionReport`.
- Warning JSON serialization.
- No orphan warnings for fully connected pipelines.
- Orphan-step warning generation.
- Deterministic orphan warning ordering.

**Status:** All Phase 1 test cases are passing (`5 passed`).

### Source mapping

- Implemented immutable `SourceMapping`.
- Implemented immutable `ResolvedSource`.
- Implemented immutable `SourceResolution`.
- Implemented explicit source-to-relation resolution.
- Supports fully qualified warehouse relation names.
- Detects conflicting source mappings.
- Preserves declaration order of resolved sources.
- Falls back to deterministic relation names derived from source file paths.
- Emits structured warnings for fallback relation names.
- Integrated source resolution with SQL generation.
- Preserves Version 1 SQL generation behavior when no source mappings are supplied.

### Source mapping test coverage

- Explicit source relation mappings.
- Fully qualified warehouse relation mappings.
- Deterministic filename fallback relations.
- Structured fallback relation warnings.
- Duplicate mapping handling.
- Conflicting mapping detection.
- Deterministic declaration order.

**Status:** All Phase 2 test cases are passing (`7 passed`).

---

### dbt artifacts

- Implemented immutable `GeneratedArtifact`.
- Implemented immutable `DbtGenerationConfig`.
- Generates deterministic `sources.yml` and `schema.yml` artifacts.
- Groups resolved sources by database and schema.
- Preserves source declaration order within generated table lists.
- Includes filename-derived fallback relations.
- Preserves generated model order in `schema.yml`.
- Supports configurable default `view` or `table` materialization.
- Writes generated YAML artifacts through the file I/O layer.
- Exposes `generate_dbt_artifacts()` from the package root.

### dbt artifact test coverage

- Resolved and fallback source relations in `sources.yml`.
- Deterministic `sources.yml` generation.
- Generated model order in `schema.yml`.
- Configurable default materialization.
- YAML artifact file writing.

**Status:** All Phase 4 test cases are passing (`5 passed`).

---

### Adapter extension contract

- Implemented the runtime-checkable `PipelineAdapter` protocol.
- Implemented the default `JsonPipelineAdapter`.
- Preserves the existing dictionary-based JSON input format.
- Rejects unsupported default-adapter source types with a clear parse error.
- Supports explicit adapter injection through `convert_pipeline()`.
- Keeps adapter normalization separate from domain parsing.
- Leaves vendor-specific adapter implementations out of scope.

### Adapter test coverage

- Existing dictionary normalization.
- Explicit protocol conformance through `normalize()`.
- Unsupported default-adapter source types.
- High-level API delegation to a supplied adapter.

**Status:** All Phase 5 test cases are passing (`4 passed`).

---

### Version 2.0 integration

- Implemented immutable `ConversionResult`.
- Integrated adapter normalization with the existing parser.
- Integrated structured diagnostics and source mapping resolution.
- Uses resolved sources throughout SQL and dbt artifact generation.
- Propagates dbt generation configuration through the high-level API.
- Combines orphan and missing-mapping warnings deterministically.
- Returns models, artifacts, and the conversion report as one result.
- Captures known mapping failures in failed conversion results.
- Preserves direct Version 1 dictionary input compatibility.
- Exposes source mapping resolution from the package root.

### Version 2.0 integration test coverage

- Complete models, artifacts, warnings, mappings, and configuration.
- Existing Version 1 JSON input compatibility.
- Conflicting source mappings returned as failed reports.
- Deterministic end-to-end conversion results.

**Status:** All Phase 6 test cases are passing (`4 passed`).

---

## In Progress

Version 2.1 – Phase 7: DuckDB Rendering and Execution

Planned scope:

- Render generated dbt references for local execution.
- Register CSV sources in DuckDB.
- Execute generated models in dependency order.
- Return the selected output relation.

---

## Next Phase

Version 2.1 – Phase 8: Result Comparison

Planned scope:

- Compare generated output with an expected CSV.
- Compare column names, column order, and row counts.
- Compare rows as multisets while preserving duplicate multiplicity.
- Produce an immutable `ValidationSummary`.

---

## Not Implemented

The following Version 2 features are not yet implemented:

### Planned Version 2.1 phases

- Executing generated SQL.
- DuckDB-based result validation.
- Comparing generated and expected datasets.

### Future versions

- Parsing real Informatica, SSIS, Talend, or IICS formats.
- Supporting additional transformation types.
- Providing a CLI.
- Building an IDE extension.
- Integrating directly with an LLM API.

---

## Current Status

Version 1 and Version 2.0 are complete. Version 2.1 development is underway.

Completed:

- Parsing and domain models ✅
- Validation ✅
- Dependency ordering and cycle detection ✅
- SQL generation ✅
- Conversion report generation ✅
- End-to-end conversion and file output ✅
- Structured warnings and diagnostics ✅
- Improved SQL generation with deterministic aliases and qualified joins ✅
- Deterministic dbt artifact generation ✅
- Adapter extension contract and default JSON adapter ✅
- Version 2.0 end-to-end integration ✅
